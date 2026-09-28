// API Configuration
const API_BASE_URL = 'http://localhost:8000/api';
let authToken = localStorage.getItem('authToken') || null;

// Helper function for API calls
async function apiCall(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }

    const response = await fetch(url, {
        ...options,
        headers,
    });

    if (!response.ok) {
        if (response.status === 401) {
            authToken = null;
            localStorage.removeItem('authToken');
            updateAuthUI();
        }
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail || error.message || 'API Error');
    }

    return await response.json();
}

// Auth APIs
function loginUser(email, password) {
    return apiCall('/token/', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
    });
}

function registerUser(username, email, password) {
    return apiCall('/auth/register/', {
        method: 'POST',
        body: JSON.stringify({ username, email, password }),
    });
}

function getCurrentUser() {
    if (!authToken) return Promise.resolve(null);
    return apiCall('/auth/me/').catch(() => null);
}

// Product APIs
function getProducts(categoryId = null) {
    let endpoint = '/products/';
    if (categoryId) {
        endpoint += `?category=${categoryId}`;
    }
    return apiCall(endpoint);
}

function getProduct(productId) {
    return apiCall(`/products/${productId}/`);
}

function getCategories() {
    return apiCall('/categories/');
}

// Cart APIs
function getCart() {
    if (!authToken) return Promise.resolve(null);
    return apiCall('/cart/').catch(() => null);
}

function addToCart(productId, quantity) {
    return apiCall('/cart/add/', {
        method: 'POST',
        body: JSON.stringify({ product_id: productId, quantity }),
    });
}

function updateCartItem(cartItemId, quantity) {
    return apiCall(`/cart/items/${cartItemId}/`, {
        method: 'PATCH',
        body: JSON.stringify({ quantity }),
    });
}

function removeCartItem(cartItemId) {
    return apiCall(`/cart/items/${cartItemId}/`, {
        method: 'DELETE',
    });
}

function clearCart() {
    return apiCall('/cart/clear/', {
        method: 'POST',
    });
}

// Order APIs
function createOrder(shippingAddress, notes = '') {
    return apiCall('/orders/', {
        method: 'POST',
        body: JSON.stringify({ shipping_address: shippingAddress, notes }),
    });
}

function getOrders() {
    if (!authToken) return Promise.resolve([]);
    return apiCall('/orders/').catch(() => []);
}

function getOrder(orderId) {
    return apiCall(`/orders/${orderId}/`);
}

// Payment APIs
function createPayment(orderId, amount) {
    return apiCall('/payments/', {
        method: 'POST',
        body: JSON.stringify({ order_id: orderId, amount }),
    });
}

function getPayment(paymentId) {
    return apiCall(`/payments/${paymentId}/`);
}

// Review APIs
function createReview(productId, rating, comment = '') {
    return apiCall(`/products/${productId}/reviews/`, {
        method: 'POST',
        body: JSON.stringify({ rating, comment }),
    });
}
