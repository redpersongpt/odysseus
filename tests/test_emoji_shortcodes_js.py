import json
import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent
_HAS_NODE = shutil.which("node") is not None


def _run_node(script: str) -> dict:
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        cwd=_REPO,
        capture_output=True,
        timeout=15,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout.splitlines()[-1])


@pytest.mark.skipif(not _HAS_NODE, reason="node binary not on PATH")
def test_expands_common_model_emoji_shortcodes():
    script = textwrap.dedent(
        """
        const { expandEmojiShortcodesInText } = await import('./static/js/emojiShortcodes.js');
        const out = expandEmojiShortcodesInText('hello :blush: sing :microphone: **:emoji:**');
        console.log(JSON.stringify({
          has_blush: out.includes('\\u{1f60a}'),
          has_microphone: out.includes('\\u{1f3a4}'),
          has_generic: out.includes('\\u{1f642}'),
          keeps_text: out.includes('hello') && out.includes('sing'),
        }));
        """
    )
    assert _run_node(script) == {
        "has_blush": True,
        "has_microphone": True,
        "has_generic": True,
        "keeps_text": True,
    }


@pytest.mark.skipif(not _HAS_NODE, reason="node binary not on PATH")
def test_does_not_expand_shortcodes_inside_code_blocks():
    script = textwrap.dedent(
        """
        const { expandEmojiShortcodesInHtml } = await import('./static/js/emojiShortcodes.js');
        const out = expandEmojiShortcodesInHtml('<p>:blush:</p><pre><code>:microphone:</code></pre>');
        console.log(JSON.stringify({
          expanded_paragraph: out.includes('\\u{1f60a}'),
          kept_code: out.includes('<code>:microphone:</code>'),
        }));
        """
    )
    assert _run_node(script) == {
        "expanded_paragraph": True,
        "kept_code": True,
    }
