import language_tool_python
import re

_tool = None

COMMON_ABBREVIATIONS = {
    "who r u": "Who are you?",
    "what r u": "What are you?",
    "where r u": "Where are you?",
    "how r u": "How are you?",
    "i am fine": "I am fine.",
    "im fine": "I am fine.",
    "u r": "you are",
    "ur": "your",
    "r": "are",
    "u": "you",
    "pls": "please",
    "plz": "please",
    "thx": "thanks",
    "ty": "thank you",
    "asap": "as soon as possible",
}


def get_tool():
    global _tool

    if _tool is None:
        _tool = language_tool_python.LanguageTool("en-US")

    return _tool


def check_grammar(text):
    errors = []
    abbreviation_errors = check_abbreviations(text)

    # Do not let LanguageTool create competing replacements for chat
    # abbreviations. The phrase-level correction is more reliable.
    if abbreviation_errors:
        errors.extend(abbreviation_errors)
        return errors

    tool = get_tool()
    matches = tool.check(text)

    for match in matches:

        # Ignore very minor style suggestions
        if match.ruleIssueType not in [
            "grammar",
            "misspelling",
            "typographical"
        ]:
            continue

        matched_text = text[match.offset:match.offset + match.errorLength]
        words = re.findall(r"[A-Za-z]+", matched_text)

        # LanguageTool can mistake names and place names for misspellings.
        # Preserve title-case words rather than applying a guessed replacement.
        if words and all(
            word[0].isupper() and word[1:].islower()
            for word in words
        ):
            continue

        replacements = match.replacements[:5]

        suggestion = (
            replacements[0]
            if replacements
            else ""
        )

        errors.append({
            "type": "grammar",
            "message": match.message,
            "word": text[
                match.offset:
                match.offset + match.errorLength
            ],
            "suggestion": suggestion,
            "suggestions": replacements,
            "offset": match.offset,
            "length": match.errorLength
        })

    errors.extend(check_basic_punctuation(text))
    return errors


def check_abbreviations(text):
    errors = []
    occupied_ranges = []
    for phrase, replacement in sorted(
        COMMON_ABBREVIATIONS.items(),
        key=lambda item: len(item[0]),
        reverse=True
    ):
        pattern = re.compile(rf"(?<![A-Za-z]){re.escape(phrase)}(?![A-Za-z])", re.I)
        for match in pattern.finditer(text):
            start = match.start()
            end = match.end()
            if any(start < old_end and end > old_start
                   for old_start, old_end in occupied_ranges):
                continue
            errors.append({
                "type": "grammar",
                "message": f"Use the proper form: {replacement}",
                "word": match.group(),
                "suggestion": replacement,
                "suggestions": [replacement],
                "offset": start,
                "length": end - start
            })
            occupied_ranges.append((start, end))
    return errors


def check_basic_punctuation(text):
    errors = []
    for match in re.finditer(r"(?m)(^|[.!?]\s+)([a-z])", text):
        offset = match.start(2)
        errors.append({
            "type": "grammar",
            "message": "The first letter of a sentence should be capitalized",
            "word": match.group(2),
            "suggestion": match.group(2).upper(),
            "suggestions": [match.group(2).upper()],
            "offset": offset,
            "length": 1
        })

    stripped = text.rstrip()
    if stripped and stripped[-1] not in ".!?":
        errors.append({
            "type": "grammar",
            "message": "Add punctuation at the end of the sentence",
            "word": "",
            "suggestion": ".",
            "suggestions": ["."],
            "offset": len(text),
            "length": 0
        })

    return errors