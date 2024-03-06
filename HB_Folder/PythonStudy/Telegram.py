import telegram
import asyncio

# 비동기 함수 정의
async def send_telegram_message():
    bot = telegram.Bot(token='6785990806:AAF4Khbpp7FWFjdjmgkiLu0ulSfDyGMTOk8')
    await bot.send_message(chat_id="5165569281", text=text_contents)

text_contents = "Hello Telegram\n This is Second message.\n IS everything ok?"

# 비동기 함수 실행
asyncio.run(send_telegram_message())