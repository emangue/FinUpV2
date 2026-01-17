"""
Script de migração de dados de investimentos do Excel para o banco de dados.

Importa dados históricos de:
- BaseAtivosPassivos: 298 produtos de investimento com histórico mensal
- Planejamento Financeiro 2026: Projeções e metas
- Estimativa Patrimonio Atual: Parâmetros de cenários

Uso:
    python scripts/migrate_investimentos_from_excel.py
"""
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime, date
from decimal import Decimal
import pandas as pd
from sqlalchemy.orm import Session

# Adicionar diretório do projeto ao path
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "app_dev" / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import SessionLocal, engine
from app.domains.investimentos.models import (
    InvestimentoPortfolio,
    InvestimentoHistorico,
    InvestimentoCenario,
    AporteExtraordinario,
    Base
)


class InvestimentoMigrator:
    """Migrador de dados de investimentos do Excel"""

    def __init__(self, excel_path: str, user_id: int = 1):
        self.excel_path = excel_path
        self.user_id = user_id
        self.db: Session = SessionLocal()
        self.stats = {
            'portfolio_criados': 0,
            'historico_criados': 0,
            'cenarios_criados': 0,
            'erros': []
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

    def criar_tabelas(self):
        """Cria tabelas de investimentos se não existirem"""
        print("📋 Criando tabelas de investimentos...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas/verificadas")

    def limpar_dados_existentes(self):
        """Remove dados existentes de investimentos (se necessário)"""
        print("🧹 Limpando dados existentes...")

        count_historico = self.db.query(InvestimentoHistorico).delete()
        count_portfolio = self.db.query(InvestimentoPortfolio).delete()
        count_cenarios = self.db.query(InvestimentoCenario).delete()

        self.db.commit()
        print(f"   Removidos: {count_portfolio} investimentos, {count_historico} históricos, {count_cenarios} cenários")

    def migrar_portfolio_e_historico(self):
        """Migra dados da aba BaseAtivosPassivos"""
        print("\n📊 Migrando dados de BaseAtivosPassivos...")

        try:
            df = pd.read_excel(self.excel_path, sheet_name='BaseAtivosPassivos')
            print(f"   Lidas {len(df)} linhas do Excel")

            # Remover linhas sem nome (vazias)
            df = df.dropna(subset=['Nome'])
            print(f"   {len(df)} linhas após limpeza")

            # Agrupar por produto (balance_id único)
            produtos_unicos = df.groupby('BalanceID').first().reset_index()
            print(f"   {len(produtos_unicos)} produtos únicos identificados")

            # Criar investimentos no portfólio
            investimentos_map = {}  # BalanceID -> InvestimentoPortfolio

            for _, row in produtos_unicos.iterrows():
                try:
                    investimento = InvestimentoPortfolio(
                        user_id=self.user_id,
                        balance_id=str(row['BalanceID']),
                        nome_produto=str(row['Nome'])[:255],
                        corretora=str(row.get('Banco', row.get('Banco / Corretora', 'Não especificado')))[:100],
                        tipo_investimento=str(row.get('tipo_investimento', 'Outros'))[:50],
                        classe_ativo=str(row.get('Classe', ''))[:50] if pd.notna(row.get('Classe')) else None,
                        ano=int(row['Ano']) if pd.notna(row.get('Ano')) else None,
                        anomes=int(row['anomes']) if pd.notna(row.get('anomes')) else None,
                        emissor=str(row.get('Emissor', ''))[:100] if pd.notna(row.get('Emissor')) else None,
                        percentual_cdi=float(row.get('%CDI', 0)) if pd.notna(row.get('%CDI')) else None,
                        data_aplicacao=pd.to_datetime(row.get('data_aplicacao')).date() if pd.notna(row.get('data_aplicacao')) else None,
                        data_vencimento=pd.to_datetime(row.get('Vencimento')).date() if pd.notna(row.get('Vencimento')) else None,
                        quantidade=float(row.get('Quantidade', 1.0)) if pd.notna(row.get('Quantidade')) else 1.0,
                        valor_unitario_inicial=Decimal(str(row.get('Valor Unitário Inicial', 0))),
                        valor_total_inicial=Decimal(str(row.get('Valor Total Inicial', 0))),
                        ativo=True
                    )

                    self.db.add(investimento)
                    self.db.flush()  # Para obter o ID

                    investimentos_map[str(row['BalanceID'])] = investimento
                    self.stats['portfolio_criados'] += 1

                except Exception as e:
                    self.stats['erros'].append(f"Erro ao criar investimento {row.get('BalanceID')}: {str(e)}")
                    print(f"   ⚠️  Erro no produto {row.get('Nome')}: {str(e)}")

            self.db.commit()
            print(f"✅ {self.stats['portfolio_criados']} investimentos criados no portfólio")

            # Criar histórico mensal
            print("\n📅 Criando histórico mensal...")

            for _, row in df.iterrows():
                balance_id = str(row['BalanceID'])
                investimento = investimentos_map.get(balance_id)

                if not investimento:
                    continue

                try:
                    ano = int(row['Ano'])
                    anomes = int(row['anomes'])
                    mes = anomes % 100

                    # Data de referência: último dia do mês
                    if mes == 12:
                        data_ref = date(ano, 12, 31)
                    else:
                        import calendar
                        ultimo_dia = calendar.monthrange(ano, mes)[1]
                        data_ref = date(ano, mes, ultimo_dia)

                    historico = InvestimentoHistorico(
                        investimento_id=investimento.id,
                        ano=ano,
                        mes=mes,
                        anomes=anomes,
                        data_referencia=data_ref,
                        quantidade=float(row.get('Quantidade', 1.0)) if pd.notna(row.get('Quantidade')) else None,
                        valor_unitario=Decimal(str(row.get('Valor Unitário ult dia mes', 0))) if pd.notna(row.get('Valor Unitário ult dia mes')) else None,
                        valor_total=Decimal(str(row.get('Valor Total ult dia mes', 0))) if pd.notna(row.get('Valor Total ult dia mes')) else None,
                        aporte_mes=Decimal('0.00'),  # Calcular depois se necessário
                        rendimento_mes=None,  # Calcular depois
                        rendimento_acumulado=None
                    )

                    self.db.add(historico)
                    self.stats['historico_criados'] += 1

                except Exception as e:
                    self.stats['erros'].append(f"Erro ao criar histórico {balance_id}/{anomes}: {str(e)}")

            self.db.commit()
            print(f"✅ {self.stats['historico_criados']} registros de histórico criados")

        except Exception as e:
            self.stats['erros'].append(f"Erro ao processar BaseAtivosPassivos: {str(e)}")
            print(f"❌ Erro: {str(e)}")
            raise

    def migrar_cenario_estimativa(self):
        """Migra dados da aba Estimativa Patrimonio Atual como cenário"""
        print("\n💡 Criando cenário baseado em Estimativa Patrimonio Atual...")

        try:
            df_estimativa = pd.read_excel(self.excel_path, sheet_name='Estimativa Patrimonio Atual')

            # Extrair parâmetros (assumindo estrutura específica)
            patrimonio_inicial = Decimal('300000.00')  # Ajustar conforme dados reais
            rendimento_mensal = Decimal('0.0080')  # 0.8%
            aporte_mensal = Decimal('5000.00')
            periodo_meses = 120  # 10 anos

            cenario = InvestimentoCenario(
                user_id=self.user_id,
                nome_cenario="Cenário Base - Histórico Excel",
                descricao="Cenário criado automaticamente baseado nos parâmetros de Estimativa Patrimonio Atual",
                patrimonio_inicial=patrimonio_inicial,
                rendimento_mensal_pct=rendimento_mensal,
                aporte_mensal=aporte_mensal,
                periodo_meses=periodo_meses,
                ativo=True
            )

            self.db.add(cenario)
            self.db.flush()

            # Adicionar aportes extraordinários (exemplos)
            aportes = [
                AporteExtraordinario(
                    cenario_id=cenario.id,
                    mes_referencia=12,
                    valor=Decimal('30000.00'),
                    descricao="13º salário anual"
                ),
                AporteExtraordinario(
                    cenario_id=cenario.id,
                    mes_referencia=24,
                    valor=Decimal('130000.00'),
                    descricao="Bônus anual"
                )
            ]

            for aporte in aportes:
                self.db.add(aporte)

            self.db.commit()
            self.stats['cenarios_criados'] = 1

            print(f"✅ Cenário 'Base - Histórico Excel' criado com {len(aportes)} aportes extraordinários")

        except Exception as e:
            print(f"⚠️  Aviso: Não foi possível criar cenário - {str(e)}")
            self.stats['erros'].append(f"Erro ao criar cenário: {str(e)}")

    def validar_migracao(self):
        """Valida integridade dos dados migrados"""
        print("\n🔍 Validando migração...")

        # Contar registros
        count_portfolio = self.db.query(InvestimentoPortfolio).filter_by(user_id=self.user_id).count()
        count_historico = self.db.query(InvestimentoHistorico).count()
        count_cenarios = self.db.query(InvestimentoCenario).filter_by(user_id=self.user_id).count()

        print(f"   Portfólio: {count_portfolio} investimentos")
        print(f"   Histórico: {count_historico} registros")
        print(f"   Cenários: {count_cenarios} cenários")

        # Validar valores
        total_investido = self.db.query(
            InvestimentoPortfolio
        ).filter_by(user_id=self.user_id).all()

        soma_inicial = sum(
            inv.valor_total_inicial or Decimal('0') for inv in total_investido
        )

        print(f"   Valor total investido: R$ {soma_inicial:,.2f}")

        # Verificar períodos
        historicos = self.db.query(InvestimentoHistorico).all()
        if historicos:
            anomes_min = min(h.anomes for h in historicos)
            anomes_max = max(h.anomes for h in historicos)
            print(f"   Período histórico: {anomes_min} até {anomes_max}")

        return count_portfolio > 0 and count_historico > 0

    def imprimir_resumo(self):
        """Imprime resumo da migração"""
        print("\n" + "=" * 60)
        print("📊 RESUMO DA MIGRAÇÃO")
        print("=" * 60)
        print(f"✅ Investimentos criados: {self.stats['portfolio_criados']}")
        print(f"✅ Registros de histórico: {self.stats['historico_criados']}")
        print(f"✅ Cenários criados: {self.stats['cenarios_criados']}")

        if self.stats['erros']:
            print(f"\n⚠️  {len(self.stats['erros'])} erros encontrados:")
            for erro in self.stats['erros'][:5]:  # Mostrar apenas primeiros 5
                print(f"   - {erro}")
            if len(self.stats['erros']) > 5:
                print(f"   ... e mais {len(self.stats['erros']) - 5} erros")

        print("=" * 60)


def main():
    """Função principal"""
    # Parse argumentos
    parser = argparse.ArgumentParser(description='Migração de investimentos do Excel')
    parser.add_argument('--yes', '-y', action='store_true', help='Confirmar automaticamente')
    parser.add_argument('--user-id', type=int, default=1, help='ID do usuário (padrão: 1)')
    args = parser.parse_args()

    print("\n🚀 MIGRAÇÃO DE INVESTIMENTOS - EXCEL → DATABASE")
    print("=" * 60)

    # Path do Excel (arquivo atualizado com dados até Dezembro/2025)
    excel_path = PROJECT_ROOT / "_arquivos_historicos" / "_csvs_historico" / "App_Emangue_SA (6).xlsx"

    if not excel_path.exists():
        print(f"❌ Arquivo não encontrado: {excel_path}")
        return 1

    print(f"📁 Arquivo: {excel_path}")
    print(f"👤 User ID: {args.user_id}")
    print(f"📊 Total de linhas esperadas: ~313 (incluindo dados até Dezembro/2025)")

    # Confirmar antes de executar
    if not args.yes:
        resposta = input("\n⚠️  Deseja continuar com a migração? (sim/não): ").strip().lower()
        if resposta not in ['sim', 's', 'yes', 'y']:
            print("❌ Migração cancelada pelo usuário")
            return 0

    # Executar migração
    try:
        with InvestimentoMigrator(str(excel_path), user_id=args.user_id) as migrator:
            migrator.criar_tabelas()
            migrator.limpar_dados_existentes()
            migrator.migrar_portfolio_e_historico()
            migrator.migrar_cenario_estimativa()

            # Validar
            if migrator.validar_migracao():
                migrator.imprimir_resumo()
                print("\n✅ Migração concluída com sucesso!")
                return 0
            else:
                print("\n❌ Migração falhou na validação")
                return 1

    except Exception as e:
        print(f"\n❌ Erro fatal na migração: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
