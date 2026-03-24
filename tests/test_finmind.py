import pytest
import responses
import json
import re
from invest_system.data.finmind import fetch_institutional, init_finmind_db, API_URL, get_conn

@responses.activate
def test_fetch_institutional(db_conn):
    """驗證 FinMind 法人買賣超抓取與解析"""
    symbol = "2330"
    init_finmind_db(conn=db_conn)
    
    # 模擬 API 回傳
    mock_data = {
        "status": 200,
        "msg": "success",
        "data": [
            {"date": "2024-03-22", "buy": 1000, "sell": 500, "name": "外資及陸資(不含外資自營商)"},
            {"date": "2024-03-22", "buy": 2000, "sell": 1000, "name": "投信"},
            {"date": "2024-03-22", "buy": 3000, "sell": 1500, "name": "自營商(自行買賣)"}
        ]
    }
    
    # 使用正則表達式匹配帶有參數的 URL
    responses.add(
        responses.GET,
        re.compile(f"{API_URL}.*"),
        json=mock_data,
        status=200
    )
    
    count = fetch_institutional(symbol, "2024-03-22", "2024-03-22", conn=db_conn)
    
    assert count == 1  # 只有一天
    
    row = db_conn.execute("SELECT * FROM tw_institutional WHERE symbol='2330'").fetchone()
    assert row["foreign_net"] == 500
    assert row["trust_net"] == 1000
    assert row["dealer_net"] == 1500
    assert row["total_net"] == 3000
