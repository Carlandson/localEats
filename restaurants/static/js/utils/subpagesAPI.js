function getCsrfToken() {
    return JSON.parse(document.getElementById('csrf_token').textContent);
}

export async function makeRequest(url, method, data) {
    console.log('Making request:', url, method, data);
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
            let errorMessage = 'Server error';
            
            // Handle form.errors dict format
            if (errorData.error && typeof errorData.error === 'object') {
                const errors = [];
                for (const [field, messages] of Object.entries(errorData.error)) {
                    if (Array.isArray(messages)) {
                        errors.push(`${field}: ${messages.join(', ')}`);
                    } else {
                        errors.push(`${field}: ${messages}`);
                    }
                }
                errorMessage = errors.join('; ');
            } 
            // Handle string error or message
            else if (errorData.error) {
                errorMessage = errorData.error;
            } 
            else if (errorData.message) {
                errorMessage = errorData.message;
            }
            
            throw new Error(errorMessage);
        }

        return await response.json();
    } catch (error) {
        console.error('Request failed:', error);
        throw error;
    }
}

export const api = {
    // About Us page settings
    aboutUs: {
        updateSettings: async (business, data) => {
            return makeRequest(`/${business}/about/settings/`, 'POST', data);
        },
        toggleSection: async (business, data) => {
            return makeRequest(`/${business}/about/settings/`, 'POST', {
                fieldType: 'boolean',
                page_type: 'about',
                ...data
            });
        }
    },
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
            return makeRequest(`/${business}/events/add/`, 'POST', formData);
        },
        update: async (business, eventId, formData) => {
            return makeRequest(`/${business}/events/edit/${eventId}/`, 'POST', formData);
        },
        delete: async (business, eventId) => {
            return makeRequest(`/${business}/events/delete/${eventId}/`, 'DELETE');
        },
        getEditForm: async (business, eventId) => {
            return makeRequest(`/${business}/events/get-form/${eventId}/`, 'GET');
        },
    },
    
    // contact page
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
    },
    services: {
        updateSettings: async (business, data) => {
            return makeRequest(`/${business}/services/settings/`, 'POST', data);
        },

        createService: async (business, formData) => {
            return makeRequest(`/${business}/services/create/`, 'POST', formData);
        },

        getService: async (business, serviceId) => {
            return makeRequest(`/${business}/services/${serviceId}/`, 'GET');
        },

        updateService: async (business, serviceId, formData) => {
            return makeRequest(`/${business}/services/${serviceId}/`, 'POST', formData);
        },

        deleteService: async (business, serviceId) => {
            return makeRequest(`/${business}/services/${serviceId}/`, 'DELETE');
        },
        getEditForm: async (business, serviceId) => {
            return makeRequest(`/${business}/services/${serviceId}/get-form/`, 'GET');
        },
    },
    gallery: {
        upload: async (business, formData) => {
            return makeRequest(`/${business}/gallery/upload/`, 'POST', formData);
        },
        updateDescription: async (business, data) => {
            return makeRequest(`/${business}/gallery/settings/`, 'POST', data);
        },

        delete: async (business, imageId) => {
            return makeRequest(`/${business}/gallery/delete/${imageId}`, 'DELETE');
        }

    }
};