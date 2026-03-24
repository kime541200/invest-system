import pytest
import sqlite3
import os
from invest_system.db.store import init_db

@pytest.fixture
def db_conn():
    """建立一個記憶體資料庫連線供測試使用"""
    # 注意：之後我們需要重構 get_conn 來支援這個連線
    # 目前先手動建立一個並初始化 schema
    conn = sqlite3.connect(":memory:")
    # 這裡我們直接呼叫 init_db 的邏輯，或者之後重構 store.py 後直接調用
    # 目前先確保 schema 建立
    from invest_system.db.store import init_db_with_conn
    init_db_with_conn(conn)
    yield conn
    conn.close()

@pytest.fixture
def mock_env(monkeypatch):
    """模擬環境變數"""
    monkeypatch.setenv("GROQ_API_KEY", "test_key")
    monkeypatch.setenv("GEMINI_API_KEY", "test_key")
