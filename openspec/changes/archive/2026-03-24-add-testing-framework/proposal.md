## Why

目前專案缺乏自動化測試機制，所有功能驗證均依賴手動執行指令。隨著系統功能增加（策略、AI 分析、資料抓取），手動驗證變得低效且容易遺漏邊界錯誤。建立自動化測試框架能確保核心邏輯的正確性，並在未來重構或新增功能時提供安全網。

## What Changes

- **基礎設施**: 引入 `pytest` 作為核心測試框架，並配置 `pytest-mock` 與 `responses` 用於模擬外部依賴。
- **架構重構**: 
    - 修改 `src/invest_system/db/store.py`，使資料庫連線可配置（支援 In-memory DB）。
    - 調整 `src/invest_system/data/fetcher.py`，分離「網路抓取」與「資料解析」邏輯，以利單元測試。
- **測試涵蓋**: 
    - 實作資料庫 CRUD 基礎測試。
    - 實作核心交易策略（如 `ma_cross`）的邏輯驗證測試。
    - 實作交易所資料解析的單元測試。

## Capabilities

### New Capabilities
- `testing-infrastructure`: 提供整體的測試執行環境與輔助工具配置。
- `db-unit-tests`: 針對資料庫存取層的單元與集成測試。
- `strategy-unit-tests`: 針對交易策略邏輯的訊號觸發測試。
- `data-parsing-tests`: 針對交易所 API 回傳格式的解析邏輯測試。

### Modified Capabilities
- `database-storage`: 修改資料庫初始化與連線獲取流程，以支援測試模式。

## Impact

- **依賴項**: 新增 `pytest`, `pytest-mock`, `responses` 開發依賴。
- **程式碼結構**: `src/invest_system/db/store.py` 與 `src/invest_system/data/fetcher.py` 會進行微幅重構。
- **開發流程**: 新增 `tests/` 目錄，開發者需在提交程式碼前執行 `pytest`。
