import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# CSS를 사용하여 개별 요소들을 중앙 정렬
st.markdown(
    """
    <style>
    .reportview-container .main .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }
    .centered {
        display: flex;
        justify-content: center;
    }
    .st-emotion-cache-1v0mbdj {
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def run_eda():
    st.markdown("<h1 style='text-align: right; padding-right: 100px;'>📊 금 가격 데이터 분석</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>금 가격 데이터를 분석합니다</p>", unsafe_allow_html=True)

    # 데이터 로드 및 처리
    df = pd.read_csv("data/XAU_gold_data.csv", sep=";")
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    df = df.set_index("Date")

    # 데이터프레임 표시
    st.subheader("금 가격 데이터")
    
    # 데이터프레임 스타일링
    styled_df = df.style.set_properties(**{
        'background-color': 'lightyellow',
        'color': 'black',
        'border-color': 'black'
    }).highlight_max(color='lightgreen').format("{:.2f}")

    st.dataframe(styled_df, use_container_width=True)

    # 데이터 기간 정보 표시
    min_date = df.index.min()
    max_date = df.index.max()
    st.markdown(f"**데이터 기간:** {min_date.strftime('%Y-%m-%d')} ~ {max_date.strftime('%Y-%m-%d')}")
    st.markdown(f"**총 {(max_date - min_date).days + 1}일 동안의 금 가격 데이터**")

    # 통계 데이터 체크박스
    if st.checkbox("통계 데이터 보기"):
        st.write(df.describe().style.format("{:.2f}"))
    
    # 메트릭 표시
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("최근 종가", f"${df['Close'].iloc[-1]:.2f}")
    with col2:
        st.metric("평균 종가", f"${df['Close'].mean():.2f}")
    with col3:
        st.metric("최고 종가", f"${df['Close'].max():.2f}")

    # 그래프 생성 및 표시
    st.markdown("<h3 style='text-align: right; padding-right: 140px;'>Gold Closing Price Over Time</h3>", unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    df['Close'].plot(ax=ax)
    plt.xlabel("Date")
    plt.ylabel("Closing Price ($)")
    st.pyplot(fig)

    # 기간별 그래프 추가
    st.markdown("<h3 style='text-align: right; padding-right: 180px;'>기간별 금가격 추이</h3>", unsafe_allow_html=True)
    period = st.selectbox('기간 선택', ['일별', '월별', '분기별', '년별'])

    def create_gold_chart(data, period):
        if period == "일별":
            resampled_data = data
        elif period == "월별":
            resampled_data = data.resample('M').last()
        elif period == "분기별":
            resampled_data = data.resample('Q').last()
        else:  # 년별
            resampled_data = data.resample('Y').last()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=resampled_data.index, y=resampled_data['Close'], mode='lines'))
        fig.update_layout(
            xaxis_title='날짜',
            yaxis_title='가격 (USD)',
            annotations=[
                dict(
                    x=1,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    text=f'기간: {period}',
                    showarrow=False,
                    xanchor='right',
                    yanchor='bottom',
                    font=dict(size=12)
                )
            ]
        )
        return fig

    # 인덱스를 datetime으로 변환
    df.index = pd.to_datetime(df.index)

    # 그래프 생성 및 표시
    chart = create_gold_chart(df, period)
    st.plotly_chart(chart, use_container_width=True)

    # 사용자 지정 기간 선택
    st.markdown("<h3 style='text-align: right; padding-right: 180px;'>사용자 지정 기간 데이터</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("시작 날짜", min_value=df.index.min().date(), max_value=df.index.max().date(), value=df.index.min().date())
    with col2:
        end_date = st.date_input("종료 날짜", min_value=df.index.min().date(), max_value=df.index.max().date(), value=df.index.max().date())

    # 선택된 기간의 데이터 표시
    if start_date <= end_date:
        mask = (df.index.date >= start_date) & (df.index.date <= end_date)
        filtered_df = df.loc[mask].copy()
        filtered_df.index = filtered_df.index.date  # 인덱스를 date 객체로 변환
        if not filtered_df.empty:
            st.write(f"{start_date} 부터 {end_date} 까지의 데이터:")
            st.dataframe(filtered_df.style.format({
                "Close": "{:.2f}", 
                "Open": "{:.2f}", 
                "High": "{:.2f}", 
                "Low": "{:.2f}"
            }), use_container_width=True)
        else:
            st.write("선택한 기간에 해당하는 데이터가 없습니다.")
    else:
        st.write("시작 날짜는 종료 날짜보다 앞서야 합니다.")

if __name__ == "__main__":
    run_eda()
