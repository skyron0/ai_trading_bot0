# config/credentials.py
"""
AI Trading Bot - API Anahtarları ve Gizli Bilgiler
UYARI: Bu dosyayı asla paylaşmayın veya GitHub'a yüklemeyin!
"""

# =============================================================================
# TELEGRAM BOT BİLGİLERİ
# =============================================================================

# Telegram Bot Token (BotFather'dan alınacak)
TELEGRAM_BOT_TOKEN = "8157323276:AAGCsJUgLMVgzUttIaE_v1Nd31KGnpAwXfM"

# Telegram Chat ID (botunuzla konuşan kullanıcının ID'si)
TELEGRAM_CHAT_ID = "6850378412"

# =============================================================================
# METATRADER 5 BİLGİLERİ
# =============================================================================

# XM Broker Demo/Live Hesap Bilgileri
MT5_LOGIN = 58656651 # Hesap numaranız
MT5_PASSWORD = "6aXkCn_y"  # MT5 şifreniz
MT5_SERVER = "AdmiralsSC-Demo"  # Demo için: "XM-Demo", Live için: "XM-Real" 
MT5_PATH = r"C:\Program Files\MetaTrader 5\terminal64.exe"  # MT5 kurulum yolu

# =============================================================================
# DIŞARDAN VERİ API'LARİ
# =============================================================================

# Alpha Vantage (Forex ve hisse verisi)
ALPHA_VANTAGE_API_KEY = "YOUR_ALPHA_VANTAGE_KEY"

# NewsAPI (Haber analizi için)
NEWS_API_KEY = "YOUR_NEWS_API_KEY"

# CoinGecko Pro (Kripto verisi - opsiyonel)
COINGECKO_API_KEY = "YOUR_COINGECKO_KEY"  # Ücretsiz versiyon için boş bırakın

# =============================================================================
# VERİTABANI VE GÜVENLİK
# =============================================================================

# Database şifreleme anahtarı
DATABASE_ENCRYPTION_KEY = "your-secret-encryption-key-32-chars"

# API güvenlik token'ı (kendi oluşturduğumuz)
INTERNAL_API_SECRET = "your-internal-api-secret-key"

# =============================================================================
# YEDEKLİ AYARLAR
# =============================================================================

# Eğer ana hesap çalışmazsa yedek hesap bilgileri
BACKUP_MT5_LOGIN = None
BACKUP_MT5_PASSWORD = None
BACKUP_MT5_SERVER = None

# =============================================================================
# NASIL DOLDURULACAĞINA DAİR BİLGİLER
# =============================================================================

"""
🔧 API Anahtarlarını Nasıl Alırsınız:

1. TELEGRAM BOT TOKEN:
   - Telegram'da @BotFather'ı bulun
   - /newbot komutunu gönderin
   - Bot adı verin (örn: MyTradingBot)
   - Verilen token'ı TELEGRAM_BOT_TOKEN'a yapıştırın

2. TELEGRAM CHAT ID:
   - Botunuzla konuşmaya başlayın (/start gönderin)  
   - https://api.telegram.org/bot<YourBOTToken>/getUpdates adresine gidin
   - "chat":{"id":123456789 kısmındaki sayıyı alın

3. MT5 BİLGİLERİ:
   - XM'den demo hesap açın
   - Hesap numarası, şifre ve sunucu bilgilerini alın
   - MT5'i bilgisayarınıza kurun

4. ALPHA VANTAGE:
   - https://www.alphavantage.co/support/#api-key adresine gidin
   - Ücretsiz API key alın

5. NEWS API:
   - https://newsapi.org/ adresine gidin
   - Ücretsiz hesap açın, API key alın
"""

# Test fonksiyonu
def validate_credentials():
    """API anahtarlarının doğru doldurulup doldurulmadığını kontrol eder"""
    missing = []
    
    if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        missing.append("TELEGRAM_BOT_TOKEN")
    
    if TELEGRAM_CHAT_ID == "YOUR_TELEGRAM_CHAT_ID_HERE":
        missing.append("TELEGRAM_CHAT_ID")
        
    if MT5_PASSWORD == "YOUR_MT5_PASSWORD":
        missing.append("MT5_PASSWORD")
    
    if missing:
        print("❌ Eksik API anahtarları:")
        for item in missing:
            print(f"   - {item}")
        return False
    else:
        print("✅ Tüm API anahtarları tanımlanmış")
        return True

if __name__ == "__main__":
    validate_credentials()