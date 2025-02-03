import {getCookie} from '../utils/cookies.js'

// Main initialization function
export function initLogout() {
    console.log('🔑 Initializing logout functionality');
    
    const logoutBtn = document.getElementById('logoutBtn');
    const logoutPopup = document.getElementById('logoutPopup');
    const confirmLogout = document.getElementById('confirmLogout');
    const cancelLogout = document.getElementById('cancelLogout');

    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            logoutPopup.classList.remove('hidden');
        });
    }

    if (cancelLogout) {
        cancelLogout.addEventListener('click', () => {
            logoutPopup.classList.add('hidden');
        });
    }

    if (confirmLogout) {
        confirmLogout.addEventListener('click', function() {
            const logoutUrl = this.getAttribute('data-logout-url');
            if (!logoutUrl) {
                console.error('Logout URL not set');
                return;
            }

            const csrfToken = getCookie('csrftoken');

            fetch(logoutUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                credentials: 'same-origin'
            })
            .then(response => {
                if (response.ok) {
                    window.location.href = '/';
                } else {
                    console.error('Logout failed');
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }
}
