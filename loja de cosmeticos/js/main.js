/* ==========================================
   BELLA GLOW - MAIN JS
   Renderização, Scroll Reveal, Quick View, Checkout
   ========================================== */

// Estado global de filtros
const state = {
    filteredProducts: [],
    activeCategory: null,
    activeSize: null,
    activeColor: null,
    activePrice: null,
    sortBy: 'relevance'
};

// ==========================================
// RENDERIZAÇÃO DE PRODUTOS
// ==========================================

function renderStars(rating) {
    const full = Math.floor(rating);
    const half = rating - full >= 0.5 ? 1 : 0;
    const empty = 5 - full - half;
    return '★'.repeat(full) + (half ? '½' : '') + '☆'.repeat(empty);
}

function renderProductCard(product, index) {
    const isWishlist = Wishlist.isWishlisted(product.id);
    return `
        <div class="product-card" data-id="${product.id}" data-index="${index}">
            <div class="product-image">
                <img class="img-primary" src="${product.images[0]}" alt="${product.name}" loading="lazy">
                ${product.images[1] ? `<img class="img-secondary" src="${product.images[1]}" alt="${product.name}" loading="lazy">` : ''}
                <div class="product-badges">
                    ${product.isNew ? '<span class="product-badge badge-new">Novo</span>' : ''}
                    ${product.isSale && product.oldPrice ? '<span class="product-badge badge-sale">Sale</span>' : ''}
                    ${product.inStock && product.stock < 3 ? '<span class="product-badge badge-low">Últimas unidades</span>' : ''}
                </div>
                <button class="product-wishlist ${isWishlist ? 'active' : ''}" data-id="${product.id}" aria-label="Favoritar">
                    <i class="fas fa-heart"></i>
                </button>
                <button class="product-quick-view" data-id="${product.id}">Visualização Rápida</button>
                ${!product.inStock ? '<div class="product-out-overlay">Esgotado</div>' : ''}
            </div>
            <div class="product-info">
                <span class="product-brand">${product.brand}</span>
                <h3 class="product-name">${product.name}</h3>
                <div class="product-rating">
                    <span class="product-stars">${renderStars(product.rating)}</span>
                    <span>(${product.reviewsCount})</span>
                </div>
                <div class="product-prices">
                    <div class="product-price">
                        ${product.oldPrice ? `<span class="price-old">${formatPrice(product.oldPrice)}</span>` : ''}
                        <span class="price-current">${formatPrice(product.price)}</span>
                    </div>
                    ${product.inStock ? `<div class="product-installments">${calculateInstallments(product.price).formatted}</div>` : ''}
                </div>
                <div class="product-actions">
                    <button class="add-to-cart-btn" data-id="${product.id}" ${!product.inStock ? 'disabled' : ''}>
                        ${product.inStock ? 'Adicionar ao Carrinho' : 'Indisponível'}
                    </button>
                </div>
            </div>
        </div>
    `;
}

function attachProductEvents(container) {
    // Wishlist
    container.querySelectorAll('.product-wishlist').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = parseInt(btn.dataset.id);
            Wishlist.toggle(id);
            btn.classList.toggle('active');
        });
    });

    // Quick View
    container.querySelectorAll('.product-quick-view').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = parseInt(btn.dataset.id);
            if (typeof openQuickView === 'function') {
                openQuickView(id);
            }
        });
    });

    // Add to Cart
    container.querySelectorAll('.add-to-cart-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = parseInt(btn.dataset.id);
            Cart.addToCart(id);
            // Animar ícone do carrinho
            const cartBtn = document.getElementById('cartBtn');
            if (cartBtn) {
                cartBtn.classList.add('shake');
                setTimeout(() => cartBtn.classList.remove('shake'), 500);
            }
        });
    });

    // Clique no card para abrir quick view (opcional)
    container.querySelectorAll('.product-card').forEach(card => {
        card.addEventListener('click', () => {
            const id = parseInt(card.dataset.id);
            if (typeof openQuickView === 'function') {
                openQuickView(id);
            }
        });
    });
}

// ==========================================
// CATEGORIAS
// ==========================================

function renderCategories() {
    const grid = document.getElementById('categoriesGrid');
    if (!grid) return;

    grid.innerHTML = CATEGORIES.map(cat => `
        <a href="#" class="category-card" data-category="${cat.id}" style="background-image: url('${cat.image}');">
            <div class="category-overlay">
                <span class="category-name">${cat.name}</span>
                <span class="category-count">${cat.count} produtos</span>
                <span class="category-cta">Explorar</span>
            </div>
        </a>
    `).join('');

    // Filtrar ao clicar na categoria
    grid.querySelectorAll('.category-card').forEach(card => {
        card.addEventListener('click', (e) => {
            e.preventDefault();
            const category = card.dataset.category;
            state.activeCategory = category;
            filterAndRender();
            document.getElementById('loja')?.scrollIntoView({ behavior: 'smooth' });
            // Atualizar filtros na loja
            document.querySelectorAll('#categoryFilters .filter-checkbox input').forEach(input => {
                input.checked = (input.dataset.category === category);
            });
        });
    });
}

// ==========================================
// FILTROS E LOJA
// ==========================================

function renderFilters() {
    const container = document.getElementById('categoryFilters');
    if (!container) return;

    container.innerHTML = CATEGORIES.map(cat => `
        <label class="filter-checkbox">
            <input type="checkbox" data-category="${cat.id}" ${state.activeCategory === cat.id ? 'checked' : ''}>
            ${cat.name}
            <span class="count">(${cat.count})</span>
        </label>
    `).join('');

    // Eventos
    container.querySelectorAll('input[type="checkbox"]').forEach(input => {
        input.addEventListener('change', () => {
            if (input.checked) {
                state.activeCategory = input.dataset.category;
            } else {
                state.activeCategory = null;
            }
            filterAndRender();
        });
    });

    // Tamanhos
    document.querySelectorAll('#sizeFilters .size-option').forEach(btn => {
        btn.addEventListener('click', () => {
            const isActive = btn.classList.contains('active');
            document.querySelectorAll('#sizeFilters .size-option').forEach(b => b.classList.remove('active'));
            if (!isActive) {
                btn.classList.add('active');
                state.activeSize = btn.dataset.size;
            } else {
                state.activeSize = null;
            }
            filterAndRender();
        });
    });

    // Cores
    document.querySelectorAll('#colorFilters .color-option').forEach(btn => {
        btn.addEventListener('click', () => {
            const isActive = btn.classList.contains('active');
            document.querySelectorAll('#colorFilters .color-option').forEach(b => b.classList.remove('active'));
            if (!isActive) {
                btn.classList.add('active');
                state.activeColor = btn.dataset.color;
            } else {
                state.activeColor = null;
            }
            filterAndRender();
        });
    });

    // Preço
    document.querySelectorAll('input[name="price"]').forEach(input => {
        input.addEventListener('change', () => {
            if (input.checked) {
                state.activePrice = {
                    min: parseInt(input.dataset.min),
                    max: parseInt(input.dataset.max)
                };
            } else {
                state.activePrice = null;
            }
            filterAndRender();
        });
    });

    // Toggle mobile filters
    const filterToggle = document.getElementById('filterToggle');
    const sidebar = document.getElementById('shopSidebar');
    filterToggle?.addEventListener('click', () => {
        sidebar.classList.toggle('active');
    });
}

// ==========================================
// ORDENAÇÃO
// ==========================================

function initSort() {
    const sortSelect = document.getElementById('sortSelect');
    if (!sortSelect) return;

    sortSelect.addEventListener('change', () => {
        state.sortBy = sortSelect.value;
        filterAndRender();
    });
}

// ==========================================
// APLICAR FILTROS E RENDERIZAR
// ==========================================

function filterAndRender() {
    let products = [...PRODUCTS];

    // Filtrar por categoria
    if (state.activeCategory) {
        products = products.filter(p => p.category === state.activeCategory);
    }

    // Filtrar por preço
    if (state.activePrice) {
        products = products.filter(p =>
            p.price >= state.activePrice.min && p.price <= state.activePrice.max
        );
    }

    // Filtrar por cor
    if (state.activeColor) {
        products = products.filter(p =>
            p.colors && p.colors.some(c => c.hex.toLowerCase() === state.activeColor.toLowerCase())
        );
    }

    // Ordenar
    products = sortProducts(products, state.sortBy);

    state.filteredProducts = products;
    const grid = document.getElementById('shopGrid');
    if (!grid) return;

    // Fade out
    grid.style.opacity = '0';
    grid.style.transition = 'opacity 0.2s';

    setTimeout(() => {
        if (products.length === 0) {
            grid.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 4rem 1rem; color: var(--color-text-light);">
                    <i class="fas fa-search" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.3;"></i>
                    <p style="font-family: var(--font-display); font-size: 1.3rem; color: var(--color-text);">Nenhum produto encontrado</p>
                    <p>Tente ajustar os filtros para ver mais resultados.</p>
                </div>
            `;
        } else {
            grid.innerHTML = products.map((p, i) => renderProductCard(p, i)).join('');
            attachProductEvents(grid);
            Wishlist.updateButtons();
        }

        // Atualizar contador
        const countEl = document.getElementById('shopCount');
        if (countEl) countEl.textContent = `${products.length} ${products.length === 1 ? 'produto' : 'produtos'}`;

        // Fade in
        grid.style.opacity = '1';

        // Reveal animations
        initScrollReveal();
    }, 200);
}

function sortProducts(products, sortBy) {
    switch (sortBy) {
        case 'price-asc':
            return products.sort((a, b) => a.price - b.price);
        case 'price-desc':
            return products.sort((a, b) => b.price - a.price);
        case 'newest':
            return products.sort((a, b) => (b.isNew ? 1 : 0) - (a.isNew ? 1 : 0));
        case 'relevance':
        default:
            return products.sort((a, b) => (b.featured ? 1 : 0) - (a.featured ? 1 : 0));
    }
}

// ==========================================
// QUICK VIEW MODAL
// ==========================================

let currentQuickViewProduct = null;
let currentQuickViewColor = null;
let currentQuickViewSize = null;
let currentQuickViewQty = 1;

function initQuickView() {
    const modal = document.getElementById('quickViewModal');
    if (!modal) return;

    // Fechar modal
    document.querySelectorAll('[data-close-modal]').forEach(el => {
        el.addEventListener('click', closeModal);
    });

    // Quantidade
    document.getElementById('qtyMinus')?.addEventListener('click', () => {
        if (currentQuickViewQty > 1) {
            currentQuickViewQty--;
            document.getElementById('qtyValue').value = currentQuickViewQty;
        }
    });

    document.getElementById('qtyPlus')?.addEventListener('click', () => {
        if (currentQuickViewQty < 10) {
            currentQuickViewQty++;
            document.getElementById('qtyValue').value = currentQuickViewQty;
        }
    });

    // Adicionar ao carrinho pelo modal
    document.getElementById('modalAddToCart')?.addEventListener('click', (e) => {
        const btn = e.currentTarget;
        const originalText = btn.textContent;
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> Adicionando...';

        setTimeout(() => {
            if (currentQuickViewProduct) {
                Cart.addToCart(currentQuickViewProduct.id, {
                    size: currentQuickViewSize,
                    color: currentQuickViewColor,
                    quantity: currentQuickViewQty
                });
            }
            btn.disabled = false;
            btn.textContent = originalText;
            closeModal();
        }, 500);
    });
}

function openQuickView(productId) {
    const product = PRODUCTS.find(p => p.id === productId);
    if (!product) return;

    currentQuickViewProduct = product;
    currentQuickViewColor = product.colors?.[0] || null;
    currentQuickViewSize = product.sizes?.[0] || null;
    currentQuickViewQty = 1;

    const modal = document.getElementById('quickViewModal');
    const modalImage = document.getElementById('modalImage');
    const modalBrand = document.getElementById('modalBrand');
    const modalName = document.getElementById('modalName');
    const modalStars = document.getElementById('modalStars');
    const modalReviews = document.getElementById('modalReviews');
    const modalDescription = document.getElementById('modalDescription');
    const modalColorOptions = document.getElementById('modalColorOptions');
    const modalSizeOptions = document.getElementById('modalSizeOptions');
    const modalOldPrice = document.getElementById('modalOldPrice');
    const modalPrice = document.getElementById('modalPrice');
    const modalInstallments = document.getElementById('modalInstallments');
    const qtyValue = document.getElementById('qtyValue');

    if (modalImage) modalImage.src = product.images[0];
    if (modalImage) modalImage.alt = product.name;
    if (modalBrand) modalBrand.textContent = product.brand;
    if (modalName) modalName.textContent = product.name;
    if (modalStars) modalStars.textContent = renderStars(product.rating);
    if (modalReviews) modalReviews.textContent = `(${product.reviewsCount} avaliações)`;
    if (modalDescription) modalDescription.textContent = product.description;
    if (modalOldPrice) {
        if (product.oldPrice) {
            modalOldPrice.textContent = formatPrice(product.oldPrice);
            modalOldPrice.style.display = 'inline';
        } else {
            modalOldPrice.style.display = 'none';
        }
    }
    if (modalPrice) modalPrice.textContent = formatPrice(product.price);
    if (modalInstallments) {
        const inst = calculateInstallments(product.price);
        modalInstallments.textContent = inst.formatted;
    }
    if (qtyValue) qtyValue.value = 1;

    // Cores
    if (modalColorOptions) {
        if (product.colors && product.colors.length > 0) {
            document.getElementById('modalColors').style.display = 'block';
            modalColorOptions.innerHTML = product.colors.map((c, i) => `
                <button class="color-option ${i === 0 ? 'active' : ''}" style="background: ${c.hex};" data-color-hex="${c.hex}" data-color-name="${c.name}" title="${c.name}" aria-label="${c.name}"></button>
            `).join('');

            modalColorOptions.querySelectorAll('.color-option').forEach(btn => {
                btn.addEventListener('click', () => {
                    modalColorOptions.querySelectorAll('.color-option').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    currentQuickViewColor = {
                        name: btn.dataset.colorName,
                        hex: btn.dataset.colorHex
                    };
                });
            });
        } else {
            document.getElementById('modalColors').style.display = 'none';
        }
    }

    // Tamanhos
    if (modalSizeOptions) {
        if (product.sizes && product.sizes.length > 0) {
            document.getElementById('modalSizes').style.display = 'block';
            modalSizeOptions.innerHTML = product.sizes.map((s, i) => `
                <button class="size-option ${i === 0 ? 'active' : ''}" data-size="${s}">${s}</button>
            `).join('');

            modalSizeOptions.querySelectorAll('.size-option').forEach(btn => {
                btn.addEventListener('click', () => {
                    modalSizeOptions.querySelectorAll('.size-option').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    currentQuickViewSize = btn.dataset.size;
                });
            });
        } else {
            document.getElementById('modalSizes').style.display = 'none';
        }
    }

    // Mostrar modal
    modal.classList.add('active');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    trapFocus(modal);
}

function closeModal() {
    const modal = document.getElementById('quickViewModal');
    if (modal) {
        modal.classList.remove('active');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }
    currentQuickViewProduct = null;
}

// Focus trap para acessibilidade
function trapFocus(element) {
    const focusable = element.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
    if (focusable.length === 0) return;

    const firstFocusable = focusable[0];
    const lastFocusable = focusable[focusable.length - 1];

    element._trapHandler = (e) => {
        if (e.key !== 'Tab') return;
        if (e.shiftKey) {
            if (document.activeElement === firstFocusable) {
                lastFocusable.focus();
                e.preventDefault();
            }
        } else {
            if (document.activeElement === lastFocusable) {
                firstFocusable.focus();
                e.preventDefault();
            }
        }
    };

    element.addEventListener('keydown', element._trapHandler);
    firstFocusable.focus();
}

// ==========================================
// SCROLL REVEAL
// ==========================================

function initScrollReveal() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15, rootMargin: '0px 0px -50px 0px' });

    document.querySelectorAll('.reveal').forEach(el => {
        if (!el.classList.contains('active')) {
            observer.observe(el);
        }
    });
}

// ==========================================
// NEWSLETTER
// ==========================================

function initNewsletter() {
    const form = document.getElementById('newsletterForm');
    if (!form) return;

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const email = form.querySelector('input').value;

        if (!isValidEmail(email)) {
            Cart.showToast('Por favor, insira um e-mail válido', 'error');
            return;
        }

        // Salvar
        try {
            const subs = JSON.parse(localStorage.getItem(STORAGE_KEYS.NEWSLETTER) || '[]');
            if (!subs.includes(email)) subs.push(email);
            localStorage.setItem(STORAGE_KEYS.NEWSLETTER, JSON.stringify(subs));
        } catch (e) {}

        Cart.showToast('E-mail cadastrado! Use o cupom BELLA10', 'success');
        form.reset();
    });
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// ==========================================
// RIPPLE EFFECT
// ==========================================

function initRippleEffect() {
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('.btn-ripple');
        if (!btn) return;

        const rect = btn.getBoundingClientRect();
        const ripple = document.createElement('span');
        ripple.classList.add('ripple');
        const size = Math.max(rect.width, rect.height);
        ripple.style.width = ripple.style.height = `${size}px`;
        ripple.style.left = `${e.clientX - rect.left - size / 2}px`;
        ripple.style.top = `${e.clientY - rect.top - size / 2}px`;
        btn.appendChild(ripple);
        setTimeout(() => ripple.remove(), 600);
    });
}

// ==========================================
// BUSCA
// ==========================================

function initSearch() {
    const searchBtn = document.getElementById('searchBtn');
    if (!searchBtn) return;

    searchBtn.addEventListener('click', () => {
        const query = prompt('🔍 Buscar produtos:');
        if (query && query.trim()) {
            const results = PRODUCTS.filter(p =>
                p.name.toLowerCase().includes(query.toLowerCase()) ||
                p.brand.toLowerCase().includes(query.toLowerCase()) ||
                p.description.toLowerCase().includes(query.toLowerCase()) ||
                (p.tags && p.tags.some(t => t.toLowerCase().includes(query.toLowerCase())))
            );

            if (results.length > 0) {
                state.filteredProducts = results;
                const grid = document.getElementById('shopGrid');
                if (grid) {
                    grid.innerHTML = results.map((p, i) => renderProductCard(p, i)).join('');
                    attachProductEvents(grid);
                    Wishlist.updateButtons();
                    document.getElementById('loja')?.scrollIntoView({ behavior: 'smooth' });
                    const countEl = document.getElementById('shopCount');
                    if (countEl) countEl.textContent = `${results.length} resultado(s) para "${query}"`;
                }
            } else {
                Cart.showToast(`Nenhum resultado para "${query}"`, 'error');
            }
        }
    });
}

// ==========================================
// CHECKOUT SIMULADO
// ==========================================

function startCheckout() {
    // Simular loading
    const loading = document.createElement('div');
    loading.className = 'modal active';
    loading.innerHTML = `
        <div class="modal-overlay"></div>
        <div class="modal-content" style="max-width: 400px; text-align: center; padding: 3rem;">
            <div class="spinner" style="width: 48px; height: 48px; border: 3px solid var(--color-border); border-top-color: var(--color-accent); border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 1.5rem;"></div>
            <h3 style="font-family: var(--font-display); font-style: italic; margin-bottom: 0.5rem;">Processando seu pedido</h3>
            <p style="color: var(--color-text-light);">Aguarde alguns instantes...</p>
        </div>
    `;
    document.body.appendChild(loading);
    document.body.style.overflow = 'hidden';

    setTimeout(() => {
        loading.remove();
        showOrderSuccess();
    }, 2000);
}

function showOrderSuccess() {
    const orderNumber = Math.floor(Math.random() * 900000 + 100000);
    const success = document.createElement('div');
    success.className = 'modal active';
    success.innerHTML = `
        <div class="modal-overlay" data-close-success></div>
        <div class="modal-content" style="max-width: 500px; text-align: center; padding: 3rem;">
            <div style="width: 80px; height: 80px; background: var(--color-success); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1.5rem; animation: bounce 0.6s ease;">
                <i class="fas fa-check" style="color: white; font-size: 2.5rem;"></i>
            </div>
            <h2 style="font-family: var(--font-display); font-size: 2rem; font-style: italic; margin-bottom: 1rem;">Pedido Confirmado!</h2>
            <p style="color: var(--color-text-body); margin-bottom: 1.5rem;">Seu pedido foi realizado com sucesso. Você receberá um e-mail com os detalhes da compra.</p>
            <div style="background: var(--color-bg-alt); padding: 1rem; margin-bottom: 1.5rem; border-radius: 4px;">
                <p style="font-size: 0.8rem; color: var(--color-text-light); margin: 0 0 4px;">Número do Pedido</p>
                <p style="font-size: 1.5rem; font-weight: 600; color: var(--color-accent); margin: 0;">#${orderNumber}</p>
            </div>
            <button class="btn btn-primary btn-block" data-close-success>Voltar à Loja</button>
        </div>
    `;
    document.body.appendChild(success);
    document.body.style.overflow = 'hidden';

    // Confetes
    launchConfetti();

    // Limpar carrinho
    Cart.clear();

    // Fechar
    success.querySelectorAll('[data-close-success]').forEach(el => {
        el.addEventListener('click', () => {
            success.remove();
            document.body.style.overflow = '';
        });
    });
}

function launchConfetti() {
    const colors = ['#C8A96E', '#1A1A1A', '#F8F5F0', '#C44545', '#5A8C5A'];
    for (let i = 0; i < 60; i++) {
        setTimeout(() => {
            const conf = document.createElement('div');
            conf.style.cssText = `
                position: fixed;
                top: -10px;
                left: ${Math.random() * 100}%;
                width: 10px;
                height: 10px;
                background: ${colors[Math.floor(Math.random() * colors.length)]};
                z-index: 9999;
                pointer-events: none;
                animation: confetti ${Math.random() * 2 + 2}s linear forwards;
            `;
            document.body.appendChild(conf);
            setTimeout(() => conf.remove(), 4000);
        }, i * 30);
    }
}

// ==========================================
// SMOOTH SCROLL
// ==========================================

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href === '#' || href.length < 2) return;
        const target = document.querySelector(href);
        if (target) {
            e.preventDefault();
            const headerHeight = 80;
            const offset = target.getBoundingClientRect().top + window.pageYOffset - headerHeight;
            window.scrollTo({ top: offset, behavior: 'smooth' });
        }
    });
});

// ==========================================
// DARK MODE
// ==========================================

function initTheme() {
    const toggle = document.getElementById('themeToggle');
    if (!toggle) return;

    const currentTheme = localStorage.getItem(STORAGE_KEYS.THEME) || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    toggle.innerHTML = currentTheme === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';

    toggle.addEventListener('click', () => {
        const theme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem(STORAGE_KEYS.THEME, theme);
        toggle.innerHTML = theme === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    });
}

// ==========================================
// COOKIE CONSENT
// ==========================================

function initCookieBanner() {
    const banner = document.getElementById('cookieBanner');
    if (!banner) return;

    const cookiesAccepted = localStorage.getItem(STORAGE_KEYS.COOKIES);
    if (cookiesAccepted === 'true') return;

    banner.classList.add('active');

    document.getElementById('cookieAccept')?.addEventListener('click', () => {
        localStorage.setItem(STORAGE_KEYS.COOKIES, 'true');
        banner.classList.remove('active');
    });

    document.getElementById('cookieReject')?.addEventListener('click', () => {
        localStorage.setItem(STORAGE_KEYS.COOKIES, 'false');
        banner.classList.remove('active');
    });
}

// ==========================================
// WISHLIST (FAVORITOS)
// ==========================================

const Wishlist = {
    getItems() {
        try {
            return JSON.parse(localStorage.getItem(STORAGE_KEYS.WISHLIST)) || [];
        } catch {
            return [];
        }
    },

    saveItems(items) {
        localStorage.setItem(STORAGE_KEYS.WISHLIST, JSON.stringify(items));
        this.updateBadge();
    },

    toggle(id) {
        let items = this.getItems();
        const index = items.indexOf(id);
        if (index !== -1) {
            items.splice(index, 1);
            Cart.showToast('Removido dos favoritos', 'info');
        } else {
            items.push(id);
            Cart.showToast('Adicionado aos favoritos', 'success');
        }
        this.saveItems(items);
    },

    isWishlisted(id) {
        return this.getItems().includes(id);
    },

    updateBadge() {
        const badge = document.getElementById('wishlistCount');
        if (badge) {
            badge.textContent = this.getItems().length;
        }
    },

    updateButtons() {
        document.querySelectorAll('.product-wishlist').forEach(btn => {
            const id = parseInt(btn.dataset.id);
            if (this.isWishlisted(id)) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }
};

// ==========================================
// HEADER SCROLL
// ==========================================

function initHeaderScroll() {
    const header = document.getElementById('header');
    if (!header) return;

    let lastScroll = 0;
    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        if (currentScroll > 80) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
        lastScroll = currentScroll;
    });
}

// ==========================================
// INICIALIZAÇÃO
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    // Renderizar categorias e produtos iniciais
    renderCategories();
    renderFilters();
    filterAndRender(); // Mostra todos os produtos

    // Inicializar módulos
    initSort();
    initQuickView();
    initScrollReveal();
    initNewsletter();
    initRippleEffect();
    initSearch();
    initTheme();
    initCookieBanner();
    initHeaderScroll();

    // Wishlist já está integrado nos eventos
    Wishlist.updateBadge();

    // Carregar produtos nas seções específicas (ex: destaque, skincare, perfumaria, sale)
    // Pode ser feito com filtros, mas para simplificar, já usamos o grid da loja
    // Opcional: você pode renderizar grids separados
});