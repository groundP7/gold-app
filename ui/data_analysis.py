import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
from datetime import datetime

def fetch_gold_data(start_date="2004-01-01"):
    """Yahoo Finance에서 2004년부터 현재까지 금 가격 데이터를 가져와 DataFrame 반환"""
    end_date = datetime.now().strftime('%Y-%m-%d')  # 오늘 날짜까지 포함
    df = yf.download('GC=F', start=start_date, end=end_date, progress=False)

    if df.empty:
        print("⚠ 데이터를 가져오지 못했습니다. 빈 데이터프레임을 반환합니다.")
        return pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close'])

    df = df[['Open', 'High', 'Low', 'Close']].reset_index()
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close']

    df['Date'] = pd.to_datetime(df['Date'])  
    df.set_index("Date", inplace=True)
    
    return df

@st.cache_data(ttl=3600)  # 1시간마다 데이터 갱신
def load_data():
    df = fetch_gold_data()
    if df.empty:
        st.warning("⚠ 데이터를 가져올 수 없습니다. 다시 시도해 주세요.")
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    return df

def aggregate_data(df, freq):
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    return df.resample(freq).mean()

def run_eda():
    df = load_data()
    if df.empty:
        st.error("❌ 금 가격 데이터를 불러오는 데 실패했습니다.")
        return
    
    st.markdown("<p style='font-size:32px; font-weight:bold; color:#4B0082; text-align:center;'>📊 금 가격 데이터 분석</p>", unsafe_allow_html=True)
    
    # 데이터 개요 (카드 스타일)
    st.markdown("<p class='medium-font'>📌 데이터 개요</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='metric-card'><strong>📅 데이터 기간</strong><br>{df.index.min().date()} ~ {df.index.max().date()}</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><strong>📊 총 데이터 수</strong><br>{len(df):,}일</div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><strong>💰 최근 종가</strong><br>${df['Close'].iloc[-1]:,.2f}</div>", unsafe_allow_html=True)
    
    # 기간별 그래프
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

    # 🔥 통계 데이터 추가
    st.markdown("### 📊 금 가격 통계 요약")
    
    # 통계 요약 데이터 생성
    stats = df.describe()

    # 통계 데이터 설명 추가
    st.markdown("""
    - **평균 (mean)**: 해당 기간 동안 금 가격의 평균값  
    - **표준편차 (std)**: 금 가격 변동성 (값이 클수록 변동성이 큼)  
    - **최솟값 (min) / 최댓값 (max)**: 해당 기간 동안의 최저 및 최고 금 가격  
    - **25% / 50% (중앙값) / 75% 백분위수**: 데이터의 분포를 나타냄  
    """)

    # 숫자 포맷 적용 (소수점 2자리 & USD 표시)
    st.dataframe(stats.style.format("${:.2f}"), use_container_width=True)

    # 사용자 선택 날짜 범위
    st.markdown("### 📅 특정 기간 금 가격 데이터 조회")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("시작 날짜", min_value=df.index.min().date(), max_value=df.index.max().date(), value=df.index.min().date())
    with col2:
        end_date = st.date_input("종료 날짜", min_value=df.index.min().date(), max_value=df.index.max().date(), value=df.index.max().date())

    if start_date > end_date:
        st.error("❌ 시작 날짜는 종료 날짜보다 이전이어야 합니다.")
        return

    df_filtered = df.loc[start_date:end_date]

    if df_filtered.empty:
        st.warning("⚠ 선택한 기간에 대한 데이터가 없습니다.")
        return

    # 날짜 형식을 'YYYY-MM-DD'로 변환하여 시분초 제거
    df_filtered.index = df_filtered.index.strftime('%Y-%m-%d')

    # 가독성을 높이기 위한 스타일 적용
    st.dataframe(df_filtered.style.format({
        "Close": "${:.2f}",
        "Open": "${:.2f}",
        "High": "${:.2f}",
        "Low": "${:.2f}"
    }), use_container_width=True)

    # 선택한 기간 그래프
    st.markdown("### 📊 선택한 기간 금 가격 추이")
    st.text("금 가격 추이 그래프의 금액은 Close(종가)를 기준으로 그려집니다.")
    fig_filtered = px.line(df_filtered, y='Close', title=f'📈 {start_date} ~ {end_date} 금 가격 추이', color_discrete_sequence=["#FF4500"])
    fig_filtered.update_layout(xaxis_title="날짜", yaxis_title="가격 (USD)", template="plotly_dark")
    st.plotly_chart(fig_filtered, use_container_width=True)


    
if __name__ == "__main__":
    run_eda()
