# ai_engine/multi_timeframe_analyzer.py
"""
AI Trading Bot - Multiple Timeframe Analyzer
Farklı zaman dilimlerinde analiz yapıp uyumlu sinyaller arar
"""

import sys
import os
from datetime import datetime

# Parent directory'yi ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_engine.simple_technical_analyzer import SimpleTechnicalAnalyzer

class MultiTimeframeAnalyzer:
    """Çoklu zaman dilimi analiz sınıfı"""
    
    def __init__(self):
        """MultiTimeframeAnalyzer'ı başlat"""
        self.technical_analyzer = SimpleTechnicalAnalyzer()
        
        # Analiz edilecek timeframe'ler (hızlıdan yavaşa)
        self.timeframes = {
            'M1': {'weight': 0.15, 'bars': 50, 'name': 'Scalping'},
            'M5': {'weight': 0.30, 'bars': 100, 'name': 'Short-term'},
            'M15': {'weight': 0.35, 'bars': 50, 'name': 'Medium-term'},
            'H1': {'weight': 0.20, 'bars': 30, 'name': 'Long-term'}
        }
        
        print("📊 MultiTimeframeAnalyzer başlatıldı")
        print(f"🕐 Timeframe'ler: {list(self.timeframes.keys())}")
    
    def analyze_multiple_timeframes(self, symbol):
        """Tüm timeframe'lerde analiz yap"""
        try:
            print(f"\n🕐 {symbol} - MULTIPLE TIMEFRAME ANALİZİ")
            print("=" * 60)
            
            timeframe_results = {}
            total_weight = 0
            weighted_buy_strength = 0
            weighted_sell_strength = 0
            weighted_confidence = 0
            
            # Her timeframe için analiz
            for tf, config in self.timeframes.items():
                try:
                    print(f"\n🔍 {tf} ({config['name']}) analizi...")
                    
                    # Teknik analiz yap
                    analysis = self.technical_analyzer.analyze_symbol(
                        symbol=symbol,
                        timeframe=tf,
                        bars=config['bars']
                    )
                    
                    if analysis:
                        # Sonuçları kaydet
                        timeframe_results[tf] = {
                            'analysis': analysis,
                            'weight': config['weight'],
                            'name': config['name']
                        }
                        
                        # Ağırlıklı ortalamalara ekle
                        weight = config['weight']
                        weighted_buy_strength += analysis['buy_strength'] * weight
                        weighted_sell_strength += analysis['sell_strength'] * weight
                        weighted_confidence += analysis['confidence'] * weight
                        total_weight += weight
                        
                        # Özet yazdır
                        print(f"   📊 Sinyal: {analysis['overall_signal']} (Güven: %{analysis['confidence']:.0f})")
                        print(f"   💪 Buy: {analysis['buy_strength']:.0f} | Sell: {analysis['sell_strength']:.0f}")
                        
                    else:
                        print(f"   ❌ {tf} analizi başarısız")
                        
                except Exception as e:
                    print(f"   ❌ {tf} analizi hatası: {e}")
                    continue
            
            # Ağırlıklı sonuçları hesapla
            if total_weight > 0:
                final_buy_strength = weighted_buy_strength / total_weight
                final_sell_strength = weighted_sell_strength / total_weight
                final_confidence = weighted_confidence / total_weight
            else:
                final_buy_strength = 0
                final_sell_strength = 0
                final_confidence = 0
            
            # Dominant sinyal belirle
            if final_buy_strength > final_sell_strength and final_buy_strength > 60:
                overall_signal = 'BUY'
                signal_strength = final_buy_strength
            elif final_sell_strength > final_buy_strength and final_sell_strength > 60:
                overall_signal = 'SELL'
                signal_strength = final_sell_strength
            else:
                overall_signal = 'NEUTRAL'
                signal_strength = max(final_buy_strength, final_sell_strength)
            
            # Timeframe uyumu analizi
            alignment_score = self._calculate_timeframe_alignment(timeframe_results)
            
            # Son sonuç
            multi_tf_result = {
                'symbol': symbol,
                'overall_signal': overall_signal,
                'confidence': final_confidence,
                'buy_strength': final_buy_strength,
                'sell_strength': final_sell_strength,
                'signal_strength': signal_strength,
                'alignment_score': alignment_score,
                'timeframe_results': timeframe_results,
                'analyzed_timeframes': len(timeframe_results),
                'timestamp': datetime.now()
            }
            
            # Özet raporu yazdır
            self._print_multi_tf_summary(multi_tf_result)
            
            return multi_tf_result
            
        except Exception as e:
            print(f"❌ Multiple timeframe analizi hatası: {e}")
            return None
    
    def _calculate_timeframe_alignment(self, timeframe_results):
        """Timeframe'ler arası uyumu hesapla"""
        try:
            if len(timeframe_results) < 2:
                return 0.0
            
            signals = []
            for tf_data in timeframe_results.values():
                signal = tf_data['analysis']['overall_signal']
                signals.append(signal)
            
            # Aynı sinyallerin oranı
            buy_count = signals.count('BUY')
            sell_count = signals.count('SELL')
            neutral_count = signals.count('NEUTRAL')
            total_count = len(signals)
            
            # En dominant sinyalin oranı
            max_same_signal = max(buy_count, sell_count, neutral_count)
            alignment_ratio = max_same_signal / total_count
            
            # Uyum skoru (%0-100)
            alignment_score = alignment_ratio * 100
            
            return alignment_score
            
        except Exception as e:
            print(f"❌ Alignment hesaplama hatası: {e}")
            return 0.0
    
    def _print_multi_tf_summary(self, result):
        """Multiple timeframe özet raporu"""
        try:
            print(f"\n📊 {result['symbol']} MULTIPLE TIMEFRAME ÖZETİ")
            print("=" * 60)
            print(f"🎯 Genel Sinyal: {result['overall_signal']}")
            print(f"🔥 Güven: %{result['confidence']:.1f}")
            print(f"📈 Buy Gücü: {result['buy_strength']:.0f}")
            print(f"📉 Sell Gücü: {result['sell_strength']:.0f}")
            print(f"🎯 Sinyal Gücü: {result['signal_strength']:.0f}")
            print(f"🔗 Timeframe Uyumu: %{result['alignment_score']:.0f}")
            print(f"📊 Analiz Edilen TF: {result['analyzed_timeframes']}/4")
            
            # Timeframe detayları
            print(f"\n📋 TIMEFRAME DETAYLARI:")
            for tf, tf_data in result['timeframe_results'].items():
                analysis = tf_data['analysis']
                weight = tf_data['weight']
                name = tf_data['name']
                
                signal_emoji = "🟢" if analysis['overall_signal'] == 'BUY' else "🔴" if analysis['overall_signal'] == 'SELL' else "⚪"
                
                print(f"   {signal_emoji} {tf} ({name}): {analysis['overall_signal']} "
                      f"- Güven: %{analysis['confidence']:.0f} "
                      f"- Ağırlık: %{weight*100:.0f}")
            
            # Uyum analizi
            if result['alignment_score'] >= 75:
                print(f"\n✅ YÜKSEK UYUM! Timeframe'ler %{result['alignment_score']:.0f} uyumlu")
            elif result['alignment_score'] >= 50:
                print(f"\n⚠️ ORTA UYUM. Timeframe'ler %{result['alignment_score']:.0f} uyumlu")
            else:
                print(f"\n❌ DÜŞÜK UYUM. Timeframe'ler %{result['alignment_score']:.0f} uyumlu")
            
        except Exception as e:
            print(f"❌ Özet rapor hatası: {e}")
    
    def get_timeframe_consensus(self, symbol, min_alignment=60):
        """Timeframe konsensüsü al (minimum uyum ile)"""
        try:
            result = self.analyze_multiple_timeframes(symbol)
            
            if not result:
                return None
            
            # Minimum uyum kontrolü
            if result['alignment_score'] < min_alignment:
                print(f"⚠️ Timeframe uyumu yetersiz: %{result['alignment_score']:.0f} < %{min_alignment}")
                return None
            
            # Güçlü konsensüs sinyali
            consensus_signal = {
                'symbol': symbol,
                'signal': result['overall_signal'],
                'confidence': result['confidence'],
                'strength': result['signal_strength'],
                'alignment': result['alignment_score'],
                'timeframes_analyzed': result['analyzed_timeframes'],
                'consensus_quality': 'HIGH' if result['alignment_score'] >= 75 else 'MEDIUM',
                'timestamp': result['timestamp']
            }
            
            return consensus_signal
            
        except Exception as e:
            print(f"❌ Timeframe konsensüs hatası: {e}")
            return None
    
    def compare_timeframes(self, symbol):
        """Timeframe'leri karşılaştır"""
        try:
            print(f"\n🔍 {symbol} TIMEFRAME KARŞILAŞTIRMASI")
            print("=" * 50)
            
            results = {}
            
            # Her timeframe'i ayrı analiz et
            for tf, config in self.timeframes.items():
                analysis = self.technical_analyzer.analyze_symbol(symbol, tf, config['bars'])
                if analysis:
                    results[tf] = analysis
            
            # Karşılaştırma tablosu
            print(f"{'TF':<4} {'Signal':<8} {'Conf%':<6} {'Buy':<4} {'Sell':<4} {'RSI':<6} {'MACD'}")
            print("-" * 50)
            
            for tf, analysis in results.items():
                print(f"{tf:<4} {analysis['overall_signal']:<8} "
                      f"{analysis['confidence']:<6.0f} "
                      f"{analysis['buy_strength']:<4.0f} "
                      f"{analysis['sell_strength']:<4.0f} "
                      f"{analysis['indicators']['rsi']:<6.1f} "
                      f"{analysis['indicators']['macd']:.5f}")
            
            return results
            
        except Exception as e:
            print(f"❌ Timeframe karşılaştırma hatası: {e}")
            return {}


# Test fonksiyonu
def test_multi_timeframe():
    """Multiple timeframe analizi test et"""
    print("🧪 MultiTimeframe Analyzer Test Başlıyor...")
    print("=" * 60)
    
    analyzer = MultiTimeframeAnalyzer()
    
    # EURUSD test
    print("\n🧪 EURUSD-T Multiple Timeframe Test:")
    result = analyzer.analyze_multiple_timeframes('EURUSD-T')
    
    if result:
        print(f"\n🎯 Sonuç: {result['overall_signal']} - Güven: %{result['confidence']:.1f}")
        print(f"🔗 Uyum: %{result['alignment_score']:.0f}")
    
    # Konsensüs test
    print(f"\n🧪 Timeframe Konsensüs Test:")
    consensus = analyzer.get_timeframe_consensus('EURUSD-T', min_alignment=50)
    
    if consensus:
        print(f"✅ Konsensüs bulundu!")
        print(f"   Sinyal: {consensus['signal']}")
        print(f"   Kalite: {consensus['consensus_quality']}")
        print(f"   Uyum: %{consensus['alignment']:.0f}")
    else:
        print("❌ Konsensüs bulunamadı")
    
    # Karşılaştırma test
    print(f"\n🧪 Timeframe Karşılaştırma:")
    analyzer.compare_timeframes('EURUSD-T')

if __name__ == "__main__":
    test_multi_timeframe()