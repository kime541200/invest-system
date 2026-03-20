"""
策略參數優化器 — Grid Search 找最佳參數組合
"""
import sys
import time
import sqlite3
import argparse
from itertools import product
from datetime import datetime
from pathlib import Path

from config import DB_PATH, DEFAULT_CASH
from strategies import STRATEGIES
from backtest import run_backtest
from db.store import get_conn

# ============================================
# 預設參數範圍
# ============================================
DEFAULT_PARAM_GRIDS = {
    'ma_cross': {
        'fast_period': [3, 5, 8, 10, 13],
        'slow_period': [15, 20, 30, 40, 60],
    },
    'rsi': {
        'rsi_period': [7, 14, 21],
        'oversold': [20, 25, 30],
        'overbought': [70, 75, 80],
    },
    'bollinger': {
        'period': [15, 20, 25, 30],
        'devfactor': [1.5, 2.0, 2.5],
    },
    'macd': {
        'fast': [8, 12, 16],
        'slow': [21, 26, 30],
        'signal': [5, 9, 13],
    },
    'breakout': {
        'entry_period': [10, 15, 20, 30],
        'exit_period': [5, 10, 15],
    },
}


def generate_combinations(param_grid):
    """產生所有參數組合"""
    keys = list(param_grid.keys())
    values = [param_grid[k] for k in keys]
    for combo in product(*values):
        yield dict(zip(keys, combo))


def save_optimization_result(strategy, symbol, params_str, total_return,
                             max_drawdown, sharpe_ratio, win_rate,
                             total_trades, initial_cash, final_value):
    """存入 backtest_results 表"""
    conn = get_conn()
    conn.execute(
        """INSERT INTO backtest_results
           (strategy, symbol, start_date, end_date, initial_cash, final_value,
            total_return, max_drawdown, sharpe_ratio, win_rate, total_trades)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (f'{strategy}|{params_str}', symbol, 'optimizer', datetime.now().isoformat(),
         initial_cash, final_value, total_return, max_drawdown,
         sharpe_ratio, win_rate, total_trades)
    )
    conn.commit()
    conn.close()


def optimize(strategy_name, symbol, param_grid=None, source='yfinance',
             period='1y', cash=None, top_n=10, start_date=None, end_date=None):
    """
    對策略做 grid search 參數優化

    Args:
        strategy_name: 策略名稱 (ma_cross, rsi, ...)
        symbol: 標的代號
        param_grid: dict of lists，每個參數的搜尋範圍
        source: 資料來源 (db / yfinance)
        period: yfinance 期間
        cash: 初始資金
        top_n: 顯示前 N 名
    """
    if strategy_name not in STRATEGIES:
        print(f'未知策略: {strategy_name}')
        print(f'可用策略: {", ".join(STRATEGIES.keys())}')
        return []

    # 使用預設或自訂參數範圍
    if param_grid is None:
        param_grid = DEFAULT_PARAM_GRIDS.get(strategy_name, {})
    if not param_grid:
        print(f'{strategy_name} 沒有定義參數範圍')
        return []

    cash = cash or DEFAULT_CASH
    combinations = list(generate_combinations(param_grid))
    total = len(combinations)

    print(f'=== 參數優化: {strategy_name} on {symbol} ===')
    print(f'參數範圍: {param_grid}')
    print(f'共 {total} 組參數組合')
    print(f'資料來源: {source} (period={period})')
    print()

    results = []
    start_time = time.time()

    for i, params in enumerate(combinations, 1):
        # 進度條
        pct = i / total * 100
        elapsed = time.time() - start_time
        eta = (elapsed / i * (total - i)) if i > 0 else 0
        sys.stdout.write(f'\r  [{i}/{total}] {pct:.0f}% | ETA {eta:.0f}s | {params}')
        sys.stdout.flush()

        result = run_backtest(
            strategy_name=strategy_name,
            symbol=symbol,
            source=source,
            period=period,
            start_date=start_date,
            end_date=end_date,
            cash=cash,
            params=params,
            silent=True,
        )

        if result:
            result['params'] = params
            results.append(result)

    elapsed = time.time() - start_time
    print(f'\n\n完成! 共跑 {len(results)}/{total} 組，耗時 {elapsed:.1f}s')

    if not results:
        print('沒有有效結果')
        return []

    # 按 total_return 排序
    results.sort(key=lambda x: x['total_return'], reverse=True)

    # 顯示 Top N
    show_n = min(top_n, len(results))
    print(f'\n{"="*90}')
    print(f' Top {show_n} 最佳參數組合')
    print(f'{"="*90}')
    print(f'{"#":>3} | {"參數":<35} | {"報酬率":>8} | {"回撤":>7} | {"Sharpe":>7} | {"勝率":>6} | {"交易":>4}')
    print(f'{"-"*3}-+-{"-"*35}-+-{"-"*8}-+-{"-"*7}-+-{"-"*7}-+-{"-"*6}-+-{"-"*4}')

    for rank, r in enumerate(results[:show_n], 1):
        params_str = ', '.join(f'{k}={v}' for k, v in r['params'].items())
        print(f'{rank:>3} | {params_str:<35} | {r["total_return"]:>+7.2f}% | '
              f'{r["max_drawdown"]:>6.2f}% | {r["sharpe_ratio"]:>7.3f} | '
              f'{r["win_rate"]:>5.1f}% | {r["total_trades"]:>4}')

        # 存入 SQLite
        save_optimization_result(
            strategy=strategy_name,
            symbol=symbol,
            params_str=params_str,
            total_return=r['total_return'],
            max_drawdown=r['max_drawdown'],
            sharpe_ratio=r['sharpe_ratio'],
            win_rate=r['win_rate'],
            total_trades=r['total_trades'],
            initial_cash=r['initial_cash'],
            final_value=r['final_value'],
        )

    print(f'{"="*90}')
    print(f'結果已存入 SQLite: {DB_PATH}')

    # 最佳參數
    best = results[0]
    print(f'\n最佳參數: {best["params"]}')
    print(f'  報酬率: {best["total_return"]:+.2f}%')
    print(f'  Sharpe: {best["sharpe_ratio"]:.3f}')

    return results


def list_strategies():
    """列出可用策略和預設參數範圍"""
    print('可用策略和預設參數範圍:')
    print('=' * 60)
    for name, cls in STRATEGIES.items():
        grid = DEFAULT_PARAM_GRIDS.get(name, {})
        combos = 1
        for v in grid.values():
            combos *= len(v)
        print(f'\n  {name}:')
        if grid:
            for param, values in grid.items():
                print(f'    {param}: {values}')
            print(f'    -> 共 {combos} 組參數組合')
        else:
            print('    (無預設參數範圍)')


# ============================================
# CLI 入口
# ============================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='策略參數優化器 (Grid Search)')
    parser.add_argument('strategy', nargs='?', default=None,
                        help=f'策略名稱: {", ".join(STRATEGIES.keys())}')
    parser.add_argument('--symbol', default='GC=F', help='標的代號')
    parser.add_argument('--source', default='yfinance', choices=['db', 'yfinance'])
    parser.add_argument('--period', default='2y', help='yfinance 期間')
    parser.add_argument('--cash', type=float, default=None, help='初始資金')
    parser.add_argument('--top', type=int, default=10, help='顯示前 N 名')
    parser.add_argument('--list', action='store_true', help='列出可用策略和參數範圍')
    parser.add_argument('--start', default=None, help='起始日 YYYY-MM-DD (db模式)')
    parser.add_argument('--end', default=None, help='結束日 YYYY-MM-DD (db模式)')
    args = parser.parse_args()

    if args.list:
        list_strategies()
        sys.exit(0)

    if not args.strategy:
        parser.print_help()
        sys.exit(1)

    optimize(
        strategy_name=args.strategy,
        symbol=args.symbol,
        source=args.source,
        period=args.period,
        cash=args.cash,
        top_n=args.top,
        start_date=args.start,
        end_date=args.end,
    )
