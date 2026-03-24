"""
回測引擎 — 跑策略、產出績效報告
"""
import sys
import os
import sqlite3
import backtrader as bt
import pandas as pd
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

from .config import DB_PATH, DEFAULT_CASH, DEFAULT_COMMISSION, DEFAULT_TAX
from .strategies import STRATEGIES
from .db.store import save_backtest


@contextmanager
def suppress_stdout():
    """暫時隱藏所有 stdout 輸出"""
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout


def load_data_from_db(symbol, start_date=None, end_date=None):
    """從 SQLite 讀取行情資料轉成 Backtrader DataFeed"""
    conn = sqlite3.connect(DB_PATH)

    query = "SELECT date, open, high, low, close, volume FROM market_data WHERE symbol=?"
    params = [symbol]

    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)

    query += " ORDER BY date ASC"

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    if df.empty:
        print(f'⚠️  {symbol} 在資料庫中沒有資料')
        return None

    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df = df.astype(float)

    print(f'📊 載入 {symbol}: {len(df)} 筆 ({df.index[0].date()} ~ {df.index[-1].date()})')
    return bt.feeds.PandasData(dataname=df)


def load_data_from_yfinance(symbol, period='1y'):
    """直接從 yfinance 載入（不經 DB）"""
    import yfinance as yf
    df = yf.download(symbol, period=period, progress=False)
    if df.empty:
        print(f'⚠️  {symbol} yfinance 無資料')
        return None

    # 處理 MultiIndex columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    print(f'📊 載入 {symbol}: {len(df)} 筆 (yfinance {period})')
    return bt.feeds.PandasData(dataname=df)


class MaxDrawdownAnalyzer(bt.Analyzer):
    """最大回撤分析器"""
    def __init__(self):
        self.peak = 0
        self.max_dd = 0

    def next(self):
        value = self.strategy.broker.getvalue()
        if value > self.peak:
            self.peak = value
        dd = (self.peak - value) / self.peak if self.peak > 0 else 0
        if dd > self.max_dd:
            self.max_dd = dd

    def get_analysis(self):
        return {'max_drawdown': self.max_dd}


def run_backtest(strategy_name, symbol, source='db', period='1y',
                 start_date=None, end_date=None, cash=None,
                 params=None, silent=False):
    """
    執行回測
    strategy_name: 'ma_cross', 'rsi' 等（見 strategies/__init__.py）
    symbol: 標的代號
    source: 'db' 或 'yfinance'
    params: dict, 策略參數覆蓋
    """
    if strategy_name not in STRATEGIES:
        if not silent:
            print(f'❌ 未知策略: {strategy_name}')
            print(f'   可用策略: {", ".join(STRATEGIES.keys())}')
        return None

    strategy_cls = STRATEGIES[strategy_name]
    cash = cash or DEFAULT_CASH

    # 載入資料（silent 時隱藏輸出）
    if silent:
        with suppress_stdout():
            if source == 'db':
                data = load_data_from_db(symbol, start_date, end_date)
            else:
                data = load_data_from_yfinance(symbol, period)
    else:
        if source == 'db':
            data = load_data_from_db(symbol, start_date, end_date)
        else:
            data = load_data_from_yfinance(symbol, period)

    if data is None:
        return None

    # 建立回測引擎
    cerebro = bt.Cerebro()
    cerebro.adddata(data)

    # 加入策略
    strategy_params = params or {}
    cerebro.addstrategy(strategy_cls, **strategy_params)

    # 設定資金和手續費
    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(commission=DEFAULT_COMMISSION)

    # 分析器
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe',
                        timeframe=bt.TimeFrame.Days, annualize=True)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    cerebro.addanalyzer(MaxDrawdownAnalyzer, _name='maxdd')

    # 執行
    if not silent:
        print(f'\n🚀 回測開始: {strategy_name} on {symbol}')
        print(f'   初始資金: ${cash:,.0f}')
        print(f'   手續費率: {DEFAULT_COMMISSION*100:.4f}%')
        print('   ---')

    if silent:
        with suppress_stdout():
            results = cerebro.run()
    else:
        results = cerebro.run()

    strat = results[0]

    # 績效報告
    final_value = cerebro.broker.getvalue()
    total_return = (final_value - cash) / cash * 100

    sharpe = strat.analyzers.sharpe.get_analysis()
    sharpe_ratio = sharpe.get('sharperatio', 0) or 0

    maxdd = strat.analyzers.maxdd.get_analysis()
    max_drawdown = maxdd.get('max_drawdown', 0) * 100

    trade_analysis = strat.analyzers.trades.get_analysis()
    total_trades = trade_analysis.get('total', {}).get('closed', 0)

    win_rate = strat.win_rate * 100 if hasattr(strat, 'win_rate') else 0

    if not silent:
        print(f'\n📈 回測結果:')
        print(f'   最終資金: ${final_value:,.0f}')
        print(f'   總報酬率: {total_return:+.2f}%')
        print(f'   最大回撤: {max_drawdown:.2f}%')
        print(f'   Sharpe Ratio: {sharpe_ratio:.3f}')
        print(f'   總交易次數: {total_trades}')
        print(f'   勝率: {win_rate:.1f}%')

    # 存入 DB（silent 模式由 optimizer 自行處理，不重複存）
    if not silent:
        save_backtest(
            strategy=strategy_name,
            symbol=symbol,
            start_date=start_date or 'N/A',
            end_date=end_date or 'N/A',
            initial_cash=cash,
            final_value=final_value,
            total_return=total_return,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            win_rate=win_rate,
            total_trades=total_trades,
        )

    return {
        'strategy': strategy_name,
        'symbol': symbol,
        'initial_cash': cash,
        'final_value': final_value,
        'total_return': total_return,
        'max_drawdown': max_drawdown,
        'sharpe_ratio': sharpe_ratio,
        'win_rate': win_rate,
        'total_trades': total_trades,
    }


def run_from_cli():
    import argparse
    parser = argparse.ArgumentParser(description='投資策略回測引擎')
    parser.add_argument('strategy', nargs='?', default='ma_cross',
                        help=f'策略名稱: {", ".join(STRATEGIES.keys())}')
    parser.add_argument('--symbol', default='GC=F', help='標的代號')
    parser.add_argument('--source', default='yfinance', choices=['db', 'yfinance'])
    parser.add_argument('--period', default='1y', help='yfinance 期間')
    parser.add_argument('--start', default=None, help='起始日 YYYY-MM-DD (db模式)')
    parser.add_argument('--end', default=None, help='結束日 YYYY-MM-DD (db模式)')
    parser.add_argument('--cash', type=float, default=None, help='初始資金')
    parser.add_argument('--list', action='store_true', help='列出所有策略')
    args = parser.parse_args()

    if args.list:
        print('可用策略:')
        for name in STRATEGIES:
            print(f'  - {name}')
        sys.exit(0)

    run_backtest(
        strategy_name=args.strategy,
        symbol=args.symbol,
        source=args.source,
        period=args.period,
        start_date=args.start,
        end_date=args.end,
        cash=args.cash,
    )


# ============================================
# CLI 入口
# ============================================

if __name__ == '__main__':
    run_from_cli()
