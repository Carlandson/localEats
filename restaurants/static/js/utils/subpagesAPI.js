function getCsrfToken() {
    return JSON.parse(document.getElementById('csrf_token').textContent);
}

export async function makeRequest(url, method, data) {
    try {
        const headers = {
            'X-CSRFToken': getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest',
            ...(!(data instanceof FormData) && { 'Content-Type': 'application/json' })
        };

        const response = await fetch(url, {
            method,
            headers,
            credentials: 'same-origin',
            body: data instanceof FormData ? data : JSON.stringify(data)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Server error');
        }

        return await response.json();
    } catch (error) {
        console.error('Request failed:', error);
        throw error;
    }
}

export const api = {
    // Home page settings
    home: {
        updateSettings: async (business, data) => {
            return makeRequest(`/${business}/home/settings/`, 'POST', data);
        },
        toggleSection: async (business, data) => {
            return makeRequest(`/${business}/home/settings/`, 'POST', {
                fieldType: 'boolean',
                page_type: 'home',
                ...data
            });
        }
    },

    // News posts
    news: {
        create: async (business, formData) => {
            return makeRequest(`/api/${business}/news-post/`, 'POST', formData);
        },
        delete: async (business, postId) => {
            return makeRequest(`/api/${business}/news-post/${postId}/`, 'DELETE');
        }
    },

    // Events
    events: {
        create: async (business, formData) => {
            return makeRequest(`/api/${business}/events/`, 'POST', formData);
        }
    },
    contact: {
        updateSettings: async (business, data) => {
            return makeRequest(`/${business}/contact/settings/`, 'POST', data);
        },
        toggleSection: async (business, data) => {
            return makeRequest(`/${business}/contact/settings/`, 'POST', {
                fieldType: 'boolean',
                page_type: 'contact',
                ...data
            });
        }
    },
    editBusiness: {
        updateField: async (business, fieldName, value) => {
            const formData = new FormData();
            formData.append('field_name', fieldName);
            formData.append(fieldName, value);
            
            return makeRequest(`/${business}/edit-business/update/`, 'POST', formData);
        }
    },
    products: {
        updateSettings: async (business, data) => {
            return makeRequest(`/${business}/products/settings/`, 'POST', data);
        },

        createProduct: async (business, formData) => {
            return makeRequest(`/${business}/products/create/`, 'POST', formData);
        },

        getProduct: async (business, productId) => {
            return makeRequest(`/${business}/products/${productId}/`, 'GET');
        },

        updateProduct: async (business, productId, formData) => {
            return makeRequest(`/${business}/products/${productId}/`, 'POST', formData);
        },

        deleteProduct: async (business, productId) => {
            return makeRequest(`/${business}/products/${productId}/`, 'DELETE');
        },
        getEditForm: async (business, productId) => {
            return makeRequest(`/${business}/products/${productId}/get-form/`, 'GET');
        },
    }
};