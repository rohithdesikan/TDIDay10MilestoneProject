# --------------------------------------------------------------
######### Import Relevant Packages
from flask import Flask, render_template, request, redirect, Markup

import numpy as np
import pandas as pd
import requests
import json

# Data Visualization Library Imports
# import matplotlib.pyplot as plt

import seaborn as sns

from bokeh.io import output_notebook, show, output_file, save

from bokeh.plotting import figure, show, output_file

from bokeh.models import ColumnDataSource as cds
from bokeh.models import Plot, DatetimeAxis, PanTool, WheelZoomTool, HoverTool, tickers, BoxAnnotation, Panel, Range1d
from bokeh.models import LabelSet, Label, DatetimeTickFormatter

from bokeh.embed import file_html, components

from bokeh.resources import INLINE, CDN

output_notebook()
# --------------------------------------------------------------



# --------------------------------------------------------------
######### Define a constant style for all plots
def style(p):
        # Title
        p.title.align = 'center'
        p.title.text_font_size = '16pt'
        p.title.text_font = 'sans serif'

        # Axis titles
        p.xaxis.axis_label_text_font_size = '12pt'
        p.xaxis.axis_label_text_font_style = 'bold'
        p.yaxis.axis_label_text_font_size = '12pt'
        p.yaxis.axis_label_text_font_style = 'bold'

        # Tick labels
        p.xaxis.major_label_text_font_size = '10pt'
        p.yaxis.major_label_text_font_size = '10pt'

        return p
# --------------------------------------------------------------



# --------------------------------------------------------------
######### Setup Quandl API key
qapi = "&api_key=KXdhzkUh3sEAJndGdmag"

# Interested Company:
# ccode = 'TSLA'
# --------------------------------------------------------------



# --------------------------------------------------------------
######### Function to pull data and clean based on user input
def obtain_clean_data(ccode,start_date,end_date):
    # Setup keys we are interested in for API call
    keys = {'column_index':'4','start_date':start_date,'end_date':end_date,'order':'asc'}

    # Specific URL
    url = "https://www.quandl.com/api/v3/datasets/WIKI/" + ccode + ".json?" + qapi

    # Pass
    r = requests.get(url,params=keys)
    json_data = r.json()
    # display(json_data)

    dfinit = pd.DataFrame({'Closing Price':json_data['dataset']['data']})
    one = ['No']*len(dfinit)
    two = np.zeros((len(dfinit),1))
    for a in range(0,len(dfinit)):
        one[a] = dfinit.iloc[a][0][0]
        two[a] = dfinit.iloc[a][0][1]

    dates = pd.to_datetime(one,yearfirst=True)
    df = pd.DataFrame({'Date':dates})
    df.set_index('Date',inplace=True)
    df['ClosePrice']=two
    code = ccode
    startdate=start_date
    enddate=end_date
    return df, code, startdate, enddate
# --------------------------------------------------------------




# --------------------------------------------------------------
######### Function to graph data
def create_graph(dfp,code,start_date,end_date):
    src = cds(dfp)

    plot = figure(plot_width=900, plot_height=600,
       x_axis_label = 'Date', x_axis_type='datetime',
       y_axis_label ='Stock Price [$]',
       title = 'Stock Closing Price Trend between %s and %s for %s' %(start_date, end_date, code),
       tools="save,pan,undo,wheel_zoom,box_zoom,reset")

    plot.line(source=src, x='Date', y='ClosePrice',line_width=2)

    # Add hover tool fuctionality
    plot.add_tools(HoverTool(
        tooltips=[
            ('Date',            '@Date{%Y-%m-%d}'),
            ('Stock Price [$]', '@ClosePrice{0.2f}'), # use @{ } for field names with spaces
        ],
        formatters={
            'Date'             : 'datetime', # use 'datetime' formatter for 'date' field
            'Stock Price [$]'  : 'printf',
        },
        mode='vline'
    ))

    plot.xaxis.formatter=DatetimeTickFormatter(
        days=["%Y-%m-%d"])

    style(plot)
    # show(plot)
    # save(plot)
    # html_plot = file_html(plot,CDN,"Stock Plot")
    script, div = components(plot)
    return plot, script, div
# --------------------------------------------------------------




# --------------------------------------------------------------
######### HTML Connection Code
app = Flask(__name__)

######### Main page
@app.route('/')
def index():
  return render_template('index.html')


######### About page
@app.route('/about')
def about():
  return render_template('about.html')


######### Stock Ticker Page
@app.route('/stocks',methods =['GET','POST'])
def stock():
    if request.method == 'GET':
        return render_template('stock.html')
    else:
        company_name=request.form['company']
        start_date = request.form['start_date']
        end_date =request.form['end_date']
        df,code,startdate,enddate = obtain_clean_data(company_name,start_date,end_date)
        plot,script,div = create_graph(df,code,startdate,enddate)
        # return render_template('stock.html', graph_num=plot)
        return Markup(file_html(plot,resources=CDN,template='stock.html'))

if __name__ == '__main__':
  app.run(port=33507,debug=True)
