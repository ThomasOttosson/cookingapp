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

    // -------------------------------
    // Smooth scroll for comment links
    // -------------------------------
    const commentLinks = document.querySelectorAll('a[href*="#comments-section"]');

    commentLinks.forEach(link => {
        link.addEventListener("click", function (event) {
            const targetUrl = link.href.split("#")[0];
            const targetHash = link.hash;

            // If same page, scroll smoothly
            if (window.location.href.split("#")[0] === targetUrl) {
                event.preventDefault();
                const target = document.querySelector(targetHash);
                if (target) {
                    const offset = 100; // adjust as needed
                    const bodyRect = document.body.getBoundingClientRect().top;
                    const elementRect = target.getBoundingClientRect().top;
                    const elementPosition = elementRect - bodyRect;
                    const offsetPosition = elementPosition - offset;

                    window.scrollTo({
                        top: offsetPosition,
                        behavior: "smooth"
                    });
                }
            } else {
                // For cross-page links (from recipe_list to recipe_detail)
                // Store in localStorage that we need to scroll to comments
                localStorage.setItem("scrollToComments", link.href);
            }
        });
    });

    // -------------------------------
    // Check on page load if we need to scroll to comments
    // -------------------------------
    window.addEventListener("load", function() { // wait for all images/content
        if (localStorage.getItem("scrollToComments")) {
            const scrollUrl = localStorage.getItem("scrollToComments");
            const [url, hash] = scrollUrl.split("#");

            // Only scroll if we are on the target page
            if (window.location.href.split("#")[0] === url) {
                const target = document.getElementById(hash);
                if (target) {
                    const offset = 100;
                    
                    // Optional small delay to ensure layout is fully loaded
                    setTimeout(() => {
                        const bodyRect = document.body.getBoundingClientRect().top;
                        const elementRect = target.getBoundingClientRect().top;
                        const elementPosition = elementRect - bodyRect;
                        const offsetPosition = elementPosition - offset;

                        window.scrollTo({
                            top: offsetPosition,
                            behavior: "smooth"
                        });

                        // Clear the flag after scrolling
                        localStorage.removeItem("scrollToComments");
                    }, 100); // 100ms delay
                }
            }
        }
    });

});
