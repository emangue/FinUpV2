// JavaScript principal

// Auto-hide alerts após 5 segundos (exceto validações de integridade)
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert:not(.alert-info)');
    alerts.forEach(alert => {
        // Não ocultar alerts com validação de integridade ou extrato
        const isValidacao = alert.textContent.includes('Validação de Integridade') || 
                           alert.textContent.includes('Extrato validado');
        
        if (!isValidacao) {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        }
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
// Editor de Cores dos Grupos
function abrirEditorCores() {
    // Carrega grupos e cores via AJAX
    fetch('/admin/api/grupos-cores')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const container = document.getElementById('listaGruposCores');
                container.innerHTML = '';
                
                data.grupos.forEach(grupo => {
                    const col = document.createElement('div');
                    col.className = 'col-md-6';
                    col.innerHTML = `
                        <div class="grupo-cor-item">
                            <label class="form-label fw-bold">
                                <i class="fas ${grupo.icone}"></i> ${grupo.nome}
                            </label>
                            <div class="input-group">
                                <input type="color" 
                                       class="form-control form-control-color" 
                                       id="cor-${grupo.id}" 
                                       value="${grupo.cor}" 
                                       title="Escolha a cor">
                                <input type="text" 
                                       class="form-control" 
                                       value="${grupo.cor}" 
                                       readonly 
                                       style="max-width: 100px;">
                            </div>
                        </div>
                    `;
                    container.appendChild(col);
                    
                    // Sincroniza color picker com texto
                    const colorInput = col.querySelector('input[type="color"]');
                    const textInput = col.querySelector('input[type="text"]');
                    colorInput.addEventListener('input', function() {
                        textInput.value = this.value;
                    });
                });
                
                // Abre modal
                const modal = new bootstrap.Modal(document.getElementById('modalEditorCores'));
                modal.show();
            } else {
                alert('Erro ao carregar grupos: ' + (data.error || 'Erro desconhecido'));
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao conectar com o servidor.');
        });
}

function salvarCores() {
    // Coleta cores alteradas
    const cores = {};
    document.querySelectorAll('input[type="color"]').forEach(input => {
        const grupoId = input.id.replace('cor-', '');
        cores[grupoId] = input.value;
    });
    
    // Envia via AJAX
    fetch('/admin/api/grupos-cores', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ cores: cores })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Fecha modal
            const modalElement = document.getElementById('modalEditorCores');
            const modal = bootstrap.Modal.getInstance(modalElement);
            modal.hide();
            
            // Recarrega página para atualizar gráficos
            window.location.reload();
        } else {
            alert('Erro ao salvar cores: ' + (data.error || 'Erro desconhecido'));
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao conectar com o servidor.');
    });
}

// Editor de Cores dos Grupos
function abrirEditorCores() {
    fetch('/admin/api/grupos-cores')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const container = document.getElementById('listaGruposCores');
                container.innerHTML = '';
                
                data.grupos.forEach(grupo => {
                    const col = document.createElement('div');
                    col.className = 'col-md-6';
                    col.innerHTML = `
                        <div class="grupo-cor-item">
                            <label class="form-label fw-bold">
                                <i class="fas ${grupo.icone}"></i> ${grupo.nome}
                            </label>
                            <div class="input-group">
                                <input type="color" 
                                       class="form-control form-control-color" 
                                       id="cor-${grupo.id}" 
                                       value="${grupo.cor}" 
                                       title="Escolha a cor">
                                <input type="text" 
                                       class="form-control" 
                                       value="${grupo.cor}" 
                                       readonly 
                                       style="max-width: 100px;">
                            </div>
                        </div>
                    `;
                    container.appendChild(col);
                    
                    const colorInput = col.querySelector('input[type="color"]');
                    const textInput = col.querySelector('input[type="text"]');
                    colorInput.addEventListener('input', function() {
                        textInput.value = this.value;
                    });
                });
                
                const modal = new bootstrap.Modal(document.getElementById('modalEditorCores'));
                modal.show();
            } else {
                alert('Erro ao carregar grupos: ' + (data.error || 'Erro desconhecido'));
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao conectar com o servidor.');
        });
}

function salvarCores() {
    const cores = {};
    document.querySelectorAll('input[type="color"]').forEach(input => {
        const grupoId = input.id.replace('cor-', '');
        cores[grupoId] = input.value;
    });
    
    fetch('/admin/api/grupos-cores', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ cores: cores })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const modalElement = document.getElementById('modalEditorCores');
            const modal = bootstrap.Modal.getInstance(modalElement);
            modal.hide();
            window.location.reload();
        } else {
            alert('Erro ao salvar cores: ' + (data.error || 'Erro desconhecido'));
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao conectar com o servidor.');
    });
}

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