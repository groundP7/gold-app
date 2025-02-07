import streamlit as st
import pandas as pd
import plotly.express as px

# CSS 스타일링 개선
st.markdown("""
    <style>
        .big-font {
            font-size: 32px !important;
            font-weight: bold;
            color: #4B0082;
            text-align: center;
        }
        .medium-font {
            font-size: 24px !important;
            color: #8B4513;
            text-align: center;
        }
        .small-font {
            font-size: 18px !important;
            color: #4B0082;
        }
        .metric-card {
            background-color: rgba(255, 255, 255, 0.8);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

def run_eda():
    # 헤더
    st.markdown("<p class='big-font'>📊 금 가격 데이터 분석</p>", unsafe_allow_html=True)
    st.markdown("<p class='small-font' style='text-align: center;'>금 가격 데이터를 분석하고 시각화합니다</p>", unsafe_allow_html=True)

    # 데이터 로드 및 처리
    @st.cache_data
    def load_data():
        try:
            df = pd.read_csv("data/XAU_gold_data.csv", sep=";")
            if df.empty:
                return None  # 데이터가 없을 경우 None 반환
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.set_index("Date")
            return df
        except Exception as e:
            st.error(f"데이터를 로드하는 중 오류 발생: {e}")
            return None

    df = load_data()

    # 데이터가 없을 경우 처리
    if df is None or df.empty:
        st.error("❌ 데이터가 없습니다. CSV 파일을 확인하세요.")
        return  # 함수 종료

    # 데이터 개요 (카드 스타일)
    st.markdown("<p class='medium-font'>📌 데이터 개요</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        min_date = df.index.min().date() if not df.empty else "데이터 없음"
        st.markdown(f"<div class='metric-card'><strong>📅 데이터 기간</strong><br>{min_date} ~ {df.index.max().date()}</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><strong>📊 총 데이터 수</strong><br>{len(df):,}일</div>", unsafe_allow_html=True)
    with col3:
        recent_close = df['Close'].iloc[-1] if not df.empty else "N/A"
        st.markdown(f"<div class='metric-card'><strong>💰 최근 종가</strong><br>${recent_close:,.2f}</div>", unsafe_allow_html=True)

    # 데이터프레임 표시
    with st.expander("📂 금 가격 데이터 보기"):
        st.dataframe(df.style.highlight_max(axis=0).format({"Close": "${:.2f}", "Open": "${:.2f}", "High": "${:.2f}", "Low": "${:.2f}"}))

    # 통계 데이터
    if st.checkbox("📊 통계 데이터 보기"):
        st.write(df.describe().style.format("{:.2f}"))

    # 📈 금 가격 추이 그래프
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
        start_date = st.date_input("🟢 시작 날짜", df.index.min().date() if not df.empty else None)
    with col2:
        end_date = st.date_input("🔴 종료 날짜", df.index.max().date() if not df.empty else None)

    if df.empty:
        st.warning("⚠ 데이터가 없으므로 기간 선택이 불가능합니다.")
        return

    if start_date and end_date:
        if start_date <= end_date:
            mask = (df.index.date >= start_date) & (df.index.date <= end_date)
            filtered_df = df.loc[mask]

            if not filtered_df.empty:
                st.write(f"📅 {start_date} 부터 {end_date} 까지의 데이터:")
                st.dataframe(filtered_df.style.format({"Close": "${:.2f}", "Open": "${:.2f}", "High": "${:.2f}", "Low": "${:.2f}"}))

                # 선택된 기간의 그래프
                fig = px.line(filtered_df, y='Close', title='📈 선택 기간 금 가격 추이', color_discrete_sequence=["#D2691E"])
                fig.update_layout(xaxis_title="날짜", yaxis_title="가격 (USD)", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠ 선택한 기간에 해당하는 데이터가 없습니다.")
        else:
            st.error("❌ 시작 날짜는 종료 날짜보다 앞서야 합니다.")

if __name__ == "__main__":
    run_eda()
