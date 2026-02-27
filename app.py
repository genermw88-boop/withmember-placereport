import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components

# 1. 제미나이 API 키 하이브리드 설정 (내 PC & 웹 동시 지원)
try:
    # 스트림릿 웹 서버(클라우드)에서 실행될 때는 비밀 금고의 키를 찾음
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except KeyError:
    # 내 PC에서 실행하거나 금고가 비어있을 때는 아래의 키를 사용함
    GOOGLE_API_KEY = "AIzaSyBKbcLD9sCgk7q-tK9vvyj6YFHArDS_diY"

genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="위드멤버 1일 차 진단기", page_icon="📊", layout="wide")

# (--- 이 아래부터는 기존 코드 그대로 두시면 됩니다! ---)

