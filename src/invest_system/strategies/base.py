"""策略基類 — 所有策略繼承此類"""
import backtrader as bt


class BaseStrategy(bt.Strategy):
    """
    可插拔策略基類
    子類只需要實作 next() 和設定 params
    """
    params = (
        ('name', 'unnamed'),
    )

    def __init__(self):
        self.order = None
        self.trade_count = 0
        self.win_count = 0
        self.trades = []

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'  [{self.p.name}] {dt} {txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'買入 @ {order.executed.price:.2f} x {order.executed.size}')
            else:
                self.log(f'賣出 @ {order.executed.price:.2f} x {order.executed.size}')

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f'訂單失敗: {order.getstatusname()}')

        self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            self.trade_count += 1
            if trade.pnl > 0:
                self.win_count += 1
            self.trades.append({
                'pnl': trade.pnl,
                'pnlcomm': trade.pnlcomm,
            })
            self.log(f'平倉 損益: {trade.pnl:.2f} (扣手續費: {trade.pnlcomm:.2f})')

    @property
    def win_rate(self):
        return self.win_count / self.trade_count if self.trade_count > 0 else 0
