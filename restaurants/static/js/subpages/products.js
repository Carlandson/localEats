import { showToast } from '../components/toast.js';
import { api } from '../utils/subpagesAPI.js';
import { createProductFormHTML } from '../utils/placeholders.js';

document.addEventListener('DOMContentLoaded', function() {
    const business = JSON.parse(document.getElementById('business').textContent);
    const formContainer = document.getElementById('product-form-container');
    const addButton = document.getElementById('add-product');
    const descriptionButton = document.getElementById('toggle-description-edit');
    const descriptionForm = document.getElementById('description-form');
    const descriptionDisplay = document.getElementById('description-display');

    descriptionButton?.addEventListener('click', () => {
        const descriptionHidden = descriptionForm.classList.contains('hidden');
        
        if (descriptionHidden) {
            // Show form, hide display
            descriptionForm.classList.remove('hidden');
            descriptionDisplay.classList.add('hidden');
            descriptionButton.textContent = 'Cancel';
            // Change button style to indicate cancel action
            descriptionButton.classList.remove('bg-indigo-600', 'hover:bg-indigo-700');
            descriptionButton.classList.add('bg-gray-500', 'hover:bg-gray-600');
        } else {
            // Hide form, show display
            descriptionForm.classList.add('hidden');
            descriptionDisplay.classList.remove('hidden');
            descriptionButton.textContent = 'Edit Description';
            // Restore original button style
            descriptionButton.classList.remove('bg-gray-500', 'hover:bg-gray-600');
            descriptionButton.classList.add('bg-indigo-600', 'hover:bg-indigo-700');
            // Optional: Reset form
            const form = descriptionForm.querySelector('form');
            if (form) form.reset();
        }
    });
    // Show/hide form handlers
    addButton?.addEventListener('click', () => {
        const isHidden = formContainer.classList.contains('hidden');
        
        if (isHidden) {
            // Show form
            formContainer.classList.remove('hidden');
            addButton.textContent = 'Cancel';
            addButton.classList.remove('bg-emerald-500', 'hover:bg-emerald-600');
            addButton.classList.add('bg-gray-500', 'hover:bg-gray-600');
        } else {
            formContainer.classList.add('hidden');
            addButton.textContent = 'Add New Product';
            addButton.classList.remove('bg-gray-500', 'hover:bg-gray-600');
            addButton.classList.add('bg-emerald-500', 'hover:bg-emerald-600');
            const form = formContainer.querySelector('form');
            if (form) form.reset();
        }
    });

    document.querySelector('.cancel-add')?.addEventListener('click', () => {
        formContainer.classList.add('hidden');
        addButton.style.display = 'block';
        document.getElementById('createProduct').reset();
    });

    document.querySelector('[data-section="save-description"]')?.addEventListener('click', async () => {
        const descriptionInput = document.getElementById('id_description');
        const descriptionText = descriptionInput.value;

        try {
            await api.products.updateSettings(business, {
                fieldName: 'description',
                description: descriptionText  // Send the actual text value
            });
            
            // Update the displayed description
            const descriptionDisplay = document.getElementById('description-display');
            descriptionDisplay.innerHTML = descriptionText 
                ? descriptionText.replace(/\n/g, '<br>') 
                : '<p class="text-gray-500 italic">No description added yet.</p>';

            // Hide form, show display
            descriptionForm.classList.add('hidden');
            descriptionDisplay.classList.remove('hidden');
            
            // Reset button
            descriptionButton.textContent = 'Edit Description';
            descriptionButton.classList.remove('bg-gray-500', 'hover:bg-gray-600');
            descriptionButton.classList.add('bg-indigo-600', 'hover:bg-indigo-700');

            showToast('Changes saved successfully!');
        } catch (error) {
            console.error('Error:', error);
            showToast('Failed to update setting. Please try again.', 'error');
        }
    });
    function handleImagePreview(input) {
        const file = input.files[0];
        if (!file) return;

        // Find or create preview container
        let previewContainer = input.parentElement.querySelector('.image-preview');
        if (!previewContainer) {
            previewContainer = document.createElement('div');
            previewContainer.className = 'image-preview mb-2 mt-2 relative';
            input.parentElement.insertBefore(previewContainer, input);
        } else {
            previewContainer.innerHTML = ''; // Clear existing preview
        }

        // Create and setup image element
        const img = document.createElement('img');
        img.className = 'w-32 h-32 object-cover rounded-lg';

        // Create remove button
        const removeButton = document.createElement('button');
        removeButton.className = 'absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center hover:bg-red-600 transition-colors duration-200';
        removeButton.innerHTML = '×';
        removeButton.type = 'button';
        
        // Remove button click handler
        removeButton.onclick = function() {
            previewContainer.remove();
            input.value = ''; // Clear the file input
        };

        // Create and show loading message
        const loading = document.createElement('div');
        loading.className = 'text-sm text-gray-500';
        loading.textContent = 'Loading preview...';
        previewContainer.appendChild(loading);

        // Setup file reader
        const reader = new FileReader();
        reader.onload = function(e) {
            loading.remove();
            img.src = e.target.result;
            previewContainer.appendChild(img);
            previewContainer.appendChild(removeButton);
        };

        reader.onerror = function() {
            previewContainer.innerHTML = '<div class="text-red-500 text-sm">Error loading preview</div>';
        };

        reader.readAsDataURL(file);
    }

    // Add event listener to file input
    document.addEventListener('change', function(e) {
        if (e.target.type === 'file' && e.target.accept.includes('image')) {
            handleImagePreview(e.target);
        }
    });

    // Form submission
    document.getElementById('createProduct')?.addEventListener('submit', async (event) => {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);
        
        const errorDisplay = document.getElementById('form-error-message');
        errorDisplay.textContent = '';
        errorDisplay.classList.add('hidden');
    
        try {
            const response = await api.products.createProduct(business, formData);
            
            if (response.success) {
                showToast('Product created successfully!');
                // Success - refresh the products list
                location.reload();
            }
    
        } catch (error) {
            console.error('Error:', error);
            errorDisplay.textContent = error.message || 'An unexpected error occurred. Please try again.';
            errorDisplay.classList.remove('hidden');
        }
    });

    // Edit/Delete handlers
    document.querySelectorAll('.editProduct').forEach(button => {
        button.addEventListener('click', () => {
            const productId = button.id.substring(1);
            editProduct(business, productId);
        });
    });

    document.querySelectorAll('.deleteProduct').forEach(button => {
        button.addEventListener('click', () => {
            const productId = button.id.substring(1);
            deleteProduct(business, productId);
        });
    });
});

async function deleteProduct(business, productId) {
    if (!confirm('Are you sure you want to delete this product?')) {
        return;
    }

    const productElement = document.getElementById(`product${productId}`);
    if (!productElement) {
        console.error('Could not find product element');
        return;
    }

    // Add loading state with transition
    productElement.style.transition = 'all 0.3s ease-out';
    productElement.style.opacity = '0.5';
    const buttons = productElement.querySelectorAll('button');
    buttons.forEach(button => button.disabled = true);

    try {
        const response = await api.products.deleteProduct(business, productId);

        if (!response.success) {
            throw new Error(response.error || 'Failed to delete product');
        }

        if (response.success) {
            // Animate the removal
            productElement.style.transform = 'translateX(100%)';
            productElement.style.opacity = '0';
            
            setTimeout(() => {
                productElement.remove();
                
                // Check if this was the last product
                const productsList = document.getElementById('products-list');
                if (productsList && productsList.children.length === 0) {
                    productsList.innerHTML = '<p class="col-span-3 text-center text-gray-500 py-8">No products added yet.</p>';
                }
            }, 300);
        }

    } catch (error) {
        console.error('Error:', error);
        productElement.style.opacity = '1';
        productElement.style.transform = 'translateX(0)';
        buttons.forEach(button => button.disabled = false);
        alert(error.message || 'Error deleting product. Please try again.');
    }
}

async function editProduct(business, productId) {
    const productElement = document.getElementById(`product${productId}`);
    if (!productElement) {
        console.error(`Could not find product element for ID: product${productId}`);
        return;
    }

    try {
        // Fetch the pre-populated form from Django
        const response = await api.products.getEditForm(business, productId);
        
        // Create edit container
        const editDiv = document.createElement('div');
        editDiv.className = 'p-4 bg-white rounded-lg shadow';
        editDiv.innerHTML = response.form_html;
        editDiv.originalProduct = productElement;

        // Replace product with form
        productElement.replaceWith(editDiv);

        // Handle image preview
        const imageInput = editDiv.querySelector('input[type="file"]');
        if (imageInput) {
            imageInput.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        // Find existing preview or create new one
                        let previewDiv = imageInput.closest('.space-y-2').querySelector('.mt-4');
                        if (!previewDiv) {
                            previewDiv = document.createElement('div');
                            previewDiv.className = 'mt-4';
                            imageInput.closest('.space-y-2').appendChild(previewDiv);
                        }
                        
                        previewDiv.innerHTML = `
                            <h4 class="text-sm font-medium text-gray-700 mb-2">Selected Image Preview</h4>
                            <div class="relative">
                                <img src="${e.target.result}" 
                                     alt="Selected image preview" 
                                     class="max-w-full h-auto rounded-lg shadow-sm">
                            </div>
                        `;
                    };
                    reader.readAsDataURL(file);
                }
            });
        }

        // Add cancel button functionality
        editDiv.querySelector('.cancel-edit').addEventListener('click', () => {
            editDiv.replaceWith(productElement);
        });
        // Add form submission handler
        const editForm = editDiv.querySelector(`#editProduct${productId}`);
        editForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            
            try {
                const response = await api.products.updateProduct(business, productId, formData);
                
                if (response.success) {
                    showToast('Product updated successfully!');
                    location.reload();
                }
            } catch (error) {
                console.error('Error updating product:', error);
                showToast('Failed to update product. Please try again.', 'error');
            }
        });

    } catch (error) {
        console.error('Error:', error);
        showToast('Error loading edit form. Please try again.', 'error');
    }
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
