export function debounce(func, wait) {
    let timeout;
    
    return function executedFunction(...args) {
        // Cancel any existing timeout
        clearTimeout(timeout);
        
        // Create a new timeout
        timeout = setTimeout(() => {
            func.apply(this, args);
        }, wait);
    };
}
export function throttle(func, limit) {
    let inThrottle;
    
    return function executedFunction(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => {
                inThrottle = false;
            }, limit);
        }
    };
}