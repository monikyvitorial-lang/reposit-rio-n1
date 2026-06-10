# 🤖 Amazon Promo Bot

Bot que busca promoções da Amazon Brasil automaticamente e envia para um canal/grupo do Telegram com seu link de afiliado.

---

## 📋 Pré-requisitos

- Python 3.10+
- Google Chrome instalado
- Conta no [Programa de Afiliados Amazon](https://associados.amazon.com.br/)
- Bot no Telegram (crie com [@BotFather](https://t.me/BotFather))

---

## ⚙️ Instalação

```bash
# 1. Clone ou extraia o projeto
cd amazon_promo_bot

# 2. Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure o .env
cp .env.example .env
nano .env   # edite com seus dados
```

---

## 🔑 Configuração

Edite o arquivo `.env`:

| Variável | Descrição | Exemplo |
|---|---|---|
| `TELEGRAM_TOKEN` | Token do bot (BotFather) | `123:AAFxxx` |
| `TELEGRAM_CHAT_ID` | Canal ou grupo | `@meucanal` |
| `AFFILIATE_TAG` | Sua tag de afiliado | `meutag-20` |
| `MIN_DISCOUNT_PERCENT` | Desconto mínimo (%) | `20` |
| `CHECK_INTERVAL_MINUTES` | Frequência de verificação | `60` |
| `SEARCH_KEYWORDS` | Produtos a monitorar | `smartphone,notebook` |

### Como obter o TELEGRAM_CHAT_ID

- **Canal público:** use `@nome_do_canal`
- **Canal/grupo privado:** adicione [@userinfobot](https://t.me/userinfobot) ao grupo e envie qualquer mensagem para obter o ID

### Como criar o bot Telegram

1. Abra o [@BotFather](https://t.me/BotFather)
2. Envie `/newbot` e siga as instruções
3. Copie o token gerado para `TELEGRAM_TOKEN`
4. Adicione o bot como **administrador** no seu canal

---

## ▶️ Execução

```bash
# Rodar manualmente
python bot.py

# Rodar em segundo plano (Linux)
nohup python bot.py > bot.log 2>&1 &

# Verificar logs
tail -f bot.log
```

### Com systemd (Linux - execução contínua)

Crie `/etc/systemd/system/amazon-bot.service`:

```ini
[Unit]
Description=Amazon Promo Bot
After=network.target

[Service]
User=seu_usuario
WorkingDirectory=/caminho/para/amazon_promo_bot
ExecStart=/caminho/para/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable amazon-bot
sudo systemctl start amazon-bot
sudo systemctl status amazon-bot
```

---

## 📁 Estrutura

```
amazon_promo_bot/
├── bot.py              # Ponto de entrada principal
├── config.py           # Configurações centralizadas
├── scraper.py          # Scraper Selenium (Amazon)
├── telegram_sender.py  # Envio de mensagens Telegram
├── requirements.txt    # Dependências Python
├── .env.example        # Template de configuração
└── bot.log             # Log gerado automaticamente
```

---

## ⚠️ Avisos

- **Use com moderação.** A Amazon pode bloquear IPs com excesso de requisições. O bot já inclui delays aleatórios para parecer mais humano.
- **Afiliados:** certifique-se de estar em conformidade com os [Termos do Programa de Afiliados Amazon](https://associados.amazon.com.br/help/operating/policies).
- **Respeite o robots.txt** do site.

---

## 🛠️ Solução de problemas

**Chrome não encontrado:**
```bash
# Ubuntu/Debian
sudo apt install google-chrome-stable
```

**Timeout no Selenium:** aumente o delay em `config.py` ou verifique sua conexão.

**Mensagem não enviada:** confirme que o bot é administrador do canal e que o `TELEGRAM_CHAT_ID` está correto.
