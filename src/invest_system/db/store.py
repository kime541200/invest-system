"""SQLite 交易紀錄儲存"""
import sqlite3
from datetime import datetime
from ..config import DB_PATH


def get_conn(db_path=None):
    path = db_path if db_path else DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db_with_conn(conn):
    """使用傳入的連線建立資料表"""
    conn.row_factory = sqlite3.Row
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy TEXT NOT NULL,
            symbol TEXT NOT NULL,
            action TEXT NOT NULL,          -- BUY / SELL
            price REAL NOT NULL,
            size INTEGER NOT NULL,
            value REAL NOT NULL,
            pnl REAL DEFAULT 0,
            ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS backtest_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy TEXT NOT NULL,
            symbol TEXT NOT NULL,
            start_date TEXT,
            end_date TEXT,
            initial_cash REAL,
            final_value REAL,
            total_return REAL,
            max_drawdown REAL,
            sharpe_ratio REAL,
            win_rate REAL,
            total_trades INTEGER,
            ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL, high REAL, low REAL, close REAL,
            volume INTEGER,
            source TEXT DEFAULT 'yfinance',
            UNIQUE(symbol, date)
        );

        CREATE TABLE IF NOT EXISTS tg_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT,
            sender_name TEXT,
            message_text TEXT,
            ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS tw_institutional (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            symbol TEXT NOT NULL,
            foreign_buy INTEGER DEFAULT 0,
            foreign_sell INTEGER DEFAULT 0,
            foreign_net INTEGER DEFAULT 0,
            trust_buy INTEGER DEFAULT 0,
            trust_sell INTEGER DEFAULT 0,
            trust_net INTEGER DEFAULT 0,
            dealer_buy INTEGER DEFAULT 0,
            dealer_sell INTEGER DEFAULT 0,
            dealer_net INTEGER DEFAULT 0,
            total_net INTEGER DEFAULT 0,
            UNIQUE(date, symbol)
        );

        CREATE TABLE IF NOT EXISTS news_intelligence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT UNIQUE,
            summary TEXT,
            source TEXT,
            sentiment TEXT,
            score INTEGER,
            keywords TEXT,
            reason TEXT,
            published_at TEXT,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()


def init_db():
    """建立預設資料庫的資料表"""
    conn = get_conn()
    init_db_with_conn(conn)
    conn.close()


def save_trade(strategy, symbol, action, price, size, value, pnl=0, db_path=None, conn=None):
    _conn = conn if conn else get_conn(db_path)
    _conn.execute(
        "INSERT INTO trades (strategy, symbol, action, price, size, value, pnl) VALUES (?,?,?,?,?,?,?)",
        (strategy, symbol, action, price, size, value, pnl)
    )
    if not conn:
        _conn.commit()
        _conn.close()


def save_backtest(strategy, symbol, start_date, end_date, initial_cash,
                  final_value, total_return, max_drawdown, sharpe_ratio,
                  win_rate, total_trades, db_path=None, conn=None):
    _conn = conn if conn else get_conn(db_path)
    _conn.execute(
        """INSERT INTO backtest_results
           (strategy, symbol, start_date, end_date, initial_cash, final_value,
            total_return, max_drawdown, sharpe_ratio, win_rate, total_trades)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (strategy, symbol, start_date, end_date, initial_cash, final_value,
         total_return, max_drawdown, sharpe_ratio, win_rate, total_trades)
    )
    if not conn:
        _conn.commit()
        _conn.close()


def save_market_data(symbol, date, o, h, l, c, vol, source='yfinance', db_path=None, conn=None):
    _conn = conn if conn else get_conn(db_path)
    _conn.execute(
        """INSERT OR IGNORE INTO market_data
           (symbol, date, open, high, low, close, volume, source)
           VALUES (?,?,?,?,?,?,?,?)""",
        (symbol, date, o, h, l, c, vol, source)
    )
    if not conn:
        _conn.commit()
        _conn.close()


def get_trades(strategy=None, limit=50, db_path=None, conn=None):
    _conn = conn if conn else get_conn(db_path)
    if strategy:
        rows = _conn.execute(
            "SELECT * FROM trades WHERE strategy=? ORDER BY ts DESC LIMIT ?",
            (strategy, limit)
        ).fetchall()
    else:
        rows = _conn.execute(
            "SELECT * FROM trades ORDER BY ts DESC LIMIT ?", (limit,)
        ).fetchall()
    if not conn:
        _conn.close()
    return [dict(r) for r in rows]


def get_backtest_results(limit=20, db_path=None, conn=None):
    _conn = conn if conn else get_conn(db_path)
    rows = _conn.execute(
        "SELECT * FROM backtest_results ORDER BY ts DESC LIMIT ?", (limit,)
    ).fetchall()
    if not conn:
        _conn.close()
    return [dict(r) for r in rows]


# 初始化
init_db()
