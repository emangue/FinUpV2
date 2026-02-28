"""
Dataset demo para modo exploração — ~90 transações em 3 meses.
Cobre os principais grupos: Receita, Despesa, Lazer, Alimentação, etc.
"""
from typing import List, Tuple

# Formato: (estabelecimento, valor, grupo, subgrupo, mes 1-3)
DEMO_SEED: List[Tuple[str, float, str, str, int]] = [
    # Receita
    ("Salário Empresa", 5000.00, "Salário", "Salário", 1),
    ("Salário Empresa", 5000.00, "Salário", "Salário", 2),
    ("Salário Empresa", 5000.00, "Salário", "Salário", 3),
    ("Freelance", 1200.00, "Salário", "Salário", 2),
    # Alimentação
    ("Supermercado Extra", -450.00, "Alimentação", "Supermercado", 1),
    ("Supermercado Pão de Açúcar", -380.00, "Alimentação", "Supermercado", 2),
    ("Supermercado Pão de Açúcar", -420.00, "Alimentação", "Supermercado", 3),
    ("iFood", -85.50, "Alimentação", "Delivery", 1),
    ("Uber Eats", -92.00, "Alimentação", "Delivery", 2),
    ("Restaurante", -120.00, "Alimentação", "Saídas", 1),
    ("Padaria", -45.00, "Alimentação", "Café da Manhã", 1),
    ("Padaria", -38.00, "Alimentação", "Café da Manhã", 2),
    ("Padaria", -52.00, "Alimentação", "Café da Manhã", 3),
    # Lazer
    ("Netflix", -55.90, "Lazer", "Assinaturas", 1),
    ("Netflix", -55.90, "Lazer", "Assinaturas", 2),
    ("Netflix", -55.90, "Lazer", "Assinaturas", 3),
    ("Spotify", -21.90, "Lazer", "Spotify", 1),
    ("Spotify", -21.90, "Lazer", "Spotify", 2),
    ("Spotify", -21.90, "Lazer", "Spotify", 3),
    ("Cinema", -78.00, "Lazer", "Cinema", 1),
    ("Parque", -25.00, "Lazer", "Saídas", 2),
    # Moradia
    ("Aluguel", -1500.00, "Moradia e Serviços", "Aluguel", 1),
    ("Aluguel", -1500.00, "Moradia e Serviços", "Aluguel", 2),
    ("Aluguel", -1500.00, "Moradia e Serviços", "Aluguel", 3),
    ("Conta de Luz", -180.00, "Moradia e Serviços", "Energia", 1),
    ("Conta de Luz", -165.00, "Moradia e Serviços", "Energia", 2),
    ("Conta de Água", -85.00, "Moradia e Serviços", "Outros", 1),
    ("Internet", -99.90, "Moradia e Serviços", "Internet", 1),
    ("Internet", -99.90, "Moradia e Serviços", "Internet", 2),
    ("Internet", -99.90, "Moradia e Serviços", "Internet", 3),
    # Transporte
    ("Uber", -45.00, "Transporte", "Uber", 1),
    ("Uber", -38.00, "Transporte", "Uber", 2),
    ("99", -32.00, "Transporte", "Uber", 1),
    ("Metrô", -120.00, "Transporte", "Bilhete Unico", 1),
    ("Metrô", -120.00, "Transporte", "Bilhete Unico", 2),
    ("Metrô", -120.00, "Transporte", "Bilhete Unico", 3),
    # Carro
    ("Posto Shell", -280.00, "Carro", "Abastecimento", 1),
    ("Posto Shell", -260.00, "Carro", "Abastecimento", 2),
    ("Posto Shell", -290.00, "Carro", "Abastecimento", 3),
    ("Estacionamento", -45.00, "Carro", "Estacionamento", 1),
    ("Estacionamento", -38.00, "Carro", "Estacionamento", 2),
    # Saúde
    ("Farmácia", -85.00, "Saúde", "Farmácia", 1),
    ("Farmácia", -62.00, "Saúde", "Farmácia", 2),
    ("Consulta Médica", -200.00, "Saúde", "Dentista", 1),
    ("Plano de Saúde", -450.00, "Saúde", "Terapia", 1),
    ("Plano de Saúde", -450.00, "Saúde", "Terapia", 2),
    ("Plano de Saúde", -450.00, "Saúde", "Terapia", 3),
    # Compras e Tecnologia
    ("Amazon", -120.00, "Compras e Tecnologia", "Amazon", 1),
    ("Mercado Livre", -89.90, "Compras e Tecnologia", "MeLi+", 2),
    ("Apple Store", -45.00, "Compras e Tecnologia", "Eletrônicos", 1),
    # Educação
    ("Curso Udemy", -79.90, "Educação", "Preply", 1),
    ("Livraria", -65.00, "Educação", "Preply", 2),
    # Investimentos
    ("Aplicação CDB", -500.00, "Investimentos", "XP", 1),
    ("Aplicação CDB", -500.00, "Investimentos", "XP", 2),
    ("Aplicação CDB", -500.00, "Investimentos", "XP", 3),
    ("Tesouro Direto", -1000.00, "Investimentos", "Santander", 1),
    ("Tesouro Direto", -1000.00, "Investimentos", "Santander", 2),
    # Transferência
    ("Transferência PIX", -200.00, "Transferência Entre Contas", "Mercado Pago", 1),
    ("Transferência PIX", 200.00, "Transferência Entre Contas", "Nubank", 1),
    ("Transferência PIX", -150.00, "Transferência Entre Contas", "Mercado Pago", 2),
    ("Transferência PIX", 150.00, "Transferência Entre Contas", "Nubank", 2),
    # Outros
    ("Doação", -50.00, "Doações", "CP", 1),
    ("Bar", -85.00, "Lazer", "Saídas", 2),
    ("Academia", -120.00, "Saúde", "Gympass", 1),
    ("Academia", -120.00, "Saúde", "Gympass", 2),
    ("Academia", -120.00, "Saúde", "Gympass", 3),
    ("Assinatura", -29.90, "Outros", "Outros", 1),
    ("Assinatura", -29.90, "Outros", "Outros", 2),
    ("Assinatura", -29.90, "Outros", "Outros", 3),
]

# Mapeamento grupo -> (tipo_gasto, categoria_geral) — fallback se não achar no template
GRUPO_FALLBACK = {
    "Salário": ("Receita", "Receita"),
    "Alimentação": ("Ajustável", "Despesa"),
    "Lazer": ("Ajustável", "Despesa"),
    "Moradia e Serviços": ("Ajustável", "Despesa"),
    "Transporte": ("Ajustável", "Despesa"),
    "Carro": ("Ajustável", "Despesa"),
    "Saúde": ("Fixo", "Despesa"),
    "Compras e Tecnologia": ("Ajustável", "Despesa"),
    "Educação": ("Fixo", "Despesa"),
    "Investimentos": ("Investimentos", "Investimentos"),
    "Transferência Entre Contas": ("Transferência", "Transferência"),
    "Doações": ("Ajustável", "Despesa"),
    "Outros": ("Ajustável", "Despesa"),
}
