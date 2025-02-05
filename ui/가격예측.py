import streamlit as st
import pandas as pd
import pickle
import requests
from sklearn.linear_model import LinearRegression

# 환율 정보를 받아오는 함수 (XAU -> KRW)
def get_exchange_rate():
    try:
        # 여기에 자신의 API 키를 입력하세요.
        api_key = "553ac17cfdac2697c92cd6a8"  # 실제 API 키로 교체
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/XAU/KRW"
        response = requests.get(url)
        
        # 상태 코드가 200이면 정상적으로 응답 받은 것
        if response.status_code == 200:
            data = response.json()
            if data['result'] == 'success':
                return data['conversion_rate']  # XAU to KRW 환율 값
            else:
                st.error(f"API 오류: {data['error-type']}")
                return None
        else:
            st.error(f"API 응답 오류. 상태 코드: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"환율 API 요청에 실패했습니다: {str(e)}")
        return None

# 모델 로드 함수
def load_model():
    try:
        with open('model/linear_model.pkl', 'rb') as file:
            model = pickle.load(file)
        return model
    except FileNotFoundError:
        st.error("모델 파일을 찾을 수 없습니다.")
        return None

# 웹 애플리케이션의 메인 함수
def run_ml():
    # HTML/CSS 스타일로 타이틀을 우측 정렬하고, 배경과 폰트 꾸미기
    st.markdown("""
        <style>
            .title {
                text-align: right;
                font-size: 40px;
                font-weight: bold;
                color: #2a4d77;
            }
            .subheader {
                font-size: 25px;
                color: #3c8d99;
            }
            .stButton>button {
                background-color: #0078d4;
                color: white;
                font-size: 18px;
                border-radius: 10px;
                padding: 12px 30px;
                border: none;
                cursor: pointer;
            }
            .stButton>button:hover {
                background-color: #005fa3;
            }
            .stInput>div>input {
                padding: 8px;
                font-size: 18px;
                border-radius: 8px;
                border: 2px solid #ccc;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # 타이틀 우측 정렬
    st.markdown("<h1 style='text-align: right; padding-right: 170px;'>예상 다음날 종가</h1>", unsafe_allow_html=True)

    # 모델 로드
    model = load_model()
    if model is None:
        return

    # 사용자 입력을 받습니다.
    st.subheader("금 가격 정보 입력")

    open_price = st.number_input("시가", value=1800.0, step=0.1)
    high_price = st.number_input("고가", value=1810.0, step=0.1)
    low_price = st.number_input("저가", value=1790.0, step=0.1)
    close_price = st.number_input("종가", value=1805.0, step=0.1)
    volume = st.number_input("거래량", value=10000, step=100)

    if st.button("예측하기"):
        # 사용자가 입력한 값을 DataFrame으로 변환
        input_data = pd.DataFrame({
            'Open': [open_price],
            'High': [high_price],
            'Low': [low_price],
            'Close': [close_price],
            'Volume': [volume]
        })

        # 예측
        try:
            # 예측하기
            predicted_value = model.predict(input_data[['Open', 'High', 'Low', 'Volume']])[0]

            # XAU를 원화로 변환
            exchange_rate = get_exchange_rate()
            if exchange_rate is not None:
                predicted_value_krw = predicted_value * exchange_rate  # 예측값을 원화로 변환
                st.success(f"예측된 다음 날 종가 (XAU): {predicted_value:.2f} XAU")
                st.success(f"예측된 다음 날 종가 (KRW): {predicted_value_krw:.2f} 원")
            else:
                st.error("환율 정보를 가져올 수 없어 원화 변환에 실패했습니다.")

        except Exception as e:
            st.error(f"예측 중 오류가 발생했습니다: {str(e)}")

# 앱 실행
if __name__ == "__main__":
    run_ml()
