## ADDED Requirements

### Requirement: Pytest Configuration
系統 SHALL 包含 `pytest` 設定檔案（如 `pyproject.toml` 或 `conftest.py`），定義測試搜尋路徑與共用 fixture。

#### Scenario: Run all tests
- **WHEN** 執行 `pytest` 指令
- **THEN** 系統應能自動偵測並執行 `tests/` 目錄下的所有測試文件

### Requirement: Mocking Infrastructure
系統 SHALL 提供模擬外部 API（如 TWSE/TPEx）與網路請求的工具。

#### Scenario: Mock network response
- **WHEN** 測試中使用 `responses` 模擬特定 URL
- **THEN** 系統發出的請求應被攔截並回傳預設數據
