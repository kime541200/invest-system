# Invest System 投資策略系統

> 開源量化投資工具集 — 資料收集、策略回測、市場情報、即時監控

## 功能

### 資料收集

- **台股** — 證交所 (TWSE) 上市個股歷史行情
- **上櫃/興櫃** — 櫃買中心 (TPEx) 歷史行情
- **台灣期貨** — 期交所 (TAIFEX) 全商品日行情（1998年起）
- **國際市場** — yfinance 整合（黃金、原油、加密貨幣、美股指數等）
- **批次下載** — 一鍵下載 28 年歷史資料

### 策略引擎

- **可插拔策略框架** — 繼承 BaseStrategy 即可新增策略
- **內建 5 個策略**：均線交叉、RSI、布林通道、MACD、突破策略
- **Backtrader 回測** — 完整績效報告（報酬率、Sharpe、最大回撤、勝率）
- **SQLite 儲存** — 所有交易紀錄和回測結果永久保存

### 市場情報

- **RSS 新聞收集** — Google News、自由時報等即時財經新聞
- **AI 情感分析** — Groq API 秒級分析（利多/利空/中性）
- **市場情緒指標** — 即時計算 bullish/bearish 比例
- **每分鐘更新** — Daemon 模式自動收集分析

### Web 儀表板

- **策略監控** — 回測結果比較、買賣點標記
- **K 線圖** — Canvas 繪製，支援縮放拖曳
- **手機友善** — 深色主題 RWD 介面
- **API 端點** — JSON API 供前端或 PWA 使用

## 快速開始

```bash
# 建立環境並安裝依賴 (使用 uv)
uv sync

# 設定環境變數
cp .env.example .env
# 編輯 .env 並填入你的 GROQ_API_KEY
```

### 環境變數說明

本專案使用 `python-dotenv` 自動載入根目錄下的 `.env` 檔案。主要支援以下變數：

- `GROQ_API_KEY`: (必填) 用於市場情報的 AI 情感分析。
- `GEMINI_API_KEY`: (選填) 備用的 AI 分析來源。
- `TELEGRAM_API_ID` / `HASH`: (選填) 用於 `tg_monitor.py` 監控群組。
- `DEFAULT_CASH`: (選填) 回測初始資金，預設為 `1000000`。
- `DEFAULT_COMMISSION`: (選填) 手續費率，預設為 `0.001425` (0.1425%)。
- `DEFAULT_TAX`: (選填) 交易稅率，預設為 `0.003` (0.3%)。

> 💡 **提示**：系統也會自動嘗試讀取 `~/.config/ai-hub/shared/.env` 作為全域備選設定。

### 常用指令

```bash
# 下載資料 (使用 uv run)
uv run python data/fetcher.py --twse 2330 2317
uv run python data/fetcher.py --yf GC=F BTC-USD

# 回測
uv run python backtest.py ma_cross --symbol GC=F --source yfinance --period 2y
uv run python backtest.py rsi --symbol 2330.TW --source yfinance

# 市場情報
uv run python intelligence.py              # 單次收集+分析
uv run python intelligence.py --daemon     # 每分鐘自動收集
uv run python intelligence.py --mood       # 查看市場情緒

# Web 儀表板
uv run python webapp.py                    # http://localhost:18900

# Telegram 監聽
uv run python tg_monitor.py --login        # 首次登入驗證
uv run python tg_monitor.py --groups       # 查看已加入群組
uv run python tg_monitor.py --listen all   # 監聽所有群組
```

## 策略回測範例

黃金期貨 (GC=F) 2 年回測：

| 策略 | 報酬率 | 最大回撤 | Sharpe | 勝率 |
|------|--------|---------|--------|------|
| MA交叉 | +37.89% | 12.06% | 0.94 | 56% |
| 突破 | +21.28% | 11.96% | 0.61 | 46% |
| MACD | +16.54% | 11.84% | 0.53 | 62% |
| 布林通道 | +4.75% | 4.18% | 0.30 | 100% |

## 技術架構

本專案採用標準的 **src-layout** 佈局，核心代碼位於 `src/invest_system/` 目錄下：

```
invest-system/
├── pyproject.toml       # 專案配置與依賴管理
├── README.md            # 專案說明
├── src/
│   └── invest_system/   # 主程式套件
│       ├── config.py    # 路徑與參數設定
│       ├── backtest.py  # 回測引擎 CLI
│       ├── webapp.py    # Flask Web App
│       ├── data/        # 資料下載器 (TWSE/TPEx/TAIFEX/yfinance)
│       ├── db/          # SQLite 儲存層 (store.py)
│       ├── strategies/  # 可插拔的交易策略
│       └── utils/       # 輔助工具
```

## 資料來源

| 來源 | 資料 | 費用 |
|------|------|------|
| TWSE | 台股上市個股 | 免費 |
| TPEx | 上櫃/興櫃 | 免費 |
| TAIFEX | 台灣期貨 | 免費 |
| yfinance | 國際市場 | 免費 |
| Google News RSS | 財經新聞 | 免費 |
| Groq API | AI 情感分析 | 免費 |

## 環境需求

- Python 3.11+ (由 `uv` 自動管理)
- 依賴：backtrader, yfinance, pandas, numpy, flask, requests, telethon (詳見 `pyproject.toml`)
- 管理工具：[uv](https://github.com/astral-sh/uv)

## 授權條款

本專案採用 [MIT License](LICENSE) 授權。
