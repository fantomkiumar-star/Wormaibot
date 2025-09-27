import logging
import threading
import os
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from bot_handlers import BotHandlers
from config import BOT_TOKEN
from app import app
from gunicorn.app.base import BaseApplication

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class FlaskApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

def start_flask_server():
    """Start Flask web server using Gunicorn"""
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🌐 Starting Flask web server on port {port}...")
    options = {
        'bind': f'0.0.0.0:{port}',
        'workers': 4,
        'timeout': 120
    }
    FlaskApplication(app, options).run()

def start_telegram_bot():
    """Start Telegram bot"""
    logger.info("🚀 Starting FANTOM DELUXE AI Bot...")
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN is not set in config")
        raise ValueError("BOT_TOKEN is required")
    
    try:
        # Build the application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Initialize handlers
        handlers = BotHandlers()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", handlers.start_command))
        application.add_handler(CommandHandler("menu", handlers.menu_command))
        application.add_handler(CommandHandler("clear", handlers.clear_command))
        application.add_handler(CommandHandler("broadcast", handlers.broadcast_command))
        application.add_handler(CommandHandler("help", handlers.help_command))
        
        # Add callback query handler for buttons
        application.add_handler(CallbackQueryHandler(handlers.button_callback))
        
        # Add message handler for regular messages
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_message))
        
        logger.info("✅ Bot handlers configured successfully")
        logger.info("🔄 Starting bot polling...")
        
        # Run polling with only supported arguments
        application.run_polling(allowed_updates=Application.Handler.ALL)
        
    except Exception as e:
        logger.error(f"❌ Critical error starting bot: {e}")
        raise

def main():
    """Main function to start both Flask server and Telegram bot"""
    logger.info("🚀 Starting FANTOM DELUXE AI Bot with Flask web server...")
    
    # Start Flask server in a separate thread
    flask_thread = threading.Thread(target=start_flask_server, daemon=True)
    flask_thread.start()
    logger.info("✅ Flask web server started in background")
    
    # Start Telegram bot in main thread
    try:
        start_telegram_bot()
    except KeyboardInterrupt:
        logger.info("🛑 Bot and web server stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        raise

if __name__ == '__main__':
    main()
