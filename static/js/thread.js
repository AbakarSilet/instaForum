// Fonction utilitaire pour récupérer le token CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Fonction générique pour gérer les likes
function setupLikeButtons(selector, likeIconSelector, likeCountSelector, fetchUrl = null) {
    const likeButtons = document.querySelectorAll(selector);

    likeButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();

            const postId = this.getAttribute('data-post-id') || this.getAttribute('data-thread-slug');
            const likeIcon = this.querySelector(likeIconSelector);
            const likeCount = this.querySelector(likeCountSelector);

            // Utiliser l'URL personnalisée si fournie, sinon construire une URL par défaut
            const url = fetchUrl ? fetchUrl(postId) : `/forum/post/${postId}/like/`;

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            })
                .then(response => response.json())
                .then(data => {
                    // Mettre à jour l'icône
                    if (data.liked) {
                        likeIcon.classList.remove('far', 'fa-heart');
                        likeIcon.classList.add('fas', 'fa-heart', 'text-red-500');
                    } else {
                        likeIcon.classList.remove('fas', 'fa-heart', 'text-red-500');
                        likeIcon.classList.add('far', 'fa-heart');
                    }

                    // Mettre à jour le nombre de likes
                    likeCount.textContent = data.total_likes;
                })
                .catch(error => {
                    console.error('Erreur:', error);
                });
        });
    });
}

// Fonction pour gérer les menus déroulants
function setupDropdownMenus() {
    const threadOptionsBtn = document.getElementById('threadOptionsBtn');
    const threadOptionsMenu = document.getElementById('threadOptionsMenu');
    const shareBtn = document.getElementById('shareBtn');
    const shareMenu = document.getElementById('shareMenu');
    const commentOptionsBtns = document.querySelectorAll('.commentOptionsBtn');
    const commentOptionsMenus = document.querySelectorAll('.commentOptionsMenu');

    // Fonction pour fermer tous les menus
    function closeAllMenus() {
        threadOptionsMenu.classList.add('scale-0');
        threadOptionsMenu.classList.remove('scale-100');
        shareMenu.classList.add('scale-0');
        shareMenu.classList.remove('scale-100');
        commentOptionsMenus.forEach(menu => {
            menu.classList.add('scale-0');
            menu.classList.remove('scale-100');
        });
    }

    // Toggle pour le menu du thread
    threadOptionsBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        threadOptionsMenu.classList.toggle('scale-0');
        threadOptionsMenu.classList.toggle('scale-100');
        // Ferme les autres menus
        shareMenu.classList.add('scale-0');
        shareMenu.classList.remove('scale-100');
        commentOptionsMenus.forEach(menu => {
            menu.classList.add('scale-0');
            menu.classList.remove('scale-100');
        });
    });

    // Toggle pour le menu de partage
    shareBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        shareMenu.classList.toggle('scale-0');
        shareMenu.classList.toggle('scale-100');
        // Ferme les autres menus
        threadOptionsMenu.classList.add('scale-0');
        threadOptionsMenu.classList.remove('scale-100');
        commentOptionsMenus.forEach(menu => {
            menu.classList.add('scale-0');
            menu.classList.remove('scale-100');
        });
    });

    // Toggle pour les menus des commentaires
    commentOptionsBtns.forEach((btn, index) => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            // Ferme tous les autres menus
            commentOptionsMenus.forEach((menu, menuIndex) => {
                if (menuIndex !== index) {
                    menu.classList.add('scale-0');
                    menu.classList.remove('scale-100');
                }
            });
            shareMenu.classList.add('scale-0');
            shareMenu.classList.remove('scale-100');
            threadOptionsMenu.classList.add('scale-0');
            threadOptionsMenu.classList.remove('scale-100');

            // Toggle le menu actuel
            commentOptionsMenus[index].classList.toggle('scale-0');
            commentOptionsMenus[index].classList.toggle('scale-100');
        });
    });

    // Ferme tous les menus si on clique ailleurs sur la page
    document.addEventListener('click', closeAllMenus);

    // Empêche la propagation des clics sur les menus
    const allMenus = [threadOptionsMenu, shareMenu, ...commentOptionsMenus];
    allMenus.forEach(menu => {
        menu.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    });
}

// Fonction pour gérer le formulaire de commentaire
function setupCommentForm() {
    const commentBtn = document.getElementById('commentBtn');
    const commentForm = document.getElementById('commentForm');
    const cancelComment = document.getElementById('cancelComment');

    commentBtn.addEventListener('click', () => {
        commentForm.classList.toggle('hidden');
    });

    cancelComment.addEventListener('click', () => {
        commentForm.classList.add('hidden');
    });
}

// Initialisation au chargement du DOM
document.addEventListener('DOMContentLoaded', function () {
    // Configuration des likes pour les threads
    setupLikeButtons('.like-button', '.like-icon', '.like-count', (threadSlug) => {
        const threadBtn = document.querySelector(`.like-button[data-thread-slug="${threadSlug}"]`);
        return threadBtn.getAttribute('data-url');
    });

    // Configuration des likes pour les posts
    setupLikeButtons('.post-like-button', '.post-like-icon', '.post-like-count');

    setupDropdownMenus();
    setupCommentForm();
});