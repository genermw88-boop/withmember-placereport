import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components

# 1. 🚨 보안 시스템: 코드 내부에는 진짜 API 키를 절대 적지 않습니다.
# 스트림릿 웹 설정(Settings > Secrets)에 넣은 키를 자동으로 불러옵니다.
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
        current_place_name = st.text_input("플레이스 등록 이름", placeholder="예: 정가네 부평점")
        target_area = st.text_input("타겟 지역명", placeholder="예: 부평동")
    with col2:
        main_menu = st.text_input("핵심 메뉴/업종", placeholder="예: 삼겹살")
        current_keywords = st.text_input("현재 등록된 키워드(태그)", placeholder="예: 부평맛집, 고기집")
    
    st.markdown("---")
    st.subheader("🛠️ 2. 네이버 플레이스 도구 세팅 여부 (체크)")
    st.caption("현재 사장님 매장에 활성화되어 있는 도구만 체크해 주세요.")
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

# 3. 진단 실행
if submitted:
    if not current_place_name or not target_area or not main_menu:
        st.error("플레이스 등록 이름, 타겟 지역명, 핵심 메뉴는 필수입니다.")
    else:
        with st.spinner("AI가 네이버 도구 가산점 누락 여부와 상권 데이터를 분석 중입니다..."):
            
            # 상태 표시용 HTML 함수 (등록-초록 / 미등록-빨강)
            def get_status_html(is_used):
                if is_used:
                    return '<span style="color: #38a169; font-weight: 800;">등록</span>'
                else:
                    return '<span style="color: #e53e3e; font-weight: 800;">미등록</span>'

            # AI 전달용 텍스트 및 보고서 표시용 HTML 생성
            tool_status_text = f"예약({'등록' if use_booking else '미등록'}), 톡톡({'등록' if use_talktalk else '미등록'}), 쿠폰({'등록' if use_coupon else '미등록'}), 안심번호({'등록' if use_safecall else '미등록'})"
            display_status = f"예약({get_status_html(use_booking)}), 톡톡({get_status_html(use_talktalk)}), 쿠폰({get_status_html(use_coupon)}), 안심번호({get_status_html(use_safecall)})"
            
            prompt = f"""
            너는 10년 경력의 네이버 플레이스 마케팅 전문 컨설턴트야.
            아래 7개의 구분자(###)를 사용하여, 특수기호나 HTML 태그 없이 오직 전문적인 '순수 텍스트'로만 간결하게 작성해.

            [입력 데이터]
            - 플레이스 등록명: {current_place_name}
            - 상권: {target_area} / 업종: {main_menu}
            - 네이버 공식 도구 세팅 현황: {tool_status_text}
            - 리뷰: 방문자 {visitor_reviews}개 / 블로그 {blog_reviews}개

            ###SEO_SCORE###
            (예: 35점)

            ###SEO_RANK###
            (예: 6~8페이지)

            ###PROBLEM###
            (현재 도구 세팅 현황({tool_status_text})을 근거로, '미등록'된 도구들 때문에 네이버 알고리즘 가산점을 못 받고 있으며 이로 인해 순위 경쟁에서 심각하게 밀리고 있다는 점을 1~2줄로 진단해)

            ###EFFECT###
            (미등록 도구들을 즉시 등록하여 알고리즘 가산점을 확보했을 때, 검색 노출 순위가 회복되고 고객 유입이 얼마나 상승할지 기대 효과를 1~2줄로 작성해)

            ###COMPETITOR_COUNT###
            ('{target_area}' 지역 내 '{main_menu}' 업종의 치열함을 고려해, 500m 반경 내 예상 경쟁 매장 수를 AI 알고리즘으로 추정해서 숫자와 '개' 단위만 출력해. 예: 약 45개)

            ###COMPETITION###
            (추정한 경쟁 매장 수 대비 현재 리뷰 수준을 고려하여, 상권 내 순위가 하위 몇 % 수준인지 등 사장님께 위기감을 주는 내용 1~2줄)

            ###REVIEW_PROBLEM###
            (현재 리뷰 수치 진단 및 2일 차에 정밀 분석 솔루션을 주겠다는 안내를 1~2줄로 작성)
            """
            
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(prompt)
                res_text = response.text
                
                # 결과 파싱 (안전 장치 포함)
                def get_val(tag, next_tag=None):
                    try:
                        part = res_text.split(tag)[1]
                        return part.split(next_tag)[0].strip() if next_tag else part.strip()
                    except: return "데이터 분석 중..."

                score = get_val("###SEO_SCORE###", "###SEO_RANK###")
                rank = get_val("###SEO_RANK###", "###PROBLEM###")
                problem = get_val("###PROBLEM###", "###EFFECT###")
                effect = get_val("###EFFECT###", "###COMPETITOR_COUNT###")
                competitor_count = get_val("###COMPETITOR_COUNT###", "###COMPETITION###")
                competition = get_val("###COMPETITION###", "###REVIEW_PROBLEM###")
                review_problem = get_val("###REVIEW_PROBLEM###")

                # HTML 디자인 리포트
                html_code = f"""
                <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
                <div style="padding: 20px; display: flex; flex-direction: column; align-items: center; font-family: 'Malgun Gothic', sans-serif;">
                    <style>
                        .section-title {{ color: #1a202c; font-size: 18px; font-weight: 800; margin-bottom: 15px; border-bottom: 2px solid #edf2f7; }}
                        .row-box {{ display: flex; margin-bottom: 12px; align-items: flex-start; }}
                        .label {{ width: 140px; font-size: 15px; font-weight: 700; color: #4a5568; }}
                        .value {{ font-size: 15px; font-weight: 600; color: #2d3748; flex: 1; word-break: keep-all; }}
                        .highlight-box {{ background-color: #f7fafc; padding: 20px; border-radius: 8px; margin-bottom: 30px; border-left: 5px solid #3182ce; }}
                    </style>
                    <div id="report-card" style="width: 100%; max-width: 680px; padding: 50px 40px; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0px 10px 25px rgba(0,0,0,0.05);">
                        <h2 style="text-align: center; margin-bottom: 10px; font-size: 26px; font-weight: 800;">📊 플레이스 진단 리포트</h2>
                        <p style="text-align: center; color: #718096; margin-bottom: 40px;">대상 매장: <strong>{current_place_name}</strong></p>
                        
                        <div class="highlight-box">
                            <h4 class="section-title" style="border:none; color:#2b6cb0;">1. 현재 점수 및 예상 순위</h4>
                            <div class="row-box"><div class="label">등록 키워드 :</div><div class="value">{current_keywords if current_keywords else "미등록"}</div></div>
                            <div class="row-box"><div class="label">플레이스 점수 :</div><div class="value" style="color: #e53e3e; font-size: 17px; font-weight: 800;">{score}</div></div>
                            <div class="row-box"><div class="label">예상 노출 순위 :</div><div class="value" style="color: #e53e3e; font-size: 17px; font-weight: 800;">{rank}</div></div>
                        </div>

                        <div style="margin-bottom: 35px;">
                            <h4 class="section-title">📌 2. 네이버 도구 누락 및 알고리즘 진단</h4>
                            <div class="row-box"><div class="label">현재 세팅 현황 :</div><div class="value" style="font-size: 14px;">{display_status}</div></div>
                            <div class="row-box"><div class="label">알고리즘 진단 :</div><div class="value">{problem}</div></div>
                        </div>

                        <div style="margin-bottom: 35px;">
                            <h4 class="section-title">💡 3. 도구 최적화 시 기대효과</h4>
                            <div class="row-box"><div class="label">순위 회복 효과 :</div><div class="value">{effect}</div></div>
                        </div>

                        <div style="margin-bottom: 35px;">
                            <h4 class="section-title">⚔️ 4. 반경 500m 상권 경쟁 진단</h4>
                            <div class="row-box"><div class="label">경쟁 매장 :</div><div class="value" style="color: #e53e3e; font-weight: 800;">{competitor_count} <span style="font-size: 12px; color:#718096;">(AI 자동 추정)</span></div></div>
                            <div class="row-box"><div class="label">상권 내 순위 진단 :</div><div class="value">{competition}</div></div>
                        </div>

                        <div style="background-color: #f7fafc; padding: 20px; border-radius: 8px; border: 1px dashed #cbd5e0;">
                            <h4 class="section-title" style="border:none; margin-bottom:10px;">🚀 2일 차 예고: 리뷰/평판 정밀 분석</h4>
                            <div class="value" style="font-size:14px;">{review_problem}</div>
                        </div>
                    </div>
                    <button onclick="downloadImage()" style="margin-top: 30px; padding: 15px 30px; font-size: 16px; font-weight: bold; color: #fff; background-color: #2d3748; border: none; border-radius: 8px; cursor: pointer;">
                        📸 보고서 이미지(.png) 다운로드
                    </button>
                </div>
                <script>
                function downloadImage() {{
                    const element = document.getElementById('report-card');
                    html2canvas(element, {{scale: 2, backgroundColor: "#ffffff"}}).then(canvas => {{
                        let link = document.createElement('a');
                        link.download = '{current_place_name}_진단리포트.png';
                        link.href = canvas.toDataURL();
                        link.click();
                    }});
                }}
                </script>
                """
                components.html(html_code, height=1300, scrolling=True)
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
