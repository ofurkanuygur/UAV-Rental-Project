// Utility Functions
const formatDate = (date) => {
    return new Date(date).toLocaleDateString('tr-TR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};

const formatStatus = (status) => {
    const statusMap = {
        'PENDING': 'Beklemede',
        'IN_PROGRESS': 'Devam Ediyor',
        'COMPLETED': 'Tamamlandı',
        'FAILED': 'Başarısız',
        'BLOCKED': 'Engellendi'
    };
    return statusMap[status] || status;
};

// Toast Notifications
const showToast = (message, type = 'info') => {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    const container = document.getElementById('toast-container') || (() => {
        const div = document.createElement('div');
        div.id = 'toast-container';
        div.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(div);
        return div;
    })();
    
    container.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
};

// Form Validations
const validateForm = (form) => {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('is-invalid');
            
            if (!field.nextElementSibling?.classList.contains('invalid-feedback')) {
                const feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                feedback.textContent = 'Bu alan zorunludur.';
                field.parentNode.insertBefore(feedback, field.nextSibling);
            }
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
};

// API Helpers
const api = {
    get: async (url) => {
        try {
            const response = await fetch(url, {
                headers: {
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            if (!response.ok) throw new Error('Network response was not ok');
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            showToast('Bir hata oluştu: ' + error.message, 'danger');
            throw error;
        }
    },
    
    post: async (url, data) => {
        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error('Network response was not ok');
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            showToast('Bir hata oluştu: ' + error.message, 'danger');
            throw error;
        }
    }
};

// UI Enhancements
document.addEventListener('DOMContentLoaded', () => {
    // Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Form validations
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', (e) => {
            if (!validateForm(form)) {
                e.preventDefault();
                e.stopPropagation();
            }
        });
    });
    
    // Dynamic form fields
    document.querySelectorAll('[data-dynamic-form]').forEach(container => {
        const addButton = container.querySelector('[data-add-field]');
        const template = container.querySelector('template');
        
        if (addButton && template) {
            addButton.addEventListener('click', () => {
                const clone = template.content.cloneNode(true);
                const removeButton = clone.querySelector('[data-remove-field]');
                
                if (removeButton) {
                    removeButton.addEventListener('click', (e) => {
                        e.preventDefault();
                        removeButton.closest('.dynamic-field').remove();
                    });
                }
                
                container.insertBefore(clone, addButton);
            });
        }
    });
    
    // Confirm dialogs
    document.querySelectorAll('[data-confirm]').forEach(button => {
        button.addEventListener('click', (e) => {
            if (!confirm(button.dataset.confirm)) {
                e.preventDefault();
                e.stopPropagation();
            }
        });
    });
});

// Export utilities for use in other scripts
window.utils = {
    formatDate,
    formatStatus,
    showToast,
    validateForm,
    api
};