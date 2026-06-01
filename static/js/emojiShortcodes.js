// Convert common chat-style emoji shortcodes (:blush:, :microphone:) into
// Unicode before markdown's existing monochrome emoji pass runs.

const SHORTCODE_TO_EMOJI = Object.freeze({
  blush: '\u{1f60a}',
  blushes: '\u{1f60a}',
  smile: '\u{1f604}',
  smiling: '\u{1f604}',
  grin: '\u{1f601}',
  joy: '\u{1f602}',
  laugh: '\u{1f602}',
  laughing: '\u{1f602}',
  wink: '\u{1f609}',
  heart: '\u{2764}\u{fe0f}',
  red_heart: '\u{2764}\u{fe0f}',
  thumbs_up: '\u{1f44d}',
  thumbsup: '\u{1f44d}',
  '+1': '\u{1f44d}',
  thumbs_down: '\u{1f44e}',
  '-1': '\u{1f44e}',
  ok_hand: '\u{1f44c}',
  clap: '\u{1f44f}',
  fire: '\u{1f525}',
  tada: '\u{1f389}',
  eyes: '\u{1f440}',
  thinking: '\u{1f914}',
  rocket: '\u{1f680}',
  microphone: '\u{1f3a4}',
  mic: '\u{1f3a4}',
  music: '\u{1f3b5}',
  musical_note: '\u{1f3b5}',
  notes: '\u{1f3b6}',
  emoji: '\u{1f642}',
});

const SHORTCODE_RE = /:([a-z0-9_+-]+):/gi;

function _lookupShortcode(name) {
  const normalized = String(name || '').toLowerCase().replace(/-/g, '_');
  return SHORTCODE_TO_EMOJI[normalized] || null;
}

export function expandEmojiShortcodesInText(text) {
  if (!text || !String(text).includes(':')) return text;
  return String(text).replace(SHORTCODE_RE, (match, name) => {
    return _lookupShortcode(name) || match;
  });
}

export function expandEmojiShortcodesInHtml(html) {
  if (!html || !String(html).includes(':')) return html;

  const parts = String(html).split(/(<[^>]*>)/);
  let codeDepth = 0;

  for (let i = 0; i < parts.length; i += 1) {
    if (i % 2 === 1) {
      const tag = parts[i].toLowerCase();
      if (/^<(pre|code)[\s>]/.test(tag)) codeDepth += 1;
      else if (/^<\/(pre|code)\s*>/.test(tag)) codeDepth = Math.max(0, codeDepth - 1);
      continue;
    }
    if (codeDepth === 0 && parts[i].includes(':')) {
      parts[i] = expandEmojiShortcodesInText(parts[i]);
    }
  }

  return parts.join('');
}

export default {
  expandEmojiShortcodesInText,
  expandEmojiShortcodesInHtml,
};
