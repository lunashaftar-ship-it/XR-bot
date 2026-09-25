import os
import streamlit as st
from job_automator import ITALIAN_AGENCIES, TORINO_TECH_COMPANIES, send_cv_via_email

# إعدادات واجهة لوحة التحكم
st.set_page_config(page_title="Khawla's Job Dashboard", page_icon="🚀", layout="wide")

st.title("🚀 Khawla's Job Application Dashboard")
st.markdown("لوحة التحكم الخاصة بك في تورينو لإرسال طلبات التدريب (6-Month Internship) بالصيغة الإنجليزية الاحترافية وبضغطة زر واحدة.")

# تقسيم اللوحة إلى تبويبات للشركات والوكالات
tab1, tab2 = st.tabs(["🏢 Tech Companies", "🏛️ Agenzie per il Lavoro"])

with tab1:
    st.subheader("الشركات التقنية واستشارات IT في تورينو")
    st.write("الشركات المتاحة لإرسال طلب التدريب (التدريب لمدة 6 أشهر):")
    
    for idx, company in enumerate(TORINO_TECH_COMPANIES):
        col1, col2, col3 = st.columns([3, 3, 2])
        with col1:
            st.write(f"**{company['name']}**")
        with col2:
            st.write(f"📧 `{company['email']}`")
        with col3:
            # زر إرسال الإيميل بالصيغة الجديدة
            if st.button("إرسال الإيميل للشركة", key=f"tech_{idx}"):
                success = send_cv_via_email(company["name"], "", company["email"], is_direct_target=True)
                if success:
                    st.success(f"تم إرسال الإيميل بنجاح إلى {company['name']}!")
                else:
                    st.error(f"حدث خطأ أثناء الإرسال إلى {company['name']}.")
        st.divider()

with tab2:
    st.subheader("وكالات التوظيف المعتمدة (Agenzie per il Lavoro)")
    st.write("الفروع الرئيسية في تورينو المخصصة لخدمات التوظيف والتدريب:")
    
    for idx, agency in enumerate(ITALIAN_AGENCIES):
        col1, col2, col3 = st.columns([3, 3, 2])
        with col1:
            st.write(f"**{agency['name']}**")
        with col2:
            st.write(f"📧 `{agency['email']}`")
        with col3:
            if st.button("إرسال الإيميل للوكالة", key=f"agency_{idx}"):
                success = send_cv_via_email(agency["name"], "", agency["email"], is_direct_target=True)
                if success:
                    st.success(f"تم إرسال الإيميل بنجاح إلى {agency['name']}!")
                else:
                    st.error(f"حدث خطأ أثناء الإرسال إلى {agency['name']}.")
        st.divider()
