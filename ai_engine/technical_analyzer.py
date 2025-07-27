# ai_engine/technical_analyzer.py
"""
AI Trading Bot - Teknik Analiz Motoru
Bu modül tüm teknik göstergeleri hesaplar ve sinyal üretir
"""

import pandas as pd
import numpy as np
import pandas_ta as ta
import sys
import os

# Parent directory'yi ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import TECHNICAL_INDICATORS
from data_manager.mt5_connector import MT5Connector

class TechnicalAnalyzer:
    """Teknik analiz ve sinyal üretim sınıfı"""
    
    def __init__(self):
        """TechnicalAnalyzer'ı başlat"""
        self.indicators = TECHNICAL_INDICATORS
        print("📊 TechnicalAnalyzer başlatıldı")
    
    def calculate_all_indicators(self, df):
        """Tüm teknik göstergeleri hesapla"""
        if df is None or df.empty:
            print("❌ Veri yok, göstergeler hesaplanamadı")
            return None
        
        # DataFrame'i kopyala
        data = df.copy()
        
        try:
            # RSI hesapla
            data['rsi'] = ta.rsi(data['close'], length=self.indicators['RSI_PERIOD'])
            
            # MACD hesapla
            macd = ta.macd(data['close'], 
                          fast=self.indicators['MACD_FAST'],
                          slow=self.indicators['MACD_SLOW'], 
                          signal=self.indicators['MACD_SIGNAL'])
            
            data['macd'] = macd['MACD_12_26_9']
            data['macd_signal'] = macd['MACDs_12_26_9']
            data['macd_histogram'] = macd['MACDh_12_26_9']
            
            # Moving Averages
            data['ma_fast'] = ta.sma(data['close'], length=self.indicators['MA_FAST'])
            data['ma_slow'] = ta.sma(data['close'], length=self.indicators['MA_SLOW'])
            data['ema_fast'] = ta.ema(data['close'], length=self.indicators['MA_FAST'])
            data['ema_slow'] = ta.ema(data['close'], length=self.indicators['MA_SLOW'])
            
            # Bollinger Bands
            bb = ta.bbands(data['close'], length=self.indicators['BOLLINGER_PERIOD'])
            data['bb_upper'] = bb['BBU_20_2.0']
            data['bb_middle'] = bb['BBM_20_2.0']  
            data['bb_lower'] = bb['BBL_20_2.0']
            data['bb_width'] = bb['BBB_20_2.0']
            data['bb_percent'] = bb['BBP_20_2.0']
            
            # ATR (Average True Range)
            data['atr'] = ta.atr(data['high'], data['low'], data['close'], 
                               length=self.indicators['ATR_PERIOD'])
            
            # Stochastic
            stoch = ta.stoch(data['high'], data['low'], data['close'])
            data['stoch_k'] = stoch['STOCHk_14_3_3']
            data['stoch_d'] = stoch['STOCHd_14_3_3']
            
            # Williams %R
            data['williams_r'] = ta.willr(data['high'], data['low'], data['close'])
            
            # Volume indicators (eğer volume varsa)
            if 'volume' in data.columns:
                data['volume_sma'] = ta.sma(data['volume'], length=20)
                data['vwap'] = ta.vwap(data['high'], data['low'], data['close'], data['volume'])
            
            # Momentum
            data['momentum'] = ta.mom(data['close'], length=10)
            
            # CCI (Commodity Channel Index)
            data['cci'] = ta.cci(data['high'], data['low'], data['close'])
            
            print(f"✅ {len(data)} bar için teknik göstergeler hesaplandı")
            return data
            
        except Exception as e:
            print(f"❌ Teknik gösterge hesaplama hatası: {e}")
            return None
    
    def get_rsi_signal(self, rsi_current, rsi_previous=None):
        """RSI sinyali üret"""
        if pd.isna(rsi_current):
            return {'signal': 'NEUTRAL', 'strength': 0, 'reason': 'RSI verisi yok'}
        
        if rsi_current < 30:
            strength = min(100, (30 - rsi_current) * 3)
            return {'signal': 'BUY', 'strength': strength, 'reason': f'RSI oversold ({rsi_current:.1f})'}
        
        elif rsi_current > 70:
            strength = min(100, (rsi_current - 70) * 3)
            return {'signal': 'SELL', 'strength': strength, 'reason': f'RSI overbought ({rsi_current:.1f})'}
        
        elif 30 <= rsi_current <= 40:
            return {'signal': 'WEAK_BUY', 'strength': 30, 'reason': f'RSI düşük ({rsi_current:.1f})'}
        
        elif 60 <= rsi_current <= 70:
            return {'signal': 'WEAK_SELL', 'strength': 30, 'reason': f'RSI yüksek ({rsi_current:.1f})'}
        
        else:
            return {'signal': 'NEUTRAL', 'strength': 0, 'reason': f'RSI nötr ({rsi_current:.1f})'}
    
    def get_macd_signal(self, macd_current, macd_signal_current, macd_previous=None, macd_signal_previous=None):
        """MACD sinyali üret"""
        if pd.isna(macd_current) or pd.isna(macd_signal_current):
            return {'signal': 'NEUTRAL', 'strength': 0, 'reason': 'MACD verisi yok'}
        
        # MACD crossover
        if macd_current > macd_signal_current:
            if macd_previous is not None and macd_signal_previous is not None:
                if macd_previous <= macd_signal_previous:  # Bullish crossover
                    strength = min(100, abs(macd_current - macd_signal_current) * 1000)
                    return {'signal': 'BUY', 'strength': strength, 'reason': 'MACD bullish crossover'}
            
            return {'signal': 'WEAK_BUY', 'strength': 40, 'reason': 'MACD > Signal'}
        
        else:  # macd_current < macd_signal_current
            if macd_previous is not None and macd_signal_previous is not None:
                if macd_previous >= macd_signal_previous:  # Bearish crossover
                    strength = min(100, abs(macd_current - macd_signal_current) * 1000)
                    return {'signal': 'SELL', 'strength': strength, 'reason': 'MACD bearish crossover'}
            
            return {'signal': 'WEAK_SELL', 'strength': 40, 'reason': 'MACD < Signal'}
    
    def get_bollinger_signal(self, close_current, bb_upper, bb_lower, bb_percent):
        """Bollinger Bands sinyali üret"""
        if any(pd.isna(val) for val in [close_current, bb_upper, bb_lower, bb_percent]):
            return {'signal': 'NEUTRAL', 'strength': 0, 'reason': 'Bollinger verisi yok'}
        
        if close_current <= bb_lower:
            strength = min(100, (bb_lower - close_current) / bb_lower * 1000)
            return {'signal': 'BUY', 'strength': strength, 'reason': 'Fiyat Bollinger alt bantında'}
        
        elif close_current >= bb_upper:
            strength = min(100, (close_current - bb_upper) / bb_upper * 1000)
            return {'signal': 'SELL', 'strength': strength, 'reason': 'Fiyat Bollinger üst bantında'}
        
        elif bb_percent < 0.2:
            return {'signal': 'WEAK_BUY', 'strength': 30, 'reason': 'Bollinger alt %20\'de'}
        
        elif bb_percent > 0.8:
            return {'signal': 'WEAK_SELL', 'strength': 30, 'reason': 'Bollinger üst %80\'de'}
        
        else:
            return {'signal': 'NEUTRAL', 'strength': 0, 'reason': 'Bollinger orta bölge'}
    
    def get_ma_signal(self, close_current, ma_fast, ma_slow):
        """Moving Average sinyali üret"""
        if any(pd.isna(val) for val in [close_current, ma_fast, ma_slow]):
            return {'signal': 'NEUTRAL', 'strength': 0, 'reason': 'MA verisi yok'}
        
        if ma_fast > ma_slow and close_current > ma_fast:
            strength = min(100, ((ma_fast - ma_slow) / ma_slow) * 1000)
            return {'signal': 'BUY', 'strength': strength, 'reason': 'MA bullish trend'}
        
        elif ma_fast < ma_slow and close_current < ma_fast:
            strength = min(100, ((ma_slow - ma_fast) / ma_fast) * 1000)
            return {'signal': 'SELL', 'strength': strength, 'reason': 'MA bearish trend'}
        
        else:
            return {'signal': 'NEUTRAL', 'strength': 0, 'reason': 'MA karışık sinyal'}
    
    def get_stochastic_signal(self, stoch_k, stoch_d):
        """Stochastic sinyali üret"""
        if pd.isna(stoch_k) or pd.isna(stoch_d):
            return {'signal': 'NEUTRAL', 'strength': 0, 'reason': 'Stochastic verisi yok'}
        
        if stoch_k < 20 and stoch_d < 20:
            return {'signal': 'BUY', 'strength': 60, 'reason': 'Stochastic oversold'}
        
        elif stoch_k > 80 and stoch_d > 80:
            return {'signal': 'SELL', 'strength': 60, 'reason': 'Stochastic overbought'}
        
        else:
            return {'signal': 'NEUTRAL', 'strength': 0, 'reason': 'Stochastic nötr'}
    
    def analyze_symbol(self, symbol, timeframe='M1', bars=100):
        """Bir sembol için tam teknik analiz yap"""
        print(f"\n🔍 {symbol} teknik analizi başlıyor ({timeframe})...")
        
        # MT5'ten veri al
        with MT5Connector() as mt5_conn:
            if not mt5_conn.connected:
                return None
            
            # Market verilerini al
            df = mt5_conn.get_market_data(symbol, timeframe, bars)
            if df is None:
                return None
            
            # Teknik göstergeleri hesapla
            data_with_indicators = self.calculate_all_indicators(df)
            if data_with_indicators is None:
                return None
            
            # Son değerleri al
            last_row = data_with_indicators.iloc[-1]
            prev_row = data_with_indicators.iloc[-2] if len(data_with_indicators) > 1 else None
            
            # Tüm sinyalleri topla
            signals = {}
            
            # RSI sinyali
            signals['rsi'] = self.get_rsi_signal(last_row.get('rsi'))
            
            # MACD sinyali
            signals['macd'] = self.get_macd_signal(
                last_row.get('macd'), 
                last_row.get('macd_signal'),
                prev_row.get('macd') if prev_row is not None else None,
                prev_row.get('macd_signal') if prev_row is not None else None
            )
            
            # Bollinger sinyali
            signals['bollinger'] = self.get_bollinger_signal(
                last_row.get('close'),
                last_row.get('bb_upper'),
                last_row.get('bb_lower'),
                last_row.get('bb_percent')
            )
            
            # MA sinyali
            signals['ma'] = self.get_ma_signal(
                last_row.get('close'),
                last_row.get('ma_fast'),
                last_row.get('ma_slow')
            )
            
            # Stochastic sinyali
            signals['stochastic'] = self.get_stochastic_signal(
                last_row.get('stoch_k'),
                last_row.get('stoch_d')
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
            if total_buy_strength > total_sell_strength and total_buy_strength > 100:
                overall_signal = 'BUY'
                confidence = min(100, total_buy_strength / 3)
            elif total_sell_strength > total_buy_strength and total_sell_strength > 100:
                overall_signal = 'SELL'
                confidence = min(100, total_sell_strength / 3)
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
def test_technical_analyzer():
    """TechnicalAnalyzer'ı test et"""
    print("🧪 TechnicalAnalyzer Test Başlıyor...")
    print("=" * 50)
    
    analyzer = TechnicalAnalyzer()
    
    # EURUSD analizi
    result = analyzer.analyze_symbol('EURUSD', 'M5', 50)
    
    if result:
        print(f"\n✅ {result['symbol']} analizi başarılı!")
    else:
        print("❌ Analiz başarısız!")

if __name__ == "__main__":
    test_technical_analyzer()