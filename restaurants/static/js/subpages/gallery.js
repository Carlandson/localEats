import { showToast } from '../components/toast.js';
import { api } from '../utils/subpagesAPI.js';


function attachDescriptionHandlers(businessSubdirectory) {
    const toggleDescriptionBtn = document.getElementById('toggle-description-edit');
    const descriptionDisplay = document.getElementById('description-display');
    const descriptionForm = document.getElementById('description-form');
    const descriptionEditForm = document.getElementById('description-edit-form');
    const saveDescriptionBtn = descriptionForm?.querySelector('.save-button');

    // Description toggle - simple click handler, no async needed
    if (toggleDescriptionBtn) {
        toggleDescriptionBtn.onclick = () => {
            descriptionDisplay.classList.toggle('hidden');
            descriptionForm.classList.toggle('hidden');
        };
    }

    // Save description - needs async for API call
    if (saveDescriptionBtn && descriptionEditForm) {
        saveDescriptionBtn.onclick = async () => {
            try {
                const formData = new FormData(descriptionEditForm);
                const description = formData.get('description');
                
                const response = await api.gallery.updateDescription(businessSubdirectory, {
                    fieldName: 'description',  // Match the expected field name
                    description: description   // The actual description content
                });
                
                if (response.status === 'success') {  // Match the response format
                    descriptionDisplay.innerHTML = description 
                        ? description 
                        : '<p class="text-gray-500 italic">No description added yet.</p>';
                    
                    descriptionDisplay.classList.remove('hidden');
                    descriptionForm.classList.add('hidden');
                    showToast('Description updated successfully', 'success');
                } else {
                    throw new Error(response.error || 'Failed to update description');
                }
            } catch (error) {
                showToast(error.message, 'error');
            }
        };
    }
}

function attachImageHandlers(business) {
    const fileInput = document.getElementById('gallery-image');
    const dropZone = document.getElementById('drop-zone');
    const originalDropZoneContent = dropZone.innerHTML;

    // Attach drag and drop handlers
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('border-indigo-500');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('border-indigo-500');
        });
    });

    // Handle file selection
    fileInput?.addEventListener('change', (event) => {
        if (event.target.files[0]) {
            handleFile(event.target.files[0], originalDropZoneContent, business);
        }
    });

    // Handle file drop
    dropZone?.addEventListener('drop', (event) => {
        const file = event.dataTransfer.files[0];
        if (file) handleFile(file, originalDropZoneContent, business);
    });

    // Attach delete handlers to existing images
    document.querySelectorAll('.delete-image-btn').forEach(btn => {
        btn.addEventListener('click', handleImageDelete);
    });
}

function createImagePreviewHTML(imageUrl, imageId) {
    return `
        <div class="relative group">
            <img src="${imageUrl}" 
                alt="Gallery image" 
                class="h-full w-64 object-cover rounded-lg shadow-md">
            <button type="button"
                data-image-id="${imageId}"
                class="delete-image-btn absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white p-2 rounded-full"
                title="Remove image">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        </div>
    `;
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

async function handleImageDelete() {
    if (!confirm('Are you sure you want to delete this image?')) return;

    const imageId = this.dataset.imageId;
    const galleryItem = this.closest('.gallery-item');
    
    try {
        const business = JSON.parse(document.getElementById('business').textContent);
        consol
        const response = await api.gallery.delete(business, imageId);
        
        if (response.success) {
            galleryItem.remove();
            showToast('Image deleted successfully', 'success');
        } else {
            throw new Error(response.error || 'Failed to delete image');
        }
    } catch (error) {
        showToast(error.message, 'error');
        console.error('Delete error:', error);
    }
}

function handleFile(file, originalContent, business) {
    if (!file.type.startsWith('image/')) {
        showToast('Only image files are allowed', 'error');
        return;
    }

    const dropZone = document.getElementById('drop-zone');
    console.log('DropZone found:', !!dropZone); // Debug log
    
    const reader = new FileReader();

    reader.onload = function(e) {
        dropZone.innerHTML = `
            <div class="relative w-full space-y-4">
                <img src="${e.target.result}" class="h-full w-64 object-cover rounded-lg">
                <button type="button" class="remove-preview absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white p-2 rounded-full transition-colors duration-200">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
                <div class="flex justify-end">
                    <button type="button" id="upload-image-btn" class="upload-btn px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg transition duration-150 ease-in-out">
                        Upload Image
                    </button>
                </div>
            </div>
        `;

        console.log('Upload button created'); // Debug log
        
        const uploadBtn = dropZone.querySelector('.upload-btn');
        console.log('Upload button found:', !!uploadBtn); // Debug log

        // Add click handler for remove button
        dropZone.querySelector('.remove-preview').addEventListener('click', () => {
            dropZone.innerHTML = originalContent;
            document.getElementById('gallery-image').value = '';
        });

        // Add click handler for upload button
        uploadBtn.onclick = async () => { 
            console.log('Upload button clicked');
            const formData = new FormData();
            formData.append('image', file);
            console.log('Form data:', formData);
        
            try {
                const response = await api.gallery.upload(business, formData);  // Use await here
                console.log('Upload response:', response);
                
                if (response.success) {
                    showToast('Image uploaded successfully', 'success');
                    
                    // Add new image to gallery
                    const galleryContainer = document.querySelector('.grid');
                    const newImageElement = document.createElement('div');
                    newImageElement.className = 'gallery-item relative group';
                    newImageElement.innerHTML = createImagePreviewHTML(response.image.url, response.image.id);
        
                    // Add delete functionality to new image
                    const deleteBtn = newImageElement.querySelector('.delete-image-btn');
                    deleteBtn.addEventListener('click', handleImageDelete);
        
                    galleryContainer.insertBefore(newImageElement, galleryContainer.firstChild);
                    
                    // Reset the dropzone
                    dropZone.innerHTML = originalContent;
                    document.getElementById('gallery-image').value = '';
                } else {
                    throw new Error(response.error || 'Upload failed');
                }
            } catch (error) {
                console.error('Upload error:', error);
                showToast(error.message, 'error');
            }
        };
    };
    
    reader.readAsDataURL(file);
}

// Initialize everything when the DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const business = JSON.parse(document.getElementById('business').textContent);
    attachImageHandlers(business);
    attachDescriptionHandlers(business);
    console.log('gallery.js loaded');
});