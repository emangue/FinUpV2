# 🎨 Como Adicionar Logos Reais das Empresas

## Passo 1: Salvar as Imagens

Salve os logos das empresas (PNG ou JPG) **nesta pasta** (`static/logos/`) com os nomes sugeridos abaixo:

### Transporte
- `uber.png` → Para transações com "UBER"
- `99.png` → Para transações com "99"

### Food Delivery
- `ifood.png` → Para transações com "IFOOD"
- `rappi.png` → Para transações com "RAPPI"
- `ubereats.png` → Para transações com "UBER EATS"

### Restaurantes
- `zdeli.png` → Para transações com "Z DELI"
- `outback.png` → Para transações com "OUTBACK"
- `mcdonalds.png` → Para transações com "MCDONALDS"
- `burgerking.png` → Para transações com "BURGER KING"

### Streaming
- `netflix.png` → Para transações com "NETFLIX"
- `spotify.png` → Para transações com "SPOTIFY"
- `youtube.png` → Para transações com "YOUTUBE"
- `prime.png` → Para transações com "AMAZON PRIME"
- `disney.png` → Para transações com "DISNEY"

### Bancos
- `nubank.png` → Para transações com "NUBANK"
- `inter.png` → Para transações com "INTER"
- `itau.png` → Para transações com "ITAU"
- `bradesco.png` → Para transações com "BRADESCO"

### E-commerce
- `amazon.png` → Para transações com "AMAZON"
- `mercadolivre.png` → Para transações com "MERCADO LIVRE"
- `magalu.png` → Para transações com "MAGAZINE LUIZA"
- `shopee.png` → Para transações com "SHOPEE"

### Supermercados
- `carrefour.png` → Para transações com "CARREFOUR"
- `paodeacucar.png` → Para transações com "PAO DE ACUCAR"

## Passo 2: Executar o Script

Após salvar as imagens, execute no terminal:

```bash
python3 scripts/add_real_logos.py
```

O script irá:
1. Detectar os novos arquivos PNG/JPG
2. Atualizar o banco de dados
3. Substituir os emojis pelos logos reais

## Passo 3: Testar

Acesse a aplicação e veja os logos reais nas transações!

## ✨ Dica Pro

Você também pode fazer upload manual pela interface web:
1. Acesse **Admin → Logos**
2. Clique em "Novo Logo"
3. Faça upload da imagem
4. Preencha o nome de busca (ex: "uber", "ifood")

## 📝 Notas

- Arquivos SVG também são suportados
- Tamanho máximo: 2MB por arquivo
- Formato circular automático
- Busca case-insensitive (UBER = uber = Uber)
