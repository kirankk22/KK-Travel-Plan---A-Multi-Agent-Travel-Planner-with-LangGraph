
const form = document.getElementById("travel-form");
const queryInput = document.getElementById("travel-query");
const submitButton = document.getElementById("submit-button");
const buttonLabel = document.getElementById("button-label");

const loadingPanel = document.getElementById("loading-panel");
const errorPanel = document.getElementById("error-panel");
const errorMessage = document.getElementById("error-message");
const resultsPanel = document.getElementById("results-panel");

const itineraryContent = document.getElementById("itinerary-content");
const flightContent = document.getElementById("flight-content");
const hotelContent = document.getElementById("hotel-content");
const resultMeta = document.getElementById("result-meta");

let currentThreadId = null;

function setLoading(isLoading) {
    submitButton.disabled = isLoading;
    buttonLabel.textContent = isLoading ? "Planning your trip..." : "Plan my trip";
    loadingPanel.hidden = !isLoading;

    if (isLoading) {
        errorPanel.hidden = true;
        resultsPanel.hidden = true;
    }
}

function showError(message) {
    errorMessage.textContent = message;
    errorPanel.hidden = false;
}


function renderPlainText(container, value, emptyMessage) {
    container.replaceChildren();

    if (typeof value !== "string" || !value.trim()) {
        const paragraph = document.createElement("p");
        paragraph.className = "empty-message";
        paragraph.textContent = emptyMessage;
        container.appendChild(paragraph);
        return;
    }

    if (
        typeof window.marked === "undefined" ||
        typeof window.DOMPurify === "undefined"
    ) {
        // Safe fallback if the external libraries are unavailable.
        const pre = document.createElement("pre");
        pre.textContent = value;
        pre.style.margin = "0";
        pre.style.fontFamily = "inherit";
        pre.style.whiteSpace = "pre-wrap";
        container.appendChild(pre);
        return;
    }

    const rawHtml = window.marked.parse(value, {
        gfm: true,
        breaks: false,
    });

    const safeHtml = window.DOMPurify.sanitize(rawHtml, {
        USE_PROFILES: { html: true },
    });

    container.innerHTML = safeHtml;
}


function displayResults(data) {
    renderPlainText(
        itineraryContent,
        data.answer || data.itinerary,
        "No itinerary was returned."
    );

    renderPlainText(
        flightContent,
        data.flight_results,
        "No flight information was returned."
    );

    renderPlainText(
        hotelContent,
        data.hotel_results,
        "No accommodation information was returned."
    );

    currentThreadId = data.thread_id || currentThreadId;

    resultMeta.textContent = currentThreadId
        ? `Trip generated · Thread ${currentThreadId}`
        : "Your travel plan has been generated.";

    resultsPanel.hidden = false;
    resultsPanel.scrollIntoView({ behavior: "smooth", block: "start" });
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const query = queryInput.value.trim();

    if (query.length < 5) {
        showError("Please enter a little more detail about your trip.");
        return;
    }

    setLoading(true);

    try {
        const response = await fetch("/api/plan", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                query,
                thread_id: null,
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "The travel planner could not complete your request."
            );
        }

        displayResults(data);
    } catch (error) {
        showError(
            error instanceof Error
                ? error.message
                : "Something went wrong. Please try again."
        );
    } finally {
        setLoading(false);
    }
});

document.querySelectorAll("[data-prompt]").forEach((button) => {
    button.addEventListener("click", () => {
        queryInput.value = button.dataset.prompt || "";
        queryInput.focus();
    });
});

document.getElementById("new-trip-button").addEventListener("click", () => {
    queryInput.value = "";
    currentThreadId = null;
    resultsPanel.hidden = true;
    errorPanel.hidden = true;
    queryInput.focus();
    document.getElementById("planner-title").scrollIntoView({
        behavior: "smooth",
        block: "center",
    });
});
