import streamlit as st
import pandas as pd

from ui import 가격예측, 데이터분석, 홈

# CSS를 사용하여 개별 요소 스타일링
st.markdown(
    """
    <style>
    /* 사이드바 스타일 */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 3px solid #e0e0e0;
    }

    /* 사이드바 제목 스타일 */
    [data-testid="stSidebarNav"]::before {
        content: "📌 메뉴 선택";
        font-size: 20px;
        font-weight: bold;
        color: #333;
        padding: 10px;
        display: block;
        text-align: center;
    }

    /* 사이드바 선택 박스 스타일 */
    .stSelectbox {
        background-color: white;
        border-radius: 10px;
        padding: 8px;
        font-size: 16px;
    }

    /* 중앙 정렬 */
    .centered {
        display: flex;
        justify-content: center;
    }

    /* 데이터프레임 중앙 정렬 */
    .stDataFrame {
        max-width: 800px;
        margin: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def main():
    st.title("💰 금 가격 예측 App")

    menu = {
        "🏠 홈": "홈",
        "📊 데이터분석": "데이터분석",
        "📈 가격예측": "가격예측"
    }
    
    choice = st.sidebar.selectbox("📌 메뉴 선택", list(menu.keys()))

    if choice == "🏠 홈":
        홈.run_home()
    elif choice == "📊 데이터분석":
        데이터분석.run_eda()
    elif choice == "📈 가격예측":
        가격예측.run_ml()

if __name__ == "__main__":
    main()
