# data_manager/mt5_connector.py
"""
AI Trading Bot - MetaTrader 5 Bağlantı Yöneticisi
Bu sınıf MT5 ile tüm bağlantı işlemlerini yönetir
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import sys
import os

# Parent directory'yi ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.credentials import MT5_LOGIN, MT5_PASSWORD, MT5_SERVER
from config.settings import TRADING_SYMBOLS, TIMEFRAMES

class MT5Connector:
    """MetaTrader 5 bağlantı ve veri yöneticisi"""
    
    def __init__(self):
        """MT5Connector sınıfını başlat"""
        self.connected = False
        self.account_info = None
        self.login_attempts = 0
        self.max_login_attempts = 3
        
        print("🔧 MT5Connector başlatılıyor...")
    
    def connect(self):
        """MT5'e bağlan"""
        try:
            # MT5'i başlat
            if not mt5.initialize():
                print(f"❌ MT5 başlatılamadı: {mt5.last_error()}")
                return False
            
            # Hesaba giriş yap
            authorized = mt5.login(MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER)
            
            if not authorized:
                print(f"❌ MT5 giriş başarısız: {mt5.last_error()}")
                self.login_attempts += 1
                
                if self.login_attempts >= self.max_login_attempts:
                    print(f"❌ Max giriş denemesi aşıldı ({self.max_login_attempts})")
                    return False
                
                return False
            
            # Hesap bilgilerini al
            self.account_info = mt5.account_info()
            if self.account_info is None:
                print("❌ Hesap bilgileri alınamadı")
                return False
            
            self.connected = True
            self.login_attempts = 0
            
            print("✅ MT5 bağlantısı başarılı")
            print(f"   Hesap: {self.account_info.login}")
            print(f"   Bakiye: ${self.account_info.balance:,.2f}")
            print(f"   Server: {self.account_info.server}")
            
            return True
            
        except Exception as e:
            print(f"❌ MT5 bağlantı hatası: {e}")
            return False
    
    def disconnect(self):
        """MT5 bağlantısını kapat"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            print("🔌 MT5 bağlantısı kapatıldı")
    
    def is_connected(self):
        """Bağlantı durumunu kontrol et"""
        if not self.connected:
            return False
        
        # Terminal bağlantısını kontrol et
        terminal_info = mt5.terminal_info()
        if terminal_info is None:
            return False
        
        return terminal_info.connected
    
    def get_account_info(self):
        """Güncel hesap bilgilerini al"""
        if not self.is_connected():
            print("❌ MT5 bağlantısı yok")
            return None
        
        account = mt5.account_info()
        if account is None:
            print("❌ Hesap bilgileri alınamadı")
            return None
        
        return {
            'login': account.login,
            'balance': account.balance,
            'equity': account.equity,
            'margin': account.margin,
            'free_margin': account.margin_free,
            'margin_level': account.margin_level,
            'profit': account.profit,
            'server': account.server,
            'currency': account.currency,
            'leverage': account.leverage
        }
    
    def get_symbol_info(self, symbol):
        """Simge bilgilerini al"""
        if not self.is_connected():
            print(f"❌ MT5 bağlantısı yok - {symbol}")
            return None
        
        # Simgeyi seç
        if not mt5.symbol_select(symbol, True):
            print(f"❌ {symbol} simgesi seçilemedi")
            return None
        
        info = mt5.symbol_info(symbol)
        if info is None:
            print(f"❌ {symbol} simge bilgileri alınamadı")
            return None
        
        return {
            'symbol': symbol,
            'bid': info.bid,
            'ask': info.ask,
            'last': info.last,
            'spread': info.spread,
            'point': info.point,
            'digits': info.digits,
            'volume_min': info.volume_min,
            'volume_max': info.volume_max,
            'volume_step': info.volume_step,
            'time': datetime.fromtimestamp(info.time)
        }
    
    def get_market_data(self, symbol, timeframe, count=100):
        """Market verilerini al"""
        if not self.is_connected():
            print(f"❌ MT5 bağlantısı yok - {symbol}")
            return None
        
        # Timeframe'i MT5 formatına çevir
        mt5_timeframe = self._get_mt5_timeframe(timeframe)
        if mt5_timeframe is None:
            print(f"❌ Geçersiz timeframe: {timeframe}")
            return None
        
        # Veriyi al
        rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)
        
        if rates is None:
            print(f"❌ {symbol} için veri alınamadı")
            return None
        
        # DataFrame'e çevir
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        
        return df
    
    def get_current_price(self, symbol):
        """Güncel fiyatı al"""
        symbol_info = self.get_symbol_info(symbol)
        if symbol_info is None:
            return None
        
        return {
            'symbol': symbol,
            'bid': symbol_info['bid'],
            'ask': symbol_info['ask'],
            'last': symbol_info['last'],
            'spread': symbol_info['spread'],
            'time': symbol_info['time']
        }
    
    def get_positions(self):
        """Açık pozisyonları al"""
        if not self.is_connected():
            print("❌ MT5 bağlantısı yok")
            return []
        
        positions = mt5.positions_get()
        if positions is None:
            return []
        
        position_list = []
        for pos in positions:
            position_list.append({
                'ticket': pos.ticket,
                'symbol': pos.symbol,
                'type': 'BUY' if pos.type == mt5.ORDER_TYPE_BUY else 'SELL',
                'volume': pos.volume,
                'open_price': pos.price_open,
                'current_price': pos.price_current,
                'sl': pos.sl,
                'tp': pos.tp,
                'profit': pos.profit,
                'swap': pos.swap,
                'commission': pos.commission,
                'time_open': datetime.fromtimestamp(pos.time),
                'comment': pos.comment
            })
        
        return position_list
    
    def _get_mt5_timeframe(self, timeframe):
        """Timeframe'i MT5 formatına çevir"""
        timeframe_map = {
            'M1': mt5.TIMEFRAME_M1,
            'M5': mt5.TIMEFRAME_M5,
            'M15': mt5.TIMEFRAME_M15,
            'M30': mt5.TIMEFRAME_M30,
            'H1': mt5.TIMEFRAME_H1,
            'H4': mt5.TIMEFRAME_H4,
            'D1': mt5.TIMEFRAME_D1
        }
        
        return timeframe_map.get(timeframe.upper())
    
    def check_trading_allowed(self):
        """Trading'in açık olup olmadığını kontrol et"""
        if not self.is_connected():
            return False
        
        terminal_info = mt5.terminal_info()
        if terminal_info is None:
            return False
        
        return terminal_info.trade_allowed
    
    def __enter__(self):
        """Context manager - with statement için"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager - with statement bitince"""
        self.disconnect()


# Test fonksiyonu
def test_connector():
    """MT5Connector'ı test et"""
    print("🧪 MT5Connector Test Başlıyor...")
    print("=" * 50)
    
    # Context manager ile test
    with MT5Connector() as mt5_conn:
        if not mt5_conn.connected:
            print("❌ Bağlantı başarısız!")
            return
        
        print("\n📊 Hesap Bilgileri:")
        account = mt5_conn.get_account_info()
        if account:
            for key, value in account.items():
                print(f"   {key}: {value}")
        
        print("\n💱 Simge Testleri:")
        for symbol_name in TRADING_SYMBOLS.keys():
            symbol = TRADING_SYMBOLS[symbol_name]['symbol']
            info = mt5_conn.get_symbol_info(symbol)
            if info:
                print(f"   ✅ {symbol}: Bid={info['bid']}, Ask={info['ask']}, Spread={info['spread']}")
        
        print("\n📈 Market Verisi Testi:")
        df = mt5_conn.get_market_data('EURUSD', 'M1', 5)
        if df is not None:
            print(f"   ✅ EURUSD son 5 M1 bar alındı")
            print(df[['open', 'high', 'low', 'close']].tail(3))
        
        print("\n📋 Açık Pozisyonlar:")
        positions = mt5_conn.get_positions()
        print(f"   Toplam açık pozisyon: {len(positions)}")
        
        print("\n🛡️ Trading Durumu:")
        trading_allowed = mt5_conn.check_trading_allowed()
        print(f"   Trading izni: {'✅ Var' if trading_allowed else '❌ Yok'}")

if __name__ == "__main__":
    test_connector()