# AGENTS.md

## Project Overview

這是一個基於 Python 建立的綜合量化投資系統，專為資料收集、策略回測、市場情報分析與即時監控所設計。主要鎖定台灣股市 (TWSE/TPEx)、期貨 (TAIFEX) 以及國際市場 (透過 `yfinance`)。

## Setup

```bash
# 安裝依賴與 Python (使用 uv)
uv sync
```

**Prerequisites (先決條件)**: Python 3.11+, uv (管理依賴與 Python 版本)。
**Environment Variables (環境變數)**: 請將必要的 API 金鑰 (如 GROQ, GEMINI 等) 填寫於專案根目錄的 `.env` 檔案中 (可參考 `.env.example`)。系統亦會自動嘗試讀取 `~/.config/ai-hub/shared/.env` 作為全域備選。在執行 AI 或監控模組前，請確認這些變數已經設定。

## Development

```bash
# 1. 啟動 Web 儀表板 (本機存取網址: http://localhost:18900)
uv run python webapp.py

# 2. 資料收集
uv run python data/fetcher.py --twse 2330         # 下載台股資料
uv run python data/fetcher.py --yf GC=F BTC-USD   # 透過 yfinance 下載國際市場資料

# 3. 市場情報分析
uv run python intelligence.py                     # 單次收集與分析
uv run python intelligence.py --daemon            # 以守護行程 (daemon) 模式執行 (每分鐘更新)

# 4. Telegram 群組監聽
uv run python tg_monitor.py --login               # 首次互動式登入
uv run python tg_monitor.py --listen all          # 開始監聽所有財經群組
```

## Testing

```bash
# 執行策略回測 (可用策略有: ma_cross, rsi, bollinger, macd, breakout)
uv run python backtest.py ma_cross --symbol 2330.TW --source yfinance --period 2y
```

*(注意: 因目前尚未配置正式的 pytest 套件，請使用 `backtest.py` 來驗證策略)*

## Code Style

- **Python 版本**: 3.11+。
- **Strategies (策略)**: 所有策略都必須繼承 `strategies/base.py` 中的 `BaseStrategy`。請實作 `next()` 方法來撰寫核心邏輯，並在 `params` 唯讀組 (tuple) 中定義參數。
- **Registration (註冊)**: 在建立新的策略檔案後 (例如 `strategies/my_strategy.py`)，必須在 `strategies/__init__.py` 註冊該策略，將它加入 `STRATEGIES` 字典中。
- **Configuration (設定)**: 使用 `config.py` 來設定目錄路徑與預設交易參數 (手續費、稅金、可動用資金)。

## Project Structure

```text
data/           # 資料抓取引擎 (TWSE, TPEx, TAIFEX, yfinance)
db/             # 資料庫 Schema 初始化 (store.py) 與本地 SQLite 資料庫 (trades.db)
strategies/     # 可插拔的回測策略與 __init__.py 的註冊表
utils/          # 實用腳本與批次處理輔助工具
```

**資料流框架 (Data Flow Framework)**: 

1. 透過 `data/fetcher.py` 抓取下來的資料會存放到 `market_data` 資料表中。
2. `backtest.py` 可讀取本地資料庫 (`--source db`) 或即時代碼 (`--source yfinance`)，並將結果存到 `backtest_results` 資料表中。
3. `webapp.py` 作為資料庫內容的唯讀檢視器，負責提供 REST API 並且回傳 HTML 模板。

## Security Notes

- **Secrets (機密資訊)**: 嚴禁將 API 金鑰直接寫死在程式碼中！請將設定寫入專案的 `.env`，或統一存放於全域的 `~/.config/ai-hub/shared/.env` 備選檔案。
- **Database (資料庫)**: 系統使用單一的 SQLite 資料庫 `db/trades.db`。請避免在系統外的邏輯進行多次併發寫入。
