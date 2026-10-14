import re


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


def check_grammar(text):
    """Apply local rule-based checks for basic English syntax and punctuation."""
    errors = []
    rules = (
        (
            r"\b(I)\s+is\b",
            "am",
            "Use 'am' with 'I'.",
        ),
        (
            r"\b(you|we|they)\s+is\b",
            "are",
            "Use 'are' with this subject.",
        ),
        (
            r"\b(he|she|it)\s+are\b",
            "is",
            "Use 'is' with this subject.",
        ),
        (
            r"\b(he|she|it)\s+don't\b",
            "doesn't",
            "Use 'doesn't' with this subject.",
        ),
        (
            r"\b([A-Za-z]+)\s+\1\b",
            None,
            "Remove the repeated word.",
        ),
    )

    for pattern, replacement, message in rules:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            matched_text = match.group()
            suggestion = (
                f"{match.group(1)} {replacement}"
                if replacement
                else match.group(1)
            )
            if (
                suggestion
                and (
                    match.start() == 0
                    or text[:match.start()].rstrip().endswith((".", "!", "?"))
                )
            ):
                suggestion = suggestion[0].upper() + suggestion[1:]
            errors.append({
                "type": "grammar",
                "message": message,
                "word": matched_text,
                "suggestion": suggestion,
                "suggestions": [suggestion],
                "offset": match.start(),
                "length": len(matched_text)
            })

    errors.extend(check_basic_punctuation(text))
    return errors


def check_semantics(text):
    """Normalize known chat abbreviations using explicit phrase mappings."""
    errors = []
    occupied_ranges = []

    for phrase, replacement in sorted(
        COMMON_ABBREVIATIONS.items(),
        key=lambda item: len(item[0]),
        reverse=True
    ):
        pattern = re.compile(
            rf"(?<![A-Za-z]){re.escape(phrase)}(?![A-Za-z])",
            re.IGNORECASE
        )
        for match in pattern.finditer(text):
            start = match.start()
            end = match.end()
            if any(start < old_end and end > old_start
                   for old_start, old_end in occupied_ranges):
                continue
            suggestion = replacement
            if (
                start == 0
                or text[:start].rstrip().endswith((".", "!", "?"))
            ):
                suggestion = suggestion[0].upper() + suggestion[1:]
            errors.append({
                "type": "semantic",
                "message": f"Expand the abbreviation to: {suggestion}",
                "word": match.group(),
                "suggestion": suggestion,
                "suggestions": [suggestion],
                "offset": start,
                "length": end - start
            })
            occupied_ranges.append((start, end))

    return errors


def check_basic_punctuation(text):
    """Check sentence-initial capitalization and final punctuation."""
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
