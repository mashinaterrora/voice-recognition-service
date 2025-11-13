from typing import Any, Dict, List, Optional

import httpx


class TelegramBotClient:
    def __init__(self, token: str, http_client: httpx.AsyncClient) -> None:
        self._token = token
        self._http = http_client
        self._base_url = f"https://api.telegram.org/bot{self._token}"
        self._file_base_url = f"https://api.telegram.org/file/bot{self._token}"

    async def get_file_path(self, file_id: str) -> str:
        resp = await self._http.get(f"{self._base_url}/getFile", params={"file_id": file_id})
        resp.raise_for_status()
        data: Dict[str, Any] = resp.json()
        if not data.get("ok"):
            raise RuntimeError("Telegram getFile failed")
        return data["result"]["file_path"]

    async def download_file(self, file_path: str) -> bytes:
        url = f"{self._file_base_url}/{file_path}"
        resp = await self._http.get(url)
        resp.raise_for_status()
        return resp.content

    async def send_message(self, chat_id: int, text: str, reply_to_message_id: Optional[int] = None) -> None:
        body: Dict[str, Any] = {"chat_id": chat_id, "text": text}
        if reply_to_message_id is not None:
            body["reply_to_message_id"] = reply_to_message_id
            body["allow_sending_without_reply"] = True
        resp = await self._http.post(f"{self._base_url}/sendMessage", json=body)
        resp.raise_for_status()

    async def send_invoice(
        self,
        chat_id: int,
        title: str,
        description: str,
        payload: str,
        currency: str,
        prices: List[Dict[str, Any]],
        reply_to_message_id: Optional[int] = None,
    ) -> None:
        body: Dict[str, Any] = {
            "chat_id": chat_id,
            "title": title,
            "description": description,
            "payload": payload,
            "currency": currency,
            "prices": prices,
        }
        if reply_to_message_id is not None:
            body["reply_to_message_id"] = reply_to_message_id
            body["allow_sending_without_reply"] = True
        resp = await self._http.post(f"{self._base_url}/sendInvoice", json=body)
        resp.raise_for_status()

    async def answer_pre_checkout_query(self, pre_checkout_query_id: str, ok: bool, error_message: str | None = None) -> None:
        body: Dict[str, Any] = {"pre_checkout_query_id": pre_checkout_query_id, "ok": ok}
        if not ok and error_message:
            body["error_message"] = error_message
        resp = await self._http.post(f"{self._base_url}/answerPreCheckoutQuery", json=body)
        resp.raise_for_status()

    async def refund_star_payment(self, user_id: int, telegram_payment_charge_id: str) -> None:
        body = {"user_id": user_id, "telegram_payment_charge_id": telegram_payment_charge_id}
        resp = await self._http.post(f"{self._base_url}/refundStarPayment", json=body)
        resp.raise_for_status()

    async def get_updates(self, offset: Optional[int] = None, timeout: int = 30) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"timeout": timeout}
        if offset is not None:
            params["offset"] = offset
        resp = await self._http.get(f"{self._base_url}/getUpdates", params=params)
        resp.raise_for_status()
        data: Dict[str, Any] = resp.json()
        if not data.get("ok"):
            return []
        return data.get("result", [])

    async def delete_webhook(self) -> None:
        resp = await self._http.post(f"{self._base_url}/setWebhook", json={"url": ""})
        resp.raise_for_status()






