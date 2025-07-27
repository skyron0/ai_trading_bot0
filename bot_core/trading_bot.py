# bot_core/trading_bot.py
"""
AI Trading Bot - Ana Bot Sınıfı (Modüler)
"""

import time
import threading
from datetime import datetime
import sys
import os
import random

# Parent directory'yi ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import (
    TRADING_SYMBOLS, DATA_UPDATE_INTERVAL_SECONDS
)
from data_manager.mt5_connector import MT5Connector
from trading_engine.order_executor import OrderExecutor
from telegram_bot.bot_handler import TelegramBotHandler
from .signal_processor import SignalProcessor

# Flask import (eğer kurulu değilse hatayı yakala)
try:
    from flask import Flask, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

class AITradingBot:
    """Modüler AI Trading Bot sınıfı"""
    
    def __init__(self, simulation_mode=True):
        """Bot'u başlat"""
        self.running = False
        self.simulation_mode = simulation_mode
        
        # Core modüller
        self.signal_processor = SignalProcessor()
        self.mt5_connector = None
        self.order_executor = OrderExecutor()
        self.telegram_handler = TelegramBotHandler(self)
        
        # Trading durumu
        self.last_signals = {}
        self.active_positions = {}
        self.trade_count = 0
        self.session_start_time = datetime.now()
        
        # Web Dashboard
        if FLASK_AVAILABLE:
            self.flask_app = Flask(__name__)
            self.setup_web_routes()
        
        self.dashboard_data = {
            'status': 'Stopped',
            'uptime': '00:00:00',
            'signals': 0,
            'balance': 0,
            'equity': 0,
            'positions': [],
            'last_analysis': 'No analysis yet'
        }
        
        print("🤖 MODULAR AI TRADING BOT başlatılıyor...")
        print(f"🎭 Simülasyon modu: {'Aktif' if self.simulation_mode else 'Kapalı'}")
        print("🚀 Modüler yapı ile optimize edildi")
    
    def start(self):
        """Bot'u başlat"""
        if self.running:
            print("⚠️ Bot zaten çalışıyor!")
            return
        
        print("\n🚀 Modular AI Bot başlatılıyor...")
        
        # MT5 bağlantısını test et
        self.mt5_connector = MT5Connector()
        if not self.mt5_connector.connect():
            print("❌ MT5 bağlantısı başarısız! Bot durduruluyor.")
            return False
        
        self.running = True
        self.session_start_time = datetime.now()
        
        # Telegram bot'u başlat
        if self.telegram_handler.enabled:
            self.telegram_handler.start_bot()
            print("📱 Telegram bot aktif!")
        
        # Web dashboard'ı başlat
        if FLASK_AVAILABLE:
            dashboard_thread = threading.Thread(target=self.run_web_dashboard, daemon=True)
            dashboard_thread.start()
            print("🌐 Web Dashboard: http://localhost:5000")
        
        print("✅ Modular AI Bot başarıyla başlatıldı!")
        print("📊 Triple AI analiz döngüsü başlıyor...\n")
        
        try:
            self._main_loop()
        except KeyboardInterrupt:
            print("\n⏹️ Bot durduruluyor...")
            self.stop()
        except Exception as e:
            print(f"\n❌ Bot hatası: {e}")
            self.stop()
        
        return True
    
    def stop(self):
        """Bot'u durdur"""
        if not self.running:
            print("⚠️ Bot zaten durdu!")
            return
        
        print("\n🛑 Bot durduruluyor...")
        self.running = False
        
        if self.mt5_connector:
            self.mt5_connector.disconnect()
        
        if self.telegram_handler:
            self.telegram_handler.stop_bot()
        
        # Session özeti
        session_duration = datetime.now() - self.session_start_time
        print(f"\n📊 SESSION ÖZETİ:")
        print(f"   Çalışma süresi: {session_duration}")
        print(f"   Toplam sinyal: {self.trade_count}")
        print(f"   Analiz edilen sembol: {len(TRADING_SYMBOLS)}")
        
        print("✅ Modular Bot başarıyla durduruldu!")
    
    def _main_loop(self):
        """Ana triple AI döngüsü"""
        print("🔄 Modular triple AI döngüsü başlatıldı...")
        
        while self.running:
            try:
                # Her sembol için analiz yap
                for symbol_name, symbol_config in TRADING_SYMBOLS.items():
                    if not self.running:
                        break
                    
                    symbol = symbol_config['symbol']
                    self._process_symbol(symbol)
                
                # Dashboard güncelle
                self.update_dashboard_data()
                
                # Bekleme
                print(f"⏱️ {DATA_UPDATE_INTERVAL_SECONDS} saniye bekleniyor...")
                time.sleep(DATA_UPDATE_INTERVAL_SECONDS)
                
            except Exception as e:
                print(f"❌ Ana döngü hatası: {e}")
                time.sleep(5)
    
    def _process_symbol(self, symbol):
        """Bir sembol için işlem sürecini yönet"""
        try:
            # Triple AI analizi yap
            triple_ai_result = self.signal_processor.analyze_symbol_triple_ai(symbol)
            
            if not triple_ai_result:
                return
            
            combined_analysis = triple_ai_result['combined_analysis']
            
            # Dashboard'a kaydet
            tech = triple_ai_result['technical_analysis']['overall_signal']
            news = triple_ai_result['news_signal']['signal']
            mtf = triple_ai_result['multi_tf_result']['overall_signal']
            final = combined_analysis['overall_signal']
            confidence = combined_analysis['confidence']
            
            self.dashboard_data['last_analysis'] = f"{symbol} T:{tech} H:{news} TF:{mtf} = {final} %{confidence:.1f}"
            
            # Güven kontrolü
            if confidence < 5.0:
                print(f"⚠️ Güven seviyesi yetersiz: %{confidence:.1f} < %5.0")
                return
            
            # Sinyal gücü kontrolü
            is_strong, strength_message = self.signal_processor.validate_signal_strength(combined_analysis)
            if not is_strong:
                print(f"⚠️ {strength_message}")
                return
            
            # Duplicate sinyal kontrolü
            if self._is_duplicate_signal(symbol, combined_analysis['overall_signal']):
                print(f"⚠️ {symbol} için yakın zamanda aynı sinyal verildi")
                return
            
            # Risk analizi ve trade işlemi
            self._execute_trade_process(triple_ai_result)
            
        except Exception as e:
            print(f"❌ {symbol} işlem süreci hatası: {e}")
    
    def _is_duplicate_signal(self, symbol, signal):
        """Duplicate sinyal kontrolü"""
        last_signal = self.last_signals.get(symbol)
        if (last_signal and 
            last_signal['signal'] == signal and 
            (datetime.now() - last_signal['time']).seconds < 300):
            return True
        return False
    
    def _execute_trade_process(self, triple_ai_result):
        """Trade sürecini yürüt"""
        try:
            symbol = triple_ai_result['symbol']
            combined = triple_ai_result['combined_analysis']
            technical = triple_ai_result['technical_analysis']
            
            # Basit risk hesaplama
            entry_price = technical['current_price']
            
            if combined['overall_signal'] == 'BUY':
                stop_loss = entry_price * 0.99
                take_profit = entry_price * 1.015
            else:  # SELL
                stop_loss = entry_price * 1.01
                take_profit = entry_price * 0.985
            
            risk_result = {
                'allowed': True,
                'risk_details': {
                    'lot_size': 0.01,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'risk_amount': 100.0,
                    'account_balance': 100000.0
                }
            }
            
            # Trade sinyali oluştur
            trade_signal = self.signal_processor.create_trade_signal(triple_ai_result, risk_result)
            
            if trade_signal:
                self._process_trade_signal(trade_signal)
                
                # Son sinyali kaydet
                self.last_signals[symbol] = {
                    'signal': combined['overall_signal'],
                    'time': datetime.now(),
                    'confidence': combined['confidence']
                }
            
        except Exception as e:
            print(f"❌ Trade süreci hatası: {e}")
    
    def _process_trade_signal(self, signal):
        """Trade sinyalini işle"""
        try:
            symbol = signal['symbol']
            signal_type = signal['signal']
            confidence = signal['confidence']
            
            print(f"\n🎯 {symbol} {signal_type} MODULAR AI SİNYALİ!")
            print("=" * 50)
            print(f"💰 Entry: {signal['entry_price']:.5f}")
            print(f"🛡️ Stop Loss: {signal['stop_loss']:.5f}")
            print(f"🎯 Take Profit: {signal['take_profit']:.5f}")
            print(f"📊 Lot Size: {signal['lot_size']}")
            print(f"🔥 Güven: %{confidence:.1f}")
            
            # Simülasyon veya gerçek trade
            if self.simulation_mode:
                print("🎭 SİMÜLASYON MODU - Modular AI Sinyal kaydedildi")
                trade_result = self._simulate_trade(signal)
                
                # Telegram bildirimi
                self._send_telegram_notification(signal)
                        
            else:
                print("🚀 CANLI MOD - Modular AI trade açılıyor...")
                trade_result = self._execute_real_trade(signal)
            
            self.trade_count += 1
            
            # Detaylı analiz yazdır
            self.signal_processor.print_detailed_signal_analysis(signal)
            
        except Exception as e:
            print(f"❌ Sinyal işleme hatası: {e}")
    
    def _simulate_trade(self, signal):
        """Demo trade simülasyonu"""
        ticket = random.randint(100000, 999999)
        
        print(f"🎭 SİMÜLE EDİLEN MODULAR AI TRADE:")
        print(f"   Ticket: {ticket}")
        print(f"   Entry: {signal['entry_price']:.5f}")
        print(f"   Lot: {signal['lot_size']}")
        print(f"   Modular AI Güven: %{signal['confidence']:.1f}")
        
        return {
            'success': True,
            'ticket': ticket,
            'symbol': signal['symbol'],
            'type': signal['signal'],
            'volume': signal['lot_size'],
            'price': signal['entry_price'],
            'simulated': True
        }
    
    def _execute_real_trade(self, signal):
        """Gerçek trade çalıştır"""
        try:
            result = self.order_executor.execute_market_order(
                symbol=signal['symbol'],
                order_type=signal['signal'],
                lot_size=signal['lot_size'],
                stop_loss=signal['stop_loss'],
                take_profit=signal['take_profit'],
                comment=f"Modular AI - Conf:{signal['confidence']:.0f}%"
            )
            
            if result['success']:
                self.active_positions[result['ticket']] = {
                    'signal': signal,
                    'trade_result': result,
                    'open_time': datetime.now()
                }
                print(f"🎯 Modular AI Trade ID {result['ticket']} aktif")
            
            return result
            
        except Exception as e:
            print(f"❌ Gerçek trade hatası: {e}")
            return {'success': False, 'error': str(e)}
    
    def _send_telegram_notification(self, signal):
        """Telegram bildirimi gönder"""
        if self.telegram_handler.enabled:
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.telegram_handler.send_signal_notification(signal))
                loop.close()
            except Exception as e:
                print(f"❌ Telegram bildirim hatası: {e}")
    
    def get_status(self):
        """Bot durumunu getir"""
        if not self.running:
            return "Modular AI Bot durduruldu"
        
        uptime = datetime.now() - self.session_start_time
        
        return f"""
🤖 MODULAR AI TRADING BOT DURUMU
==================================
▶️ Durum: Çalışıyor
⏱️ Çalışma süresi: {uptime}
📊 Toplam sinyal: {self.trade_count}
🔍 Analiz edilen: {len(TRADING_SYMBOLS)} sembol
🏗️ Yapı: Modüler
🚀 AI: Triple Engine (Teknik + Haber + Multi-TF)
"""
    
    # Web Dashboard Methods
    def setup_web_routes(self):
        """Web dashboard route'larını ayarla"""
        
        @self.flask_app.route('/')
        def dashboard():
            return f"""
<!DOCTYPE html>
<html><head><title>🤖 Modular AI Trading Bot</title>
<style>
body {{ font-family: Arial; background: #1a1a2e; color: white; margin: 0; padding: 20px; }}
.container {{ max-width: 800px; margin: 0 auto; }}
.header {{ text-align: center; margin-bottom: 30px; }}
.cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }}
.card {{ background: #16213e; padding: 20px; border-radius: 10px; border: 1px solid #0f3460; }}
.card h3 {{ color: #4fc3f7; margin-top: 0; }}
.metric {{ display: flex; justify-content: space-between; margin: 10px 0; padding: 5px 0; border-bottom: 1px solid #333; }}
.value {{ color: #4caf50; font-weight: bold; }}
.status-running {{ color: #4caf50; }}
.status-stopped {{ color: #f44336; }}
.modular {{ background: linear-gradient(45deg, #667eea, #764ba2); padding: 10px; border-radius: 5px; }}
</style>
<meta http-equiv="refresh" content="5">
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🤖 Modular AI Trading Bot</h1>
        <div class="modular">🏗️ Modüler Yapı | 🚀 Triple AI Engine</div>
    </div>
    
    <div class="cards">
        <div class="card">
            <h3>🚀 Bot Status</h3>
            <div class="metric">
                <span>Status:</span>
                <span class="value status-{self.dashboard_data['status'].lower()}">{self.dashboard_data['status']}</span>
            </div>
            <div class="metric">
                <span>Architecture:</span>
                <span class="value">Modular</span>
            </div>
            <div class="metric">
                <span>Signals:</span>
                <span class="value">{self.dashboard_data['signals']}</span>
            </div>
        </div>
        
        <div class="card">
            <h3>💰 Account</h3>
            <div class="metric">
                <span>Balance:</span>
                <span class="value">${self.dashboard_data['balance']:,.2f}</span>
            </div>
            <div class="metric">
                <span>Equity:</span>
                <span class="value">${self.dashboard_data['equity']:,.2f}</span>
            </div>
            <div class="metric">
                <span>Positions:</span>
                <span class="value">{len(self.dashboard_data['positions'])}</span>
            </div>
        </div>
        
        <div class="card">
            <h3>📊 Last Analysis</h3>
            <div class="metric">
                <span>Result:</span>
                <span class="value">{self.dashboard_data['last_analysis']}</span>
            </div>
            <div class="metric">
                <span>Time:</span>
                <span class="value">{datetime.now().strftime('%H:%M:%S')}</span>
            </div>
        </div>
    </div>
    
    <div style="text-align: center; margin-top: 30px;">
        <p>🔄 Auto-refresh every 5 seconds</p>
        <p>🏗️ Modular Architecture | 🚀 Triple AI</p>
    </div>
</div>
</body>
</html>"""
    
    def update_dashboard_data(self):
        """Dashboard verilerini güncelle"""
        try:
            self.dashboard_data['status'] = 'Running' if self.running else 'Stopped'
            if self.running:
                uptime = datetime.now() - self.session_start_time
                self.dashboard_data['uptime'] = str(uptime).split('.')[0]
            
            self.dashboard_data['signals'] = self.trade_count
            
            # MT5 verileri
            with MT5Connector() as mt5_conn:
                if mt5_conn.connected:
                    account_info = mt5_conn.get_account_info()
                    if account_info:
                        self.dashboard_data['balance'] = account_info['balance']
                        self.dashboard_data['equity'] = account_info['equity']
                    
                    positions = mt5_conn.get_positions()
                    self.dashboard_data['positions'] = positions
        except:
            pass
    
    def run_web_dashboard(self):
        """Web dashboard'ı çalıştır"""
        try:
            self.flask_app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
        except Exception as e:
            print(f"❌ Web dashboard hatası: {e}")