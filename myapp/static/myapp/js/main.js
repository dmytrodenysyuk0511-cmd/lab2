document.addEventListener("DOMContentLoaded", function () {
    // Theme toggle functionality
    const themeToggle = document.getElementById("themeToggle");
    const themeIcon = themeToggle ? themeToggle.querySelector(".theme-icon") : null;
    const body = document.body;

    // Set initial icon based on current theme
    if (themeToggle && themeIcon) {
        const currentTheme = body.classList.contains("theme-dark") ? "dark" : "light";
        themeIcon.textContent = currentTheme === "dark" ? "☀️" : "🌙";

        themeToggle.addEventListener("click", function () {
            const isDark = body.classList.contains("theme-dark");

            if (isDark) {
                body.classList.remove("theme-dark");
                body.classList.add("theme-light");
                themeIcon.textContent = "🌙";
                saveThemeToServer("light");
            } else {
                body.classList.remove("theme-light");
                body.classList.add("theme-dark");
                themeIcon.textContent = "☀️";
                saveThemeToServer("dark");
            }
        });
    }

    function saveThemeToServer(theme) {
        fetch(window.location.origin + "/account-settings/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: "theme=" + theme + "&language=" + (document.documentElement.lang || "uk")
        }).catch(err => console.error("Theme save error:", err));
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const replyButtons = document.querySelectorAll(".reply-message-btn");
    const parentInput = document.getElementById("parentMessageId");
    const replyTarget = document.getElementById("replyTarget");
    const replyTargetAuthor = document.getElementById("replyTargetAuthor");
    const replyTargetText = document.getElementById("replyTargetText");
    const cancelReplyBtn = document.getElementById("cancelReplyBtn");
    const chatMessages = document.getElementById("chatMessages");

    // Smooth scroll to chat messages
    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Observe new messages and scroll
        const observer = new MutationObserver(() => {
            chatMessages.scrollTo({
                top: chatMessages.scrollHeight,
                behavior: 'smooth'
            });
        });

        observer.observe(chatMessages, { childList: true, subtree: true });
    }

    // Reply functionality with animations
    replyButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            const messageId = button.dataset.messageId;
            const author = button.dataset.author;
            const text = button.dataset.text;

            if (parentInput) {
                parentInput.value = messageId;
            }

            if (replyTarget) {
                replyTarget.style.display = "flex";
                setTimeout(() => {
                    replyTarget.style.opacity = "1";
                    replyTarget.style.transform = "translateY(0)";
                }, 10);
            }

            if (replyTargetAuthor) {
                replyTargetAuthor.textContent = "Відповідь для: " + author;
            }

            if (replyTargetText) {
                replyTargetText.textContent = text;
            }

            const textarea = document.querySelector(".chat-textarea");
            if (textarea) {
                textarea.focus();
            }
        });
    });

    if (cancelReplyBtn) {
        cancelReplyBtn.addEventListener("click", function () {
            if (parentInput) {
                parentInput.value = "";
            }

            if (replyTarget) {
                replyTarget.style.opacity = "0";
                replyTarget.style.transform = "translateY(-10px)";
                setTimeout(() => {
                    replyTarget.style.display = "none";
                }, 300);
            }

            if (replyTargetAuthor) {
                replyTargetAuthor.textContent = "";
            }

            if (replyTargetText) {
                replyTargetText.textContent = "";
            }
        });
    }

    // Add loading states to forms
    const forms = document.querySelectorAll("form");
    forms.forEach(form => {
        form.addEventListener("submit", function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.disabled = true;
                submitBtn.style.opacity = "0.6";
                submitBtn.style.cursor = "not-allowed";
                const originalText = submitBtn.textContent;
                submitBtn.textContent = "Завантаження...";

                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.style.opacity = "1";
                    submitBtn.style.cursor = "pointer";
                    submitBtn.textContent = originalText;
                }, 5000);
            }
        });
    });

    // Lazy load images
    const images = document.querySelectorAll("img[data-src]");
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute("data-src");
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));

    // Add smooth transitions to cards
    const cards = document.querySelectorAll(".forum-category-row, .forum-latest-row, .product-card, .topic-card");
    cards.forEach((card, index) => {
        card.style.opacity = "0";
        card.style.transform = "translateY(20px)";
        setTimeout(() => {
            card.style.transition = "all 0.5s ease";
            card.style.opacity = "1";
            card.style.transform = "translateY(0)";
        }, index * 50);
    });

    // Initialize reply target styles
    if (replyTarget) {
        replyTarget.style.transition = "all 0.3s ease";
        replyTarget.style.opacity = "0";
        replyTarget.style.transform = "translateY(-10px)";
    }
});