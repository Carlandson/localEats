    // saved from home for changes later
    document.getElementById('id_image').addEventListener('change', function(e) {
        const previewContainer = document.getElementById('image-preview-container');
        const preview = document.getElementById('image-preview');
        const file = e.target.files[0];
    
        if (file) {
            // Show the preview container
            previewContainer.classList.remove('hidden');
            
            // Create a URL for the file
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.src = e.target.result;
            };
            reader.readAsDataURL(file);
        } else {
            // Hide the preview container if no file is selected
            previewContainer.classList.add('hidden');
            preview.src = '';
        }
    });
    // Remove image functionality
    document.getElementById('remove-image').addEventListener('click', function() {
        const imageInput = document.getElementById('id_image');
        const previewContainer = document.getElementById('image-preview-container');
        const preview = document.getElementById('image-preview');
        
        // Clear the file input
        imageInput.value = '';
        
        // Hide the preview
        previewContainer.classList.add('hidden');
        preview.src = '';
    });
    // Update your existing save-news-post event listener to handle the case when image is removed
    document.getElementById('save-news-post').addEventListener('click', async function() {
        const formData = new FormData();
        formData.append('title', document.getElementById('id_title').value);
        formData.append('content', document.getElementById('id_content').value);
        
        const imageInput = document.getElementById('id_image');
        if (imageInput.files.length > 0) {
            formData.append('image', imageInput.files[0]);
        }

        try {
            const response = await fetch(`/api/${business}/news-post/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                },
                body: formData
            });

            const data = await response.json();
            if (response.ok) {
                showToast('News post created successfully!', 'success');
                // Clear the form and preview
                document.getElementById('id_title').value = '';
                document.getElementById('id_content').value = '';
                imageInput.value = '';
                document.getElementById('image-preview-container').classList.add('hidden');
                document.getElementById('image-preview').src = '';
            } else {
                showToast(data.message || 'Error creating news post', 'error');
            }
        } catch (error) {
            showToast('Error creating news post', 'error');
            console.error('Error:', error);
        }
    });