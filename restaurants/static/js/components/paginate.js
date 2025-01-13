document.addEventListener('DOMContentLoaded', function() {
    console.log('paginate.js loaded')
    const businessList = document.getElementById('business-list');  // Change to match your business list container ID
    const pagination = document.getElementById('pagination');

    pagination.addEventListener('click', function(e) {
        if (e.target.classList.contains('page-link')) {
            e.preventDefault();
            const url = new URL(e.target.href);
            const page = url.searchParams.get('page');
            const currentUrl = window.location.pathname;
            const scrollPosition = window.pageYOffset;
            fetchPage(`${currentUrl}?page=${page}`, scrollPosition);
        }
    });

    function fetchPage(url, scrollPosition) {
        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.businesses) { 
                updateBusinessList(data.businesses);
                updatePagination(data);
                window.scrollTo(0, scrollPosition);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    function updateBusinessList(businesses) { 
        businessList.innerHTML = businesses.map(business => `
            <div class="p-4 border rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300">
                <a href="${business.url}" class="block">
                    <h2 class="text-xl font-bold mb-2">${business.name}</h2>
                    <p class="text-gray-600 italic">${business.business_type}</p>
                    <p class="text-gray-600">${business.city}, ${business.state}</p>
                    ${business.cuisines.length > 0 
                        ? `<p class="text-gray-600">${business.cuisines.join(', ')}</p>`
                        : ''
                    }
                    <p class="text-gray-500 italic mt-2">opened ${business.created}</p>
                </a>
            </div>
        `).join('');
    }

    function updatePagination(data) {
        const currentUrl = window.location.pathname;
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