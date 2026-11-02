import logging
import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

# የሎግ ማስተካከያ (Logging Configuration)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ከ Render Environment Variables ቶከኑን እና የአስተዳዳሪውን ID በደህንነት ማንበብ
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "644789117"))

# -------------------------------------------------------------
# ለ Render ነፃ Web Service ፖርት ክፍት እንዲያደርግ የ Flask ሰርቨር ማዘጋጀት
# -------------------------------------------------------------
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "A2bot is running live and active 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)
# -------------------------------------------------------------

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ተጠቃሚው /start ሲልክ ፕሮፌሽናል እና ማራኪ አቀባበል መልእክት ይሰጣል"""
    welcome_text = (
        "👋 **እንኳን ደህና መጡ! Welcome!**\n\n"
        "የምንሰጣቸው አገልግሎቶች፦\n"
        "• የሶሻል ሚዲያ አካውንቶች ግዢ እና ሽያጭ \n"
        "• Facebook, TikTok & Instagram Boost\n\n"
        "💻 **በተጨማሪ ባሉበት ቦታ ሁነው (Remotely / በበርቀት የተለያዩ ሰልኮችን እንከፍታለን)፦**\n"
        "🔹 FRP Unlock\n"
        "🔹 MDM Unlock\n"
        "🔹 Anti-Crack Remove\n"
        "🔹 Soft Brick Fix\n"
        "🔹 PC ላይ Software መጫን\n"
        "🔹 PC ላይ Driver መጫን\n"
        "🔹 Flash File መጫን\n\n"
        "• **Professional Tools (Hourly Rental):**\n"
        "  - MDM Fix Tool\n"
        "  - Unlock Tool\n"
        "  - CM2 Dongle\n"
        "  - TSM Tool\n\n"
        "• 💸 **USDT እንሸጥአለን እንገዛለን💵**\n\n"
        "መልእክትዎን ወይም ጥያቄዎን ያስቀምጡልን፤ ፈጣን ምላሽ እንሰጥዎታለን! ⏳"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def forward_message_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ተጠቃሚው የላከውን መልእክት (ጽሁፍ፣ ፎቶ፣ ወዘተ) መታወቂያውን (ID) ጨምሮ ለአስተዳዳሪው ያስተላልፋል"""
    user = update.effective_user
    
    if user.id == ADMIN_CHAT_ID:
        return

    try:
        await update.message.reply_text("መልእክትዎ ደርሶኛል! ኦንላይን ስሆን ወዲያውኑ እመልስልዎታለሁ። 🙏")
        
        msg_text = update.message.text or update.message.caption or "ፋይል/ፎቶ (ያለ ጽሁፍ)"

        admin_notification = (
            f"📩 **አዲስ መልእክት ደርሶታል!**\n\n"
            f"👤 **ስም:** {user.full_name}\n"
            f"🆔 **ID:** `{user.id}`\n\n"
            f"💬 **መልእክት:**\n{msg_text}"
        )
        
        if update.message.photo:
            photo_file_id = update.message.photo[-1].file_id
            await context.bot.send_photo(
                chat_id=ADMIN_CHAT_ID,
                photo=photo_file_id,
                caption=admin_notification,
                parse_mode='Markdown'
            )
        else:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=admin_notification,
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"መልእክት ወደ አስተዳዳሪ ማስተላለፍ አልተቻለም: {e}")

async def reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """አስተዳዳሪው ኖቲፊኬሽኑን ሪፕላይ አድርጎ ሲመልስ ለተጠቃሚው ያደርሳል"""
    reply_msg = update.message.reply_to_message
    
    if not reply_msg:
        return

    try:
        content_to_search = reply_msg.text or reply_msg.caption or ""
        lines = content_to_search.split('\n')
        target_user_id = None
        
        for line in lines:
            if "ID:" in line:
                clean_line = line.replace("🆔", "").replace("**ID:**", "").replace("ID:", "").replace("`", "").strip()
                if clean_line.isdigit():
                    target_user_id = int(clean_line)
                    break

        if target_user_id:
            if update.message.photo:
                await context.bot.send_photo(
                    chat_id=target_user_id,
                    photo=update.message.photo[-1].file_id,
                    caption=update.message.caption
                )
            elif update.message.text:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text=update.message.text
                )
            
            await update.message.reply_text("✅ መልእክትዎ ለተጠቃሚው በተሳካ ሁኔታ ተልኳል!")
        else:
            await update.message.reply_text("❌ የዚህን ተጠቃሚ ID ማግኘት አልተቻለም። እባክዎን ትክክለኛውን ኖቲፊኬሽን መልእክት ሪፕላይ (Reply) ያድርጉ።")
            
    except Exception as e:
        logger.error(f"መልእክት ለተጠቃሚው መላክ አልተቻለም: {e}")
        logger.exception(e)
        await update.message.reply_text(f"❌ መላክ አልቻለም: {e}")

def main() -> None:
    """ቦቱን ማስጀመሪያ ዋናው ተግባር"""
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN አልተገኘም! እባክዎን በ Environment Variables ውስጥ ያስገቡ።")
        return

    # የ Flask ሰርቨሩን በሌላ ፕሬድ (Thread) ማስጀመር
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    logger.info("የ Flask ዌብ ሰርቨር ፖርት ማስተናገጃ ተጀምሯል...")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.Chat(ADMIN_CHAT_ID) & filters.REPLY, reply_to_user))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND & ~filters.Chat(ADMIN_CHAT_ID), forward_message_to_admin))

    logger.info("ቦቱ የፖሊንግ ስራ ጀምሯል...")
    app.run_polling()

if __name__ == '__main__':
    main()
