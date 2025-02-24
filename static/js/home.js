document.addEventListener('DOMContentLoaded', function () {
    const carousels = document.querySelectorAll('.news-carousel, .event-carousel');

    carousels.forEach(carousel => {
        const items = Array.from(carousel.children);
        const itemWidth = items[0].offsetWidth + 20;
        const totalWidth = itemWidth * items.length;
        carousel.style.width = `${totalWidth}px`;

        let position = 0;
        let currentIndex = 0;
        const speed = 1;
        let animationFrame;

        // Fonction pour mettre à jour l'élément actif
        function updateActiveItem() {
            items.forEach(item => {
                item.classList.remove('active');
            });
            
            // Calculer l'index de l'élément actif basé sur la position
            const activeIndex = Math.floor((position + itemWidth / 2) / itemWidth) % items.length;
            items[activeIndex]?.classList.add('active');
        }

        function animate() {
            position += speed;

            if (position >= totalWidth / 2) {
                position = 0;
            }

            carousel.style.transform = `translateX(${-position}px)`;
            updateActiveItem();
            animationFrame = requestAnimationFrame(animate);
        }

        animate();

        // Gestion des flèches
        const container = carousel.closest('.carousel-container');
        const leftArrow = container.querySelector('.carousel-arrow.left');
        const rightArrow = container.querySelector('.carousel-arrow.right');

        function moveToItem(index) {
            cancelAnimationFrame(animationFrame);
            position = index * itemWidth;
            carousel.style.transform = `translateX(${-position}px)`;
            updateActiveItem();
            setTimeout(() => {
                animate();
            }, 100);
        }

        leftArrow.addEventListener('click', () => {
            moveToItem(0);
        });

        rightArrow.addEventListener('click', () => {
            moveToItem(Math.floor(items.length / 2));
        });

        // Gestion des pauses
        const pauseAnimation = () => {
            cancelAnimationFrame(animationFrame);
        };

        const resumeAnimation = () => {
            if (!carousel.matches(':hover') && 
                !leftArrow.matches(':hover') && 
                !rightArrow.matches(':hover')) {
                animate();
            }
        };

        carousel.addEventListener('mouseenter', pauseAnimation);
        carousel.addEventListener('mouseleave', resumeAnimation);
        leftArrow.addEventListener('mouseenter', pauseAnimation);
        leftArrow.addEventListener('mouseleave', resumeAnimation);
        rightArrow.addEventListener('mouseenter', pauseAnimation);
        rightArrow.addEventListener('mouseleave', resumeAnimation);

        // Animation initiale
        updateActiveItem();
    });
});