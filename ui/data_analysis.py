import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
import os

# 데이터 저장 경로
DATA_PATH = "data/XAU_gold_data.csv"

# 실시간 데이터 가져오기 및 저장
def fetch_gold_data():
    try:
        # 기존 데이터 로드
        if os.path.exists(DATA_PATH):
            try:
                existing_df = pd.read_csv(DATA_PATH, sep=';', index_col=0, parse_dates=True)
                existing_df.index = pd.to_datetime(existing_df.index)  # 인덱스를 날짜 형식으로 변환
            except Exception as e:
                st.error(f"⚠ 기존 데이터를 불러오는 중 오류 발생: {e}")
                existing_df = None
        else:
            existing_df = None

        # 최신 데이터 다운로드
        new_df = yf.download("GC=F", start="2004-01-01", progress=False)

        # 데이터 유효성 검사
        if new_df is None or new_df.empty:
            st.error("❌ 데이터를 가져올 수 없습니다.")
            return existing_df if existing_df is not None else None

        # 필요한 컬럼만 선택
        new_df = new_df[['Open', 'High', 'Low', 'Close']]
        new_df.reset_index(inplace=True)
        new_df.rename(columns={'Date': 'Date'}, inplace=True)
        new_df['Date'] = pd.to_datetime(new_df['Date'])
        new_df.set_index('Date', inplace=True)

        # 기존 데이터가 있는 경우 새로운 데이터만 추가
        if existing_df is not None:
            last_date = existing_df.index.max()

            # 새로운 데이터 중에서 기존 데이터 이후의 데이터만 선택
            new_data = new_df[new_df.index > last_date]

            if new_data.empty:
                st.info("✅ 데이터가 최신 상태입니다. 새로운 데이터가 없습니다.")
                return existing_df  # 기존 데이터 반환

            # 기존 데이터와 새로운 데이터 병합 (중복 방지)
            updated_df = pd.concat([existing_df, new_data]).drop_duplicates()
            st.success(f"📢 {len(new_data)}개의 새로운 데이터가 추가되었습니다.")
        else:
            updated_df = new_df  # 기존 데이터가 없으면 새로운 데이터 사용
            st.success("✅ 새 데이터가 다운로드되었습니다.")

        # 최신 데이터 저장
        updated_df.to_csv(DATA_PATH, sep=';', index=True)
        return updated_df
    except Exception as e:
        st.error(f"❌ 데이터 업데이트 중 오류 발생: {e}")
        return None

# 최신 데이터 로드
def load_latest_data():
    if os.path.exists(DATA_PATH):
        try:
            df = pd.read_csv(DATA_PATH, sep=';', index_col=0, parse_dates=True)

            # "Close" 컬럼이 없으면 fetch_gold_data() 실행
            if df.empty or "Close" not in df.columns:
                st.warning("⚠ 데이터가 유효하지 않습니다. 최신 데이터를 가져옵니다.")
                return fetch_gold_data()

            df.index = pd.to_datetime(df.index)  # 인덱스를 날짜 형식으로 변환
            return df
        except Exception as e:
            st.error(f"로컬 데이터를 불러오는 중 오류 발생: {e}")
            return fetch_gold_data()  # 오류 발생 시 새로 다운로드
    else:
        return fetch_gold_data()  # 파일이 없으면 새로 다운로드

# 🔥 EDA 실행 함수
def run_eda():
    st.title("📊 금 가격 데이터 분석")
    st.write("실시간 데이터를 기반으로 금 가격을 분석합니다.")

    df = load_latest_data()  # 최신 데이터 로드

    if df is None or df.empty:
        st.error("❌ 데이터가 없습니다. 다시 시도하세요.")
        return  # 이후 코드 실행 중지

    # 데이터 개요
    st.write("### 데이터 개요")
    st.write(f"📅 데이터 기간: {df.index.min().date()} ~ {df.index.max().date()}")
    st.write(f"📊 총 데이터 수: {len(df):,}일")

    # 💰 최근 종가가 존재하는지 확인 후 출력
    if 'Close' in df.columns and not df['Close'].empty:
        st.write(f"💰 최근 종가: ${df['Close'].iloc[-1]:,.2f}")
    else:
        st.warning("⚠ 최근 종가 데이터를 찾을 수 없습니다.")

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
