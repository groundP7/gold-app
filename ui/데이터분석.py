import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
import os
from datetime import datetime, timedelta

# CSS 스타일 적용
st.markdown("""
    <style>
        .big-font { font-size: 32px !important; font-weight: bold; color: #4B0082; text-align: center; }
        .medium-font { font-size: 24px !important; color: #8B4513; text-align: center; }
        .small-font { font-size: 18px !important; color: #4B0082; }
        .metric-card { background-color: rgba(255, 255, 255, 0.8); padding: 15px; border-radius: 10px; 
                       text-align: center; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

# CSV 파일 경로
DATA_FILE = "gold_price_data.csv"

# 📌 데이터 로드 및 실시간 업데이트 함수
@st.cache_data(ttl=3600)  # 1시간마다 새로고침
def load_gold_data():
    # 기존 데이터 불러오기 (파일이 있으면)
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, parse_dates=["Date"])
        df = df.set_index("Date")
    else:
        # 처음 실행 시 2004년 데이터부터 로드
        df = fetch_gold_data("2004-01-01")
        df.to_csv(DATA_FILE)  # CSV 파일로 저장
    return df

def fetch_gold_data(start_date):
    """Yahoo Finance에서 금 가격 데이터 가져오기"""
    end_date = datetime.now().strftime('%Y-%m-%d')
    gold_data = yf.download('GC=F', start=start_date, end=end_date)  # 'GC=F'는 금 선물 코드
    df = gold_data[['Close']].reset_index()
    df.columns = ['Date', 'Close']
    return df

def update_gold_data():
    """실시간 데이터 업데이트 및 저장"""
    df = load_gold_data()
    last_date = df.index.max().date()
    today = datetime.now().date()

    if last_date < today:
        new_data = fetch_gold_data(last_date + timedelta(days=1))
        new_data = new_data.set_index("Date")

        # 데이터 병합 및 저장
        updated_df = pd.concat([df, new_data])
        updated_df.to_csv(DATA_FILE)
        return updated_df
    return df

# 📌 데이터 로드 및 업데이트 실행
df = update_gold_data()

# 📌 UI 구성
st.markdown("<p class='big-font'>📊 실시간 금 가격 데이터 분석</p>", unsafe_allow_html=True)
st.markdown("<p class='small-font' style='text-align: center;'>실시간으로 금 가격을 분석하고 시각화합니다.</p>", unsafe_allow_html=True)

# 데이터 개요
st.markdown("<p class='medium-font'>📌 데이터 개요</p>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"<div class='metric-card'><strong>📅 데이터 기간</strong><br>{df.index.min().date()} ~ {df.index.max().date()}</div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='metric-card'><strong>📊 총 데이터 수</strong><br>{len(df):,}일</div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='metric-card'><strong>💰 최근 종가</strong><br>${df['Close'].iloc[-1]:,.2f}</div>", unsafe_allow_html=True)

# 데이터프레임 표시
with st.expander("📂 금 가격 데이터 보기"):
    st.dataframe(df.style.highlight_max(axis=0).format({"Close": "${:.2f}"}))

# 통계 데이터
if st.checkbox("📊 통계 데이터 보기"):
    st.write(df.describe().style.format("{:.2f}"))

# 📌 그래프 시각화
st.markdown("<p class='medium-font'>📈 금 가격 추이</p>", unsafe_allow_html=True)
fig = px.line(df, y='Close', title='📈 Gold Closing Price Over Time', color_discrete_sequence=["#4B0082"])
fig.update_layout(xaxis_title="Date", yaxis_title="Closing Price ($)", template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# 📌 기간별 분석
st.markdown("<p class='medium-font'>⏳ 기간별 금 가격 추이</p>", unsafe_allow_html=True)
period = st.selectbox('📅 기간 선택', ['일별', '월별', '분기별', '년별'])

def create_gold_chart(data, period):
    if period == "일별":
        resampled_data = data
    elif period == "월별":
        resampled_data = data.resample('M').last()
    elif period == "분기별":
        resampled_data = data.resample('Q').last()
    else:  # 년별
        resampled_data = data.resample('Y').last()

    fig = px.line(resampled_data, y='Close', title=f'📈 {period} 금 가격 추이', color_discrete_sequence=["#8B4513"])
    fig.update_layout(xaxis_title="날짜", yaxis_title="가격 (USD)", template="plotly_dark")
    return fig

chart = create_gold_chart(df, period)
st.plotly_chart(chart, use_container_width=True)

# 📌 사용자 지정 기간 데이터
st.markdown("<p class='medium-font'>📆 사용자 지정 기간 데이터</p>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("🟢 시작 날짜", df.index.min().date())
with col2:
    end_date = st.date_input("🔴 종료 날짜", df.index.max().date())

if start_date <= end_date:
    mask = (df.index.date >= start_date) & (df.index.date <= end_date)
    filtered_df = df.loc[mask]

    if not filtered_df.empty:
        st.write(f"📅 {start_date} 부터 {end_date} 까지의 데이터:")
        st.dataframe(filtered_df.style.format({"Close": "${:.2f}"}))

        # 선택된 기간의 그래프
        fig = px.line(filtered_df, y='Close', title='📈 선택 기간 금 가격 추이', color_discrete_sequence=["#D2691E"])
        fig.update_layout(xaxis_title="날짜", yaxis_title="가격 (USD)", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠ 선택한 기간에 해당하는 데이터가 없습니다.")
else:
    st.error("❌ 시작 날짜는 종료 날짜보다 앞서야 합니다.")
