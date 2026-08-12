/* ==========================================
   BELLA GLOW - CARRINHO DE COMPRAS
   Persistência em localStorage
   ========================================== */

const STORAGE_KEYS = {
    CART: '@bellaglow/cart',
    WISHLIST: '@bellaglow/wishlist',
    THEME: '@bellaglow/theme',
    COOKIES: '@bellaglow/cookies'
};

const Cart = {
    // Obter carrinho do localStorage
    getItems() {
        try {
            return JSON.parse(localStorage.getItem(STORAGE_KEYS.CART)) || [];
        } catch {
            return [];
        }
    },

    // Salvar carrinho
    saveItems(items) {
        localStorage.setItem(STORAGE_KEYS.CART, JSON.stringify(items));
        this.updateBadge();
        this.updateCartUI();
    },

    // Adicionar produto ao carrinho
    addToCart(productId, { size = null, color = null, quantity = 1 } = {}) {
        const items = this.getItems();
        const existingIndex = items.findIndex(item =>
            item.id === productId &&
            item.size === size &&
            item.color === color
        );

        if (existingIndex !== -1) {
            items[existingIndex].quantity += quantity;
        } else {
            const product = PRODUCTS.find(p => p.id === productId);
            if (!product) return;
            items.push({
                id: productId,
                name: product.name,
                brand: product.brand,
                price: product.price,
                image: product.images[0],
                size: size,
                color: color,
                quantity: quantity
            });
        }

        this.saveItems(items);
        this.showToast(`${quantity}x ${product ? product.name : 'produto'} adicionado!`, 'success');
    },

    // Remover item
    removeFromCart(productId, size, color) {
        let items = this.getItems();
        items = items.filter(item =>
            !(item.id === productId && item.size === size && item.color === color)
        );
        this.saveItems(items);
        this.showToast('Item removido do carrinho', 'info');
    },

    // Atualizar quantidade
    updateQuantity(productId, size, color, newQuantity) {
        const items = this.getItems();
        const item = items.find(i => i.id === productId && i.size === size && i.color === color);
        if (item) {
            if (newQuantity <= 0) {
                this.removeFromCart(productId, size, color);
            } else {
                item.quantity = newQuantity;
                this.saveItems(items);
            }
        }
    },

    // Limpar carrinho
    clear() {
        this.saveItems([]);
    },

    // Obter total de itens
    getTotalItems() {
        const items = this.getItems();
        return items.reduce((sum, item) => sum + item.quantity, 0);
    },

    // Obter subtotal
    getSubtotal() {
        const items = this.getItems();
        return items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    },

    // Calcular frete (simulação)
    getShipping(subtotal) {
        return subtotal > 30000 ? 0 : 1500; // grátis acima de R$ 300
    },

    // Atualizar badge do carrinho
    updateBadge() {
        const badge = document.getElementById('cartCount');
        const total = this.getTotalItems();
        if (badge) {
            badge.textContent = total;
            badge.classList.toggle('show', total > 0);
        }
    },

    // Atualizar UI do carrinho (off-canvas)
    updateCartUI() {
        const cartItems = document.getElementById('cartItems');
        const cartSummary = document.getElementById('cartSummary');
        const subtotalEl = document.getElementById('cartSubtotal');
        const shippingEl = document.getElementById('cartShipping');
        const totalEl = document.getElementById('cartTotal');

        const items = this.getItems();

        if (items.length === 0) {
            if (cartItems) cartItems.innerHTML = `
                <div class="cart-empty">
                    <i class="fas fa-shopping-bag"></i>
                    <p>Seu carrinho está vazio</p>
                    <small>Adicione produtos para continuar</small>
                </div>
            `;
            if (cartSummary) cartSummary.style.display = 'none';
            return;
        }

        // Renderizar itens
        if (cartItems) {
            cartItems.innerHTML = items.map((item, index) => `
                <div class="cart-item" data-index="${index}">
                    <div class="cart-item-image">
                        <img src="${item.image}" alt="${item.name}">
                    </div>
                    <div class="cart-item-info">
                        <span class="cart-item-brand">${item.brand}</span>
                        <h4 class="cart-item-name">${item.name}</h4>
                        ${item.size ? `<span class="cart-item-variant">Tamanho: ${item.size}</span>` : ''}
                        ${item.color ? `<span class="cart-item-variant">Cor: ${item.color}</span>` : ''}
                        <div class="cart-item-price">${formatPrice(item.price)}</div>
                        <div class="cart-item-qty">
                            <button class="qty-btn" data-action="decrease" data-id="${item.id}" data-size="${item.size || ''}" data-color="${item.color || ''}">−</button>
                            <span>${item.quantity}</span>
                            <button class="qty-btn" data-action="increase" data-id="${item.id}" data-size="${item.size || ''}" data-color="${item.color || ''}">+</button>
                        </div>
                    </div>
                    <button class="cart-item-remove" data-id="${item.id}" data-size="${item.size || ''}" data-color="${item.color || ''}">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `).join('');

            // Event listeners para quantidade e remoção
            cartItems.querySelectorAll('.qty-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const action = btn.dataset.action;
                    const id = parseInt(btn.dataset.id);
                    const size = btn.dataset.size || null;
                    const color = btn.dataset.color || null;
                    const item = this.getItems().find(i => i.id === id && i.size === size && i.color === color);
                    if (!item) return;
                    if (action === 'increase') {
                        this.updateQuantity(id, size, color, item.quantity + 1);
                    } else if (action === 'decrease') {
                        this.updateQuantity(id, size, color, item.quantity - 1);
                    }
                });
            });

            cartItems.querySelectorAll('.cart-item-remove').forEach(btn => {
                btn.addEventListener('click', () => {
                    const id = parseInt(btn.dataset.id);
                    const size = btn.dataset.size || null;
                    const color = btn.dataset.color || null;
                    this.removeFromCart(id, size, color);
                });
            });
        }

        // Atualizar resumo
        if (cartSummary) cartSummary.style.display = 'block';
        const subtotal = this.getSubtotal();
        const shipping = this.getShipping(subtotal);
        const total = subtotal + shipping;

        if (subtotalEl) subtotalEl.textContent = formatPrice(subtotal);
        if (shippingEl) {
            if (shipping === 0) {
                shippingEl.textContent = 'GRÁTIS';
                shippingEl.className = 'free';
            } else {
                shippingEl.textContent = formatPrice(shipping);
                shippingEl.className = '';
            }
        }
        if (totalEl) totalEl.textContent = formatPrice(total);
    },

    // Toast
    showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        const msgEl = document.getElementById('toastMessage');
        if (!toast || !msgEl) return;

        msgEl.textContent = message;
        toast.className = 'toast ' + type;

        // Forçar reflow para reiniciar animação
        void toast.offsetWidth;
        toast.classList.add('active');

        clearTimeout(toast._timeout);
        toast._timeout = setTimeout(() => {
            toast.classList.remove('active');
        }, 4000);
    },

    // Inicializar listeners do carrinho
    init() {
        // Abrir carrinho
        document.getElementById('cartBtn')?.addEventListener('click', () => {
            this.updateCartUI();
            document.getElementById('cartSidebar')?.classList.add('active');
            document.getElementById('cartOverlay')?.classList.add('active');
            document.body.style.overflow = 'hidden';
        });

        // Fechar carrinho
        const closeCart = () => {
            document.getElementById('cartSidebar')?.classList.remove('active');
            document.getElementById('cartOverlay')?.classList.remove('active');
            document.body.style.overflow = '';
        };
        document.getElementById('cartClose')?.addEventListener('click', closeCart);
        document.getElementById('cartOverlay')?.addEventListener('click', closeCart);
        document.getElementById('continueShoppingBtn')?.addEventListener('click', closeCart);

        // Checkout
        document.getElementById('checkoutBtn')?.addEventListener('click', () => {
            if (typeof startCheckout === 'function') {
                startCheckout();
            } else {
                this.showToast('Função de checkout não implementada', 'error');
            }
        });

        // Atualizar badge ao carregar
        this.updateBadge();
        this.updateCartUI();
    }
};

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => Cart.init());