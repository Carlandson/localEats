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