document.addEventListener('DOMContentLoaded', function() {
    const postForm = document.getElementById('post-form');
    
    if (postForm) {
        postForm.addEventListener('submit', function(e) {
            e.preventDefault(); // Empêche le rechargement de la page
            const postText = document.getElementById('post-text').value;
            const threadId = '{{ thread.id }}'; // Assurez-vous que l'ID est correctement rendu

            fetch(`/forum/add_post/${threadId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token }}',
                },
                body: JSON.stringify({ text: postText })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erreur lors de l\'ajout du post');
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    // Créez un nouvel élément de commentaire
                    const commentList = document.getElementById('comment-list');
                    const newComment = document.createElement('div');
                    newComment.className = 'comment';
                    newComment.innerHTML = `
                        <img src="${data.author.profile_image}" alt="Commentateur" class="comment-avatar">
                        <div class="comment-details">
                            <span class="commentator-name">${data.author.username}</span>
                            <span class="comment-date">${new Date(data.created_at).toLocaleString()}</span>
                            <p class="comment-text">${data.text}</p>
                        </div>
                    `;
                    commentList.prepend(newComment); // Ajoute le nouveau commentaire en haut de la liste
                    document.getElementById('post-text').value = ''; // Réinitialise le champ de texte
                }
            })
            .catch(error => console.error('Erreur:', error));
        });
    }
});