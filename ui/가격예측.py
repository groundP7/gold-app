import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import joblib  # ARIMA 모델 로드용
from datetime import datetime, timedelta
import requests
import io  # 파일 저장을 위한 라이브러리

# 1️⃣ ARIMA 모델 로드 함수
def load_arima_model():
    model_path = 'model/gold_price_arima.pkl'  # 새로운 모델 경로 확인
    try:
        model = joblib.load(model_path)
        return model
    except (FileNotFoundError, joblib.externals.loky.process_executor.TerminatedWorkerError) as e:
        st.error(f"모델 로딩 중 오류 발생: {str(e)}")
        st.error("모델 파일을 확인해주세요.")
        return None

# 2️⃣ 환율 정보 가져오는 함수
def get_exchange_rate():
    url = "https://v6.exchangerate-api.com/v6/553ac17cfdac2697c92cd6a8/latest/USD"
    response = requests.get(url)
    data = response.json()
    return data['conversion_rates']['KRW']

# 3️⃣ 예측 실행 함수
def run_ml():
    st.markdown("<p class='big-font'>🏅 금 가격 예측기 (ARIMA 모델 적용)</p>", unsafe_allow_html=True)
    st.markdown("고급 ARIMA 모델을 사용하여 미래의 금 가격을 예측해보세요! 📈")

    # 모델 로드
    model = load_arima_model()
    if model is None:
        st.error("모델을 로드할 수 없습니다. 프로그램을 종료합니다.")
        return

    # 4️⃣ 날짜 선택 방식
    date_option = st.radio("날짜 선택 방식", ["하나의 날짜 선택", "시작과 끝 날짜 선택"])

    if date_option == "하나의 날짜 선택":
        prediction_date = st.date_input("예측할 날짜를 선택하세요", min_value=datetime.today().date() + timedelta(days=1))
        start_date, end_date = None, None
    else:
        start_date = st.date_input("시작 날짜를 선택하세요", min_value=datetime.today().date() + timedelta(days=1))
        end_date = st.date_input("끝 날짜를 선택하세요", min_value=start_date)
        prediction_date = None

    # 예측 버튼
    predict_button = st.button("🔮 금 가격 예측하기")

    if predict_button:
        # 5️⃣ 예측 실행
        if date_option == "하나의 날짜 선택":
            days_to_predict = (prediction_date - datetime.today().date()).days
            forecast_values = model.forecast(steps=days_to_predict).tolist()
            forecast_dates = [prediction_date]
            predicted_prices = [forecast_values[-1]]
        else:
            days_to_predict = (end_date - datetime.today().date()).days
            forecast_values = model.forecast(steps=days_to_predict).tolist()
            forecast_dates = pd.date_range(start=start_date, end=end_date)
            predicted_prices = forecast_values[-len(forecast_dates):]

        # 6️⃣ 환율 정보 가져오기
        exchange_rate = get_exchange_rate()

        # 7️⃣ 예측 결과 데이터프레임 생성
        df_result = pd.DataFrame({
            "날짜": forecast_dates,
            "예측 금 가격 (XAU/온스)": predicted_prices,
            "예측 금 가격 (KRW/그램)": [(price / 31.1035) * exchange_rate for price in predicted_prices]
        })

        # 🔹 날짜 형식 변환 후 문자열로 변환 (YYYY-MM-DD)
        df_result["날짜"] = pd.to_datetime(df_result["날짜"]).dt.strftime("%Y-%m-%d")

        # 🔹 XAU/온스 값 소수점 2자리까지 반올림
        df_result["예측 금 가격 (XAU/온스)"] = df_result["예측 금 가격 (XAU/온스)"].round(2)

        # 🔹 한화(KRW) 가격을 3자리마다 콤마 추가한 문자열로 변환
        df_result["예측 금 가격 (KRW/그램)"] = df_result["예측 금 가격 (KRW/그램)"].apply(lambda x: f"{x:,.0f}")

        # 9️⃣ 예측 결과 출력
        st.subheader("📊 예측 결과")
        st.dataframe(df_result)

        # 🔟 시각화
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_result["날짜"],
            y=df_result["예측 금 가격 (XAU/온스)"],
            mode='lines+markers',
            name='예측 금 가격',
            marker=dict(size=8, color='gold')
        ))

        fig.update_layout(
            title="📉 금 가격 예측 (XAU/온스)",
            xaxis_title="날짜",
            yaxis_title="예측 금 가격 (XAU/온스)",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )

        st.plotly_chart(fig, use_container_width=True)

        # 11️⃣ 데이터 다운로드 기능 추가
        csv_data = df_result.to_csv(index=False, encoding="utf-8-sig")  # 한글 깨짐 방지
        csv_file = io.BytesIO(csv_data.encode("utf-8-sig"))  # 스트림 데이터로 변환

        st.download_button(
            label="📥 예측 결과 다운로드 (CSV)",
            data=csv_file,
            file_name=f"gold_price_prediction_{datetime.today().date()}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    run_ml()
