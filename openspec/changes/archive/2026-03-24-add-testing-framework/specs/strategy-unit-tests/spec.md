## ADDED Requirements

### Requirement: Strategy Signal Validation
系統 SHALL 支援針對個別交易策略進行單元測試，驗證其買賣訊號（Buy/Sell signals）的觸發邏輯。

#### Scenario: Golden Cross Signal
- **WHEN** 傳入一組「短均線剛超過長均線」的合成數據給 `MA_Cross` 策略
- **THEN** 系統應在該時間點正確觸發 `buy` 訊號

### Requirement: Synthetic Data Feeding
系統 SHALL 支援將 `pandas.DataFrame` 數據餵給回測引擎中的策略。

#### Scenario: Verify Strategy logic with DataFrame
- **WHEN** 測試腳本餵入特定構造的行情數據
- **THEN** 策略內部的指標計算（如 MA, RSI）應與預期值相符
