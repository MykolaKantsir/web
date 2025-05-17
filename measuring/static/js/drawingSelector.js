document.addEventListener("DOMContentLoaded", async () => {
    const searchBtn = document.getElementById("drawing-search-btn");
    const searchInput = document.getElementById("drawing-search-input");
    const errorText = document.getElementById("drawing-search-error");

    // Optional: ensure CSRF token is present
    await fetchCsrfToken?.();

    if (searchBtn && searchInput) {
        searchBtn.addEventListener("click", async () => {
            const query = searchInput.value.trim();
            if (!query) return;

            const csrfToken = getCsrfToken?.(); // safely call if function is loaded

            try {
                const response = await fetch(`/measuring/api/find_drawing/?query=${encodeURIComponent(query)}`, {
                    headers: {
                        "X-CSRFToken": csrfToken || "",
                    },
                    credentials: "include"
                });

                const result = await response.json();

                if (result && result.drawing_id) {
                    window.location.href = `/measuring/measure/${result.drawing_id}/`;
                } else {
                    errorText.style.display = "block";
                }
            } catch (err) {
                console.error("❌ Search failed:", err);
                errorText.style.display = "block";
            }
        });
    }
});
