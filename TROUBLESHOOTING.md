# 🔍 Troubleshooting - Bot Amazon

## Problema: 0 promoções enviadas

Se o bot rodou mas não enviou nenhuma promoção, pode ser uma desses problemas:

### 1️⃣ **Desconto mínimo muito alto**
- **MIN_DISCOUNT_PERCENT** está em 20%
- Amazon pode não ter muitos produtos com 20%+ de desconto no momento
- **Solução:** Reduzir para 10% ou 5%

### 2️⃣ **Scraper não conseguindo fazer scraping**
- Amazon bloqueou as requisições
- Seletores CSS mudaram
- Erro silencioso no scraping
- **Solução:** Usar o workflow DEBUG

### 3️⃣ **Palavras-chave muito específicas**
- SEARCH_KEYWORDS podem não ter resultados
- **Solução:** Adicionar mais palavras-chave comuns

## 🧪 Como Testar

### Opção 1: Workflow DEBUG (Recomendado)

1. Vá para **Actions** no GitHub
2. Selecione **"Amazon Bot - TESTE (Debug)"**
3. Clique em **"Run workflow"**
4. Este workflow:
   - ✅ Reduz MIN_DISCOUNT_PERCENT para 5%
   - ✅ Ativa FORCE_SEND_ALL=true (envia TUDO que encontrar)
   - ✅ Mostra logs detalhados

### Opção 2: Testar Localmente

```bash
# No seu computador
export FORCE_SEND_ALL=true
export MIN_DISCOUNT_PERCENT=5
export HEADLESS=true
python bot.py
```

## 📊 Interpretando os Logs

### Se vir isto:
```
✅ {N} promoções encontradas
```
= Bot encontrou produtos ✓

### Se vir isto:
```
🤖 Iniciando busca de promoções...
  → {N} cards encontrados em /deals
```
= Scraper funcionando ✓

### Se vir isto:
```
✅ X promoções encontradas
  → Ignorando (desconto abaixo do mínimo)
```
= Problema é desconto muito alto (reduzir MIN_DISCOUNT_PERCENT)

### Se vir isto:
```
✅ 0 promoções encontradas
```
= Problema pode ser:
- ❌ Seletores CSS obsoletos (Amazon mudou layout)
- ❌ Bloqueio pela Amazon
- ❌ Erro silencioso no scraping

## 🛠️ Soluções Rápidas

### Problema: Muitos produtos ignorados por desconto baixo

**Arquivo:** `.env` ou workflow

Altere:
```
MIN_DISCOUNT_PERCENT=20
```

Para:
```
MIN_DISCOUNT_PERCENT=10
```

### Problema: Quer enviar TUDO para testar

**Arquivo:** `.env` ou workflow

Altere:
```
FORCE_SEND_ALL=false
```

Para:
```
FORCE_SEND_ALL=true
```

### Problema: Amazon está bloqueando

**Possíveis causas:**
1. Muitas requisições rápido (aumentar DELAY_BETWEEN_MESSAGES)
2. User-Agent desatualizado
3. Bot detectado como automático

**Solução temporária:**
```
DELAY_BETWEEN_MESSAGES=5  # Aumentar de 3 para 5 segundos
```

## 📝 Próximos Passos

1. **Execute o workflow DEBUG** (Amazon Bot - TESTE)
2. **Verifique os logs** para ver quantos produtos foram encontrados
3. **Se encontrou mas não enviou:** Reduzir MIN_DISCOUNT_PERCENT
4. **Se não encontrou nada:** Problema de scraping (verificar seletores CSS)

---

## ❓ Dúvidas Frequentes

**P: Por que nenhum produto é encontrado?**
A: Amazon pode ter bloqueado ou os seletores CSS mudaram. Use o workflow DEBUG para mais detalhes.

**P: Posso aumentar o volume de produtos?**
A: Sim! Altere `MAX_PRODUCTS_PER_RUN` de 10 para 20+

**P: Posso mudar os horários do cron?**
A: Sim! Edite `.github/workflows/amazon-bot.yml` e altere a linha:
```yaml
- cron: '0 9 * * *'  # Altere 09 para outro horário
```
