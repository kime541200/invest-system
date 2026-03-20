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
# 建立虛擬環境
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 下載資料
.venv/bin/python data/fetcher.py --taifex TX MTX
.venv/bin/python data/fetcher.py --twse 2330 2317
.venv/bin/python data/fetcher.py --yf GC=F BTC-USD

# 回測
.venv/bin/python backtest.py ma_cross --symbol GC=F --source yfinance --period 2y
.venv/bin/python backtest.py rsi --symbol 2330.TW --source yfinance

# 市場情報
.venv/bin/python intelligence.py              # 單次收集+分析
.venv/bin/python intelligence.py --daemon     # 每分鐘自動收集
.venv/bin/python intelligence.py --mood       # 查看市場情緒

# Web 儀表板
.venv/bin/python webapp.py                    # http://localhost:18900
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

```
invest-system/
├── config.py              # 設定
├── backtest.py            # 回測引擎 CLI
├── intelligence.py        # 市場情報收集 + AI 分析
├── webapp.py              # Flask Web App
├── trading.html           # 策略監控看盤介面
├── tg_monitor.py          # Telegram 群組監聽
├── batch_download_all.py  # 全資料批次下載
├── data/
│   └── fetcher.py         # 資料下載器（TWSE/TPEx/TAIFEX/yfinance）
├── db/
│   └── store.py           # SQLite 儲存層
├── strategies/
│   ├── base.py            # 策略基類
│   ├── ma_cross.py        # 均線交叉
│   ├── rsi.py             # RSI
│   ├── bollinger.py       # 布林通道
│   ├── macd.py            # MACD
│   └── breakout.py        # 突破策略
└── utils/
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

- Python 3.10+
- 依賴：backtrader, yfinance, pandas, numpy, flask, requests, telethon

## License

MIT

---

Built with Symbiosis AI System
