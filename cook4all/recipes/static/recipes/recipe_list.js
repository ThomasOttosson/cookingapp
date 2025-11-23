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
    // Instant search filtering
    // -------------------------------
    const searchInput = document.getElementById("search-input");
    const recipesContainer = document.getElementById("recipes-container");

    if (searchInput && recipesContainer) {
        searchInput.addEventListener("input", function () {
            const query = searchInput.value;

            fetch(`${window.location.pathname}?q=${encodeURIComponent(query)}`, {
                headers: { "X-Requested-With": "XMLHttpRequest" },
            })
                .then(response => response.text())
                .then(html => {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, "text/html");
                    const newRecipes = doc.getElementById("recipes-container");

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

            if (window.location.href.split("#")[0] === targetUrl) {
                event.preventDefault();
                const target = document.querySelector(targetHash);
                if (target) {
                    const offset = 100;
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
                localStorage.setItem("scrollToComments", link.href);
            }
        });
    });

    // -------------------------------
    // Check on page load if we need to scroll to comments
    // -------------------------------
    window.addEventListener("load", function () {
        if (localStorage.getItem("scrollToComments")) {
            const scrollUrl = localStorage.getItem("scrollToComments");
            const [url, hash] = scrollUrl.split("#");

            if (window.location.href.split("#")[0] === url) {
                const target = document.getElementById(hash);
                if (target) {
                    const offset = 100;
                    setTimeout(() => {
                        const bodyRect = document.body.getBoundingClientRect().top;
                        const elementRect = target.getBoundingClientRect().top;
                        const elementPosition = elementRect - bodyRect;
                        const offsetPosition = elementPosition - offset;

                        window.scrollTo({
                            top: offsetPosition,
                            behavior: "smooth"
                        });

                        localStorage.removeItem("scrollToComments");
                    }, 100);
                }
            }
        }
    });

    // -------------------------------
    // COMMENT EDIT FUNCTIONALITY
    // -------------------------------
    document.addEventListener('click', function (event) {

        // Edit button click
        if (event.target.classList.contains('edit-comment-btn')) {
            const id = event.target.dataset.id;
            const commentDiv = document.getElementById(`comment-${id}`);
            const editForm = document.getElementById(`edit-form-${id}`);
            const editBtn = event.target;
            const deleteBtn = commentDiv.querySelector('.original-delete-btn'); // Original delete button

            if (commentDiv && editForm) {
                // Hide comment content and original buttons
                commentDiv.querySelector('.comment-content').style.display = 'none';
                editBtn.style.display = 'none';
                if (deleteBtn) deleteBtn.style.display = 'none';

                // Show edit form and delete button inside form
                editForm.classList.remove('d-none');
                const editFormDelete = editForm.querySelector('.delete-button-form');
                if (editFormDelete) editFormDelete.classList.remove('d-none');
            }
        }

        // Cancel button click
        if (event.target.classList.contains('cancel-edit-btn')) {
            const id = event.target.dataset.id;
            const commentDiv = document.getElementById(`comment-${id}`);
            const editForm = document.getElementById(`edit-form-${id}`);
            const editBtn = commentDiv.querySelector(`.edit-comment-btn`);
            const deleteBtn = commentDiv.querySelector('.original-delete-btn');

            if (commentDiv && editForm) {
                // Hide edit form, show original content & buttons
                editForm.classList.add('d-none');
                commentDiv.querySelector('.comment-content').style.display = 'block';
                if (editBtn) editBtn.style.display = 'inline-block';
                if (deleteBtn) deleteBtn.style.display = 'inline-block';

                // Hide delete inside edit form again
                const editFormDelete = editForm.querySelector('.delete-button-form');
                if (editFormDelete) editFormDelete.classList.add('d-none');
            }
        }

    });

});
