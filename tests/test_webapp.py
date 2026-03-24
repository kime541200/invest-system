import pytest
import json
import os
from invest_system.webapp import app, get_conn
from invest_system.db.store import init_db_with_conn, save_trade, get_trades

@pytest.fixture
def test_db_path(tmp_path):
    """建立一個臨時資料庫檔案路徑"""
    db_file = tmp_path / "test_trades.db"
    return str(db_file)

def test_index(test_db_path):
    """驗證首頁是否能正常載入"""
    conn = get_conn(test_db_path)
    init_db_with_conn(conn)
    conn.close()
    
    with app.test_request_context():
        from invest_system.webapp import index
        response = index(db_path=test_db_path)
        assert "儀表板" in response

def test_api_trades(test_db_path):
    """驗證 API 端點"""
    conn = get_conn(test_db_path)
    init_db_with_conn(conn)
    
    # 插入測試資料
    save_trade("test", "2330", "BUY", 600, 100, 60000, conn=conn)
    conn.commit() # 確保寫入
    
    # 驗證資料庫確實有東西
    local_trades = get_trades(conn=conn)
    print(f"DEBUG: Local trades: {local_trades}")
    assert len(local_trades) == 1
    
    conn.close()
    
    with app.test_request_context():
        from invest_system.webapp import api_trades
        resp = api_trades(db_path=test_db_path)
        data = resp.get_json()
        print(f"DEBUG: API trades: {data}")
        assert len(data) == 1
        assert data[0]["symbol"] == "2330"
