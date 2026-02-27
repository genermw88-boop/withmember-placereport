import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components

# 1. API 키 설정 (스트림릿 웹 금고에서 안전하게 가져옴)
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("보안 금고(Secrets)에 API 키가 설정되지 않았습니다. 관리자 설정에서 키를 입력해주세요.")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="위드멤버 1일 차 진단기", page_icon="📊", layout="wide")

st.title("📊 플레이스 진단 리포트")
st.markdown("네이버 공식 도구 활용 여부에 따른 알고리즘 순위 누락 현상을 정밀 진단합니다.")

# 폼 입력
with st.form("diagnostic_form"):
    st.subheader("📋 1. 매장 기본 정보")
    col1, col2 = st.columns(2)
    with col1:
        current_place_name = st.text_input("플레이스 등록 이름", placeholder="예: 화양식 부평점")
        target_area = st.text_input("타겟 지역명", placeholder="예: 부평구 갈산동")
    with col2:
        main_menu = st.text_input("핵심 메뉴/업종", placeholder="예: 양식")
        current_keywords = st.text_input("현재 등록된 키워드(태그)", placeholder="예: 부평맛집, 파스타")
    
    st.markdown("---")
    st.subheader("🛠️ 2. 네이버 플레이스 도구 세팅 여부 (체크)")
    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    with col_t1:
        use_booking = st.checkbox("📅 네이버 예약")
    with col_t2:
        use_talktalk = st.checkbox("💬 네이버 톡톡")
    with col_t3:
        use_coupon = st.checkbox("🎟️ 네이버 쿠폰")
    with col_t4:
        use_safecall = st.checkbox("📞 안심번호(스마트콜)")

    st.markdown("---")
    st.subheader("📊 3. 매장 리뷰 데이터")
    col3, col4 = st.columns(2)
    with col3:
        visitor_reviews = st.number_input("방문자 리뷰 수", min_value=0, step=1)
    with col4:
        blog_reviews = st.number_input("블로그 리뷰 수", min_value=0, step=1)
    
    submitted = st.form_submit_button("🚀 정밀 보고서 생성 및 이미지 추출")

if submitted:
    if not current_place_name or not target_area or not main_menu:
        st.error("필수 정보를 모두 입력해주세요.")
    else:
        with st.spinner("AI가 데이터를 분석 중입니다..."):
            
            # 상태 표시용 HTML 함수 (등록-초록 / 미등록-빨강)
            def get_status_html(is_used):
                if is_used:
                    return '<span style="color: #38a169; font-weight: 800;">등록</span>'
                else:
                    return '<span style="color: #e53e3e; font-weight: 800;">미등록</span>'

            tool_status_text = f"예약({'등록' if use_booking else '미등록'}), 톡톡({'등록' if use_talktalk else '미등록'}), 쿠폰({'등록' if use_coupon else '미등록'}), 안심번호({'등록' if use_safecall else '미등록'})"
            display_status = f"예약({get_status_html(use_booking)}), 톡톡({get_status_html(use_talktalk)}), 쿠폰({get_status_html(use_coupon)}), 안심번호({get_status_html(use_safecall)})"
            
            prompt = f"""
            너는 10년 경력의 네이버 플레이스 마케팅 컨설턴트야.
            ###SEO_SCORE###, ###SEO_RANK###, ###PROBLEM###, ###EFFECT###, ###COMPETITOR_COUNT###, ###COMPETITION###, ###REVIEW_PROBLEM### 구분자를 사용해.
            현황: {tool_status_text}, 리뷰: 방문자 {visitor_reviews}/블로그 {blog_reviews}.
            미등록 도구로 인한 순위 하락을 강조하고 위기감을 조성해줘.
            """
            
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(prompt)
                res_text = response.text
                
                def get_val(tag, next_tag=None):
                    try:
                        part = res_text.split(tag)[1]
                        return part.split(next_tag)[0].strip() if next_tag else part.strip()
                    except: return "분석 데이터 생성 중..."

                score = get_val("###SEO_SCORE###", "###SEO_RANK###")
                rank = get_val("###SEO_RANK###", "###PROBLEM###")
                problem = get_val("###PROBLEM###", "###EFFECT###")
                effect = get_val("###EFFECT###", "###COMPETITOR_COUNT###")
                competitor_count = get_val("###COMPETITOR_COUNT###", "###COMPETITION###")
                competition = get_val("###COMPETITION###", "###REVIEW_PROBLEM###")
                review_problem = get_val("###REVIEW_PROBLEM###")

                html_code = f"""
                <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
                <div style="padding: 20px; display: flex; flex-direction: column; align-items: center; font-family: 'Malgun Gothic', sans-serif;">
                    <style>
                        .section-title {{ color: #1a202c; font-size: 18px; font-weight: 800; margin-bottom: 15px; border-bottom: 2px solid #edf2f7; }}
                        .row-box {{ display: flex; margin-bottom: 12px; }}
                        .label {{ width: 140px; font-weight: 700; color: #4a5568; }}
                        .value {{ font-weight: 600; color: #2d3748; flex: 1; }}
                    </style>
                    <div id="report-card" style="width: 100%; max-width: 650px; padding: 40px; background: white; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 10px 20px rgba(0,0,0,0.05);">
                        <h2 style="text-align: center; margin-bottom: 30px;">📊 플레이스 진단 리포트</h2>
                        <div style="background: #f7fafc; padding: 15px; border-radius: 8px; border-left: 5px solid #3182ce; margin-bottom: 25px;">
                            <div class="row-box"><div class="label">플레이스 점수 :</div><div class="value" style="color: #e53e3e;">{score}</div></div>
                            <div class="row-box"><div class="label">예상 노출 순위 :</div><div class="value" style="color: #e53e3e;">{rank}</div></div>
                        </div>
                        <div style="margin-bottom: 25px;">
                            <h4 class="section-title">📌 네이버 도구 및 알고리즘 진단</h4>
                            <div class="row-box"><div class="label">세팅 현황 :</div><div class="value" style="font-size:14px;">{display_status}</div></div>
                            <div class="row-box"><div class="label">진단 내용 :</div><div class="value">{problem}</div></div>
                        </div>
                        <div style="margin-bottom: 25px;">
                            <h4 class="section-title">⚔️ 반경 500m 상권 경쟁 진단</h4>
                            <div class="row-box"><div class="label">경쟁 매장 :</div><div class="value" style="color: #e53e3e;">{competitor_count}</div></div>
                            <div class="row-box"><div class="label">순위 진단 :</div><div class="value">{competition}</div></div>
                        </div>
                        <div style="background: #f7fafc; padding: 15px; border-radius: 8px; border: 1px dashed #cbd5e0;">
                            <h4 class="section-title" style="border:none; margin-bottom:10px;">🚀 2일 차 예고: 리뷰/평판 분석</h4>
                            <div class="value" style="font-size:14px;">{review_problem}</div>
                        </div>
                    </div>
                    <button onclick="downloadImage()" style="margin-top:20px; padding: 12px 24px; background:#2d3748; color:white; border-radius:8px; border:none; cursor:pointer; font-weight:bold;">📸 보고서 이미지 다운로드</button>
                </div>
                <script>
                function downloadImage() {{
                    html2canvas(document.getElementById('report-card'), {{scale: 2, backgroundColor: "#ffffff"}}).then(canvas => {{
                        let link = document.createElement('a');
                        link.download = '{current_place_name}_진단리포트.png';
                        link.href = canvas.toDataURL();
                        link.click();
                    }});
                }}
                </script>
                """
                components.html(html_code, height=1200, scrolling=True)
            except Exception as e:
                st.error(f"오류 발생: {e}")
