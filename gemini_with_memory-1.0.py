#Developer: @OCTPOBCEKPETOB Channel: @newHikka
from hikkatl.types import Message
from hikka import loader, utils
import aiohttp
import json
from typing import Dict, List, Optional
#Developer: @OCTPOBCEKPETOB Channel: @newHikka
@loader.tds
class GeminiProByOCTPOBCEKPETOB(loader.Module):
    strings = {
        "name": "GeminiAI",
        "no_api_key": "<b>API-ключ Gemini не найден!</b>\nИспользуй: <code>{}gemini_key [ключ]</code>",
        "no_text": " <b>Ты забыл кое что написать..</b>\nПримерчик: <code>{}gemini как дела?</code>",
        "thinking": "💭 <i>Обрабатываю запрос...</i>",
        "memory_cleared": "🧹 <b>История диалога очищена!</b>",
        "error": "⚠️ <b>Обратитесь к разработчику @OCTPOBCEKPETOB\nОшибка:</b> <code>{}</code>",
        "response": "<b>Ваш запрос:</b> <code>{}</code>\n\n<b>Gemini:</b>\n<code>{}</code>",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            "gemini_key", None, "API-ключ от Google AI Studio"
        )
        self.chat_histories: Dict[int, List[dict]] = {}
        self.session: Optional[aiohttp.ClientSession] = None

    async def client_ready(self, client, db):
        self._client = client
        self.session = aiohttp.ClientSession()

    async def on_unload(self):
        if self.session:
            await self.session.close()

    async def _make_gemini_request(self, messages: List[dict]) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        params = {"key": self.config["gemini_key"]}
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": messages,
            "generationConfig": {
                "temperature": 0.7,
                "topP": 1,
                "topK": 32,
                "maxOutputTokens": 2000,
            }
        }

        async with self.session.post(
            url,
            params=params,
            headers=headers,
            data=json.dumps(payload),
        ) as response:
            if response.status != 200:
                error = await response.text()
                raise Exception(f"Ошибка, обратитесь к разработчику @OCTPOBCEKPETOB {response.status}: {error}")
            data = await response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

    async def gemini_key(self, message: Message):
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(
                message,
                self.strings["no_api_key"].format(self.get_prefix()),
            )
            return

        self.config["gemini_key"] = args
        await utils.answer(message, "<b>Спасибо! Ключ Gemini успешно сохранён!</b>")


    async def gemini(self, message: Message):
        if not self.config["gemini_key"]:
            await utils.answer(
                message,
                self.strings["no_api_key"].format(self.get_prefix()),
            )
            return

        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(
                message,
                self.strings["no_text"].format(self.get_prefix()),
            )
            return

        user_id = message.sender_id
        if user_id not in self.chat_histories:
            self.chat_histories[user_id] = []

        self.chat_histories[user_id].append({
            "role": "user",
            "parts": [{"text": args}],
        })

        processing_msg = await utils.answer(message, self.strings["thinking"])

        try:
            reply = await self._make_gemini_request(self.chat_histories[user_id])
            self.chat_histories[user_id].append({
                "role": "model",
                "parts": [{"text": reply}],
            })

            formatted_response = self.strings["response"].format(
                utils.escape_html(args),
                utils.escape_html(reply),
            )
            await processing_msg.edit(formatted_response)

        except Exception as e:
            await processing_msg.edit(self.strings["error"].format(str(e)))

    async def gemini_clear(self, message: Message):
        user_id = message.sender_id
        if user_id in self.chat_histories:
            self.chat_histories[user_id] = []
        await utils.answer(message, self.strings["memory_cleared"])
#Developer: @OCTPOBCEKPETOB Channel: @newHikka
#Developer: @OCTPOBCEKPETOB Channel: @newHikka
#Developer: @OCTPOBCEKPETOB Channel: @newHikka