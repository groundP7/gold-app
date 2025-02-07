import yfinance as yf
import pandas as pd
import os
import schedule
import time
import streamlit as st
import plotly.express as px

# CSV 저장 경로
CSV_FILE = "gold_prices.csv"

# 금 가격 데이터 가져오기
def fetch_gold_price(start_date="2004-01-01"):
    gold = yf.Ticker("GC=F")  # 금 선물 티커
    data = gold.history(period="1d", start=start_date, auto_adjust=True)
    return data[["Close"]].reset_index()

# 기존 데이터 불러오기
def load_existing_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE, parse_dates=["Date"])
    return pd.DataFrame(columns=["Date", "Close"])

# 데이터 병합 및 저장
def update_gold_data():
    print("최신 금 가격 데이터 업데이트 중...")
    
    existing_data = load_existing_data()
    
    if existing_data.empty:
        start_date = "2004-01-01"
    else:
        last_date = existing_data["Date"].max().strftime("%Y-%m-%d")
        start_date = last_date  # 마지막 날짜부터 새 데이터 가져오기

    new_data = fetch_gold_price(start_date)
    
    if not new_data.empty:
        updated_data = pd.concat([existing_data, new_data]).drop_duplicates(subset=["Date"]).reset_index(drop=True)
        updated_data.to_csv(CSV_FILE, index=False)
        print(f"{len(new_data)}개의 새로운 데이터가 추가되었습니다.")
    else:
        print("새로운 데이터가 없습니다.")

# 매일 자동 업데이트 (스케줄링)
schedule.every().day.at("00:10").do(update_gold_data)  # 매일 00:10에 실행

# Streamlit 앱 실행
def run_streamlit():
    st.title("금 가격 데이터 분석")
    st.markdown("금 가격 데이터의 통계 및 시각화 결과를 확인하세요.")

    # CSV 데이터 불러오기
    @st.cache_data
    def load_data():
        if not os.path.exists(CSV_FILE):
            st.error("데이터 파일이 없습니다. 먼저 데이터를 업데이트하세요!")
            return None
        df = pd.read_csv(CSV_FILE, parse_dates=["Date"])
        df.set_index("Date", inplace=True)
        return df

    df = load_data()

    # 데이터가 없으면 실행 중지
    if df is None:
        st.stop()

    # 데이터 개요
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("데이터 기간", f"{df.index.min().date()} ~ {df.index.max().date()}")
    with col2:
        st.metric("총 데이터 수", f"{len(df):,}일")
    with col3:
        st.metric("최근 종가", f"${df['Close'].iloc[-1]:,.2f}")

    # 데이터 요약 (통계)
    with st.expander("금 가격 데이터 보기"):
        st.dataframe(df.style.format({"Close": "${:.2f}"}))

    if st.checkbox("통계 데이터 보기"):
        st.write(df.describe().style.format("{:.2f}"))

    # 전체 데이터 그래프
    st.subheader("금 가격 추이")
    fig = px.line(df, y="Close", title="금 가격 변동", color_discrete_sequence=["#4B0082"])
    fig.update_layout(xaxis_title="날짜", yaxis_title="가격 ($)", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # 기간별 데이터 그래프
    st.subheader("기간별 금 가격 추이")
    period = st.selectbox("기간 선택", ["일별", "월별", "분기별", "년별"])

    def create_gold_chart(data, period):
        if period == "일별":
            resampled_data = data
        elif period == "월별":
            resampled_data = data.resample("M").last()
        elif period == "분기별":
            resampled_data = data.resample("Q").last()
        else:  # 년별
            resampled_data = data.resample("Y").last()
        
        fig = px.line(resampled_data, y="Close", title=f"{period} 금 가격 추이", color_discrete_sequence=["#8B4513"])
        fig.update_layout(xaxis_title="날짜", yaxis_title="가격 ($)", template="plotly_dark")
        return fig

    st.plotly_chart(create_gold_chart(df, period), use_container_width=True)

    # 사용자 지정 기간 선택
    st.subheader("사용자 지정 기간 데이터")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("시작 날짜", min_value=df.index.min().date(), max_value=df.index.max().date(), value=df.index.min().date())
    with col2:
        end_date = st.date_input("종료 날짜", min_value=df.index.min().date(), max_value=df.index.max().date(), value=df.index.max().date())

    if start_date <= end_date:
        mask = (df.index.date >= start_date) & (df.index.date <= end_date)
        filtered_df = df.loc[mask]
        if not filtered_df.empty:
            st.dataframe(filtered_df.style.format({"Close": "${:.2f}"}))
            fig = px.line(filtered_df, y="Close", title="선택 기간 금 가격 추이", color_discrete_sequence=["#D2691E"])
            fig.update_layout(xaxis_title="날짜", yaxis_title="가격 ($)", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("선택한 기간에 해당하는 데이터가 없습니다.")
    else:
        st.error("시작 날짜는 종료 날짜보다 앞서야 합니다.")

if __name__ == "__main__":
    update_gold_data()  # 실행 시 즉시 업데이트

    # Streamlit 실행
    import threading

    def run_streamlit_app():
        os.system("streamlit run gold_analysis.py")

    thread = threading.Thread(target=run_streamlit_app)
    thread.start()

    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 체크
