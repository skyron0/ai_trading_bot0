# ai_engine/simple_technical_analyzer.py
"""
AI Trading Bot - Basit Teknik Analiz Motoru (pandas_ta olmadan)
Manuel hesaplanan teknik göstergeler
"""

import pandas as pd
import numpy as np
import sys
import os

# Parent directory'yi ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import TECHNICAL_INDICATORS
from data_manager.mt5_connector import MT5Connector

class SimpleTechnicalAnalyzer:
    """Basit teknik analiz sınıfı - kendi hesaplamalarımızla"""
    
    def __init__(self):
        """SimpleTechnicalAnalyzer'ı başlat"""
        self.indicators = TECHNICAL_INDICATORS
        print("📊 SimpleTechnicalAnalyzer başlatıldı")
    
    def calculate_sma(self, data, period):
        """Simple Moving Average hesapla"""
        return data.rolling(window=period).mean()
    
    def calculate_ema(self, data, period):
        """Exponential Moving Average hesapla"""
        return data.ewm(span=period).mean()
    
    def calculate_rsi(self, data, period=14):
        """RSI hesapla"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, data, fast=12, slow=26, signal=9):
        """MACD hesapla"""
        ema_fast = self.calculate_ema(data, fast)
        ema_slow = self.calculate_ema(data, slow)
        
        macd_line = ema_fast - ema_slow
        signal_line = self.calculate_ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def calculate_bollinger_bands(self, data, period=20, std_dev=2):
        """Bollinger Bands hesapla"""
        sma = self.calculate_sma(data, period)
        std = data.rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        # Bollinger %B
        bb_percent = (data - lower_band) / (upper_band - lower_band)
        
        return upper_band, sma, lower_band, bb_percent
    
    def calculate_stochastic(self, high, low, close, k_period=14, d_period=3):
        """Stochastic Oscillator hesapla"""
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return k_percent, d_percent
    
    def calculate_atr(self, high, low, close, period=14):
        """Average True Range hesapla"""
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr
    
    def calculate_all_indicators(self, df):
        """Tüm teknik göstergeleri hesapla"""
        if df is None or df.empty:
            print("❌ Veri yok, göstergeler hesaplanamadı")
            return None
        
        # DataFrame'i kopyala
        data = df.copy()
        
        try:
            print(f"🔧 {len(data)} bar için göstergeler hesaplanıyor...")
            
            # RSI
            data['rsi'] = self.calculate_rsi(data['close'], self.indicators['RSI_PERIOD'])
            
            # Moving Averages
            data['ma_fast'] = self.calculate_sma(data['close'], self.indicators['MA_FAST'])
            data['ma_slow'] = self.calculate_sma(data['close'], self.indicators['MA_SLOW'])
            data['ema_fast'] = self.calculate_ema(data['close'], self.indicators['MA_FAST'])
            data['ema_slow'] = self.calculate_ema(data['close'], self.indicators['MA_SLOW'])
            
            # MACD
            macd_line, signal_line, histogram = self.calculate_macd(
                data['close'], 
                self.indicators['MACD_FAST'],
                self.indicators['MACD_SLOW'],
                self.indicators['MACD_SIGNAL']
            )
            data['macd'] = macd_line
            data['macd_signal'] = signal_line
            data['macd_histogram'] = histogram
            
            # Bollinger Bands
            bb_upper, bb_middle, bb_lower, bb_percent = self.calculate_bollinger_bands(
                data['close'], self.indicators['BOLLINGER_PERIOD']
            )
            data['bb_upper'] = bb_upper
            data['bb_middle'] = bb_middle
            data['bb_lower'] = bb_lower
            data['bb_percent'] = bb_percent
            
            # Stochastic
            stoch_k, stoch_d = self.calculate_stochastic(data['high'], data['low'], data['close'])
            data['stoch_k'] = stoch_k
            data['stoch_d'] = stoch_d
            
            # ATR
            data['atr'] = self.calculate_atr(data['high'], data['low'], data['close'], 
                                           self.indicators['ATR_PERIOD'])
            
            # Williams %R
            period = 14
            highest_high = data['high'].rolling(window=period).max()
            lowest_low = data['low'].rolling(window=period).min()
            data['williams_r'] = -100 * ((highest_high - data['close']) / (highest_high - lowest_low))
            
            # Momentum
            data['momentum'] = data['close'] / data['close'].shift(10) * 100
            
            print(f"✅ Tüm teknik göstergeler hesaplandı")
            return data
            
        except Exception as e:
            print(f"❌ Teknik gösterge hesaplama hatası: {e}")
            return None
    
    def get_rsi_signal(self, rsi_current):
        """RSI sinyali üret"""
        if pd.isna(rsi_current):
            return {'signal': 'NEUTRAL', 'strength': 0, 'reason': 'RSI verisi yok'}
        
        if rsi_current < 30:
            strength = min(100, (30 - rsi_current) * 2.5)
            return {'signal': 'BUY', 'strength': strength, 'reason': f'RSI oversold ({rsi_current:.1f})'}
        
        elif rsi_current > 70:
            strength = min(100, (rsi_current - 70) * 2.5)
            return {'signal': 'SELL', 'strength': strength, 'reason': f'RSI overbought ({rsi_current:.1f})'}
        
        elif 30 <= rsi_current <= 40:
            return {'signal': 'WEAK_BUY', 'strength': 25, 'reason': f'RSI düşük ({rsi_current:.1f})'}
        
        elif 60 <= rsi_current <= 70:
            return {'signal': 'WEAK_SELL', 'strength': 25, 'reason': f'RSI yüksek ({rsi_current:.1f})'}
        
        else:
            return {'signal': 'NEUTRAL', 'strength': 0, 'reason': f'RSI nötr ({rsi_current:.1f})'}
    
    def get_macd_signal(self, macd_current, macd_signal_current, macd_previous=None, macd_signal_previous=None):
        """MACD sinyali üret"""
        if pd.isna(macd_current) or pd.isna(macd_signal_current):
            return {'signal': 'NEUTRAL', 'strength': 0, 'reason': 'MACD verisi yok'}
        
        # MACD crossover kontrol
        if macd_current > macd_signal_current:
            if (macd_previous is not None and macd_signal_previous is not None and 
                macd_previous <= macd_signal_previous):
                strength = 70
                return {'signal': 'BUY', 'strength': strength, 'reason': 'MACD bullish crossover'}
            
            return {'signal': 'WEAK_BUY', 'strength': 30, 'reason': 'MACD > Signal'}
        
        else:
            if (macd_previous is not None and macd_signal_previous is not None and 
                macd_previous >= macd_signal_previous):
                strength = 70
                return {'signal': 'SELL', 'strength': strength, 'reason': 'MACD bearish crossover'}
            
            return {'signal': 'WEAK_SELL', 'strength': 30, 'reason': 'MACD < Signal'}
    
    def get_bollinger_signal(self, close_current, bb_upper, bb_lower, bb_percent):
        """Bollinger Bands sinyali üret"""
        if any(pd.isna(val) for val in [close_current, bb_upper, bb_lower, bb_percent]):
            return {'signal': 'NEUTRAL', 'strength': 0, 'reason': 'Bollinger verisi yok'}
        
        if close_current <= bb_lower:
            strength = 80
            return {'signal': 'BUY', 'strength': strength, 'reason': 'Fiyat Bollinger alt bantında'}
        
        elif close_current >= bb_upper:
            strength = 80
            return {'signal': 'SELL', 'strength': strength, 'reason': 'Fiyat Bollinger üst bantında'}
        
        elif bb_percent < 0.2:
            return {'signal': 'WEAK_BUY', 'strength': 40, 'reason': 'Bollinger alt %20\'de'}
        
        elif bb_percent > 0.8:
            return {'signal': 'WEAK_SELL', 'strength': 40, 'reason': 'Bollinger üst %80\'de'}
        
        else:
            return {'signal': 'NEUTRAL', 'strength': 0, 'reason': 'Bollinger orta bölge'}
    
    def get_ma_signal(self, close_current, ma_fast, ma_slow):
        """Moving Average sinyali üret"""
        if any(pd.isna(val) for val in [close_current, ma_fast, ma_slow]):
            return {'signal': 'NEUTRAL', 'strength': 0, 'reason': 'MA verisi yok'}
        
        if ma_fast > ma_slow and close_current > ma_fast:
            strength = 50
            return {'signal': 'BUY', 'strength': strength, 'reason': 'MA bullish trend'}
        
        elif ma_fast < ma_slow and close_current < ma_fast:
            strength = 50
            return {'signal': 'SELL', 'strength': strength, 'reason': 'MA bearish trend'}
        
        else:
            return {'signal': 'NEUTRAL', 'strength': 0, 'reason': 'MA karışık sinyal'}
    
    def analyze_symbol(self, symbol, timeframe='M1', bars=100):
        """Bir sembol için tam teknik analiz yap"""
        print(f"\n🔍 {symbol} teknik analizi başlıyor ({timeframe})...")
        
        with MT5Connector() as mt5_conn:
            if not mt5_conn.connected:
                print("❌ MT5 bağlantısı yok")
                return None
            
            # Market verilerini al
            df = mt5_conn.get_market_data(symbol, timeframe, bars)
            if df is None:
                print("❌ Market verisi alınamadı")
                return None
            
            # Teknik göstergeleri hesapla
            data_with_indicators = self.calculate_all_indicators(df)
            if data_with_indicators is None:
                return None
            
            # Son değerleri al
            last_row = data_with_indicators.iloc[-1]
            prev_row = data_with_indicators.iloc[-2] if len(data_with_indicators) > 1 else None
            
            # Sinyalleri topla
            signals = {}
            
            signals['rsi'] = self.get_rsi_signal(last_row.get('rsi'))
            
            signals['macd'] = self.get_macd_signal(
                last_row.get('macd'), 
                last_row.get('macd_signal'),
                prev_row.get('macd') if prev_row is not None else None,
                prev_row.get('macd_signal') if prev_row is not None else None
            )
            
            signals['bollinger'] = self.get_bollinger_signal(
                last_row.get('close'),
                last_row.get('bb_upper'),
                last_row.get('bb_lower'),
                last_row.get('bb_percent')
            )
            
            signals['ma'] = self.get_ma_signal(
                last_row.get('close'),
                last_row.get('ma_fast'),
                last_row.get('ma_slow')
            )
            
            # Genel sinyal gücünü hesapla
            total_buy_strength = 0
            total_sell_strength = 0
            
            for indicator, signal_data in signals.items():
                if signal_data['signal'] in ['BUY', 'WEAK_BUY']:
                    total_buy_strength += signal_data['strength']
                elif signal_data['signal'] in ['SELL', 'WEAK_SELL']:
                    total_sell_strength += signal_data['strength']
            
            # Dominant sinyali belirle
            if total_buy_strength > total_sell_strength and total_buy_strength > 80:
                overall_signal = 'BUY'
                confidence = min(100, total_buy_strength / 2)
            elif total_sell_strength > total_buy_strength and total_sell_strength > 80:
                overall_signal = 'SELL'
                confidence = min(100, total_sell_strength / 2)
            else:
                overall_signal = 'NEUTRAL'
                confidence = 0
            
            result = {
                'symbol': symbol,
                'timeframe': timeframe,
                'timestamp': last_row.name,
                'current_price': last_row.get('close'),
                'overall_signal': overall_signal,
                'confidence': confidence,
                'buy_strength': total_buy_strength,
                'sell_strength': total_sell_strength,
                'signals': signals,
                'indicators': {
                    'rsi': last_row.get('rsi'),
                    'macd': last_row.get('macd'),
                    'macd_signal': last_row.get('macd_signal'),
                    'bb_percent': last_row.get('bb_percent'),
                    'ma_fast': last_row.get('ma_fast'),
                    'ma_slow': last_row.get('ma_slow'),
                    'stoch_k': last_row.get('stoch_k'),
                    'atr': last_row.get('atr')
                }
            }
            
            self._print_analysis_summary(result)
            return result
    
    def _print_analysis_summary(self, result):
        """Analiz özetini yazdır"""
        print(f"\n📊 {result['symbol']} TEKNİK ANALİZ ÖZETİ")
        print("=" * 40)
        print(f"💰 Güncel Fiyat: {result['current_price']:.5f}")
        print(f"🎯 Genel Sinyal: {result['overall_signal']}")
        print(f"🔥 Güven: %{result['confidence']:.1f}")
        print(f"📈 Buy Gücü: {result['buy_strength']:.0f}")
        print(f"📉 Sell Gücü: {result['sell_strength']:.0f}")
        
        print(f"\n📋 Gösterge Detayları:")
        for indicator, signal in result['signals'].items():
            print(f"   {indicator.upper()}: {signal['signal']} ({signal['strength']:.0f}) - {signal['reason']}")

# Test fonksiyonu
def test_simple_analyzer():
    """SimpleTechnicalAnalyzer'ı test et"""
    print("🧪 SimpleTechnicalAnalyzer Test Başlıyor...")
    print("=" * 50)
    
    analyzer = SimpleTechnicalAnalyzer()
    
    # EURUSD analizi
    result = analyzer.analyze_symbol('EURUSD', 'M5', 50)
    
    if result:
        print(f"\n✅ {result['symbol']} analizi başarılı!")
    else:
        print("❌ Analiz başarısız!")

if __name__ == "__main__":
    test_simple_analyzer()