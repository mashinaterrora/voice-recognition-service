from typing import Any, Dict

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

    async def send_message(self, chat_id: int, text: str) -> None:
        resp = await self._http.post(f"{self._base_url}/sendMessage", json={"chat_id": chat_id, "text": text})
        resp.raise_for_status()
