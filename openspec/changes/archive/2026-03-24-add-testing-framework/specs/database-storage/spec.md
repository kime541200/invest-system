## ADDED Requirements

### Requirement: Configurable DB Connection
系統 SHALL 支援從 `get_conn` 函式傳入自定義資料庫路徑。

#### Scenario: Use custom path for connection
- **WHEN** 呼叫 `get_conn(db_path=":memory:")`
- **THEN** 系統應連線至記憶體資料庫而非預設的 `trades.db`

### Requirement: Automated DB Schema Init
系統 SHALL 支援在建立新資料庫連線時（包括測試資料庫），自動執行 `init_db` 確保所有 Table 存在。

#### Scenario: Verify Table creation in new DB
- **WHEN** 在空的記憶體資料庫上呼叫初始化指令
- **THEN** `market_data`, `backtest_results`, `trades` 等 Table 應成功建立
