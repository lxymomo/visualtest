import pandas as pd
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource
from bokeh.layouts import column
import numpy as np

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
    p1 = figure(x_axis_type="datetime", title="SuperChart with Strategy Signals", width=800, height=400)
    p1.line(data.index, data['close'], color='blue', legend_label='Close Price')
    p1.line(data.index, data['FastMA'], color='green', legend_label='Fast MA')
    p1.line(data.index, data['SlowMA'], color='red', legend_label='Slow MA')

    buy_signals = data[data['Position'] == 1]
    sell_signals = data[data['Position'] == -1]

    p1.triangle(buy_signals.index, buy_signals['FastMA'], size=10, color='green', legend_label='Buy')
    p1.inverted_triangle(sell_signals.index, sell_signals['FastMA'], size=10, color='red', legend_label='Sell')

    p2 = figure(x_axis_type="datetime", title="Total Portfolio Value", width=800, height=400)
    p2.line(portfolio.index, portfolio['total'], color='blue', legend_label='Total Portfolio Value')

    show(column(p1, p2))

output_file("superchart.html")
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
        self.data.loc[self.data.index[self.fast_window:], 'Signal'] = np.where(self.data.loc[self.data.index[self.fast_window:], 'FastMA'] > self.data.loc[self.data.index[self.fast_window:], 'SlowMA'], 1, 0)
        self.data['Position'] = self.data['Signal'].diff()

    def performance(self):
        return strategy_performance(self.data)

    def plot(self):
        portfolio = self.performance()
        plot_chart(self.data, portfolio)

# 使用自定义策略
strategy = Strategy(data, fast_window=10, slow_window=20)
strategy.plot()
