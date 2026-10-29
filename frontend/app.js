document.addEventListener("DOMContentLoaded", () => {
    const tripForm = document.getElementById("trip-form");

    if (!tripForm) {
        console.error("TripSync AI: Trip form not found.");
        return;
    }

    const submitButton = tripForm.querySelector('button[type="submit"]');
    const formMessage = document.getElementById("form-message");

    // Local development URL. Change this when you deploy the backend.
    const API_URL = "http://127.0.0.1:8000/api/plan-trip";

    let budgetChart = null;
    let currentTrip = null;
    let currentBudget = 0;

    function formatCurrency(amount) {
        return new Intl.NumberFormat("en-IN", {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 0
        }).format(Number(amount) || 0);
    }

    function formatPDFCurrency(amount) {
        return "INR " + new Intl.NumberFormat("en-IN", {
            maximumFractionDigits: 0
        }).format(Math.round(Number(amount) || 0));
    }

    function escapeHTML(value) {
        return String(value ?? "").replace(/[&<>"']/g, character => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        })[character]);
    }

    function showMessage(message, type = "info") {
        if (!formMessage) return;

        formMessage.textContent = message;
        formMessage.className = `form-message ${type}`;
        formMessage.style.display = "block";
    }

    function getAgentName(agent) {
        const names = {
            transport: "Transport Agent",
            stay: "Stay Agent",
            activities: "Activities Agent",
            food: "Food Agent"
        };

        const key = String(agent || "").toLowerCase();

        return names[key] || agent || "Specialist Agent";
    }

    function getRecommendation(report) {
        const recommendation =
            report.ai_recommendation || report.recommendation;

        if (typeof recommendation === "string") {
            return recommendation;
        }

        if (recommendation && typeof recommendation === "object") {
            return Object.entries(recommendation)
                .map(([key, value]) => `${key}: ${value}`)
                .join("\n");
        }

        return "No recommendation available.";
    }

    function formatDate(value) {
        if (!value) return "Not specified";

        const date = new Date(`${value}T00:00:00`);

        if (Number.isNaN(date.getTime())) {
            return String(value);
        }

        return date.toLocaleDateString("en-IN", {
            day: "numeric",
            month: "short",
            year: "numeric"
        });
    }

    function getReportTotal(reports) {
        return reports.reduce(
            (sum, report) =>
                sum + (Number(report.estimated_cost) || 0),
            0
        );
    }

    // =====================================
    // RESULTS DASHBOARD
    // =====================================

    function displayTripResult(trip, userBudget) {
        let resultSection = document.getElementById("trip-result");

        if (!resultSection) {
            resultSection = document.createElement("section");
            resultSection.id = "trip-result";
            resultSection.className = "trip-result";

            tripForm.insertAdjacentElement(
                "afterend",
                resultSection
            );
        }

        const reports = Array.isArray(trip.reports)
            ? trip.reports
            : [];

        const budgetReport = trip.budget_report || {};

        const estimatedTotal = Number(
            budgetReport.estimated_total ?? getReportTotal(reports)
        );

        const budget = Number(userBudget) || 0;
        const remainingBudget = budget - estimatedTotal;

        const withinBudget =
            budgetReport.within_budget === true;

        const initialTotal = Number(
            trip.initial_total ?? estimatedTotal
        );

        const savings = Math.max(
            0,
            initialTotal - estimatedTotal
        );

        const overBudget = Math.max(
            0,
            estimatedTotal - budget
        );

        const aiCount = Number(
            trip.ai_enabled_count ??
            reports.filter(report => report.ai_recommendation).length
        );

        const duration = Number(trip.days) || 0;
        const nights = Number(trip.nights) || 0;
        const travelers = Number(trip.travelers) || 1;

        const budgetPercentage = budget > 0
            ? Math.min((estimatedTotal / budget) * 100, 100)
            : 0;

        resultSection.innerHTML = `
            <div class="results-dashboard">

                <div class="results-heading">
                    <div>
                        <span class="results-eyebrow">
                            YOUR PERSONALIZED ITINERARY
                        </span>

                        <h2>Your Trip Plan</h2>

                        <p>
                            Designed around your destination,
                            travel dates and budget.
                        </p>
                    </div>

                    <span class="results-status ${
                        withinBudget
                            ? "status-success"
                            : "status-warning"
                    }">
                        ${
                            withinBudget
                                ? "Within Budget"
                                : "Over Budget"
                        }
                    </span>
                </div>

                <div class="trip-overview-grid">

                    <article class="overview-card">
                        <span class="overview-icon">📍</span>
                        <p>Destination</p>

                        <h3>
                            ${escapeHTML(
                                trip.destination || "Not specified"
                            )}
                        </h3>

                        <small>
                            From ${escapeHTML(trip.origin || "Delhi")}
                        </small>
                    </article>

                    <article class="overview-card">
                        <span class="overview-icon">📅</span>
                        <p>Duration</p>
                        <h3>${duration} Days</h3>
                        <small>${nights} nights</small>
                    </article>

                    <article class="overview-card">
                        <span class="overview-icon">👥</span>
                        <p>Travelers</p>
                        <h3>${travelers}</h3>
                        <small>People traveling</small>
                    </article>

                    <article class="overview-card">
                        <span class="overview-icon">🤖</span>
                        <p>AI Specialists</p>
                        <h3>${aiCount}/${reports.length}</h3>
                        <small>Using Gemini recommendations</small>
                    </article>

                </div>

                <div class="results-main-grid">

                    <article class="results-panel budget-panel">

                        <div class="panel-heading">
                            <div>
                                <span class="panel-kicker">
                                    FINANCIAL OVERVIEW
                                </span>
                                <h3>Budget Summary</h3>
                            </div>

                            <span class="panel-icon">💰</span>
                        </div>

                        <div class="budget-total">
                            <span>Final Estimated Trip Cost</span>
                            <strong>
                                ${formatCurrency(estimatedTotal)}
                            </strong>
                        </div>

                        <div class="budget-progress-track">
                            <div
                                class="budget-progress-fill ${
                                    withinBudget
                                        ? "progress-safe"
                                        : "progress-over"
                                }"
                                style="width: ${budgetPercentage}%"
                            ></div>
                        </div>

                        <div class="budget-comparison">
                            <span>Your budget</span>
                            <strong>${formatCurrency(budget)}</strong>
                        </div>

                        <div class="budget-comparison">
                            <span>Initial estimated cost</span>
                            <strong>${formatCurrency(initialTotal)}</strong>
                        </div>

                        <div class="budget-comparison">
                            <span>Estimated savings</span>
                            <strong class="text-success">
                                ${formatCurrency(savings)}
                            </strong>
                        </div>

                        <div class="budget-comparison">
                            <span>
                                ${
                                    remainingBudget >= 0
                                        ? "Budget remaining"
                                        : "Amount over budget"
                                }
                            </span>

                            <strong class="${
                                remainingBudget >= 0
                                    ? "text-success"
                                    : "text-danger"
                            }">
                                ${formatCurrency(
                                    Math.abs(remainingBudget)
                                )}
                            </strong>
                        </div>

                        <div class="budget-status-message ${
                            withinBudget
                                ? "budget-message-success"
                                : "budget-message-warning"
                        }">
                            ${
                                withinBudget
                                    ? "Your estimated trip cost fits within your budget."
                                    : `The available options could not fully meet your budget. The current estimate is ${formatCurrency(overBudget)} over budget.`
                            }
                        </div>

                    </article>

                    <article class="results-panel chart-panel">

                        <div class="panel-heading">
                            <div>
                                <span class="panel-kicker">
                                    COST BREAKDOWN
                                </span>
                                <h3>Where Your Money Goes</h3>
                            </div>

                            <span class="panel-icon">📊</span>
                        </div>

                        <div class="chart-container">
                            <canvas
                                id="budget-chart"
                                aria-label="Trip cost breakdown chart"
                            ></canvas>

                            <p id="chart-unavailable" hidden>
                                The chart library is unavailable.
                                Your cost breakdown is shown below.
                            </p>
                        </div>

                        <div
                            id="cost-breakdown-list"
                            class="cost-breakdown-list"
                        ></div>

                    </article>

                </div>

                <div class="results-panel specialists-panel">

                    <div class="panel-heading">
                        <div>
                            <span class="panel-kicker">
                                MULTI-AGENT INTELLIGENCE
                            </span>

                            <h3>Your Specialist Recommendations</h3>

                            <p>
                                Each agent focuses on a different
                                part of your journey.
                            </p>
                        </div>
                    </div>

                    <div class="agent-results">

                        ${reports.map((report, index) => {
                            const recommendation =
                                getRecommendation(report);

                            const agentName =
                                getAgentName(report.agent);

                            const cost =
                                Number(report.estimated_cost) || 0;

                            const aiUsed =
                                Boolean(report.ai_recommendation);

                            return `
                                <article class="agent-result-card">

                                    <div class="agent-card-top">
                                        <span class="agent-number">
                                            ${String(index + 1).padStart(2, "0")}
                                        </span>

                                        <span class="agent-ai-badge ${
                                            aiUsed
                                                ? "ai-active"
                                                : "ai-fallback"
                                        }">
                                            ${
                                                aiUsed
                                                    ? "Gemini AI"
                                                    : "Python Fallback"
                                            }
                                        </span>
                                    </div>

                                    <h4>${escapeHTML(agentName)}</h4>

                                    <p class="agent-recommendation">
                                        ${escapeHTML(recommendation)}
                                    </p>

                                    <div class="agent-cost-row">
                                        <span>Estimated cost</span>
                                        <strong>${formatCurrency(cost)}</strong>
                                    </div>

                                </article>
                            `;
                        }).join("")}

                    </div>
                </div>



                                <div class="results-panel activity-panel">

                    <div class="panel-heading">
                        <div>
                            <span class="panel-kicker">
                                BEHIND THE SCENES
                            </span>
                            <h3>Trip Planning Activity</h3>
                        </div>

                        <span class="panel-icon">⚙️</span>
                    </div>

                    <div class="activity-timeline">
                        ${(Array.isArray(trip.activity_log)
                            ? trip.activity_log
                            : []
                        ).map((activity, index) => `
                            <div class="activity-item">
                                <span class="activity-dot"></span>

                                <div>
                                    <strong>Step ${index + 1}</strong>
                                    <p>${escapeHTML(activity)}</p>
                                </div>
                            </div>
                        `).join("")}
                    </div>

                    <div class="replanning-summary">
                        <span>Budget optimization rounds</span>
                        <strong>
                            ${Number(trip.replanning_rounds) || 0}
                        </strong>
                    </div>

                </div>

                <div class="results-footer-note">
                    <span>Information</span>

                    <p>
                        Costs are illustrative planning estimates,
                        not live prices or booking guarantees.
                        Verify transport, accommodation, activity
                        prices and availability before booking.
                    </p>
                </div>

                <div class="pdf-download-panel">
                    <div>
                        <h3>Keep Your Adventure Plan</h3>
                        <p>
                            Download your personalized itinerary
                            and budget report as a PDF.
                        </p>
                    </div>

                    <button
                        type="button"
                        id="download-pdf"
                        class="primary-button pdf-download-button"
                    >
                        Download Trip PDF
                    </button>
                </div>

            </div>
        `;

        currentTrip = trip;
        currentBudget = budget;

        renderBudgetChart(reports);
        attachPDFButton();

        resultSection.style.display = "block";

        resultSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    }

    // =====================================
    // BUDGET CHART
    // =====================================

    function renderBudgetChart(reports) {
        const canvas = document.getElementById("budget-chart");
        const fallbackMessage =
            document.getElementById("chart-unavailable");

        const breakdownList =
            document.getElementById("cost-breakdown-list");

        if (!canvas || !breakdownList) return;

        breakdownList.innerHTML = reports.map((report, index) => `
            <div class="cost-breakdown-item">

                <span class="cost-label">
                    <span class="cost-color-marker cost-color-${index % 4}"></span>

                    ${escapeHTML(getAgentName(report.agent))}
                </span>

                <strong>
                    ${formatCurrency(report.estimated_cost || 0)}
                </strong>

            </div>
        `).join("");

        if (typeof Chart === "undefined") {
            if (fallbackMessage) {
                fallbackMessage.hidden = false;
            }

            canvas.style.display = "none";
            return;
        }

        if (budgetChart) {
            budgetChart.destroy();
            budgetChart = null;
        }

        canvas.style.display = "block";

        if (fallbackMessage) {
            fallbackMessage.hidden = true;
        }

        budgetChart = new Chart(canvas, {
            type: "doughnut",

            data: {
                labels: reports.map(report =>
                    getAgentName(report.agent)
                ),

                datasets: [{
                    label: "Estimated Cost",

                    data: reports.map(report =>
                        Number(report.estimated_cost) || 0
                    ),

                    backgroundColor: [
                        "#21c7a8",
                        "#5b8def",
                        "#f5b942",
                        "#a78bfa"
                    ],

                    borderColor: "#ffffff",
                    borderWidth: 3,
                    hoverOffset: 8
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "65%",

                plugins: {
                    legend: {
                        position: "bottom",

                        labels: {
                            color: "#e8eef7",
                            padding: 18,
                            usePointStyle: true,
                            pointStyle: "circle"
                        }
                    },

                    tooltip: {
                        callbacks: {
                            label(context) {
                                return `${context.label}: ${formatCurrency(context.raw)}`;
                            }
                        }
                    }
                }
            }
        });
    }

    // =====================================
    // PDF GENERATION
    // =====================================

    function attachPDFButton() {
        const oldButton = document.getElementById("download-pdf");

        if (!oldButton) return;

        const newButton = oldButton.cloneNode(true);

        oldButton.replaceWith(newButton);

        newButton.addEventListener("click", downloadTripPDF);
    }

    function downloadTripPDF() {
        if (!currentTrip) {
            showMessage(
                "Generate a trip plan before downloading a PDF.",
                "error"
            );
            return;
        }

        if (!window.jspdf || !window.jspdf.jsPDF) {
            showMessage(
                "The PDF library could not load. Check your internet connection and refresh the page.",
                "error"
            );
            return;
        }

        const button = document.getElementById("download-pdf");

        const originalText = button
            ? button.textContent
            : "";

        try {
            if (button) {
                button.disabled = true;
                button.textContent = "Preparing PDF...";
            }

            const { jsPDF } = window.jspdf;

            const pdf = new jsPDF({
                orientation: "portrait",
                unit: "mm",
                format: "a4"
            });

            const pageWidth = pdf.internal.pageSize.getWidth();
            const pageHeight = pdf.internal.pageSize.getHeight();

            const margin = 18;
            const contentWidth = pageWidth - margin * 2;

            let y = 20;

            const trip = currentTrip;

            const reports = Array.isArray(trip.reports)
                ? trip.reports
                : [];

            const budgetReport = trip.budget_report || {};

            const total = Number(
                budgetReport.estimated_total ?? getReportTotal(reports)
            );

            const budget = Number(currentBudget) || 0;
            const remaining = budget - total;

            const initialTotal = Number(
                trip.initial_total ?? total
            );

            const savings = Math.max(
                0,
                initialTotal - total
            );

            function addPageIfNeeded(requiredHeight = 12) {
                if (y + requiredHeight > pageHeight - 18) {
                    pdf.addPage();
                    y = 20;
                }
            }

            function addSectionTitle(title) {
                addPageIfNeeded(18);

                pdf.setFont("helvetica", "bold");
                pdf.setFontSize(14);
                pdf.setTextColor(20, 65, 85);

                pdf.text(title, margin, y);

                y += 9;
            }

            function addParagraph(text, options = {}) {
                const fontSize = options.fontSize || 10;
                const lineHeight = options.lineHeight || 5;
                const indent = options.indent || 0;

                pdf.setFont(
                    "helvetica",
                    options.bold ? "bold" : "normal"
                );

                pdf.setFontSize(fontSize);
                pdf.setTextColor(55, 65, 81);

                const cleanText = String(text ?? "")
                    .replace(/\u00A0/g, " ")
                    .replace(/[\u200B-\u200D\uFEFF]/g, "")
                    .replace(/[^\x20-\x7E\u00A0-\u024F]/g, "")
                    .replace(/\s+/g, " ")
                    .trim();

                const lines = pdf.splitTextToSize(
                    cleanText,
                    contentWidth - indent
                );

                lines.forEach(line => {
                    addPageIfNeeded(lineHeight);

                    pdf.text(line, margin + indent, y);

                    y += lineHeight;
                });

                y += options.after ?? 2;
            }

            function addDivider() {
                addPageIfNeeded(5);

                pdf.setDrawColor(220, 228, 235);

                pdf.line(
                    margin,
                    y,
                    pageWidth - margin,
                    y
                );

                y += 7;
            }

            pdf.setFillColor(16, 36, 59);
            pdf.rect(0, 0, pageWidth, 48, "F");

            pdf.setFont("helvetica", "bold");
            pdf.setFontSize(23);
            pdf.setTextColor(255, 255, 255);

            pdf.text("TripSync AI", margin, 20);

            pdf.setFont("helvetica", "normal");
            pdf.setFontSize(11);

            pdf.text(
                "YOUR PERSONALIZED TRAVEL PLAN",
                margin,
                29
            );

            pdf.setFontSize(9);

            pdf.text(
                `Generated on ${new Date().toLocaleDateString("en-IN")}`,
                margin,
                38
            );

            y = 60;

            addSectionTitle("1. Trip Overview");

            addParagraph(`Origin: ${trip.origin || "Delhi"}`, {
                bold: true
            });

            addParagraph(
                `Destination: ${trip.destination || "Not specified"}`
            );

            addParagraph(
                `Departure: ${formatDate(trip.start_date)}`
            );

            addParagraph(
                `Return: ${formatDate(trip.end_date)}`
            );

            addParagraph(
                `Duration: ${Number(trip.days) || 0} days / ${Number(trip.nights) || 0} nights`
            );

            addParagraph(
                `Travelers: ${Number(trip.travelers) || 1}`
            );

            addDivider();

            addSectionTitle("2. Budget Summary");

            addParagraph(
                `Planned budget: ${formatPDFCurrency(budget)}`,
                { bold: true }
            );

            addParagraph(
                `Initial estimated cost: ${formatPDFCurrency(initialTotal)}`,
                { bold: true }
            );

            addParagraph(
                `Final estimated trip cost: ${formatPDFCurrency(total)}`,
                { bold: true }
            );

            addParagraph(
                `Estimated savings after optimization: ${formatPDFCurrency(savings)}`
            );

            addParagraph(
                `${remaining >= 0 ? "Estimated budget remaining" : "Estimated amount over budget"}: ${formatPDFCurrency(Math.abs(remaining))}`
            );

            addParagraph(
                `Budget status: ${budgetReport.within_budget === true ? "Within budget" : "Target not met / over budget"}`
            );

            addParagraph(
                `Budget optimization rounds: ${Number(trip.replanning_rounds) || 0}`
            );

            addDivider();

            addSectionTitle("3. Estimated Cost Breakdown");

            reports.forEach(report => {
                addParagraph(
                    `${getAgentName(report.agent)}: ${formatPDFCurrency(report.estimated_cost || 0)}`,
                    {
                        bold: true,
                        after: 3
                    }
                );
            });

            addDivider();

            addSectionTitle("4. Specialist Recommendations");

            reports.forEach(report => {
                addPageIfNeeded(22);

                addParagraph(
                    getAgentName(report.agent),
                    {
                        bold: true,
                        fontSize: 11,
                        after: 2
                    }
                );

                addParagraph(
                    `Recommendation source: ${report.ai_recommendation ? "Gemini AI" : "Python fallback"}`,
                    {
                        fontSize: 9,
                        after: 2
                    }
                );

                addParagraph(
                    getRecommendation(report),
                    {
                        fontSize: 9,
                        lineHeight: 4.5,
                        after: 3
                    }
                );

                addParagraph(
                    `Estimated cost: ${formatPDFCurrency(report.estimated_cost || 0)}`,
                    {
                        bold: true,
                        fontSize: 9
                    }
                );

                addDivider();
            });

            const activityLog = Array.isArray(trip.activity_log)
                ? trip.activity_log
                : [];

            if (activityLog.length) {
                addSectionTitle("5. Planning Activity");

                activityLog.forEach((activity, index) => {
                    addParagraph(
                        `${index + 1}. ${activity}`,
                        {
                            fontSize: 9,
                            lineHeight: 4.5,
                            after: 2
                        }
                    );
                });
            }

            const pageCount = pdf.getNumberOfPages();

            for (let page = 1; page <= pageCount; page++) {
                pdf.setPage(page);

                pdf.setFont("helvetica", "normal");
                pdf.setFontSize(8);
                pdf.setTextColor(120, 130, 140);

                pdf.text(
                    "TripSync AI | Illustrative planning estimates; verify prices and availability.",
                    margin,
                    pageHeight - 9
                );

                pdf.text(
                    `Page ${page} of ${pageCount}`,
                    pageWidth - margin,
                    pageHeight - 9,
                    { align: "right" }
                );
            }

            const safeDestination = String(
                trip.destination || "Trip"
            )
                .replace(/[^a-z0-9]+/gi, "-")
                .replace(/^-+|-+$/g, "")
                .substring(0, 50) || "Trip";

            pdf.save(`TripSync-AI-${safeDestination}.pdf`);

            showMessage(
                "Your trip PDF has been downloaded successfully!",
                "success"
            );

        } catch (error) {
            console.error("PDF generation error:", error);

            showMessage(
                "Could not generate the PDF. Please check the browser console and try again.",
                "error"
            );

        } finally {
            if (button) {
                button.disabled = false;
                button.textContent = originalText;
            }
        }
    }


        // =====================================
    // FORM SUBMISSION
    // =====================================

    tripForm.addEventListener("submit", async event => {
        event.preventDefault();

        const origin =
            document.getElementById("origin")?.value.trim() || "Delhi";

        const destination =
            document.getElementById("destination")?.value.trim() || "";

        const startDate =
            document.getElementById("start-date")?.value || "";

        const endDate =
            document.getElementById("end-date")?.value || "";

        const travelers =
            Number(document.getElementById("travelers")?.value);

        const budget =
            Number(document.getElementById("budget")?.value);

        if (
            !destination ||
            !startDate ||
            !endDate ||
            !travelers ||
            !budget
        ) {
            showMessage(
                "Please complete all required fields.",
                "error"
            );
            return;
        }

        if (
            new Date(`${endDate}T00:00:00`) <=
            new Date(`${startDate}T00:00:00`)
        ) {
            showMessage(
                "Return date must be after the departure date.",
                "error"
            );
            return;
        }

        if (travelers < 1 || travelers > 6) {
            showMessage(
                "Please enter between 1 and 6 travelers.",
                "error"
            );
            return;
        }

        if (budget <= 0) {
            showMessage(
                "Please enter a budget greater than zero.",
                "error"
            );
            return;
        }

        const requestData = {
            origin,
            destination,
            start_date: startDate,
            end_date: endDate,
            travelers,
            budget
        };

        const originalButtonText = submitButton
            ? submitButton.dataset.originalText || submitButton.textContent
            : "";

        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = "Planning Your Trip...";
        }

        showMessage(
            "Your specialist agents are preparing your trip plan. Please wait.",
            "info"
        );

        try {
            const response = await fetch(API_URL, {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(requestData)
            });

            let data;

            try {
                data = await response.json();
            } catch {
                throw new Error(
                    "The server returned an invalid response. Check that the backend is running."
                );
            }

            if (!response.ok) {
                throw new Error(
                    data.detail || "Unable to generate your trip plan."
                );
            }

            if (data.status !== "success" || !data.trip) {
                throw new Error(
                    "The server returned an unexpected response."
                );
            }

            showMessage(
                "Your trip plan is ready!",
                "success"
            );

            displayTripResult(data.trip, budget);

        } catch (error) {
            console.error("Trip planning error:", error);

            showMessage(
                `Could not generate your trip plan. ${error.message} Make sure the FastAPI backend is running at ${API_URL.replace("/api/plan-trip", "")}.`,
                "error"
            );

        } finally {
            if (submitButton) {
                submitButton.disabled = false;

                submitButton.textContent =
                    originalButtonText || "Plan My Trip";
            }
        }
    });

    // Save the original submit-button label once.
    if (submitButton && !submitButton.dataset.originalText) {
        submitButton.dataset.originalText = submitButton.textContent;
    }

    // =====================================
    // SMOOTH NAVIGATION
    // =====================================

    document.querySelectorAll('a[href^="#"]').forEach(link => {
        link.addEventListener("click", event => {
            const targetId = link.getAttribute("href");

            if (!targetId || targetId === "#") return;

            const target = document.querySelector(targetId);

            if (target) {
                event.preventDefault();

                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }
        });
    });
});