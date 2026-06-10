"""
Amazon scraper using Selenium
"""

import re
import time
import random
import logging
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from config import Config

logger = logging.getLogger(__name__)


class AmazonScraper:
    def __init__(self):
        self.driver = self._init_driver()
        self.seen_asins: set = set()  # avoid duplicates across runs

    def _init_driver(self) -> webdriver.Chrome:
        options = Options()

        if Config.HEADLESS:
            options.add_argument("--headless=new")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(f"--user-agent={Config.USER_AGENT}")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--window-size=1920,1080")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        # Hide webdriver flag
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        return driver

    # ─────────────────────────────────────────────────────────────
    def get_deals(self) -> list[dict]:
        """Scrape deals from multiple sources and return product list"""
        products = []

        # 1. Amazon Deals page
        products += self._scrape_deals_page()

        # 2. Keyword searches
        for keyword in Config.SEARCH_KEYWORDS[: 3]:  # limit to 3 keywords
            products += self._scrape_search(keyword.strip())
            time.sleep(random.uniform(2, 4))

        # Deduplicate by ASIN
        seen = set()
        unique = []
        for p in products:
            if p.get("asin") and p["asin"] not in seen:
                seen.add(p["asin"])
                unique.append(p)

        # Sort by discount descending, cap results
        unique.sort(key=lambda x: x.get("discount", 0), reverse=True)
        return unique[: Config.MAX_PRODUCTS_PER_RUN]

    # ─────────────────────────────────────────────────────────────
    def _scrape_deals_page(self) -> list[dict]:
        """Scrape amazon.com.br/deals"""
        url = "https://www.amazon.com.br/deals"
        logger.info(f"Acessando página de ofertas: {url}")
        products = []

        try:
            self.driver.get(url)
            self._human_pause()
            self._scroll_page()

            cards = self.driver.find_elements(
                By.CSS_SELECTOR,
                "[data-testid='deal-card'], .DealCard-module__container, .a-section.octopus-dlp-asin-section"
            )

            logger.info(f"  → {len(cards)} cards encontrados em /deals")

            for card in cards[:20]:
                product = self._parse_deal_card(card)
                if product:
                    products.append(product)

        except Exception as e:
            logger.warning(f"Erro em /deals: {e}")

        return products

    def _scrape_search(self, keyword: str) -> list[dict]:
        """Scrape search results filtered by discount"""
        url = (
            f"https://www.amazon.com.br/s?k={keyword.replace(' ', '+')}"
            "&rh=p_n_pct-off-with-tax%3A20-100%25"
            "&sort=price-asc-rank"
        )
        logger.info(f"Buscando '{keyword}'...")
        products = []

        try:
            self.driver.get(url)
            self._human_pause()

            items = self.driver.find_elements(
                By.CSS_SELECTOR,
                "div[data-component-type='s-search-result']"
            )

            logger.info(f"  → {len(items)} resultados para '{keyword}'")

            for item in items[:8]:
                product = self._parse_search_result(item)
                if product:
                    products.append(product)

        except Exception as e:
            logger.warning(f"Erro ao buscar '{keyword}': {e}")

        return products

    # ─────────────────────────────────────────────────────────────
    def _parse_deal_card(self, card) -> Optional[dict]:
        """Extract product data from a deal card element"""
        try:
            title = self._safe_text(card, [
                "[data-testid='deal-title']",
                ".DealCard-module__title",
                "h2 span", "h3 span"
            ])
            if not title:
                return None

            price_text = self._safe_text(card, [
                "[data-testid='deal-price']",
                ".DealCard-module__price",
                ".a-price .a-offscreen",
                ".a-price-whole"
            ])

            original_text = self._safe_text(card, [
                "[data-testid='original-price']",
                ".DealCard-module__originalPrice",
                ".a-text-strike"
            ])

            discount_text = self._safe_text(card, [
                "[data-testid='discount-badge']",
                ".DealCard-module__discountBadge",
                ".savingsPercentage",
                ".a-badge-text"
            ])

            link = self._safe_attr(card, [
                "a[href*='/dp/']",
                "a[href*='amazon.com.br']"
            ], "href")

            image = self._safe_attr(card, ["img"], "src")

            price = _parse_price(price_text)
            original = _parse_price(original_text)
            discount = _parse_discount(discount_text)

            # Calculate discount if not found directly
            if not discount and price and original and original > price:
                discount = round((1 - price / original) * 100)

            asin = _extract_asin(link) if link else None

            if not asin or not link:
                return None

            # Normalize URL
            clean_url = f"https://www.amazon.com.br/dp/{asin}"

            return {
                "title": title[:120],
                "price": price,
                "original_price": original,
                "discount": discount or 0,
                "url": clean_url,
                "asin": asin,
                "image": image,
                "source": "deals",
            }

        except Exception:
            return None

    def _parse_search_result(self, item) -> Optional[dict]:
        """Extract product data from a search result element"""
        try:
            title = self._safe_text(item, [
                "h2 a span",
                "[data-cy='title-recipe'] span"
            ])
            if not title:
                return None

            price_whole = self._safe_text(item, [".a-price-whole"])
            price_fraction = self._safe_text(item, [".a-price-fraction"])
            price_text = f"{price_whole},{price_fraction}" if price_whole else ""

            original_text = self._safe_text(item, [
                ".a-text-strike .a-offscreen",
                ".a-price.a-text-strike .a-offscreen"
            ])

            discount_text = self._safe_text(item, [
                ".a-badge-text",
                ".savingsPercentage"
            ])

            link_el = self._safe_find(item, ["h2 a", "[data-cy='title-recipe'] a"])
            href = link_el.get_attribute("href") if link_el else None

            image = self._safe_attr(item, ["img.s-image", ".s-image"], "src")

            price = _parse_price(price_text)
            original = _parse_price(original_text)
            discount = _parse_discount(discount_text)

            if not discount and price and original and original > price:
                discount = round((1 - price / original) * 100)

            asin = _extract_asin(href) if href else None
            if not asin or not href:
                return None

            clean_url = f"https://www.amazon.com.br/dp/{asin}"

            return {
                "title": title[:120],
                "price": price,
                "original_price": original,
                "discount": discount or 0,
                "url": clean_url,
                "asin": asin,
                "image": image,
                "source": "search",
            }

        except Exception:
            return None

    # ─────────────────────────────────────────────────────────────
    def _safe_text(self, parent, selectors: list) -> str:
        for sel in selectors:
            try:
                el = parent.find_element(By.CSS_SELECTOR, sel)
                text = el.text.strip() or el.get_attribute("textContent").strip()
                if text:
                    return text
            except NoSuchElementException:
                continue
        return ""

    def _safe_attr(self, parent, selectors: list, attr: str) -> str:
        for sel in selectors:
            try:
                el = parent.find_element(By.CSS_SELECTOR, sel)
                val = el.get_attribute(attr)
                if val:
                    return val
            except NoSuchElementException:
                continue
        return ""

    def _safe_find(self, parent, selectors: list):
        for sel in selectors:
            try:
                return parent.find_element(By.CSS_SELECTOR, sel)
            except NoSuchElementException:
                continue
        return None

    def _scroll_page(self, times: int = 3):
        for _ in range(times):
            self.driver.execute_script(
                "window.scrollBy(0, window.innerHeight * 0.8)"
            )
            time.sleep(random.uniform(0.8, 1.5))

    def _human_pause(self):
        time.sleep(random.uniform(2.5, 5.0))

    def close(self):
        try:
            self.driver.quit()
        except Exception:
            pass


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _parse_price(text: str) -> Optional[float]:
    if not text:
        return None
    # Remove currency symbols, convert BR format
    cleaned = re.sub(r"[^\d,\.]", "", text)
    # Handle "1.299,99" → "1299.99"
    if "," in cleaned and "." in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def _parse_discount(text: str) -> Optional[int]:
    if not text:
        return None
    match = re.search(r"(\d+)", text)
    if match:
        return int(match.group(1))
    return None


def _extract_asin(url: str) -> Optional[str]:
    if not url:
        return None
    match = re.search(r"/dp/([A-Z0-9]{10})", url)
    return match.group(1) if match else None
