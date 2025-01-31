document.addEventListener('DOMContentLoaded', function() {
    fetch('{% url "get_product_templates" business_details.subdirectory %}')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('templateSelect');
            data.templates.forEach(template => {
                const option = document.createElement('option');
                option.value = template.id;
                option.textContent = `${template.name} - ${template.type}`;
                select.appendChild(option);
            });
        })
        .catch(error => console.error('Error loading templates:', error));
});

function openProductModal() {
    document.getElementById('productModal').classList.remove('hidden');
}

function closeProductModal() {
    document.getElementById('productModal').classList.add('hidden');
}

function editProduct(productId) {
    // Implement edit functionality
    console.log('Editing product:', productId);
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('productModal');
    if (event.target == modal) {
        closeProductModal();
    }
}