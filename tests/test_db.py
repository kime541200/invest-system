import pytest
import sqlite3
from invest_system.db.store import (
    save_trade, get_trades, save_market_data, get_conn
)

def test_db_init(db_conn):
    """驗證資料表是否成功建立"""
    cursor = db_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    assert "trades" in tables
    assert "market_data" in tables
    assert "backtest_results" in tables

def test_save_trade(db_conn):
    """驗證 save_trade 與 get_trades 功能"""
    save_trade("test_strat", "2330.TW", "BUY", 600.0, 1000, 600000.0, conn=db_conn)
    trades = get_trades(conn=db_conn)
    
    assert len(trades) == 1
    assert trades[0]["symbol"] == "2330.TW"
    assert trades[0]["action"] == "BUY"

def test_save_market_data_unique(db_conn):
    """驗證 UNIQUE 約束是否能防止重複日期寫入"""
    # 插入第一筆
    save_market_data("2330.TW", "2024-03-24", 600, 610, 595, 605, 10000, conn=db_conn)
    # 插入重複日期（應被忽略）
    save_market_data("2330.TW", "2024-03-24", 999, 999, 999, 999, 999, conn=db_conn)

    row = db_conn.execute("SELECT * FROM market_data WHERE symbol='2330.TW'").fetchone()
    assert row["close"] == 605  # 應該還是原始數據
