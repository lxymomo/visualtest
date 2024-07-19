import pandas as pd
import numpy as np
import datashader as ds
import datashader.transfer_functions as tf
import matplotlib.pyplot as plt
from datashader.mpl_ext import dsshow

# 加载数据
data = pd.read_csv('BATS_QQQ, 5_processed.csv', index_col='datetime', parse_dates=True)

# 计算移动平均线
data['FastMA'] = data['close'].rolling(window=10).mean()
data['SlowMA'] = data['close'].rolling(window=20).mean()

# 生成交易信号
data['Signal'] = 0
data.loc[data.index[10:], 'Signal'] = np.where(data.loc[data.index[10:], 'FastMA'] > data.loc[data.index[10:], 'SlowMA'], 1, 0)
data['Position'] = data['Signal'].diff()

def strategy_performance(data):
    initial_capital = 100000.0
    share_size = 10
    positions = pd.DataFrame(index=data.index).fillna(0.0)
    positions['Stock'] = share_size * data['Signal']
    
    portfolio = positions.multiply(data['close'], axis=0)
    pos_diff = positions.diff()
    
    portfolio['holdings'] = (positions.multiply(data['close'], axis=0)).sum(axis=1)
    portfolio['cash'] = initial_capital - (pos_diff.multiply(data['close'], axis=0)).sum(axis=1).cumsum()
    portfolio['total'] = portfolio['cash'] + portfolio['holdings']
    portfolio['returns'] = portfolio['total'].pct_change()
    
    return portfolio

portfolio = strategy_performance(data)
print(portfolio.tail())

def plot_chart(data, portfolio):
    cvs = ds.Canvas(plot_width=800, plot_height=400, x_range=(data.index.min(), data.index.max()), y_range=(data['close'].min(), data['close'].max()))
    agg = cvs.line(data, 'datetime', 'close', ds.mean('close'))
    img = tf.shade(agg, cmap=["lightblue", "darkblue"], how='log')
    
    # 绘制资金曲线
    fig, ax = plt.subplots(2, sharex=True, figsize=(14,8))
    
    # Datashader的绘图
    dsshow(img, ax=ax[0], how='log')
    ax[0].set_title('SuperChart with Strategy Signals')
    
    # 绘制资金曲线
    ax[1].plot(portfolio['total'], label='Total Portfolio Value')
    ax[1].set_ylabel('Portfolio Value in $')
    ax[1].legend()

    plt.show()

plot_chart(data, portfolio)

class Strategy:
    def __init__(self, data, fast_window=10, slow_window=20):
        self.data = data
        self.fast_window = fast_window
        self.slow_window = slow_window
        self._calculate_indicators()

    def _calculate_indicators(self):
        self.data['FastMA'] = self.data['close'].rolling(window=self.fast_window).mean()
        self.data['SlowMA'] = self.data['close'].rolling(window=self.slow_window).mean()
        self.data['Signal'] = 0
        self.data.loc[self.data.index[self.fast_window:], 'Signal'] = np.where(self.data.loc[self.data.index[self.fast_window:], 'FastMA'] > self.data.loc[self.fast_window:, 'SlowMA'], 1, 0)
        self.data['Position'] = self.data['Signal'].diff()

    def performance(self):
        return strategy_performance(self.data)

    def plot(self):
        portfolio = self.performance()
        plot_chart(self.data, portfolio)

# 使用自定义策略
strategy = Strategy(data, fast_window=10, slow_window=20)
strategy.plot()
