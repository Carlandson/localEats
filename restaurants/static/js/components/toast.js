export function showToast(message, duration = 3000) {
    console.log('Showing toast:', message);
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    
    if (!toast || !toastMessage) return;
    
    toastMessage.textContent = message;
    
    // Show the toast
    toast.classList.remove('translate-x-[-100%]', 'opacity-0');
    toast.classList.add('translate-x-0', 'opacity-100');
    
    // Hide the toast after duration
    setTimeout(() => {
        toast.classList.remove('translate-x-0', 'opacity-100');
        toast.classList.add('translate-x-[-100%]', 'opacity-0');
    }, duration);
}