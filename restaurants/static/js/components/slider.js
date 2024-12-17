export function initializeSlider() {
    let currentSlide = 0;
    let slideInterval;
    let isPlaying = false;

    function setup(startingSlide = 0) {
        // Get only slides that contain images
        const allSlides = document.querySelectorAll('.slide');
        const slides = Array.from(allSlides).filter(slide => slide.querySelector('img'));
        const dots = document.querySelectorAll('.dot-nav'); 
        const prevButton = document.querySelector('#prev-slide');
        const nextButton = document.querySelector('#next-slide');
        const pausePlayButton = document.querySelector('#pause-play-slider');
        
        if (slides.length === 0) {
            console.log('No slides with images found');
            return null;
        }

        function showSlide(index) {            // Hide all slides first
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
            const nextIndex = (currentSlide + 1) % slides.length;
            showSlide(nextIndex);
        }

        function prevSlide() {
            const prevIndex = (currentSlide - 1 + slides.length) % slides.length;
            showSlide(prevIndex);
        }

        function updateIcons(playing) {
            const pauseIcon = document.querySelector('#pause-play-slider .pause-icon');
            const playIcon = document.querySelector('#pause-play-slider .play-icon');
            
            if (playing) {
                pauseIcon?.classList.remove('hidden');
                playIcon?.classList.add('hidden');
            } else {
                pauseIcon?.classList.add('hidden');
                playIcon?.classList.remove('hidden');
            }
        }

        function startAutoSlide() {
            if (slideInterval) clearInterval(slideInterval);
            slideInterval = setInterval(nextSlide, 5000);
            isPlaying = true;
            updateIcons(true);
        }

        function stopAutoSlide() {
            if (slideInterval) {
                clearInterval(slideInterval);
                slideInterval = null;
            }
            isPlaying = false;
            updateIcons(false);
        }

        function handleSlideChange(direction) {
            if (direction === 'next') {
                nextSlide();
            } else {
                prevSlide();
            }
            
            // Reset the interval if playing
            if (isPlaying) {
                clearInterval(slideInterval);
                slideInterval = setInterval(nextSlide, 5000);
            }
        }

        // Add event listeners
        if (prevButton) {
            prevButton.addEventListener('click', (e) => {
                e.preventDefault();
                handleSlideChange('prev');
            });
        }

        if (nextButton) {
            nextButton.addEventListener('click', (e) => {
                e.preventDefault();
                handleSlideChange('next');
            });
        }

        if (pausePlayButton) {
            pausePlayButton.addEventListener('click', (e) => {
                e.preventDefault();
                if (isPlaying) {
                    stopAutoSlide();
                } else {
                    startAutoSlide();
                }
            });
        }

        dots.forEach((dot, index) => {
            if (index < slides.length) {
                dot.addEventListener('click', (e) => {
                    e.preventDefault();
                    showSlide(index);
                    if (isPlaying) {
                        clearInterval(slideInterval);
                        slideInterval = setInterval(nextSlide, 5000);
                    }
                });
                dot.style.display = 'block';
            } else {
                dot.style.display = 'none';
            }
        });

        // Initialize slider
        showSlide(startingSlide);
        startAutoSlide();
        function getCurrentSlide() {
            return currentSlide;
        }
    
        return {
            start: startAutoSlide,
            stop: stopAutoSlide,
            getCurrentSlide,
            showSlide,
            isPlaying: () => isPlaying,
        }
    }

    return {
        init: setup
    };
}