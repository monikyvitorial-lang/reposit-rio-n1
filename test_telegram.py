"""
Script para testar envio ao Telegram sem fazer scraping
"""

import logging
from telegram_sender import TelegramSender
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Validar configs
if not Config.TELEGRAM_TOKEN or not Config.TELEGRAM_CHAT_ID:
    logger.error("❌ TELEGRAM_TOKEN e TELEGRAM_CHAT_ID são obrigatórios!")
    exit(1)

logger.info("📤 Testando conexão com Telegram...")

sender = TelegramSender(Config.TELEGRAM_TOKEN, Config.TELEGRAM_CHAT_ID)

# Teste 1: Mensagem simples
logger.info("\n🧪 Teste 1: Enviando mensagem simples...")
msg = "✅ <b>Bot testado com sucesso!</b>\nO Telegram está funcionando corretamente."
if sender._send_message(msg):
    logger.info("✅ Mensagem simples enviada com sucesso!")
else:
    logger.error("❌ Falha ao enviar mensagem simples")

# Teste 2: Mensagem com produto
logger.info("\n🧪 Teste 2: Enviando produto teste...")
test_product = {
    "title": "AirFryer Multilaser 4.5L Preta",
    "price": 189.90,
    "original_price": 299.90,
    "discount": 37,
    "url": "https://www.amazon.com.br/AirFryer-Multilaser-4-5L-Preta/dp/B099XYK8Z9",
    "affiliate_url": "https://www.amazon.com.br/AirFryer-Multilaser-4-5L-Preta/dp/B099XYK8Z9?tag=mv2334-20"
}

if sender.send_deal(test_product):
    logger.info("✅ Produto teste enviado com sucesso!")
else:
    logger.error("❌ Falha ao enviar produto teste")

logger.info("\n" + "="*50)
logger.info("🎉 Testes concluídos!")
logger.info("="*50)
