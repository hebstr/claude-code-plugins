#!/usr/bin/env python3
"""Check OpenRouter generation IDs against the account's generation records.

Each `--check GEN_ID MODEL` pair names the `gen-...` ID a call reported and
the model the call requested, never the model the caller reports as having
served it, which would only test the caller against itself. The script looks each ID up on
OpenRouter's generation endpoint and prints one JSON array to stdout, one
object per pair, in argument order:

    {"id": str, "expected_model": str,
     "status": "verified" | "model_mismatch" | "stale" | "not_found" | "error",
     "model": str | null, "provider": str | null, "total_cost": float | null,
     "tokens_prompt": int | null, "tokens_completion": int | null,
     "created_at": str | null, "error": str | null}

`model` and the fields after it are what OpenRouter declares for the ID, never
what the caller claimed. A record is only published about two minutes after
the call completes (measured 2026-09-19), so a 404 is retried every
`--interval` seconds until `--deadline`; no lookup starts after it, so a run
lasts at most `--deadline` plus one `--timeout`. `stale` means the record predates
`--since`, the time the checked calls were launched: a real ID replayed from an
earlier call. `--since` is a local epoch while `created_at` comes from OpenRouter,
so the bound is realigned on the offset read from the first response's `Date`
header, leaving `CLOCK_SKEW` to absorb request latency alone; without that header
the raw local value is used and the comparison keeps whatever clock drift exists.
Exit status is 0 when every pair is `verified`, 1 otherwise, and
2 on invalid arguments (the reason goes to stderr, no JSON).

Used by audit/blindspot/SKILL.md and agents/ouroboros-bridge.md.
"""

import argparse
import http.client
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from email.utils import parsedate_to_datetime

ENDPOINT = "https://openrouter.ai/api/v1/generation"
GEN_PAT = re.compile(r"^gen-[A-Za-z0-9-]+$")
MODEL_PAT = re.compile(r"^[A-Za-z0-9_-]+/[A-Za-z0-9._-]+(:[A-Za-z0-9._-]+)?$")
CLOCK_SKEW = 60


def server_epoch(headers):
    """Epoch seconds OpenRouter reports in its `Date` header, None when unusable."""
    raw = headers.get("Date") if headers is not None else None
    if not raw:
        return None
    try:
        return parsedate_to_datetime(raw).timestamp()
    except (TypeError, ValueError):
        return None


def model_matches(declared, expected):
    declared, expected = declared.split(":")[0], expected.split(":")[0]
    return declared == expected or declared.startswith(f"{expected}-")


def make_result(gen_id, expected, status, *, data=None, error=None):
    data = data or {}
    return {
        "id": gen_id,
        "expected_model": expected,
        "status": status,
        "model": data.get("model"),
        "provider": data.get("provider_name"),
        "total_cost": data.get("total_cost"),
        "tokens_prompt": data.get("native_tokens_prompt"),
        "tokens_completion": data.get("native_tokens_completion"),
        "created_at": data.get("created_at"),
        "error": error,
    }


def classify(gen_id, expected, data, since):
    model = data.get("model")
    created = data.get("created_at")
    if not isinstance(model, str) or not isinstance(created, str):
        return make_result(gen_id, expected, "error", data=data, error="record lacks model")
    try:
        created_ts = datetime.fromisoformat(created).timestamp()
    except ValueError:
        return make_result(gen_id, expected, "error", data=data, error="bad created_at")
    if not model_matches(model, expected):
        return make_result(
            gen_id, expected, "model_mismatch", data=data, error=f"record names {model}"
        )
    if created_ts < since - CLOCK_SKEW:
        return make_result(gen_id, expected, "stale", data=data, error=f"record created {created}")
    return make_result(gen_id, expected, "verified", data=data)


def fetch(gen_id, api_key, timeout, opener):
    """Return (outcome, payload, observed), outcome in {found, missing, failed}.

    `observed` is the server epoch the response advertised, or None.
    """
    url = f"{ENDPOINT}?{urllib.parse.urlencode({'id': gen_id})}"
    request = urllib.request.Request(
        url, method="GET", headers={"Authorization": f"Bearer {api_key}"}
    )
    try:
        with opener(request, timeout=timeout) as response:
            raw = response.read()
            observed = server_epoch(getattr(response, "headers", None))
    except urllib.error.HTTPError as exc:
        observed = server_epoch(exc.headers)
        if exc.code == 404:
            return "missing", f"generation {gen_id} not found", observed
        return "failed", f"HTTP {exc.code}: {exc.reason}", observed
    except urllib.error.URLError as exc:
        return "failed", f"network error: {exc.reason}", None
    except TimeoutError:
        return "failed", f"timed out after {timeout}s", None
    except (OSError, http.client.HTTPException) as exc:
        return "failed", f"network error: {exc}", None
    try:
        body = json.loads(raw)
    except ValueError:
        return "failed", f"response is not JSON: {raw[:200]!r}", observed
    data = body.get("data") if isinstance(body, dict) else None
    if not isinstance(data, dict):
        return "failed", "response has no data", observed
    return "found", data, observed


def verify_all(
    checks, api_key, *, since, deadline, interval, timeout, opener, clock, sleep, now=time.time
):
    results = {}
    last = {}
    offset = None
    start = clock()
    while True:
        for index, (gen_id, expected) in enumerate(checks):
            if index in results:
                continue
            if clock() - start >= deadline:
                last.setdefault(index, ("failed", "deadline reached before lookup"))
                continue
            outcome, payload, observed = fetch(gen_id, api_key, timeout, opener)
            if offset is None and observed is not None:
                offset = observed - now()
            if outcome == "found":
                bound = since if offset is None else since + offset
                results[index] = classify(gen_id, expected, payload, bound)
            else:
                last[index] = (outcome, payload)
        elapsed = clock() - start
        if len(results) == len(checks) or elapsed >= deadline:
            break
        sleep(min(interval, deadline - elapsed))
    for index, (gen_id, expected) in enumerate(checks):
        if index not in results:
            outcome, reason = last[index]
            status = "not_found" if outcome == "missing" else "error"
            results[index] = make_result(gen_id, expected, status, error=reason)
    return [results[index] for index in range(len(checks))]


def positive_int(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError(f"expected a positive integer, got {value}")
    return number


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        nargs=2,
        action="append",
        required=True,
        metavar=("GEN_ID", "MODEL"),
        help="generation ID and the model the call requested",
    )
    parser.add_argument(
        "--since", type=positive_int, required=True, help="epoch seconds the calls began"
    )
    parser.add_argument("--deadline", type=positive_int, default=300)
    parser.add_argument("--interval", type=positive_int, default=15)
    parser.add_argument("--timeout", type=positive_int, default=20)
    args = parser.parse_args(argv)
    for gen_id, model in args.check:
        if not GEN_PAT.match(gen_id):
            parser.error(f"generation ID does not match gen-...: {gen_id!r}")
        if not MODEL_PAT.match(model):
            parser.error(f"model ID does not match provider/model: {model!r}")
    return args


def main(argv=None):
    args = parse_args(argv)
    checks = [tuple(pair) for pair in args.check]
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        results = [
            make_result(gen_id, model, "error", error="OPENROUTER_API_KEY is not set")
            for gen_id, model in checks
        ]
    else:
        results = verify_all(
            checks,
            api_key,
            since=args.since,
            deadline=args.deadline,
            interval=args.interval,
            timeout=args.timeout,
            opener=urllib.request.urlopen,
            clock=time.monotonic,
            sleep=time.sleep,
            now=time.time,
        )
    json.dump(results, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0 if all(result["status"] == "verified" for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
