######################################################################################
#
# Topic: Visualizing and Comparing Streaming Stocks data from Google API using Bokeh.
# Execution: 
#			1) Go to the code directory.
#			2) Open terminal/command prompt.
#			3) Run command: python -m bokeh serve <FileName>.py
#
######################################################################################

# importing libraries
from datetime import datetime

import pandas as pd
from pandas_datareader import data

from bokeh.io import curdoc
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import PreText, Select
from bokeh.plotting import figure

# declare default Stock names
DEFAULT_TICKERS = [ 'GOOG', 'AMZN', 'T', 'S', 'VZ']

def nix(val, lst):
    return [x for x in lst if x != val]
	
# extract stock closing prices from quandl
def load_ticker(ticker):
    sname = [ticker]
    data_source = 'quandl'
    start_date = datetime(2016, 1, 1)
    end_date = datetime(2017, 1, 1)
    all_data = {ticker: data.DataReader(ticker, data_source, start_date, end_date) for ticker in DEFAULT_TICKERS}
    stocks_data = pd.DataFrame({ticker: data['AdjClose'] for ticker, data in all_data.items()})		
    #stock_data = data.DataReader(sname, data_source, start_date, end_date)
    #stock_closing_data = stock_data.loc['AdjClose']
    return pd.DataFrame({ticker: stocks_data[ticker], ticker+'_returns': stocks_data[ticker].diff()})

def get_data(t1, t2):
    df1 = load_ticker(t1)
    df2 = load_ticker(t2)
    data = pd.concat([df1, df2], axis=1)
    data = data.dropna()
    data['t1'] = data[t1]
    data['t2'] = data[t2]
    data['t1_returns'] = data[t1+'_returns']
    data['t2_returns'] = data[t2+'_returns']
    return data

# set up widgets

stats = PreText(text='Aggregated Statistics', width=1000)
ticker1 = Select(value='AMZN', options=nix('GOOG', DEFAULT_TICKERS))
ticker2 = Select(value='GOOG', options=nix('AMZN', DEFAULT_TICKERS))

# set up plots
source = ColumnDataSource(data=dict(Date=[], t1=[], t2=[], t1_returns=[], t2_returns=[]))
source_static = ColumnDataSource(data=dict(Date=[], t1=[], t2=[], t1_returns=[], t2_returns=[]))
tools = 'pan,wheel_zoom,xbox_select,reset'

ts1 = figure(plot_width=1000,
             plot_height=350, 
             tools=tools,
             x_axis_type='datetime',
             active_drag="xbox_select")
ts1.line('Date', 't1', source=source_static, color='green' )
ts1.line('Date', 't2', source=source_static, color='blue')
ts1.circle('Date', 't1', size=1, source=source, color=None, selection_color="orange")
ts1.circle('Date', 't2', size=1, source=source, color=None, selection_color="orange")

# set up callbacks
def ticker1_change(attrname, old, new):
    ticker2.options = nix(new, DEFAULT_TICKERS)
    update()

def ticker2_change(attrname, old, new):
    ticker1.options = nix(new, DEFAULT_TICKERS)
    update()

def update(selected=None):
    t1, t2 = ticker1.value, ticker2.value

    data = get_data(t1, t2)
    source.data = source.from_df(data[['t1', 't2', 't1_returns', 't2_returns']])
    source_static.data = source.data

    update_stats(data, t1, t2)
    ts1.title.text = '%s (Green) vs. %s (Blue)' % (t1, t2)

def update_stats(data, t1, t2):
    stats.text = str(data[[t1, t2, t1+'_returns', t2+'_returns']].describe())

ticker1.on_change('value', ticker1_change)
ticker2.on_change('value', ticker2_change)

def selection_change(attrname, old, new):
    t1, t2 = ticker1.value, ticker2.value
    data = get_data(t1, t2)
    selected = source.selected['1d']['indices']
    if selected:
        data = data.iloc[selected, :]
    update_stats(data, t1, t2)

source.on_change('selected', selection_change)

# set up layout
layout = column(row(ticker1, ticker2), ts1, stats)

# initialize
update()

curdoc().add_root(layout)
curdoc().title = "Stocks"
