## Context

目前專案代碼與 IO 操作（資料庫路徑、網路請求）高度耦合。`src/invest_system/db/store.py` 直接使用全域變數 `DB_PATH` 指向本地 SQLite 檔案。為了進行測試，我們需要一種方式在不修改程式碼邏輯的前提下，動態注入「測試用資料庫」或「模擬網路回傳」。

## Goals / Non-Goals

**Goals:**
- 提供統一的測試進入點。
- 實現資料庫測試的隔離性（使用 In-memory DB）。
- 建立範例測試，涵蓋策略與資料解析。
- 自動化安裝必要的測試工具。

**Non-Goals:**
- 達成 100% 的測試覆蓋率（此階段僅先建立基礎與核心邏輯測試）。
- 重構整個 Web UI 邏輯。
- 整合大型 CI/CD 流程（僅限於本地測試）。

## Decisions

### 1. 測試框架選用 Pytest
- **決策**: 使用 `pytest` 作為核心框架，搭配 `pytest-mock` (mocker) 與 `responses`。
- **理由**: `pytest` 的 fixture 機制非常適合處理資料庫連線的 setup/teardown。`responses` 比直接用 `mock` 攔截 `requests` 更好維護且語法更簡潔。

### 2. 資料庫連線重構 (Dependency Injection)
- **決策**: 修正 `store.py` 中的 `get_conn` 函式，新增一個選擇性參數 `db_path=None`。
- **理由**: 當傳入參數時，函式使用指定的路徑；否則預設使用正式資料庫路徑。這允許測試 fixture 在 setup 時輕鬆開啟 `:memory:` 連線。

### 3. 測試資料夾結構
- **決策**: 在根目錄建立 `tests/` 資料夾，並包含 `conftest.py`。
- **理由**: 符合 Python 社群標準，方便 `pytest` 自動偵測測試案例，且 `conftest.py` 可集中管理共用的 fixtures（如 `db_conn`, `mock_fetcher`）。

### 4. 模擬策略回測數據
- **決策**: 在 `tests/strategies/` 中，建立一組合成的 CSV 或 DataFrame 數據餵給 Backtrader。
- **理由**: 不需要真實歷史數據即可驗證 `BaseStrategy` 的繼承子類是否能正確偵測到「黃金交叉」等訊號。

## Risks / Trade-offs

- **[Risk]** 重構 `store.py` 可能影響現有功能的穩定性。 → **Mitigation**: 保持參數預設值不變，並在重構後立即跑一次現有的手動執行腳本確保運作正常。
- **[Risk]** Backtrader 的回測引擎測試較為複雜。 → **Mitigation**: 初期僅針對策略類別的訊號邏輯進行單元測試，而非測試整個回測引擎。
