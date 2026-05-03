"""
Utility: sentence_splitter
Splits English text into individual sentences while handling common edge cases:
- Abbreviations (Mr., Mrs., Dr., Prof., e.g., i.e., etc.)
- Decimal numbers (3.14, $1.99)
- Ellipsis (...)
- Quoted sentences ("Hello." said John.)
- Multiple punctuation (!?, ?!)
"""
import re
from typing import List

# Abbreviations that should NOT end a sentence
_ABBREVS = {
    "mr", "mrs", "ms", "dr", "prof", "sr", "jr", "vs",
    "e.g", "i.e", "etc", "approx", "dept", "est",
    "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "oct", "nov", "dec",
    "st", "ave", "blvd", "corp", "inc", "ltd", "co",
    "u.s", "u.k", "u.n",
}

# Sentence-ending punctuation pattern, handles .  !  ?  ...  !?  ?!
_SENTENCE_END = re.compile(
    r'(?<!\.\.)(?<!\w\.\w)'   # not inside abbreviation with mid-word dots
    r'([.!?]+)'               # one or more terminal punctuation
    r'(?=[\s\'"»)\]]|$)',     # followed by whitespace or quote/close bracket
    re.UNICODE,
)


def _is_abbreviation_dot(text: str, dot_pos: int) -> bool:
    """Return True if the dot at dot_pos is part of an abbreviation, not end of sentence."""
    # Extract the word just before this dot
    before = text[:dot_pos].rstrip()
    word_match = re.search(r'\b(\w+)$', before, re.IGNORECASE)
    if not word_match:
        return False
    word = word_match.group(1).lower()
    # Single capital letter initials (e.g. "J.", "A.")
    if len(word) == 1 and word.isalpha():
        return True
    return word in _ABBREVS


def split_sentences(text: str) -> List[str]:
    """
    Split a passage into a list of clean sentences.
    Returns a list of non-empty sentence strings.
    """
    if not text or not text.strip():
        return []

    # Normalize whitespace
    text = re.sub(r'\r\n|\r', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)

    # Protect ellipsis by replacing with placeholder
    text = text.replace('...', '⟦ELL⟧')

    # Protect abbreviations by replacing period with placeholder
    def protect_abbrev(m):
        word = m.group(1)
        if word.lower() in _ABBREVS or (len(word) == 1 and word.isalpha()):
            return word + '⟦DOT⟧'
        return word + '.'

    text = re.sub(r'\b([A-Za-z]{1,6})\.',  protect_abbrev, text)

    # Protect decimal numbers (3.14, $1.99, 99.9%)
    text = re.sub(r'(\d+)\.(\d+)', r'\1⟦NUM⟧\2', text)

    # Split on sentence-ending punctuation
    parts = re.split(r'([.!?]+(?:\s|$))', text)

    sentences = []
    buf = ''
    for part in parts:
        buf += part
        stripped = buf.strip()
        if re.search(r'[.!?]$', stripped):
            sentences.append(stripped)
            buf = ''

    if buf.strip():
        sentences.append(buf.strip())

    # Restore placeholders
    result = []
    for s in sentences:
        s = s.replace('⟦ELL⟧', '...')
        s = s.replace('⟦DOT⟧', '.')
        s = s.replace('⟦NUM⟧', '.')
        s = s.strip()
        if s:
            result.append(s)

    return result


def split_to_sentence_dicts(text: str) -> List[dict]:
    """
    Split text and return list of sentence dicts matching PracticePassage.sentences_json format.
    Each dict: {index, text, translation_vi, audio_url}
    translation_vi and audio_url are left as None — to be filled later.
    """
    sentences = split_sentences(text)
    return [
        {
            "index": i,
            "text": sentence,
            "translation_vi": None,
            "audio_url": None,
        }
        for i, sentence in enumerate(sentences)
    ]
