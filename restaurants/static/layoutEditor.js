document.addEventListener('DOMContentLoaded', function() {
    const kitchen = JSON.parse(document.getElementById('kitchen').textContent);

    // Image Upload Handling
    const uploadButton = document.getElementById('upload-hero-button');
    const fileInput = document.getElementById('hero-image-upload');
    const removeButton = document.getElementById('remove-hero-image');

    if (uploadButton && fileInput) {
        uploadButton.addEventListener('click', () => {
            fileInput.click();
        });

        fileInput.addEventListener('change', handleImageUpload);
    }

    if (removeButton) {
        removeButton.addEventListener('click', removeHeroImage);
    }

    // Component Selectors
    document.querySelectorAll('.component-selector').forEach(selector => {
        selector.addEventListener('change', function() {
            const component = this.dataset.component;
            const style = this.value;
            console.log('Changing component:', component, 'to style:', style);
            updateComponent(component, style);
        });
    });

    // Color Pickers
    document.querySelectorAll('.color-picker').forEach(picker => {
        picker.addEventListener('input', function() {
            const colorType = this.dataset.colorType;
            updateColors(colorType, this.value);
        });
    });

    // Functions
    function handleImageUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('hero_image', file);
        
        // Show loading state
        const uploadButton = document.getElementById('upload-hero-button');
        const originalText = uploadButton.textContent;
        uploadButton.textContent = 'Uploading...';
        uploadButton.disabled = true;

        fetch(`/${kitchen}/upload-hero-image/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Refresh the preview
                updateComponent('hero', document.querySelector('input[name="hero_style"]:checked').value);
                location.reload(); // Simple solution - refresh the page
            } else {
                alert('Error uploading image: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error uploading image');
        })
        .finally(() => {
            // Reset button state
            uploadButton.textContent = originalText;
            uploadButton.disabled = false;
            // Reset file input
            event.target.value = '';
        });
    }

    function removeHeroImage(event) {
        event.preventDefault();
        
        if (!confirm('Are you sure you want to remove the hero image?')) {
            return;
        }

        const button = event.target.closest('button');
        button.disabled = true;

        fetch(`/${kitchen}/remove-hero-image/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Refresh the preview
                updateComponent('hero', document.querySelector('input[name="hero_style"]:checked').value);
                location.reload();
            } else {
                alert('Error removing image: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error removing image');
        })
        .finally(() => {
            button.disabled = false;
        });
    }

    function updateComponent(component, style) {
        const url = `/${kitchen}/preview-component/${component}/${style}/`;
        console.log('Fetching from:', url);
        
        fetch(url)
            .then(response => {
                console.log('Response status:', response.status);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.text();
            })
            .then(html => {
                console.log('Received HTML length:', html.length);
                const previewElement = document.getElementById(`${component}-preview`);
                if (previewElement) {
                    console.log(`Found ${component}-preview element`);
                    previewElement.innerHTML = html;
                    console.log('Updated preview content');
                } else {
                    console.error(`Could not find element with id: ${component}-preview`);
                }
            })
            .catch(error => {
                console.error('Error updating component:', error);
                console.error('Component:', component);
                console.error('Style:', style);
            });
    }

    function updateColors(type, value) {
        document.documentElement.style.setProperty(`--color-${type}`, value);
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});