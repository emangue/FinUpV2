#!/usr/bin/env python3
"""
Regenera base_padroes em tabela temporária para validação
Permite comparar antes de aplicar mudanças
"""

import sys
sys.path.insert(0, 'app_dev/backend')

from app.core.database import SessionLocal, engine
from app.domains.patterns.models import BasePadroes
from app.domains.upload.processors.pattern_generator import gerar_base_padroes
from sqlalchemy import Table, Column, Integer, String, Float, DateTime, MetaData, text
from datetime import datetime
import json

def criar_tabela_temp():
    """Cria tabela temporária base_padroes_new"""
    metadata = MetaData()
    
    base_padroes_new = Table(
        'base_padroes_new', metadata,
        Column('id', Integer, primary_key=True),
        Column('user_id', Integer, nullable=False),
        Column('padrao_estabelecimento', String, nullable=False),
        Column('padrao_num', String, nullable=False),
        Column('contagem', Integer, nullable=False),
        Column('valor_medio', Float, nullable=False),
        Column('valor_min', Float, nullable=False),
        Column('valor_max', Float, nullable=False),
        Column('desvio_padrao', Float, nullable=False),
        Column('coef_variacao', Float, nullable=False),
        Column('percentual_consistencia', Integer, nullable=False),
        Column('confianca', String, nullable=False),
        Column('grupo_sugerido', String),
        Column('subgrupo_sugerido', String),
        Column('tipo_gasto_sugerido', String),
        Column('categoria_geral_sugerida', String),
        Column('faixa_valor', String),
        Column('segmentado', Integer, default=0),
        Column('exemplos', String),
        Column('data_criacao', DateTime, default=datetime.utcnow),
        Column('status', String, default='ativo')
    )
    
    # Drop se existir
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS base_padroes_new"))
        conn.commit()
    
    # Criar nova
    metadata.create_all(engine)
    print("✅ Tabela base_padroes_new criada")

def gerar_padroes_novos(user_id: int = 1):
    """Gera padrões e insere na tabela temporária"""
    db = SessionLocal()
    
    print(f"\n🔄 Gerando padrões para user_id={user_id}...")
    padroes = gerar_base_padroes(db, user_id)
    
    print(f"✅ {len(padroes)} padrões gerados")
    
    # Inserir na tabela temporária
    print("\n💾 Inserindo na tabela base_padroes_new...")
    with engine.connect() as conn:
        for padrao in padroes:
            conn.execute(text("""
                INSERT INTO base_padroes_new (
                    user_id, padrao_estabelecimento, padrao_num, contagem,
                    valor_medio, valor_min, valor_max, desvio_padrao, coef_variacao,
                    percentual_consistencia, confianca, grupo_sugerido, subgrupo_sugerido,
                    tipo_gasto_sugerido, categoria_geral_sugerida, faixa_valor, segmentado, exemplos, data_criacao, status
                ) VALUES (
                    :user_id, :padrao_estabelecimento, :padrao_num, :contagem,
                    :valor_medio, :valor_min, :valor_max, :desvio_padrao, :coef_variacao,
                    :percentual_consistencia, :confianca, :grupo_sugerido, :subgrupo_sugerido,
                    :tipo_gasto_sugerido, :categoria_geral_sugerida, :faixa_valor, :segmentado, :exemplos, :data_criacao, :status
                )
            """), {
                'user_id': user_id,
                'padrao_estabelecimento': padrao['padrao_estabelecimento'],
                'padrao_num': padrao['padrao_num'],
                'contagem': padrao['contagem'],
                'valor_medio': padrao['valor_medio'],
                'valor_min': padrao['valor_min'],
                'valor_max': padrao['valor_max'],
                'desvio_padrao': padrao['desvio_padrao'],
                'coef_variacao': padrao['coef_variacao'],
                'percentual_consistencia': padrao['percentual_consistencia'],
                'confianca': padrao['confianca'],
                'grupo_sugerido': padrao['grupo_sugerido'],
                'subgrupo_sugerido': padrao['subgrupo_sugerido'],
                'tipo_gasto_sugerido': padrao['tipo_gasto_sugerido'],
                'categoria_geral_sugerida': padrao.get('categoria_geral_sugerida', ''),
                'faixa_valor': padrao.get('faixa_valor'),
                'segmentado': padrao['segmentado'],
                'exemplos': padrao['exemplos'],
                'data_criacao': datetime.now(),
                'status': 'ativo'
            })
        conn.commit()
    
    print(f"✅ {len(padroes)} padrões inseridos em base_padroes_new")
    
    db.close()
    return padroes

def comparar_bases(user_id: int = 1):
    """Compara base antiga vs nova"""
    with engine.connect() as conn:
        # Contagens gerais
        result_old = conn.execute(text("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN confianca = 'alta' THEN 1 ELSE 0 END) as alta,
                   SUM(CASE WHEN confianca = 'media' THEN 1 ELSE 0 END) as media,
                   SUM(CASE WHEN confianca = 'baixa' THEN 1 ELSE 0 END) as baixa,
                   SUM(CASE WHEN segmentado = 1 THEN 1 ELSE 0 END) as segmentados,
                   SUM(CASE WHEN padrao_estabelecimento LIKE '% [%]%' THEN 1 ELSE 0 END) as brackets,
                   SUM(CASE WHEN padrao_estabelecimento LIKE '%|FAIXA:%' THEN 1 ELSE 0 END) as pipe_faixa
            FROM base_padroes
            WHERE user_id = :user_id
        """), {'user_id': user_id}).fetchone()
        
        result_new = conn.execute(text("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN confianca = 'alta' THEN 1 ELSE 0 END) as alta,
                   SUM(CASE WHEN confianca = 'media' THEN 1 ELSE 0 END) as media,
                   SUM(CASE WHEN confianca = 'baixa' THEN 1 ELSE 0 END) as baixa,
                   SUM(CASE WHEN segmentado = 1 THEN 1 ELSE 0 END) as segmentados,
                   SUM(CASE WHEN padrao_estabelecimento LIKE '% [%]%' THEN 1 ELSE 0 END) as brackets,
                   SUM(CASE WHEN padrao_estabelecimento LIKE '%|FAIXA:%' THEN 1 ELSE 0 END) as pipe_faixa
            FROM base_padroes_new
            WHERE user_id = :user_id
        """), {'user_id': user_id}).fetchone()
        
        print("\n" + "=" * 80)
        print("📊 COMPARAÇÃO: BASE ANTIGA vs BASE NOVA")
        print("=" * 80)
        
        print("\n📋 ESTATÍSTICAS GERAIS:")
        print(f"                          ANTIGA    NOVA      DIFERENÇA")
        print(f"  Total de padrões:       {result_old[0]:>6}    {result_new[0]:>6}    {result_new[0] - result_old[0]:+6}")
        print(f"  Confiança ALTA:         {result_old[1]:>6}    {result_new[1]:>6}    {result_new[1] - result_old[1]:+6}")
        print(f"  Confiança MÉDIA:        {result_old[2]:>6}    {result_new[2]:>6}    {result_new[2] - result_old[2]:+6}")
        print(f"  Confiança BAIXA:        {result_old[3]:>6}    {result_new[3]:>6}    {result_new[3] - result_old[3]:+6}")
        print(f"  Segmentados:            {result_old[4]:>6}    {result_new[4]:>6}    {result_new[4] - result_old[4]:+6}")
        
        print("\n📐 FORMATOS:")
        print(f"  Formato [ ] (correto):  {result_old[5]:>6}    {result_new[5]:>6}    {result_new[5] - result_old[5]:+6}")
        print(f"  Formato |FAIXA: (velho): {result_old[6]:>6}    {result_new[6]:>6}    {result_new[6] - result_old[6]:+6}")
        
        # Top 10 padrões mais frequentes - comparação
        print("\n📈 TOP 10 PADRÕES (por contagem):")
        print("\nBASE ANTIGA:")
        top_old = conn.execute(text("""
            SELECT padrao_estabelecimento, contagem, grupo_sugerido
            FROM base_padroes
            WHERE user_id = :user_id AND confianca = 'alta'
            ORDER BY contagem DESC
            LIMIT 10
        """), {'user_id': user_id}).fetchall()
        
        for i, row in enumerate(top_old, 1):
            print(f"  {i:2}. {row[0][:50]:50} | {row[1]:>4} | {row[2]}")
        
        print("\nBASE NOVA:")
        top_new = conn.execute(text("""
            SELECT padrao_estabelecimento, contagem, grupo_sugerido
            FROM base_padroes_new
            WHERE user_id = :user_id AND confianca = 'alta'
            ORDER BY contagem DESC
            LIMIT 10
        """), {'user_id': user_id}).fetchall()
        
        for i, row in enumerate(top_new, 1):
            print(f"  {i:2}. {row[0][:50]:50} | {row[1]:>4} | {row[2]}")
        
        # Padrões novos (que não existiam antes)
        novos = conn.execute(text("""
            SELECT n.padrao_estabelecimento, n.contagem
            FROM base_padroes_new n
            LEFT JOIN base_padroes o ON o.padrao_estabelecimento = n.padrao_estabelecimento 
                AND o.user_id = n.user_id
            WHERE n.user_id = :user_id AND o.id IS NULL
            ORDER BY n.contagem DESC
            LIMIT 5
        """), {'user_id': user_id}).fetchall()
        
        if novos:
            print("\n🆕 PADRÕES NOVOS (não existiam na base antiga):")
            for row in novos:
                print(f"  - {row[0]} ({row[1]} ocorrências)")
        
        # Padrões removidos (que existiam mas não estão mais)
        removidos = conn.execute(text("""
            SELECT o.padrao_estabelecimento, o.contagem
            FROM base_padroes o
            LEFT JOIN base_padroes_new n ON n.padrao_estabelecimento = o.padrao_estabelecimento 
                AND n.user_id = o.user_id
            WHERE o.user_id = :user_id AND n.id IS NULL
            ORDER BY o.contagem DESC
            LIMIT 5
        """), {'user_id': user_id}).fetchall()
        
        if removidos:
            print("\n🗑️  PADRÕES REMOVIDOS (não atendem mais critérios):")
            for row in removidos:
                print(f"  - {row[0]} ({row[1]} ocorrências)")
        
        print("\n" + "=" * 80)

def salvar_relatorio():
    """Salva relatório de comparação em arquivo"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"relatorio_padroes_{timestamp}.txt"
    
    # Redirecionar output para arquivo
    import subprocess
    subprocess.run(
        f"cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5 && python regenerate_patterns_preview.py > {filename}",
        shell=True
    )
    
    print(f"\n💾 Relatório salvo em: {filename}")

if __name__ == "__main__":
    print("🔄 REGENERAÇÃO DE BASE_PADROES - MODO PREVIEW")
    print("=" * 80)
    
    # 1. Criar tabela temporária
    print("\n1️⃣  Criando tabela temporária...")
    criar_tabela_temp()
    
    # 2. Gerar padrões novos
    print("\n2️⃣  Gerando padrões...")
    padroes = gerar_padroes_novos(user_id=1)
    
    # 3. Comparar bases
    print("\n3️⃣  Comparando bases...")
    comparar_bases(user_id=1)
    
    print("\n" + "=" * 80)
    print("✅ PREVIEW CONCLUÍDO")
    print("=" * 80)
    print("\n📋 PRÓXIMOS PASSOS:")
    print("  1. Analise o relatório acima")
    print("  2. Se aprovado, execute: python apply_new_patterns.py")
    print("  3. Para descartar: DROP TABLE base_padroes_new")
    print()
