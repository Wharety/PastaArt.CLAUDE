// ===== MODAL CUSTOMIZADO =====
// Funções para substituir alert() e confirm() nativos

// Função para mostrar modal de alerta (substitui alert())
function showAlert(message, title = 'Aviso', icon = 'fas fa-info-circle') {
    return new Promise((resolve) => {
        const trigger = document.activeElement;
        // Criar modal
        const modal = document.createElement('div');
        modal.className = 'custom-modal';
        modal.innerHTML = `
            <div class="custom-modal-content" role="dialog" aria-modal="true" aria-labelledby="custom-alert-title" aria-describedby="custom-alert-desc">
                <div class="custom-modal-header">
                    <i class="${icon}" aria-hidden="true"></i>
                    <h3 id="custom-alert-title">${title}</h3>
                </div>
                <div class="custom-modal-body">
                    <p id="custom-alert-desc">${message}</p>
                </div>
                <div class="custom-modal-footer">
                    <button class="btn modal-ok">OK</button>
                </div>
            </div>
        `;
        
        // Adicionar ao body
        document.body.appendChild(modal);
        
        // Mostrar modal e focar no botão OK
        setTimeout(() => {
            modal.classList.add('show');
            const okBtn = modal.querySelector('.modal-ok');
            if (okBtn) okBtn.focus();
        }, 10);

        // Trap de foco básico dentro do modal
        modal.addEventListener('keydown', (e) => {
            if (e.key !== 'Tab') return;
            const focusable = modal.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
            const first = focusable[0];
            const last = focusable[focusable.length - 1];
            if (e.shiftKey && document.activeElement === first) {
                e.preventDefault();
                last.focus();
            } else if (!e.shiftKey && document.activeElement === last) {
                e.preventDefault();
                first.focus();
            }
        });
        
        // Função para fechar
        function closeCustomModal(result) {
            const opened = document.querySelector('.custom-modal');
            if (!opened) return;
            opened.classList.remove('show');
            setTimeout(() => {
                if (opened.parentNode) opened.parentNode.removeChild(opened);
                resolve(result);
                // Restaurar foco ao elemento de origem
                if (trigger && typeof trigger.focus === 'function') {
                    setTimeout(() => trigger.focus(), 0);
                }
            }, 300);
        }
        modal.querySelector('.modal-ok').addEventListener('click', () => closeCustomModal(true));
        
        // Fechar com ESC
        const handleEsc = (e) => {
            if (e.key === 'Escape') {
                closeCustomModal(true);
                document.removeEventListener('keydown', handleEsc);
            }
        };
        document.addEventListener('keydown', handleEsc);
        
        // Fechar clicando fora
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeCustomModal(true);
            }
        });
    });
}

// Função para mostrar modal de confirmação (substitui confirm())
function showConfirm(message, title = 'Confirmação', icon = 'fas fa-question-circle') {
    return new Promise((resolve) => {
        const trigger = document.activeElement;
        // Criar modal
        const modal = document.createElement('div');
        modal.className = 'custom-modal';
        modal.innerHTML = `
            <div class="custom-modal-content" role="dialog" aria-modal="true" aria-labelledby="custom-confirm-title" aria-describedby="custom-confirm-desc">
                <div class="custom-modal-header">
                    <i class="${icon}" aria-hidden="true"></i>
                    <h3 id="custom-confirm-title">${title}</h3>
                </div>
                <div class="custom-modal-body">
                    <p id="custom-confirm-desc">${message}</p>
                </div>
                <div class="custom-modal-footer">
                    <button class="btn modal-cancel">Cancelar</button>
                    <button class="btn modal-ok">Confirmar</button>
                </div>
            </div>
        `;
        
        // Adicionar ao body
        document.body.appendChild(modal);
        
        // Mostrar modal e focar no botão Confirmar
        setTimeout(() => {
            modal.classList.add('show');
            const okBtn = modal.querySelector('.modal-ok');
            if (okBtn) okBtn.focus();
        }, 10);

        // Trap de foco básico dentro do modal
        modal.addEventListener('keydown', (e) => {
            if (e.key !== 'Tab') return;
            const focusable = modal.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
            const first = focusable[0];
            const last = focusable[focusable.length - 1];
            if (e.shiftKey && document.activeElement === first) {
                e.preventDefault();
                last.focus();
            } else if (!e.shiftKey && document.activeElement === last) {
                e.preventDefault();
                first.focus();
            }
        });
        
        // Função para fechar
        function closeConfirmModal(result) {
            const opened = document.querySelector('.custom-modal');
            if (!opened) return;
            opened.classList.remove('show');
            setTimeout(() => {
                if (opened.parentNode) opened.parentNode.removeChild(opened);
                resolve(result);
                // Restaurar foco ao elemento de origem
                if (trigger && typeof trigger.focus === 'function') {
                    setTimeout(() => trigger.focus(), 0);
                }
            }, 300);
        }
        modal.querySelector('.modal-cancel').addEventListener('click', () => closeConfirmModal(false));
        modal.querySelector('.modal-ok').addEventListener('click', () => closeConfirmModal(true));
        
        // Fechar com ESC (cancela)
        const handleEsc = (e) => {
            if (e.key === 'Escape') {
                closeConfirmModal(false);
                document.removeEventListener('keydown', handleEsc);
            }
        };
        document.addEventListener('keydown', handleEsc);
        
        // Fechar clicando fora (cancela)
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeConfirmModal(false);
            }
        });
    });
}

// Substituir funções nativas
window.alert = showAlert;
window.confirm = showConfirm;
