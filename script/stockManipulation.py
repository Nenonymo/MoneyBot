#Raw packages
import numpy as np
import pandas as pd

#Data source
import yfinance as yf
from yahoo_fin import stock_info as si

#Data viz
import plotly.graph_objs as go #need kaleido to work



def lastValue(stockID):
    return(si.get_live_price(stockID))

def graph1Day(stockID):
    data = yf.download(tickers=stockID, period='1d', interval='1m')
    #declare Figure
    fig = go.Figure()
    #Candlestick
    fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'],
                                low=data['Low'], close=data['Close'], name='market_data'))
    # Add titles
    fig.update_layout(
                    title=stockID+' live share price evolution, One DAY',
                    yaxis_title='Stock Price (USD per Shares)')
    fig.write_image('images/graph1D.png')

def graph1Month(stockID):
    data = yf.download(tickers=stockID, period='1mo', interval='1d')
    #declare Figure
    fig = go.Figure()
    #Candlestick
    fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'],
                                low=data['Low'], close=data['Close'], name='market_data'))
    # Add titles
    fig.update_layout(
                    title=stockID+' live share price evolution, One MONTH',
                    yaxis_title='Stock Price (USD per Shares)')
    fig.write_image('images/graph1M.png')

def graph6Month(stockID):
    data = yf.download(tickers=stockID, period='6mo', interval='1d')
    #declare Figure
    fig = go.Figure()
    #Candlestick
    fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'],
                                low=data['Low'], close=data['Close'], name='market_data'))
    # Add titles
    fig.update_layout(
                    title=stockID+' live share price evolution, Six MONTHS',
                    yaxis_title='Stock Price (USD per Shares)')
    fig.write_image('images/graph6M.png')