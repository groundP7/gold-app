# gold-app
# Gold Price Prediction App

## 📌 프로젝트 개요

금 가격을 예측하는 머신러닝 애플리케이션입니다. Streamlit을 사용하여 직관적인 UI를 제공하며, RandomForest 모델을 활용하여 금 가격을 예측합니다.

## 🛠️ 기술 스택

- **언어**: Python
- **프레임워크**: Streamlit
- **머신러닝 모델**: RandomForest
- **시각화**: Plotly
- **데이터 처리**: Pandas

## 🔥 주요 기능

- 사용자가 선택한 날짜의 금 가격 예측
- XAU(온스)와 그램(g) 단위로 가격 변환 제공
- USD → KRW 환율 적용
- 예측 결과 그래프 시각화

## 🏗️ 프로젝트 구조

```
📂 gold-app-main
 ┣ 📂 model
 ┃ ┗ 📄 gold_price_model.pkl  # 학습된 모델 파일
 ┣ 📂 pages
 ┣ 📄 app.py                 # 메인 애플리케이션
 ┣ 📄 requirements.txt        # 필요 라이브러리 목록
 ┣ 📄 README.md              # 프로젝트 설명 파일
```

## 🛠️ 설치 및 실행 방법

1. 필수 라이브러리 설치:
   ```bash
   pip install -r requirements.txt
   ```
2. 애플리케이션 실행:
   ```bash
   streamlit run app.py
   ```

## 🐞 디버깅 기록

### 📌 Prophet → RandomForest 전환 시 발생한 오류

**오류 내용:** Prophet 모델을 사용할 때는 `future` 데이터프레임이 `ds(날짜)` 열만 필요했지만, RandomForest 모델은 다음과 같은 추가 입력이 필요하여 오류가 발생했습니다:

```
'Year', 'Month', 'Day', 'Weekday', 'Quarter', 'Price_Change', 'Volume_Change'
```

**해결 방법:** `future` 데이터프레임을 다음과 같이 수정하여 해결했습니다:

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

## 📌 추가 참고 사항

- AI 모델은 과거 데이터를 기반으로 예측하기 때문에, 시장 변동성이나 예측 불가능한 이벤트를 반영하지 못할 수 있습니다.
- 예측 결과는 참고용으로만 활용해주세요.

---

📌 **문의:** 프로젝트 관련 문의는 GitHub Issue를 이용해주세요! 🚀

