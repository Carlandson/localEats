export function createSliderControls(slideInterval, nextSlide) {
    let isPlaying = true;
    let interval = slideInterval;

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

    const controls = {
        start: () => {
            console.log('Starting auto-slide');
            isPlaying = true;
            if (interval) clearInterval(interval);
            interval = setInterval(nextSlide, 5000);
            updateIcons(true);
        },
        stop: () => {
            console.log('Stopping auto-slide');
            isPlaying = false;
            if (interval) {
                clearInterval(interval);
                interval = null;
            }
            updateIcons(false);
        },
        toggle: () => {
            console.log('Toggling slider:', { currentState: isPlaying });
            if (isPlaying) {
                controls.stop();
            } else {
                controls.start();
            }
        },
        isPlaying: () => isPlaying
    };

    return controls;
}