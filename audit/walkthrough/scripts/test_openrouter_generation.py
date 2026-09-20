import http.client
import importlib.util
import io
import json
import urllib.error
from datetime import UTC, datetime
from email.utils import formatdate
from pathlib import Path

import pytest

SCRIPT = Path(__file__).with_name("openrouter-generation.py")
GEN = "gen-1789848711-DY3K9lDJO3kqDAfH1bPA"
MODEL = "openai/gpt-5.6-sol"
SINCE = 1789848700
SERVER_NOW = 1789848760
LOCAL_AHEAD = 600


def load_module():
    spec = importlib.util.spec_from_file_location("openrouter_generation", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


og = load_module()


def record(model="openai/gpt-5.6-sol-20260709", created="2026-09-19T20:11:51.206Z"):
    return {
        "data": {
            "id": GEN,
            "model": model,
            "provider_name": "OpenAI",
            "total_cost": 0.000076,
            "native_tokens_prompt": 13,
            "native_tokens_completion": 5,
            "created_at": created,
        }
    }


def headers(date=None):
    message = http.client.HTTPMessage()
    if date is not None:
        message["Date"] = date
    return message


class FakeResponse:
    def __init__(self, payload, date=None):
        self.payload = payload
        self.headers = headers(date)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return self.payload


def not_found():
    body = json.dumps({"error": {"message": f"Generation {GEN} not found", "code": 404}})
    return urllib.error.HTTPError(
        og.ENDPOINT, 404, "Not Found", http.client.HTTPMessage(), io.BytesIO(body.encode())
    )


def scripted_opener(steps, captured=None, date=None):
    steps = list(steps)

    def opener(request, timeout):
        if captured is not None:
            captured.append(request)
        step = steps.pop(0) if len(steps) > 1 else steps[0]
        if isinstance(step, BaseException):
            raise step
        return FakeResponse(json.dumps(step).encode(), date)

    return opener


class Clock:
    def __init__(self):
        self.now = 0.0

    def time(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


def run(
    steps,
    *,
    expected=MODEL,
    since=SINCE,
    deadline=300,
    interval=15,
    captured=None,
    date=None,
    now=None,
):
    clock = Clock()
    results = og.verify_all(
        [(GEN, expected)],
        "sk-test",
        since=since,
        deadline=deadline,
        interval=interval,
        timeout=20,
        opener=scripted_opener(steps, captured, date),
        clock=clock.time,
        sleep=clock.sleep,
        **({} if now is None else {"now": now}),
    )
    return results[0], clock


@pytest.mark.parametrize(
    ("served", "expected"),
    [
        ("openai/gpt-5.6-sol", True),
        ("openai/gpt-5.6-sol-20260709", True),
        ("openai/gpt-5.6-solx", False),
        ("anthropic/claude-opus-5", False),
        ("", False),
    ],
)
def test_model_matches_accepts_dated_permaslug_only(served, expected):
    assert og.model_matches(served, MODEL) is expected


@pytest.mark.parametrize(
    ("served", "requested"),
    [
        ("deepseek/deepseek-r1:free", "deepseek/deepseek-r1:free"),
        ("deepseek/deepseek-r1", "deepseek/deepseek-r1:free"),
        ("deepseek/deepseek-r1-20260101", "deepseek/deepseek-r1:free"),
        ("deepseek/deepseek-r1:free", "deepseek/deepseek-r1"),
    ],
)
def test_model_matches_ignores_the_variant_suffix(served, requested):
    assert og.model_matches(served, requested) is True


def test_verified_record_reports_what_openrouter_declares():
    captured = []
    result, _ = run([record()], captured=captured)
    assert result == {
        "id": GEN,
        "expected_model": MODEL,
        "status": "verified",
        "model": "openai/gpt-5.6-sol-20260709",
        "provider": "OpenAI",
        "total_cost": 0.000076,
        "tokens_prompt": 13,
        "tokens_completion": 5,
        "created_at": "2026-09-19T20:11:51.206Z",
        "error": None,
    }
    request = captured[0]
    assert request.get_method() == "GET"
    assert request.full_url == f"{og.ENDPOINT}?id={GEN}"
    assert request.get_header("Authorization") == "Bearer sk-test"


def test_record_published_after_delay_is_polled_until_found():
    result, clock = run([not_found(), not_found(), record()])
    assert result["status"] == "verified"
    assert clock.now == 30


def test_record_never_published_is_not_found_at_deadline():
    result, clock = run([not_found()], deadline=60, interval=15)
    assert result["status"] == "not_found"
    assert "not found" in result["error"]
    assert clock.now >= 60


def test_deadline_bounds_a_pass_over_slow_lookups():
    clock = Clock()

    def hanging(request, timeout):
        clock.now += timeout
        raise TimeoutError

    checks = [(f"gen-{n}", MODEL) for n in range(10)]
    results = og.verify_all(
        checks,
        "sk-test",
        since=SINCE,
        deadline=60,
        interval=15,
        timeout=20,
        opener=hanging,
        clock=clock.time,
        sleep=clock.sleep,
    )
    assert clock.now <= 60 + 20
    assert [r["status"] for r in results] == ["error"] * 10
    assert results[-1]["error"] == "deadline reached before lookup"


def test_other_model_is_a_mismatch():
    result, _ = run([record(model="anthropic/claude-opus-5")])
    assert result["status"] == "model_mismatch"
    assert result["model"] == "anthropic/claude-opus-5"


def test_generation_older_than_since_is_a_replay():
    result, _ = run([record(created="2026-01-01T00:00:00Z")])
    assert result["status"] == "stale"


def test_since_tolerates_small_clock_skew():
    result, _ = run([record()], since=1789848711 + 30)
    assert result["status"] == "verified"


@pytest.mark.parametrize("value", [None, "", "not a date"])
def test_server_epoch_ignores_an_unusable_date(value):
    assert og.server_epoch(headers(value)) is None


def test_date_header_realigns_since_on_the_server_clock():
    result, _ = run(
        [record()],
        since=SINCE + LOCAL_AHEAD,
        date=formatdate(SERVER_NOW, usegmt=True),
        now=lambda: SERVER_NOW + LOCAL_AHEAD,
    )
    assert result["status"] == "verified"


def test_without_a_date_header_the_local_bound_stands():
    result, _ = run([record()], since=SINCE + LOCAL_AHEAD, now=lambda: SERVER_NOW + LOCAL_AHEAD)
    assert result["status"] == "stale"


def test_date_header_catches_a_replay_a_lagging_local_clock_would_admit():
    replay = datetime.fromtimestamp(SINCE - 300, tz=UTC).isoformat()
    result, _ = run(
        [record(created=replay)],
        since=SINCE - LOCAL_AHEAD,
        date=formatdate(SERVER_NOW, usegmt=True),
        now=lambda: SERVER_NOW - LOCAL_AHEAD,
    )
    assert result["status"] == "stale"


def test_transient_error_is_retried_then_verified():
    result, _ = run([urllib.error.URLError("reset"), record()])
    assert result["status"] == "verified"


def test_persistent_error_reports_last_error():
    auth = urllib.error.HTTPError(
        og.ENDPOINT, 401, "Unauthorized", http.client.HTTPMessage(), io.BytesIO(b"{}")
    )
    result, _ = run([auth], deadline=30)
    assert result["status"] == "error"
    assert result["error"].startswith("HTTP 401")


def test_malformed_record_is_an_error():
    result, _ = run([{"data": {"id": GEN}}], deadline=15)
    assert result["status"] == "error"


def write_args(*pairs):
    args = []
    for gen_id, model in pairs:
        args += ["--check", gen_id, model]
    return args


@pytest.mark.parametrize(
    "pair",
    [("gen-1;rm", MODEL), ("req-123", MODEL), (GEN, "gpt 5"), (GEN, "<MODEL>")],
)
def test_main_rejects_malformed_arguments(pair, capsys):
    with pytest.raises(SystemExit) as excinfo:
        og.main([*write_args(pair), "--since", str(SINCE)])
    assert excinfo.value.code == 2
    assert capsys.readouterr().out == ""


def test_parse_args_accepts_a_variant_suffix():
    args = og.parse_args([*write_args((GEN, "deepseek/deepseek-r1:free")), "--since", str(SINCE)])
    assert args.check == [[GEN, "deepseek/deepseek-r1:free"]]


def test_main_requires_a_check(capsys):
    with pytest.raises(SystemExit) as excinfo:
        og.main(["--since", str(SINCE)])
    assert excinfo.value.code == 2


def test_main_without_key_reports_error_for_each_check(monkeypatch, capsys):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    assert og.main([*write_args((GEN, MODEL)), "--since", str(SINCE)]) == 1
    output = json.loads(capsys.readouterr().out)
    assert output[0]["status"] == "error"
    assert output[0]["error"] == "OPENROUTER_API_KEY is not set"


def test_main_exit_status_follows_worst_result(monkeypatch, capsys):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
    monkeypatch.setattr(og.urllib.request, "urlopen", scripted_opener([record()]))
    assert og.main([*write_args((GEN, MODEL)), "--since", str(SINCE)]) == 0
    assert json.loads(capsys.readouterr().out)[0]["status"] == "verified"
    monkeypatch.setattr(og.urllib.request, "urlopen", scripted_opener([record(model="x/y")]))
    assert og.main([*write_args((GEN, MODEL)), "--since", str(SINCE)]) == 1
