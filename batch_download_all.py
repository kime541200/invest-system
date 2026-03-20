"""
全資料批次下載腳本
背景執行：nohup .venv/bin/python batch_download_all.py &
"""
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from data.fetcher import (
    batch_download_taifex, batch_download_twse_stock,
    batch_download_yfinance, save_to_db, fetch_twse_stock
)

LOG_FILE = Path(__file__).parent / 'download_progress.log'

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    line = f'[{ts}] {msg}'
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

# ============================================
# 1. 期貨全商品（1998~今）— 約 30 分鐘
# ============================================
FUTURES_PRODUCTS = [
    'TX',    # 台指期
    'MTX',   # 小台
    'TE',    # 電子期
    'TF',    # 金融期
    'XIF',   # 非金電期
    'T5F',   # 台灣50期
    'MSF',   # 小型股期
    'GTF',   # 櫃買期
    'G2F',   # 富櫃200期
    'TXO',   # 台指選（日行情）
]

# ============================================
# 2. 台股精選（台灣50 + 熱門股）
# ============================================
TWSE_STOCKS = [
    # 台灣50成分股（主要）
    '2330', '2317', '2454', '2308', '2382',  # 台積電、鴻海、聯發科、台達電、廣達
    '2891', '2881', '2882', '2886', '2884',  # 中信金、富邦金、國泰金、兆豐金、玉山金
    '2412', '3711', '2303', '1301', '1303',  # 中華電、日月光、聯電、台塑、南亞
    '2002', '1326', '2105', '5880', '2892',  # 中鋼、台化、正新、合庫金、第一金
    '3034', '2357', '3231', '6505', '2301',  # 聯詠、華碩、緯創、台塑化、光寶科
    '4904', '2912', '1101', '1102', '5871',  # 遠傳、統一超、台泥、亞泥、中租-KY
    '2207', '3045', '2395', '3008', '2379',  # 和泰車、台灣大、研華、大立光、瑞昱
    '2880', '4938', '6669', '3037', '2603',  # 華南金、和碩、緯穎、欣興、長榮
    '2609', '5876', '2615', '1216', '9910',  # 陽明、上海商銀、萬海、統一、豐泰
    '2345', '6415', '2327', '3661', '2049',  # 智邦、矽力-KY、國巨、世芯-KY、上銀
]

# ============================================
# 3. 國際市場 (yfinance)
# ============================================
YFINANCE_SYMBOLS = [
    # 貴金屬
    ('GC=F', 'max'),     # 黃金期貨
    ('MGC=F', '5y'),     # 微型黃金
    ('SI=F', 'max'),     # 白銀期貨
    # 指數
    ('^TWII', 'max'),    # 台灣加權指數
    ('^GSPC', 'max'),    # S&P 500
    ('^IXIC', 'max'),    # Nasdaq
    # 加密貨幣
    ('BTC-USD', 'max'),  # 比特幣
    ('ETH-USD', 'max'),  # 以太幣
    # 能源
    ('CL=F', 'max'),     # 原油
    # 匯率
    ('USDTWD=X', 'max'), # 美元/台幣
]


def download_all():
    start = datetime.now()
    log('='*50)
    log('全資料批次下載開始')
    log('='*50)

    # --- Phase 1: 國際市場（最快，1~2 分鐘）---
    log('\n📦 Phase 1/3: 國際市場 (yfinance)')
    for symbol, period in YFINANCE_SYMBOLS:
        try:
            batch_download_yfinance(symbol, period)
        except Exception as e:
            log(f'  ❌ {symbol} 失敗: {e}')
        time.sleep(1)

    # --- Phase 2: 期貨（約 30 分鐘）---
    log('\n📦 Phase 2/3: 台灣期貨 (TAIFEX)')
    for product in FUTURES_PRODUCTS:
        try:
            batch_download_taifex(product, '1998/07/01')
        except Exception as e:
            log(f'  ❌ {product} 失敗: {e}')

    # --- Phase 3: 台股（約 2~3 小時）---
    log('\n📦 Phase 3/3: 台股精選 (TWSE)')
    total = len(TWSE_STOCKS)
    for i, symbol in enumerate(TWSE_STOCKS, 1):
        log(f'  [{i}/{total}] {symbol}')
        try:
            batch_download_twse_stock(symbol, '1998-01-01')
        except Exception as e:
            log(f'  ❌ {symbol} 失敗: {e}')

    elapsed = (datetime.now() - start).total_seconds()
    log(f'\n{"="*50}')
    log(f'全部完成！耗時: {elapsed/60:.1f} 分鐘')
    log(f'{"="*50}')


if __name__ == '__main__':
    download_all()
