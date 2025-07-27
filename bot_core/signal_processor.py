# bot_core/signal_processor.py
"""
AI Trading Bot - Signal Processing Module
Triple AI sinyal işleme ve birleştirme
"""

import random
from datetime import datetime
import sys
import os

# Parent directory'yi ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_engine.simple_technical_analyzer import SimpleTechnicalAnalyzer
from ai_engine.news_analyzer import NewsAnalyzer
from ai_engine.multi_timeframe_analyzer import MultiTimeframeAnalyzer
from ai_engine.scalping_analyzer import ScalpingAnalyzer  # SCALPING EKLENDİ
from trading_engine.risk_manager import RiskManager
from config.settings import SIGNAL_STRENGTH_MIN

class SignalProcessor:
    """Triple AI sinyal işleme sınıfı"""
    
    def __init__(self):
        """SignalProcessor'ı başlat"""
        self.technical_analyzer = SimpleTechnicalAnalyzer()
        self.news_analyzer = NewsAnalyzer()
        self.multi_tf_analyzer = MultiTimeframeAnalyzer()
        self.scalping_analyzer = ScalpingAnalyzer()  # SCALPING EKLENDİ
        self.risk_manager = RiskManager()
        
        print("🎯 SignalProcessor başlatıldı - Quadruple AI Ready (Teknik+Haber+MultiTF+Scalping)")
    
    def analyze_symbol_triple_ai(self, symbol):
        """Bir sembol için Triple AI analizi yap"""
        try:
            print(f"\n🔍 {symbol} TRIPLE AI ANALİZİ başlıyor...")
            
            # 1. TEKNİK ANALİZ (M5)
            analysis_result = self.technical_analyzer.analyze_symbol(
                symbol=symbol,
                timeframe='M5',
                bars=100
            )
            
            if not analysis_result:
                print(f"❌ {symbol} teknik analizi başarısız")
                return None
            
            # 2. HABER ANALİZİ
            news_signal = self.news_analyzer.get_trading_signal_from_news(symbol)
            
            # 3. MULTIPLE TIMEFRAME ANALİZİ
            multi_tf_result = self.multi_tf_analyzer.analyze_multiple_timeframes(symbol)
            
            # 4. SCALPING ANALİZİ
            scalping_result = self.scalping_analyzer.analyze_scalping_opportunity(symbol)
            
            # TÜM SİNYALLERİ BİRLEŞTİR (QUADRUPLE AI)
            combined_analysis = self._combine_all_signals(analysis_result, news_signal, multi_tf_result, scalping_result)
            
            # Sonuç paketi
            triple_ai_result = {
                'symbol': symbol,
                'technical_analysis': analysis_result,
                'news_signal': news_signal,
                'multi_tf_result': multi_tf_result,
                'scalping_result': scalping_result,  # SCALPING EKLENDİ
                'combined_analysis': combined_analysis,
                'timestamp': datetime.now()
            }
            
            self._print_triple_analysis_summary(triple_ai_result)
            
            return triple_ai_result
            
        except Exception as e:
            print(f"❌ {symbol} triple AI analiz hatası: {e}")
            return None
    
    def _combine_all_signals(self, technical_analysis, news_signal, multi_tf_result):
        """Triple AI: Teknik + Haber + Multiple Timeframe birleştirme"""
        try:
            # Ağırlıklar
            technical_weight = 0.4   # %40 teknik analiz (M5)
            news_weight = 0.2        # %20 haber analizi  
            multi_tf_weight = 0.4    # %40 multiple timeframe
            
            # Teknik analiz skorları (M5)
            tech_buy_strength = technical_analysis['buy_strength']
            tech_sell_strength = technical_analysis['sell_strength']
            tech_confidence = technical_analysis['confidence']
            
            # Haber analizi skorları
            news_strength = news_signal['strength']
            news_confidence = news_signal['confidence'] * 100
            
            # Multiple timeframe skorları
            mtf_buy_strength = multi_tf_result['buy_strength']
            mtf_sell_strength = multi_tf_result['sell_strength']
            mtf_confidence = multi_tf_result['confidence']
            mtf_alignment = multi_tf_result['alignment_score']
            
            # Haber sinyalini sayısal değere çevir
            if news_signal['signal'] == 'BUY':
                news_buy_boost = news_strength
                news_sell_boost = 0
            elif news_signal['signal'] == 'SELL':
                news_buy_boost = 0
                news_sell_boost = news_strength
            else:
                news_buy_boost = 0
                news_sell_boost = 0
            
            # Birleşik güç hesapla
            combined_buy_strength = (
                (tech_buy_strength * technical_weight) + 
                (news_buy_boost * news_weight) + 
                (mtf_buy_strength * multi_tf_weight)
            )
            
            combined_sell_strength = (
                (tech_sell_strength * technical_weight) + 
                (news_sell_boost * news_weight) + 
                (mtf_sell_strength * multi_tf_weight)
            )
            
            # Birleşik güven hesapla (timeframe uyumu bonus)
            base_confidence = (
                (tech_confidence * technical_weight) + 
                (news_confidence * news_weight) + 
                (mtf_confidence * multi_tf_weight)
            )
            
            # Timeframe uyumu bonusu
            alignment_bonus = (mtf_alignment / 100) * 20
            combined_confidence = base_confidence + alignment_bonus
            
            # Dominant sinyali belirle
            if combined_buy_strength > combined_sell_strength and combined_buy_strength > 35:
                overall_signal = 'BUY'
                signal_strength = combined_buy_strength
            elif combined_sell_strength > combined_buy_strength and combined_sell_strength > 35:
                overall_signal = 'SELL'
                signal_strength = combined_sell_strength
            else:
                overall_signal = 'NEUTRAL'
                signal_strength = max(combined_buy_strength, combined_sell_strength)
            
            return {
                'overall_signal': overall_signal,
                'confidence': min(combined_confidence, 100),
                'buy_strength': combined_buy_strength,
                'sell_strength': combined_sell_strength,
                'signal_strength': signal_strength,
                'technical_weight': technical_weight,
                'news_weight': news_weight,
                'multi_tf_weight': multi_tf_weight,
                'alignment_bonus': alignment_bonus,
                'components': {
                    'technical': {'buy': tech_buy_strength, 'sell': tech_sell_strength},
                    'news': {'buy': news_buy_boost, 'sell': news_sell_boost},
                    'multi_tf': {'buy': mtf_buy_strength, 'sell': mtf_sell_strength}
                }
            }
            
        except Exception as e:
            print(f"❌ Triple sinyal birleştirme hatası: {e}")
            return {
                'overall_signal': technical_analysis['overall_signal'],
                'confidence': technical_analysis['confidence'],
                'buy_strength': technical_analysis['buy_strength'],
                'sell_strength': technical_analysis['sell_strength']
            }
    
    def _print_triple_analysis_summary(self, result):
        """Triple AI analiz özetini yazdır"""
        try:
            symbol = result['symbol']
            technical = result['technical_analysis']
            news = result['news_signal']
            multi_tf = result['multi_tf_result']
            combined = result['combined_analysis']
            
            print(f"📊 {symbol} Teknik: {technical['overall_signal']} (Güven: %{technical['confidence']:.1f})")
            print(f"📰 {symbol} Haber: {news['signal']} (Güç: {news['strength']:.0f})")
            print(f"🕐 {symbol} Multi-TF: {multi_tf['overall_signal']} (Uyum: %{multi_tf['alignment_score']:.0f})")
            print(f"🎯 {symbol} FINAL: {combined['overall_signal']} (Güven: %{combined['confidence']:.1f})")
            
        except Exception as e:
            print(f"❌ Özet yazdırma hatası: {e}")
    
    def validate_signal_strength(self, combined_analysis):
        """Sinyal gücünü doğrula"""
        try:
            signal_strength = combined_analysis['signal_strength']
            
            if signal_strength < SIGNAL_STRENGTH_MIN:
                return False, f"Sinyal gücü yetersiz: {signal_strength:.0f} < {SIGNAL_STRENGTH_MIN}"
            
            return True, f"Sinyal gücü yeterli: {signal_strength:.0f}"
            
        except Exception as e:
            return False, f"Sinyal doğrulama hatası: {e}"
    
    def create_trade_signal(self, triple_ai_result, risk_result):
        """Trade sinyali oluştur"""
        try:
            symbol = triple_ai_result['symbol']
            combined = triple_ai_result['combined_analysis']
            technical = triple_ai_result['technical_analysis']
            
            trade_signal = {
                'symbol': symbol,
                'signal': combined['overall_signal'],
                'entry_price': technical['current_price'],
                'confidence': combined['confidence'],
                'timestamp': datetime.now(),
                'analysis': technical,
                'news_signal': triple_ai_result['news_signal'],
                'multi_tf_result': triple_ai_result['multi_tf_result'],
                'combined_analysis': combined,
                'risk_details': risk_result['risk_details'],
                'lot_size': risk_result['risk_details']['lot_size'],
                'stop_loss': risk_result['risk_details']['stop_loss'],
                'take_profit': risk_result['risk_details']['take_profit']
            }
            
            return trade_signal
            
        except Exception as e:
            print(f"❌ Trade sinyali oluşturma hatası: {e}")
            return None
    
    def print_detailed_signal_analysis(self, signal):
        """Detaylı sinyal analizi yazdır"""
        try:
            analysis = signal['analysis']
            news = signal['news_signal']
            multi_tf = signal['multi_tf_result']
            combined = signal['combined_analysis']
            
            print(f"\n📋 {signal['symbol']} TRIPLE AI SINYAL DETAYLARI:")
            print("=" * 60)
            
            print("📊 TEKNİK ANALİZ (M5):")
            print(f"   RSI: {analysis['indicators']['rsi']:.1f}")
            print(f"   MACD: {analysis['indicators']['macd']:.5f}")
            print(f"   Sinyal: {analysis['overall_signal']} (Güven: %{analysis['confidence']:.0f})")
            
            print("📰 HABER ANALİZİ:")
            print(f"   Sinyal: {news['signal']} (Güç: {news['strength']:.0f})")
            print(f"   Güven: %{news['confidence']*100:.0f}")
            
            print("🕐 MULTIPLE TIMEFRAME:")
            print(f"   Sinyal: {multi_tf['overall_signal']}")
            print(f"   Uyum: %{multi_tf['alignment_score']:.0f}")
            print(f"   Analiz edilen TF: {multi_tf['analyzed_timeframes']}/4")
            
            print("🎯 BİRLEŞİK SONUÇ:")
            print(f"   Final Sinyal: {combined['overall_signal']}")
            print(f"   Final Güven: %{combined['confidence']:.1f}")
            print(f"   Buy Gücü: {combined['buy_strength']:.0f}")
            print(f"   Sell Gücü: {combined['sell_strength']:.0f}")
            print(f"   Uyum Bonusu: +%{combined['alignment_bonus']:.0f}")
            
        except Exception as e:
            print(f"❌ Detaylı analiz yazdırma hatası: {e}")


# Test fonksiyonu
def test_signal_processor():
    """SignalProcessor'ı test et"""
    print("🧪 SignalProcessor Test Başlıyor...")
    print("=" * 50)
    
    processor = SignalProcessor()
    
    # EURUSD test
    result = processor.analyze_symbol_triple_ai('EURUSD-T')
    
    if result:
        combined = result['combined_analysis']
        print(f"\n✅ Test sonucu:")
        print(f"   Sinyal: {combined['overall_signal']}")
        print(f"   Güven: %{combined['confidence']:.1f}")
        print(f"   Güç: {combined['signal_strength']:.0f}")
        
        # Sinyal gücü testi
        is_strong, message = processor.validate_signal_strength(combined)
        print(f"   Güç testi: {message}")

if __name__ == "__main__":
    test_signal_processor()