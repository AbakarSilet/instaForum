
function toggleShareDropdown(button) {
    const dropdownMenu = button.nextElementSibling;
    dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
}

function toggleDropdown(element) {
    const dropdownMenu = element.nextElementSibling;
    dropdownMenu.style.display = dropdownMenu.style.display === "block" ? "none" : "block";
    event.stopPropagation();
}


// Gestion des messages d'alerte
document.addEventListener('DOMContentLoaded', function () {
    // Fermeture des alertes automatiquement après 5 secondes
    setTimeout(function () {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            const closeBtn = new bootstrap.Alert(alert);
            closeBtn.close();
        });
    }, 5000);

    // Bouton pour annuler le commentaire
    const cancelBtn = document.getElementById('cancel-comment-btn');
    const commentForm = document.getElementById('add-comment-form');
    const showFormIcon = document.getElementById('show-form-icon');

    if (cancelBtn && commentForm && showFormIcon) {
        cancelBtn.addEventListener('click', function () {
            commentForm.reset();
            commentForm.style.display = 'none';
            showFormIcon.style.display = 'flex';
        });
    }

    // Afficher le formulaire quand on clique sur l'icône
    if (showFormIcon && commentForm) {
        showFormIcon.addEventListener('click', function () {
            commentForm.style.display = 'block';
            showFormIcon.style.display = 'none';
            // Focus sur le champ de texte du commentaire
            const textArea = commentForm.querySelector('textarea');
            if (textArea) {
                textArea.focus();
            }
        });
    }

    // Gestion de la soumission du formulaire avec feedback
    if (commentForm) {
        commentForm.addEventListener('submit', function (e) {
            const submitBtn = document.getElementById('submit-comment-btn');
            const spinner = submitBtn.querySelector('.spinner-border');
            const buttonText = submitBtn.querySelector('.button-text');
            const feedback = document.getElementById('form-feedback');

            // Validation simple côté client
            const textarea = commentForm.querySelector('textarea');
            if (textarea && textarea.value.trim() === '') {
                e.preventDefault();
                feedback.textContent = 'Veuillez écrire un commentaire avant de publier.';
                feedback.style.display = 'block';
                feedback.style.backgroundColor = '#f8d7da';
                return;
            }

            // Afficher le spinner et désactiver le bouton
            spinner.classList.remove('d-none');
            buttonText.textContent = 'Publication en cours...';
            submitBtn.disabled = true;
        });
    }

    // Mettre en évidence le nouveau post si l'URL contient un ancre
    if (window.location.hash) {
        const postId = window.location.hash.substring(1);
        const postElement = document.getElementById(postId);

        if (postElement) {
            postElement.classList.add('highlight-new');
            postElement.scrollIntoView({ behavior: 'smooth' });
        }
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const showFormTrigger = document.getElementById('show-form-trigger');
    const addCommentForm = document.getElementById('add-comment-form');
    const submitButton = document.getElementById('submit-comment-btn');

    // Initialement masquer le formulaire
    addCommentForm.style.display = 'none';

    // Afficher le formulaire au clic
    showFormTrigger.addEventListener('click', function () {
        addCommentForm.style.display = 'block';
        showFormTrigger.style.display = 'none';
    });

    // Gérer la soumission du formulaire
    addCommentForm.addEventListener('submit', function (e) {
        const defaultText = submitButton.getAttribute('data-text-default');
        const loadingText = submitButton.getAttribute('data-text-loading');

        submitButton.disabled = true;
        submitButton.textContent = loadingText;
    });
});
