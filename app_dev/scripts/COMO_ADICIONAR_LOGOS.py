"""
GUIA RÁPIDO: Como adicionar logos reais

1. BAIXE os logos das empresas:
   - Uber: https://logos-world.net/uber-logo/ (fundo preto)
   - iFood: https://logodownload.org/ifood-logo/ (fundo vermelho)
   - Z Deli: https://zdeli.com/assets/logo (site oficial)
   - Outros: busque no Google "[empresa] logo png transparent"

2. SALVE as imagens na pasta:
   /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/static/logos/

3. RENOMEIE os arquivos conforme o padrão:
   - uber.png (não Uber_Logo.png)
   - ifood.png (não iFood-logo.png)
   - zdeli.png (não z-deli.png)
   
4. EXECUTE o script:
   python3 scripts/add_real_logos.py

OU use a interface web:
   - Acesse http://localhost:5001/admin/logos
   - Clique em "Novo Logo"
   - Faça upload e preencha os campos
   
IMPORTANTE:
- O nome de busca deve corresponder ao que aparece nas transações
- Exemplo: Se na transação está "UBER EATS", use busca "uber eats"
- A busca é case-insensitive e parcial (UBER123 encontra "uber")
"""
print(__doc__)
