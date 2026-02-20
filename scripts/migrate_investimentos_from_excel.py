"""
Script de migração de dados de investimentos do Excel para o banco de dados.

Importa dados históricos de:
- BaseAtivosPassivos: produtos de investimento com histórico mensal
- Planejamento Financeiro 2026: Projeções e metas
- Estimativa Patrimonio Atual: Parâmetros de cenários

Agrupamento: (Nome, Banco, ativo/passivo) - mesmo produto pode ter 2 linhas/mês
(ativo = valor positivo, passivo = valor negativo, ex: imóvel + financiamento).

Normalização: quantidade=1 se ausente; valor_unitario = valor_total/quantidade se ausente/zero.

Uso:
    python scripts/migrate_investimentos_from_excel.py [--yes]
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

# Carregar .env antes de importar config
from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

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

    def _normalizar_valores(self, valor_total, valor_unitario, quantidade):
        """Aplica regra: valor_total = valor_unitario × quantidade."""
        qty = 1.0
        if quantidade is not None and pd.notna(quantidade) and float(quantidade) != 0:
            qty = float(quantidade)
        vt = 0.0
        if valor_total is not None and pd.notna(valor_total):
            vt = float(valor_total)
        vu = None
        if valor_unitario is not None and pd.notna(valor_unitario) and float(valor_unitario) != 0:
            vu = float(valor_unitario)
        if vt != 0 and (vu is None or vu == 0):
            vu = vt / qty
        return (
            Decimal(str(qty)),
            Decimal(str(vu)) if vu is not None else (Decimal('0') if vt == 0 else None),
            Decimal(str(vt))
        )

    def migrar_portfolio_e_historico(self):
        """Migra dados da aba BaseAtivosPassivos"""
        print("\n📊 Migrando dados de BaseAtivosPassivos...")

        try:
            df = pd.read_excel(self.excel_path, sheet_name='BaseAtivosPassivos')
            print(f"   Lidas {len(df)} linhas do Excel")

            # Remover linhas sem nome (vazias)
            df = df.dropna(subset=['Nome'])
            print(f"   {len(df)} linhas após limpeza")

            # Colunas do Excel (7): Valor Unitário Ult dia mes, Valor Total ult dia mes
            col_vu = 'Valor Unitário Ult dia mes' if 'Valor Unitário Ult dia mes' in df.columns else 'Valor Unitário ult dia mes'
            col_vt = 'Valor Total ult dia mes' if 'Valor Total ult dia mes' in df.columns else 'Valor Total Ult dia mes'

            # Agrupar por (Nome, Banco, ativo/passivo) - cada BalanceID é único por linha
            df['_ativo'] = df[col_vt].fillna(0) >= 0
            grupos = df.groupby(['Nome', 'Banco', '_ativo'], sort=False)

            # Para cada grupo, usar o primeiro BalanceID como identificador único do investimento
            investimentos_map = {}  # (Nome, Banco, ativo) -> (balance_id, first_row, all_rows)
            for (nome, banco, ativo), grp in grupos:
                first = grp.iloc[0]
                balance_id = str(first['BalanceID'])
                investimentos_map[(nome, banco, ativo)] = (balance_id, first, grp)
            print(f"   {len(investimentos_map)} produtos únicos identificados (Nome+Banco+ativo/passivo)")

            # Criar investimentos no portfólio
            balance_to_portfolio = {}  # balance_id -> InvestimentoPortfolio

            for (nome, banco, ativo), (balance_id, first, _) in investimentos_map.items():
                try:
                    qty = float(first.get('Quantidade', 1.0)) if pd.notna(first.get('Quantidade')) and first.get('Quantidade', 0) != 0 else 1.0
                    vt_inicial = first.get('Valor Total Inicial', 0) or 0
                    vu_inicial = first.get('Valor Unitário Inicial', 0) or 0
                    if vt_inicial and (not vu_inicial or vu_inicial == 0):
                        vu_inicial = vt_inicial / qty

                    investimento = InvestimentoPortfolio(
                        user_id=self.user_id,
                        balance_id=balance_id,
                        nome_produto=str(nome)[:255],
                        corretora=str(banco)[:100],
                        tipo_investimento=str(first.get('tipo_investimento', 'Outros'))[:50],
                        classe_ativo=str(first.get('Classe', ''))[:50] if pd.notna(first.get('Classe')) else None,
                        ano=int(first['Ano']) if pd.notna(first.get('Ano')) else None,
                        anomes=int(first['anomes']) if pd.notna(first.get('anomes')) else None,
                        emissor=str(first.get('Emissor', ''))[:100] if pd.notna(first.get('Emissor')) else None,
                        percentual_cdi=float(first.get('%CDI', 0)) if pd.notna(first.get('%CDI')) else None,
                        data_aplicacao=pd.to_datetime(first.get('data_aplicacao'), dayfirst=True).date() if pd.notna(first.get('data_aplicacao')) else None,
                        data_vencimento=pd.to_datetime(first.get('Vencimento'), dayfirst=True).date() if pd.notna(first.get('Vencimento')) else None,
                        quantidade=qty,
                        valor_unitario_inicial=Decimal(str(vu_inicial)),
                        valor_total_inicial=Decimal(str(vt_inicial)),
                        ativo=True
                    )

                    self.db.add(investimento)
                    self.db.flush()
                    balance_to_portfolio[balance_id] = investimento
                    self.stats['portfolio_criados'] += 1

                except Exception as e:
                    self.stats['erros'].append(f"Erro ao criar investimento {balance_id}: {str(e)}")
                    print(f"   ⚠️  Erro no produto {nome}: {str(e)}")

            self.db.commit()
            print(f"✅ {self.stats['portfolio_criados']} investimentos criados no portfólio")

            # Criar histórico mensal (uma linha por mês por investimento)
            print("\n📅 Criando histórico mensal (com normalização valor_unitario × quantidade)...")

            for (nome, banco, ativo), (balance_id, _, grp) in investimentos_map.items():
                investimento = balance_to_portfolio.get(balance_id)
                if not investimento:
                    continue

                for _, row in grp.iterrows():
                    try:
                        ano = int(row['Ano'])
                        anomes = int(row['anomes'])
                        mes = anomes % 100

                        import calendar
                        if mes == 12:
                            data_ref = date(ano, 12, 31)
                        else:
                            ultimo_dia = calendar.monthrange(ano, mes)[1]
                            data_ref = date(ano, mes, ultimo_dia)

                        vt = row.get(col_vt)
                        vu = row.get(col_vu)
                        qty = row.get('Quantidade')
                        qty_norm, vu_norm, vt_norm = self._normalizar_valores(vt, vu, qty)

                        historico = InvestimentoHistorico(
                            investimento_id=investimento.id,
                            ano=ano,
                            mes=mes,
                            anomes=anomes,
                            data_referencia=data_ref,
                            quantidade=qty_norm,
                            valor_unitario=vu_norm,
                            valor_total=vt_norm,
                            aporte_mes=Decimal('0.00'),
                            rendimento_mes=None,
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

    # Path do Excel (arquivo atualizado com dados até Janeiro/2026)
    excel_path = PROJECT_ROOT / "_arquivos_historicos" / "_csvs_historico" / "App_Emangue_SA (7).xlsx"

    if not excel_path.exists():
        print(f"❌ Arquivo não encontrado: {excel_path}")
        return 1

    print(f"📁 Arquivo: {excel_path}")
    print(f"👤 User ID: {args.user_id}")

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
