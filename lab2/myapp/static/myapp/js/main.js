document.addEventListener("DOMContentLoaded", function () {
    const replyButtons = document.querySelectorAll(".reply-message-btn");
    const parentInput = document.getElementById("parentMessageId");
    const replyTarget = document.getElementById("replyTarget");
    const replyTargetAuthor = document.getElementById("replyTargetAuthor");
    const replyTargetText = document.getElementById("replyTargetText");
    const cancelReplyBtn = document.getElementById("cancelReplyBtn");
    const chatMessages = document.getElementById("chatMessages");
    const conversationMessages = document.getElementById("conversationMessages");
    const pageLanguage = document.documentElement.lang || "uk";

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
            }

            if (replyTargetAuthor) {
                replyTargetAuthor.textContent = (pageLanguage === "en" ? "Reply to: " : "Відповідь для: ") + author;
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
                replyTarget.style.display = "none";
            }

            if (replyTargetAuthor) {
                replyTargetAuthor.textContent = "";
            }

            if (replyTargetText) {
                replyTargetText.textContent = "";
            }
        });
    }

    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    if (conversationMessages) {
        conversationMessages.scrollTop = conversationMessages.scrollHeight;
    }

    // Smooth scroll for reply links
    document.querySelectorAll('a[href^="#message-"]').forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
                targetElement.style.backgroundColor = '#e8f0ff';
                setTimeout(function() {
                    targetElement.style.backgroundColor = '';
                }, 2000);
            }
        });
    });

    // Auto-resize textareas
    const textareas = document.querySelectorAll('.chat-textarea, .conversation-textarea');
    textareas.forEach(function(textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });

    document.querySelectorAll(".telegram-composer").forEach(function (form) {
        const fileInput = form.querySelector(".chat-media-input, .conversation-media-input");
        const preview = form.querySelector("[data-attachment-preview]");
        const fileName = form.querySelector("[data-attachment-name]");
        const clearButton = form.querySelector("[data-attachment-clear]");

        if (!fileInput || !preview || !fileName) {
            return;
        }

        fileInput.classList.add("attachment-input");

        fileInput.addEventListener("change", function () {
            const file = fileInput.files && fileInput.files[0];

            if (!file) {
                preview.hidden = true;
                fileName.textContent = "";
                form.classList.remove("has-attachment");
                return;
            }

            fileName.textContent = file.name;
            preview.hidden = false;
            form.classList.add("has-attachment");
        });

        if (clearButton) {
            clearButton.addEventListener("click", function () {
                fileInput.value = "";
                fileName.textContent = "";
                preview.hidden = true;
                form.classList.remove("has-attachment");
            });
        }
    });

    document.querySelectorAll("[data-auto-submit]").forEach(function (control) {
        control.addEventListener("change", function () {
            const form = control.closest("form");

            if (!form) {
                return;
            }

            if (form.requestSubmit) {
                form.requestSubmit();
            } else {
                form.submit();
            }
        });
    });

    // Add animation to cards on hover
    const cards = document.querySelectorAll('.forum-category-row, .forum-latest-row, .friend-card, .conversation-card');
    cards.forEach(function(card) {
        card.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.3s ease';
        });
    });

    // Notification for new messages (placeholder for future WebSocket implementation)
    function checkNewMessages() {
        // This would be implemented with WebSocket or polling in production
        console.log('Checking for new messages...');
    }

    // Check every 30 seconds (disabled by default, enable when backend supports it)
    // setInterval(checkNewMessages, 30000);
});
