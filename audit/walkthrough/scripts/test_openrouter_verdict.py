import http.client
import importlib.util
import io
import json
import urllib.error
from pathlib import Path

import pytest

SCRIPT = Path(__file__).with_name("openrouter-verdict.py")
MODEL = "openai/gpt-5.6-sol"


def load_module():
    spec = importlib.util.spec_from_file_location("openrouter_verdict", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ov = load_module()


def completion(content, *, finish="stop", served=MODEL):
    return {
        "model": served,
        "choices": [{"finish_reason": finish, "message": {"content": content}}],
    }


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return self.payload


def opener_returning(payload, captured=None):
    def opener(request, timeout):
        if captured is not None:
            captured["request"] = request
            captured["timeout"] = timeout
        return FakeResponse(payload)

    return opener


def opener_raising(exc):
    def opener(request, timeout):
        raise exc

    return opener


def http_error(code, body):
    return urllib.error.HTTPError(ov.ENDPOINT, code, "Bad Request", None, io.BytesIO(body))


def test_payload_requests_named_strict_schema():
    payload = ov.build_payload(MODEL, "claim", "code", "a.sh", 2048)
    response_format = payload["response_format"]
    assert response_format["type"] == "json_schema"
    assert response_format["json_schema"]["name"]
    assert response_format["json_schema"]["strict"] is True
    assert payload["model"] == MODEL
    assert payload["max_tokens"] == 2048
    assert "File: a.sh" in payload["messages"][1]["content"]


def test_payload_omits_file_label_without_path():
    payload = ov.build_payload(MODEL, "claim", "code", "", 2048)
    assert "File:" not in payload["messages"][1]["content"]


def test_parse_plain_json_verdict():
    body = completion('{"verdict": "valid", "rationale": " Real bug. "}', served="openai/x")
    result = ov.parse_completion(MODEL, body)
    assert result == {
        "verdict": "valid",
        "rationale": "Real bug.",
        "requested_model": MODEL,
        "served_model": "openai/x",
        "error": None,
    }


def test_parse_fenced_json_verdict():
    body = completion('```json\n{"verdict": "invalid", "rationale": "Handled."}\n```')
    result = ov.parse_completion(MODEL, body)
    assert result["verdict"] == "invalid"
    assert result["error"] is None


def test_parse_truncated_response_is_an_error():
    body = completion('{"verdict": "val', finish="length")
    result = ov.parse_completion(MODEL, body)
    assert result["verdict"] is None
    assert "truncated" in result["error"]
    assert result["served_model"] == MODEL


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        ("", "empty"),
        ("not json at all", "not JSON"),
        ('{"verdict": "maybe", "rationale": "x"}', "not valid/invalid"),
        ('["valid"]', "not valid/invalid"),
        ('{"verdict": "valid"}', "rationale"),
    ],
)
def test_parse_rejects_unusable_content(content, expected):
    result = ov.parse_completion(MODEL, completion(content))
    assert result["verdict"] is None
    assert expected in result["error"]


def test_parse_null_content_is_an_error():
    body = {"model": MODEL, "choices": [{"finish_reason": "stop", "message": {"content": None}}]}
    assert "empty" in ov.parse_completion(MODEL, body)["error"]


def test_parse_missing_choices_is_an_error():
    assert "no choices" in ov.parse_completion(MODEL, {"model": MODEL})["error"]


def test_parse_error_body_surfaces_provider_message():
    raw = json.dumps({"error": {"message": "Missing required parameter: 'name'."}})
    body = {"error": {"message": "Provider returned error", "metadata": {"raw": raw}}}
    result = ov.parse_completion(MODEL, body)
    assert result["error"] == "Provider returned error: Missing required parameter: 'name'."


def test_parse_error_body_with_non_json_raw():
    body = {"error": {"message": "Provider returned error", "metadata": {"raw": "upstream down"}}}
    assert ov.parse_completion(MODEL, body)["error"] == "Provider returned error: upstream down"


def test_request_sends_authorized_post_and_parses_answer():
    captured = {}
    payload = json.dumps(completion('{"verdict": "valid", "rationale": "ok"}')).encode()
    result = ov.request_verdict(
        MODEL, "claim", "code", "", "sk-test", 30, 2048, opener_returning(payload, captured)
    )
    request = captured["request"]
    assert result["verdict"] == "valid"
    assert captured["timeout"] == 30
    assert request.get_method() == "POST"
    assert request.full_url == ov.ENDPOINT
    assert request.get_header("Authorization") == "Bearer sk-test"
    assert json.loads(request.data)["model"] == MODEL


def test_request_http_error_with_json_body():
    body = json.dumps({"error": {"message": "No endpoints found for x/y."}}).encode()
    result = ov.request_verdict(
        MODEL, "c", "c", "", "k", 30, 2048, opener_raising(http_error(404, body))
    )
    assert result["error"] == "HTTP 404: No endpoints found for x/y."


def test_request_http_error_with_text_body():
    result = ov.request_verdict(
        MODEL, "c", "c", "", "k", 30, 2048, opener_raising(http_error(502, b"<html>bad</html>"))
    )
    assert result["error"].startswith("HTTP 502:")


@pytest.mark.parametrize(
    ("exc", "expected"),
    [
        (urllib.error.URLError("Name or service not known"), "network error"),
        (TimeoutError(), "timed out after 30s"),
        (ConnectionResetError("reset"), "network error"),
    ],
)
def test_request_transport_failures(exc, expected):
    result = ov.request_verdict(MODEL, "c", "c", "", "k", 30, 2048, opener_raising(exc))
    assert result["verdict"] is None
    assert expected in result["error"]


class TruncatedResponse(FakeResponse):
    def read(self):
        raise http.client.IncompleteRead(b'{"choi', 512)


def test_request_body_cut_mid_read_reports_error():
    result = ov.request_verdict(
        MODEL, "c", "c", "", "k", 30, 2048, lambda request, timeout: TruncatedResponse(b"")
    )
    assert result["verdict"] is None
    assert "network error" in result["error"]


def test_request_non_json_success_body():
    result = ov.request_verdict(
        MODEL, "c", "c", "", "k", 30, 2048, opener_returning(b"<html></html>")
    )
    assert "not JSON" in result["error"]


def write_inputs(tmp_path, claim="The loop never ends.", code="while True: pass"):
    claim_file = tmp_path / "claim.txt"
    code_file = tmp_path / "code.txt"
    claim_file.write_text(claim)
    code_file.write_text(code)
    return ["--claim-file", str(claim_file), "--code-file", str(code_file)]


def test_main_rejects_malformed_model(tmp_path, capsys):
    with pytest.raises(SystemExit) as excinfo:
        ov.main(["--model", "gpt 5; rm -rf /", *write_inputs(tmp_path)])
    assert excinfo.value.code == 2
    assert capsys.readouterr().out == ""


def test_main_rejects_empty_claim(tmp_path):
    with pytest.raises(SystemExit) as excinfo:
        ov.main(["--model", MODEL, *write_inputs(tmp_path, claim="  \n")])
    assert excinfo.value.code == 2


def test_main_rejects_missing_file(tmp_path):
    args = ["--model", MODEL, "--claim-file", str(tmp_path / "nope"), "--code-file", "x"]
    with pytest.raises(SystemExit) as excinfo:
        ov.main(args)
    assert excinfo.value.code == 2


def test_main_without_key_reports_error(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    assert ov.main(["--model", MODEL, *write_inputs(tmp_path)]) == 1
    output = json.loads(capsys.readouterr().out)
    assert output["error"] == "OPENROUTER_API_KEY is not set"
    assert output["requested_model"] == MODEL


def test_main_success_prints_verdict(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
    payload = json.dumps(completion('{"verdict": "invalid", "rationale": "Guarded."}')).encode()
    monkeypatch.setattr(ov.urllib.request, "urlopen", opener_returning(payload))
    assert ov.main(["--model", MODEL, "--path", "loop.py", *write_inputs(tmp_path)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["verdict"] == "invalid"
    assert output["served_model"] == MODEL


def test_main_failed_call_exits_one(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
    monkeypatch.setattr(ov.urllib.request, "urlopen", opener_raising(TimeoutError()))
    assert ov.main(["--model", MODEL, "--timeout", "5", *write_inputs(tmp_path)]) == 1
    assert json.loads(capsys.readouterr().out)["error"] == "timed out after 5s"
