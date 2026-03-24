## ADDED Requirements

### Requirement: In-memory Database Support
系統 SHALL 支援在測試時使用 SQLite 的 `:memory:` 模式，確保測試結果不影響正式環境的 `trades.db`。

#### Scenario: Verify CRUD with in-memory DB
- **WHEN** 測試執行 `save_trade` 與 `load_trades` 指令
- **THEN** 所有操作應在記憶體中完成，且在連線關閉後自動清除數據

### Requirement: DB Integrity Checks
系統 SHALL 驗證資料庫的 `UNIQUE` 約束與各欄位格式（如日期格式是否正確）。

#### Scenario: Prevent duplicate entries
- **WHEN** 嘗試在同一日期儲存兩筆重複的市場數據
- **THEN** 系統應拋出異常或正確處理重複寫入
