# Gold Price Prediction App

## 📌 프로젝트 개요

이 프로젝트는 **금 가격을 예측**하는 머신러닝 애플리케이션입니다.
Streamlit을 사용하여 직관적인 UI를 제공하며,
RandomForest 모델을 활용하여 금 가격을 예측합니다.&#x20;

## 🛠 기술 스택

- **Python**
- **Streamlit**&#x20;
- **Scikit-learn**&#x20;
- **Facebook Prophet**&#x20;
- **Plotly**&#x20;
- **Pandas, NumPy** 
- **yfinance** 
- **ExchangeRate-API**&#x20;

## 📂 프로젝트 구성

```
📦 gold-app-main
📂 data                # 데이터 파일 저장
📂 model               # 머신러닝 모델 저장 (pkl 파일)
📂 ui                  # Streamlit UI 구성 파일
📝 app.py                 # 메인 실행 파일
📝 gold.ipynb             # 데이터 분석 및 모델 학습 노트북
📝 requirements.txt       # 필수 패키지 목록
📝 README.md              # 프로젝트 설명 파일
```

## 🛠 프로젝트 프로그램 설치 방법

```bash
# 가상 환경 생성 (선택 사항)
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# 필수 패키지 설치
pip install -r requirements.txt

# 애플리케이션 실행
streamlit run app.py
```

## 🎮 프로젝트 프로그램 사용법

1. `app.py`를 실행하여 Streamlit 애플리케이션을 시작합니다.
2. 예측할 날짜를 선택합니다.
3. `🔮 금 가격 예측하기` 버튼을 클릭하여 결과를 확인합니다.
4. 예측된 금 가격(XAU/USD, USD/그램, KRW/그램)과 그래프를 확인합니다.
5. **홈 화면에서 yfinance 라이브러리를 사용하여 최근 5일간의 금 가격이 표시되며, 날짜가 변경되면 실시간으로 변경됩니다.**

## 📜 저작권 및 사용권 정보

- 이 프로젝트는 자유롭게 사용 가능하지만, 상업적 용도로 이용하려면 반드시 출처를 표기해야 합니다.
- 본 프로젝트의 코드 및 데이터는 **MIT 라이선스**에 따라 배포됩니다.

## 🐞 버그 및 디버깅

## 🔍 Prophet → RandomForest 변경 시 발생한 오류 해결

초기에 **Prophet**을 사용하여 `ds`(날짜)와 `y`(종가)만을 사용하여 학습을 진행했으나, 로컬에서 돌려본 결과 정확도가 낮게 나와 **RandomForest** 모델로 변경하였습니다. 이후 **RandomForest** 모델을 사용하여 다시 학습을 진행하고 로컬에서 테스트한 결과, Prophet을 사용할 때보다 정확도가 향상되었습니다.

그러나 VSC에서 Prophet을 사용하던 코드 그대로 RandomForest 모델을 적용하는 과정에서 기존 Prophet의 `future` 데이터프레임을 그대로 사용하려다 오류가 발생했습니다.

#### ✅ 오류 원인

- Prophet에서 사용하던 `future` 데이터프레임에는 `ds`(날짜)만 포함되어 있었음.
- 하지만 **RandomForest** 모델은 여러 개의 특성(`Year`, `Month`, `Day`, `Weekday`, `Quarter`, `Price_Change`, `Volume_Change`)을 입력값으로 요구함.
- 따라서 `future` 데이터프레임을 새롭게 생성할 필요가 있었음.

#### 🛠 해결 방법

다음과 같이 `future` 데이터프레임을 수정하여 모델의 입력 형식에 맞도록 변경하였습니다.

```python
future = pd.DataFrame({
    'Year': [year],
    'Month': [month],
    'Day': [day],
    'Weekday': [weekday],
    'Quarter': [quarter],
    'Price_Change': [price_change],
    'Volume_Change': [volume_change]
})
```

### 🔍 온스(oz) → 그램(g) 변환 오류 수정

초기에 **예측된 금 가격을 온스(oz) 단위로 환산한 후 환율을 적용**하여 원화(KRW)로 변환했으나, **그램(g) 단위로 변환하지 않아 가격이 비정상적으로 높게 나오는 문제**가 있었습니다.

#### ✅ 오류 원인

```python
predicted_price_krw = predicted_price_xau * exchange_rate
```

위 코드에서는 **온스(oz) 단위의 금 가격을 환율에 곱하여 직접 변환**하는 방식이었기 때문에, 실제보다 약 31배 더 높은 값이 출력되었습니다.

#### 🛠 해결 방법

금을 **그램(g) 단위로 변환**한 후 환율을 적용하도록 변경하였습니다.

```python
predicted_price_gram = predicted_price_xau / 31.1034768  # XAU에서 그램으로 변환
predicted_price_krw = predicted_price_gram * exchange_rate
```

이제 예측된 금 가격이 **그램 단위**로 변환된 후 환율을 적용하므로, 보다 정확한 값이 출력됩니다.

## 📚 참고 및 출처

- **Scikit-learn 공식 문서:** [https://scikit-learn.org/stable/](https://scikit-learn.org/stable/)
- **Facebook Prophet 공식 문서:** [https://facebook.github.io/prophet/](https://facebook.github.io/prophet/)
- **Streamlit 공식 문서:** [https://docs.streamlit.io/](https://docs.streamlit.io/)
- **yfinance 공식 문서:** [https://pypi.org/project/yfinance/](https://pypi.org/project/yfinance/)
- **ExchangeRate-API:** [https://www.exchangerate-api.com/](https://www.exchangerate-api.com/)

---

