"""可用策略註冊表"""
from .ma_cross import MACrossStrategy
from .rsi import RSIStrategy
from .bollinger import BollingerStrategy
from .macd import MACDStrategy
from .breakout import BreakoutStrategy
from .ensemble import EnsembleStrategy

# 所有可用策略
STRATEGIES = {
    'ma_cross': MACrossStrategy,
    'rsi': RSIStrategy,
    'bollinger': BollingerStrategy,
    'macd': MACDStrategy,
    'breakout': BreakoutStrategy,
    'ensemble': EnsembleStrategy,
}
