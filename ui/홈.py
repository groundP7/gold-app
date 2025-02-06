from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

def run_home():
    # CSS 스타일링
    st.markdown("""
    <style>
    .big-font {
        font-size: 50px !important;
        color: #4B0082;
        text-align: center;
    }
    .medium-font {
        font-size: 30px !important;
        color: #8B4513;
        text-align: center;
    }
    .small-font {
        font-size: 20px !important;
        color: #4B0082;
    }
    .intro-text {
        font-size: 18px !important;
        color: #555;
        text-align: justify;
    }
    .card {
        background-color: #F8F8FF;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .card-header {
        font-size: 24px;
        color: #8B4513;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .card-body {
        font-size: 18px;
        color: #333;
    }
    </style>
    """, unsafe_allow_html=True)

    # 헤더
    st.markdown('<p class="big-font">🏅 금 가격 예측 앱</p>', unsafe_allow_html=True)
    st.markdown('<p class="medium-font">머신러닝을 활용한 금 가격 분석 및 예측</p>', unsafe_allow_html=True)

    # 앱 이미지
    st.image("https://images.unsplash.com/photo-1610375461246-83df859d849d", use_container_width=True)

    # 간단한 소개
    st.markdown('<p class="intro-text">이 앱은 과거 금 가격 데이터를 분석하고, 머신러닝 모델을 통해 미래 금 가격을 예측합니다. 금 가격 예측을 통해 투자 결정을 돕고, 데이터 기반의 시각화를 통해 금 시장의 변동성을 이해할 수 있습니다.</p>', unsafe_allow_html=True)

    # 최근 금 가격 데이터 표시
    @st.cache_data(ttl=3600)  # 1시간마다 데이터 갱신
    def load_recent_data():
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)  # 최근 7일간의 데이터
        
        gold_data = yf.download('GLD', start=start_date, end=end_date)
        
        recent_data = gold_data[['Close']].reset_index()
        recent_data.columns = ['Date', 'Price']
        recent_data['Date'] = recent_data['Date'].dt.strftime('%Y-%m-%d')
        recent_data['Price_per_oz'] = recent_data['Price'] * 10  # 1온스 가격으로 변환
        recent_data['Price_per_g'] = recent_data['Price_per_oz'] / 31.1  # 1g 가격으로 변환
        
        return recent_data.tail(5)  # 최근 5일간의 데이터만 반환

    recent_data = load_recent_data()

    # 최근 금 가격 섹션
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-header'>📊 최근 금 가격</div>", unsafe_allow_html=True)
    st.markdown("<div class='card-body'>최근 5일간의 금 가격 데이터를 확인할 수 있습니다.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.dataframe(recent_data.style.format({
        'Price': '${:.2f} (1/10 oz)',
        'Price_per_oz': '${:.2f} per oz (31.1g)',
        'Price_per_g': '${:.2f} per g'
    }))

    # 주요 기능 소개
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-header'>💡 주요 기능</div>", unsafe_allow_html=True)
    st.markdown("<div class='card-body'>앱의 주요 기능을 소개합니다:</div>", unsafe_allow_html=True)
    st.markdown("<ul><li>과거 금 가격 데이터 분석</li><li>다양한 시각화 도구 제공</li><li>머신러닝 기반 금 가격 예측</li><li>사용자 정의 예측 기간 설정</li></ul>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 데이터 분석 설명
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-header'>📊 데이터 분석</div>", unsafe_allow_html=True)
    st.markdown("<div class='card-body'>앱은 과거 금 가격 데이터를 분석하고, 이를 시각화하여 사용자가 금 가격의 변동성을 더 잘 이해할 수 있도록 돕습니다. 분석 기능은 다음과 같습니다:</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <ol>
        <li><b>데이터 개요:</b> 데이터의 기간, 총 데이터 수, 최근 종가 등의 주요 정보를 확인할 수 있습니다.</li>
        <li><b>가격 추이 시각화:</b> 금 가격의 변동을 시간에 따른 라인 그래프 형태로 시각화하여 금 시장의 흐름을 확인할 수 있습니다.</li>
        <li><b>기간별 금 가격 추이:</b> 사용자가 선택한 기간(일별, 월별, 분기별, 년별)에 따른 금 가격의 변화를 분석할 수 있습니다.</li>
        <li><b>사용자 정의 기간 선택:</b> 원하는 시작 날짜와 종료 날짜를 선택하여 특정 기간 동안의 금 가격 데이터를 필터링하고 시각화할 수 있습니다.</li>
    </ol>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # 예측 시스템 설명
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-header'>🔮 예측 시스템</div>", unsafe_allow_html=True)
    st.markdown("<div class='card-body'>이 앱은 머신러닝 모델을 기반으로 금 가격을 예측합니다. 예측 시스템은 주로 과거 금 가격 데이터를 기반으로 학습된 모델을 사용하며, 이 모델은 미래의 금 가격을 예측하는 데 도움을 줍니다. 예측 과정은 다음과 같습니다:</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <ol>
        <li><b>데이터 수집:</b> Yahoo Finance API를 통해 과거 금 가격 데이터를 수집합니다. 이 데이터는 금의 일별 종가를 포함합니다.</li>
        <li><b>특성 생성:</b> 각 날짜에 대해 요일, 월, 분기 등의 정보를 특성으로 추가합니다. 이를 통해 모델이 금 가격의 패턴을 더 잘 학습할 수 있도록 돕습니다.</li>
        <li><b>머신러닝 모델 학습:</b> 과거 데이터를 기반으로 Random Forest 모델을 학습시킵니다. 이 모델은 복잡한 패턴을 인식하고 미래의 금 가격을 예측할 수 있습니다.</li>
        <li><b>예측 수행:</b> 사용자가 선택한 날짜를 입력받아, 학습된 모델을 사용하여 금 가격을 예측합니다. 예측된 가격은 1온스 및 1그램 기준으로 제공됩니다.</li>
    </ol>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # 사용 방법
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-header'>🚀 사용 방법</div>", unsafe_allow_html=True)
    st.markdown("<div class='card-body'>앱 사용 방법을 확인하세요:</div>", unsafe_allow_html=True)
    st.markdown("<ol><li>좌측 사이드바에서 원하는 기능을 선택하세요.</li><li>'데이터 분석'에서 과거 금 데이터를 탐색할 수 있습니다.</li><li>'가격 예측'에서 미래 금 가격을 예측할 수 있습니다.</li></ol>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 면책 조항
    st.info("주의: 이 앱의 예측은 참고용으로만 사용해주세요. 실제 투자 결정을 내리기 전에 전문가와 상담하시기 바랍니다.")

if __name__ == "__main__":
    run_home()
