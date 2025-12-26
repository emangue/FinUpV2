// JavaScript principal

// Auto-hide alerts após 5 segundos
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert:not(.alert-info)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Confirmação antes de salvar
document.addEventListener('DOMContentLoaded', function() {
    const saveButtons = document.querySelectorAll('button[type="submit"]');
    saveButtons.forEach(button => {
        if (button.textContent.includes('Salvar') && button.textContent.includes('Journal')) {
            button.addEventListener('click', function(e) {
                const checkboxes = document.querySelectorAll('.origem-checkbox:checked');
                if (checkboxes.length === 0) {
                    e.preventDefault();
                    alert('Selecione pelo menos uma origem para salvar!');
                    return false;
                }
                
                if (!confirm(`Você está prestes a salvar ${checkboxes.length} origem(ns) no banco de dados. Confirma?`)) {
                    e.preventDefault();
                    return false;
                }
            });
        }
    });
});

// Validação de formulários
(function() {
    'use strict';
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
})();
