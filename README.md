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
- PySpellChecker
- LanguageTool
- Natural Language Processing

## Features

- Spelling error detection
- Grammar error detection
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

### 2. Syntactic Analysis
- Implemented in: `modules/grammar_checker.py`
- Purpose: check grammar, sentence structure, punctuation, and capitalization.
- Example: detecting missing punctuation, improper capitalization, sentence-level grammar issues.
- Role in this project: LanguageTool is used to detect grammar and spelling issues, while custom rules identify punctuation and capitalization problems.

### 3. Semantic Analysis (Limited)
- Implemented in: `modules/grammar_checker.py` and `modules/correction.py`
- Purpose: map informal or incorrect phrases to their correct meaning.
- Example: `"u" -> "you"`, `"r" -> "are"`, `"pls" -> "please"`.
- Role in this project: this is a shallow semantic layer because it recognizes common abbreviations and transforms them to proper English.
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
3. `check_spelling()` identifies misspelled words
4. `check_grammar()` detects grammar and punctuation issues
5. `analyze_discourse()` checks sentence continuity and reference clarity
6. `analyze_pragmatic()` detects tone and intent patterns
7. `apply_corrections()` applies the suggested replacements
8. Final corrected text and analysis results are returned to the user

## How to Run

Install dependencies:

pip install -r requirements.txt

Run the application:

python app.py

Open:

http://127.0.0.1:5000

