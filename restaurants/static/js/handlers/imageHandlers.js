import { displayError } from '../utils/errors.js';
import { updatePreview } from '../utils/previewUpdates.js';
import { getCookie } from '../utils/cookies.js';
import { createHeroImageHTML, createUploadPlaceholderHTML } from '../utils/placeholders.js';

function attachRemoveListeners(context) {
    document.querySelectorAll('[id^="remove-"]').forEach(button => {
        // Remove existing listeners by cloning and replacing the button
        const newButton = button.cloneNode(true);
        button.parentNode.replaceChild(newButton, button);
        
        // Add new listener
        newButton.addEventListener('click', () => {
            const prefix = newButton.id.replace('remove-', '');
            removeHeroImage(prefix, context);
        });
    });
}

function getImageElements() {
    // Match the exact prefixes from the template
    const elements = {};
    const prefixes = ['hero-image', 'hero_banner_2', 'hero_banner_3'];
    
    prefixes.forEach(prefix => {
        elements[`${prefix}UploadButton`] = document.getElementById(`upload-${prefix}-button`);
        elements[`${prefix}FileInput`] = document.getElementById(`${prefix}-upload`);
    });
    
    return elements;
}

export function initializeImageUploads(context) {
    const elements = getImageElements();
    const prefixes = ['hero-image', 'hero_banner_2', 'hero_banner_3'];  // Match template prefixes

    attachRemoveListeners(context);

    prefixes.forEach(prefix => {
        const uploadButton = elements[`${prefix}UploadButton`];
        const fileInput = elements[`${prefix}FileInput`];

        if (uploadButton && fileInput) {
            // Remove existing listeners before adding new ones
            uploadButton.replaceWith(uploadButton.cloneNode(true));
            fileInput.replaceWith(fileInput.cloneNode(true));

            // Get the fresh elements after replacing
            const newUploadButton = document.getElementById(`upload-${prefix}-button`);
            const newFileInput = document.getElementById(`${prefix}-upload`);

            if (newUploadButton && newFileInput) {
                // Add click listener to upload button
                newUploadButton.addEventListener('click', () => {
                    if (!newUploadButton.disabled) {
                        newFileInput.click();
                    }
                });

                // Add change listener to file input
                newFileInput.addEventListener('change', async (event) => {
                    await handleImageUpload(event, context);
                });
            }
        }
    });
}

export async function handleImageUpload(event, context) {
    const file = event.target.files[0];
    if (!file) return;

    // Get the prefix from the input ID
    const inputId = event.target.id;
    const prefix = inputId.replace('-upload', '');

    // Map frontend prefix to backend format
    let bannerType;
    switch (prefix) {
        case 'hero-image':
            bannerType = 'hero_primary';
            break;
        case 'hero_banner_2':
            bannerType = 'hero_banner_2';
            break;
        case 'hero_banner_3':
            bannerType = 'hero_banner_3';
            break;
        default:
            bannerType = 'hero_primary';
    }

    const uploadButton = document.getElementById(`upload-${prefix}-button`);
    const formData = new FormData();
    formData.append('image', file);
    formData.append('page_type', context.pageSelector.value);
    formData.append('banner_type', bannerType);

    if (uploadButton) {
        uploadButton.textContent = 'Uploading...';
        uploadButton.disabled = true;
    }

    try {
        const response = await fetch(`/${context.business_subdirectory}/upload-hero-image/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            const container = document.getElementById(`${prefix}-container`);
            if (container) {
                container.innerHTML = `
                    ${createHeroImageHTML(data.image_url, prefix)}
                    <input type="file" id="${prefix}-upload" accept="image/*" class="hidden">
                `;

                initializeImageUploads(context);
            }

            await updatePreview(context.pageSelector.value, context);
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

export async function removeHeroImage(prefix, context) {
    if (!confirm('Are you sure you want to remove this image?')) return;

    // Match the IDs from the template
    const removeButton = document.getElementById(`remove-${prefix}`);
    const container = document.getElementById(`${prefix}-container`);

    if (!removeButton || !container) {
        console.error('Required elements not found:', {
            prefix,
            removeButtonId: `remove-${prefix}`,
            containerId: `${prefix}-container`
        });
        return;
    }

    removeButton.disabled = true;

    try {
        console.log('Removing image for prefix:', prefix);
        const response = await fetch(`/${context.business_subdirectory}/remove-hero-image/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                page_type: context.pageSelector.value,
                banner_type: prefix === 'hero-image' ? 'hero_primary' : prefix
            })
        });

        const data = await response.json();
        console.log('Remove response:', data);

        if (data.success) {
            console.log('Image removed successfully');
            
            // Update container with placeholder
            container.innerHTML = createUploadPlaceholderHTML(prefix);
            
            // Get the new elements with correct ID format
            const uploadButton = document.getElementById(`upload-${prefix}-button`);
            const fileInput = document.getElementById(`${prefix}-upload`);
            
            // Attach new listeners
            if (uploadButton && fileInput) {
                uploadButton.addEventListener('click', () => {
                    if (!uploadButton.disabled) {
                        fileInput.click();
                    }
                });

                fileInput.addEventListener('change', async (event) => {
                    await handleImageUpload(event, context);
                });
            }
            
            await updatePreview(context.pageSelector.value, context);
        } else {
            throw new Error(data.error || 'Remove failed');
        }
    } catch (error) {
        console.error('Error removing image:', error);
        displayError('Failed to remove image: ' + error.message);
    } finally {
        if (removeButton) {
            removeButton.disabled = false;
        }
    }
}