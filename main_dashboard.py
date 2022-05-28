# GUI and others
import streamlit as st
import unicodedata
import pandas as pd

# stock data gathering,plotting and prediction
import datetime
import yfinance as yf
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go

#webscrapping
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import requests

# twitter library and internal files
import tweepy
import config
import bert_model

#  tweepy stuff
auth = tweepy.OAuth1UserHandler(
    config.TWITTER_COMSUMER_KEY,
    config.TWITTER_COMSUMER_SECRET,
    config.TWITTER_ACCESS_TOKEN,
    config.TWITTER_ACCESS_TOKEN_SECRET
)
api = tweepy.API(auth)

# sidebar
option = st.sidebar.selectbox("DASHBORAD", ("Stock Technical Analysis","Stock Sentiment Analysis","Predictions","Twitter Feed", "Stocktwits Feed"))
st.markdown("<a id='top'></a>",unsafe_allow_html=True)

# FUNCTIONS     
@st.cache
def get_ticker(keyword):
    # keyword is the searched compnay name
    if keyword.isalpha() == False:
        st.sidebar.error("No special characters or spaces allowed!")
    else:
        search_url = f'https://finviz.com/search.ashx?p={keyword}'
        req=Request(url=search_url,headers={'user-agent':'my-app'})
        response=urlopen(req)

        soup = BeautifulSoup(response,features="html.parser")
        comp_table = soup.find(class_="styled-table is-full-width is-condensed is-striped is-hoverable has-full-row-links")
        ticker = comp_table.find('a').get_text()
        return ticker

@st.cache
def get_comp_name(symbol):
    # symbol = ticker
    yahoo_url = f'https://finance.yahoo.com/quote/{symbol}'
    req = Request(url=yahoo_url, headers={'user-agent': 'my-app'})
    response = urlopen(req)

    html = BeautifulSoup(response, features="html.parser")
    comp_name = html.find('h1', "D(ib) Fz(18px)")
    return comp_name.get_text()

def get_data(ticker):
    data = yf.download(tickers=ticker,period="20y")
    data.reset_index(inplace=True)
    return data

def plot_raw_data(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'],y=data['Open'],name="stock_open"))
    fig.add_trace(go.Scatter(x=data['Date'],y=data['Close'],name="stock_close"))
    st.subheader("Time Series Data")
    fig.layout.update(xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)


# DASHBOARDS

# Stock Analysis & News
if(option == "Stock Technical Analysis"):

    st.header('Stock Technical Analysis')
    st.markdown(' ')

    # loading animation
    with st.spinner('loading...'):

        keyword = st.sidebar.text_input("COMPANY NAME","apple")
        symbol = get_ticker(keyword)
        comp_name = get_comp_name(symbol)
        data = get_data(symbol)
        ticker = yf.Ticker(symbol)

    # company logo and  name
    col1,col2 = st.columns([2,20])
    col1.image(ticker.info['logo_url'])
    col2.markdown(f'<p style="font-family:Tahoma; font-size:30px;">{comp_name}</p>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-family:Tahoma; font-size:18px; font-weight:medium">{ticker.info["country"]} | {ticker.info["sector"]}</p>', unsafe_allow_html=True)

    # metrics
    st.markdown("---")
    col1, col2, col3, col4, col5 = st.columns([4,2,4,2,4])
    # Current high low
    col1.metric("Current (USD)",ticker.info['currentPrice'],round(ticker.info['currentPrice']-ticker.info['open'],2))
    col3.metric("Day Low (USD)",ticker.info['dayLow'],round(ticker.info['dayLow']-ticker.info['currentPrice'],2))
    col5.metric("Day High (USD)",ticker.info['dayHigh'],round(ticker.info['dayHigh']-ticker.info['currentPrice'],2))
    col1.markdown("---")
    col3.markdown("---")
    col5.markdown("---")

    # close open
    col1.metric("Prev CLose (USD)",ticker.info['previousClose'],round(ticker.info['previousClose']-ticker.info['regularMarketPreviousClose'],2))
    col3.metric("Open (USD)",ticker.info['open'],round(ticker.info['open']-ticker.info['regularMarketOpen'],2))
    col5.metric("50 Days Avg (USD)",round(ticker.info['fiftyDayAverage'],2),round(ticker.info['fiftyDayAverage']-ticker.info['twoHundredDayAverage'],2))
    col1.markdown("---")
    col3.markdown("---")
    col5.markdown("---")

    # prices
    col1.metric("Recommendation",ticker.info['recommendationKey'] )
    col3.metric("Target Low (USD)",ticker.info['targetLowPrice'],round(ticker.info['targetLowPrice']-ticker.info['dayLow'],2))
    col5.metric("Target High (USD)",ticker.info['targetHighPrice'],round(ticker.info['dayHigh']-ticker.info['targetHighPrice'],2))

    # timedata
    st.markdown("---")
    timedata = datetime.datetime.now().strftime("%m-%d-%Y  %I:%M:%S %p")
    st.markdown(f'<p style="color:#1ac49f; font-family:Tahoma; font-size:14px;">{timedata}</p>', unsafe_allow_html=True)
    
    # image + finviz link
    st.markdown(f"[![Foo](https://charts2.finviz.com/chart.ashx?t={symbol})](https://finviz.com/quote.ashx?t={symbol})")

    # stock technicals
    st.sidebar.write("TECHNICALS")
    st.sidebar.markdown("<a href='#Quaterly_Financials' style='color:#1ac49f; font-family:Tahoma; font-size:14px; text-decoration: none;'>&#8227; Quaterly Financials </a>",unsafe_allow_html=True)
    st.sidebar.markdown("<a href='#Quaterly_Cashflow' style='color:#1ac49f; font-family:Tahoma; font-size:14px; text-decoration: none;'>&#8227; Quaterly Cashflow </a>",unsafe_allow_html=True)
    st.sidebar.markdown("<a href='#Quaterly_Earnings' style='color:#1ac49f; font-family:Tahoma; font-size:14px; text-decoration: none;'>&#8227; Quaterly Earnings </a>",unsafe_allow_html=True)
    st.sidebar.markdown("<a href='#Balance_Sheet' style='color:#1ac49f; font-family:Tahoma; font-size:14px; text-decoration: none;'>&#8227; Balance Sheet </a>",unsafe_allow_html=True)
    st.sidebar.markdown("<a href='#Major_Holder' style='color:#1ac49f; font-family:Tahoma; font-size:14px; text-decoration: none;'>&#8227; Major Holders </a>",unsafe_allow_html=True)
    st.sidebar.markdown("<a href='#Institutional_Holders' style='color:#1ac49f; font-family:Tahoma; font-size:14px; text-decoration: none;'>&#8227; Institutional Holders </a>",unsafe_allow_html=True)
    st.sidebar.markdown("<a href='#Recommendations' style='color:#1ac49f; font-family:Tahoma; font-size:14px; text-decoration: none;'>&#8227; Recommendations </a>",unsafe_allow_html=True)
    st.sidebar.markdown("<a href='#top' style='color:#1ac49f; font-family:Tahoma; font-size:14px; text-decoration: none;'>&#8227; Back to top </a>",unsafe_allow_html=True)

    # routing
    st.markdown("<a id='Quaterly_Financials'></a>",unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("Quaterly Financials")
    st.write(ticker.quarterly_financials)

    st.markdown("<a id='Quaterly_Cashflow'></a>",unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("Quaterly Cashflow")
    st.write(ticker.quarterly_cashflow)

    st.markdown("<a id='Quaterly_Earnings'></a>",unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("Quaterly Earnings")
    st.write(ticker.quarterly_earnings)

    st.markdown("<a id='Balance_Sheet'></a>",unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("Balance Sheet")
    st.write(ticker.balance_sheet)

    st.markdown("<a id='Major_Holder'></a>",unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("Major Holder")
    st.write(ticker.major_holders)

    st.markdown("<a id='Institutional_Holders'></a>",unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("Institutional Holders")
    st.write(ticker.institutional_holders)

    st.markdown("<a id='Recommendations'></a>",unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("Recommendations")
    st.write(ticker.recommendations)

# Predictions
if(option == "Predictions"):

    st.header("Predictions")
    st.markdown(" ")
    st.sidebar.markdown("<a href='#top' style='color:#1ac49f; font-family:Tahoma; font-size:14px; text-decoration: none;'>&#8227; Back to top </a>",unsafe_allow_html=True)
    # loading animation
    with st.spinner('loading...'):
        keyword = st.sidebar.text_input("COMPANY NAME","apple")
        symbol = get_ticker(keyword)
        comp_name = get_comp_name(symbol)

        data = get_data(symbol)
        ticker = yf.Ticker(symbol)

        # company logo and  name
        col1,col2 = st.columns([2,20])
        col1.image(ticker.info['logo_url'])
        col2.markdown(f'<p style="font-family:Tahoma; font-size:30px;">{comp_name}</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-family:Tahoma; font-size:18px; font-weight:medium">{ticker.info["country"]} | {ticker.info["sector"]}</p>', unsafe_allow_html=True)

        timedata = datetime.datetime.now().strftime("%m-%d-%Y  %I:%M:%S %p")
        START = "2010-01-01"
        TODAY = timedata
        st.markdown("")

        st.subheader("Years of prediction:")
        n_years = st.slider("",1,10)
        period = n_years * 365

        # plotting raw data
        plot_raw_data(data)

    # loading animation
    with st.spinner('Computing predictions...'):
        # Forcasting
        df_train = data[['Date','Close']]
        df_train = df_train.rename(columns={"Date" : "ds","Close" : "y"})

        m = Prophet()
        m.fit(df_train)
        future = m.make_future_dataframe(periods=period)
        forecast = m.predict(future)

        st.subheader("Forecast data")
        fig1 = plot_plotly(m,forecast)
        st.plotly_chart(fig1)

        st.subheader("Forecast components")
        fig2 = m.plot_components(forecast)
        st.write(fig2)

        st.markdown('---')

        st.markdown("<a href='#top'> Back to top </a>",unsafe_allow_html=True)

# Stock Sentiment Analysis
if(option == "Stock Sentiment Analysis"):

    st.header("Stock Sentiment Analysis")
    st.markdown(" ")

    # loading animation
    with st.spinner('loading...'):
        keyword = st.sidebar.text_input("COMPANY NAME","apple")
        symbol = get_ticker(keyword)
        comp_name = get_comp_name(symbol)
        ticker = yf.Ticker(symbol)
        # back to top
        st.sidebar.markdown("<a href='#top' style='color:#1ac49f; font-family:Tahoma; font-size:14px; text-decoration: none;'>&#8227; Back to top </a>",unsafe_allow_html=True)

        # combined text list ( twitter + news )
        text_list = []

        # TWITTER FEED
        twitter_data=[]
        # webscrapping
        r = requests.get(f"https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json")
        data = r.json()

        # defining function
        @st.cache
        def tweet_data():
            for msg in data['messages']:
                text = unicodedata.normalize( 'NFKC', msg['body'])
                if len(text) > 120:
                    continue

                timedata = datetime.datetime.strptime(msg['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                timedata.strftime("%m-%d-%Y %I:%M:%S &p")
                twitter_data.append([timedata,text])
                text_list.append(text)
        
        # calling 
        tweet_data()
        # creating a pandas dataframe
        # tdf = pd.DataFrame(twitter_data,columns=['time','text'])

        # NEWS
        news_data=[]
        # webscrapping
        url = f"https://finviz.com/quote.ashx?t={symbol}"
        req=Request(url=url,headers={'user-agent':'my-app'})
        response=urlopen(req)
        soup = BeautifulSoup(response,features="html.parser")
        news_table=soup.find(id='news-table')

        # defining function
        @st.cache
        def stock_news_data():
            for row in news_table.findAll('tr'):
                title = row.a.get_text()
                source = row.span.get_text()
                date_data = row.td.text.split(' ')

                if len(date_data) ==1:
                    time=date_data[0]
                else:
                    date=date_data[0]
                    time=date_data[1]

                news_data.append([date,time,title,source])
                text_list.append(title)

        # calling 
        stock_news_data()
        # creating a pandas dataframe
        # ndf = pd.DataFrame(news_data,columns=['time','text'])

        # SENTIMENT ANALYSIS 
        stock_sentiment_scores = bert_model.get_sentiment_score(text_list)
        print(stock_sentiment_scores)

        # company logo and  name
        col1,col2 = st.columns([2,20])
        col1.image(ticker.info['logo_url'])
        col2.markdown(f'<p style="font-family:Tahoma; font-size:30px;">{comp_name}</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-family:Tahoma; font-size:18px; font-weight:medium">{ticker.info["country"]} | {ticker.info["sector"]}</p>', unsafe_allow_html=True)

        comps=stock_sentiment_scores[0]
        pols=stock_sentiment_scores[1]

        # metrics
        st.markdown("---")
        col1, col2, col3, col4, col5 = st.columns([4,2,4,2,4])
        col1.metric("Recommendation Score",ticker.info['recommendationMean'] + comps)
        col3.metric("Sentiment Score", comps)
        col5.metric("Variance Score", pols)
        st.markdown("---")

        # printing data
        col1, col2, col3 = st.columns([8,2,8])

        # TWEETS
        col1.subheader("Twitter Feed")
        col1.markdown("""---""")
        # prinitng tweets
        for row in twitter_data:
            timedata=row[0]
            text=row[1]
            col1.markdown(f'<p style="color:#1ac49f; font-family:Tahoma; font-size:14px; ">{timedata}</p>', unsafe_allow_html=True)
            col1.markdown(f'<span style="word-wrap:break-word;">{text}</span>', unsafe_allow_html=True)
            col1.markdown("""---""")

        # NEWS
        col3.subheader("Latest News")
        col3.markdown("---")
        # prinitng news
        for row in news_data:
            date=row[0]
            time=row[1]
            title=row[2]
            source=row[3]
            col3.markdown(f'<p style="color:#1ac49f; font-family:Tahoma; font-size:14px; word-wrap:break-word;">{date}, {time} - {source}</p>', unsafe_allow_html=True)
            col3.markdown(f'<span style="word-wrap:break-word;">{title}</span>', unsafe_allow_html=True)
            col3.markdown("---")
            


# Twitter Feed
if(option == "Twitter Feed"):

    st.header("Famous Twitter Traders")
    list_of_traders = ['traderstewie',
            'the_chart_life',
            'canuck2usa',
            'sunrisetrader',
            'tmltrader']
    option = st.sidebar.selectbox("TRADER",list_of_traders)
    keyword = st.sidebar.text_input("SEARCH TRADER",'traderstewie')
    if keyword.isalpha() == False:
        st.sidebar.error("No special characters or spaces allowed!")
    else:
        # list_of_traders.append(keyword)
        option = keyword

    st.sidebar.markdown("<a href='#top' style='color:#1ac49f; font-family:Tahoma; font-size:14px; text-decoration: none;'>&#8227; Back to top </a>",unsafe_allow_html=True)

    user = api.get_user(screen_name=option)
    tweets = api.user_timeline(screen_name=option)

    # twitter trader profile pic and name
    st.markdown("---")
    col1, col2 = st.columns([2, 20])
    col1.image(user.profile_image_url)
    col2.subheader(option)
    st.markdown("---")

    for tweet in tweets:
        if '$' in tweet.text:
            words = tweet.text.split(' ')
            for word in words:
                if word.startswith('$') and word[1:].isalpha():
                    # loading animation
                    with st.spinner('loading...'):
                        # get data
                        symbol = word[1:]
                        timedata = tweet.created_at.strftime("%m-%d-%Y  %I:%M:%S %p")

                        # web scrapping
                        comp_name = get_comp_name(symbol)

                    # display data
                    st.markdown(f'<p style="font-family:Tahoma; font-size:30px;">{comp_name}</p>', unsafe_allow_html=True)
                    st.markdown(f'<p style="color:#1ac49f; font-family:Tahoma; font-size:14px;">{timedata}</p>', unsafe_allow_html=True)

                    st.write(tweet.text)
                    # image + finviz link
                    st.markdown(f"[![Foo](https://charts2.finviz.com/chart.ashx?t={symbol})](https://finviz.com/quote.ashx?t={symbol})")
                    st.markdown("""---""")

# Stockwits Feed
if(option == "Stocktwits Feed"):

    keyword=st.sidebar.text_input("COMPNAY NAME","microsoft")
    symbol = get_ticker(keyword)
    r = requests.get(f"https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json")
    data = r.json()

    # web scrapping
    comp_name = get_comp_name(symbol)

    # display data
    st.header(f"Latest Tweets - {comp_name}")
    st.markdown(" ")
    st.markdown("---")
    st.sidebar.markdown("<a href='#top' style='color:#1ac49f; font-family:Tahoma; font-size:14px; text-decoration: none;'>&#8227; Back to top </a>",unsafe_allow_html=True)

    for msg in data['messages']:

        col1, col2 = st.columns([2, 20])
        col1.image(msg['user']['avatar_url'])
        col2.subheader(msg['user']['username'])

        timedata = datetime.datetime.strptime(msg['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        timedata.strftime("%m-%d-%Y %I:%M:%S &p")
        st.markdown(f'<p style="color:#1ac49f; font-family:Tahoma; font-size:14px;">{timedata}</p>', unsafe_allow_html=True)

        st.write(msg['body'])
        st.markdown("""---""")
