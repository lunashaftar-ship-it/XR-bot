import time
import html
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from jobspy import scrape_jobs

# ==================== [ CONFIGURATION & ACCOUNTS ] ====================
TELEGRAM_BOT_TOKEN = "8235854300:AAFOpRtf1fImlWRMxqbtWRdc0uyiOYhQZEw"
TELEGRAM_CHAT_ID = "7084743209"  

SENDER_EMAIL = "luna.shaftar@gmail.com"
SENDER_PASSWORD = "wvhfhkwiujskehgh"  
CV_FILE_PATH = "Khawla_shaftar_FlowCV_Resume_2026-05-25.pdf"

MAX_APPLICATIONS_PER_DAY = 50
MIN_MATCH_SCORE = 0.0                  # تم خفضها لضمان معالجة كل الوظائف
AUTO_EMAIL_THRESHOLD = 0.0             # 🔥 تم جعلها 0 ليرسل فوراً دون أي شروط معقدة لنسبة التوافق

# وكالات تورينو المعتمدة - إيميلات الطوارئ المباشرة
EMERGENCY_AGENCIES = [
    {"name": "Adecco Torino", "email": "torino.oropa@adecco.it"},
    {"name": "Randstad Torino", "email": "torino.technical@randstad.it"},
    {"name": "Manpower Torino", "email": "torino.gramsci@manpower.it"}
]

MY_PROFILE = """
Name: Khawla shaftar
Target Roles: Junior Full-Stack Developer, Junior Web Developer, Technical Project Lead
Location: Torino, Italy
Languages: Arabic (Native), English (B2), Italian (B1)

Technical Skills & Tech Stack:
- Frontend: TypeScript, JavaScript, Tailwind CSS, Responsive Design, HTML, CSS
- Backend & Databases: Prisma ORM, SQL, PHP, Python, JSON Data Management
- Project Management & UX: Trello (Agile/Scrum), Stakeholder Reporting, Strategic Reporting, Canva, Figma, User Experience (UX) principles
"""

BLACKLIST_KEYWORDS = ["senior", "sr.", "lead architect", "manager", "head", "principal", "expert"]
# =====================================================================

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

def search_google_for_company_email(company_name):
    print(f"🔍 Searching Google for {company_name} email...")
    query = f'"{company_name}" (HR OR careers OR recruitment OR "info") "email" @'
    url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', response.text)
            for email in emails:
                if not any(x in email.lower() for x in ['example', 'w3', 'bootstrap', 'domain', 'privacy', 'git', 'github', 'noreply']):
                    if email.lower().endswith(('.com', '.it', '.net')):
                        return email.lower()
    except: pass
    return None

def send_cv_via_email(company_name, job_title, recipient_email):
    if not recipient_email or "@" not in recipient_email:
        return False
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email
    msg['Subject'] = f"Application for {job_title if job_title else 'Junior Developer'} - Khawla Shaftar"
    
    body = f"""Dear Hiring Team at {company_name},

I hope this email finds you well. 

I am highly interested in contributing to your technical projects in Torino as a Junior Full-Stack Developer. Please find my attached resume for your review.

Best regards,
Khawla Shaftar
Phone: 3278073506
Website: https://lunashaftar-ship-it.github.io/website
"""
    msg.attach(MIMEText(body, 'plain'))
    try:
        with open(CV_FILE_PATH, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename= {CV_FILE_PATH}")
            msg.attach(part)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"✅ Email successfully sent to {recipient_email}")
        return True
    except Exception as e:
        print(f"⚠️ SMTP Error: {e}")
        return False

def check_job_suitability(title):
    for word in BLACKLIST_KEYWORDS:
        if word in title.lower() and "junior" not in title.lower():
            return False
    return True

def run_torino_job_system():
    print("🚀 System started. Forcing direct applications...")
    
    print("🌍 Scraping live job listings...")
    target_countries = ["italy", "switzerland"]
    all_scraped_jobs = []
    
    for country in target_countries:
        try:
            jobs_df = scrape_jobs(site_name=["linkedin", "indeed"], search_term="Full-Stack Developer", location="", results_wanted=15, hours_old=168, country_indeed=country)
            if not jobs_df.empty:
                all_scraped_jobs.extend(jobs_df.to_dict(orient='records'))
        except: continue

    sent_count = 0
    for row in all_scraped_jobs:
        if sent_count >= MAX_APPLICATIONS_PER_DAY: break

        title = str(row.get('title', ''))
        company = str(row.get('company', ''))
        job_url = str(row.get('job_url', ''))

        if not check_job_suitability(title): continue

        sent_count += 1
        
        # 1. محاولة البحث الفوري عن إيميل الشركة في جوجل
        detected_email = search_google_for_company_email(company)
        
        if detected_email:
            # لو وجد إيميل الشركة، يرسل لها مباشرة
            is_sent = send_cv_via_email(company, title, detected_email)
            status_text = f"✅ Sent directly to Company: {detected_email}" if is_sent else "❌ SMTP Failed"
        else:
            # 🔥 خطة الطوارئ: لو لم يجد إيميل الشركة، يرسل فوراً إلى إحدى وكالات تورينو المعتمدة نيابة عنها!
            agency = EMERGENCY_AGENCIES[sent_count % len(EMERGENCY_AGENCIES)]
            is_sent = send_cv_via_email(agency['name'], f"{title} at {company}", agency['email'])
            status_text = f"🏢 No Company Email. Sent CV to Agency: <b>{agency['name']} ({agency['email']})</b>"

        notification_text = (
            f"🔥 <b>LIVE APPLICATION DISPATCHED</b>\n\n"
            f"🏢 <b>Company:</b> {html.escape(company)}\n"
            f"💼 <b>Role:</b> {html.escape(title)}\n"
            f"📨 <b>Status:</b> {status_text}\n\n"
            f"🔗 <a href='{job_url}'>Open Posting</a>"
        )
        send_telegram_message(notification_text)
        time.sleep(5)  # انتظام زمني لحماية البريد

if __name__ == "__main__":
    run_torino_job_system()
