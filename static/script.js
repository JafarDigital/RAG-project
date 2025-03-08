document.addEventListener("DOMContentLoaded", function () {
    const contextInput = document.getElementById("context");
    const questionInput = document.getElementById("question");
    const tokenCountSpan = document.getElementById("token-count");
    const submitButton = document.getElementById("submit-all");
    const aiResponse = document.getElementById("ai-response");
    const resultsSection = document.getElementById("results-section");

    // Function to estimate token count (Mistral: ~1.3 tokens per word)
    function estimateTokens(text) {
        if (!text.trim()) return 0;
        return Math.ceil(text.trim().split(/\s+/).length * 1.3);
    }

    function updateTokenCount() {
        const contextTokens = estimateTokens(contextInput.value);
        const questionTokens = estimateTokens(questionInput.value);
        const totalTokens = contextTokens + questionTokens;
        
        tokenCountSpan.innerText = `🔢 Tokens Used: ${totalTokens} / 32768 tokens remaining`;
    }

    // Update token count in real time
    contextInput.addEventListener("input", updateTokenCount);
    questionInput.addEventListener("input", updateTokenCount);
    updateTokenCount(); // Initial update

    // Submit button click handler
    submitButton.addEventListener("click", async function () {
        const context = contextInput.value.trim();
        const question = questionInput.value.trim();

        if (!context && !question) {
            aiResponse.textContent = "⚠️ Please enter context or a question!";
            return;
        }

        try {
            console.log("📡 Sending request to backend...");

            const response = await fetch("http://127.0.0.1:8000/ask", {  
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question, context })
            });

            console.log("📡 Response received:", response);

            if (!response.ok) {
                console.error("❌ Server error:", response.status);
                aiResponse.textContent = `⚠️ Server error: ${response.status}`;
                return;
            }

            const data = await response.json();
            console.log("📡 AI Response:", data);

            displayResponse(data.answer);
        } catch (error) {
            console.error("❌ Fetch error:", error);
            aiResponse.textContent = "⚠️ Error reaching AI server.";
        }
    });

    // Function to display response properly formatted
		function displayResponse(answer) {
		const responseContainer = document.getElementById("ai-response");
		const resultsSection = document.getElementById("results-section");

		if (!responseContainer) {
			console.error("⚠️ Element #ai-response not found!");
			return;
		}

		if (!answer) {
			responseContainer.innerHTML = "<p>⚠️ No response from AI.</p>";
			return;
		}

		let formattedAnswer = answer.replace(/\n/g, "<br>"); // Preserve line breaks
		responseContainer.innerHTML = `<p>${formattedAnswer}</p>`;

		// Ensure the container becomes visible
		if (resultsSection) {
			resultsSection.classList.remove("hidden");
		}

		// Debugging: Log the entire response in case of issues
		console.log("📡 Full AI Response:", answer);
	}

});
