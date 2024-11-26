document.addEventListener('DOMContentLoaded', function() {
    const kitchenList = document.getElementById('kitchen-list');
    const pagination = document.getElementById('pagination');

    pagination.addEventListener('click', function(e) {
        if (e.target.classList.contains('page-link')) {
            e.preventDefault();
            const url = e.target.href;
            const scrollPosition = window.pageYOffset;
            fetchPage(url, scrollPosition);
        }
    });

    function fetchPage(url, scrollPosition) {
        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            updateKitchenList(data.kitchens);
            updatePagination(data);
            window.scrollTo(0, scrollPosition);
        })
        .catch(error => console.error('Error:', error));
    }

    function updateKitchenList(kitchens) {
        kitchenList.innerHTML = kitchens.map(kitchen => `
            <div class="p-4 border rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300">
                <a href="${kitchen.url}" class="block">
                    <h2 class="text-xl font-bold mb-2">${kitchen.name}</h2>
                    <p class="text-gray-600">${kitchen.city}, ${kitchen.state}</p>
                    <p class="text-gray-600">${kitchen.cuisine} cuisine</p>
                    <p class="text-gray-500 italic mt-2">opened ${kitchen.created}</p>
                </a>
            </div>
        `).join('');
    }

    function updatePagination(data) {
        let paginationHTML = '';
        if (data.has_previous) {
            paginationHTML += `
                <a href="?page=1" class="page-link px-3 py-2 bg-gray-200 text-gray-700 rounded-l-md">&laquo; first</a>
                <a href="?page=${data.current_page - 1}" class="page-link px-3 py-2 bg-gray-200 text-gray-700">previous</a>
            `;
        }
        paginationHTML += `
            <span class="px-3 py-2 bg-gray-300 text-gray-700">
                Page ${data.current_page} of ${data.num_pages}
            </span>
        `;
        if (data.has_next) {
            paginationHTML += `
                <a href="?page=${data.current_page + 1}" class="page-link px-3 py-2 bg-gray-200 text-gray-700">next</a>
                <a href="?page=${data.num_pages}" class="page-link px-3 py-2 bg-gray-200 text-gray-700 rounded-r-md">last &raquo;</a>
            `;
        }
        pagination.innerHTML = paginationHTML;
    }
});