# Grammar and Spell Checker

## NLP Mini Project

A web-based Natural Language Processing application that detects spelling
and grammatical errors in English text and provides correction suggestions.

## Technologies

- Python
- Flask
- HTML
- CSS
- JavaScript
- PySpellChecker's bundled English dictionary
- Natural Language Processing

## Features

- Spelling error detection
- Rule-based grammar and punctuation checks
- Dictionary-based spelling detection
- Five-stage lexical, syntactic, semantic, discourse, and pragmatic analysis
- Correction suggestions
- Automatically corrected text
- Error statistics
- Word counter
- Copy corrected text
- Upload `.txt` files and download corrected text
- Clickable correction suggestions
- Highlighted spelling and grammar errors
- Writing quality score
- Dark mode
- Error breakdown chart
- Recent-check history stored in the browser
- Common chat abbreviations expanded to proper English
- Proper punctuation and sentence capitalization checks
- Responsive web interface

## Project Architecture

User
↓
Web Interface
↓
Flask Backend
↓
Text Processing
↓
Spell Checker + Grammar Checker
↓
Correction Engine
↓
Corrected Text

## NLP Stages in This Project

This project implements a simplified NLP pipeline for English grammar and spelling correction. The stages below show how the application works in practice:

### 1. Lexical Analysis
- Implemented in: `modules/spell_checker.py`
- Purpose: split the text into words and identify tokens.
- Example: `"I am goin to collge tommorow."` is tokenized into words like `I`, `am`, `goin`, `to`, `collge`, `tommorow`.
- Role in this project: spelling detection uses regex-based tokenization and dictionary lookup.
- Dictionary source: [PySpellChecker bundled English dictionary (`en.json.gz`)](https://github.com/barrust/pyspellchecker/blob/master/spellchecker/resources/en.json.gz).

### 2. Syntactic Analysis
- Implemented in: `modules/grammar_checker.py`
- Purpose: check grammar, sentence structure, punctuation, and capitalization.
- Example: detecting selected subject-verb agreement patterns, repeated words, missing punctuation, and improper capitalization.
- Role in this project: local Python rules perform these checks without an external grammar service.
- Limitation: these rules cover common examples and are not a complete grammar checker.

### 3. Semantic Analysis (Limited)
- Implemented in: `modules/grammar_checker.py`
- Purpose: map informal or incorrect phrases to their correct meaning.
- Example: `"u" -> "you"`, `"r" -> "are"`, `"pls" -> "please"`.
- Role in this project: explicit abbreviation mappings produce semantic findings and correction suggestions.
- Limitation: the project does not deeply analyze sentence meaning or context.

### 4. Discourse Analysis
- Implemented as a lightweight rule-based layer in `modules/discourse_pragmatic.py`
- Purpose: analyze how sentences relate to each other across a paragraph or conversation.
- Example checks include:
  - sentence-to-sentence topic continuity
  - sudden topic drift
  - unclear pronoun references
- Limitation: this is a simplified discourse model, not a full discourse parser.

### 5. Pragmatic Analysis
- Implemented as a lightweight rule-based layer in `modules/discourse_pragmatic.py`
- Purpose: interpret user intent, tone, and social communication style.
- Example checks include:
  - formal vs informal tone
  - polite request detection
  - urgent communication detection
  - question and exclamation patterns
- Limitation: this is heuristic-based and does not fully understand deep social context.

## NLP Pipeline in the Application

1. User enters text in the web interface
2. Flask server receives the request in `app.py`
3. Lexical analysis tokenizes the text and looks up words in PySpellChecker's English dictionary
4. Syntactic analysis applies local grammar, capitalization, and punctuation rules
5. Semantic analysis checks known informal phrases against explicit abbreviation mappings
6. Discourse analysis checks sentence continuity and reference clarity
7. Pragmatic analysis detects heuristic tone and intent patterns
8. The UI displays the result of each stage; `apply_corrections()` applies supported suggestions

## How to Run

Install dependencies:

pip install -r requirements.txt

Run the application:

python app.py

Open:

http://127.0.0.1:5000
