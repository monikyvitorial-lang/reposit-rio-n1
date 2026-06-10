"""
Amazon Promotions Bot - Selenium + Telegram
Scrapes deals from Amazon and sends to Telegram with affiliate links
"""

import time
import logging
import sys
import io
from datetime import datetime
from scraper import AmazonScraper
from telegram_sender import TelegramSender
from config import Config

# Configure logging handlers with UTF-8 encoding to avoid
# UnicodeEncodeError on Windows consoles when logging emoji
file_handler = logging.FileHandler("bot.log", encoding="utf-8")
# Wrap stdout in a TextIOWrapper with UTF-8 encoding for the stream handler
stdout_stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
stream_handler = logging.StreamHandler(stdout_stream)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[file_handler, stream_handler]
)
logger = logging.getLogger(__name__)


def run_bot():
    logger.info("🤖 Iniciando busca de promoções...")
    
    scraper = AmazonScraper()
    sender = TelegramSender(Config.TELEGRAM_TOKEN, Config.TELEGRAM_CHAT_ID)
    
    try:
        products = scraper.get_deals()
        logger.info(f"✅ {len(products)} promoções encontradas")

        # Log product details for debugging
        for i, p in enumerate(products, 1):
            logger.info(f"  [{i}] {p.get('title','-')[:60]} | desconto={p.get('discount')} | preço={p.get('price')} | url={p.get('url')}")

        sent = 0
        for product in products:
            # Build affiliate URL early for logging and sending
            affiliate_url = build_affiliate_url(product.get("url", ""))
            product["affiliate_url"] = affiliate_url

            discount = product.get("discount", 0)
            within_range = Config.MIN_DISCOUNT_PERCENT <= discount <= Config.MAX_DISCOUNT_PERCENT
            should_send = Config.FORCE_SEND_ALL or within_range
            if not should_send:
                reason = (
                    "desconto abaixo do mínimo"
                    if discount < Config.MIN_DISCOUNT_PERCENT
                    else "desconto acima do máximo"
                )
                logger.info(
                    f"  → Ignorando ({reason}): {product.get('title','-')[:60]} | {discount}"
                )
                continue

            success = sender.send_deal(product)
            if success:
                sent += 1
                time.sleep(Config.DELAY_BETWEEN_MESSAGES)

        logger.info(f"📤 {sent} promoções enviadas ao Telegram")

    except Exception as e:
        logger.error(f"Erro no bot: {e}")
    finally:
        scraper.close()


def build_affiliate_url(url: str) -> str:
    """Append affiliate tag to Amazon URL"""
    tag = Config.AFFILIATE_TAG
    if not tag:
        return url
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}tag={tag}"


def main():
    # Validate required configs
    if not Config.TELEGRAM_TOKEN or not Config.TELEGRAM_CHAT_ID:
        logger.error("❌ TELEGRAM_TOKEN e TELEGRAM_CHAT_ID são obrigatórios!")
        logger.error("Defina as variáveis de ambiente ou adicione ao arquivo .env")
        sys.exit(1)
    
    logger.info("=" * 50)
    logger.info("🚀 Amazon Promo Bot iniciado")
    logger.info(f"⏰ Intervalo: {Config.CHECK_INTERVAL_MINUTES} minutos")
    logger.info("=" * 50)

    # Send a single startup message to verify Telegram connection
    try:
        sender = TelegramSender(Config.TELEGRAM_TOKEN, Config.TELEGRAM_CHAT_ID)
        sender.send_startup_message()
    except Exception:
        logger.warning("Não foi possível enviar mensagem de inicialização ao Telegram")

    # Run once and exit (suitable for GitHub Actions / cron jobs)
    run_bot()
    logger.info("Execução única concluída; saindo.")


if __name__ == "__main__":
    main()
