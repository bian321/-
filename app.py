import streamlit as st
import google.generativeai as genai
import json

# --- إعدادات الصفحة ---
st.set_page_config(page_title="بوت المحقق الذكي (Gemini)", page_icon="🔍", layout="centered")

# --- ربط مفتاح Google Gemini ---
# ملاحظة: استبدل 'YOUR_API_KEY' بمفتاحك الحقيقي أو استخدم st.secrets
genai.configure(api_key="AIzaSyBfBDLC0wtKj40JePHvavZitCcM6rZ9Ft8")
model = genai.GenerativeModel('gemini')

# --- وظيفة توليد القضية ---
def generate_ai_case(subject, level):
    prompt = f"""
    أنت نظام تعليمي تفاعلي يسمى 'بوت المحقق الذكي'. 
    قم بإنشاء قضية غامضة لغرض تعليم موضوع ({subject}) لمستوى ({level}).
    يجب أن يكون الرد بتنسيق JSON حصراً باللغة العربية، ويحتوي على الحقول التالية:
    - title: عنوان القضية.
    - story: مقدمة درامية للموقف.
    - clue: الدليل المادي الذي عثر عليه المحقق.
    - question: السؤال الذي يحل اللغز.
    - options: قائمة من 3 خيارات.
    - correct_answer: الخيار الصحيح حرفياً.
    - explanation: شرح تعليمي بسيط للحل.
    """
    
    try:
        response = model.generate_content(prompt)
        # تنظيف النص الناتج ليصبح JSON صالح
        cleaned_response = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(cleaned_response)
    except Exception as e:
        return {"error": str(e)}

# --- إدارة حالة الجلسة ---
if 'game_state' not in st.session_state:
    st.session_state.game_state = "home"
    st.session_state.current_case = None

# --- الواجهة الرسومية ---
st.title("🕵️‍♂️ بوت المحقق الذكي")
st.caption("تعلم من خلال التحليل، الاستكشاف، وحل الألغاز")

if st.session_state.game_state == "home":
    st.subheader("إعداد ملف التحقيق")
    subject = st.selectbox("اختر المادة التعليمية:", ["البرمجة", "العلوم", "التاريخ", "الرياضيات", "اللغة العربية"])
    level = st.select_slider("مستوى الصعوبة:", options=["أطفال", "يافعين", "بالغين"])
    
    if st.button("توليد قضية جديدة ✨"):
        with st.spinner("جاري صياغة القضية بواسطة الذكاء الاصطناعي..."):
            case_data = generate_ai_case(subject, level)
            if "error" in case_data:
                st.error("حدث خطأ في الاتصال بالذكاء الاصطناعي. تأكد من صحة المفتاح.")
            else:
                st.session_state.current_case = case_data
                st.session_state.game_state = "playing"
                st.rerun()

elif st.session_state.game_state == "playing":
    case = st.session_state.current_case
    
    st.header(f"📌 قضية: {case['title']}")
    
    with st.expander("📖 تفاصيل القصة", expanded=True):
        st.write(case['story'])
    
    st.warning(f"💡 **الدليل المكتشف:** {case['clue']}")
    
    st.markdown(f"### 🔍 السؤال: {case['question']}")
    user_choice = st.radio("اختر استنتاجك:", case['options'])
    
    if st.button("تقديم التقرير النهائي"):
        if user_choice == case['correct_answer']:
            st.success("✅ مذهل! لقد قمت بحل القضية بنجاح.")
            st.balloons()
            st.info(f"📘 **المعلومة التعليمية:** {case['explanation']}")
            st.session_state.game_state = "finished"
        else:
            st.error("❌ استنتاج غير دقيق. الأدلة تشير إلى شيء آخر، حاول مرة أخرى!")

    if st.button("انسحاب من القضية 🚩"):
        st.session_state.game_state = "home"
        st.rerun()

elif st.session_state.game_state == "finished":
    st.button("بدء تحقيق في قضية جديدة 🔄", on_click=lambda: setattr(st.session_state, 'game_state', 'home'))
