import pandas as pd
import numpy as np
import holoviews as hv
import hvplot.pandas
from holoviews.operation.datashader import datashade
import panel as pn

hv.extension('bokeh')

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

# 创建买卖点标记
buy_signals = data[data['Position'] == 1]
sell_signals = data[data['Position'] == -1]

# 使用Holoviews和Datashader绘制
close_curve = data.hvplot.line(y='close', label='Close Price').opts(width=800, height=400)
fast_ma_curve = data.hvplot.line(y='FastMA', label='Fast MA')
slow_ma_curve = data.hvplot.line(y='SlowMA', label='Slow MA')

buy_points = buy_signals.hvplot.scatter(y='FastMA', color='green', marker='^', size=10, label='Buy')
sell_points = sell_signals.hvplot.scatter(y='FastMA', color='red', marker='v', size=10, label='Sell')

shaded_close_curve = datashade(close_curve)
shaded_fast_ma_curve = datashade(fast_ma_curve)
shaded_slow_ma_curve = datashade(slow_ma_curve)

portfolio_curve = portfolio.hvplot.line(y='total', label='Total Portfolio Value').opts(width=800, height=400)

# 显示图表和数据分析
dashboard = pn.Column(
    (shaded_close_curve * shaded_fast_ma_curve * shaded_slow_ma_curve * buy_points * sell_points).opts(title='Strategy Performance'),
    portfolio_curve.opts(title='Portfolio Value'),
    data.hvplot.table(columns=['close', 'FastMA', 'SlowMA', 'Signal', 'Position']),
    portfolio.hvplot.table(columns=['holdings', 'cash', 'total', 'returns'])
)

# 在浏览器中显示
pn.serve(dashboard, start=True)
