import { displayError } from '../utils/errors.js';
import { smartUpdate } from '../utils/previewUpdates.js';
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
    const prefixes = ['hero-image', 'banner_2', 'banner_3'];
    
    prefixes.forEach(prefix => {
        elements[`${prefix}UploadButton`] = document.getElementById(`upload-${prefix}-button`);
        elements[`${prefix}FileInput`] = document.getElementById(`${prefix}-upload`);
    });
    
    return elements;
}

export function initializeImageUploads(context) {
    const elements = getImageElements();
    const prefixes = ['hero-image', 'banner_2', 'banner_3'];  // Match template prefixes

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

    const inputId = event.target.id;
    const prefix = inputId.replace('-upload', '');
    const bannerType = prefix === 'hero-image' ? 'hero_primary' : prefix;
    const uploadButton = document.getElementById(`upload-${prefix}-button`);

    if (uploadButton) {
        uploadButton.textContent = 'Uploading...';
        uploadButton.disabled = true;
    }

    try {
        // For images, we'll use smartUpdate with a special image type
        await smartUpdate(context, {
            fieldType: 'image',
            fieldName: bannerType,
            value: file,  // Pass the file directly
            previousValue: null, // Previous value not needed for images
            page_type: context.pageSelector.value,
            return_preview: true,
            isFileUpload: true,  // Flag to indicate this is a file upload
            isGlobal: false
        });

        // Update the UI with the new image
        const container = document.getElementById(`${prefix}-container`);
        if (container && context.lastUploadedImageUrl) {
            container.innerHTML = `
                ${createHeroImageHTML(context.lastUploadedImageUrl, prefix)}
                <input type="file" id="${prefix}-upload" accept="image/*" class="hidden">
            `;
            initializeImageUploads(context);
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

    const removeButton = document.getElementById(`remove-${prefix}`);
    const container = document.getElementById(`${prefix}-container`);

    if (!removeButton || !container) {
        console.error('Required elements not found');
        return;
    }

    removeButton.disabled = true;

    try {
        await smartUpdate(context, {
            fieldType: 'image',
            fieldName: prefix === 'hero-image' ? 'hero_primary' : prefix,
            value: null,  // null indicates image removal
            previousValue: container.querySelector('img')?.src || null,
            page_type: context.pageSelector.value,
            return_preview: true,
            isImageRemoval: true,  // Flag to indicate this is an image removal
            isGlobal: false
        });

        // Update container with placeholder
        container.innerHTML = createUploadPlaceholderHTML(prefix);
        
        // Reattach event listeners
        const uploadButton = document.getElementById(`upload-${prefix}-button`);
        const fileInput = document.getElementById(`${prefix}-upload`);
        
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

    } catch (error) {
        console.error('Error removing image:', error);
        displayError('Failed to remove image: ' + error.message);
    } finally {
        if (removeButton) {
            removeButton.disabled = false;
        }
    }
}