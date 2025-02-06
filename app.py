import streamlit as st
import pandas as pd

from ui import 가격예측, 데이터분석, 홈

# CSS를 사용하여 개별 요소들을 중앙 정렬
st.markdown(
    """
    <style>
    .centered {
        display: flex;
        justify-content: center;
    }
    .stDataFrame {
        max-width: 800px;
        margin: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def main() :
    st.title("금 가격 예측 App")

    menu = ["홈", "데이터분석", "가격예측"]
    choice = st.sidebar.selectbox("메뉴", menu)

    if choice == menu[0] :
        홈.run_home()
    elif choice == menu[1] :
        데이터분석.run_eda()
    elif choice == menu[2] :
        가격예측.run_ml()

if __name__ == "__main__" :
    main()