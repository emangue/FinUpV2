import sqlite3

conn = sqlite3.connect('database/financas_dev.db')
c = conn.cursor()

items = [
    ('budget-geral', 'Meta Geral', 'P', None, 61, 'budget', '/budget'),
    ('budget-simples', 'Meta Simples', 'P', None, 62, 'budget', '/budget/simples'),
    ('budget-detalhada', 'Meta Detalhada', 'P', None, 63, 'budget', '/budget/detalhada'),
    ('budget-planning', 'Planejamento', 'D', None, 64, 'budget', '/budget/planning'),
    ('budget-configuracoes', 'Configurações Orçamento', 'P', None, 65, 'budget', '/budget/configuracoes'),
    ('reports', 'Relatórios', 'A', 'BarChart3', 70, None, '/reports'),
    ('reports-monthly', 'Mensal', 'A', None, 71, 'reports', '/reports/monthly'),
    ('reports-yearly', 'Anual', 'A', None, 72, 'reports', '/reports/yearly'),
    ('reports-categories', 'Categorias', 'A', None, 73, 'reports', '/reports/categories'),
    ('settings-profile', 'Perfil', 'P', None, 74, 'settings', '/settings/profile'),
    ('settings-cartoes', 'Gestão de Cartões', 'P', None, 75, 'settings', '/settings/cartoes'),
    ('settings-categorias', 'Gestão de Categorias', 'P', None, 76, 'settings', '/settings/categorias'),
    ('settings-grupos', 'Gestão de Grupos', 'P', None, 77, 'settings', '/settings/grupos'),
    ('settings-exclusoes', 'Regras de Exclusão', 'P', None, 78, 'settings', '/settings/exclusoes'),
    ('admin', 'Administração', 'A', 'Shield', 80, None, '/admin'),
    ('admin-contas', 'Contas', 'A', None, 81, 'admin', '/settings/admin'),
    ('admin-bancos', 'Gestão de Bancos', 'A', None, 83, 'admin', '/settings/bancos'),
    ('admin-backup', 'Backup', 'A', None, 84, 'admin', '/settings/backup')
]

inserted = 0
for item in items:
    c.execute('INSERT OR IGNORE INTO screen_visibility (screen_key, screen_name, status, icon, display_order, parent_key, url) VALUES (?, ?, ?, ?, ?, ?, ?)', item)
    if c.rowcount > 0:
        inserted += 1

conn.commit()
print(f'✅ Inseridos {inserted} novos registros!')

# Mostrar total
c.execute('SELECT COUNT(*) FROM screen_visibility')
total = c.fetchone()[0]
print(f'📊 Total de telas: {total}')

conn.close()
