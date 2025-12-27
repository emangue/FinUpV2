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
// Toggle de Status Dashboard nas transações
document.addEventListener('DOMContentLoaded', function() {
    const toggles = document.querySelectorAll('.toggle-dashboard');
    
    toggles.forEach(toggle => {
        toggle.addEventListener('change', function() {
            const idTransacao = this.getAttribute('data-id');
            const ignorar = !this.checked; // Invertido: checked = considerado (não ignorar)
            const label = this.nextElementSibling;
            const badge = label.querySelector('.badge');
            
            // Feedback visual imediato
            this.disabled = true;
            
            // Requisição AJAX
            fetch(`/dashboard/toggle_dashboard/${idTransacao}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ ignorar: ignorar })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Atualiza badge
                    if (ignorar) {
                        badge.className = 'badge bg-secondary';
                        badge.innerHTML = '<i class="fas fa-eye-slash"></i> Ignorado';
                    } else {
                        badge.className = 'badge bg-success';
                        badge.innerHTML = '<i class="fas fa-check"></i> Considerado';
                    }
                    
                    console.log(`✅ Status atualizado: ${ignorar ? 'Ignorado' : 'Considerado'}`);
                } else {
                    // Reverte o switch em caso de erro
                    this.checked = !this.checked;
                    alert('Erro ao atualizar status: ' + (data.error || 'Erro desconhecido'));
                }
            })
            .catch(error => {
                // Reverte o switch em caso de erro
                this.checked = !this.checked;
                console.error('Erro na requisição:', error);
                alert('Erro ao conectar com o servidor. Tente novamente.');
            })
            .finally(() => {
                // Reabilita o switch
                this.disabled = false;
            });
        });
    });
});