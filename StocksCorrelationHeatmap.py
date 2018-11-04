# -*- coding: utf-8 -*-

######################################################################################
#
# Topic: Visualizing Correlation Between Stock Closing Rates using Heat Map.
# Execution: 
#			1) Go to the code directory.
#			2) Open terminal/command prompt.
#			3) Run command: python -m bokeh serve <FileName>.py
#
######################################################################################

# importing libraries
import math
from datetime import datetime
import numpy as np, pandas as pd, pandas_datareader.data as dataR

from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.layouts import layout
from bokeh.models import (
                            ColumnDataSource, 
                            Slider, Button, 
                            LinearColorMapper, 
                            BasicTicker, ColorBar,
                            PrintfTickFormatter
                         )

# read stock data from quandl API

stocks = ['AAPL', 'IBM', 'MSFT', 'GOOG', 'AMZN', 'NFLX']
start = datetime(2016, 10, 17)
end = datetime(2017, 10, 27)
all_data = {ticker: dataR.DataReader(ticker,'quandl',start, end)
            for ticker in stocks}
stocks_data = pd.DataFrame({ticker: data['AdjClose']
                     for ticker, data in all_data.items()})



# window size
window_days = 30

# step size
increment_days = 1

stock_dates = stocks_data.index.values
sub_dates = pd.date_range(min(stock_dates), periods=window_days, freq='D').values

slider_values = []

i=0
for date in stock_dates:
    date = int(str(date)[:10].replace('-', ''))
    slider_values.append([i, date])
    i = i+1
    

def get_stock_subset (start_date, window_days, increment_days):
    sub_dates = pd.date_range(start_date, periods=window_days, freq='D').values
    df_subset = stocks_data.ix[min(sub_dates): max(sub_dates)]
    subset_start_date = min(sub_dates)
    subset_end_date = max(sub_dates)
    return subset_start_date, subset_end_date, df_subset
    

window_start_date, window_end_date, stocks_data_subset = get_stock_subset (min(stock_dates), window_days, increment_days)

######################################################################################################################
# Data Processing and Graph Creation
######################################################################################################################
'''
stocks_ln =pd.DataFrame()
for col in stocks_data_subset:
    if col not in stocks_ln:
        stocks_ln[col] = np.log(stocks_data_subset[col]).diff()
'''		
# calculate percentage change
stocks_ln = stocks_data_subset.pct_change()
	
# calculate correlation between stock closing rates
corr_stocks = stocks_ln.corr()

factors_s = stocks

x_s = []
y_s = []
rate_s = []

for i in factors_s:
    for j in range(corr_stocks.shape[0]):
        x_s.append(i)

for i in range(corr_stocks.shape[0]):
    for j in factors_s:
        y_s.append(j)

for i in factors_s:
    for j in factors_s:
        rate_s.append(corr_stocks[i][j]*100)

# choose a diverging color pallete 
colors = ['#a50026','#d73027','#f46d43','#fdae61','#fee08b','#ffffbf','#d9ef8b','#a6d96a','#66bd63','#1a9850','#006837']       
mapper = LinearColorMapper(palette=colors, low=-100.0, high=100.0)

# create column data source using input subset of data
source = pd.DataFrame(
		{'x': x_s,
		 'y': y_s,
		 'rate': rate_s
		})
source = ColumnDataSource(source)

# create a plotting object for visualization
p = figure(title="Year: 2017 Stocks Correlation Heatmap", 
				tools="hover", 
				toolbar_location=None,
				x_range=factors_s, 
				y_range=factors_s,
				plot_height=700,
				plot_width=800)

# add a heatmap glyph to the plotting object
p.rect(    'x', 
           'y', 
           color=colors, 
           width=1, 
           height=1, 
           source=source,
		   fill_color={'field': 'rate', 'transform': mapper},
		   line_color=None)

# add a color bar to the plotting object
color_bar = ColorBar(color_mapper=mapper, 
                     major_label_text_font_size="5pt",
                     ticker=BasicTicker(desired_num_ticks=len(colors)),
                     formatter=PrintfTickFormatter(format="%d%%"),
                     label_standoff=6, 
                     border_line_color=None, 
                     location=(0, 0))

p.add_layout(color_bar, 'right')

p.title.text = "Stocks Correlation Heatmap:   Step Size: %d    Window Size: %d    Start Date: %s    End Date: %s" % ( increment_days, window_days, str(window_start_date)[:10], str(window_end_date)[:10])

TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"


######################################################################################################################
# Slider Functions
######################################################################################################################


def animate_update():
    slider_seq = math.floor(slider.value) + 1
    if int(slider_seq) > int(slider_values[-1][0]):
        slider_seq = int(slider_values[0][0])
    slider.value = slider_seq


def slider_update(attrname, old, new): 
    slider_date = slider_values[math.floor(slider.value)][1] 
    start_datetime = datetime.strptime(str(slider_date), '%Y%m%d')
    window_start_date, window_end_date, stocks_data_subset = get_stock_subset(start_datetime, window_days, increment_days)
    
    ######################################################################################################################
    # Data Processing and Graph Creation
    ######################################################################################################################
    
    stocks_ln =pd.DataFrame()
    
    for col in stocks_data_subset:
        if col not in stocks_ln:
            stocks_ln[col] = np.log(stocks_data_subset[col]).diff()
    
    corr_stocks = stocks_ln.corr()

    x_s = []
    y_s = []
    rate_s = []
    
    for i in factors_s:
        for j in range(corr_stocks.shape[0]):
            x_s.append(i)
            
    for i in range(corr_stocks.shape[0]):
        for j in factors_s:
            y_s.append(j)
            
    for i in factors_s:
        for j in factors_s:
            rate_s.append(corr_stocks[i][j]*100)
            
    new_source = pd.DataFrame(
		{'x': x_s,
		 'y': y_s,
		 'rate': rate_s
		})
    
    new_source = ColumnDataSource(new_source)
    source.data = new_source.data
    p.title.text = "Stocks Correlation Heatmap:   Step Size: %d    Window Size: %d    Start Date: %s    End Date: %s" % (increment_days, window_days, str(window_start_date)[:10], str(window_end_date)[:10])
    ######################################################################################################################
    
  
slider = Slider(start=int(slider_values[0][0]), end=int(slider_values[-1][0]), value=int(slider_values[0][0]), step=1, title="Simulation Sequence")
slider.on_change('value', slider_update)


def animate():
    if button.label == 'Play':
        button.label = 'Pause'
        curdoc().add_periodic_callback(animate_update, 1000)
    else:
        button.label = 'Play'
        curdoc().remove_periodic_callback(animate_update)

button = Button(label='Play', width=60)
button.on_click(animate)


layout = layout([
                   [slider, button], [p] 
                   
                ] 
               )

curdoc().add_root(layout)