export function initializeSlider() {
    let currentSlide = 0;
    let slideInterval;
    let isPlaying = true;

    function setup() {
        // Get only slides that contain images
        const allSlides = document.querySelectorAll('.slide');
        const slides = Array.from(allSlides).filter(slide => slide.querySelector('img'));
        const dots = document.querySelectorAll('.dot-nav'); 
        const prevButton = document.querySelector('#prev-slide');
        const nextButton = document.querySelector('#next-slide');
        const pausePlayButton = document.querySelector('#pause-play-slider');
        const pauseIcon = pausePlayButton?.querySelector('.pause-icon');
        const playIcon = pausePlayButton?.querySelector('.play-icon');

        function pauseResumeSlider() {
            isPlaying = !isPlaying;
            
            if (isPlaying) {
                console.log('Resuming auto-slide');
                slideInterval = setInterval(nextSlide, 5000);
                // Update button icons
                pauseIcon?.classList.remove('hidden');
                playIcon?.classList.add('hidden');
            } else {
                console.log('Pausing auto-slide');
                clearInterval(slideInterval);
                slideInterval = null;
                // Update button icons
                pauseIcon?.classList.add('hidden');
                playIcon?.classList.remove('hidden');
            }
        }

        if (pausePlayButton) {
            pausePlayButton.addEventListener('click', (e) => {
                e.preventDefault();
                pauseResumeSlider();
            });
        }

        console.log('Setting up slider with:', {
            totalSlides: allSlides.length,
            activeSlides: slides.length,
            dots: dots.length,
            prevButton: prevButton?.id,
            nextButton: nextButton?.id,
            slideContents: Array.from(allSlides).map((slide, index) => ({
                index,
                hasImage: !!slide.querySelector('img'),
                imageSrc: slide.querySelector('img')?.src || 'no image'
            }))
        });

        if (slides.length === 0) {
            console.log('No slides with images found');
            return null;
        }

        function showSlide(index) {
            console.log('Showing slide:', index);
            // Hide all slides first
            allSlides.forEach(slide => {
                slide.style.opacity = '0';
                slide.style.pointerEvents = 'none';
            });
            
            // Remove active state from all dots
            dots.forEach(dot => {
                dot.classList.remove('opacity-100');
                dot.classList.add('opacity-50');
            });
            
            // Show the active slide
            slides[index].style.opacity = '1';
            slides[index].style.pointerEvents = 'auto';
            
            // Update the corresponding dot
            if (dots[index]) {
                dots[index].classList.remove('opacity-50');
                dots[index].classList.add('opacity-100');
            }

            currentSlide = index;
        }

        function nextSlide() {
            console.log('Next slide clicked, current:', currentSlide, 'total:', slides.length);
            const nextIndex = (currentSlide + 1) % slides.length;
            showSlide(nextIndex);
        }

        function prevSlide() {
            console.log('Previous slide clicked, current:', currentSlide, 'total:', slides.length);
            const prevIndex = (currentSlide - 1 + slides.length) % slides.length;
            showSlide(prevIndex);
        }

        // Add event listeners with error checking
        if (prevButton) {
            console.log('Attaching prev button listener');
            prevButton.addEventListener('click', (e) => {
                e.preventDefault();
                nextSlide();
                restartAutoSlide();
            });
        }

        if (nextButton) {
            console.log('Attaching next button listener');
            nextButton.addEventListener('click', (e) => {
                e.preventDefault();
                prevSlide();
                restartAutoSlide();
            });
        }

        // Add dot listeners only for available slides
        dots.forEach((dot, index) => {
            if (index < slides.length) {
                dot.addEventListener('click', (e) => {
                    e.preventDefault();
                    showSlide(index);
                    restartAutoSlide();
                });
                // Show dot only for available slides
                dot.style.display = 'block';
            } else {
                // Hide dots for non-existent slides
                dot.style.display = 'none';
            }
        });

        function restartAutoSlide() {
            if (slideInterval && isPlaying) {
                clearInterval(slideInterval);
                slideInterval = setInterval(nextSlide, 5000);
            }
        }


        // Show initial slide
        showSlide(0);

        return {
            start: () => {
                console.log('Starting auto-slide');
                isPlaying = true;
                if (slideInterval) clearInterval(slideInterval);
                slideInterval = setInterval(nextSlide, 5000);
                pauseIcon?.classList.remove('hidden');
                playIcon?.classList.add('hidden');
            },
            stop: () => {
                console.log('Stopping auto-slide');
                isPlaying = false;
                if (slideInterval) {
                    clearInterval(slideInterval);
                    slideInterval = null;
                }
                pauseIcon?.classList.add('hidden');
                playIcon?.classList.remove('hidden');
            }
        };
    }

    return {
        init: setup
    };
}