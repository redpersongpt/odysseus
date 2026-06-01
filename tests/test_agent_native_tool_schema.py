from src.agent_loop import FUNCTION_TOOL_SCHEMAS, _API_HOSTS


def _schema_names():
    return {schema["function"]["name"] for schema in FUNCTION_TOOL_SCHEMAS}


def test_manage_notes_is_available_as_native_tool_schema():
    assert "manage_notes" in _schema_names()


def test_local_openai_compatible_hosts_get_native_tool_schemas():
    assert {"localhost", "127.0.0.1", "host.docker.internal"} <= _API_HOSTS
