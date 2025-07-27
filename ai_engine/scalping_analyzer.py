# ai_engine/scalping_analyzer.py
"""
AI Trading Bot - Scalping Analyzer
Ultra-fast scalping sinyalleri için özel analiz motoru
"""

import numpy as np
import sys
import os
from datetime import datetime, timedelta

# Parent directory'yi ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_manager.mt5_connector import MT5Connector

class ScalpingAnalyzer:
    """Scalping özel analiz sınıfı"""
    
    def __init__(self):
        """ScalpingAnalyzer'ı başlat"""
        self.scalping_timeframes = ['M1']  # Ultra-fast scalping
        self.min_spread_pips = {
            'EURUSD-T': 1.5,  # Max 1.5 pip spread
            'GOLD-T': 3.0,    # Max 3.0 pip spread  
            'BTCUSD-T': 50.0  # Max 50 pip spread
        }
        
        print("⚡ ScalpingAnalyzer başlatıldı - Ultra-fast mode")
    
    def _check_spread_simple(self, symbol):
        """Basit spread kontrolü"""
        try:
            import MetaTrader5 as mt5
            symbol_info = mt5.symbol_info(symbol)
            
            if symbol_info:
                spread_pips = symbol_info.spread * symbol_info.point * 10000
                max_spread = self.min_spread_pips.get(symbol, 2.0)
                
                return {
                    'allowed': spread_pips <= max_spread,
                    'spread_pips': spread_pips,
                    'max_allowed': max_spread
                }
            else:
                return {'allowed': True, 'spread_pips': 1.0, 'max_allowed': 2.0}
                
        except:
            return {'allowed': True, 'spread_pips': 1.0, 'max_allowed': 2.0}
    
    def _calculate_simple_indicators(self, bars):
        """Basit indikatörler"""
        try:
            closes = [bar['close'] for bar in bars]
            
            # Basit RSI
            if len(closes) >= 10:
                rsi = self._simple_rsi(closes, 5)
            else:
                rsi = 50
            
            # Basit EMA
            if len(closes) >= 5:
                ema5 = sum(closes[-5:]) / 5
                ema13 = sum(closes[-13:]) / 13 if len(closes) >= 13 else ema5
            else:
                ema5 = closes[-1]
                ema13 = closes[-1]
            
            return {
                'rsi': rsi,
                'ema5': ema5,
                'ema13': ema13,
                'current_price': closes[-1]
            }
            
        except Exception as e:
            print(f"❌ İndikatör hesaplama hatası: {e}")
            return {'rsi': 50, 'ema5': 0, 'ema13': 0, 'current_price': 0}
    
    def _simple_rsi(self, prices, period=5):
        """Basit RSI hesaplama"""
        try:
            if len(prices) < period + 1:
                return 50
            
            gains = []
            losses = []
            
            for i in range(1, len(prices)):
                change = prices[i] - prices[i-1]
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(-change)
            
            if len(gains) >= period:
                avg_gain = sum(gains[-period:]) / period
                avg_loss = sum(losses[-period:]) / period
                
                if avg_loss == 0:
                    return 100
                
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
                return rsi
            
            return 50
            
        except:
            return 50
    
    def _generate_simple_signal(self, indicators):
        """Basit sinyal üretimi"""
        try:
            buy_score = 0
            sell_score = 0
            
            rsi = indicators.get('rsi', 50)
            ema5 = indicators.get('ema5', 0)
            ema13 = indicators.get('ema13', 0)
            
            # RSI sinyalleri
            if rsi < 30:
                buy_score += 40
            elif rsi > 70:
                sell_score += 40
            
            # EMA crossover
            if ema5 > ema13:
                buy_score += 30
            else:
                sell_score += 30
            
            # Sonuç
            if buy_score > sell_score and buy_score > 50:
                return {'signal': 'BUY', 'strength': buy_score, 'confidence': buy_score * 0.8}
            elif sell_score > buy_score and sell_score > 50:
                return {'signal': 'SELL', 'strength': sell_score, 'confidence': sell_score * 0.8}
            else:
                return {'signal': 'NEUTRAL', 'strength': 0, 'confidence': 0}
                
        except:
            return {'signal': 'NEUTRAL', 'strength': 0, 'confidence': 0}
    
    def _print_simple_scalping_result(self, result):
        """Basit sonuç yazdırma"""
        try:
            print(f"\n⚡ {result['symbol']} SCALPING SONUCU:")
            print("=" * 40)
            print(f"🎯 Sinyal: {result['signal']} (Güç: {result['strength']:.0f})")
            print(f"🔥 Güven: %{result['confidence']:.1f}")
            print(f"📊 Spread: {result['spread_info']['spread_pips']:.1f} pips")
            print(f"✅ Scalping Ready: {'YES' if result['scalping_ready'] else 'NO'}")
            print(f"💰 Entry Price: {result['entry_price']:.5f}")
            
            indicators = result['indicators']
            print(f"\n📋 İNDİKATÖRLER:")
            print(f"   RSI: {indicators.get('rsi', 0):.1f}")
            print(f"   EMA5: {indicators.get('ema5', 0):.5f}")
            print(f"   EMA13: {indicators.get('ema13', 0):.5f}")
            
        except Exception as e:
            print(f"❌ Sonuç yazdırma hatası: {e}")
    
    def analyze_scalping_opportunity(self, symbol):
        """Scalping fırsatı analizi"""
        try:
            print(f"\n⚡ {symbol} SCALPING ANALİZİ (M1)...")
            
            # MT5 bağlantısını kontrol et
            import MetaTrader5 as mt5
            
            if not mt5.initialize():
                print("❌ MT5 başlatılamadı")
                return None
            
            # Hesap bilgilerini kontrol et
            account_info = mt5.account_info()
            if account_info is None:
                print("❌ MT5 hesap bilgisi alınamadı")
                return None
                
            print(f"✅ MT5 bağlı - Hesap: {account_info.login}")
            
            # Mevcut sembolleri listele
            print("🔍 Mevcut semboller kontrol ediliyor...")
            symbols = mt5.symbols_get()
            if symbols:
                # EUR içeren sembolleri bul
                eur_symbols = [s.name for s in symbols if 'EUR' in s.name and 'USD' in s.name]
                print(f"📊 EUR/USD sembolleri: {eur_symbols[:5]}")  # İlk 5'i göster
                
                if eur_symbols:
                    selected_symbol = eur_symbols[0]  # İlkini kullan
                    print(f"🎯 Kullanılacak symbol: {selected_symbol}")
                else:
                    print("❌ EUR/USD symbol bulunamadı")
                    return None
            else:
                print("❌ Symbol listesi alınamadı")
                return None
            
            # Symbol'ü seç
            print(f"🔧 {selected_symbol} sembolü seçiliyor...")
            if not mt5.symbol_select(selected_symbol, True):
                print(f"❌ {selected_symbol} sembolü seçilemedi")
                return None
            
            print("🔍 M1 verisi alınıyor...")
            rates = mt5.copy_rates_from_pos(selected_symbol, mt5.TIMEFRAME_M1, 0, 50)
            
            if rates is None:
                print(f"❌ {selected_symbol} için M1 verisi alınamadı")
                return None
                
            if len(rates) < 20:
                print(f"❌ {selected_symbol} için yeterli veri yok: {len(rates)} bar")
                return None
            
            print(f"✅ {len(rates)} bar M1 verisi alındı")
            
            # Bars formatına çevir
            print("🔄 Veri formatlanıyor...")
            bars = []
            for i, rate in enumerate(rates):
                try:
                    bar = {
                        'open': float(rate['open']),
                        'high': float(rate['high']),
                        'low': float(rate['low']),
                        'close': float(rate['close']),
                        'volume': int(rate['tick_volume']) if 'tick_volume' in rate.dtype.names else 0
                    }
                    bars.append(bar)
                except Exception as e:
                    print(f"❌ Bar {i} formatlanırken hata: {e}")
                    continue
            
            if len(bars) < 20:
                print(f"❌ Formatlanmış bar sayısı yetersiz: {len(bars)}")
                return None
            
            print(f"✅ {len(bars)} bar formatlandı")
            
            # Spread kontrolü
            print("📊 Spread kontrol ediliyor...")
            spread_check = self._check_spread_simple(selected_symbol)
            
            # Basit scalping indikatörleri
            print("📈 İndikatörler hesaplanıyor...")
            indicators = self._calculate_simple_indicators(bars)
            
            # Basit sinyal
            print("🎯 Sinyal üretiliyor...")
            signal = self._generate_simple_signal(indicators)
            
            result = {
                'symbol': selected_symbol,
                'original_symbol': symbol,
                'timeframe': 'M1',
                'signal': signal['signal'],
                'strength': signal['strength'],
                'confidence': signal['confidence'],
                'spread_info': spread_check,
                'indicators': indicators,
                'entry_price': bars[-1]['close'],
                'timestamp': datetime.now(),
                'scalping_ready': spread_check['allowed'] and signal['strength'] > 50
            }
            
            self._print_simple_scalping_result(result)
            return result
                
        except Exception as e:
            print(f"❌ Scalping analiz hatası: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _check_spread(self, symbol, mt5_conn):
        """Spread kontrolü - scalping için kritik"""
        try:
            import MetaTrader5 as mt5
            
            # MT5'ten symbol info al
            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                return {'allowed': False, 'reason': 'Symbol info alınamadı'}
            
            # Spread hesapla (pip cinsinden)
            point = symbol_info.point
            spread_points = symbol_info.spread
            
            # Pip değerine çevir
            if 'JPY' in symbol:
                spread_pips = spread_points * point * 100  # JPY için
            else:
                spread_pips = spread_points * point * 10000  # Diğer paralar için
            
            # Symbol için max spread kontrolü
            max_spread = self.min_spread_pips.get(symbol, 2.0)
            
            if spread_pips <= max_spread:
                return {
                    'allowed': True,
                    'spread_pips': spread_pips,
                    'max_allowed': max_spread,
                    'status': 'GOOD'
                }
            else:
                return {
                    'allowed': False,
                    'spread_pips': spread_pips,
                    'max_allowed': max_spread,
                    'status': 'TOO_HIGH',
                    'reason': f'Spread çok yüksek: {spread_pips:.1f} > {max_spread}'
                }
                
        except Exception as e:
            print(f"❌ Spread kontrolü hatası: {e}")
            return {'allowed': True, 'spread_pips': 1.0, 'max_allowed': 2.0, 'status': 'UNKNOWN'}
    
    def _calculate_scalping_indicators(self, bars):
        """Scalping özel indikatörleri hesapla"""
        try:
            closes = np.array([bar['close'] for bar in bars])
            highs = np.array([bar['high'] for bar in bars])
            lows = np.array([bar['low'] for bar in bars])
            volumes = np.array([bar.get('volume', 0) for bar in bars])
            
            # Stochastic Oscillator (scalping favorisi)
            stoch_k, stoch_d = self._calculate_stochastic(highs, lows, closes, 14, 3)
            
            # Williams %R (momentum)
            williams_r = self._calculate_williams_r(highs, lows, closes, 14)
            
            # CCI (Commodity Channel Index)
            cci = self._calculate_cci(highs, lows, closes, 20)
            
            # Awesome Oscillator
            ao = self._calculate_awesome_oscillator(highs, lows)
            
            # RSI (ultra-fast 5 period)
            rsi_fast = self._calculate_rsi(closes, 5)
            
            # ADX ve Directional Movement (+DI, -DI)
            adx, plus_di, minus_di = self._calculate_adx_di(highs, lows, closes, 14)
            
            # EMA crossovers (5 vs 13)
            ema5 = self._calculate_ema(closes, 5)
            ema13 = self._calculate_ema(closes, 13)
            
            # Price action patterns
            price_action = self._detect_price_action_patterns(bars[-10:])  # Son 10 bar
            
            return {
                'stoch_k': stoch_k[-1] if len(stoch_k) > 0 else 50,
                'stoch_d': stoch_d[-1] if len(stoch_d) > 0 else 50,
                'williams_r': williams_r[-1] if len(williams_r) > 0 else -50,
                'cci': cci[-1] if len(cci) > 0 else 0,
                'awesome_oscillator': ao[-1] if len(ao) > 0 else 0,
                'rsi_fast': rsi_fast[-1] if len(rsi_fast) > 0 else 50,
                'adx': adx[-1] if len(adx) > 0 else 20,
                'plus_di': plus_di[-1] if len(plus_di) > 0 else 25,
                'minus_di': minus_di[-1] if len(minus_di) > 0 else 25,
                'ema5': ema5[-1] if len(ema5) > 0 else closes[-1],
                'ema13': ema13[-1] if len(ema13) > 0 else closes[-1],
                'price_action': price_action,
                'current_price': closes[-1]
            }
            
        except Exception as e:
            print(f"❌ Scalping indikatör hatası: {e}")
            return {}
    
    def _calculate_stochastic(self, highs, lows, closes, k_period=14, d_period=3):
        """Stochastic Oscillator hesapla"""
        try:
            if len(closes) < k_period:
                return np.array([]), np.array([])
            
            k_values = []
            for i in range(k_period - 1, len(closes)):
                high_max = np.max(highs[i - k_period + 1:i + 1])
                low_min = np.min(lows[i - k_period + 1:i + 1])
                if high_max != low_min:
                    k = 100 * (closes[i] - low_min) / (high_max - low_min)
                else:
                    k = 50
                k_values.append(k)
            
            k_values = np.array(k_values)
            
            # %D hesapla (moving average of %K)
            if len(k_values) >= d_period:
                d_values = np.convolve(k_values, np.ones(d_period)/d_period, mode='valid')
            else:
                d_values = k_values
            
            return k_values, d_values
            
        except:
            return np.array([50]), np.array([50])
    
    def _calculate_williams_r(self, highs, lows, closes, period=14):
        """Williams %R hesapla"""
        try:
            if len(closes) < period:
                return np.array([])
            
            wr_values = []
            for i in range(period - 1, len(closes)):
                high_max = np.max(highs[i - period + 1:i + 1])
                low_min = np.min(lows[i - period + 1:i + 1])
                if high_max != low_min:
                    wr = -100 * (high_max - closes[i]) / (high_max - low_min)
                else:
                    wr = -50
                wr_values.append(wr)
            
            return np.array(wr_values)
            
        except:
            return np.array([-50])
    
    def _calculate_cci(self, highs, lows, closes, period=20):
        """CCI (Commodity Channel Index) hesapla"""
        try:
            if len(closes) < period:
                return np.array([])
            
            typical_prices = (highs + lows + closes) / 3
            cci_values = []
            
            for i in range(period - 1, len(typical_prices)):
                tp_slice = typical_prices[i - period + 1:i + 1]
                sma = np.mean(tp_slice)
                mad = np.mean(np.abs(tp_slice - sma))
                if mad != 0:
                    cci = (typical_prices[i] - sma) / (0.015 * mad)
                else:
                    cci = 0
                cci_values.append(cci)
            
            return np.array(cci_values)
            
        except:
            return np.array([0])
    
    def _calculate_awesome_oscillator(self, highs, lows):
        """Awesome Oscillator hesapla"""
        try:
            if len(highs) < 34:
                return np.array([])
            
            median_prices = (highs + lows) / 2
            sma5 = self._calculate_ema(median_prices, 5)
            sma34 = self._calculate_ema(median_prices, 34)
            
            if len(sma5) > 0 and len(sma34) > 0:
                min_len = min(len(sma5), len(sma34))
                ao = sma5[-min_len:] - sma34[-min_len:]
                return ao
            
            return np.array([0])
            
        except:
            return np.array([0])
    
    def _calculate_rsi(self, prices, period=14):
        """RSI hesapla"""
        try:
            if len(prices) < period + 1:
                return np.array([])
            
            deltas = np.diff(prices)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            avg_gain = np.mean(gains[:period])
            avg_loss = np.mean(losses[:period])
            
            rs_values = []
            for i in range(period, len(deltas)):
                avg_gain = (avg_gain * (period - 1) + gains[i]) / period
                avg_loss = (avg_loss * (period - 1) + losses[i]) / period
                
                if avg_loss != 0:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
                else:
                    rsi = 100
                
                rs_values.append(rsi)
            
            return np.array(rs_values)
            
        except:
            return np.array([50])
    
    def _calculate_ema(self, prices, period):
        """EMA hesapla"""
        try:
            if len(prices) < period:
                return np.array([])
            
            alpha = 2 / (period + 1)
            ema_values = [prices[0]]
            
            for price in prices[1:]:
                ema_values.append(alpha * price + (1 - alpha) * ema_values[-1])
            
            return np.array(ema_values)
            
        except:
            return np.array([])
    
    def _calculate_adx_di(self, highs, lows, closes, period=14):
        """ADX ve Directional Movement (+DI, -DI) hesapla"""
        try:
            if len(highs) < period + 1:
                return np.array([20]), np.array([25]), np.array([25])
            
            # True Range hesapla
            tr_values = []
            plus_dm_values = []
            minus_dm_values = []
            
            for i in range(1, len(highs)):
                # True Range
                tr = max(
                    highs[i] - lows[i],
                    abs(highs[i] - closes[i-1]),
                    abs(lows[i] - closes[i-1])
                )
                tr_values.append(tr)
                
                # Directional Movement
                plus_dm = max(highs[i] - highs[i-1], 0) if highs[i] - highs[i-1] > lows[i-1] - lows[i] else 0
                minus_dm = max(lows[i-1] - lows[i], 0) if lows[i-1] - lows[i] > highs[i] - highs[i-1] else 0
                
                plus_dm_values.append(plus_dm)
                minus_dm_values.append(minus_dm)
            
            # Smoothed TR ve DM değerleri
            smoothed_tr = []
            smoothed_plus_dm = []
            smoothed_minus_dm = []
            
            # İlk değerler (simple average)
            smoothed_tr.append(np.mean(tr_values[:period]))
            smoothed_plus_dm.append(np.mean(plus_dm_values[:period]))
            smoothed_minus_dm.append(np.mean(minus_dm_values[:period]))
            
            # Wilder smoothing
            for i in range(period, len(tr_values)):
                smoothed_tr.append(smoothed_tr[-1] - (smoothed_tr[-1] / period) + tr_values[i])
                smoothed_plus_dm.append(smoothed_plus_dm[-1] - (smoothed_plus_dm[-1] / period) + plus_dm_values[i])
                smoothed_minus_dm.append(smoothed_minus_dm[-1] - (smoothed_minus_dm[-1] / period) + minus_dm_values[i])
            
            # DI hesapla
            plus_di = []
            minus_di = []
            dx_values = []
            
            for i in range(len(smoothed_tr)):
                if smoothed_tr[i] != 0:
                    plus_di_val = 100 * smoothed_plus_dm[i] / smoothed_tr[i]
                    minus_di_val = 100 * smoothed_minus_dm[i] / smoothed_tr[i]
                else:
                    plus_di_val = 25
                    minus_di_val = 25
                
                plus_di.append(plus_di_val)
                minus_di.append(minus_di_val)
                
                # DX hesapla
                di_sum = plus_di_val + minus_di_val
                if di_sum != 0:
                    dx = 100 * abs(plus_di_val - minus_di_val) / di_sum
                else:
                    dx = 0
                dx_values.append(dx)
            
            # ADX hesapla (DX'in smoothed average'ı)
            adx_values = []
            if len(dx_values) >= period:
                adx_values.append(np.mean(dx_values[:period]))  # İlk ADX değeri
                
                # Wilder smoothing for ADX
                for i in range(period, len(dx_values)):
                    adx_val = (adx_values[-1] * (period - 1) + dx_values[i]) / period
                    adx_values.append(adx_val)
            
            return np.array(adx_values), np.array(plus_di), np.array(minus_di)
            
        except Exception as e:
            print(f"❌ ADX hesaplama hatası: {e}")
            return np.array([20]), np.array([25]), np.array([25])
    
    def _detect_price_action_patterns(self, recent_bars):
        """Price action pattern tespiti"""
        try:
            if len(recent_bars) < 3:
                return {'pattern': 'INSUFFICIENT_DATA', 'strength': 0}
            
            # Son 3 bar'ı analiz et
            bar1, bar2, bar3 = recent_bars[-3], recent_bars[-2], recent_bars[-1]
            
            # Doji pattern
            if abs(bar3['close'] - bar3['open']) / (bar3['high'] - bar3['low']) < 0.1:
                return {'pattern': 'DOJI', 'strength': 40}
            
            # Hammer/Hanging Man
            body_size = abs(bar3['close'] - bar3['open'])
            lower_shadow = min(bar3['open'], bar3['close']) - bar3['low']
            upper_shadow = bar3['high'] - max(bar3['open'], bar3['close'])
            
            if lower_shadow > 2 * body_size and upper_shadow < body_size:
                return {'pattern': 'HAMMER', 'strength': 60}
            
            # Engulfing pattern
            if (bar2['close'] > bar2['open'] and bar3['close'] < bar3['open'] and
                bar3['open'] > bar2['close'] and bar3['close'] < bar2['open']):
                return {'pattern': 'BEARISH_ENGULFING', 'strength': 70}
            
            if (bar2['close'] < bar2['open'] and bar3['close'] > bar3['open'] and
                bar3['open'] < bar2['close'] and bar3['close'] > bar2['open']):
                return {'pattern': 'BULLISH_ENGULFING', 'strength': 70}
            
            return {'pattern': 'NONE', 'strength': 0}
            
        except:
            return {'pattern': 'ERROR', 'strength': 0}
    
    def _generate_scalping_signal(self, indicators):
        """Scalping sinyali üret"""
        try:
            buy_score = 0
            sell_score = 0
            
            # Stochastic signals
            if indicators.get('stoch_k', 50) < 20 and indicators.get('stoch_d', 50) < 20:
                buy_score += 25  # Oversold
            elif indicators.get('stoch_k', 50) > 80 and indicators.get('stoch_d', 50) > 80:
                sell_score += 25  # Overbought
            
            # Williams %R signals  
            if indicators.get('williams_r', -50) < -80:
                buy_score += 20  # Oversold
            elif indicators.get('williams_r', -50) > -20:
                sell_score += 20  # Overbought
            
            # CCI signals
            cci = indicators.get('cci', 0)
            if cci < -100:
                buy_score += 15
            elif cci > 100:
                sell_score += 15
            
            # ADX trend gücü kontrolü
            adx = indicators.get('adx', 20)
            plus_di = indicators.get('plus_di', 25)
            minus_di = indicators.get('minus_di', 25)
            
            # Güçlü trend (ADX > 25) ve yön kontrolü
            if adx > 25:
                if plus_di > minus_di:
                    buy_score += 30  # Güçlü uptrend
                elif minus_di > plus_di:
                    sell_score += 30  # Güçlü downtrend
            
            # Zayıf trend (ADX < 20) - sideways market
            elif adx < 20:
                # Sideways market'te oscillator sinyallerine daha fazla ağırlık
                buy_score = int(buy_score * 0.7)  # Azalt
                sell_score = int(sell_score * 0.7)  # Azalt
            
            # EMA crossover
            ema5 = indicators.get('ema5', 0)
            ema13 = indicators.get('ema13', 0)
            if ema5 > ema13:
                buy_score += 20
            else:
                sell_score += 20
            
            # RSI fast
            rsi_fast = indicators.get('rsi_fast', 50)
            if rsi_fast < 30:
                buy_score += 15
            elif rsi_fast > 70:
                sell_score += 15
            
            # Price action boost
            pattern = indicators.get('price_action', {})
            if pattern.get('pattern') == 'BULLISH_ENGULFING':
                buy_score += pattern.get('strength', 0)
            elif pattern.get('pattern') == 'BEARISH_ENGULFING':
                sell_score += pattern.get('strength', 0)
            
            # Sonuç
            if buy_score > sell_score and buy_score > 60:
                return {
                    'signal': 'BUY',
                    'strength': min(buy_score, 100),
                    'confidence': min(buy_score * 0.8, 100)
                }
            elif sell_score > buy_score and sell_score > 60:
                return {
                    'signal': 'SELL', 
                    'strength': min(sell_score, 100),
                    'confidence': min(sell_score * 0.8, 100)
                }
            else:
                return {
                    'signal': 'NEUTRAL',
                    'strength': max(buy_score, sell_score),
                    'confidence': 0
                }
                
        except Exception as e:
            print(f"❌ Scalping sinyal üretim hatası: {e}")
            return {'signal': 'NEUTRAL', 'strength': 0, 'confidence': 0}
    
    def _check_volatility(self, bars):
        """Volatilite kontrolü - scalping için gerekli"""
        try:
            if len(bars) < 10:
                return False
            
            # Son 10 bar'ın ATR'ini hesapla
            atr_values = []
            for i in range(1, len(bars)):
                tr = max(
                    bars[i]['high'] - bars[i]['low'],
                    abs(bars[i]['high'] - bars[i-1]['close']),
                    abs(bars[i]['low'] - bars[i-1]['close'])
                )
                atr_values.append(tr)
            
            current_atr = np.mean(atr_values[-10:])  # Son 10 period ATR
            
            # Minimum volatilite kontrolü (sembol bazında)
            min_atr = 0.0001  # Varsayılan
            return current_atr > min_atr
            
        except:
            return True  # Hata durumunda izin ver
    
    def _print_scalping_analysis(self, result):
        """Scalping analiz sonucunu yazdır"""
        try:
            print(f"\n⚡ {result['symbol']} SCALPING SONUCU:")
            print("=" * 50)
            print(f"🎯 Sinyal: {result['signal']} (Güç: {result['strength']:.0f})")
            print(f"🔥 Güven: %{result['confidence']:.1f}")
            print(f"📊 Spread: {result['spread_info']['spread_pips']:.1f} pips")
            print(f"✅ Scalping Ready: {'YES' if result['scalping_ready'] else 'NO'}")
            
            indicators = result['indicators']
            print(f"\n📋 SCALPING İNDİKATÖRLER:")
            print(f"   Stochastic K: {indicators.get('stoch_k', 0):.1f}")
            print(f"   Williams %R: {indicators.get('williams_r', 0):.1f}")
            print(f"   CCI: {indicators.get('cci', 0):.1f}")
            print(f"   RSI Fast: {indicators.get('rsi_fast', 0):.1f}")
            print(f"   ADX: {indicators.get('adx', 0):.1f}")
            print(f"   +DI: {indicators.get('plus_di', 0):.1f}")
            print(f"   -DI: {indicators.get('minus_di', 0):.1f}")
            print(f"   EMA5: {indicators.get('ema5', 0):.5f}")
            print(f"   EMA13: {indicators.get('ema13', 0):.5f}")
            
            pattern = indicators.get('price_action', {})
            print(f"   Pattern: {pattern.get('pattern', 'NONE')}")
            
        except Exception as e:
            print(f"❌ Scalping rapor hatası: {e}")
    
    def _check_volatility(self, bars):
        """Volatilite kontrolü"""
        try:
            if len(bars) < 5:
                return True
            
            recent_ranges = []
            for bar in bars[-5:]:
                range_size = bar['high'] - bar['low']
                recent_ranges.append(range_size)
            
            avg_range = np.mean(recent_ranges)
            return avg_range > 0.00001  # Minimum volatilite
            
        except:
            return True


# Test fonksiyonu
def test_scalping_analyzer():
    """Scalping analyzer test"""
    print("🧪 Scalping Analyzer Test Başlıyor...")
    print("=" * 50)
    
    analyzer = ScalpingAnalyzer()
    
    # EURUSD scalping test
    result = analyzer.analyze_scalping_opportunity('EURUSD-T')
    
    if result:
        print(f"\n✅ Scalping test sonucu:")
        print(f"   Sinyal: {result['signal']}")
        print(f"   Güç: {result['strength']:.0f}")
        print(f"   Scalping Ready: {result['scalping_ready']}")
    else:
        print("❌ Scalping analizi başarısız")

if __name__ == "__main__":
    test_scalping_analyzer()