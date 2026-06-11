document.addEventListener("DOMContentLoaded", () => {
    // DOM Navigation
    const navItems = document.querySelectorAll(".nav-item");
    const tabPanes = document.querySelectorAll(".tab-pane");
    const summaryTabBtn = document.getElementById("summary-tab-btn");
    const analyticsTabBtn = document.getElementById("analytics-tab-btn");

    // DOM - Transcript Input
    const transcriptInput = document.getElementById("transcript-input");
    const summarizeForm = document.getElementById("summarize-form");
    const compileBtn = document.getElementById("compile-btn");
    const sidebarStatsCard = document.getElementById("sidebar-stats-card");
    const statWords = document.getElementById("stat-words");
    const statSpeakers = document.getElementById("stat-speakers");

    // DOM - Summary recap
    const textExecSummary = document.getElementById("text-exec-summary");
    const listDecisions = document.getElementById("list-decisions");
    const actionsTableBody = document.querySelector("#actions-table tbody");
    const copyMarkdownBtn = document.getElementById("copy-markdown-btn");
    const downloadMarkdownBtn = document.getElementById("download-markdown-btn");

    // Global charts instances cache
    let speakerShareChart = null;
    let sentimentTimelineChart = null;
    let topicWeightsChart = null;
    
    // In-memory presets cache
    let presets = {};
    let activeSummaryData = null; // Caches API results for exports

    // Load presets on startup
    async function loadPresets() {
        try {
            const resp = await fetch("/api/presets");
            if (resp.ok) {
                presets = await resp.json();
            }
        } catch (err) {
            console.error("Presets load failure:", err);
        }
    }
    loadPresets();

    // Wire preset buttons
    document.getElementById("preset-retro-btn").addEventListener("click", () => {
        setTranscript("retro");
    });
    document.getElementById("preset-marketing-btn").addEventListener("click", () => {
        setTranscript("marketing");
    });
    document.getElementById("preset-board-btn").addEventListener("click", () => {
        setTranscript("board");
    });

    function setTranscript(key) {
        if (presets[key]) {
            transcriptInput.value = presets[key];
            transcriptInput.classList.add("flash-highlight");
            setTimeout(() => transcriptInput.classList.remove("flash-highlight"), 500);
        }
    }

    // Tab switches
    navItems.forEach(item => {
        item.addEventListener("click", () => {
            if (item.style.display === "none") return;
            
            navItems.forEach(nav => nav.classList.remove("active"));
            tabPanes.forEach(pane => pane.classList.remove("active"));

            item.classList.add("active");
            const targetId = item.getAttribute("data-tab");
            document.getElementById(targetId).classList.add("active");
        });
    });

    // Form Submission
    summarizeForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const text = transcriptInput.value.trim();
        if (!text) return;

        // Loading UI state
        compileBtn.disabled = true;
        compileBtn.innerHTML = `<span>Processing Transcript...</span> <i class="fa-solid fa-spinner fa-spin"></i>`;

        try {
            const resp = await fetch("/api/summarize-transcript", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ transcript_text: text })
            });

            if (!resp.ok) {
                throw new Error(`Server returned code: ${resp.status}`);
            }

            const data = await resp.json();
            activeSummaryData = data; // Cache for copy/downloads

            // 1. Sidebar stats update
            sidebarStatsCard.style.display = "block";
            statWords.textContent = data.total_words;
            const speakerList = Object.keys(data.speaker_shares);
            statSpeakers.textContent = speakerList.length;

            // 2. Enable nav items
            summaryTabBtn.style.display = "flex";
            analyticsTabBtn.style.display = "flex";

            // 3. Navigate to Summary Tab
            triggerTabSwitch("summary-pane", summaryTabBtn);

            // 4. Render Summary details
            textExecSummary.textContent = data.summary.executive_summary;
            
            listDecisions.innerHTML = "";
            data.summary.decisions.forEach(dec => {
                const li = document.createElement("li");
                li.textContent = dec;
                listDecisions.appendChild(li);
            });

            actionsTableBody.innerHTML = "";
            data.summary.action_items.forEach((item, index) => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>
                        <input type="checkbox" class="task-checkbox" id="chk-task-${index}">
                    </td>
                    <td>
                        <span class="task-text">${escapeHtml(item.action)}</span>
                    </td>
                    <td>
                        <span class="owner-tag">${escapeHtml(item.owner)}</span>
                    </td>
                    <td>
                        <span class="badge-priority ${item.priority.toLowerCase()}">${item.priority}</span>
                    </td>
                    <td>
                        <span class="timeline-txt"><i class="fa-regular fa-clock"></i> ${escapeHtml(item.deadline)}</span>
                    </td>
                `;
                
                // Toggle task completions strike through
                const chk = tr.querySelector(".task-checkbox");
                chk.addEventListener("change", (e) => {
                    if (e.target.checked) {
                        tr.classList.add("task-completed");
                    } else {
                        tr.classList.remove("task-completed");
                    }
                });

                actionsTableBody.appendChild(tr);
            });

            // 5. Render Analytics Charts
            renderSpeakerShareChart(data.speaker_shares);
            renderSentimentTimelineChart(data.timeline);
            renderTopicWeightsChart(data.topics);

        } catch (err) {
            alert(`Summarization Error: ${err.message}`);
        } finally {
            compileBtn.disabled = false;
            compileBtn.innerHTML = `<span>Compile Minutes & Analytics</span> <i class="fa-solid fa-wand-magic-sparkles"></i>`;
        }
    });

    function triggerTabSwitch(paneId, tabBtnElement) {
        navItems.forEach(nav => nav.classList.remove("active"));
        tabPanes.forEach(pane => pane.classList.remove("active"));

        tabBtnElement.classList.add("active");
        document.getElementById(paneId).classList.add("active");
    }

    // ---------------- CHARTJS RENDERINGS ----------------
    function renderSpeakerShareChart(shares) {
        if (speakerShareChart) {
            speakerShareChart.destroy();
        }
        
        const ctx = document.getElementById("speaker-share-chart").getContext("2d");
        const labels = Object.keys(shares);
        const data = Object.values(shares);

        speakerShareChart = new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        "#06b6d4", // Cyan
                        "#10b981", // Emerald Green
                        "#f59e0b", // Amber
                        "#ef4444", // Red
                        "#a855f7"  // Purple
                    ],
                    borderWidth: 1,
                    borderColor: "rgba(255,255,255,0.08)"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "right",
                        labels: {
                            color: "#94a3b8",
                            font: { family: "Outfit", size: 12 }
                        }
                    }
                }
            }
        });
    }

    function renderSentimentTimelineChart(timeline) {
        if (sentimentTimelineChart) {
            sentimentTimelineChart.destroy();
        }

        const ctx = document.getElementById("sentiment-timeline-chart").getContext("2d");
        
        sentimentTimelineChart = new Chart(ctx, {
            type: "line",
            data: {
                labels: ["Seg 1 (Start)", "Seg 2", "Seg 3", "Seg 4", "Seg 5 (End)"],
                datasets: [{
                    label: "Sentiment Valence",
                    data: timeline,
                    borderColor: "#38bdf8",
                    backgroundColor: "rgba(56, 189, 248, 0.05)",
                    borderWidth: 2,
                    fill: true,
                    tension: 0.35,
                    pointBackgroundColor: "#38bdf8",
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        min: -1.0,
                        max: 1.0,
                        grid: { color: "rgba(255,255,255,0.04)" },
                        ticks: { color: "#94a3b8", font: { family: "Outfit" } }
                    },
                    x: {
                        grid: { color: "rgba(255,255,255,0.04)" },
                        ticks: { color: "#94a3b8", font: { family: "Outfit" } }
                    }
                }
            }
        });
    }

    function renderTopicWeightsChart(topics) {
        if (topicWeightsChart) {
            topicWeightsChart.destroy();
        }

        const ctx = document.getElementById("topic-weights-chart").getContext("2d");
        const labels = Object.keys(topics);
        const data = Object.values(topics);

        topicWeightsChart = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: "rgba(56, 189, 248, 0.45)",
                    borderColor: "#38bdf8",
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: { color: "rgba(255,255,255,0.04)" },
                        ticks: { color: "#94a3b8", font: { family: "Outfit" } }
                    },
                    x: {
                        grid: { color: "rgba(255,255,255,0.04)" },
                        ticks: { color: "#94a3b8", font: { family: "Outfit" } }
                    }
                }
            }
        });
    }

    // ---------------- EXPORT WORKFLOWS ----------------
    function generateMarkdown() {
        if (!activeSummaryData) return "";
        
        const summary = activeSummaryData.summary;
        let md = `# Meeting Minutes Recap\n\n`;
        md += `## Executive Summary\n${summary.executive_summary}\n\n`;
        
        md += `## Key Decisions Approved\n`;
        summary.decisions.forEach(dec => {
            md += `- ${dec}\n`;
        });
        md += `\n`;

        md += `## Action Items Deliverables\n`;
        md += `| Task Deliverable | Assigned Owner | Priority | Target Deadline |\n`;
        md += `| --- | --- | --- | --- |\n`;
        summary.action_items.forEach(item => {
            md += `| ${item.action} | ${item.owner} | ${item.priority} | ${item.deadline} |\n`;
        });
        
        return md;
    }

    // Copy to clipboard
    copyMarkdownBtn.addEventListener("click", () => {
        const md = generateMarkdown();
        if (!md) return;

        navigator.clipboard.writeText(md)
            .then(() => {
                const originalText = copyMarkdownBtn.innerHTML;
                copyMarkdownBtn.innerHTML = `<i class="fa-solid fa-check" style="color: var(--success);"></i> Copied!`;
                copyMarkdownBtn.disabled = true;
                setTimeout(() => {
                    copyMarkdownBtn.innerHTML = originalText;
                    copyMarkdownBtn.disabled = false;
                }, 2000);
            })
            .catch(err => {
                alert("Failed to copy transcript: " + err);
            });
    });

    // Download markdown file
    downloadMarkdownBtn.addEventListener("click", () => {
        const md = generateMarkdown();
        if (!md) return;

        const blob = new Blob([md], { type: "text/markdown;charset=utf-8;" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", "meeting_minutes_recap.md");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });

    function escapeHtml(str) {
        if (!str) return "";
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
