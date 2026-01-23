import { showToast } from '../components/toast.js';
import { api } from '../utils/subpagesAPI.js';


function attachDescriptionHandlers(businessSubdirectory) {
    const toggleDescriptionBtn = document.getElementById('toggle-description-edit');
    const showDescriptionBtn = document.getElementById('show-description-checkbox');
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
    // show description toggle 
    // need to check this first
    showDescriptionBtn.addEventListener('change', async () => {
        try {
            await api.gallery.toggleDescription(businessSubdirectory, {
                fieldName: 'show_description',
                value: showDescriptionBtn.checked
            });
            showToast('Description toggle updated successfully');

        } catch (error) {
            console.error('Error:', error);
            showToast('Failed to update description toggle. Please try again.');
        }
    });
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
                    showToast('Description updated successfully');
                } else {
                    throw new Error(response.error || 'Failed to update description');
                }
            } catch (error) {
                showToast(error.message);
            }
        };
    }
}

function attachImageHandlers(business) {
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

    // Function to attach file input handler (can be called multiple times)
    const attachFileInputHandler = () => {
        const currentFileInput = document.getElementById('gallery-image');
        if (currentFileInput) {
            // Remove any existing listeners by cloning
            const newFileInput = currentFileInput.cloneNode(true);
            currentFileInput.parentNode.replaceChild(newFileInput, currentFileInput);
            
            newFileInput.addEventListener('change', (event) => {
                if (event.target.files[0]) {
                    handleFile(event.target.files[0], originalDropZoneContent, business, attachFileInputHandler);
                }
            });
        }
    };
    attachFileInputHandler();
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
        <div class="relative">
            <img src="${imageUrl}" 
                alt="Gallery image"
                class="w-full h-auto object-cover rounded-lg shadow-md"
                loading="lazy"
                data-aspect-ratio>
            <button type="button"
                data-image-id="${imageId}"
                class="delete-image-btn absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white p-2 rounded-full">
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
        const response = await api.gallery.delete(business, imageId);
        
        if (response.success) {
            galleryItem.remove();
            showToast('Image deleted successfully');
        } else {
            throw new Error(response.error || 'Failed to delete image');
        }
    } catch (error) {
        showToast('error', error.message);
        console.error('Delete error:', error);
    }
}

function handleFile(file, originalContent, business, reattachHandler) {
    if (!file.type.startsWith('image/')) {
        showToast('Only image files are allowed', 'error');
        return;
    }

    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('gallery-image');
    console.log('DropZone found:', !!dropZone); // Debug log
    
    const reader = new FileReader();

    reader.onload = function(e) {
        dropZone.innerHTML = `
            <div class="relative w-full space-y-4 flex flex-col items-center justify-center">
                <img src="${e.target.result}" class="h-full w-64 object-cover rounded-lg">
                <button type="button" class="remove-preview absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white p-2 rounded-full transition-colors duration-200">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
                <button type="button" id="upload-image-btn" class="upload-btn w-full px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg transition duration-150 ease-in-out">
                    Upload Image
                </button>
            </div>
        `;

        console.log('Upload button created'); // Debug log
        
        const uploadBtn = dropZone.querySelector('.upload-btn');
        console.log('Upload button found:', !!uploadBtn); // Debug log

        // Add click handler for remove button
        dropZone.querySelector('.remove-preview').addEventListener('click', () => {
            dropZone.innerHTML = originalContent;
            fileInput.value = '';
            // Re-attach file input handler after restoring content
            if (reattachHandler) {
                reattachHandler();
            }
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
                    const newImg = newImageElement.querySelector('img');
                    if (newImg) {
                        newImg.onload = () => {
                            calculateItemSpan(newImageElement, newImg, 10, 16);
                        };
                        if (newImg.complete) {
                            calculateItemSpan(newImageElement, newImg, 10, 16);
                        }
                    }
                    // Reset the dropzone
                    dropZone.innerHTML = originalContent;
                    document.getElementById('gallery-image').value = '';
                    if (reattachHandler) {
                        reattachHandler();
                    }
                } else {
                    showToast(response.error, 'error');
                    throw new Error(response.error || 'Upload failed');
                }
            } catch (error) {
                console.error('Upload error:', error);
                showToast(error.message);
            }
        };
    };
    
    reader.readAsDataURL(file);
}

// masonry grid layout logic
function calculateGridSpans() {
    const grid = document.getElementById('gallery-grid');
    if (!grid) return;
    
    const items = grid.querySelectorAll('.gallery-item');
    const rowHeight = 10; // Match auto-rows-[10px]
    const gap = 16; // Match gap-4 (1rem = 16px)
    
    items.forEach(item => {
        const img = item.querySelector('img');
        if (!img.complete) {
            img.onload = () => calculateItemSpan(item, img, rowHeight, gap);
        } else {
            calculateItemSpan(item, img, rowHeight, gap);
        }
    });
}

function calculateItemSpan(item, img, rowHeight, gap) {
    const grid = document.getElementById('gallery-grid');
    const gridWidth = grid.offsetWidth;
    const cols = window.innerWidth >= 768 ? 4 : 1;
    const colWidth = (gridWidth - (gap * (cols - 1))) / cols;
    console.log(window.innerWidth, cols, colWidth);
    const naturalHeight = img.naturalHeight;
    const naturalWidth = img.naturalWidth;
    const aspectRatio = naturalHeight / naturalWidth;
    const displayHeight = colWidth * aspectRatio;
    
    // Calculate span (height + gap) / rowHeight
    const span = Math.ceil((displayHeight + gap) / rowHeight);
    item.style.gridRowEnd = `span ${span}`;
}

// Progressive image loading
function setupProgressiveLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                const placeholder = img.src;
                const fullImage = new Image();
                
                fullImage.onload = () => {
                    img.src = fullImage.src;
                    img.classList.remove('blur-sm', 'opacity-50');
                    img.classList.add('opacity-100');
                };
                
                fullImage.src = img.dataset.src;
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Initialize everything when the DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const business = JSON.parse(document.getElementById('business').textContent);
    attachImageHandlers(business);
    setupProgressiveLoading();
    attachDescriptionHandlers(business);
    if (document.getElementById('gallery-grid')) {
        calculateGridSpans();
        // Recalculate on window resize
        let resizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(calculateGridSpans, 250);
        });
    }
});
