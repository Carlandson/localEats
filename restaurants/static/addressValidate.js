document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded');
    const addressInput = document.getElementById('id_address');
    const validateButton = document.getElementById('validate-address');

    if (!addressInput) {
        console.error('Address input not found');
    }
    if (!validateButton) {
        console.error('Validate button not found');
    }

    validateButton.addEventListener('click', function() {
        console.log('Validate button clicked');
        const address = addressInput.value;
        validateAddress(address);
    });

    function validateAddress(address) {
        console.log('Validating address:', address);
        if (typeof google === 'undefined' || typeof google.maps === 'undefined') {
            console.error('Google Maps API not loaded');
            return;
        }
        const geocoder = new google.maps.Geocoder();
        geocoder.geocode({ address: address }, function(results, status) {
            console.log('Geocode result:', status);
            if (status === google.maps.GeocoderStatus.OK) {
                const formattedAddress = results[0].formatted_address;
                addressInput.value = formattedAddress;
                console.log('Address validated:', formattedAddress);
                alert('Address validated and formatted: ' + formattedAddress);
            } else {
                console.error('Geocode failed:', status);
                alert('Unable to validate address. Please check and try again.');
            }
        });
    }
});