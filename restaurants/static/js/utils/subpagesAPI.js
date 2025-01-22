export async function makeRequest(url, method, data) {
    try {
        const headers = {
            ...(!(data instanceof FormData) && { 'Content-Type': 'application/json' })
        };

        const response = await fetch(url, {
            method,
            headers,
            credentials: 'same-origin', // Important for CSRF
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
    }
};