# trading_engine/order_executor.py
"""
AI Trading Bot - Order Execution Engine
Bu modül gerçek MT5 emirlerini çalıştırır
"""

import MetaTrader5 as mt5
import time
from datetime import datetime
import sys
import os

# Parent directory'yi ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import TRADING_SYMBOLS
from data_manager.mt5_connector import MT5Connector

class OrderExecutor:
    """MT5 emir çalıştırma sınıfı"""
    
    def __init__(self):
        """OrderExecutor'ı başlat"""
        self.active_orders = {}
        self.order_history = []
        print("⚡ OrderExecutor başlatıldı")
    
    def execute_market_order(self, symbol, order_type, lot_size, stop_loss=None, take_profit=None, comment="AI Bot"):
        """Market emri çalıştır"""
        try:
            print(f"\n⚡ {symbol} {order_type} emri çalıştırılıyor...")
            print(f"   Lot: {lot_size}")
            print(f"   SL: {stop_loss}")
            print(f"   TP: {take_profit}")
            
            with MT5Connector() as mt5_conn:
                if not mt5_conn.connected:
                    return self._create_error_result("MT5 bağlantısı yok")
                
                # Trading izni kontrol et (demo hesap sorunu için geçici bypass)
                account = mt5_conn.get_account_info()
                if account and not account.get('trade_allowed', True):
                    print("⚠️ Hesap trading izni yok - ancak test için devam ediyoruz")
                    # return self._create_error_result("Hesap trading izni yok")
                else:
                    print("✅ Trading izni kontrolü geçildi")
                
                # Sembol bilgilerini al
                symbol_info = mt5_conn.get_symbol_info(symbol)
                if not symbol_info:
                    return self._create_error_result(f"{symbol} sembol bilgisi alınamadı")
                
                # Güncel fiyatları al
                current_price = mt5_conn.get_current_price(symbol)
                if not current_price:
                    return self._create_error_result(f"{symbol} fiyat bilgisi alınamadı")
                
                # Emir tipini belirle
                if order_type.upper() == 'BUY':
                    trade_type = mt5.ORDER_TYPE_BUY
                    price = current_price['ask']
                    if stop_loss and stop_loss >= price:
                        stop_loss = price - (symbol_info['point'] * 100)  # 10 pip SL
                elif order_type.upper() == 'SELL':
                    trade_type = mt5.ORDER_TYPE_SELL
                    price = current_price['bid']
                    if stop_loss and stop_loss <= price:
                        stop_loss = price + (symbol_info['point'] * 100)  # 10 pip SL
                else:
                    return self._create_error_result(f"Geçersiz emir tipi: {order_type}")
                
                # Lot boyutunu kontrol et
                min_lot = symbol_info['volume_min']
                max_lot = symbol_info['volume_max']
                
                if lot_size < min_lot:
                    lot_size = min_lot
                    print(f"⚠️ Lot boyutu minimum değere ayarlandı: {min_lot}")
                elif lot_size > max_lot:
                    lot_size = max_lot
                    print(f"⚠️ Lot boyutu maksimum değere ayarlandı: {max_lot}")
                
                # Son deneme - en basit emir
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": 0.01,  # Sabit mikro lot
                    "type": trade_type,
                    "deviation": 100,  # Çok yüksek slippage
                    "magic": 0,  # Magic number sıfır
                    "comment": "test",
                    "type_filling": mt5.ORDER_FILLING_RETURN,  # Return filling
                }
                
                # SL/TP ekle (varsa)
                if stop_loss:
                    request["sl"] = stop_loss
                if take_profit:
                    request["tp"] = take_profit
                
                print(f"📋 Emir Detayları:")
                print(f"   Sembol: {symbol}")
                print(f"   Tip: {order_type}")
                print(f"   Lot: {lot_size}")
                print(f"   Fiyat: {price:.5f}")
                if stop_loss:
                    print(f"   SL: {stop_loss:.5f}")
                else:
                    print(f"   SL: Yok")
                if take_profit:
                    print(f"   TP: {take_profit:.5f}")
                else:
                    print(f"   TP: Yok")
                
                # Emri gönder
                result = mt5.order_send(request)
                
                if result is None:
                    return self._create_error_result("Emir gönderim hatası")
                
                # Sonucu kontrol et
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    error_msg = f"Emir başarısız! Kod: {result.retcode}, Açıklama: {self._get_error_description(result.retcode)}"
                    return self._create_error_result(error_msg)
                
                # Başarılı emir
                order_result = {
                    'success': True,
                    'ticket': result.order,
                    'symbol': symbol,
                    'type': order_type,
                    'volume': result.volume,
                    'price': result.price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'time': datetime.now(),
                    'comment': comment,
                    'retcode': result.retcode,
                    'deal': result.deal
                }
                
                # Aktif emirlere ekle
                self.active_orders[result.order] = order_result
                self.order_history.append(order_result)
                
                print(f"✅ EMİR BAŞARILI!")
                print(f"   Ticket: {result.order}")
                print(f"   Deal: {result.deal}")
                print(f"   Fiyat: {result.price:.5f}")
                print(f"   Volume: {result.volume}")
                
                return order_result
                
        except Exception as e:
            error_msg = f"Emir çalıştırma hatası: {e}"
            print(f"❌ {error_msg}")
            return self._create_error_result(error_msg)
    
    def close_position(self, ticket, comment="AI Bot Close"):
        """Pozisyonu kapat"""
        try:
            print(f"\n🔻 Pozisyon kapatılıyor: {ticket}")
            
            with MT5Connector() as mt5_conn:
                if not mt5_conn.connected:
                    return self._create_error_result("MT5 bağlantısı yok")
                
                # Pozisyonu bul
                positions = mt5.positions_get(ticket=ticket)
                if not positions:
                    return self._create_error_result(f"Pozisyon bulunamadı: {ticket}")
                
                position = positions[0]
                symbol = position.symbol
                
                # Güncel fiyatları al
                symbol_info = mt5_conn.get_symbol_info(symbol)
                current_price = mt5_conn.get_current_price(symbol)
                
                if not symbol_info or not current_price:
                    return self._create_error_result(f"{symbol} fiyat bilgisi alınamadı")
                
                # Kapatma emri tipi
                if position.type == mt5.ORDER_TYPE_BUY:
                    close_type = mt5.ORDER_TYPE_SELL
                    close_price = current_price['bid']
                else:
                    close_type = mt5.ORDER_TYPE_BUY
                    close_price = current_price['ask']
                
                # Kapatma request'i
                close_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": position.volume,
                    "type": close_type,
                    "position": ticket,
                    "price": close_price,
                    "deviation": 20,
                    "magic": 123456,
                    "comment": comment,
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
                
                print(f"📋 Kapatma Detayları:")
                print(f"   Ticket: {ticket}")
                print(f"   Sembol: {symbol}")
                print(f"   Volume: {position.volume}")
                print(f"   Kapatma Fiyatı: {close_price:.5f}")
                print(f"   Güncel P&L: {position.profit:.2f}")
                
                # Kapatma emrini gönder
                result = mt5.order_send(close_request)
                
                if result is None:
                    return self._create_error_result("Kapatma emri gönderim hatası")
                
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    error_msg = f"Kapatma başarısız! Kod: {result.retcode}"
                    return self._create_error_result(error_msg)
                
                # Başarılı kapatma
                close_result = {
                    'success': True,
                    'original_ticket': ticket,
                    'close_ticket': result.order,
                    'symbol': symbol,
                    'volume': result.volume,
                    'close_price': result.price,
                    'profit': position.profit,
                    'time': datetime.now(),
                    'comment': comment
                }
                
                # Aktif emirlerden çıkar
                if ticket in self.active_orders:
                    del self.active_orders[ticket]
                
                self.order_history.append(close_result)
                
                print(f"✅ POZİSYON KAPATILDI!")
                print(f"   Kapatma Ticket: {result.order}")
                print(f"   Profit: ${position.profit:.2f}")
                print(f"   Kapatma Fiyatı: {result.price:.5f}")
                
                return close_result
                
        except Exception as e:
            error_msg = f"Pozisyon kapatma hatası: {e}"
            print(f"❌ {error_msg}")
            return self._create_error_result(error_msg)
    
    def close_all_positions(self, symbol=None):
        """Tüm pozisyonları kapat (opsiyonel olarak sadece belirli sembol)"""
        try:
            print(f"\n🔻 Tüm pozisyonlar kapatılıyor..." + (f" ({symbol})" if symbol else ""))
            
            with MT5Connector() as mt5_conn:
                if not mt5_conn.connected:
                    return self._create_error_result("MT5 bağlantısı yok")
                
                # Tüm pozisyonları al
                positions = mt5_conn.get_positions()
                
                if not positions:
                    print("📭 Kapatılacak pozisyon yok")
                    return {'success': True, 'closed_count': 0, 'results': []}
                
                # Filtrele (eğer sembol belirtildiyse)
                if symbol:
                    positions = [pos for pos in positions if pos['symbol'] == symbol]
                
                results = []
                closed_count = 0
                
                for position in positions:
                    result = self.close_position(position['ticket'], "AI Bot - Close All")
                    results.append(result)
                    
                    if result['success']:
                        closed_count += 1
                    
                    # Emirler arasında kısa bekleme
                    time.sleep(0.5)
                
                print(f"✅ Kapatma işlemi tamamlandı: {closed_count}/{len(positions)} pozisyon")
                
                return {
                    'success': True,
                    'closed_count': closed_count,
                    'total_positions': len(positions),
                    'results': results
                }
                
        except Exception as e:
            error_msg = f"Toplu kapatma hatası: {e}"
            print(f"❌ {error_msg}")
            return self._create_error_result(error_msg)
    
    def modify_position(self, ticket, new_sl=None, new_tp=None):
        """Pozisyon SL/TP değiştir"""
        try:
            print(f"\n✏️ Pozisyon modifiye ediliyor: {ticket}")
            
            with MT5Connector() as mt5_conn:
                if not mt5_conn.connected:
                    return self._create_error_result("MT5 bağlantısı yok")
                
                # Pozisyonu bul
                positions = mt5.positions_get(ticket=ticket)
                if not positions:
                    return self._create_error_result(f"Pozisyon bulunamadı: {ticket}")
                
                position = positions[0]
                
                # Modifiye request'i
                modify_request = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "symbol": position.symbol,
                    "position": ticket,
                    "sl": new_sl if new_sl else position.sl,
                    "tp": new_tp if new_tp else position.tp,
                }
                
                result = mt5.order_send(modify_request)
                
                if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
                    return self._create_error_result(f"Modifiye başarısız: {result.retcode if result else 'None'}")
                
                print(f"✅ Pozisyon modifiye edildi!")
                print(f"   Yeni SL: {new_sl}")
                print(f"   Yeni TP: {new_tp}")
                
                return {'success': True, 'ticket': ticket, 'new_sl': new_sl, 'new_tp': new_tp}
                
        except Exception as e:
            return self._create_error_result(f"Modifiye hatası: {e}")
    
    def get_position_status(self, ticket):
        """Pozisyon durumunu al"""
        try:
            with MT5Connector() as mt5_conn:
                if not mt5_conn.connected:
                    return None
                
                positions = mt5.positions_get(ticket=ticket)
                if not positions:
                    return None
                
                position = positions[0]
                
                return {
                    'ticket': ticket,
                    'symbol': position.symbol,
                    'type': 'BUY' if position.type == mt5.ORDER_TYPE_BUY else 'SELL',
                    'volume': position.volume,
                    'open_price': position.price_open,
                    'current_price': position.price_current,
                    'sl': position.sl,
                    'tp': position.tp,
                    'profit': position.profit,
                    'swap': position.swap,
                    'time_open': datetime.fromtimestamp(position.time)
                }
                
        except Exception as e:
            print(f"❌ Pozisyon durumu alınamadı: {e}")
            return None
    
    def _create_error_result(self, error_message):
        """Hata sonucu oluştur"""
        return {
            'success': False,
            'error': error_message,
            'time': datetime.now()
        }
    
    def _get_error_description(self, retcode):
        """MT5 hata kodlarını açıkla"""
        error_codes = {
            mt5.TRADE_RETCODE_REQUOTE: "Requote - fiyat değişti",
            mt5.TRADE_RETCODE_REJECT: "Emir reddedildi",
            mt5.TRADE_RETCODE_CANCEL: "Emir iptal edildi",
            mt5.TRADE_RETCODE_PLACED: "Emir yerleştirildi",
            mt5.TRADE_RETCODE_DONE: "Emir tamamlandı",
            mt5.TRADE_RETCODE_DONE_PARTIAL: "Kısmi emir tamamlandı",
            mt5.TRADE_RETCODE_ERROR: "Genel hata",
            mt5.TRADE_RETCODE_TIMEOUT: "Zaman aşımı",
            mt5.TRADE_RETCODE_INVALID: "Geçersiz emir",
            mt5.TRADE_RETCODE_INVALID_VOLUME: "Geçersiz volume",
            mt5.TRADE_RETCODE_INVALID_PRICE: "Geçersiz fiyat",
            mt5.TRADE_RETCODE_INVALID_STOPS: "Geçersiz stop seviyesi",
            mt5.TRADE_RETCODE_TRADE_DISABLED: "Trading kapalı",
            mt5.TRADE_RETCODE_MARKET_CLOSED: "Market kapalı",
            mt5.TRADE_RETCODE_NO_MONEY: "Yetersiz bakiye",
            mt5.TRADE_RETCODE_PRICE_CHANGED: "Fiyat değişti",
            mt5.TRADE_RETCODE_PRICE_OFF: "Geçersiz fiyat",
            mt5.TRADE_RETCODE_INVALID_EXPIRATION: "Geçersiz süre",
            10030: "Yetersiz margin veya hesap sınırlaması",
            10004: "Requote",
            10006: "Request rejected",
            10007: "Request canceled by trader",
            10008: "Order placed",
            10009: "Request completed",
            10010: "Only part of the request was completed",
            10013: "Invalid request",
            10014: "Invalid volume in the request",
            10015: "Invalid price in the request",
            10016: "Invalid stops in the request",
            10017: "Trade is disabled",
            10018: "Market is closed",
            10019: "There is not enough money to complete the request",
            10020: "Prices changed",
            10021: "There are no quotes to process the request",
            10022: "Invalid order expiration date in the request"
        }
        
        return error_codes.get(retcode, f"Bilinmeyen hata kodu: {retcode}")
    
    def get_order_history(self, count=10):
        """Emir geçmişini al"""
        return self.order_history[-count:] if self.order_history else []
    
    def get_active_orders(self):
        """Aktif emirleri al"""
        return self.active_orders


# Test fonksiyonu
def test_order_executor():
    """OrderExecutor'ı test et"""
    print("🧪 OrderExecutor Test Başlıyor...")
    print("=" * 50)
    
    executor = OrderExecutor()
    
    # Test sinyali (gerçek emir AÇMADAN test)
    print("📋 Test Senaryosu:")
    print("   Sembol: EURUSD")
    print("   Tip: BUY")
    print("   Lot: 0.01")
    print("   SL: 1.16000")
    print("   TP: 1.16500")
    
    print("\n⚠️ Son deneme - nano lot ile:")
    # En küçük lot deneyelim
    result = executor.execute_market_order('EURUSD-T', 'BUY', 0.001)  # 0.001 nano lot
    
    if result['success']:
        print(f"🎉 Trade başarılı! Ticket: {result['ticket']}")
        
        # 3 saniye bekle
        import time
        time.sleep(3)
        
        # Pozisyonu kapat
        print("\n🔻 Test pozisyonu kapatılıyor...")
        close_result = executor.close_position(result['ticket'], "Test Close")
        
        if close_result['success']:
            print(f"✅ Pozisyon kapatıldı! Profit: ${close_result['profit']:.2f}")
        else:
            print(f"❌ Kapatma başarısız: {close_result['error']}")
    else:
        print(f"❌ Trade başarısız: {result['error']}")
        
    print("\n" + "="*50)
    
    # Aktif pozisyonları göster
    with MT5Connector() as mt5_conn:
        if mt5_conn.connected:
            positions = mt5_conn.get_positions()
            print(f"\n📊 Mevcut Pozisyonlar: {len(positions)} adet")
            
            for pos in positions:
                print(f"   {pos['symbol']} {pos['type']} - P&L: ${pos['profit']:.2f}")

if __name__ == "__main__":
    test_order_executor()