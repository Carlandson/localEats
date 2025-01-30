export function createHeroImageHTML(imageUrl, prefix, layout = 'banner-slider') {
    const isDisabled = prefix !== 'hero-image' && layout !== 'banner-slider';
    return `
        <div class="relative group">
            <img src="${imageUrl}" 
                 alt="${prefix} image" 
                 class="w-full h-40 object-cover rounded-lg cursor-pointer"
                 id="${prefix}-preview">
            <button type="button"
                    id="remove-${prefix}"
                    class="absolute top-2 right-2 p-2 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors"
                    title="Remove image"
                    ${isDisabled ? 'disabled' : ''}>
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
            </button>
        </div>
    `;
}

export function createUploadPlaceholderHTML(prefix) {
    const displayText = prefix === 'hero-image' ? 
        'Add Primary Image' : 
        `Add ${prefix.replace('-', ' ').replace(/^\w/, c => c.toUpperCase())}`;
    
    return `
        <div class="relative group cursor-pointer" id="${prefix}-placeholder">
            <button type="button" id="upload-${prefix}-button" class="w-full">
                <div class="w-full h-40 bg-gray-100 rounded-lg flex items-center justify-center border-2 border-dashed border-gray-300 hover:border-gray-400">
                    <div class="text-center">
                        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                        </svg>
                        <span class="mt-2 block text-sm font-medium text-gray-600">
                            ${displayText}
                        </span>
                    </div>
                </div>
            </button>
            <input type="file" 
                   id="${prefix}-upload" 
                   accept="image/*" 
                   class="hidden">
        </div>
    `;
}

export function createProductFormHTML(product, productId) {
    return `
        <div id="edit-form-${productId}" class="border rounded-lg p-4 bg-white shadow-sm">
            <form id="editProduct${productId}" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700">Name</label>
                    <input type="text" name="name" value="${product.name}"
                           class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500">
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700">Description</label>
                    <textarea name="description" rows="3"
                             class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500"
                    >${product.description}</textarea>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700">Price</label>
                    <input type="number" name="price" value="${product.price}" step="0.01"
                           class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500">
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Product Image</label>
                    <div id="product-image-container">
                        ${product.image_url ? 
                            createHeroImageHTML(product.image_url, 'product-image') :
                            createUploadPlaceholderHTML('product-image')}
                    </div>
                    <input type="file" 
                           name="image" 
                           id="product-image-upload"
                           accept="image/*"
                           class="hidden">
                </div>
                
                <div class="flex justify-end space-x-2">
                    <button type="button" class="cancel-edit px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded transition-colors duration-200">
                        Cancel
                    </button>
                    <button type="submit" class="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded transition-colors duration-200">
                        Save Changes
                    </button>
                </div>
            </form>
        </div>
    `;
}

export function createServiceFormHTML(service, serviceId) {
    return `
        <div id="edit-form-${serviceId}" class="border rounded-lg p-4 bg-white shadow-sm">
            <form id="editService${serviceId}" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700">Name</label>
                    <input type="text" name="name" value="${service.name}"
                           class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500">
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700">Description</label>
                    <textarea name="description" rows="3"
                             class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500"
                    >${service.description}</textarea>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Service Image</label>
                    <div id="service-image-container">
                        ${service.image_url ? 
                            createHeroImageHTML(service.image_url, 'service-image') :
                            createUploadPlaceholderHTML('service-image')}
                    </div>
                    <input type="file" 
                           name="image" 
                           id="service-image-upload"
                           accept="image/*"
                           class="hidden">
                </div>
                
                <div class="flex justify-end space-x-2">
                    <button type="button" class="cancel-edit px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded transition-colors duration-200">
                        Cancel
                    </button>
                    <button type="submit" class="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded transition-colors duration-200">
                        Save Changes
                    </button>
                </div>
            </form>
        </div>
    `;
}