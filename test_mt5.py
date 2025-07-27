import MetaTrader5 as mt5

# MetaTrader 5 terminaline bağlan
if not mt5.initialize():
    print("❌ Bağlantı kurulamadı:", mt5.last_error())
else:
    print("✅ Bağlantı başarılı!")

# Bağlantıyı kapat
mt5.shutdown()
