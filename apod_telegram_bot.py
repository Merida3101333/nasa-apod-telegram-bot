from dotenv import load_dotenv
import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import logging

# 設置日誌
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# 載入 .env 文件中的環境變數
load_dotenv()

# 從環境變數獲取 Telegram Bot Token 和 NASA API KEY
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
NASA_API_KEY = os.getenv("NASA_API_KEY")

def get_apod():
    logger.info("正在請求 APOD 數據...")
    url = f'https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}'
    try:
        response = requests.get(url)
        response.raise_for_status()  # 如果請求不成功則拋出異常
        logger.info("APOD 數據請求成功")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"請求 APOD 數據失敗: {e}")
        return None

async def send_apod(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text="正在獲取今天的天文圖片，請稍候...")
    
    apod_data = get_apod()
    if apod_data:
        message = f"Title: {apod_data['title']}\n\n{apod_data['explanation']}"
        try:
            await context.bot.send_photo(chat_id=chat_id, photo=apod_data['url'], caption=message)
            logger.info(f"成功發送 APOD 到聊天 ID: {chat_id}")
        except Exception as e:
            logger.error(f"發送 APOD 失敗: {e}")
            await context.bot.send_message(chat_id=chat_id, text="抱歉，發送圖片時出現錯誤。")
    else:
        await context.bot.send_message(chat_id=chat_id, text="抱歉，無法獲取今天的天文圖片。請稍後再試。")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, 
                             text="歡迎使用 APOD Bot！使用 /apod 命令來獲取今天的天文圖片。")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"更新 {update} 導致錯誤 {context.error}")

def main():
    logger.info("啟動 bot...")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("apod", send_apod))
    application.add_error_handler(error_handler)

    logger.info("Bot 已啟動，開始輪詢更新...")
    application.run_polling()

if __name__ == '__main__':
    main()