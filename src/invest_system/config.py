"""投資系統設定"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 路徑
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
DB_PATH = BASE_DIR / 'db' / 'trades.db'
ROOT_DIR = BASE_DIR.parent.parent

# 確保資料夾存在
DATA_DIR.mkdir(exist_ok=True)
DB_PATH.parent.mkdir(exist_ok=True)

# 載入環境變數
def load_env():
    """載入專案與共用環境變數"""
    # 1. 優先載入專案內的 .env (位於專案根目錄)
    load_dotenv(ROOT_DIR / '.env')
    
    # 2. 備選方案：載入 ai-hub 共用 .env (若未在專案中設定)
    shared_env = Path.home() / '.config' / 'ai-hub' / 'shared' / '.env'
    if shared_env.exists():
        for line in shared_env.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, value = line.partition('=')
                k = key.strip()
                if k not in os.environ:
                    os.environ[k] = value.strip()

# 初始化載入
load_env()

# 預設設定
DEFAULT_CASH = int(os.environ.get('DEFAULT_CASH', 1000000))       # 回測初始資金（台幣）
DEFAULT_COMMISSION = float(os.environ.get('DEFAULT_COMMISSION', 0.001425))  # 手續費率
DEFAULT_TAX = float(os.environ.get('DEFAULT_TAX', 0.003))            # 交易稅率

