
    const gridRow1 = document.getElementById('gridRow1');
    const gridRow2 = document.getElementById('gridRow2');
    const leftArrow = document.querySelector('.left-arrow');
    const rightArrow = document.querySelector('.right-arrow');

    let scrollPosition = 0;
    let isAnimating = false;
    const scrollAmount = 200;
    const animationDuration = 500; // durée de l'animation en ms

    function checkOverflow(element) {
        return element.scrollWidth > element.clientWidth;
    }

    function updateArrowVisibility() {
        const maxScroll = gridRow1.scrollWidth - gridRow1.clientWidth;
        const shouldShowArrows = checkOverflow(gridRow1) || checkOverflow(gridRow2);
        
        leftArrow.style.display = shouldShowArrows && scrollPosition < 0 ? 'flex' : 'none';
        rightArrow.style.display = shouldShowArrows && scrollPosition > maxScroll * -1 ? 'flex' : 'none';
    }

    function smoothScroll(targetPosition) {
        if (isAnimating) return;
        isAnimating = true;

        const startPosition = scrollPosition;
        const distance = targetPosition - startPosition;
        const startTime = performance.now();

        function animate(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / animationDuration, 1);

            // Fonction d'easing pour une animation plus fluide
            const easeProgress = progress < .5 ? 
                4 * progress * progress * progress : 
                (progress - 1) * (2 * progress - 2) * (2 * progress - 2) + 1;

            scrollPosition = startPosition + (distance * easeProgress);
            gridRow1.style.transform = `translateX(${scrollPosition}px)`;
            gridRow2.style.transform = `translateX(${scrollPosition}px)`;

            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                isAnimating = false;
                updateArrowVisibility();
            }
        }

        requestAnimationFrame(animate);
    }

    leftArrow.addEventListener('click', () => {
        const targetPosition = Math.min(scrollPosition + scrollAmount, 0);
        smoothScroll(targetPosition);
    });

    rightArrow.addEventListener('click', () => {
        const maxScroll = -(gridRow1.scrollWidth - gridRow1.clientWidth);
        const targetPosition = Math.max(scrollPosition - scrollAmount, maxScroll);
        smoothScroll(targetPosition);
    });

    // Ajout du défilement par glissement tactile
    let touchStartX = 0;
    let touchEndX = 0;

    document.querySelector('.grids-container').addEventListener('touchstart', (e) => {
        touchStartX = e.touches[0].clientX;
    }, false);

    document.querySelector('.grids-container').addEventListener('touchmove', (e) => {
        e.preventDefault();
        touchEndX = e.touches[0].clientX;
    }, { passive: false });

    document.querySelector('.grids-container').addEventListener('touchend', () => {
        const swipeDistance = touchStartX - touchEndX;
        if (Math.abs(swipeDistance) > 50) { // Seuil minimal pour déclencher le défilement
            const targetPosition = scrollPosition + (swipeDistance < 0 ? scrollAmount : -scrollAmount);
            const maxScroll = -(gridRow1.scrollWidth - gridRow1.clientWidth);
            smoothScroll(Math.max(Math.min(targetPosition, 0), maxScroll));
        }
    }, false);

    window.addEventListener('load', updateArrowVisibility);
    window.addEventListener('resize', updateArrowVisibility);

    // const items = document.querySelectorAll('.grid-item');
    // items.forEach(item => {
    //     item.addEventListener('click', () => {
    //         alert('Vous avez cliqué sur ' + item.textContent);
    //     });
    // });


    // Get the button
    let mybutton = document.getElementById("scrollToTopBtn");

    // When the user scrolls down 20px from the top of the document, show the button
    window.onscroll = function () {
        scrollFunction();
    };

    function scrollFunction() {
        if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
            mybutton.classList.add("show");
        } else {
            mybutton.classList.remove("show");
        }
    }

    // When the user clicks on the button, scroll to the top of the document
    mybutton.addEventListener('click', function () {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });


 
    document.addEventListener('DOMContentLoaded', function() {
        const gridItems = document.querySelectorAll('.grid-item');
        const colors = [
            '#FF5733', '#33FF57', '#3357FF', '#FF33A6', '#A633FF',
            '#33FFF5', '#FF9F33', '#33FF9F', '#FF5733', '#FF5733',
            '#A6FF33', '#FF33C1', '#5733FF', '#FFC133', '#33A6FF'
        ];

        gridItems.forEach(item => {
            // Générer des indices aléatoires pour choisir deux couleurs
            const colorStartIndex = Math.floor(Math.random() * colors.length);
            let colorEndIndex = Math.floor(Math.random() * colors.length);

            // S'assurer que les deux couleurs sont différentes
            while (colorEndIndex === colorStartIndex) {
                colorEndIndex = Math.floor(Math.random() * colors.length);
            }

            const colorStart = colors[colorStartIndex];
            const colorEnd = colors[colorEndIndex];

            item.style.background = `linear-gradient(45deg, ${colorStart}, ${colorEnd})`;

            // Définir la couleur du texte en fonction de la luminosité de la couleur de départ
            const rgb = hexToRgb(colorStart);
            const brightness = Math.round(((parseInt(rgb.r) * 299) + (parseInt(rgb.g) * 587) + (parseInt(rgb.b) * 114)) / 1000);
            item.style.color = (brightness > 125) ? 'black' : 'white';
        });

        function hexToRgb(hex) {
            const shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
            hex = hex.replace(shorthandRegex, function(m, r, g, b) {
                return r + r + g + g + b + b;
            });

            const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
            return result ? {
                r: parseInt(result[1], 16),
                g: parseInt(result[2], 16),
                b: parseInt(result[3], 16)
            } : null;
        }
    });

