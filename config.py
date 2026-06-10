"""
Configuration - edit this file or use environment variables
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ─── Telegram ────────────────────────────────────────────────
    # Bot token from @BotFather
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")

    # Channel or group ID (e.g. "@meucanal" or "-1001234567890")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")

    # ─── Amazon Affiliate ────────────────────────────────────────
    # Your affiliate tag (e.g. "meutag-20")
    AFFILIATE_TAG: str = os.getenv("AFFILIATE_TAG", "")

    # ─── Scraping ────────────────────────────────────────────────
    # Minimum discount % to send (0 = send everything)
    MIN_DISCOUNT_PERCENT: int = int(os.getenv("MIN_DISCOUNT_PERCENT", "20"))

    # Maximum discount % to send (useful to keep range narrow)
    MAX_DISCOUNT_PERCENT: int = int(os.getenv("MAX_DISCOUNT_PERCENT", "30"))

    # How often to check for new deals (minutes)
    CHECK_INTERVAL_MINUTES: int = int(os.getenv("CHECK_INTERVAL_MINUTES", "60"))

    # Seconds to wait between Telegram messages (avoid flood)
    DELAY_BETWEEN_MESSAGES: float = float(os.getenv("DELAY_BETWEEN_MESSAGES", "3"))

    # Max products to send per run
    MAX_PRODUCTS_PER_RUN: int = int(os.getenv("MAX_PRODUCTS_PER_RUN", "10"))

    # ─── Selenium ────────────────────────────────────────────────
    HEADLESS: bool = os.getenv("HEADLESS", "true").lower() == "true"
    USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    # Amazon pages to scrape (can add more)
    AMAZON_URLS: list = [
        "https://www.amazon.com.br/deals",
        "https://www.amazon.com.br/s?i=electronics&rh=p_n_pct-off-with-tax%3A20-100%25&sort=price-asc-rank",
    ]

    # Categories to search (used as keywords)
    SEARCH_KEYWORDS: list = os.getenv(
        "SEARCH_KEYWORDS",
        "smartphone,notebook,fone,smart tv,kindle,airfryer"
    ).split(",")

    # Force sending all found deals regardless of MIN_DISCOUNT_PERCENT (useful for testing)
    FORCE_SEND_ALL: bool = os.getenv("FORCE_SEND_ALL", "false").lower() == "true"
