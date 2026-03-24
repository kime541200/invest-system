import pytest
from invest_system.data.fetcher import parse_twse_stock_row

def test_parse_twse_stock_row():
    """驗證證交所日行情列解析邏輯"""
    symbol = "2330"
    # 原始資料格式: 日期, 成交股數, 成交金額, 開盤價, 最高價, 最低價, 收盤價, 漲跌價差, 成交筆數
    row = ["113/03/22", "30,000,000", "21,000,000,000", "750.00", "760.00", "740.00", "755.00", "+5.0", "15,000"]
    
    result = parse_twse_stock_row(symbol, row)
    
    assert result is not None
    assert result["symbol"] == "2330"
    assert result["date"] == "2024-03-22"  # 113 + 1911 = 2024
    assert result["open"] == 750.0
    assert result["high"] == 760.0
    assert result["low"] == 740.0
    assert result["close"] == 755.0
    assert result["volume"] == 30000000

def test_parse_twse_stock_row_invalid():
    """驗證異常資料處理"""
    symbol = "2330"
    row = ["113/03/22", "invalid", "---", "--", "--", "--", "--", "0", "0"]
    result = parse_twse_stock_row(symbol, row)
    assert result is None
