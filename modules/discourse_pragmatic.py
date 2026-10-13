import re


PRONOUNS = {
    "he", "she", "it", "they", "them", "this", "that", "these", "those",
    "his", "her", "their", "its", "who", "which", "what", "where"
}


def _sentence_split(text):
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()]


def _extract_words(text):
    return re.findall(r"[A-Za-z']+", text.lower())


def _word_overlap(prev_words, current_words):
    prev_set = set(prev_words)
    current_set = set(current_words)
    if not prev_set or not current_set:
        return 0.0
    overlap = len(prev_set & current_set)
    union = len(prev_set | current_set)
    if union == 0:
        return 0.0
    return overlap / union


def analyze_discourse(text):
    """
    Discourse Analysis (rule-based approximation).

    This module performs a lightweight discourse check by evaluating continuity
    between sentences. It is not a full discourse parser, but it approximates the
    kind of analysis normally used to detect topic drift or unclear references.
    """
    sentences = _sentence_split(text)
    issues = []

    if len(sentences) < 2:
        return {
            "summary": "Only one sentence detected; discourse continuity is not strongly assessable.",
            "issues": issues,
            "status": "limited"
        }

    previous_words = _extract_words(sentences[0])

    for index in range(1, len(sentences)):
        sentence = sentences[index]
        current_words = _extract_words(sentence)
        overlap = _word_overlap(previous_words, current_words)

        # Detect abrupt topic shift between consecutive sentences.
        if overlap < 0.15:
            issues.append({
                "type": "discourse",
                "message": "Possible topic drift between sentences.",
                "word": sentence,
                "suggestion": "Add a transition or repeat context from the previous sentence.",
                "suggestions": [
                    "Add a transition word such as 'however', 'therefore', or 'also'.",
                    "Repeat the main topic to maintain sentence continuity."
                ],
                "offset": 0,
                "length": len(sentence)
            })

        # Detect unclear pronoun reference without a clear antecedent.
        sentence_pronouns = [word for word in _extract_words(sentence) if word in PRONOUNS]
        if sentence_pronouns and not previous_words:
            issues.append({
                "type": "discourse",
                "message": "Possible unclear pronoun reference in a new sentence.",
                "word": sentence,
                "suggestion": "Replace the pronoun with a specific noun to make the reference clearer.",
                "suggestions": [
                    "Use a repeated noun instead of a pronoun.",
                    "Add a clear subject before the pronoun."
                ],
                "offset": 0,
                "length": len(sentence)
            })

        previous_words = current_words

    if issues:
        summary = "Discourse analysis detected possible continuity or reference issues."
        status = "warning"
    else:
        summary = "Discourse structure appears coherent across sentences."
        status = "good"

    return {
        "summary": summary,
        "issues": issues,
        "status": status
    }


def analyze_pragmatic(text):
    """
    Pragmatic Analysis (rule-based approximation).

    This module estimates the communicative intent and tone of the text. It does
    not fully understand real-world context, but it can detect common pragmatic
    patterns such as polite requests, urgent messaging, question style, and chat
    informality.
    """
    normalized = text.lower()
    issues = []
    tone = "neutral"
    intent = "statement"

    if re.search(r"\?", text):
        intent = "question"
        issues.append({
            "type": "pragmatic",
            "message": "Question-oriented communication detected.",
            "word": "?",
            "suggestion": "Ensure the question is clear and precise.",
            "suggestions": [
                "Use clear wording to express the exact information needed.",
                "Add context if the question is ambiguous."
            ],
            "offset": text.find("?"),
            "length": 1
        })

    if re.search(r"!", text):
        issues.append({
            "type": "pragmatic",
            "message": "Exclamatory or emphatic tone detected.",
            "word": "!",
            "suggestion": "Use emphasis carefully; avoid sounding abrupt if the tone is not intended.",
            "suggestions": [
                "Use a formal tone if needed.",
                "Consider rewriting for a calmer professional tone."
            ],
            "offset": text.find("!"),
            "length": 1
        })

    polite_match = re.search(r"\b(?:please|kindly|could you|would you|may i|can you)\b", normalized)
    if polite_match:
        tone = "polite"
        intent = "request"
        issues.append({
            "type": "pragmatic",
            "message": "Polite request pattern detected.",
            "word": polite_match.group(0),
            "suggestion": "Keep the polite structure if you want a courteous tone.",
            "suggestions": [
                "Use polite phrasing for professional communication.",
                "Keep the request clear and specific."
            ],
            "offset": polite_match.start(),
            "length": len(polite_match.group(0))
        })

    urgency_match = re.search(r"\b(?:asap|urgent|immediately|now|quickly)\b", normalized)
    if urgency_match:
        tone = "urgent"
        intent = "request"
        issues.append({
            "type": "pragmatic",
            "message": "Urgency or time-sensitivity detected.",
            "word": urgency_match.group(0),
            "suggestion": "If urgency is important, mention the deadline clearly and professionally.",
            "suggestions": [
                "Use 'as soon as possible' or a specific deadline.",
                "State the reason for urgency when needed."
            ],
            "offset": urgency_match.start(),
            "length": len(urgency_match.group(0))
        })

    informal_markers = [
        "u", "r", "im", "pls", "plz", "thx", "ty", "omg", "wtf", "lol", "idk"
    ]
    if any(marker in normalized.split() for marker in informal_markers):
        tone = "informal"
        issues.append({
            "type": "pragmatic",
            "message": "Informal chat style detected.",
            "word": "informal",
            "suggestion": "Convert informal chat wording to standard English for formal writing.",
            "suggestions": [
                "Replace abbreviations with full words.",
                "Use a more formal tone for academic or professional text."
            ],
            "offset": 0,
            "length": len(text)
        })

    if not issues:
        summary = "No strong pragmatic cues were detected; the statement appears neutral and contextually balanced."
    else:
        summary = "Pragmatic analysis detected some tone or intention patterns in the text."

    return {
        "summary": summary,
        "issues": issues,
        "tone": tone,
        "intent": intent
    }
