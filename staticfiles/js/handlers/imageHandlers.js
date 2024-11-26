import { displayError } from '../utils/errors.js';
import { updatePreview } from '../utils/previewUpdates.js';
import { getCookie } from '../utils/cookies.js';
import { createHeroImageHTML, createUploadPlaceholderHTML } from '../utils/placeholders.js';

function getImageElements() {
    return {
        uploadButton: document.getElementById('upload-hero-button'),
        fileInput: document.getElementById('hero-image-upload')
    };
}

export function initializeImageUploads(context) {
    const elements = getImageElements();

    if (elements.uploadButton && elements.fileInput) {
        elements.uploadButton.addEventListener('click', () => {
            if (!elements.uploadButton.disabled) {
                elements.fileInput.click();
            }
        });

        elements.fileInput.addEventListener('change', async function (event) {
            const file = event.target.files[0];
            if (!file) return;

            try {
                const formData = new FormData();
                formData.append('image', file);
                formData.append('page_type', context.pageSelector.value);

                const response = await fetch(`/${context.business_subdirectory}/upload-hero-image/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: formData
                });

                if (!response.ok) {
                    throw new Error('Failed to upload image');
                }

                const data = await response.json();
                if (data.success) {
                    await updatePreview(context.pageSelector.value);
                } else {
                    throw new Error(data.error || 'Upload failed');
                }
            } catch (error) {
                console.error('Error uploading image:', error);
                displayError('Failed to upload image: ' + error.message);
            }
        });
    }
}

export async function handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Get the prefix from the input ID
    const inputId = event.target.id;
    const prefix = inputId.replace('-upload', '');

    const uploadButton = document.getElementById(`upload-${prefix}-button`);
    const formData = new FormData();
    formData.append('image', file);
    formData.append('page_type', pageSelector.value);

    // Map the prefix to the correct banner type
    let bannerType;
    switch (prefix) {
        case 'hero-image':
            bannerType = 'primary';
            break;
        case 'banner-2':
            bannerType = 'banner_2';
            break;
        case 'banner-3':
            bannerType = 'banner_3';
            break;
        default:
            bannerType = 'primary';
    }
    formData.append('banner_type', bannerType);

    if (uploadButton) {
        uploadButton.textContent = 'Uploading...';
        uploadButton.disabled = true;
    }

    try {
        console.log('Uploading image...', prefix);
        const response = await fetch(`/${business_subdirectory}/upload-hero-image/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: formData
        });

        const data = await response.json();
        console.log('Upload response:', data);

        if (data.success) {
            console.log('Image uploaded successfully:', data.image_url);

            // Update the container with the new image
            const container = document.getElementById(`${prefix}-container`);
            if (container) {
                // Use the createHeroImageHTML function instead of inline HTML
                container.innerHTML = `
                    ${createHeroImageHTML(data.image_url, prefix)}
                    <input type="file" id="${prefix}-upload" accept="image/*" class="hidden">
                `;

                // Reattach event listeners
                initializeImageUploads();
                attachRemoveListeners();
            }

            // Update preview
            await updatePreview(pageSelector.value);
        } else {
            throw new Error(data.error || 'Upload failed');
        }
    } catch (error) {
        console.error('Error uploading image:', error);
        displayError('Failed to upload image: ' + error.message);
    } finally {
        if (uploadButton) {
            uploadButton.textContent = 'Upload Image';
            uploadButton.disabled = false;
        }
    }
}

export async function removeHeroImage(prefix) {
    if (!confirm('Are you sure you want to remove this image?')) return;

    const removeButton = document.getElementById(`remove-${prefix}`);
    const container = document.getElementById(`${prefix}-container`);
    const business_subdirectory = document.getElementById('business')?.textContent?.trim().replace(/['"]/g, '');
    const pageSelector = document.getElementById('page-selector');

    if (!removeButton || !container || !business_subdirectory || !pageSelector) {
        console.error('Required elements not found');
        return;
    }

    removeButton.disabled = true;

    try {
        console.log('Removing image for prefix:', prefix);
        const response = await fetch(`/${business_subdirectory}/remove-hero-image/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                page_type: pageSelector.value,
                banner_type: prefix === 'hero-image' ? 'primary' : prefix.replace('banner-', '')
            })
        });

        const data = await response.json();
        console.log('Remove response:', data);

        if (data.success) {
            console.log('Image removed successfully');
            container.innerHTML = createUploadPlaceholderHTML(prefix);
            initializeImageUploads();
            await updatePreview(pageSelector.value);
        } else {
            throw new Error(data.error || 'Remove failed');
        }
    } catch (error) {
        console.error('Error removing image:', error);
        alert('Failed to remove image: ' + error.message);
    } finally {
        if (removeButton) {
            removeButton.disabled = false;
        }
    }
};