import re
from spellchecker import SpellChecker

spell = SpellChecker()

# Common words that should not be treated as spelling errors
CUSTOM_WORDS = {
    "NLP",
    "AI",
    "Python",
    "JavaScript",
    "Flask",
    "HTML",
    "CSS",
    "MongoDB",
    "React",
    "DBIT",
    "Kurla"
}

spell.word_frequency.load_words(CUSTOM_WORDS)


def check_spelling(text):
    errors = []

    # Find words while keeping their positions
    matches = list(re.finditer(r"\b[A-Za-z]+\b", text))

    words = [match.group() for match in matches]

    # Convert to lowercase for checking
    words_lower = [word.lower() for word in words]

    unknown_words = spell.unknown(words_lower)

    for match, original_word in zip(matches, words):

        word_lower = original_word.lower()

        # Title-case words are commonly names, cities, organizations, or
        # other proper nouns. Do not replace them with dictionary guesses.
        is_proper_noun = (
            original_word[0].isupper()
            and original_word[1:].islower()
        )

        if word_lower in unknown_words and not is_proper_noun:

            suggestions = spell.candidates(word_lower)

            if suggestions:

                # Sort suggestions alphabetically and take top 5
                suggestions = sorted(
                    list(suggestions)
                )[:5]

                best_suggestion = spell.correction(word_lower)

                errors.append({
                    "type": "spelling",
                    "message": "Possible spelling mistake",
                    "word": original_word,
                    "suggestion": best_suggestion,
                    "suggestions": suggestions,
                    "offset": match.start(),
                    "length": len(original_word)
                })

    return errors