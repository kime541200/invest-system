import pytest
import backtrader as bt
import pandas as pd
from datetime import datetime, timedelta
from invest_system.strategies.ma_cross import MACrossStrategy
from invest_system.strategies.rsi import RSIStrategy

def run_strategy_test(strategy_class, df, **kwargs):
    """通用測試輔助函式"""
    data = bt.feeds.PandasData(
        dataname=df,
        datetime='datetime',
        open='open',
        high='high',
        low='low',
        close='close',
        volume='volume',
        openinterest=-1
    )
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy_class, **kwargs)
    cerebro.adddata(data)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.broker.setcash(1000000.0)
    return cerebro.run(), cerebro

def test_ma_cross_signal():
    """驗證 MA 交叉策略的買入訊號"""
    dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(100)]
    prices = [100.0 - i*0.1 for i in range(50)] + [200.0] * 50
    df = pd.DataFrame({'datetime': dates, 'open': prices, 'high': [p+2 for p in prices], 'low': [p-2 for p in prices], 'close': prices, 'volume': [1000]*100})
    
    strats, cerebro = run_strategy_test(MACrossStrategy, df, fast_period=5, slow_period=20)
    assert cerebro.broker.getvalue() < 1000000.0

def test_rsi_signal():
    """驗證 RSI 策略的超賣買入訊號"""
    # 建立數據：股價一路跌到底，讓 RSI 低於 30
    dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(100)]
    # RSI 需要變動價格來計算，我們構造一個快速下跌的過程
    prices = [100.0 - i for i in range(60)] + [40.0] * 40
    
    df = pd.DataFrame({'datetime': dates, 'open': prices, 'high': [p+1 for p in prices], 'low': [p-1 for p in prices], 'close': prices, 'volume': [1000]*100})
    
    strats, cerebro = run_strategy_test(RSIStrategy, df, rsi_period=14, oversold=30)
    
    # 只要有觸發 RSI < 30 的買入
    assert cerebro.broker.getvalue() < 1000000.0
