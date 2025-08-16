import telegram
from datetime import datetime
import os

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = telegram.Bot(token=TOKEN)

def send_message():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    msg = f"테스트 메시지입니다. 현재 시간: {now}"
    bot.send_message(chat_id=CHAT_ID, text=msg)

if __name__ == "__main__":
    send_message()
