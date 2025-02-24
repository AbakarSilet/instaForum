document.addEventListener('DOMContentLoaded', function () {
    const threadSlug = "{{ thread.slug }}";
    const socket = new WebSocket(`ws://${window.location.host.replace(':8000', '')}/ws/thread/${threadSlug}/`);

    socket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        if (data.type === 'new_post') {
            const postList = document.getElementById('post-list');
            const newPostElement = document.createElement('div');
            newPostElement.classList.add('post');
            newPostElement.innerHTML = `
                <strong>${data.post.author_username}</strong>
                <p>${data.post.content}</p>
                <small>${new Date(data.post.created_at).toLocaleString()}</small>
            `;
            postList.appendChild(newPostElement);
        }
    };

    const showFormIcon = document.getElementById("show-form-icon");
    const addCommentForm = document.getElementById("add-comment-form");

    showFormIcon.addEventListener("click", () => {
        addCommentForm.style.display = addCommentForm.style.display === "none" || addCommentForm.style.display === "" ? "block" : "none";
    });

    const dropdowns = document.querySelectorAll('.dropdown-toggle');
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('click', function (e) {
            e.stopPropagation();
            const menu = this.nextElementSibling;
            menu.classList.toggle('show');
        });
    });

    document.addEventListener('click', function (e) {
        const dropdowns = document.querySelectorAll('.dropdown-menu');
        dropdowns.forEach(dropdown => {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('show');
            }
        });
        
        const shareDropdowns = document.querySelectorAll('.share-dropdown-menu');
        shareDropdowns.forEach(menu => {
            if (!menu.contains(e.target) && !menu.previousElementSibling.contains(e.target)) {
                menu.style.display = 'none';
            }
        });
    });

    if (window.location.hash) {
        var element = document.querySelector(window.location.hash);
        if (element) {
            element.scrollIntoView();
        }
    }
});

function toggleShareDropdown(button) {
    const dropdownMenu = button.nextElementSibling;
    dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
}

function toggleDropdown(element) {
    const dropdownMenu = element.nextElementSibling;
    dropdownMenu.style.display = dropdownMenu.style.display === "block" ? "none" : "block";
    event.stopPropagation();
}

function quotePost(postId, postContent, postAuthor, postPage) {
    const textarea = document.getElementById('comment');
    const quotedTextInput = document.getElementById('quoted-text');

    if (!textarea || !quotedTextInput) {
        console.error('Elements not found:', { textarea: !!textarea, quotedTextInput: !!quotedTextInput });
        return;
    }

    const maxLength = 500;
    const truncatedContent = truncateText(postContent, maxLength);
    const quotedText = `Réponse à @${postAuthor}: "${truncatedContent}"`;
    const quotedTextWithLink = `<a href="?page=${postPage}#post-${postId}" target="_blank">${quotedText}</a>`;
    quotedTextInput.value = quotedTextWithLink;

    if (!textarea.value.trim()) {
        textarea.value = `${quotedText}`;
    }

    textarea.focus();
    textarea.setSelectionRange(textarea.value.length, textarea.value.length);

    const addCommentForm = document.getElementById("add-comment-form");
    if (addCommentForm) {
        addCommentForm.style.display = "block";
    }
}

function truncateText(text, maxLength) {
    return text.length <= maxLength ? text : text.substr(0, maxLength) + '...';
}
