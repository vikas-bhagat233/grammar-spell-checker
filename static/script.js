const textInput = document.getElementById("textInput");
const wordCount = document.getElementById("wordCount");
let latestResult = null;
let currentErrors = [];


// Word counter
textInput.addEventListener("input", function () {

    const text = textInput.value.trim();

    if (!text) {
        wordCount.textContent = "0 words";
        return;
    }

    const words = text.split(/\s+/);

    wordCount.textContent =
        words.length + " words";
});


// Check text
async function checkText() {

    const text = textInput.value.trim();

    if (!text) {
        alert("Please enter some text first.");
        return;
    }

    const loading =
        document.getElementById("loading");

    const results =
        document.getElementById("results");

    const successMessage =
        document.getElementById("successMessage");

    loading.classList.remove("hidden");
    results.classList.add("hidden");
    successMessage.classList.add("hidden");


    try {

        const response = await fetch("/check", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                text: text
            })

        });


        const data = await response.json();


        if (!data.success) {
            throw new Error(data.error);
        }


        displayResults(data);
        saveHistory(data);


    } catch (error) {

        alert(
            "Error: " + error.message
        );

    } finally {

        loading.classList.add("hidden");

    }
}


// Display results
function displayResults(data) {
    latestResult = data;

    const spelling =
        data.spelling_errors || [];

    const grammar =
        data.grammar_errors || [];


    document.getElementById(
        "spellingCount"
    ).textContent = spelling.length;


    document.getElementById(
        "grammarCount"
    ).textContent = grammar.length;


    document.getElementById(
        "totalCount"
    ).textContent =
        data.total_errors;
    const qualityScore = Number(data.quality_score);
    document.getElementById("qualityScore").textContent =
        `${Number.isFinite(qualityScore) ? qualityScore : 0}/100`;


    const correctedText =
        document.getElementById(
            "correctedText"
        );


    correctedText.textContent =
        data.corrected_text;
    renderHighlights(data.original_text, [...spelling, ...grammar]);
    renderChart(spelling.length, grammar.length);


    const errorList =
        document.getElementById(
            "errorList"
        );


    errorList.innerHTML = "";


    const allErrors = [
        ...spelling,
        ...grammar
    ];
    currentErrors = allErrors;


    if (allErrors.length === 0) {

        document.getElementById(
            "results"
        ).classList.add("hidden");

        document.getElementById(
            "successMessage"
        ).classList.remove("hidden");

        return;
    }


    allErrors.forEach(error => {

        const item =
            document.createElement("div");

        item.className = "error-item";


        const type =
            error.type === "spelling"
                ? "Spelling"
                : "Grammar";


        item.innerHTML = `

            <div class="error-top">

                <span class="error-word">
                    ${escapeHTML(error.word)}
                </span>

                <span class="error-type">
                    ${type}
                </span>

            </div>

            <div class="error-message">
                ${escapeHTML(error.message)}
            </div>

            <div class="suggestion">
                Suggested correction:
                <span class="suggestion-buttons">
                    ${(error.suggestions || [error.suggestion]).map(suggestion =>
                        `<button class="suggestion-btn" onclick="applySuggestion(${error.offset}, ${error.length}, '${escapeAttribute(suggestion)}')">${escapeHTML(suggestion)}</button>`
                    ).join("") || "No suggestion"}
                </span>
            </div>

        `;


        errorList.appendChild(item);

    });


    document.getElementById(
        "results"
    ).classList.remove("hidden");

}


// Clear everything
function clearText() {

    textInput.value = "";

    wordCount.textContent = "0 words";

    document.getElementById(
        "results"
    ).classList.add("hidden");

    document.getElementById(
        "successMessage"
    ).classList.add("hidden");
    document.getElementById("highlightedText").innerHTML = "";
    latestResult = null;
}


// Copy corrected text
async function copyCorrection() {

    const text =
        document.getElementById(
            "correctedText"
        ).textContent;


    if (!text) {
        return;
    }


    try {

        await navigator.clipboard.writeText(text);

        alert("Corrected text copied!");

    } catch (error) {

        alert(
            "Unable to copy text."
        );

    }
}


// Prevent HTML injection
function escapeHTML(text) {

    const div =
        document.createElement("div");

    div.textContent = text;

    return div.innerHTML;
}

function escapeAttribute(text) {
    return String(text).replace(/\\/g, "\\\\").replace(/'/g, "\\'");
}

function applySuggestion(offset, length, suggestion) {
    const text = textInput.value;
    textInput.value = text.slice(0, offset) + suggestion + text.slice(offset + length);
    textInput.dispatchEvent(new Event("input"));
    checkText();
}

function renderHighlights(text, errors) {
    const target = document.getElementById("highlightedText");
    if (!target) return;
    const sorted = [...errors].sort((a, b) => a.offset - b.offset);
    let cursor = 0;
    target.innerHTML = "";
    sorted.forEach(error => {
        if (error.offset < cursor) return;
        target.appendChild(document.createTextNode(text.slice(cursor, error.offset)));
        const mark = document.createElement("mark");
        mark.className = error.type === "spelling" ? "spelling-mark" : "grammar-mark";
        mark.textContent = text.slice(error.offset, error.offset + error.length);
        mark.title = error.suggestion ? `Suggestion: ${error.suggestion}` : error.message;
        target.appendChild(mark);
        cursor = error.offset + error.length;
    });
    target.appendChild(document.createTextNode(text.slice(cursor)));
}

function renderChart(spelling, grammar) {
    const total = Math.max(spelling + grammar, 1);
    document.getElementById("errorChart").innerHTML = `
        <div class="bar-row"><span>Spelling</span><div class="bar"><i class="bar-spelling" style="width:${spelling / total * 100}%"></i></div><b>${spelling}</b></div>
        <div class="bar-row"><span>Grammar</span><div class="bar"><i class="bar-grammar" style="width:${grammar / total * 100}%"></i></div><b>${grammar}</b></div>`;
}

function downloadCorrection() {
    if (!latestResult) return;
    const blob = new Blob([latestResult.corrected_text], {type: "text/plain;charset=utf-8"});
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "corrected-text.txt";
    link.click();
    URL.revokeObjectURL(link.href);
}

async function uploadFile() {
    const file = document.getElementById("fileInput").files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    try {
        const response = await fetch("/upload", {method: "POST", body: formData});
        const data = await response.json();
        if (!data.success) throw new Error(data.error);
        textInput.value = data.text;
        textInput.dispatchEvent(new Event("input"));
    } catch (error) {
        alert("Upload error: " + error.message);
    }
}

function toggleDarkMode() {
    document.body.classList.toggle("dark-mode");
    localStorage.setItem("darkMode", document.body.classList.contains("dark-mode"));
}

function saveHistory(data) {
    const history = JSON.parse(localStorage.getItem("checkHistory") || "[]");
    history.unshift({
        text: data.original_text,
        score: data.quality_score,
        errors: data.total_errors,
        date: new Date().toLocaleString()
    });
    localStorage.setItem("checkHistory", JSON.stringify(history.slice(0, 10)));
    renderHistory();
}

function renderHistory() {
    const history = JSON.parse(localStorage.getItem("checkHistory") || "[]");
    const list = document.getElementById("historyList");
    if (!history.length) {
        list.innerHTML = '<p class="muted">Your recent checks will appear here.</p>';
        return;
    }
    list.innerHTML = history.map(item => `
        <button class="history-item" onclick="loadHistory(${JSON.stringify(item.text).replace(/"/g, "&quot;")})">
            <span>${escapeHTML(item.text.slice(0, 70))}${item.text.length > 70 ? "..." : ""}</span>
            <small>${item.score}/100 · ${item.errors} errors · ${escapeHTML(item.date)}</small>
        </button>`).join("");
}

function loadHistory(text) {
    textInput.value = text;
    textInput.dispatchEvent(new Event("input"));
    checkText();
}

function clearHistory() {
    localStorage.removeItem("checkHistory");
    renderHistory();
}

document.addEventListener("DOMContentLoaded", () => {
    if (localStorage.getItem("darkMode") === "true") document.body.classList.add("dark-mode");
    renderHistory();
});