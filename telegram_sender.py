"""
Telegram message sender
"""

import logging
import requests
import html
from typing import Optional

logger = logging.getLogger(__name__)

EMOJI_MAP = {
    "eletronicos": "📱",
    "smartphone": "📱",
    "notebook": "💻",
    "tv": "📺",
    "fone": "🎧",
    "kindle": "📚",
    "airfryer": "🍳",
    "default": "🛒",
}


class TelegramSender:
    BASE_URL = "https://api.telegram.org/bot{token}/{method}"

    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id

    def send_deal(self, product: dict) -> bool:
        """Send a single deal to Telegram. Returns True on success."""
        message = self._format_message(product)

        # Try to send with photo first
        if product.get("image"):
            success = self._send_photo(product["image"], message)
            if success:
                return True

        # Fallback: text only
        return self._send_message(message)

    # ─────────────────────────────────────────────────────────────
    def _format_message(self, p: dict) -> str:
        """Build an HTML message safely escaped for Telegram HTML parse mode."""
        emoji = _pick_emoji(p.get("title", ""))
        title = p.get("title", "Produto Amazon")
        price = p.get("price")
        original = p.get("original_price")
        discount = p.get("discount", 0)
        url = p.get("affiliate_url") or p.get("url", "")

        esc_title = html.escape(str(title))
        esc_url = html.escape(str(url), quote=True)

        parts = []
        parts.append(f"{emoji} <b>{esc_title}</b>")

        if discount and discount > 0:
            parts.append(f"🔥 <b>{discount}% OFF</b>")

        if price is not None:
            price_str = f"R$ {price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            parts.append(f"💰 <b>{html.escape(price_str)}</b>")

        if original and original > (price or 0):
            orig_fmt = f"R$ {original:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            parts.append(f"<s>De {html.escape(orig_fmt)}</s>")

        parts.append(f"<a href=\"{esc_url}\">🛒 Comprar na Amazon</a>")
        parts.append("<i>Preço pode variar. Confira antes de comprar.</i>")

        return "\n".join(parts)

    def _send_photo(self, photo_url: str, caption: str) -> bool:
        url = self.BASE_URL.format(token=self.token, method="sendPhoto")
        payload = {
            "chat_id": self.chat_id,
            "photo": photo_url,
            "caption": caption,
            "parse_mode": "HTML",
        }
        try:
            r = requests.post(url, json=payload, timeout=15)
            try:
                data = r.json()
            except Exception:
                data = {"raw": r.text}
            logger.debug(f"sendPhoto status={r.status_code} resp={r.text}")
            if data.get("ok"):
                return True
            logger.warning(f"sendPhoto falhou: {data.get('description') or data}")
        except Exception as e:
            logger.warning(f"Erro sendPhoto: {e}")
        return False

    def _send_message(self, text: str) -> bool:
        url = self.BASE_URL.format(token=self.token, method="sendMessage")
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        }
        try:
            r = requests.post(url, json=payload, timeout=15)
            try:
                data = r.json()
            except Exception:
                data = {"raw": r.text}
            logger.debug(f"sendMessage status={r.status_code} resp={r.text}")
            if data.get("ok"):
                logger.info(f"✅ Mensagem enviada: {text[:50]}...")
                return True
            logger.warning(f"Telegram erro: {data.get('description') or data}")
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
        return False

    def send_startup_message(self):
        msg = "🤖 <b>Bot de Promoções Amazon iniciado!</b>\nAguarde as próximas ofertas. 🛒"
        self._send_message(msg)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _pick_emoji(title: str) -> str:
    title_lower = title.lower()
    for keyword, emoji in EMOJI_MAP.items():
        if keyword in title_lower:
            return emoji
    return EMOJI_MAP["default"]


def _escape(text: str) -> str:
    """Escape text for HTML output (simple wrapper)."""
    return html.escape(str(text))
