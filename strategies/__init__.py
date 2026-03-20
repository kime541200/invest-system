"""可用策略註冊表"""
from strategies.ma_cross import MACrossStrategy
from strategies.rsi import RSIStrategy
from strategies.bollinger import BollingerStrategy
from strategies.macd import MACDStrategy
from strategies.breakout import BreakoutStrategy
from strategies.ensemble import EnsembleStrategy

# 所有可用策略
STRATEGIES = {
    'ma_cross': MACrossStrategy,
    'rsi': RSIStrategy,
    'bollinger': BollingerStrategy,
    'macd': MACDStrategy,
    'breakout': BreakoutStrategy,
    'ensemble': EnsembleStrategy,
}
