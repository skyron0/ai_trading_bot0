# ai_engine/news_analyzer.py
"""
AI Trading Bot - Haber Analizi Motoru
Ekonomik haberleri analiz edip trading sinyallerini güçlendirir
"""

import requests
import json
from datetime import datetime, timedelta
import re
import sys
import os

# Parent directory'yi ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Sentiment analizi için basit implementation (textblob yerine)
class SimpleSentimentAnalyzer:
    """Basit sentiment analizi"""
    
    def __init__(self):
        # Pozitif kelimeler
        self.positive_words = [
            'rise', 'increase', 'growth', 'strong', 'bullish', 'positive', 
            'gains', 'boost', 'surge', 'rally', 'optimistic', 'better',
            'improve', 'upgrade', 'beat', 'exceeds', 'outperform', 'up'
        ]
        
        # Negatif kelimeler
        self.negative_words = [
            'fall', 'decrease', 'decline', 'weak', 'bearish', 'negative',
            'losses', 'drop', 'crash', 'plunge', 'pessimistic', 'worse',
            'deteriorate', 'downgrade', 'miss', 'below', 'underperform', 'down'
        ]
        
        # Forex/ekonomi anahtar kelimeleri
        self.forex_keywords = {
            'USD': ['dollar', 'usd', 'fed', 'federal reserve', 'powell', 'fomc'],
            'EUR': ['euro', 'eur', 'ecb', 'european central bank', 'lagarde'],
            'GBP': ['pound', 'gbp', 'bank of england', 'boe'],
            'JPY': ['yen', 'jpy', 'bank of japan', 'boj'],
            'GOLD': ['gold', 'xau', 'precious metals'],
            'OIL': ['oil', 'crude', 'wti', 'brent']
        }
    
    def analyze_sentiment(self, text):
        """Basit sentiment analizi"""
        if not text:
            return 0.0
        
        text_lower = text.lower()
        positive_count = sum(1 for word in self.positive_words if word in text_lower)
        negative_count = sum(1 for word in self.negative_words if word in text_lower)
        
        total_words = len(text.split())
        if total_words == 0:
            return 0.0
        
        # -1 ile +1 arası score
        score = (positive_count - negative_count) / max(total_words * 0.1, 1)
        return max(-1.0, min(1.0, score))
    
    def get_affected_currencies(self, text):
        """Hangi para birimlerinin etkilendiğini bul"""
        affected = []
        text_lower = text.lower()
        
        for currency, keywords in self.forex_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    affected.append(currency)
                    break
        
        return list(set(affected))  # Duplicate'ları kaldır

class NewsAnalyzer:
    """Haber analizi sınıfı"""
    
    def __init__(self):
        """NewsAnalyzer'ı başlat"""
        self.sentiment_analyzer = SimpleSentimentAnalyzer()
        self.news_cache = []
        self.last_update = None
        
        # Haber kaynakları (ücretsiz API'ler)
        self.news_sources = {
            'finviz': 'https://finviz.com/news.ashx',
            'marketwatch': 'https://www.marketwatch.com/latest-news',
            'investing': 'https://www.investing.com/news/forex-news'
        }
        
        print("📰 NewsAnalyzer başlatıldı")
    
    def get_economic_news(self, hours_back=6):
        """Son X saat içindeki ekonomik haberleri al"""
        try:
            print(f"📰 Son {hours_back} saatin haberleri alınıyor...")
            
            # Basit news scraping (demo amaçlı)
            news_items = self._fetch_sample_news()
            
            # Haberleri filtrele ve analiz et
            analyzed_news = []
            for news in news_items:
                analysis = self.analyze_news_item(news)
                if analysis:
                    analyzed_news.append(analysis)
            
            self.news_cache = analyzed_news
            self.last_update = datetime.now()
            
            print(f"✅ {len(analyzed_news)} haber analiz edildi")
            return analyzed_news
            
        except Exception as e:
            print(f"❌ Haber alma hatası: {e}")
            return []
    
    def _fetch_sample_news(self):
        """Demo amaçlı örnek haberler (gerçek API entegrasyonu için)"""
        # Gerçek uygulamada burada RSS feed'ler veya news API'ları kullanılır
        sample_news = [
            {
                'title': 'Fed Signals More Rate Hikes as Inflation Persists',
                'content': 'Federal Reserve officials indicated they may need to raise interest rates further to combat persistent inflation. The dollar strengthened on the news.',
                'source': 'Reuters',
                'timestamp': datetime.now() - timedelta(hours=2),
                'url': 'https://example.com/news1'
            },
            {
                'title': 'ECB Holds Rates Steady, Euro Weakens',
                'content': 'European Central Bank kept rates unchanged despite pressure for more aggressive action. The euro fell against major currencies following the announcement.',
                'source': 'Bloomberg',
                'timestamp': datetime.now() - timedelta(hours=4),
                'url': 'https://example.com/news2'
            },
            {
                'title': 'Gold Rallies on Safe Haven Demand',
                'content': 'Gold prices surged to multi-week highs as investors sought safe haven assets amid geopolitical tensions and market uncertainty.',
                'source': 'MarketWatch',
                'timestamp': datetime.now() - timedelta(hours=1),
                'url': 'https://example.com/news3'
            },
            {
                'title': 'US Jobs Data Beats Expectations',
                'content': 'Non-farm payrolls increased by more than expected, showing continued strength in the labor market. The dollar gained ground following the release.',
                'source': 'CNBC',
                'timestamp': datetime.now() - timedelta(minutes=30),
                'url': 'https://example.com/news4'
            }
        ]
        
        return sample_news
    
    def analyze_news_item(self, news_item):
        """Bir haber maddesini analiz et"""
        try:
            title = news_item.get('title', '')
            content = news_item.get('content', '')
            full_text = f"{title} {content}"
            
            # Sentiment analizi
            sentiment_score = self.sentiment_analyzer.analyze_sentiment(full_text)
            
            # Etkilenen para birimleri
            affected_currencies = self.sentiment_analyzer.get_affected_currencies(full_text)
            
            # Önem seviyesi belirleme
            importance = self._calculate_importance(title, content)
            
            # Market etkisi tahmini
            market_impact = self._predict_market_impact(sentiment_score, affected_currencies, importance)
            
            analysis = {
                'title': title,
                'content': content[:200] + '...' if len(content) > 200 else content,
                'source': news_item.get('source', 'Unknown'),
                'timestamp': news_item.get('timestamp', datetime.now()),
                'sentiment_score': sentiment_score,
                'sentiment_label': self._get_sentiment_label(sentiment_score),
                'affected_currencies': affected_currencies,
                'importance': importance,
                'market_impact': market_impact,
                'url': news_item.get('url', '')
            }
            
            return analysis
            
        except Exception as e:
            print(f"❌ Haber analizi hatası: {e}")
            return None
    
    def _calculate_importance(self, title, content):
        """Haberin önem seviyesini hesapla"""
        high_importance_keywords = [
            'fed', 'federal reserve', 'interest rate', 'inflation', 'gdp',
            'employment', 'jobs', 'nfp', 'cpi', 'ppi', 'fomc', 'powell',
            'ecb', 'lagarde', 'recession', 'crisis', 'war', 'trade'
        ]
        
        medium_importance_keywords = [
            'retail sales', 'manufacturing', 'housing', 'consumer confidence',
            'industrial production', 'trade balance', 'current account'
        ]
        
        text_lower = f"{title} {content}".lower()
        
        high_count = sum(1 for keyword in high_importance_keywords if keyword in text_lower)
        medium_count = sum(1 for keyword in medium_importance_keywords if keyword in text_lower)
        
        if high_count >= 2:
            return 'HIGH'
        elif high_count >= 1 or medium_count >= 2:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _predict_market_impact(self, sentiment_score, affected_currencies, importance):
        """Market etkisini tahmin et"""
        impact_predictions = {}
        
        # Önem seviyesine göre çarpan
        multiplier = {'HIGH': 1.0, 'MEDIUM': 0.6, 'LOW': 0.3}.get(importance, 0.3)
        
        for currency in affected_currencies:
            # Sentiment score'u market etkisine çevir
            base_impact = sentiment_score * multiplier
            
            # Para birimine özel ayarlamalar
            if currency == 'USD':
                # USD haberleri genelde daha etkili
                adjusted_impact = base_impact * 1.2
            elif currency == 'EUR':
                adjusted_impact = base_impact * 1.0
            elif currency == 'GOLD':
                # Altın genelde ters korelasyon
                adjusted_impact = base_impact * 1.1
            else:
                adjusted_impact = base_impact
            
            # -1 ile +1 arası sınırla
            impact_predictions[currency] = max(-1.0, min(1.0, adjusted_impact))
        
        return impact_predictions
    
    def _get_sentiment_label(self, score):
        """Sentiment score'unu label'a çevir"""
        if score > 0.3:
            return 'POSITIVE'
        elif score < -0.3:
            return 'NEGATIVE'
        else:
            return 'NEUTRAL'
    
    def get_currency_sentiment(self, currency, hours_back=6):
        """Belirli bir para birimi için sentiment analizi"""
        try:
            # Eğer cache eski ise haberleri yenile
            if (not self.last_update or 
                (datetime.now() - self.last_update).total_seconds() > 3600):  # 1 saat
                self.get_economic_news(hours_back)
            
            currency_news = []
            total_impact = 0.0
            total_importance_weight = 0.0
            
            for news in self.news_cache:
                if currency in news['affected_currencies']:
                    currency_news.append(news)
                    
                    # Önem ağırlığı
                    weight = {'HIGH': 1.0, 'MEDIUM': 0.6, 'LOW': 0.3}.get(news['importance'], 0.3)
                    impact = news['market_impact'].get(currency, 0.0)
                    
                    total_impact += impact * weight
                    total_importance_weight += weight
            
            # Ortalama etki
            if total_importance_weight > 0:
                avg_impact = total_impact / total_importance_weight
            else:
                avg_impact = 0.0
            
            sentiment_result = {
                'currency': currency,
                'sentiment_score': avg_impact,
                'sentiment_label': self._get_sentiment_label(avg_impact),
                'news_count': len(currency_news),
                'relevant_news': currency_news[:3],  # En son 3 haber
                'confidence': min(len(currency_news) * 0.2, 1.0)  # Haber sayısına göre güven
            }
            
            return sentiment_result
            
        except Exception as e:
            print(f"❌ Para birimi sentiment analizi hatası: {e}")
            return {
                'currency': currency,
                'sentiment_score': 0.0,
                'sentiment_label': 'NEUTRAL',
                'news_count': 0,
                'relevant_news': [],
                'confidence': 0.0
            }
    
    def get_trading_signal_from_news(self, symbol):
        """Haberlere dayalı trading sinyali üret"""
        try:
            print(f"📰 {symbol} için haber bazlı sinyal analizi...")
            
            # Sembol çiftini parse et
            if symbol == 'EURUSD-T':
                base_currency = 'EUR'
                quote_currency = 'USD'
            elif symbol == 'GOLD-T':
                base_currency = 'GOLD'
                quote_currency = 'USD'
            elif symbol == 'BTCUSD-T':
                base_currency = 'BTC'
                quote_currency = 'USD'
            else:
                return {'signal': 'NEUTRAL', 'strength': 0, 'reason': 'Unknown symbol'}
            
            # Her para birimi için sentiment al
            base_sentiment = self.get_currency_sentiment(base_currency)
            quote_sentiment = self.get_currency_sentiment(quote_currency)
            
            # Sinyal hesaplama
            base_score = base_sentiment['sentiment_score'] * base_sentiment['confidence']
            quote_score = quote_sentiment['sentiment_score'] * quote_sentiment['confidence']
            
            # Net sinyal (base güçlü = BUY, quote güçlü = SELL)
            net_signal = base_score - quote_score
            
            # Sinyal gücü
            signal_strength = abs(net_signal) * 100
            
            # Sinyal yönü
            if net_signal > 0.2:
                signal_direction = 'BUY'
                reason = f'{base_currency} positive news vs {quote_currency}'
            elif net_signal < -0.2:
                signal_direction = 'SELL'
                reason = f'{quote_currency} positive news vs {base_currency}'
            else:
                signal_direction = 'NEUTRAL'
                reason = 'No significant news impact'
            
            news_signal = {
                'signal': signal_direction,
                'strength': min(signal_strength, 100),
                'reason': reason,
                'base_sentiment': base_sentiment,
                'quote_sentiment': quote_sentiment,
                'net_score': net_signal,
                'confidence': (base_sentiment['confidence'] + quote_sentiment['confidence']) / 2
            }
            
            print(f"📰 {symbol} haber sinyali: {signal_direction} (Güç: {signal_strength:.0f})")
            
            return news_signal
            
        except Exception as e:
            print(f"❌ Haber sinyali hatası: {e}")
            return {'signal': 'NEUTRAL', 'strength': 0, 'reason': 'Analysis error'}
    
    def print_news_summary(self, hours_back=6):
        """Haber özetini yazdır"""
        try:
            print(f"\n📰 SON {hours_back} SAATİN HABER ÖZETİ")
            print("=" * 50)
            
            news_list = self.get_economic_news(hours_back)
            
            if not news_list:
                print("📭 Yeni haber bulunamadı")
                return
            
            for i, news in enumerate(news_list[:5], 1):  # En önemli 5 haber
                print(f"\n{i}. {news['title']}")
                print(f"   Kaynak: {news['source']}")
                print(f"   Sentiment: {news['sentiment_label']} ({news['sentiment_score']:.2f})")
                print(f"   Önem: {news['importance']}")
                print(f"   Etkilenen: {', '.join(news['affected_currencies'])}")
                print(f"   Zaman: {news['timestamp'].strftime('%H:%M')}")
                
                if news['market_impact']:
                    print(f"   Market Etkisi:")
                    for currency, impact in news['market_impact'].items():
                        impact_emoji = "📈" if impact > 0 else "📉" if impact < 0 else "➡️"
                        print(f"     {currency}: {impact_emoji} {impact:.2f}")
            
        except Exception as e:
            print(f"❌ Haber özeti hatası: {e}")


# Test fonksiyonu
def test_news_analyzer():
    """NewsAnalyzer'ı test et"""
    print("🧪 NewsAnalyzer Test Başlıyor...")
    print("=" * 50)
    
    analyzer = NewsAnalyzer()
    
    # Genel haber özeti
    analyzer.print_news_summary(6)
    
    # EURUSD için haber sinyali
    print(f"\n🧪 EURUSD-T Haber Sinyali Testi:")
    signal = analyzer.get_trading_signal_from_news('EURUSD-T')
    print(f"   Sinyal: {signal['signal']}")
    print(f"   Güç: {signal['strength']:.0f}")
    print(f"   Neden: {signal['reason']}")
    print(f"   Güven: %{signal['confidence']*100:.0f}")
    
    # GOLD için haber sinyali
    print(f"\n🧪 GOLD-T Haber Sinyali Testi:")
    gold_signal = analyzer.get_trading_signal_from_news('GOLD-T')
    print(f"   Sinyal: {gold_signal['signal']}")
    print(f"   Güç: {gold_signal['strength']:.0f}")
    print(f"   Neden: {gold_signal['reason']}")

if __name__ == "__main__":
    test_news_analyzer()