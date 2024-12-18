export class GoogleMapsLoader {
    static loadAPI(apiKey) {
        return new Promise((resolve, reject) => {
            // Check if API is already loaded
            if (window.google && window.google.maps) {
                resolve(window.google.maps);
                return;
            }

            // Create callback function
            window.initGoogleMaps = () => {
                if (window.google && window.google.maps) {
                    resolve(window.google.maps);
                } else {
                    reject(new Error('Google Maps failed to load'));
                }
            };

            try {
                // Dynamically create the script element
                const script = document.createElement('script');
                script.defer = true;  // Add defer
                script.async = true;  // Keep async
                script.nonce = document.querySelector('meta[name="csp-nonce"]')?.content; // Optional: Add CSP nonce if you use it
                
                // Set the complete URL with callback
                const url = new URL('https://maps.googleapis.com/maps/api/js');
                url.searchParams.append('key', apiKey);
                url.searchParams.append('libraries', 'places');
                url.searchParams.append('callback', 'initGoogleMaps');
                url.searchParams.append('loading', 'async'); // Add explicit async loading parameter
                
                script.src = url.toString();
                
                // Add error handling
                script.onerror = () => {
                    reject(new Error('Failed to load Google Maps API script'));
                };

                // Append the script to head
                document.head.appendChild(script);
            } catch (error) {
                reject(error);
            }
        });
    }
}