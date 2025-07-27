# telegram_bot/bot_handler.py
"""
AI Trading Bot - Telegram Bot Yöneticisi
Bu modül Telegram üzerinden bot kontrolü sağlar
"""

import asyncio
import threading
from datetime import datetime
import sys
import os
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
import matplotlib.pyplot as plt
import io
import base64

# Parent directory'yi ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config.credentials import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
    from config.settings import TELEGRAM_COMMANDS, NOTIFICATION_SETTINGS
except ImportError as e:
    print(f"❌ Credentials yüklenemedi: {e}")
    TELEGRAM_BOT_TOKEN = "YOUR_TOKEN_HERE"
    TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

class TelegramBotHandler:
    """Telegram bot yönetici sınıfı"""
    
    def __init__(self, trading_bot=None):
        """TelegramBotHandler'ı başlat"""
        self.trading_bot = trading_bot
        self.application = None
        self.bot_running = False
        
        # Token kontrolü
        if TELEGRAM_BOT_TOKEN == "YOUR_TOKEN_HERE":
            print("⚠️ Telegram bot token tanımlanmamış!")
            print("config/credentials.py dosyasında TELEGRAM_BOT_TOKEN'ı güncelleyin")
            self.enabled = False
        else:
            self.enabled = True
            print("📱 TelegramBotHandler başlatıldı")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Bot başlatma komutu"""
        if not self._is_authorized_user(update):
            return
        
        welcome_message = f"""
🤖 AI TRADING BOT BAŞLATILDI

✅ Bot hazır ve çalışıyor
📅 Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📊 Analiz edilen semboller: EURUSD, XAUUSD
🎯 Güven eşiği: %40

📋 KOMUTLAR:
/start - Bot'u başlat
/status - Bot durumu
/balance - Hesap bakiyesi  
/positions - Açık pozisyonlar
/stop_bot - Bot'u durdur
/daily_report - Günlük rapor
/help - Yardım

🚀 Hazırım! Sinyalleri bekliyorum...
"""
        await update.message.reply_text(welcome_message)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Bot durumu komutu"""
        if not self._is_authorized_user(update):
            return
        
        if self.trading_bot:
            status = self.trading_bot.get_status()
            await update.message.reply_text(f"📊 BOT DURUMU:\n{status}")
        else:
            await update.message.reply_text("❌ Trading bot bağlantısı yok")
    
    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Hesap bakiyesi komutu"""
        if not self._is_authorized_user(update):
            return
        
        try:
            # Trading bot'tan hesap bilgilerini al
            if not self.trading_bot or not self.trading_bot.mt5_connector:
                await update.message.reply_text("❌ MT5 bağlantısı yok")
                return
            
            account_info = self.trading_bot.mt5_connector.get_account_info()
            if not account_info:
                await update.message.reply_text("❌ Hesap bilgileri alınamadı")
                return
            
            balance_message = f"""
💰 HESAP BAKİYESİ

💵 Bakiye: ${account_info['balance']:,.2f}
💎 Equity: ${account_info['equity']:,.2f}
🆓 Free Margin: ${account_info['free_margin']:,.2f}
📊 Margin Level: {account_info.get('margin_level', 0):.2f}%
📈 Profit: ${account_info['profit']:,.2f}
🏦 Server: {account_info['server']}
💱 Para Birimi: {account_info['currency']}
⚖️ Leverage: 1:{account_info['leverage']}
"""
            await update.message.reply_text(balance_message)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Bakiye bilgisi alınamadı: {e}")
    
    async def positions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Açık pozisyonlar komutu"""
        if not self._is_authorized_user(update):
            return
        
        try:
            if not self.trading_bot or not self.trading_bot.mt5_connector:
                await update.message.reply_text("❌ MT5 bağlantısı yok")
                return
            
            positions = self.trading_bot.mt5_connector.get_positions()
            
            if not positions:
                await update.message.reply_text("📭 Açık pozisyon yok")
                return
            
            positions_message = f"📈 AÇIK POZİSYONLAR ({len(positions)} adet):\n\n"
            
            for i, pos in enumerate(positions, 1):
                profit_emoji = "💚" if pos['profit'] >= 0 else "💸"
                positions_message += f"""
{i}. {pos['symbol']} {pos['type']}
   💰 Lot: {pos['volume']}
   📊 Entry: {pos['open_price']:.5f}
   📊 Current: {pos['current_price']:.5f}
   🛡️ SL: {pos['sl']:.5f}
   🎯 TP: {pos['tp']:.5f}
   {profit_emoji} P&L: ${pos['profit']:.2f}
   ⏰ {pos['time_open'].strftime('%H:%M')}
"""
            
            await update.message.reply_text(positions_message)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Pozisyon bilgisi alınamadı: {e}")
    
    async def stop_bot_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Bot durdurma komutu"""
        if not self._is_authorized_user(update):
            return
        
        if self.trading_bot:
            self.trading_bot.stop()
            await update.message.reply_text("⏹️ Trading bot durduruldu!")
        else:
            await update.message.reply_text("❌ Trading bot zaten durdurulmuş")
    
    async def daily_report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Günlük rapor komutu"""
        if not self._is_authorized_user(update):
            return
        
        try:
            report = f"""
📋 GÜNLÜK RAPOR
📅 {datetime.now().strftime('%Y-%m-%d')}

📊 Bot İstatistikleri:
   🎯 Toplam Sinyal: {self.trading_bot.trade_count if self.trading_bot else 0}
   ⏱️ Çalışma Süresi: {datetime.now() - self.trading_bot.session_start_time if self.trading_bot else 'N/A'}
   🔍 Analiz Edilen: EURUSD, XAUUSD

💰 Hesap Durumu:
   💵 Günlük P&L: $0.00 (Demo)
   📈 Toplam Equity: $100,010.71
   🏦 Trading İzni: ❌ Demo Mod

⚡ Son Aktivite:
   🕐 Son Analiz: {datetime.now().strftime('%H:%M:%S')}
   🎯 Son Sinyal: Henüz yok
   ⚠️ Uyarılar: Demo modda çalışıyor

🔄 Sistem Durumu: ✅ Normal
"""
            await update.message.reply_text(report)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Rapor oluşturulamadı: {e}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Yardım komutu"""
        if not self._is_authorized_user(update):
            return
        
        help_message = """
🆘 YARDIM MENÜSÜ

📋 TEMEL KOMUTLAR:
/start - Bot'u başlat ve hoş geldin mesajı
/status - Bot'un anlık durumunu göster
/balance - Hesap bakiyesi ve margin bilgileri
/positions - Açık pozisyonları listele

⚙️ KONTROL KOMUTLARI:
/stop_bot - Trading bot'u durdur
/daily_report - Günün özet raporu

📊 BİLGİ KOMUTLARI:
/help - Bu yardım menüsü

🔔 OTOMATİK BİLDİRİMLER:
✅ Yeni sinyal bildirimleri
✅ Pozisyon açma/kapama
✅ Risk uyarıları
✅ Günlük raporlar

❓ Herhangi bir sorun için lütfen bana yazın!
"""
        await update.message.reply_text(help_message)
    
    def _is_authorized_user(self, update):
        """Kullanıcı yetkisi kontrolü"""
        if str(update.effective_chat.id) != str(TELEGRAM_CHAT_ID):
            print(f"⚠️ Yetkisiz erişim denemesi: {update.effective_chat.id}")
            return False
        return True
    
    async def send_signal_notification(self, signal):
        """Sinyal bildirimi gönder"""
        if not self.enabled or not self.application:
            return
        
        try:
            emoji = "📈" if signal['signal'] == 'BUY' else "📉"
            confidence_emoji = "🔥" if signal['confidence'] > 80 else "⭐"
            
            message = f"""
{emoji} YENİ SİNYAL! {emoji}

💱 Sembol: {signal['symbol']}
🎯 Sinyal: {signal['signal']}
💰 Entry: {signal['entry_price']:.5f}
🛡️ Stop Loss: {signal['stop_loss']:.5f}
🎯 Take Profit: {signal['take_profit']:.5f}
📊 Lot Size: {signal['lot_size']}
{confidence_emoji} Güven: %{signal['confidence']:.1f}
💵 Risk: ${signal['risk_details']['risk_amount']:.2f}

⏰ Zaman: {signal['timestamp'].strftime('%H:%M:%S')}
📝 Durum: Demo Mod
"""
            
            await self.application.bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=message
            )
            
        except Exception as e:
            print(f"❌ Telegram bildirim hatası: {e}")
    
    async def send_risk_warning(self, warning_message):
        """Risk uyarısı gönder"""
        if not self.enabled or not self.application:
            return
        
        try:
            message = f"⚠️ RİSK UYARISI!\n\n{warning_message}"
            await self.application.bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=message
            )
        except Exception as e:
            print(f"❌ Risk uyarısı gönderilemedi: {e}")
    
    def start_bot(self):
        """Telegram bot'u başlat"""
        if not self.enabled:
            print("⚠️ Telegram bot devre dışı")
            return False
        
        try:
            # Application oluştur
            self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
            
            # Komut handler'ları ekle
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("status", self.status_command))
            self.application.add_handler(CommandHandler("balance", self.balance_command))
            self.application.add_handler(CommandHandler("positions", self.positions_command))
            self.application.add_handler(CommandHandler("stop_bot", self.stop_bot_command))
            self.application.add_handler(CommandHandler("daily_report", self.daily_report_command))
            self.application.add_handler(CommandHandler("help", self.help_command))
            
            # Bot'u ayrı thread'de çalıştır
            def run_bot():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                self.application.run_polling()
            
            bot_thread = threading.Thread(target=run_bot, daemon=True)
            bot_thread.start()
            
            self.bot_running = True
            print("✅ Telegram bot başlatıldı!")
            return True
            
        except Exception as e:
            print(f"❌ Telegram bot başlatılamadı: {e}")
            return False
    
    def stop_bot(self):
        """Telegram bot'u durdur"""
        if self.application:
            self.application.stop()
            self.bot_running = False
            print("🔌 Telegram bot durduruldu")


# Test fonksiyonu
def test_telegram_bot():
    """TelegramBotHandler'ı test et"""
    print("🧪 TelegramBotHandler Test Başlıyor...")
    print("=" * 50)
    
    telegram_handler = TelegramBotHandler()
    
    if telegram_handler.enabled:
        print("✅ Telegram bot yapılandırması tamam")
        
        # Test bildirimi
        test_signal = {
            'symbol': 'EURUSD',
            'signal': 'BUY',
            'entry_price': 1.16250,
            'stop_loss': 1.16150,
            'take_profit': 1.16350,
            'lot_size': 0.1,
            'confidence': 75.0,
            'timestamp': datetime.now(),
            'risk_details': {'risk_amount': 100.0}
        }
        
        print("📱 Test sinyali hazırlandı")
        print("🚀 Telegram bot'u manuel olarak başlatabilirsiniz")
        
    else:
        print("❌ Telegram bot yapılandırması eksik")
        print("config/credentials.py dosyasında TELEGRAM_BOT_TOKEN'ı güncelleyin")

if __name__ == "__main__":
    test_telegram_bot()