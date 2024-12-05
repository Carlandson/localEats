import { createSliderControls } from './sliderControls.js';

export function initializeSlider() {
    let currentSlide = 0;
    let slideInterval;

    function setup() {
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

        // Move icon update to a separate function
        function updateIcons(playing) {
            const pauseIcon = pausePlayButton?.querySelector('.pause-icon');
            const playIcon = pausePlayButton?.querySelector('.play-icon');
            
            console.log('Updating icons:', { playing, pauseIcon, playIcon });
            
            if (playing) {
                pauseIcon?.classList.remove('hidden');
                playIcon?.classList.add('hidden');
            } else {
                pauseIcon?.classList.add('hidden');
                playIcon?.classList.remove('hidden');
            }
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

        const controls = createSliderControls(slideInterval, nextSlide);

        // Add event listeners with error checking
        if (prevButton) {
            prevButton.addEventListener('click', (e) => {
                e.preventDefault();
                nextSlide();
                restartAutoSlide();
            });
        }

        if (nextButton) {
            nextButton.addEventListener('click', (e) => {
                e.preventDefault();
                prevSlide();
                restartAutoSlide();
            });
        }

        if (pausePlayButton) {
            pausePlayButton.addEventListener('click', (e) => {
                e.preventDefault();
                controls.toggle();
            });
        }

        dots.forEach((dot, index) => {
            if (index < slides.length) {
                dot.addEventListener('click', (e) => {
                    e.preventDefault();
                    showSlide(index);
                    restartAutoSlide();
                });
                dot.style.display = 'block';
            } else {
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
        controls.start();  
    }

    return {
        init: setup
    };
}