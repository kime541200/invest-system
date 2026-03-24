## 1. 測試環境準備 (Setup)

- [x] 1.1 安裝 `pytest`, `pytest-mock`, `responses` 開發依賴 (`uv add --dev pytest pytest-mock responses`)
- [x] 1.2 建立 `tests/` 目錄結構
- [x] 1.3 建立 `tests/conftest.py` 定義全域 fixtures (如 `db_conn`, `mock_env`)

## 2. 資料庫層重構與測試 (DB Layer)

- [x] 2.1 修改 `src/invest_system/db/store.py` 中的 `get_conn` 支援 `db_path` 參數
- [x] 2.2 實作 `tests/test_db.py`：驗證 In-memory DB 初始化
- [x] 2.3 實作 `tests/test_db.py`：驗證 `save_trade` 與 `load_trades` 功能
- [x] 2.4 實作 `tests/test_db.py`：驗證 `UNIQUE` 約束（重複日期寫入）

## 3. 資料解析邏輯測試 (Data Parsing)

- [x] 3.1 實作 `tests/test_fetcher.py`：驗證民國年轉西元年解析
- [x] 3.2 實作 `tests/test_fetcher.py`：驗證金額千分位與字串轉浮點數解析
- [x] 3.3 實作 `tests/test_finmind.py`：使用 `responses` 模擬 FinMind API 回傳並驗證 DataFrame 轉換

## 4. 交易策略單元測試 (Strategy)

- [x] 4.1 實作 `tests/test_strategies.py`：建立 `Golden Cross` 合成數據 feed
- [x] 4.2 實作 `tests/test_strategies.py`：驗證 `MA_Cross` 策略的買入訊號觸發
- [x] 4.3 實作 `tests/test_strategies.py`：驗證 `RSI` 策略的超買/超賣訊號

## 5. WebApp 基礎連通測試 (WebApp)

- [x] 5.1 實作 `tests/test_webapp.py`：使用 Flask Test Client 驗證首頁 (`/`) 回傳 200
- [x] 5.2 實作 `tests/test_webapp.py`：驗證 API 端點（如 `/api/trades`）回傳正確的 JSON 結構
