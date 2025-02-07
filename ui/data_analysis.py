import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
import os

# 데이터 저장 경로
DATA_PATH = "data/XAU_gold_data.csv"

# 실시간 데이터 가져오기 및 저장
@st.cache_data
def fetch_gold_data():
    try:
        df = yf.download("GC=F", start="2004-01-01", progress=False)
        df = df[['Open', 'High', 'Low', 'Close']]
        df.reset_index(inplace=True)
        df.rename(columns={'Date': 'Date'}, inplace=True)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        df.to_csv(DATA_PATH, sep=';', index=True)
        return df
    except Exception as e:
        st.error(f"데이터를 가져오는 중 오류 발생: {e}")
        return None

# 로컬 데이터 로드
def load_local_data():
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH, sep=';', parse_dates=['Date'], index_col='Date')
        return df
    return fetch_gold_data()

# 🔥 **run_eda 함수 추가**
def run_eda():
    st.title("📊 금 가격 데이터 분석")
    st.write("실시간 데이터를 기반으로 금 가격을 분석합니다.")

    df = load_local_data()

    if df is None or df.empty:
        st.error("❌ 데이터가 없습니다. 다시 시도하세요.")
    else:
        # 데이터 개요
        st.write("### 데이터 개요")
        st.write(f"📅 데이터 기간: {df.index.min().date()} ~ {df.index.max().date()}")
        st.write(f"📊 총 데이터 수: {len(df):,}일")
        st.write(f"💰 최근 종가: ${df['Close'].iloc[-1]:,.2f}")

        # 데이터프레임 표시
        with st.expander("📂 금 가격 데이터 보기"):
            st.dataframe(df.style.highlight_max(axis=0))

        # 시각화
        st.write("### 📈 금 가격 추이")
        fig = px.line(df, y='Close', title='📈 Gold Closing Price Over Time', color_discrete_sequence=["#4B0082"])
        fig.update_layout(xaxis_title="Date", yaxis_title="Closing Price ($)", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        # 사용자 지정 기간 선택
        st.write("### 📆 사용자 지정 기간 데이터")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("🟢 시작 날짜", df.index.min().date())
        with col2:
            end_date = st.date_input("🔴 종료 날짜", df.index.max().date())

        if start_date <= end_date:
            mask = (df.index.date >= start_date) & (df.index.date <= end_date)
            filtered_df = df.loc[mask]
            if not filtered_df.empty:
                st.dataframe(filtered_df)
                fig = px.line(filtered_df, y='Close', title='📈 선택 기간 금 가격 추이', color_discrete_sequence=["#D2691E"])
                fig.update_layout(xaxis_title="날짜", yaxis_title="가격 (USD)", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠ 선택한 기간에 해당하는 데이터가 없습니다.")
        else:
            st.error("❌ 시작 날짜는 종료 날짜보다 앞서야 합니다.")
