export function initializeSlider() {
    let currentSlider = null;

    function createSlider() {
        const slides = document.querySelectorAll('.slide');
        const dots = document.querySelectorAll('.bottom-4 button');
        const prevButton = document.getElementById('prev-slide');
        const nextButton = document.getElementById('next-slide');
        let currentSlide = 0;
        let slideInterval;

        function showSlide(index) {
            slides.forEach(slide => slide.style.opacity = '0');
            dots.forEach(dot => dot.classList.remove('opacity-100'));
            
            slides[index].style.opacity = '1';
            dots[index].classList.add('opacity-100');
        }

        function nextSlide() {
            currentSlide = (currentSlide + 1) % slides.length;
            showSlide(currentSlide);
        }

        function prevSlide() {
            currentSlide = (currentSlide - 1 + slides.length) % slides.length;
            showSlide(currentSlide);
        }

        // Only initialize if we have slides
        if (slides.length > 0) {
            if (nextButton) nextButton.addEventListener('click', nextSlide);
            if (prevButton) prevButton.addEventListener('click', prevSlide);
            
            dots.forEach((dot, index) => {
                dot.addEventListener('click', () => {
                    currentSlide = index;
                    showSlide(currentSlide);
                });
            });

            slideInterval = setInterval(nextSlide, 5000);
            showSlide(0);
        }

        return {
            destroy: () => {
                if (slideInterval) clearInterval(slideInterval);
                if (nextButton) nextButton.removeEventListener('click', nextSlide);
                if (prevButton) prevButton.removeEventListener('click', prevSlide);
                dots.forEach((dot, index) => {
                    dot.removeEventListener('click', () => {});
                });
            }
        };
    }

    return {
        start: () => {
            console.log('Starting slider');
            if (currentSlider) currentSlider.destroy();
            currentSlider = createSlider();
        },
        stop: () => {
            console.log('Stopping slider');
            if (currentSlider) {
                currentSlider.destroy();
                currentSlider = null;
            }
        }
    };
}