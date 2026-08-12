/* ==========================================
   DADOS MOCK - BellaGlow Cosméticos
   Array de produtos com todas propriedades
   ========================================== */

const PRODUCTS = [
    {
        id: 1,
        name: "Sérum Vitamina C Premium",
        brand: "BellaGlow",
        description: "Sérum facial antioxidante com 20% de vitamina C pura e ácido ferúlico. Reduz manchas, ilumina e uniformiza o tom da pele. Textura leve e rápida absorção.",
        price: 18990, // R$ 189,90 em centavos
        oldPrice: 24990, // R$ 249,90
        images: [
            "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600&q=80",
            "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600&q=80"
        ],
        category: "skincare",
        subcategory: "serum",
        sizes: ["30ml", "50ml"],
        colors: [
            { name: "Original", hex: "#F4D9C4" }
        ],
        rating: 4.8,
        reviewsCount: 234,
        inStock: true,
        stock: 12,
        isNew: true,
        isSale: true,
        featured: true,
        tags: ["antioxidante", "iluminador", "manchas"]
    },
    {
        id: 2,
        name: "Paleta Sombras Rose Quartz",
        brand: "BellaGlow Studio",
        description: "Paleta com 12 tons rosados e neutros. Pigmentação intensa e longa duração. Acabamento matte, shimmer e metálico.",
        price: 15990,
        oldPrice: null,
        images: [
            "https://images.unsplash.com/photo-1583241800698-9c2e9c5e9656?w=600&q=80",
            "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=600&q=80"
        ],
        category: "maquiagem",
        subcategory: "olhos",
        sizes: ["Único"],
        colors: [
            { name: "Rose", hex: "#E8B4B8" },
            { name: "Nude", hex: "#D4B5A0" }
        ],
        rating: 4.9,
        reviewsCount: 567,
        inStock: true,
        stock: 8,
        isNew: true,
        isSale: false,
        featured: true,
        tags: ["sombras", "paleta", "olhos"]
    },
    {
        id: 3,
        name: "Batom Líquido Matte Veludo",
        brand: "BellaGlow",
        description: "Batom líquido de longa duração com acabamento matte aveludado. Não resseca os lábios e mantém a cor por até 12 horas.",
        price: 4990,
        oldPrice: 6990,
        images: [
            "https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=600&q=80",
            "https://images.unsplash.com/photo-1631214524020-7e18db9a8f92?w=600&q=80"
        ],
        category: "maquiagem",
        subcategory: "labios",
        sizes: ["5ml"],
        colors: [
            { name: "Nude Rosé", hex: "#D4A595" },
            { name: "Vermelho Clássico", hex: "#C44545" },
            { name: "Berry", hex: "#8B2C4A" },
            { name: "Mauve", hex: "#A87A8B" }
        ],
        rating: 4.7,
        reviewsCount: 892,
        inStock: true,
        stock: 25,
        isNew: false,
        isSale: true,
        featured: true,
        tags: ["batom", "matte", "labios"]
    },
    {
        id: 4,
        name: "Hidratante Facial Hyaluronic",
        brand: "BellaGlow Skin",
        description: "Hidratante com ácido hialurônico de alto e baixo peso molecular. Hidratação profunda por 72 horas. Pele macia e luminosa.",
        price: 12990,
        oldPrice: null,
        images: [
            "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=600&q=80",
            "https://images.unsplash.com/photo-1570194065650-d99fb4bedf0a?w=600&q=80"
        ],
        category: "skincare",
        subcategory: "hidratante",
        sizes: ["50ml"],
        colors: [
            { name: "Original", hex: "#F0E4D8" }
        ],
        rating: 4.9,
        reviewsCount: 412,
        inStock: true,
        stock: 18,
        isNew: true,
        isSale: false,
        featured: true,
        tags: ["hidratante", "acido hialuronico", "rosto"]
    },
    {
        id: 5,
        name: "Base Líquida Second Skin",
        brand: "BellaGlow Studio",
        description: "Base com cobertura modulável e acabamento natural. Contém SPF 30 e ácido hialurônico. 24 cores disponíveis para todos os tons de pele.",
        price: 8990,
        oldPrice: 11990,
        images: [
            "https://images.unsplash.com/photo-1631214524110-bf7c1c14b16a?w=600&q=80",
            "https://images.unsplash.com/photo-1522335789203-aaa0f6c7e3b1?w=600&q=80"
        ],
        category: "maquiagem",
        subcategory: "rosto",
        sizes: ["30ml"],
        colors: [
            { name: "Porcelain", hex: "#F5DCC4" },
            { name: "Beige", hex: "#E8C8A8" },
            { name: "Sand", hex: "#D4B088" },
            { name: "Caramel", hex: "#B89070" },
            { name: "Mocha", hex: "#8B6048" }
        ],
        rating: 4.8,
        reviewsCount: 1203,
        inStock: true,
        stock: 35,
        isNew: false,
        isSale: true,
        featured: true,
        tags: ["base", "cobertura", "spf"]
    },
    {
        id: 6,
        name: "Perfume Eau de Parfum Lumière",
        brand: "BellaGlow Maison",
        description: "Fragrância feminina sofisticada com notas florais e amadeiradas. Notas de topo: bergamota e pêssego. Coração: jasmim e rosa. Fundo: sândalo e almíscar.",
        price: 34990,
        oldPrice: 42990,
        images: [
            "https://images.unsplash.com/photo-1541643600914-78b084683601?w=600&q=80",
            "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=600&q=80"
        ],
        category: "perfumaria",
        subcategory: "feminino",
        sizes: ["30ml", "50ml", "100ml"],
        colors: [
            { name: "Original", hex: "#E8D4C8" }
        ],
        rating: 4.9,
        reviewsCount: 678,
        inStock: true,
        stock: 6,
        isNew: true,
        isSale: true,
        featured: true,
        tags: ["perfume", "feminino", "floral"]
    },
    {
        id: 7,
        name: "Máscara Capilar Reconstrução",
        brand: "BellaGlow Hair",
        description: "Máscara de tratamento intensivo com queratina e óleo de argan. Repara danos, nutre e devolve brilho aos fios.",
        price: 7990,
        oldPrice: null,
        images: [
            "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600&q=80",
            "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=600&q=80"
        ],
        category: "corpo",
        subcategory: "cabelo",
        sizes: ["300g", "500g"],
        colors: [
            { name: "Original", hex: "#F0D8C0" }
        ],
        rating: 4.6,
        reviewsCount: 234,
        inStock: true,
        stock: 22,
        isNew: false,
        isSale: false,
        featured: false,
        tags: ["cabelo", "tratamento", "queratina"]
    },
    {
        id: 8,
        name: "Kit Skincare Rotina Completa",
        brand: "BellaGlow",
        description: "Kit com 5 produtos essenciais: limpador, tônico, sérum, hidratante e protetor solar. Rotina completa de cuidados com a pele.",
        price: 29990,
        oldPrice: 39990,
        images: [
            "https://images.unsplash.com/photo-1556228841-a3c527ebefe5?w=600&q=80",
            "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=600&q=80"
        ],
        category: "skincare",
        subcategory: "kit",
        sizes: ["Kit Completo"],
        colors: [
            { name: "Original", hex: "#E8C5B8" }
        ],
        rating: 5.0,
        reviewsCount: 156,
        inStock: true,
        stock: 2,
        isNew: true,
        isSale: true,
        featured: true,
        tags: ["kit", "skincare", "rotina"]
    },
    {
        id: 9,
        name: "Máscara de Cílios Volume Extreme",
        brand: "BellaGlow Studio",
        description: "Máscara de cílios com efeito volume extremo. Fórmula enriquecida com queratina. Não borra e é fácil de remover.",
        price: 5990,
        oldPrice: 7990,
        images: [
            "https://images.unsplash.com/photo-1631214524110-bf7c1c14b16a?w=600&q=80",
            "https://images.unsplash.com/photo-1583241800698-9c2e9c5e9656?w=600&q=80"
        ],
        category: "maquiagem",
        subcategory: "olhos",
        sizes: ["10ml"],
        colors: [
            { name: "Preto", hex: "#1A1A1A" }
        ],
        rating: 4.7,
        reviewsCount: 445,
        inStock: true,
        stock: 30,
        isNew: false,
        isSale: true,
        featured: false,
        tags: ["mascara", "cilios", "olhos"]
    },
    {
        id: 10,
        name: "Gloss Labial Hidratante",
        brand: "BellaGlow",
        description: "Gloss labial com efeito volumizador e brilho intenso. Hidrata os lábios com manteiga de karité. Não gruda.",
        price: 3990,
        oldPrice: null,
        images: [
            "https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=600&q=80",
            "https://images.unsplash.com/photo-1631214524020-7e18db9a8f92?w=600&q=80"
        ],
        category: "maquiagem",
        subcategory: "labios",
        sizes: ["5ml"],
        colors: [
            { name: "Crystal", hex: "#F0E4D8" },
            { name: "Rosé", hex: "#E8B4B8" },
            { name: "Nude", hex: "#D4A595" }
        ],
        rating: 4.5,
        reviewsCount: 178,
        inStock: false,
        stock: 0,
        isNew: true,
        isSale: false,
        featured: false,
        tags: ["gloss", "labios", "brilho"]
    },
    {
        id: 11,
        name: "Esfoliante Facial Enzimático",
        brand: "BellaGlow Skin",
        description: "Esfoliante suave com enzimas naturais de mamão e abacaxi. Remove células mortas e renova a pele sem agredir. Uso semanal.",
        price: 8990,
        oldPrice: null,
        images: [
            "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=600&q=80",
            "https://images.unsplash.com/photo-1570194065650-d99fb4bedf0a?w=600&q=80"
        ],
        category: "skincare",
        subcategory: "esfoliante",
        sizes: ["75ml"],
        colors: [
            { name: "Original", hex: "#E8C8A8" }
        ],
        rating: 4.6,
        reviewsCount: 123,
        inStock: true,
        stock: 15,
        isNew: false,
        isSale: false,
        featured: false,
        tags: ["esfoliante", "renovacao", "rosto"]
    },
    {
        id: 12,
        name: "Body Splash Vanilla Dreams",
        brand: "BellaGlow Body",
        description: "Body splash com notas de baunilha, coco e flores brancas. Fragrância suave e duradoura para o dia a dia. Frasco 200ml.",
        price: 6990,
        oldPrice: 9990,
        images: [
            "https://images.unsplash.com/photo-1541643600914-78b084683601?w=600&q=80",
            "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=600&q=80"
        ],
        category: "perfumaria",
        subcategory: "body",
        sizes: ["200ml"],
        colors: [
            { name: "Vanilla", hex: "#F0D8B0" }
        ],
        rating: 4.8,
        reviewsCount: 345,
        inStock: true,
        stock: 28,
        isNew: true,
        isSale: true,
        featured: false,
        tags: ["body splash", "vanilla", "corpo"]
    }
];

// Categorias disponíveis
const CATEGORIES = [
    { id: "skincare", name: "Skincare", count: 0, image: "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=600&q=80" },
    { id: "maquiagem", name: "Maquiagem", count: 0, image: "https://images.unsplash.com/photo-1522335789203-aaa0f6c7e3b1?w=600&q=80" },
    { id: "perfumaria", name: "Perfumaria", count: 0, image: "https://images.unsplash.com/photo-1541643600914-78b084683601?w=600&q=80" },
    { id: "corpo", name: "Corpo & Banho", count: 0, image: "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600&q=80" }
];

// Ordenação
const SORT_OPTIONS = [
    { value: "relevance", label: "Mais Relevantes" },
    { value: "price-asc", label: "Menor Preço" },
    { value: "price-desc", label: "Maior Preço" },
    { value: "newest", label: "Mais Recentes" }
];

// Contar produtos por categoria
PRODUCTS.forEach(product => {
    const cat = CATEGORIES.find(c => c.id === product.category);
    if (cat) cat.count++;
});

// Helper: Formatar preço
function formatPrice(cents) {
    return (cents / 100).toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    });
}

// Helper: Calcular parcelas
function calculateInstallments(cents, maxInstallments = 3) {
    const total = cents / 100;
    const installment = total / maxInstallments;
    return {
        total: total,
        installment: installment,
        formatted: `em até ${maxInstallments}x de ${installment.toLocaleString('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        })} sem juros`
    };
}