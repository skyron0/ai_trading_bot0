# main.py
"""
AI Trading Bot - Main Entry Point (Modular Edition)
Triple AI Power: Teknik + Haber + Multiple Timeframe
"""

import sys
import time
from datetime import datetime

# Konfigürasyon
from config.settings import (
    TRADING_SYMBOLS, DATA_UPDATE_INTERVAL_SECONDS
)

# Core modüller
from bot_core.signal_processor import SignalProcessor
from bot_core.trading_bot import AITradingBot  # AKTİFLEŞTİRİLDİ!

# Simulation mode
SIMULATION_MODE = True  # False = Gerçek trading, True = Simülasyon

def main():
    """Ana fonksiyon - Modüler yapı"""
    print("🚀 TRIPLE AI TRADING BOT - MODULAR EDITION")
    print("=" * 60)
    print("🔧 Modüler yapı ile yeniden tasarlandı")
    print("📊 Triple AI: Teknik + Haber + Multiple Timeframe")
    print(f"🎭 Simülasyon modu: {'Aktif' if SIMULATION_MODE else 'Kapalı'}")
    print(f"💰 Hedef semboller: {list(TRADING_SYMBOLS.keys())}")
    print(f"⏱️ Analiz sıklığı: {DATA_UPDATE_INTERVAL_SECONDS} saniye")
    
    # Bot'u oluştur - TAM MODÜLER BOT!
    bot = AITradingBot(simulation_mode=SIMULATION_MODE)
    
    # Komut satırı kontrolü
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'start':
            bot.start()
        elif command == 'status':
            print(bot.get_status())
        elif command == 'test':
            test_signal_processor()
        else:
            print("Kullanım: python main.py [start|status|test]")
    else:
        # Default: Bot'u başlat
        bot.start()
    
    # Komut satırı kontrolü
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'start':
            bot.start()
        elif command == 'status':
            print(bot.get_status())
        elif command == 'test':
            test_signal_processor()
        else:
            print("Kullanım: python main.py [start|status|test]")
    else:
        # Default: Bot'u başlat
        bot.start()

def test_signal_processor():
    """Signal processor test"""
    print("\n🧪 MODULAR SIGNAL PROCESSOR TEST")
    print("=" * 50)
    
    processor = SignalProcessor()
    
    # Test sembolü
    result = processor.analyze_symbol_triple_ai('EURUSD-T')
    
    if result:
        combined = result['combined_analysis']
        print(f"\n✅ Modüler test başarılı!")
        print(f"   Sinyal: {combined['overall_signal']}")
        print(f"   Güven: %{combined['confidence']:.1f}")
        
        # Detaylı analiz
        processor.print_detailed_signal_analysis(
            processor.create_trade_signal(result, {
                'risk_details': {
                    'lot_size': 0.01,
                    'stop_loss': 1.16000,
                    'take_profit': 1.16500
                }
            })
        )
    else:
        print("❌ Test başarısız")

if __name__ == "__main__":
    main()