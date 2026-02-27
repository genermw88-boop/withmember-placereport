import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components

# 1. API 키 설정 (스트림릿 웹 금고에서 가져옴)
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("API 키가 설정되지 않았습니다. Streamlit 웹 설정의 Secrets에 키를 넣어주세요.")
    st.stop()
    
genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="위드멤버 1일 차 진단기", page_icon="📊", layout="wide")

st.title("📊 플레이스 진단 리포트")
st.markdown("가독성을 극대화한 프리미엄 보고서 폼입니다. 500m 상권 경쟁 분석이 추가되었습니다.")

# 폼 입력
with st.form("diagnostic_form"):
    st.subheader("📋 매장 기본 정보")
    col1, col2 = st.columns(2)
    with col1:
        store_name = st.text_input("1. 실제 간판 상호명", placeholder="예: 정가네")
        target_area = st.text_input("3. 타겟 지역명", placeholder="예: 서현동")
        current_keywords = st.text_input("5. 현재 등록된 키워드(태그)", placeholder="예: 서현동맛집, 고기집")
    with col2:
        current_place_name = st.text_input("2. 플레이스 등록 이름", placeholder="예: 정가네")
        main_menu = st.text_input("4. 핵심 메뉴/업종", placeholder="예: 삼겹살")
        intro_text = st.text_area("6. 현재 플레이스 소개글", placeholder="예: 안녕하세요 정가네입니다.")
    
    st.markdown("---")
    st.subheader("📊 매장 리뷰 데이터")
    col3, col4, col5 = st.columns(3)
    with col3:
        visitor_reviews = st.number_input("방문자 리뷰 수", min_value=0, step=1)
    with col4:
        blog_reviews = st.number_input("블로그 리뷰 수", min_value=0, step=1)
    with col5:
        competitor_count = st.number_input("500m 내 예상 경쟁 매장 수", min_value=0, step=1, value=15)
    
    submitted = st.form_submit_button("🚀 정밀 보고서 생성 및 이미지 추출")

# 3. 진단 실행
if submitted:
    if not store_name or not target_area or not main_menu:
        st.error("상호명, 타겟 지역명, 핵심 메뉴는 필수입니다.")
    else:
        with st.spinner("AI가 지역 상권 데이터와 알고리즘을 정밀 분석 중입니다..."):
            
            # 2. AI 프롬프트
            prompt = f"""
            너는 10년 경력의 네이버 플레이스 마케팅 전문 컨설턴트야.
            아래 7개의 구분자(###)를 사용하여, 특수기호나 HTML 태그 없이 오직 자연스럽고 전문적인 '순수 텍스트'로만 간결하게 작성해.

            [입력 데이터]
            - 매장명: {store_name} / 등록명: {current_place_name}
            - 상권: {target_area} / 업종: {main_menu}
            - 소개글: {intro_text}
            - 리뷰: 방문자 {visitor_reviews}개 / 블로그 {blog_reviews}개

            [출력 규칙 - 매우 중요]
            1. 문장에 색상을 넣기 위한 HTML 태그를 절대 쓰지 마.
            2. 구구절절 쓰지 말고 항목당 1~2줄 이내로 핵심만 딱 떨어지게 요약해.

            ###SEO_SCORE###
            (예: 35점)

            ###SEO_RANK###
            (예: 6~8페이지)

            ###PROBLEM###
            (등록명 '{current_place_name}'의 알고리즘상 한계와 '{intro_text}' 소개글의 부족함, 도구 미활용으로 인한 고객 이탈을 1~2줄로 진단해)

            ###EFFECT###
            (빈약했던 소개글을 보완하고 네이버 도구를 적극 세팅했을 때 잠재 고객의 체류 시간과 방문 전환율 향상 기대 효과를 1~2줄로 작성해)

            ###COMPETITOR_COUNT###
            ('{target_area}' 지역 내 '{main_menu}' 업종의 치열함을 고려해, 500m 반경 내 예상 경쟁 매장 수를 현실적으로 추정해서 숫자와 '개' 단위만 딱 1줄로 출력해. 예: 약 25개)

            ###COMPETITION###
            (위에서 추정한 경쟁 매장 수 대비, 현재 리뷰({visitor_reviews}개/{blog_reviews}개) 수준이라면 500m 상권 내에서 순위가 대략 어느 정도로 밀려있는지(예: "경쟁 매장 30곳 중 20위권 밖으로 밀려남" 또는 "하위 30% 수준") 팩트를 짚어 사장님께 경각심을 주는 내용 1~2줄)

            ###REVIEW_PROBLEM###
            (현재 방문자 및 블로그 리뷰 수치에 대한 객관적인 진단을 하고, 2일 차에 해당 데이터를 정밀 분석해 솔루션을 주겠다는 안내를 1~2줄로 묶어서 작성해)
            """
            
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(prompt)
                
                res_text = response.text
                
                # 결과 파싱
                try:
                    score = res_text.split("###SEO_SCORE###")[1].split("###SEO_RANK###")[0].strip()
                    rank = res_text.split("###SEO_RANK###")[1].split("###PROBLEM###")[0].strip()
                    problem = res_text.split("###PROBLEM###")[1].split("###EFFECT###")[0].strip()
                    effect = res_text.split("###EFFECT###")[1].split("###COMPETITOR_COUNT###")[0].strip()
                    competitor_count = res_text.split("###COMPETITOR_COUNT###")[1].split("###COMPETITION###")[0].strip()
                    competition = res_text.split("###COMPETITION###")[1].split("###REVIEW_PROBLEM###")[0].strip()
                    review_problem = res_text.split("###REVIEW_PROBLEM###")[1].strip()
                except:
                    st.error("AI 응답 형식이 일치하지 않습니다. 버튼을 한 번 더 눌러주세요.")
                    st.stop()
                
                # 3. HTML/JS 디자인
                html_code = f"""
                <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
                <div style="padding: 20px; display: flex; flex-direction: column; align-items: center; font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;">
                    
                    <style>
                        .section-title {{ color: #1a202c; font-size: 18px; font-weight: 800; margin: 0 0 15px 0; padding-bottom: 8px; border-bottom: 2px solid #edf2f7; }}
                        .row-box {{ display: flex; margin-bottom: 12px; align-items: flex-start; }}
                        .label {{ width: 150px; font-size: 15px; font-weight: 700; color: #4a5568; flex-shrink: 0; padding-top: 1px; line-height: 1.6; }}
                        .value {{ font-size: 15px; font-weight: 600; color: #2d3748; line-height: 1.6; flex-grow: 1; word-break: keep-all; }}
                        .highlight-box {{ background-color: #f7fafc; padding: 20px; border-radius: 8px; margin-bottom: 30px; border-left: 5px solid #3182ce; }}
                    </style>

                    <div id="report-card" style="width: 100%; max-width: 680px; padding: 50px 40px; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0px 10px 25px rgba(0,0,0,0.05);">
                        <h2 style="color: #1a202c; text-align: center; margin: 0 0 10px 0; font-size: 26px; font-weight: 800; letter-spacing: -1px;">📊 플레이스 진단 리포트</h2>
                        <p style="text-align: center; color: #718096; font-size: 15px; margin-bottom: 40px; font-weight: 600;">대상 매장: <span style="color:#1a202c; font-weight: 800;">{current_place_name}</span></p>
                        
                        <div class="highlight-box">
                            <h4 class="section-title" style="border:none; margin-bottom: 15px; color:#2b6cb0;">1. 현재 점수 및 예상 순위</h4>
                            <div class="row-box"><div class="label">등록된 키워드 :</div><div class="value">{current_keywords if current_keywords else "미등록"}</div></div>
                            <div class="row-box"><div class="label">플레이스 점수 :</div><div class="value" style="color: #e53e3e; font-size: 17px; font-weight: 800;">{score}</div></div>
                            <div class="row-box" style="margin-bottom:0;"><div class="label">예상 노출 순위 :</div><div class="value" style="color: #e53e3e; font-size: 17px; font-weight: 800;">{rank}</div></div>
                        </div>

                        <div style="margin-bottom: 35px;">
                            <h4 class="section-title">📌 2. 매장 노출 알고리즘 진단</h4>
                            <div class="row-box"><div class="label">현재 매장명 :</div><div class="value" style="font-weight: 800;">{current_place_name}</div></div>
                            <div class="row-box" style="margin-bottom:0;"><div class="label">진단 내용 :</div><div class="value">{problem}</div></div>
                        </div>

                        <div style="margin-bottom: 35px;">
                            <h4 class="section-title">💡 3. 네이버 최적화 및 도구 활용 기대효과</h4>
                            <div class="row-box"><div class="label">상호명 최적화 :</div><div class="value" style="color: #2b6cb0;"><strong>[업체명] + [지역명] + [업종]</strong> 조합으로 세팅 시 검색 노출 및 유입률이 대폭 증대됩니다.</div></div>
                            <div class="row-box" style="margin-bottom:0;"><div class="label">도구 및 소개글 :</div><div class="value">{effect}</div></div>
                        </div>

                        <div style="margin-bottom: 35px;">
                            <h4 class="section-title">⚔️ 4. 반경 500m 상권 경쟁 진단</h4>
                            <div class="row-box"><div class="label">상권 내 경쟁 매장 :</div><div class="value" style="color: #e53e3e; font-weight: 800;">{competitor_count} <span style="font-size: 13px; color: #718096; font-weight: 600;">(500m 반경 예상 기준)</span></div></div>
                            <div class="row-box" style="margin-bottom:0;"><div class="label">상권 내 순위 진단 :</div><div class="value">{competition}</div></div>
                        </div>

                        <div style="background-color: #f7fafc; padding: 20px; border-radius: 8px; border: 1px dashed #cbd5e0;">
                            <h4 class="section-title" style="border:none; margin-bottom: 15px;">🚀 [예고] 2일 차: 리뷰 및 평판 정밀 분석</h4>
                            <div class="row-box"><div class="label">현재 리뷰 수 :</div><div class="value">방문자 <strong>{visitor_reviews}</strong>개 &nbsp;|&nbsp; 블로그 <strong>{blog_reviews}</strong>개</div></div>
                            <div class="row-box" style="margin-bottom:0;"><div class="label">진단 및 예정 :</div><div class="value">{review_problem}</div></div>
                        </div>
                    </div>

                    <button onclick="downloadImage()" style="margin-top: 30px; padding: 15px 30px; font-size: 16px; font-weight: bold; color: #fff; background-color: #2d3748; border: none; border-radius: 8px; cursor: pointer; box-shadow: 0px 4px 6px rgba(0,0,0,0.1); transition: 0.2s;">
                        📸 이 보고서를 이미지(.png)로 다운로드
                    </button>
                </div>

                <script>
                function downloadImage() {{
                    const element = document.getElementById('report-card');
                    html2canvas(element, {{scale: 2, backgroundColor: "#ffffff"}}).then(canvas => {{
                        let link = document.createElement('a');
                        link.download = '{current_place_name}_1일차_진단보고서.png';
                        link.href = canvas.toDataURL('image/png');
                        link.click();
                    }});
                }}
                </script>
                """
                
                # HTML 렌더링
                components.html(html_code, height=1350, scrolling=True)
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
