import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
import os
from datetime import datetime, timedelta

# CSV 파일 경로
DATA_FILE = "gold_price_data.csv"

# 📌 데이터 로드 함수
@st.cache_data(ttl=3600)
def load_gold_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, parse_dates=["Date"])
        df = df.set_index("Date")
        if df.empty:
            df = fetch_gold_data("2004-01-01")  # 데이터가 비어 있을 경우 초기 데이터 로드
    else:
        df = fetch_gold_data("2004-01-01")
        df.to_csv(DATA_FILE)
    return df

# 📌 데이터 가져오기 함수
def fetch_gold_data(start_date):
    end_date = datetime.now().strftime('%Y-%m-%d')
    gold_data = yf.download('GC=F', start=start_date, end=end_date)
    df = gold_data[['Close']].reset_index()
    df.columns = ['Date', 'Close']
    df = df.set_index("Date")
    return df

# 📌 데이터 업데이트 함수
def update_gold_data():
    df = load_gold_data()
    
    if df.empty or df.index.max() is None:
        last_date = datetime.strptime("2004-01-01", "%Y-%m-%d").date()
    else:
        last_date = df.index.max().date()
    
    today = datetime.now().date()
    
    if last_date < today:
        new_data = fetch_gold_data(last_date + timedelta(days=1))
        updated_df = pd.concat([df, new_data])
        updated_df.to_csv(DATA_FILE)
        return updated_df
    return df

# 📌 데이터 로드 실행
df = update_gold_data()

# 📌 UI 구성
st.title("📊 실시간 금 가격 데이터 분석")
st.write("실시간으로 금 가격을 분석하고 시각화합니다.")

# 📌 데이터 개요
if not df.empty:
    st.write(f"데이터 기간: {df.index.min().date()} ~ {df.index.max().date()}")
    st.write(f"총 데이터 수: {len(df):,}일")
    st.write(f"최근 종가: ${df['Close'].iloc[-1]:,.2f}")
    
    # 📌 그래프 시각화
    fig = px.line(df, y='Close', title='금 가격 추이')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("데이터가 없습니다. 잠시 후 다시 시도하세요.")
