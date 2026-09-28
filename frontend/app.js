// State
let currentUser = null;
let cart = null;
let products = [];
let categories = [];
let selectedProduct = null;

// Initialize App
async function initApp() {
    try {
        // Check if user is logged in
        if (authToken) {
            currentUser = await getCurrentUser();
        }
        updateAuthUI();

        // Load categories and products
        categories = await getCategories();
        products = await getProducts();

        renderCategories();
        renderProducts(products);

        // Load cart
        if (authToken) {
            cart = await getCart();
            updateCartCount();
        }
    } catch (error) {
        console.error('Error initializing app:', error);
        showToast('Failed to load app', 'error');
    }
}

// Authentication
async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorDiv = document.getElementById('login-error');
    errorDiv.textContent = '';

    try {
        const response = await loginUser(email, password);
        authToken = response.access;
        localStorage.setItem('authToken', authToken);
        currentUser = await getCurrentUser();
        updateAuthUI();
        closeAuthModal();
        cart = await getCart();
        updateCartCount();
        showToast('Logged in successfully!', 'success');
    } catch (error) {
        errorDiv.textContent = error.message || 'Login failed';
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const confirm = document.getElementById('register-confirm').value;
    const errorDiv = document.getElementById('register-error');
    errorDiv.textContent = '';

    if (password !== confirm) {
        errorDiv.textContent = 'Passwords do not match';
        return;
    }

    try {
        await registerUser(username, email, password);
        showToast('Account created! Please login.', 'success');
        switchTab('login');
        document.getElementById('login-email').value = email;
    } catch (error) {
        errorDiv.textContent = error.message || 'Registration failed';
    }
}

function logout() {
    authToken = null;
    localStorage.removeItem('authToken');
    currentUser = null;
    cart = null;
    updateAuthUI();
    showToast('Logged out successfully', 'success');
    showPage('home');
}

function updateAuthUI() {
    const authLink = document.getElementById('auth-link');
    if (currentUser) {
        authLink.textContent = 'Logout';
        authLink.onclick = logout;
    } else {
        authLink.textContent = 'Login';
        authLink.onclick = showAuthModal;
    }
}

// Page Navigation
function showPage(pageName) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.style.display = 'none';
    });

    // Show selected page
    const page = document.getElementById(`${pageName}-page`);
    if (page) {
        page.style.display = 'block';
        window.scrollTo(0, 0);
    }
}

// Categories
function renderCategories() {
    const container = document.getElementById('categories-list');
    container.innerHTML = '<button class="category-btn active" onclick="filterByCategory(null)">All Products</button>';

    categories.forEach(category => {
        const btn = document.createElement('button');
        btn.className = 'category-btn';
        btn.textContent = category.name;
        btn.onclick = () => filterByCategory(category.id);
        container.appendChild(btn);
    });
}

async function filterByCategory(categoryId) {
    try {
        // Update active button
        document.querySelectorAll('.category-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.classList.add('active');

        // Load products
        const filtered = categoryId
            ? products.filter(p => p.category === categoryId)
            : products;
        renderProducts(filtered);
    } catch (error) {
        showToast('Error filtering products', 'error');
    }
}

// Products
function renderProducts(productList) {
    const container = document.getElementById('products-list');
    container.innerHTML = '';

    if (productList.length === 0) {
        container.innerHTML = '<p class="empty-cart">No products found</p>';
        return;
    }

    productList.forEach(product => {
        const card = document.createElement('div');
        card.className = 'product-card';
        card.innerHTML = `
            <div class="product-image">
                <img src="https://via.placeholder.com/250x200?text=${encodeURIComponent(product.name)}" alt="${product.name}">
            </div>
            <div class="product-content">
                <div class="product-category">${getCategoryName(product.category)}</div>
                <div class="product-name">${product.name}</div>
                <div class="product-rating">${'★'.repeat(Math.round(product.rating))}${'☆'.repeat(5 - Math.round(product.rating))}</div>
                <div class="product-price">$${parseFloat(product.price).toFixed(2)}</div>
                <div class="product-stock">${product.stock > 0 ? 'In Stock' : 'Out of Stock'}</div>
                <div class="product-actions">
                    <button class="btn btn-primary" ${product.stock === 0 ? 'disabled' : ''} onclick="showProductDetail(${product.id})">View Details</button>
                </div>
            </div>
        `;
        container.appendChild(card);
    });
}

function getCategoryName(categoryId) {
    const category = categories.find(c => c.id === categoryId);
    return category ? category.name : 'Unknown';
}

// Product Detail Modal
function showProductDetail(productId) {
    selectedProduct = products.find(p => p.id === productId);
    if (!selectedProduct) return;

    document.getElementById('modal-product-name').textContent = selectedProduct.name;
    document.getElementById('modal-product-image').src = `https://via.placeholder.com/400x300?text=${encodeURIComponent(selectedProduct.name)}`;
    document.getElementById('modal-product-price').textContent = `$${parseFloat(selectedProduct.price).toFixed(2)}`;
    document.getElementById('modal-product-description').textContent = selectedProduct.description || 'No description available';
    document.getElementById('modal-product-rating').textContent = '★'.repeat(Math.round(selectedProduct.rating)) + '☆'.repeat(5 - Math.round(selectedProduct.rating));
    document.getElementById('modal-review-count').textContent = `(${selectedProduct.review_count} reviews)`;
    document.getElementById('modal-quantity').value = 1;
    document.getElementById('modal-quantity').max = selectedProduct.stock || 10;

    if (selectedProduct.discount_price) {
        document.getElementById('modal-product-discount').textContent = `$${parseFloat(selectedProduct.discount_price).toFixed(2)}`;
    } else {
        document.getElementById('modal-product-discount').textContent = '';
    }

    document.getElementById('product-modal').style.display = 'block';
}

function closeProductModal() {
    document.getElementById('product-modal').style.display = 'none';
}

async function addToCartFromModal() {
    if (!currentUser) {
        showToast('Please login first', 'error');
        showAuthModal();
        return;
    }

    const quantity = parseInt(document.getElementById('modal-quantity').value);
    try {
        await addToCart(selectedProduct.id, quantity);
        cart = await getCart();
        updateCartCount();
        closeProductModal();
        showToast(`${selectedProduct.name} added to cart!`, 'success');
    } catch (error) {
        showToast('Failed to add to cart: ' + error.message, 'error');
    }
}

// Cart
function showCart() {
    if (!currentUser) {
        showToast('Please login to view cart', 'error');
        showAuthModal();
        return;
    }
    showPage('cart');
    renderCart();
}

function renderCart() {
    const container = document.getElementById('cart-items');
    const checkoutBtn = document.getElementById('checkout-btn');

    if (!cart || cart.items.length === 0) {
        container.innerHTML = '<p class="empty-cart">Your cart is empty</p>';
        checkoutBtn.style.display = 'none';
        document.getElementById('subtotal').textContent = '$0.00';
        document.getElementById('tax').textContent = '$0.00';
        document.getElementById('total').textContent = '$0.00';
        return;
    }

    container.innerHTML = '';
    let subtotal = 0;

    cart.items.forEach(item => {
        const product = products.find(p => p.id === item.product);
        if (!product) return;

        const itemTotal = parseFloat(product.price) * item.quantity;
        subtotal += itemTotal;

        const cartItem = document.createElement('div');
        cartItem.className = 'cart-item';
        cartItem.innerHTML = `
            <div class="cart-item-image">📦</div>
            <div class="cart-item-details">
                <h4>${product.name}</h4>
                <p>$${parseFloat(product.price).toFixed(2)} each</p>
            </div>
            <div class="cart-item-quantity">
                <input type="number" min="1" max="${product.stock}" value="${item.quantity}" 
                    onchange="updateCartItem(${item.id}, this.value)">
            </div>
            <div>
                <div class="cart-item-price">$${itemTotal.toFixed(2)}</div>
                <button class="remove-btn" onclick="removeFromCart(${item.id})">Remove</button>
            </div>
        `;
        container.appendChild(cartItem);
    });

    const tax = subtotal * 0.1;
    const shipping = 5.00;
    const total = subtotal + tax + shipping;

    document.getElementById('subtotal').textContent = `$${subtotal.toFixed(2)}`;
    document.getElementById('tax').textContent = `$${tax.toFixed(2)}`;
    document.getElementById('total').textContent = `$${total.toFixed(2)}`;
    checkoutBtn.style.display = 'block';
}

async function updateCartItem(cartItemId, quantity) {
    try {
        quantity = parseInt(quantity);
        if (quantity <= 0) {
            await removeCartItem(cartItemId);
        } else {
            await updateCartItem(cartItemId, quantity);
        }
        cart = await getCart();
        updateCartCount();
        renderCart();
    } catch (error) {
        showToast('Error updating cart: ' + error.message, 'error');
    }
}

async function removeFromCart(cartItemId) {
    try {
        await removeCartItem(cartItemId);
        cart = await getCart();
        updateCartCount();
        renderCart();
        showToast('Item removed from cart', 'success');
    } catch (error) {
        showToast('Error removing item: ' + error.message, 'error');
    }
}

function updateCartCount() {
    const count = cart ? cart.items.reduce((sum, item) => sum + item.quantity, 0) : 0;
    document.getElementById('cart-count').textContent = count;
}

// Checkout
function goToCheckout() {
    if (!cart || cart.items.length === 0) {
        showToast('Cart is empty', 'error');
        return;
    }
    showPage('checkout');
    renderCheckout();
}

function renderCheckout() {
    const container = document.getElementById('checkout-items');
    container.innerHTML = '';
    let subtotal = 0;

    cart.items.forEach(item => {
        const product = products.find(p => p.id === item.product);
        if (!product) return;

        const itemTotal = parseFloat(product.price) * item.quantity;
        subtotal += itemTotal;

        const checkoutItem = document.createElement('div');
        checkoutItem.className = 'checkout-item';
        checkoutItem.innerHTML = `
            <span>${product.name} x ${item.quantity}</span>
            <span>$${itemTotal.toFixed(2)}</span>
        `;
        container.appendChild(checkoutItem);
    });

    const tax = subtotal * 0.1;
    const shipping = 5.00;
    const total = subtotal + tax + shipping;

    document.getElementById('checkout-subtotal').textContent = `$${subtotal.toFixed(2)}`;
    document.getElementById('checkout-tax').textContent = `$${tax.toFixed(2)}`;
    document.getElementById('checkout-total').textContent = `$${total.toFixed(2)}`;
}

async function processPayment() {
    const fullName = document.getElementById('full-name').value;
    const address = document.getElementById('address').value;
    const city = document.getElementById('city').value;
    const state = document.getElementById('state').value;
    const zipCode = document.getElementById('zip-code').value;

    if (!fullName || !address || !city || !state || !zipCode) {
        showToast('Please fill all fields', 'error');
        return;
    }

    const shippingAddress = `${fullName}, ${address}, ${city}, ${state} ${zipCode}`;

    try {
        // Create order
        const order = await createOrder(shippingAddress);
        const subtotal = cart.items.reduce((sum, item) => {
            const product = products.find(p => p.id === item.product);
            return sum + (parseFloat(product.price) * item.quantity);
        }, 0);
        const total = subtotal * 1.1 + 5.00;

        // Create payment
        const payment = await createPayment(order.id, total);

        // Clear cart
        await clearCart();
        cart = null;
        updateCartCount();

        // Show success page
        document.getElementById('order-number').textContent = `Order #${order.order_number}`;
        const detailsDiv = document.getElementById('order-details');
        detailsDiv.innerHTML = `
            <div class="order-detail-row">
                <span>Order Total:</span>
                <span>$${total.toFixed(2)}</span>
            </div>
            <div class="order-detail-row">
                <span>Status:</span>
                <span>${order.status}</span>
            </div>
            <div class="order-detail-row">
                <span>Shipping Address:</span>
                <span>${shippingAddress}</span>
            </div>
        `;

        showPage('payment-success');
        showToast('Payment processed successfully!', 'success');
    } catch (error) {
        showToast('Payment failed: ' + error.message, 'error');
    }
}

function goHome() {
    showPage('home');
}

// Auth Modal
function showAuthModal() {
    document.getElementById('auth-modal').style.display = 'block';
}

function closeAuthModal() {
    document.getElementById('auth-modal').style.display = 'none';
    document.getElementById('login-error').textContent = '';
    document.getElementById('register-error').textContent = '';
    document.getElementById('login-form').reset();
    document.getElementById('register-form').reset();
}

function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    document.getElementById(`${tabName}-tab`).classList.add('active');
    event.target.classList.add('active');
}

// Toast Notifications
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = 'toast show';
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Close modal when clicking outside
window.onclick = function(event) {
    const authModal = document.getElementById('auth-modal');
    const productModal = document.getElementById('product-modal');

    if (event.target == authModal) {
        closeAuthModal();
    }
    if (event.target == productModal) {
        closeProductModal();
    }
};

// Initialize app on load
window.addEventListener('load', initApp);
