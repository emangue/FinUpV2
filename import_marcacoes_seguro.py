"""
Script SEGURO para importar APENAS BaseMarcacoesGastos com validação interativa
Criado para proteger as bases de dados contra alterações não autorizadas
"""
import pandas as pd
from app.models import BaseMarcacao, init_db, get_db_session
import sqlite3


def verificar_estado_atual():
    """Verifica o estado atual da tabela base_marcacoes"""
    try:
        conn = sqlite3.connect('financas.db')
        cursor = conn.cursor()
        
        # Verifica se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='base_marcacoes';")
        table_exists = cursor.fetchone()
        
        if table_exists:
            # Conta registros
            cursor.execute('SELECT COUNT(*) FROM base_marcacoes;')
            count = cursor.fetchone()[0]
            print(f"📊 Tabela base_marcacoes: {count} registros existentes")
            
            if count > 0:
                # Mostra primeiros registros
                cursor.execute('SELECT * FROM base_marcacoes LIMIT 5;')
                records = cursor.fetchall()
                print("🔍 Primeiros registros atuais:")
                for record in records:
                    print(f"   • {record[1]} → {record[2]} ({record[3]})")
                return count
            else:
                print("⚠️  Tabela base_marcacoes está VAZIA")
                return 0
        else:
            print("❌ Tabela base_marcacoes não existe")
            return 0
            
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
        return -1
    finally:
        if 'conn' in locals():
            conn.close()


def preview_dados_arquivo():
    """Mostra preview dos dados que serão importados"""
    arquivo = 'base_dados_geral.xlsx'
    
    try:
        print(f"\n📖 Verificando arquivo: {arquivo}")
        xls = pd.ExcelFile(arquivo, engine='openpyxl')
        
        if 'BaseMarcacoesGastos' not in xls.sheet_names:
            print("❌ Aba 'BaseMarcacoesGastos' não encontrada no arquivo!")
            print(f"   Abas disponíveis: {xls.sheet_names}")
            return None
        
        df = pd.read_excel(xls, 'BaseMarcacoesGastos')
        
        # Remove linhas vazias
        df_clean = df.dropna(subset=['GRUPO'])
        total_registros = len(df_clean)
        
        print(f"✓ Encontrados {total_registros} registros na aba BaseMarcacoesGastos")
        print("\n🔍 Preview dos primeiros registros a serem importados:")
        
        for i, (_, row) in enumerate(df_clean.head(8).iterrows()):
            grupo = str(row.get('GRUPO', '')).strip()
            subgrupo = str(row.get('SUBGRUPO', '')).strip() 
            tipo_gasto = str(row.get('TipoGasto', '')).strip()
            print(f"   {i+1}. {grupo} → {subgrupo} ({tipo_gasto})")
        
        if total_registros > 8:
            print(f"   ... e mais {total_registros - 8} registros")
            
        return df_clean
        
    except FileNotFoundError:
        print(f"❌ Erro: Arquivo '{arquivo}' não encontrado")
        return None
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        return None


def confirmar_operacao(registros_atuais, novos_registros):
    """Solicita confirmação interativa do usuário"""
    print(f"\n{'='*60}")
    print("🔔 CONFIRMAÇÃO NECESSÁRIA")
    print(f"{'='*60}")
    print(f"📊 Estado atual: {registros_atuais} registros na base")
    print(f"📥 Novos dados: {len(novos_registros) if novos_registros is not None else 0} registros para importar")
    print(f"⚠️  AÇÃO: Importar BaseMarcacoesGastos (essencial para dropdowns)")
    
    if registros_atuais > 0:
        print(f"⚡ NOTA: Registros duplicados serão ignorados automaticamente")
    
    print(f"\n🎯 Esta operação é SEGURA e RECOMENDADA")
    print(f"   • Foca apenas na base BaseMarcacoesGastos")
    print(f"   • Essencial para funcionamento dos dropdowns")
    print(f"   • Não altera outras bases sem permissão")
    
    resposta = input(f"\n✅ Confirma a importação? [S/n]: ").strip().lower()
    
    return resposta in ['', 's', 'sim', 'y', 'yes']


def importar_marcacoes_seguro():
    """Importa APENAS BaseMarcacoesGastos com validação"""
    
    print("🛡️  SCRIPT SEGURO - IMPORTAÇÃO BASEMARCACOESGASTOS")
    print("="*60)
    
    # 1. Verificar estado atual
    registros_atuais = verificar_estado_atual()
    if registros_atuais == -1:
        return
    
    # 2. Preview dos dados do arquivo
    novos_dados = preview_dados_arquivo()
    if novos_dados is None:
        return
    
    # 3. Solicitar confirmação
    if not confirmar_operacao(registros_atuais, novos_dados):
        print("\n❌ Operação cancelada pelo usuário")
        return
    
    # 4. Executar importação
    print(f"\n🚀 Iniciando importação SEGURA...")
    
    # Inicializa banco se necessário
    init_db()
    
    try:
        session = get_db_session()
        count_novos = 0
        count_existentes = 0
        
        print(f"📊 Processando {len(novos_dados)} registros...")
        
        for _, row in novos_dados.iterrows():
            grupo = str(row.get('GRUPO', '')).strip()
            subgrupo = str(row.get('SUBGRUPO', '')).strip()
            tipo_gasto = str(row.get('TipoGasto', '')).strip()
            
            if not grupo:
                continue
            
            # Verifica se já existe
            existe = session.query(BaseMarcacao).filter_by(
                GRUPO=grupo,
                SUBGRUPO=subgrupo,
                TipoGasto=tipo_gasto
            ).first()
            
            if not existe:
                marcacao = BaseMarcacao(
                    GRUPO=grupo,
                    SUBGRUPO=subgrupo,
                    TipoGasto=tipo_gasto
                )
                session.add(marcacao)
                count_novos += 1
                
                if count_novos % 10 == 0:
                    print(f"  ... {count_novos} registros adicionados")
            else:
                count_existentes += 1
        
        session.commit()
        session.close()
        
        print(f"\n✅ IMPORTAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"   • {count_novos} novos registros adicionados")
        print(f"   • {count_existentes} registros já existentes (ignorados)")
        
        # Verificação final
        print(f"\n🔍 VERIFICAÇÃO FINAL:")
        verificar_estado_atual()
        
        print(f"\n🎯 PRÓXIMOS PASSOS:")
        print(f"   1. Teste os dropdowns na tela de validação")
        print(f"   2. Verifique se grupo/subgrupo aparecem corretamente")
        print(f"   3. Execute: python app.py")
        
    except Exception as e:
        print(f"❌ Erro durante importação: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    importar_marcacoes_seguro()