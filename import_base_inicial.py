"""
Script para importar base inicial do base_dados_geral.xlsx
⚠️ ATENÇÃO: Este script modifica MÚLTIPLAS bases de dados
🛡️ RECOMENDADO: Use import_marcacoes_seguro.py apenas para BaseMarcacoesGastos
"""
import pandas as pd
from app.models import JournalEntry, BasePadrao, BaseMarcacao, init_db, get_db_session
from datetime import datetime


def confirmar_importacao_completa():
    """Solicita confirmação para importação de todas as bases"""
    print("⚠️ " + "="*60)
    print("🔔 ATENÇÃO: IMPORTAÇÃO COMPLETA DE MÚLTIPLAS BASES")
    print("="*65)
    print("📊 Este script importará TODAS as seguintes bases:")
    print("   1. BaseMarcacoesGastos → base_marcacoes")
    print("   2. Journal Entries → journal_entries")
    print("   3. Base_Padroes → base_padroes")
    print()
    print("🛡️  RECOMENDAÇÃO:")
    print("   • Para apenas BaseMarcacoesGastos: use import_marcacoes_seguro.py")
    print("   • Para importação completa: continue aqui")
    print()
    print("⚡ Esta operação pode SOBRESCREVER dados existentes!")
    
    resposta = input("\n❓ Deseja REALMENTE importar TODAS as bases? [s/N]: ").strip().lower()
    return resposta in ['s', 'sim', 'y', 'yes']


def confirmar_base_individual(nome_base, descricao):
    """Confirma importação de uma base específica"""
    print(f"\n📊 Importar {nome_base}?")
    print(f"   Descrição: {descricao}")
    
    resposta = input(f"   Confirmar importação de {nome_base}? [S/n]: ").strip().lower()
    return resposta in ['', 's', 'sim', 'y', 'yes']


def importar_base_inicial():
    """Importa dados do arquivo base_dados_geral.xlsx"""
    
    print("🚀 Iniciando importação da base inicial...\n")
    
    # Confirmação inicial
    if not confirmar_importacao_completa():
        print("\n❌ Importação cancelada pelo usuário")
        print("💡 Para importar apenas BaseMarcacoesGastos, use: python import_marcacoes_seguro.py")
        return
    
    # Inicializa banco
    init_db()
    
    arquivo = 'base_dados_geral.xlsx'
    
    try:
        # Lê arquivo Excel
        print(f"📖 Lendo arquivo: {arquivo}")
        xls = pd.ExcelFile(arquivo, engine='openpyxl')
        print(f"✓ Abas encontradas: {xls.sheet_names}\n")
        
        session = get_db_session()
        
        # 1. Importar BaseMarcacoesGastos
        if 'BaseMarcacoesGastos' in xls.sheet_names:
            if confirmar_base_individual("BaseMarcacoesGastos", "Marcações essenciais para dropdowns"):
                print("📊 Importando BaseMarcacoesGastos...")
                df_marcacoes = pd.read_excel(xls, 'BaseMarcacoesGastos')
                
                count = 0
                for _, row in df_marcacoes.iterrows():
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
                        count += 1
                
                session.commit()
                print(f"✓ {count} marcações importadas\n")
            else:
                print("⏭️  BaseMarcacoesGastos ignorada\n")
        
        # 2. Importar Journal Entries
        if 'Journal Entries' in xls.sheet_names:
            if confirmar_base_individual("Journal Entries", "Transações históricas - PODE SOBRESCREVER dados existentes"):
                print("📊 Importando Journal Entries...")
                df_journal = pd.read_excel(xls, 'Journal Entries')
            
            count = 0
            for _, row in df_journal.iterrows():
                id_transacao = str(row.get('IdTransacao', '')).strip()
                if not id_transacao or id_transacao == 'nan':
                    continue
                
                # Verifica se já existe
                existe = session.query(JournalEntry).filter_by(
                    IdTransacao=id_transacao
                ).first()
                
                if not existe:
                    # Tratamento de valores (aceita vírgula como separador decimal)
                    valor_raw = row.get('Valor', 0)
                    if pd.notna(valor_raw):
                        valor_str = str(valor_raw).replace(',', '.')
                        try:
                            valor = float(valor_str)
                        except:
                            valor = 0
                    else:
                        valor = 0
                    
                    valor_pos_raw = row.get('ValorPositivo', 0)
                    if pd.notna(valor_pos_raw):
                        valor_pos_str = str(valor_pos_raw).replace(',', '.')
                        try:
                            valor_positivo = float(valor_pos_str)
                        except:
                            valor_positivo = 0
                    else:
                        valor_positivo = 0
                    
                    entry = JournalEntry(
                        IdTransacao=id_transacao,
                        Data=str(row.get('Data', '')),
                        Estabelecimento=str(row.get('Estabelecimento', '')),
                        Valor=valor,
                        ValorPositivo=valor_positivo,
                        TipoTransacao=str(row.get('TipoTransacao', '')) if pd.notna(row.get('TipoTransacao')) else None,
                        TipoTransacaoAjuste=str(row.get('TipoTransacaoAjuste', '')) if pd.notna(row.get('TipoTransacaoAjuste')) else None,
                        TipoGasto=str(row.get('TipoGasto', '')) if pd.notna(row.get('TipoGasto')) else None,
                        GRUPO=str(row.get('GRUPO', '')) if pd.notna(row.get('GRUPO')) else None,
                        SUBGRUPO=str(row.get('SUBGRUPO', '')) if pd.notna(row.get('SUBGRUPO')) else None,
                        Ano=int(row.get('ano', 0)) if pd.notna(row.get('ano')) else None,
                        DT_Fatura=str(row.get('DT_FATURA', '')) if pd.notna(row.get('DT_FATURA')) else None,
                        NomeTitular=str(row.get('Portador', '')) if pd.notna(row.get('Portador')) else None,
                        origem=str(row.get('nome_TC', '')) if pd.notna(row.get('nome_TC')) else 'Desconhecido',
                        MarcacaoIA=str(row.get('MarcacaoIA', '')) if pd.notna(row.get('MarcacaoIA')) else None,
                        ValidarIA=str(row.get('ValidarIA', '')) if pd.notna(row.get('ValidarIA')) else None,
                        created_at=datetime.utcnow()
                    )
                    session.add(entry)
                    count += 1
                    
                    if count % 100 == 0:
                        session.commit()
                        print(f"  ... {count} registros processados")
            
            session.commit()
            print(f"✓ {count} transações importadas\n")
        else:
            print("⏭️  Journal Entries ignorada\n")
        
        # 3. Importar Base_Padroes (se existir)
        if 'Base_Padroes' in xls.sheet_names:
            if confirmar_base_individual("Base_Padroes", "Padrões de classificação aprendidos - PODE SOBRESCREVER dados existentes"):
                print("📊 Importando Base_Padroes...")
                df_padroes = pd.read_excel(xls, 'Base_Padroes')
            
            count = 0
            for _, row in df_padroes.iterrows():
                padrao_estab = str(row.get('padrao_estabelecimento', '')).strip()
                if not padrao_estab or padrao_estab == 'nan':
                    continue
                
                # Verifica se já existe
                existe = session.query(BasePadrao).filter_by(
                    padrao_estabelecimento=padrao_estab
                ).first()
                
                if not existe:
                    padrao = BasePadrao(
                        padrao_estabelecimento=padrao_estab,
                        padrao_num=str(row.get('padrao_num', '')),
                        contagem=int(row.get('contagem', 0)) if pd.notna(row.get('contagem')) else 0,
                        valor_medio=float(row.get('valor_medio', 0)) if pd.notna(row.get('valor_medio')) else 0,
                        percentual_consistencia=int(row.get('percentual_consistencia', 0)) if pd.notna(row.get('percentual_consistencia')) else 0,
                        confianca=str(row.get('confianca', 'baixa')),
                        grupo_sugerido=str(row.get('grupo_sugerido', '')) if pd.notna(row.get('grupo_sugerido')) else None,
                        subgrupo_sugerido=str(row.get('subgrupo_sugerido', '')) if pd.notna(row.get('subgrupo_sugerido')) else None,
                        tipo_gasto_sugerido=str(row.get('tipo_gasto_sugerido', '')) if pd.notna(row.get('tipo_gasto_sugerido')) else None,
                        exemplos=str(row.get('exemplos', '')) if pd.notna(row.get('exemplos')) else None,
                        status=str(row.get('status', 'ativo')),
                        data_criacao=datetime.utcnow()
                    )
                    session.add(padrao)
                    count += 1
            
            session.commit()
            print(f"✓ {count} padrões importados\n")
        else:
            print("⏭️  Base_Padroes ignorada\n")
        
        session.close()
        
        print("✅ Importação concluída com sucesso!")
        print("\n� RECOMENDAÇÃO para futuras importações:")
        print("   • Para BaseMarcacoesGastos apenas: python import_marcacoes_seguro.py")
        print("   • Para importação completa: python import_base_inicial.py")
        print("\n�🚀 Para iniciar a aplicação, execute:")
        print("   source venv/bin/activate")
        print("   python app.py")
        
    except FileNotFoundError:
        print(f"❌ Erro: Arquivo '{arquivo}' não encontrado")
        print("   Certifique-se de que o arquivo base_dados_geral.xlsx está no diretório do projeto")
    except Exception as e:
        print(f"❌ Erro durante importação: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    importar_base_inicial()
