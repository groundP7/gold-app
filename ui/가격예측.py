import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import pickle
from datetime import datetime, timedelta
import requests

# 모델 로딩 함수
def load_or_create_model():
    model_path = 'model/gold_price_model.pkl'  # 모델 경로를 확인
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        return model
    except (FileNotFoundError, pickle.UnpicklingError) as e:
        st.error(f"모델 로딩 중 오류 발생: {str(e)}")
        st.error("모델 파일을 확인해주세요.")
        return None

# 환율 정보 가져오는 함수
def get_exchange_rate():
    url = "https://v6.exchangerate-api.com/v6/553ac17cfdac2697c92cd6a8/latest/USD"
    response = requests.get(url)
    data = response.json()
    return data['conversion_rates']['KRW']

def run_ml():
    # 타이틀과 설명
    st.markdown("<p class='big-font'>🏅 금 가격 예측기</p>", unsafe_allow_html=True)
    st.markdown("고급 머신러닝을 사용하여 미래의 금 가격을 예측해보세요!")

    # 모델 로드
    model = load_or_create_model()
    if model is None:
        st.error("모델을 로드할 수 없습니다. 프로그램을 종료합니다.")
        return

    # 두 개의 열 생성
    col1, col2 = st.columns([2, 1])

    with col1:
        # 사용자로부터 시작 날짜와 끝 날짜 또는 하나의 날짜 입력 받기
        date_option = st.radio("날짜 선택 방식", ["하나의 날짜 선택", "시작과 끝 날짜 선택"])

        if date_option == "하나의 날짜 선택":
            prediction_date = st.date_input("예측할 날짜를 선택하세요", min_value=datetime.now().date() + timedelta(days=1))
            start_date = None
            end_date = None
        else:
            start_date = st.date_input("시작 날짜를 선택하세요", min_value=datetime.now().date() + timedelta(days=1))
            end_date = st.date_input("끝 날짜를 선택하세요", min_value=start_date)
            prediction_date = None  # 예측 날짜는 선택하지 않음

    with col2:
        # 예측 버튼
        predict_button = st.button("🔮 금 가격 예측하기")

    if predict_button:
        if date_option == "하나의 날짜 선택":
            # 예측할 날짜에 대한 특성 계산
            year = prediction_date.year
            month = prediction_date.month
            day = prediction_date.day
            weekday = prediction_date.weekday()  # 0: Monday, 1: Tuesday, ..., 6: Sunday
            quarter = (month - 1) // 3 + 1  # 1 ~ 4 분기
            price_change = 0  # 가격 변화 (기본값 0, 실제 데이터에 맞게 설정 필요)
            volume_change = 0  # 거래량 변화 (기본값 0, 실제 데이터에 맞게 설정 필요)

            # 예측할 데이터를 DataFrame으로 생성
            future = pd.DataFrame({
                'Year': [year],
                'Month': [month],
                'Day': [day],
                'Weekday': [weekday],
                'Quarter': [quarter],
                'Price_Change': [price_change],
                'Volume_Change': [volume_change]
            })

            # 예측 수행 (RandomForest 모델을 사용)
            rf_pred = model.predict(future)  # RandomForest 모델 사용

            # 예측 결과 표시 (XAU 가격으로 가정)
            predicted_price_xau = rf_pred[0] * 10  # 예측값에 10배 곱하기 (온스 기준으로 조정)
            predicted_price_gram = predicted_price_xau / 31.1034768  # XAU에서 그램으로 변환

            # 환율 정보 가져오기
            exchange_rate = get_exchange_rate()

            # 예측 결과를 카드 형식으로 표시
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='card-header'>예측된 금 가격 (XAU/온스)</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card-body'>${predicted_price_xau:.2f}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='card-header'>예측된 금 가격 (USD/그램)</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card-body'>${predicted_price_gram:.2f}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='card-header'>예측된 금 가격 (KRW/그램)</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card-body'>₩{predicted_price_gram * exchange_rate:,.0f}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # 환율 정보 표시
            st.markdown(f"*적용 환율: $1 = ₩{exchange_rate:,.2f}*")

            # 예측 결과 시각화 (XAU 기준으로 수정)
            fig = go.Figure()

            # 예측 라인 (현재 예측값)
            fig.add_trace(go.Scatter(
                x=[prediction_date], y=[predicted_price_xau],
                mode='lines+markers', name='예측 가격 (현재)',  # lines+markers 추가
                marker=dict(size=15, color='gold', symbol='star')
            ))

            # 그래프 레이아웃
            fig.update_layout(
                title='금 가격 예측 (XAU/온스)',
                xaxis_title='날짜',
                yaxis_title='가격 (XAU/온스)',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    tickformat='%Y-%m-%d',
                    dtick='D1'
                )
            )

            st.plotly_chart(fig, use_container_width=True)

        else:  # 시작 날짜와 끝 날짜 선택한 경우
            st.write(f"예측할 기간: {start_date} ~ {end_date}")

            # 기간 동안 예측을 위한 날짜 범위 생성
            date_range = pd.date_range(start=start_date, end=end_date)

            # 예측 값 저장을 위한 리스트
            predicted_prices = []

            for prediction_date in date_range:
                # 예측할 날짜에 대한 특성 계산
                year = prediction_date.year
                month = prediction_date.month
                day = prediction_date.day
                weekday = prediction_date.weekday()  # 0: Monday, 1: Tuesday, ..., 6: Sunday
                quarter = (month - 1) // 3 + 1  # 1 ~ 4 분기
                price_change = 0  # 가격 변화 (기본값 0, 실제 데이터에 맞게 설정 필요)
                volume_change = 0  # 거래량 변화 (기본값 0, 실제 데이터에 맞게 설정 필요)

                # 예측할 데이터를 DataFrame으로 생성
                future = pd.DataFrame({
                    'Year': [year],
                    'Month': [month],
                    'Day': [day],
                    'Weekday': [weekday],
                    'Quarter': [quarter],
                    'Price_Change': [price_change],
                    'Volume_Change': [volume_change]
                })

                # 예측 수행 (RandomForest 모델을 사용)
                rf_pred = model.predict(future)  # RandomForest 모델 사용

                # 예측 결과 표시 (XAU 가격으로 가정)
                predicted_price_xau = rf_pred[0] * 10  # 예측값에 10배 곱하기 (온스 기준으로 조정)
                predicted_price_gram = predicted_price_xau / 31.1034768  # XAU에서 그램으로 변환

                # 예측된 가격을 리스트에 저장
                predicted_prices.append((prediction_date, predicted_price_xau))

            # 예측된 값들을 그래프에 추가
            fig = go.Figure()

            # 날짜와 예측된 가격 리스트를 unpack하여 그래프에 추가
            dates, prices = zip(*predicted_prices)

            # 예측값을 그래프에 추가 (선 연결)
            fig.add_trace(go.Scatter(
                x=dates, y=prices,
                mode='lines+markers',  # lines+markers로 점과 선을 동시에 표시
                name='예측 가격 (선 연결)',
                marker=dict(size=8, color='gold')
            ))

            # 그래프 레이아웃
            fig.update_layout(
                title='금 가격 예측 (XAU/온스)',
                xaxis_title='날짜',
                yaxis_title='가격 (XAU/온스)',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    tickformat='%Y-%m-%d',
                    dtick='D1'
                )
            )

            st.plotly_chart(fig, use_container_width=True)

        # 추가 정보
        st.info("주의사항: AI 모델은 과거 데이터를 기반으로 예측하므로, 예상치 못한 사건이나 급격한 시장 변화를 반영하지 못할 수 있습니다")

if __name__ == "__main__":
    run_ml()
