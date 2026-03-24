## ADDED Requirements

### Requirement: TWSE/TPEx Data Normalization
系統 SHALL 驗證交易所原始行情資料解析的正確性（如金額千分位、民國年轉西元年）。

#### Scenario: Normalize TWSE daily report row
- **WHEN** 餵入一筆包含「113/03/24」與「1,234.56」金額的行情字串
- **THEN** 系統解析後應回傳 `2024-03-24` 與浮點數 `1234.56`

### Requirement: FinMind API Parsing
系統 SHALL 驗證從 FinMind API 獲取的數據格式是否正確轉換為系統內部的 `DataFrame`。

#### Scenario: Successful FinMind data parsing
- **WHEN** 餵入一組 JSON 格式的模擬 FinMind API 回應
- **THEN** 系統應正確轉換為包含 `date`, `open`, `high`, `low`, `close` 等欄位的 DataFrame
