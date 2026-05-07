"""Additional render-focused tests for envdiff.templater."""

from envdiff.templater import build_template, render_template


def test_render_template_key_order_is_alphabetical():
    env = {"ZEBRA": "z", "ALPHA": "a", "MIDDLE": "m"}
    result = build_template(env)
    output = render_template(result)
    lines = [l for l in output.strip().splitlines() if not l.startswith("#")]
    keys = [l.split("=")[0] for l in lines]
    assert keys == ["ALPHA", "MIDDLE", "ZEBRA"]


def test_render_template_multiple_comments():
    env = {"A": "1", "B": "2"}
    comments = {"A": "First var", "B": "Second var"}
    result = build_template(env, comments=comments)
    output = render_template(result)
    assert "# First var" in output
    assert "# Second var" in output


def test_render_template_no_extra_blank_lines():
    env = {"X": "1", "Y": "2"}
    result = build_template(env)
    output = render_template(result)
    # Should not have consecutive blank lines
    assert "\n\n" not in output


def test_render_template_keep_and_redact_mixed():
    env = {"PUBLIC": "open", "PRIVATE": "secret", "PORT": "3000"}
    result = build_template(env, keep_keys=["PUBLIC", "PORT"])
    output = render_template(result)
    assert "PUBLIC=open" in output
    assert "PORT=3000" in output
    assert "PRIVATE=<REPLACE_ME>" in output


def test_render_template_single_key():
    env = {"ONLY_KEY": "value"}
    result = build_template(env)
    output = render_template(result)
    assert output == "ONLY_KEY=<REPLACE_ME>\n"


def test_build_template_returns_template_result_type():
    from envdiff.templater import TemplateResult
    env = {"K": "v"}
    result = build_template(env)
    assert isinstance(result, TemplateResult)
