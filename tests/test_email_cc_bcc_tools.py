import json
from pathlib import Path

from src import agent_tools


def _schema_for(name):
    return next(
        schema["function"]
        for schema in agent_tools.FUNCTION_TOOL_SCHEMAS
        if schema["function"]["name"] == name
    )


def test_send_email_native_schema_exposes_cc_and_bcc():
    props = _schema_for("send_email")["parameters"]["properties"]

    assert "cc" in props
    assert "bcc" in props
    assert props["cc"]["type"] == "string"
    assert props["bcc"]["type"] == "string"


def test_send_email_native_call_preserves_cc_and_bcc_for_mcp():
    block = agent_tools.function_call_to_tool_block(
        "send_email",
        json.dumps(
            {
                "to": "recipient@example.com",
                "cc": "manager@example.com",
                "bcc": "archive@example.com",
                "subject": "Status",
                "body": "Sending the update.",
            }
        ),
    )

    assert block.tool_type == "mcp__email__send_email"
    assert json.loads(block.content)["cc"] == "manager@example.com"
    assert json.loads(block.content)["bcc"] == "archive@example.com"


def test_send_email_agent_prompt_mentions_cc_and_bcc():
    prompt_source = Path("src/agent_loop.py").read_text(encoding="utf-8")

    assert '"cc": "manager@example.com"' in prompt_source
    assert '"bcc": "archive@example.com"' in prompt_source
    assert "If the user asks to CC or BCC someone" in prompt_source
