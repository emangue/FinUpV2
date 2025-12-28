# Solicitação de Tarefas - 27/12/2025

## 1. Revisão do arquivo de bugs
- Revisar o topo do arquivo BUGS.md, ajustando o conceito para o correto.

## 2. Revisão do arquivo de estrutura do projeto
- Revisar o topo do arquivo ESTRUTURA_PROJETO.md, ajustando o conceito para o correto.

## 3. Comando para religar o servidor
Comando padrão para religar o servidor:

```bash
/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/venv/bin/python run.py
```
## 7. Validação do extrato BTG
As bases do Mercado Pago são os arquivos account_statement. Realizar a mesma validação feita com esses arquivos para o extrato do BTG, mantendo o texto e o padrão de validação semelhantes.

## 4. Automação de religamento do servidor
- Após cada ajuste, religar automaticamente o servidor.
- Documentar essa obrigação no arquivo de obrigações da IA.

## 5. Avaliação dos arquivos account_statement
- Verificar se os arquivos account_statement... estão preparados para serem reconhecidos como extrato.
- Avaliar se as validações feitas para fatura do Itaú funcionam para esses arquivos ou se precisam de ajustes.
- Se necessário, mapear o arquivo para extrair dados e validações corretamente.

## 6. Validação de duplicidade no extrato_itau
- Verificar por que transações já presentes na base não estão sendo consideradas duplicadas.
- Validar e ajustar o hash para garantir que operações duplicadas sejam reconhecidas corretamente.
