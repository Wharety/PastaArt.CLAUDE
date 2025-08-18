/**
 * PASTAART ENCANTO - JavaScript Administrativo
 * Funcionalidades específicas para o painel admin
 */

// Inicialização quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    initializeAdminApp();
});

/**
 * Inicializar aplicação administrativa
 */
function initializeAdminApp() {
    initAdminNavigation();
    initDataTables();
    initImageUpload();
    initFormValidations();
    initConfirmations();
    initPreviewUpdates();
    initImageLightbox();
    initBottomNav();
    
    console.log('🛠️ Painel Administrativo - Aplicação inicializada');
}

/**
 * Navegação administrativa
 */
function initAdminNavigation() {
    // Marcar link ativo
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.admin-nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Navegação responsive (mobile)
    const mobileToggle = document.querySelector('.mobile-nav-toggle');
    if (mobileToggle) {
        mobileToggle.addEventListener('click', function() {
            const adminMenu = document.querySelector('.admin-menu');
            adminMenu.classList.toggle('show');
        });
    }
}

/**
 * Funcionalidades de tabelas
 */
function initDataTables() {
    // Filtros
    const statusFilter = document.getElementById('status-filter');
    if (statusFilter) {
        statusFilter.addEventListener('change', function() {
            filterTableRows('status', this.value);
        });
    }
    
    // Ordenação
    const sortButtons = document.querySelectorAll('[data-sort]');
    sortButtons.forEach(button => {
        button.addEventListener('click', function() {
            const column = this.dataset.sort;
            const direction = this.dataset.direction === 'asc' ? 'desc' : 'asc';
            this.dataset.direction = direction;
            
            sortTable(column, direction);
        });
    });
    
    // Seleção múltipla
    const selectAll = document.querySelector('#select-all');
    if (selectAll) {
        selectAll.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.row-select');
            checkboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            updateBulkActions();
        });
    }
    
    const rowSelects = document.querySelectorAll('.row-select');
    rowSelects.forEach(checkbox => {
        checkbox.addEventListener('change', updateBulkActions);
    });
}

/**
 * Filtrar linhas da tabela
 */
function filterTableRows(filterType, filterValue) {
    const rows = document.querySelectorAll('.product-row');
    
    rows.forEach(row => {
        let show = true;
        
        if (filterType === 'status' && filterValue) {
            const rowStatus = row.dataset.status;
            show = rowStatus === filterValue;
        }
        
        row.style.display = show ? 'table-row' : 'none';
    });
    
    updateTableCount();
}

/**
 * Ordenar tabela
 */
function sortTable(column, direction) {
    const tbody = document.querySelector('.admin-table tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        let aValue, bValue;
        
        switch (column) {
            case 'name':
                aValue = a.querySelector('.product-name-content h4').textContent;
                bValue = b.querySelector('.product-name-content h4').textContent;
                break;
            case 'price':
                aValue = parseFloat(a.querySelector('.price-display').textContent.replace('R$ ', ''));
                bValue = parseFloat(b.querySelector('.price-display').textContent.replace('R$ ', ''));
                break;
            case 'date':
                aValue = a.querySelector('.date-display').textContent;
                bValue = b.querySelector('.date-display').textContent;
                break;
            default:
                return 0;
        }
        
        if (direction === 'asc') {
            return aValue > bValue ? 1 : -1;
        } else {
            return aValue < bValue ? 1 : -1;
        }
    });
    
    rows.forEach(row => tbody.appendChild(row));
}

/**
 * Atualizar contador da tabela
 */
function updateTableCount() {
    const visibleRows = document.querySelectorAll('.product-row[style*="table-row"], .product-row:not([style])');
    const totalRows = document.querySelectorAll('.product-row');
    const countElement = document.querySelector('.table-count');
    
    if (countElement) {
        countElement.textContent = `${visibleRows.length} de ${totalRows.length} produtos`;
    }
}

/**
 * Atualizar ações em lote
 */
function updateBulkActions() {
    const selectedCount = document.querySelectorAll('.row-select:checked').length;
    const bulkActions = document.querySelector('.bulk-actions');
    
    if (bulkActions) {
        bulkActions.style.display = selectedCount > 0 ? 'block' : 'none';
        
        const countSpan = bulkActions.querySelector('.selected-count');
        if (countSpan) {
            countSpan.textContent = selectedCount;
        }
    }
}

/**
 * Upload de imagens
 */
function initImageUpload() {
    const fileInput = document.getElementById('imagem');
    const previewContainer = document.getElementById('image-preview');
    const previewImg = document.getElementById('preview-img');
    
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            
            if (file) {
                // Validar tipo de arquivo
                if (!isValidImageType(file)) {
                    showError('Tipo de arquivo não suportado. Use JPG, PNG, GIF ou WebP.');
                    this.value = '';
                    return;
                }
                
                // Validar tamanho
                if (file.size > 16 * 1024 * 1024) { // 16MB
                    showError('Arquivo muito grande. Máximo 16MB.');
                    this.value = '';
                    return;
                }
                
                // Mostrar preview
                const reader = new FileReader();
                reader.onload = function(e) {
                    if (previewImg && previewContainer) {
                        previewImg.src = e.target.result;
                        previewContainer.style.display = 'block';
                        
                        // Atualizar preview do produto
                        updateProductPreview();
                    }
                };
                reader.readAsDataURL(file);
                
                // Atualizar label do arquivo
                updateFileLabel(file.name);
            }
        });
    }
    
    // Drag and drop
    const fileUploadLabel = document.querySelector('.file-upload-label');
    if (fileUploadLabel) {
        fileUploadLabel.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('drag-over');
        });
        
        fileUploadLabel.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
        });
        
        fileUploadLabel.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                fileInput.dispatchEvent(new Event('change'));
            }
        });
    }
}

/**
 * Validar tipo de imagem
 */
function isValidImageType(file) {
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    return validTypes.includes(file.type);
}

/**
 * Atualizar label do arquivo
 */
function updateFileLabel(filename) {
    const fileUploadText = document.querySelector('.file-upload-text');
    if (fileUploadText) {
        fileUploadText.textContent = `Arquivo selecionado: ${filename}`;
    }
}

/**
 * Remover preview da imagem
 */
function removeImagePreview() {
    const fileInput = document.getElementById('imagem');
    const previewContainer = document.getElementById('image-preview');
    const fileUploadText = document.querySelector('.file-upload-text');
    
    if (fileInput) fileInput.value = '';
    if (previewContainer) previewContainer.style.display = 'none';
    if (fileUploadText) fileUploadText.textContent = 'Clique para selecionar uma imagem';
    
    updateProductPreview();
}

/**
 * Validações de formulário
 */
function initFormValidations() {
    const forms = document.querySelectorAll('.admin-form, .product-form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateAdminForm(this)) {
                e.preventDefault();
                return false;
            }
            
            // Mostrar loading
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                showLoading(submitBtn, 'Salvando...');
            }
        });
    });
    
    // Validação em tempo real
    const requiredFields = document.querySelectorAll('input[required], textarea[required]');
    requiredFields.forEach(field => {
        field.addEventListener('blur', function() {
            validateField(this);
        });
    });
    
    // Contador de caracteres
    const textareas = document.querySelectorAll('textarea[maxlength]');
    textareas.forEach(textarea => {
        const maxLength = parseInt(textarea.getAttribute('maxlength'));
        createCharCounter(textarea, maxLength);
        
        textarea.addEventListener('input', function() {
            updateCharCounter(this, maxLength);
        });
    });
}

/**
 * Validar formulário administrativo
 */
function validateAdminForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('input[required], textarea[required], select[required]');
    
    requiredFields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    // Validações específicas
    const priceField = form.querySelector('input[name="preco"]');
    if (priceField && parseFloat(priceField.value) <= 0) {
        showFieldError(priceField, 'O preço deve ser maior que zero');
        isValid = false;
    }
    
    return isValid;
}

/**
 * Validar campo individual
 */
function validateField(field) {
    const value = field.value.trim();
    
    clearFieldError(field);
    
    if (field.hasAttribute('required') && !value) {
        showFieldError(field, 'Este campo é obrigatório');
        return false;
    }
    
    if (field.type === 'email' && value && !isValidEmail(value)) {
        showFieldError(field, 'Email inválido');
        return false;
    }
    
    if (field.type === 'number' && value && isNaN(value)) {
        showFieldError(field, 'Valor numérico inválido');
        return false;
    }
    
    return true;
}

/**
 * Validar email
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Mostrar erro em campo
 */
function showFieldError(field, message) {
    clearFieldError(field);
    
    field.classList.add('error');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

/**
 * Limpar erro de campo
 */
function clearFieldError(field) {
    field.classList.remove('error');
    
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
}

/**
 * Criar contador de caracteres
 */
function createCharCounter(textarea, maxLength) {
    const counter = document.createElement('small');
    counter.className = 'char-counter';
    counter.style.color = '#6c757d';
    counter.style.fontSize = '0.8rem';
    
    textarea.parentNode.appendChild(counter);
    updateCharCounter(textarea, maxLength);
}

/**
 * Atualizar contador de caracteres
 */
function updateCharCounter(textarea, maxLength) {
    const current = textarea.value.length;
    const remaining = maxLength - current;
    const counter = textarea.parentNode.querySelector('.char-counter');
    
    if (counter) {
        counter.textContent = `${current}/${maxLength} caracteres`;
        counter.style.color = remaining < 50 ? '#e74c3c' : '#6c757d';
    }
}

/**
 * Confirmações de ação
 */
function initConfirmations() {
    // Exclusões
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.dataset.confirmDelete || 'Tem certeza que deseja excluir este item?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
    
    // Alterações de status
    const statusButtons = document.querySelectorAll('[data-confirm-status]');
    statusButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.dataset.confirmStatus || 'Tem certeza que deseja alterar o status?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
}

/**
 * Atualizações de preview em tempo real
 */
function initPreviewUpdates() {
    const previewFields = ['nome', 'descricao', 'preco'];
    
    previewFields.forEach(fieldName => {
        const field = document.getElementById(fieldName);
        if (field) {
            field.addEventListener('input', debounce(updateProductPreview, 300));
        }
    });
}

/**
 * Atualizar preview do produto
 */
function updateProductPreview() {
    const nome = document.getElementById('nome')?.value || 'Nome do Produto';
    const descricao = document.getElementById('descricao')?.value || 'Descrição do produto aparecerá aqui...';
    const preco = document.getElementById('preco')?.value || '0.00';
    
    // Atualizar elementos do preview
    const previewName = document.getElementById('preview-name');
    const previewDescription = document.getElementById('preview-description');
    const previewPrice = document.getElementById('preview-price');
    const previewImage = document.getElementById('preview-product-image');
    
    if (previewName) {
        previewName.textContent = nome;
    }
    
    if (previewDescription) {
        const truncatedDesc = descricao.length > 80 ? descricao.substring(0, 80) + '...' : descricao;
        previewDescription.textContent = truncatedDesc;
    }
    
    if (previewPrice) {
        previewPrice.textContent = `R$ ${parseFloat(preco || 0).toFixed(2)}`;
    }
    
    // Atualizar imagem do preview
    if (previewImage) {
        const previewImg = document.getElementById('preview-img');
        const currentImage = document.querySelector('#current-image');
        
        if (previewImg && previewImg.src && previewImg.src !== window.location.href) {
            previewImage.innerHTML = `<img src="${previewImg.src}" alt="${nome}">`;
        } else if (currentImage) {
            previewImage.innerHTML = `<img src="${currentImage.src}" alt="${nome}">`;
        } else {
            previewImage.innerHTML = '<div class="product-placeholder"><i class="fas fa-birthday-cake"></i></div>';
        }
    }
}

/**
 * Modal de confirmação personalizado
 */
function showConfirmModal(title, message, confirmCallback, cancelCallback) {
    // Criar modal se não existir
    let modal = document.getElementById('confirmModal');
    if (!modal) {
        modal = createConfirmModal();
        document.body.appendChild(modal);
    }
    
    // Atualizar conteúdo
    modal.querySelector('.modal-title').textContent = title;
    modal.querySelector('.modal-message').textContent = message;
    
    // Configurar botões
    const confirmBtn = modal.querySelector('.confirm-btn');
    const cancelBtn = modal.querySelector('.cancel-btn');
    
    confirmBtn.onclick = function() {
        hideModal(modal);
        if (confirmCallback) confirmCallback();
    };
    
    cancelBtn.onclick = function() {
        hideModal(modal);
        if (cancelCallback) cancelCallback();
    };
    
    // Mostrar modal
    showModal(modal);
}

/**
 * Criar modal de confirmação
 */
function createConfirmModal() {
    const modal = document.createElement('div');
    modal.id = 'confirmModal';
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3 class="modal-title">Confirmar Ação</h3>
            </div>
            <div class="modal-body">
                <p class="modal-message">Tem certeza que deseja realizar esta ação?</p>
            </div>
            <div class="modal-footer">
                <button class="btn btn-outline cancel-btn">Cancelar</button>
                <button class="btn btn-primary confirm-btn">Confirmar</button>
            </div>
        </div>
    `;
    
    // Fechar ao clicar fora
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            hideModal(modal);
        }
    });
    
    return modal;
}

/**
 * Mostrar modal
 */
function showModal(modal) {
    modal.style.display = 'flex';
    setTimeout(() => {
        modal.classList.add('show');
    }, 10);
}

/**
 * Esconder modal
 */
function hideModal(modal) {
    modal.classList.remove('show');
    setTimeout(() => {
        modal.style.display = 'none';
    }, 300);
}

/**
 * Mostrar notificação de sucesso
 */
function showSuccess(message) {
    showNotification(message, 'success');
}

/**
 * Mostrar notificação de erro
 */
function showError(message) {
    showNotification(message, 'error');
}

/**
 * Mostrar notificação
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    // Adicionar ao DOM
    document.body.appendChild(notification);
    
    // Auto-remove
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

/**
 * Obter ícone da notificação
 */
function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'times-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

/**
 * Lightbox de imagem com zoom/arraste para o admin
 */
function initImageLightbox() {
    const selectors = [
        '.table-product-image',
        '.product-mini-image img',
        '.product-image-mobile img',
        '.current-image img',
        '.upload-preview img',
        '#current-image',
        '#preview-product-image img',
        '#currentLogo', '#currentBanner',
        '#currentTradicionalImage', '#currentPersonalizadoImage',
        '.order-items-card .item-image img'
    ];

    // Marcar imagens como zoomable e bindar clique
    const images = document.querySelectorAll(selectors.join(','));
    images.forEach(img => {
        if (!img.dataset.zoomBound) {
            img.dataset.zoomBound = 'true';
            img.style.cursor = 'zoom-in';
            img.addEventListener('click', () => openImageLightbox(img.src, img.alt || 'Imagem'));
        }
    });

    // Observar inserções dinâmicas (previews, etc.)
    if (!window.__imageLightboxObserver) {
        const observer = new MutationObserver((mutations) => {
            for (const m of mutations) {
                m.addedNodes && m.addedNodes.forEach(node => {
                    if (node.nodeType !== 1) return;
                    const isImg = node.tagName === 'IMG' ? [node] : Array.from(node.querySelectorAll?.('img') || []);
                    isImg.forEach(img => {
                        if (!img.dataset.zoomBound && (
                            img.closest('.upload-preview') ||
                            img.closest('.current-image') ||
                            img.closest('#preview-product-image')
                        )) {
                            img.dataset.zoomBound = 'true';
                            img.style.cursor = 'zoom-in';
                            img.addEventListener('click', () => openImageLightbox(img.src, img.alt || 'Imagem'));
                        }
                    });
                });
            }
        });
        observer.observe(document.body, { childList: true, subtree: true });
        window.__imageLightboxObserver = observer;
    }
}

function openImageLightbox(src, alt) {
    let overlay = document.getElementById('imageLightboxOverlay');
    if (!overlay) {
        overlay = createImageLightboxOverlay();
        document.body.appendChild(overlay);
    }

    const img = overlay.querySelector('.image-lightbox-img');
    const title = overlay.querySelector('.image-lightbox-title');
    img.src = src;
    title.textContent = alt || '';

    // Reset estado
    resetImageTransform(overlay);

    // Mostrar
    overlay.style.display = 'flex';
    requestAnimationFrame(() => overlay.classList.add('show'));
}

function createImageLightboxOverlay() {
    const overlay = document.createElement('div');
    overlay.id = 'imageLightboxOverlay';
    overlay.className = 'image-lightbox-overlay';
    overlay.innerHTML = `
        <div class="image-lightbox-toolbar">
            <div class="image-lightbox-title"></div>
            <div class="image-lightbox-actions">
                <button class="image-lightbox-btn" data-action="zoom-out" title="Diminuir ( - )"><i class="fas fa-search-minus"></i></button>
                <button class="image-lightbox-btn" data-action="zoom-in" title="Aumentar ( + )"><i class="fas fa-search-plus"></i></button>
                <button class="image-lightbox-btn" data-action="reset" title="Ajustar (0)"><i class="fas fa-compress"></i></button>
                <button class="image-lightbox-btn close" data-action="close" title="Fechar (Esc)"><i class="fas fa-times"></i></button>
            </div>
        </div>
        <div class="image-lightbox-stage">
            <img class="image-lightbox-img" alt="preview" draggable="false" />
        </div>
    `;

    // Eventos de fechamento
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) hideImageLightbox(overlay);
    });
    overlay.querySelector('[data-action="close"]').addEventListener('click', () => hideImageLightbox(overlay));

    // Interações de zoom/arraste
    const stage = overlay.querySelector('.image-lightbox-stage');
    const img = overlay.querySelector('.image-lightbox-img');
    const ZOOM_STEP = 0.2;
    const MIN_SCALE = 1;
    const MAX_SCALE = 5;
    let scale = 1;
    let pos = { x: 0, y: 0 };
    let isPanning = false;
    let start = { x: 0, y: 0 };

    function applyTransform() {
        img.style.transform = `translate(${pos.x}px, ${pos.y}px) scale(${scale})`;
        img.style.cursor = scale > 1 ? 'grab' : 'zoom-out';
    }

    stage.addEventListener('wheel', (e) => {
        e.preventDefault();
        const delta = Math.sign(e.deltaY);
        scale = Math.min(MAX_SCALE, Math.max(MIN_SCALE, scale + (delta > 0 ? -ZOOM_STEP : ZOOM_STEP)));
        applyTransform();
    }, { passive: false });

    stage.addEventListener('mousedown', (e) => {
        if (scale <= 1) return;
        isPanning = true;
        start = { x: e.clientX - pos.x, y: e.clientY - pos.y };
        img.style.cursor = 'grabbing';
    });
    window.addEventListener('mouseup', () => {
        isPanning = false;
        if (scale > 1) img.style.cursor = 'grab';
    });
    window.addEventListener('mousemove', (e) => {
        if (!isPanning) return;
        pos = { x: e.clientX - start.x, y: e.clientY - start.y };
        applyTransform();
    });

    // Duplo clique para alternar zoom
    stage.addEventListener('dblclick', () => {
        scale = scale > 1 ? 1 : 2;
        pos = { x: 0, y: 0 };
        applyTransform();
    });

    // Botões
    overlay.querySelector('[data-action="zoom-in"]').addEventListener('click', () => {
        scale = Math.min(MAX_SCALE, scale + ZOOM_STEP);
        applyTransform();
    });
    overlay.querySelector('[data-action="zoom-out"]').addEventListener('click', () => {
        scale = Math.max(MIN_SCALE, scale - ZOOM_STEP);
        applyTransform();
    });
    overlay.querySelector('[data-action="reset"]').addEventListener('click', () => {
        scale = 1; pos = { x: 0, y: 0 }; applyTransform();
    });

    // Teclado
    window.addEventListener('keydown', (e) => {
        if (overlay.style.display !== 'flex') return;
        if (e.key === 'Escape') hideImageLightbox(overlay);
        if (e.key === '+') { scale = Math.min(MAX_SCALE, scale + ZOOM_STEP); applyTransform(); }
        if (e.key === '-') { scale = Math.max(MIN_SCALE, scale - ZOOM_STEP); applyTransform(); }
        if (e.key === '0') { scale = 1; pos = { x: 0, y: 0 }; applyTransform(); }
    });

    // Guardar estado e helpers
    overlay._imageState = { get scale() { return scale; }, set scale(v) { scale = v; }, get pos() { return pos; }, set pos(v) { pos = v; }, applyTransform };

    function reset() { scale = 1; pos = { x: 0, y: 0 }; applyTransform(); }
    overlay._reset = reset;

    return overlay;
}

function resetImageTransform(overlay) {
    if (overlay && typeof overlay._reset === 'function') overlay._reset();
}

function hideImageLightbox(overlay) {
    overlay.classList.remove('show');
    setTimeout(() => { overlay.style.display = 'none'; }, 200);
}

/**
 * Mostrar loading
 */
function showLoading(element, text = 'Carregando...') {
    const originalContent = element.innerHTML;
    element.dataset.originalContent = originalContent;
    element.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${text}`;
    element.disabled = true;
}

/**
 * Esconder loading
 */
function hideLoading(element) {
    if (element.dataset.originalContent) {
        element.innerHTML = element.dataset.originalContent;
        delete element.dataset.originalContent;
    }
    element.disabled = false;
}

/**
 * Debounce para otimizar eventos
 */
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction() {
        const context = this;
        const args = arguments;
        
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        
        if (callNow) func.apply(context, args);
    };
}

/**
 * Utilitários para estatísticas
 */
const AdminStats = {
    updateCard: function(cardId, value) {
        const card = document.querySelector(`[data-stat="${cardId}"]`);
        if (card) {
            const valueElement = card.querySelector('.stat-value');
            if (valueElement) {
                this.animateNumber(valueElement, parseInt(valueElement.textContent), value);
            }
        }
    },
    
    animateNumber: function(element, start, end, duration = 1000) {
        const range = end - start;
        let current = start;
        const increment = range / (duration / 16);
        
        const timer = setInterval(() => {
            current += increment;
            element.textContent = Math.round(current);
            
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                element.textContent = end;
                clearInterval(timer);
            }
        }, 16);
    }
};

// Exportar funções para uso global
window.AdminApp = {
    showConfirmModal,
    showSuccess,
    showError,
    showLoading,
    hideLoading,
    updateProductPreview,
    removeImagePreview,
    AdminStats,
    initImageLightbox,
    initBottomNav
};

/**
 * Bottom navbar (mobile) - marcar ativo conforme rota
 */
function initBottomNav() {
    const links = document.querySelectorAll('.admin-bottom-nav .admin-bottom-link');
    if (!links.length) return;
    const path = window.location.pathname;

    links.forEach(a => a.classList.remove('active'));

    let key = null;
    if (/\/admin(\/dashboard)?\/?$/.test(path)) key = 'dashboard';
    else if (/\/admin\/doces/.test(path)) key = 'produtos';
    else if (/\/admin\/pedidos/.test(path)) key = 'pedidos';
    else if (/\/configuracoes/.test(path)) key = 'configuracoes';

    if (key) {
        const active = document.querySelector(`.admin-bottom-link[data-nav="${key}"]`);
        if (active) active.classList.add('active');
    }
}
