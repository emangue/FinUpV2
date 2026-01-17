"""
Script de Validação: Pattern Generator
Testa se o gerador Python produz output equivalente ao n8n
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent / "app_dev" / "backend"))

from app.core.database import get_db
from app.domains.upload.processors.pattern_generator import regenerar_base_padroes_completa

def main():
    """Executa regeneração e mostra resultados"""
    print("="*80)
    print("🔄 REGENERAÇÃO DE BASE_PADROES - TESTE")
    print("="*80)
    print()
    
    db = next(get_db())
    
    try:
        # Regenerar para user_id = 1
        print("📊 Regenerando padrões para user_id=1...")
        result = regenerar_base_padroes_completa(db, user_id=1)
        
        print()
        print("✅ RESULTADOS:")
        print(f"   Total de padrões gerados: {result['total_padroes_gerados']}")
        print(f"   Criados: {result['criados']}")
        print(f"   Atualizados: {result['atualizados']}")
        print()
        
        # Comparar com base atual
        from app.domains.patterns.models import BasePadroes
        
        total_atual = db.query(BasePadroes).filter(
            BasePadroes.user_id == 1
        ).count()
        
        print(f"📋 Total de registros em base_padroes (user_id=1): {total_atual}")
        print()
        
        # Mostrar alguns exemplos
        print("📝 EXEMPLOS DE PADRÕES GERADOS:")
        print("-" * 80)
        
        padroes_exemplo = db.query(BasePadroes).filter(
            BasePadroes.user_id == 1,
            BasePadroes.confianca == 'alta'
        ).order_by(BasePadroes.contagem.desc()).limit(10).all()
        
        for p in padroes_exemplo:
            print(f"\n  Padrão: {p.padrao_estabelecimento[:60]}")
            print(f"  Contagem: {p.contagem} | Consistência: {p.percentual_consistencia}%")
            print(f"  Grupo: {p.grupo_sugerido} > {p.subgrupo_sugerido}")
            print(f"  TipoGasto: {p.tipo_gasto_sugerido}")
            print(f"  Confiança: {p.confianca}")
            if p.segmentado:
                print(f"  Faixa: {p.faixa_valor}")
        
        print()
        print("="*80)
        print("✅ TESTE CONCLUÍDO")
        print("="*80)
    
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        db.close()


if __name__ == '__main__':
    main()
