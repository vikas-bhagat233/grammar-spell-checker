from flask import Flask, jsonify, render_template, request

from modules.spell_checker import check_spelling
from modules.grammar_checker import check_grammar
from modules.correction import apply_corrections

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

        # Combine corrections
        all_corrections = spelling_errors + grammar_errors

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