# trading_engine/risk_manager.py
"""
AI Trading Bot - Risk Yönetimi Modülü
Bu modül tüm risk kontrollerini, position sizing ve SL/TP hesaplamalarını yapar
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Parent directory'yi ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import (
    DAILY_MAX_LOSS_PERCENT, MAX_POSITIONS_PER_SYMBOL, MAX_TOTAL_POSITIONS,
    RISK_PER_TRADE, DEFAULT_LOT_SIZE, MIN_ACCOUNT_BALANCE,
    DEFAULT_STOP_LOSS_PIPS, DEFAULT_TAKE_PROFIT_PIPS, TRADING_SYMBOLS
)
from data_manager.mt5_connector import MT5Connector

class RiskManager:
    """Risk yönetimi ve position sizing sınıfı"""
    
    def __init__(self):
        """RiskManager'ı başlat"""
        self.daily_loss_tracker = {}
        self.position_count = {}
        print("🛡️ RiskManager başlatıldı")
    
    def check_daily_loss_limit(self, account_balance, daily_pnl):
        """Günlük zarar limitini kontrol et"""
        max_daily_loss = account_balance * (DAILY_MAX_LOSS_PERCENT / 100)
        
        if daily_pnl <= -max_daily_loss:
            return {
                'allowed': False,
                'reason': f'Günlük zarar limiti aşıldı: ${abs(daily_pnl):.2f} / ${max_daily_loss:.2f}',
                'current_loss': abs(daily_pnl),
                'max_loss': max_daily_loss
            }
        
        return {
            'allowed': True,
            'reason': 'Günlük zarar limiti içinde',
            'current_loss': abs(daily_pnl) if daily_pnl < 0 else 0,
            'max_loss': max_daily_loss,
            'remaining': max_daily_loss - abs(daily_pnl) if daily_pnl < 0 else max_daily_loss
        }
    
    def check_position_limits(self, symbol, current_positions):
        """Pozisyon limitleri kontrol et"""
        # Toplam pozisyon sayısı
        total_positions = len(current_positions)
        if total_positions >= MAX_TOTAL_POSITIONS:
            return {
                'allowed': False,
                'reason': f'Max toplam pozisyon limiti aşıldı: {total_positions}/{MAX_TOTAL_POSITIONS}'
            }
        
        # Sembole özel pozisyon sayısı
        symbol_positions = [pos for pos in current_positions if pos['symbol'] == symbol]
        if len(symbol_positions) >= MAX_POSITIONS_PER_SYMBOL:
            return {
                'allowed': False,
                'reason': f'{symbol} için max pozisyon limiti aşıldı: {len(symbol_positions)}/{MAX_POSITIONS_PER_SYMBOL}'
            }
        
        return {
            'allowed': True,
            'reason': 'Pozisyon limitleri içinde',
            'total_positions': total_positions,
            'symbol_positions': len(symbol_positions)
        }
    
    def calculate_position_size(self, account_balance, symbol, entry_price, stop_loss_price):
        """Position size hesapla (Risk bazlı)"""
        try:
            # Sembol bilgilerini al
            symbol_info = TRADING_SYMBOLS.get(symbol)
            if not symbol_info:
                return {
                    'lot_size': DEFAULT_LOT_SIZE,
                    'reason': f'Sembol bilgisi bulunamadı, varsayılan lot: {DEFAULT_LOT_SIZE}'
                }
            
            # Risk miktarını hesapla (hesabın %2'si)
            risk_amount = account_balance * (RISK_PER_TRADE / 100)
            
            # Pip değerini hesapla
            pip_difference = abs(entry_price - stop_loss_price)
            
            # Position value ve lot size hesaplama
            point_value = symbol_info['point_value']
            pip_value = pip_difference / point_value
            
            # Lot size hesapla
            if pip_value > 0:
                # Pip başına değer (1 lot için)
                pip_value_per_lot = self._get_pip_value_per_lot(symbol)
                
                # Risk bazlı lot size
                calculated_lot = risk_amount / (pip_value * pip_value_per_lot)
                
                # Minimum ve maksimum lotları kontrol et
                min_lot = symbol_info['min_lot']
                max_lot = symbol_info['max_lot']
                
                # Lot size'ı sınırlar içinde tut
                final_lot = max(min_lot, min(calculated_lot, max_lot))
                
                # Lot size'ı standart adımlara yuvarla (0.01'in katları)
                final_lot = round(final_lot, 2)
                
                return {
                    'lot_size': final_lot,
                    'risk_amount': risk_amount,
                    'pip_difference': pip_value,
                    'calculated_lot': calculated_lot,
                    'reason': f'Risk bazlı: ${risk_amount:.2f} risk, {pip_value:.1f} pip fark'
                }
            else:
                return {
                    'lot_size': DEFAULT_LOT_SIZE,
                    'reason': 'Stop loss farkı çok küçük, varsayılan lot kullanıldı'
                }
                
        except Exception as e:
            print(f"❌ Position size hesaplama hatası: {e}")
            return {
                'lot_size': DEFAULT_LOT_SIZE,
                'reason': f'Hesaplama hatası, varsayılan lot: {DEFAULT_LOT_SIZE}'
            }
    
    def calculate_stop_loss_take_profit(self, symbol, entry_price, signal_type, atr_value=None):
        """Stop Loss ve Take Profit seviyelerini hesapla"""
        try:
            symbol_info = TRADING_SYMBOLS.get(symbol)
            if not symbol_info:
                return None
            
            point_value = symbol_info['point_value']
            
            # ATR bazlı SL/TP (varsa)
            if atr_value and not pd.isna(atr_value):
                # ATR'ın 1.5 katı SL, 2.5 katı TP
                sl_distance = atr_value * 1.5
                tp_distance = atr_value * 2.5
            else:
                # Varsayılan pip değerleri
                sl_distance = DEFAULT_STOP_LOSS_PIPS * point_value
                tp_distance = DEFAULT_TAKE_PROFIT_PIPS * point_value
            
            if signal_type.upper() == 'BUY':
                stop_loss = entry_price - sl_distance
                take_profit = entry_price + tp_distance
            else:  # SELL
                stop_loss = entry_price + sl_distance
                take_profit = entry_price - tp_distance
            
            return {
                'stop_loss': round(stop_loss, symbol_info.get('digits', 5)),
                'take_profit': round(take_profit, symbol_info.get('digits', 5)),
                'sl_distance': sl_distance,
                'tp_distance': tp_distance,
                'method': 'ATR' if atr_value else 'Fixed'
            }
            
        except Exception as e:
            print(f"❌ SL/TP hesaplama hatası: {e}")
            return None
    
    def _get_pip_value_per_lot(self, symbol):
        """1 lot için pip değerini hesapla"""
        # Basitleştirilmiş pip değerleri
        pip_values = {
            'EURUSD': 10.0,  # $10 per pip for 1 lot
            'GBPUSD': 10.0,
            'USDCAD': 10.0,
            'USDJPY': 10.0,
            'XAUUSD': 1.0,   # $1 per pip for gold
            'XAGUSD': 0.5,   # $0.5 per pip for silver
        }
        
        return pip_values.get(symbol, 10.0)  # Varsayılan $10
    
    def validate_trade_risk(self, symbol, signal_type, entry_price, confidence, atr_value=None):
        """Bir trade'in tüm risk parametrelerini kontrol et"""
        print(f"\n🛡️ {symbol} {signal_type} trade risk analizi...")
        
        validation_result = {
            'allowed': True,
            'reasons': [],
            'warnings': [],
            'risk_details': {}
        }
        
        try:
            with MT5Connector() as mt5_conn:
                if not mt5_conn.connected:
                    validation_result['allowed'] = False
                    validation_result['reasons'].append('MT5 bağlantısı yok')
                    return validation_result
                
                # Hesap bilgilerini al
                account_info = mt5_conn.get_account_info()
                if not account_info:
                    validation_result['allowed'] = False
                    validation_result['reasons'].append('Hesap bilgileri alınamadı')
                    return validation_result
                
                balance = account_info['balance']
                equity = account_info['equity']
                
                # Minimum bakiye kontrolü
                if balance < MIN_ACCOUNT_BALANCE:
                    validation_result['allowed'] = False
                    validation_result['reasons'].append(f'Yetersiz bakiye: ${balance:.2f} < ${MIN_ACCOUNT_BALANCE:.2f}')
                
                # Günlük P&L hesapla (basit - bugünkü profit)
                daily_pnl = account_info['profit']
                
                # Günlük zarar limitini kontrol et
                daily_check = self.check_daily_loss_limit(balance, daily_pnl)
                if not daily_check['allowed']:
                    validation_result['allowed'] = False
                    validation_result['reasons'].append(daily_check['reason'])
                
                # Mevcut pozisyonları al
                current_positions = mt5_conn.get_positions()
                
                # Pozisyon limitlerini kontrol et
                position_check = self.check_position_limits(symbol, current_positions)
                if not position_check['allowed']:
                    validation_result['allowed'] = False
                    validation_result['reasons'].append(position_check['reason'])
                
                # SL/TP hesapla
                sl_tp = self.calculate_stop_loss_take_profit(symbol, entry_price, signal_type, atr_value)
                if not sl_tp:
                    validation_result['allowed'] = False
                    validation_result['reasons'].append('SL/TP hesaplanamadı')
                    return validation_result
                
                # Position size hesapla
                position_size = self.calculate_position_size(balance, symbol, entry_price, sl_tp['stop_loss'])
                
                # Risk detaylarını kaydet
                validation_result['risk_details'] = {
                    'account_balance': balance,
                    'account_equity': equity,
                    'daily_pnl': daily_pnl,
                    'daily_loss_limit': daily_check['max_loss'],
                    'position_count': len(current_positions),
                    'entry_price': entry_price,
                    'stop_loss': sl_tp['stop_loss'],
                    'take_profit': sl_tp['take_profit'],
                    'lot_size': position_size['lot_size'],
                    'risk_amount': position_size.get('risk_amount', 0),
                    'confidence': confidence
                }
                
                # Uyarılar
                if confidence < 60:
                    validation_result['warnings'].append(f'Düşük güven seviyesi: %{confidence:.1f}')
                
                if len(current_positions) > MAX_TOTAL_POSITIONS * 0.8:
                    validation_result['warnings'].append('Pozisyon sayısı limite yaklaşıyor')
                
                if daily_check.get('remaining', 0) < daily_check['max_loss'] * 0.3:
                    validation_result['warnings'].append('Günlük zarar limitine yaklaşılıyor')
                
                print(f"✅ Risk analizi tamamlandı")
                print(f"   Lot Size: {position_size['lot_size']}")
                print(f"   Risk: ${position_size.get('risk_amount', 0):.2f}")
                print(f"   SL: {sl_tp['stop_loss']:.5f}")
                print(f"   TP: {sl_tp['take_profit']:.5f}")
                
                return validation_result
                
        except Exception as e:
            print(f"❌ Risk validasyon hatası: {e}")
            validation_result['allowed'] = False
            validation_result['reasons'].append(f'Risk analizi hatası: {e}')
            return validation_result
    
    def get_risk_summary(self):
        """Risk durumu özeti"""
        try:
            with MT5Connector() as mt5_conn:
                if not mt5_conn.connected:
                    return None
                
                account_info = mt5_conn.get_account_info()
                positions = mt5_conn.get_positions()
                
                if not account_info:
                    return None
                
                # Günlük P&L
                daily_pnl = account_info['profit']
                daily_check = self.check_daily_loss_limit(account_info['balance'], daily_pnl)
                
                summary = {
                    'account_balance': account_info['balance'],
                    'account_equity': account_info['equity'],
                    'free_margin': account_info['free_margin'],
                    'margin_level': account_info.get('margin_level', 0),
                    'daily_pnl': daily_pnl,
                    'daily_loss_remaining': daily_check.get('remaining', 0),
                    'total_positions': len(positions),
                    'max_positions': MAX_TOTAL_POSITIONS,
                    'trading_allowed': daily_check['allowed'] and len(positions) < MAX_TOTAL_POSITIONS
                }
                
                return summary
                
        except Exception as e:
            print(f"❌ Risk özeti hatası: {e}")
            return None


# Test fonksiyonu
def test_risk_manager():
    """RiskManager'ı test et"""
    print("🧪 RiskManager Test Başlıyor...")
    print("=" * 50)
    
    risk_mgr = RiskManager()
    
    # EURUSD için risk analizi
    test_entry_price = 1.16250
    test_confidence = 75.0
    
    result = risk_mgr.validate_trade_risk(
        symbol='EURUSD',
        signal_type='BUY',
        entry_price=test_entry_price,
        confidence=test_confidence,
        atr_value=0.0015  # Test ATR değeri
    )
    
    if result:
        print(f"\n📊 RİSK ANALİZİ SONUCU:")
        print(f"   İzin Durumu: {'✅ İZİNLİ' if result['allowed'] else '❌ İZİNSİZ'}")
        
        if not result['allowed']:
            print(f"   ❌ Nedenler:")
            for reason in result['reasons']:
                print(f"      - {reason}")
        
        if result['warnings']:
            print(f"   ⚠️ Uyarılar:")
            for warning in result['warnings']:
                print(f"      - {warning}")
        
        if result['risk_details']:
            details = result['risk_details']
            print(f"\n📋 RİSK DETAYLARI:")
            print(f"   Bakiye: ${details['account_balance']:,.2f}")
            print(f"   Lot Size: {details['lot_size']}")
            print(f"   Risk Tutarı: ${details.get('risk_amount', 0):.2f}")
            print(f"   Entry: {details['entry_price']:.5f}")
            print(f"   Stop Loss: {details['stop_loss']:.5f}")
            print(f"   Take Profit: {details['take_profit']:.5f}")
    
    # Risk özeti
    print(f"\n📊 RİSK ÖZETİ:")
    summary = risk_mgr.get_risk_summary()
    if summary:
        for key, value in summary.items():
            print(f"   {key}: {value}")

if __name__ == "__main__":
    test_risk_manager()