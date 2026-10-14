import re

from flask import Flask, jsonify, render_template, request

# NLP Pipeline Flow in this project:
# 1. Lexical Analysis -> dictionary-backed check_spelling()
# 2. Syntactic Analysis -> local rules in check_grammar()
# 3. Semantic Analysis -> mapped phrase normalization in check_semantics()
# 4. Discourse Analysis -> analyze_discourse()
# 5. Pragmatic Analysis -> analyze_pragmatic()
# 6. Correction Engine -> apply_corrections()
# 7. All five analysis stages are returned to the frontend as JSON

from modules.spell_checker import check_spelling
from modules.grammar_checker import check_grammar, check_semantics
from modules.correction import apply_corrections
from modules.discourse_pragmatic import analyze_discourse, analyze_pragmatic

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/check", methods=["POST"])
def check_text():
    try:
        data = request.get_json()

        if not data or "text" not in data:
            return jsonify({
                "success": False,
                "error": "No text provided."
            }), 400

        text = data["text"].strip()

        if not text:
            return jsonify({
                "success": False,
                "error": "Please enter some text."
            }), 400

        # Spell checking
        spelling_errors = check_spelling(text)

        # Grammar checking
        grammar_errors = check_grammar(text)
        semantic_errors = check_semantics(text)

        # Keep dictionary suggestions from duplicating phrase-level findings.
        handled_ranges = [
            (error["offset"], error["offset"] + error["length"])
            for error in grammar_errors + semantic_errors
        ]
        spelling_errors = [
            error
            for error in spelling_errors
            if not any(
                error["offset"] < end
                and error["offset"] + error["length"] > start
                for start, end in handled_ranges
            )
        ]

        tokens = re.findall(r"\b[A-Za-z]+\b", text)
        lexical_summary = (
            f"Tokenized {len(tokens)} words with the built-in English dictionary; "
            f"{len(spelling_errors)} possible spelling issue(s) found."
        )
        syntactic_summary = (
            f"Local grammar rules checked subject-verb agreement, repeated words, "
            f"capitalization, and sentence punctuation; "
            f"{len(grammar_errors)} issue(s) found."
        )
        semantic_summary = (
            f"Checked common chat abbreviations against phrase mappings; "
            f"{len(semantic_errors)} abbreviation(s) found."
        )

        # Discourse analysis: detect topic continuity and reference clarity.
        discourse_analysis = analyze_discourse(text)

        # Pragmatic analysis: detect tone, intent, and style markers.
        pragmatic_analysis = analyze_pragmatic(text)

        # Combine corrections
        all_corrections = grammar_errors + semantic_errors + spelling_errors

        corrected_text = apply_corrections(
            text,
            all_corrections
        )

        word_count = len(text.split())
        error_count = len(all_corrections)
        # Penalize each issue without allowing a few short-text issues
        # to collapse every result to zero.
        quality_score = max(0, min(100, 100 - (error_count * 10)))

        return jsonify({
            "success": True,
            "original_text": text,
            "corrected_text": corrected_text,
            "spelling_errors": spelling_errors,
            "grammar_errors": grammar_errors,
            "semantic_errors": semantic_errors,
            "discourse_analysis": discourse_analysis["issues"],
            "discourse_summary": discourse_analysis["summary"],
            "discourse_status": discourse_analysis["status"],
            "pragmatic_analysis": pragmatic_analysis["issues"],
            "pragmatic_summary": pragmatic_analysis["summary"],
            "pragmatic_tone": pragmatic_analysis["tone"],
            "pragmatic_intent": pragmatic_analysis["intent"],
            "nlp_stages": [
                {
                    "id": "lexical",
                    "title": "Lexical Analysis",
                    "status": "warning" if spelling_errors else "complete",
                    "summary": lexical_summary,
                    "tokens": tokens,
                    "source_url": "https://github.com/barrust/pyspellchecker/blob/master/spellchecker/resources/en.json.gz",
                    "source_label": "View PySpellChecker English dictionary (en.json.gz)",
                    "findings": spelling_errors,
                },
                {
                    "id": "syntactic",
                    "title": "Syntactic Analysis",
                    "status": "warning" if grammar_errors else "complete",
                    "summary": syntactic_summary,
                    "findings": grammar_errors,
                },
                {
                    "id": "semantic",
                    "title": "Semantic Analysis",
                    "status": "warning" if semantic_errors else "complete",
                    "summary": semantic_summary,
                    "findings": semantic_errors,
                },
                {
                    "id": "discourse",
                    "title": "Discourse Analysis",
                    "status": discourse_analysis["status"],
                    "summary": discourse_analysis["summary"],
                    "findings": discourse_analysis["issues"],
                },
                {
                    "id": "pragmatic",
                    "title": "Pragmatic Analysis",
                    "status": "complete" if not pragmatic_analysis["issues"] else "info",
                    "summary": pragmatic_analysis["summary"],
                    "details": [
                        f"Tone: {pragmatic_analysis['tone']}",
                        f"Intent: {pragmatic_analysis['intent']}",
                    ],
                    "findings": pragmatic_analysis["issues"],
                },
            ],
            "total_errors": error_count,
            "word_count": word_count,
            "quality_score": quality_score
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/upload", methods=["POST"])
def upload_text():
    uploaded_file = request.files.get("file")

    if not uploaded_file or not uploaded_file.filename:
        return jsonify({"success": False, "error": "Please choose a text file."}), 400

    if not uploaded_file.filename.lower().endswith(".txt"):
        return jsonify({"success": False, "error": "Only .txt files are supported."}), 400

    try:
        text = uploaded_file.read().decode("utf-8")
    except UnicodeDecodeError:
        return jsonify({
            "success": False,
            "error": "The file must be a valid UTF-8 text file."
        }), 400

    return jsonify({"success": True, "text": text})


if __name__ == "__main__":
    app.run(
        debug=True,
        use_reloader=False,
        host="127.0.0.1",
        port=5000
    )