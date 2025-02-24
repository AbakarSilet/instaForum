document.addEventListener('DOMContentLoaded', function() {
    const profileImageInput = document.getElementById('id_profile_image');
    const profileImagePreview = document.getElementById('profile_preview');

    if (profileImageInput) {
        profileImageInput.addEventListener('change', function(event) {
            const [file] = event.target.files;
            if (file) {
                profileImagePreview.src = URL.createObjectURL(file);
                profileImagePreview.style.display = 'block';
            }
        });
    }
});
