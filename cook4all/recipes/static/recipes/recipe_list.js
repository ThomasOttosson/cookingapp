// recipe_list.js

document.addEventListener("DOMContentLoaded", function () {

    // -------------------------------
    // Make recipe cards clickable
    // -------------------------------
    const cards = document.querySelectorAll(".recipe-card");

    cards.forEach(card => {
        const url = card.dataset.href;
        if (url) {
            card.addEventListener("click", function () {
                window.location.href = url;
            });
        }
    });

    // Stop propagation for forms/buttons inside cards
    const forms = document.querySelectorAll(".recipe-card form");
    forms.forEach(form => {
        form.addEventListener("click", function (event) {
            event.stopPropagation();
        });
    });

    // -------------------------------
    // NEW: Instant search filtering
    // -------------------------------
    const searchInput = document.getElementById("search-input");
    const recipesContainer = document.getElementById("recipes-container");

    if (searchInput && recipesContainer) {
        searchInput.addEventListener("input", function () {
            const query = searchInput.value;

            // Fetch updated recipes from server via AJAX
            fetch(`${window.location.pathname}?q=${encodeURIComponent(query)}`, {
                headers: { "X-Requested-With": "XMLHttpRequest" },
            })
                .then(response => response.text())
                .then(html => {
                    // Parse the HTML response
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, "text/html");
                    const newRecipes = doc.getElementById("recipes-container");

                    // Replace the recipes container content
                    if (newRecipes) {
                        recipesContainer.innerHTML = newRecipes.innerHTML;

                        // Re-apply clickable cards behavior to new elements
                        const updatedCards = recipesContainer.querySelectorAll(".recipe-card");
                        updatedCards.forEach(card => {
                            const url = card.dataset.href;
                            if (url) {
                                card.addEventListener("click", function () {
                                    window.location.href = url;
                                });
                            }
                        });

                        // Stop propagation for new forms/buttons
                        const updatedForms = recipesContainer.querySelectorAll(".recipe-card form");
                        updatedForms.forEach(form => {
                            form.addEventListener("click", function (event) {
                                event.stopPropagation();
                            });
                        });
                    }
                })
                .catch(err => console.error("Search error:", err));
        });
    }

});
