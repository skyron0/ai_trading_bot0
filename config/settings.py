# config/settings.py
"""
AI Trading Bot - Ana Konfigürasyon Dosyası
Bu dosyada botun tüm temel ayarları bulunur
"""

# =============================================================================
# TRADING PARAMETRELERİ
# =============================================================================

# İşlem yapılacak semboller (Admiral Markets uyumlu)
TRADING_SYMBOLS = {
    'EURUSD': {
        'symbol': 'EURUSD-T',  # Admiral Markets format
        'point_value': 0.00001,  # 1 pip değeri
        'min_lot': 0.01,
        'max_lot': 100.0,
        'spread_limit': 60  # Demo'da spread daha yüksek olabilir
    },
    'XAUUSD': {  # Altın
        'symbol': 'GOLD-T',  # Admiral Markets'te GOLD-T
        'point_value': 0.01,
        'min_lot': 0.01,
        'max_lot': 50.0,
        'spread_limit': 50  # Altında spread daha yüksek
    },
    'BTCUSD': {  # Bitcoin
        'symbol': 'BTCUSD-T',  # Admiral Markets format
        'point_value': 1.0,
        'min_lot': 0.01,
        'max_lot': 10.0,
        'spread_limit': 100
    }
}

# =============================================================================
# RİSK YÖNETİMİ PARAMETRELERİ
# =============================================================================

# Günlük risk limitleri
DAILY_MAX_LOSS_PERCENT = 10.0  # Günlük max %10 kayıp
MAX_POSITIONS_PER_SYMBOL = 2   # Sembole max 2 açık pozisyon
MAX_TOTAL_POSITIONS = 6        # Toplam max 6 pozisyon
MAX_CORRELATION_POSITIONS = 3   # Korelasyonlu max 3 pozisyon

# Position sizing
RISK_PER_TRADE = 2.0          # İşlem başına risk %2
DEFAULT_LOT_SIZE = 0.01       # Varsayılan lot boyutu
MIN_ACCOUNT_BALANCE = 100.0   # Min hesap bakiyesi ($)

# Stop Loss & Take Profit (Scalping için)
DEFAULT_STOP_LOSS_PIPS = 15   # Varsayılan SL (pip)
DEFAULT_TAKE_PROFIT_PIPS = 20 # Varsayılan TP (pip)
TRAILING_STOP_DISTANCE = 10   # Trailing stop mesafesi
MAX_TRADE_DURATION_MINUTES = 30  # Max açık kalma süresi

# =============================================================================
# AI VE ANALİZ PARAMETRELERİ  
# =============================================================================

# Teknik analiz zaman dilimleri
TIMEFRAMES = {
    'M1': 1,      # 1 dakika (scalping için ana)
    'M5': 5,      # 5 dakika 
    'M15': 15,    # 15 dakika
    'H1': 60      # 1 saat (trend için)
}

# Teknik göstergeler
TECHNICAL_INDICATORS = {
    'RSI_PERIOD': 14,
    'MACD_FAST': 12,
    'MACD_SLOW': 26,
    'MACD_SIGNAL': 9,
    'MA_FAST': 10,
    'MA_SLOW': 20,
    'BOLLINGER_PERIOD': 20,
    'ATR_PERIOD': 14
}

# AI karar verme eşikleri
AI_CONFIDENCE_THRESHOLD = 0.05  # Test için %5'e düşürüldü
SIGNAL_STRENGTH_MIN = 60       # Min sinyal gücü
NEWS_IMPACT_WEIGHT = 0.3       # Haber etkisi ağırlığı

# =============================================================================
# TELEGRAM BOT AYARLARI
# =============================================================================

# Bot komutları
TELEGRAM_COMMANDS = {
    'start_bot': '🚀 Bot Başlatıldı',
    'stop_bot': '⏹️ Bot Durduruldu',
    'status': '📊 Bot Durumu',
    'balance': '💰 Hesap Bakiyesi',
    'positions': '📈 Açık Pozisyonlar',
    'daily_report': '📋 Günlük Rapor',
    'close_all': '🚨 Tüm Pozisyonları Kapat'
}

# Bildirim ayarları
NOTIFICATION_SETTINGS = {
    'send_entry_signals': True,
    'send_exit_signals': True,
    'send_risk_warnings': True,
    'send_daily_reports': True,
    'send_news_alerts': True
}

# =============================================================================
# VERİ KAYNAKLARI
# =============================================================================

# Market data kaynakları
DATA_SOURCES = {
    'MT5': True,           # MetaTrader 5 (ana kaynak)
    'ALPHA_VANTAGE': True, # Forex & hisse
    'COINAPI': False,      # Kripto (premium)
    'YAHOO_FINANCE': True  # Ücretsiz backup
}

# Haber kaynakları
NEWS_SOURCES = {
    'NEWSAPI': True,       # newsapi.org
    'FOREXFACTORY': True,  # Forex calendar
    'TRADINGECONOMICS': False  # Economic data
}

# =============================================================================
# SİSTEM AYARLARI
# =============================================================================

# Logging ayarları
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = True
LOG_TO_CONSOLE = True
MAX_LOG_FILES = 10

# Database ayarları
DATABASE_PATH = 'data/trading_bot.db'
BACKUP_INTERVAL_HOURS = 24

# Performance ayarları
DATA_UPDATE_INTERVAL_SECONDS = 1   # Veri güncellem sıklığı
MAX_MEMORY_USAGE_MB = 1024        # Max RAM kullanımı
CLEANUP_INTERVAL_MINUTES = 60     # Temizlik sıklığı

# =============================================================================
# GÜVENLİK AYARLARI
# =============================================================================

# Acil durum ayarları
EMERGENCY_STOP_LOSS_PERCENT = 15.0  # Acil durum SL
MAX_CONSECUTIVE_LOSSES = 5          # Ard arda max 5 zarar
CIRCUIT_BREAKER_COOLDOWN = 30       # Devre kesici bekleme (dk)

# API güvenliği
MAX_API_CALLS_PER_MINUTE = 100
API_TIMEOUT_SECONDS = 30

print("✅ Konfigürasyon dosyası yüklendi")
print(f"📊 İşlem sembolleri: {list(TRADING_SYMBOLS.keys())}")
print(f"⚠️ Günlük risk limiti: %{DAILY_MAX_LOSS_PERCENT}")
print(f"🎯 AI güven eşiği: %{AI_CONFIDENCE_THRESHOLD*100}")