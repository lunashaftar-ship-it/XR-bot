import time
import random
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

# Real Email Configuration
SENDER_EMAIL = "luna.shaftar@gmail.com"
SENDER_PASSWORD = "wvhfhkwiujskehgh"  # تأكدي من وضع الرمز السري هنا بدون مسافات
CV_FILE_PATH = "Khawla_shaftar_FlowCV_Resume_2026-05-25.pdf"

MAX_APPLICATIONS_PER_DAY = 50
MIN_MATCH_SCORE = 5.0                
AUTO_EMAIL_THRESHOLD = 25.0          

# Phase 1: Verified Agenzie per il Lavoro (Torino Branches / Tech divisions)
ITALIAN_AGENCIES = [
    {"name": "Adecco Torino", "email": "torino.oropa@adecco.it"},
    {"name": "Randstad Torino Tech", "email": "torino.technical@randstad.it"},
    {"name": "Manpower Torino", "email": "torino.gramsci@manpower.it"},
    {"name": "Synergie Italia Torino", "email": "torino1@synergie-italia.it"},
    {"name": "Gi Group Torino", "email": "torino.marconi@gigroup.com"},
    {"name": "Umana Torino", "email": "infoto@umana.it"},
    {"name": "Openjobmetis Torino", "email": "torino@openjobmetis.it"},
    {"name": "Orienta Torino", "email": "torino@orienta.net"},
    {"name": "Ali Spa Torino", "email": "info.to@alispa.it"}
]

# Phase 2: Verified Tech & IT Consulting Companies in Torino (Direct HR / Careers)
TORINO_TECH_COMPANIES = [
    {"name": "Reply Spa (Torino Main Hub)", "email": "job@reply.it"},
    {"name": "Alten Italia (Torino Division)", "email": "hr-recruiting@alten.it"},
    {"name": "Capgemini Italia (Torino HR)", "email": "recruitment.it@capgemini.com"},
    {"name": "Engineering Ingegneria Informatica", "email": "scuola.it@eng.it"},
    {"name": "AizoOn Technology Consulting", "email": "recruitment@aizoon.it"},
    {"name": "Concepts Audio Video (Torino Tech)", "email": "hr@concepts.it"},
    {"name": "Arancia-ICT Torino", "email": "job@arancia-ict.it"},
    {"name": "Bitrock Tech Torino", "email": "hr@bitrock.it"},
    {"name": "Synchrono IT Torino", "email": "recruiting@synchrono.it"},
    {"name": "Neosperience (Torino Careers)", "email": "careers@neosperience.com"}
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
- AI Capabilities: AI-Assisted Development, AI Tools Integration, Prompt Engineering
"""

BLACKLIST_KEYWORDS = ["senior", "sr.", "lead architect", "manager", "head", "principal", "expert"]
# =====================================================================

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML", "disable_web_page_preview": False}
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Telegram Error: {e}")

def send_cv_via_email(company_name, job_title, recipient_email, is_direct_target=False):
    if SENDER_PASSWORD == "YOUR_GMAIL_APP_PASSWORD" or SENDER_PASSWORD == "":
        print(f"ℹ️ SMTP Skipped for {company_name}: Google App Password not configured.")
        return False

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email
    
    if is_direct_target:
        msg['Subject'] = f"Candidatura spontanea Junior Full-Stack Developer - Khawla Shaftar"
        body = f"""Gentile Team delle Risorse Umane di {company_name},

Mi chiamo Khawla Shaftar, sono una Junior Full-Stack Developer e Technical Project Lead residente a Torino. 

Vi contatto per presentare la mia candidatura spontanea presso la Vostra azienda, in quanto apprezzo molto i vostri progetti tecnologici e il vostro impatto nel settore IT a Torino.

Ho competenze esercitate nello sviluppo web con tecnologie quali TypeScript, JavaScript, Python, PHP, SQL, Prisma ORM e Tailwind CSS, unite a solide basi di gestione tecnica dei progetti (Agile/Scrum).

In allegato invio il mio Curriculum Vitae per una Vostra valutazione. Resto a completa disposizione per un eventuale colloquio conoscitivo.

Cordiali saluti,
Khawla Shaftar
Telefono: 3278073506
Sito web: https://lunashaftar-ship-it.github.io/website
"""
    else:
        msg['Subject'] = f"Application for {job_title} - Khawla Shaftar"
        body = f"""Dear Hiring Team at {company_name},

I hope this email finds you well. 

I recently came across your opening for the {job_title} position. Given my background as a Junior Full-Stack Developer and Technical Project Lead, I am highly interested in contributing to your team.

Please find my attached resume for your review. I would welcome the opportunity to discuss how my technical stack can align with your current goals.

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
        return True
    except Exception as e:
        print(f"⚠️ SMTP Error for {company_name}: {e}")
        return False

def check_job_suitability(title, description):
    for word in BLACKLIST_KEYWORDS:
        if word in title.lower():
            if "junior" not in title.lower() and "project lead" not in title.lower():
                return False
    for i in range(4, 15):
        if f"{i}+ years" in description.lower() or f"{i} years experience" in description.lower() or f"{i} anni di esperienza" in description.lower():
            return False
    return True

def extract_email_from_text(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else None

def run_torino_job_system():
    print("🚀 System active. Executing Torino Local Blaster (Agencies & Tech Companies)...")
    
    # 1. PROCESS TORINO AGENCIES
    for agency in ITALIAN_AGENCIES:
        success = send_cv_via_email(agency['name'], "", agency['email'], is_direct_target=True)
        if success:
            send_telegram_message(f"🏢 <b>[AGENZIA - TORINO]</b>\n✅ CV Sent to: {agency['name']}\n📩 {agency['email']}")
            time.sleep(3)

    # 2. PROCESS TORINO TECH COMPANIES
    for company in TORINO_TECH_COMPANIES:
        success = send_cv_via_email(company['name'], "", company['email'], is_direct_target=True)
        if success:
            send_telegram_message(f"💻 <b>[TECH COMPANY - TORINO]</b>\n✅ Direct CV Sent to: {company['name']}\n📩 {company['email']}")
            time.sleep(3)

    # 3. SCRAPE ONLINE LIVE POSTINGS
    print("🌍 Scraping online portals for live Full-Stack job posts...")
    target_countries = ["italy", "switzerland", "france", "germany", "uk"]
    all_scraped_jobs = []
    
    for country in target_countries:
        try:
            jobs_df = scrape_jobs(site_name=["linkedin", "indeed"], search_term="Full-Stack Developer", location="", results_wanted=15, hours_old=168, country_indeed=country)
            if not jobs_df.empty:
                all_scraped_jobs.extend(jobs_df.to_dict(orient='records'))
            time.sleep(2)
        except Exception:
            continue

    if not all_scraped_jobs:
        print("✅ Finished local target list.")
        return

    vectorizer = TfidfVectorizer()
    sent_count = 0

    for row in all_scraped_jobs:
        if sent_count >= MAX_APPLICATIONS_PER_DAY:
            break

        title = str(row.get('title', ''))
        company = str(row.get('company', ''))
        description = str(row.get('description', ''))
        job_url = str(row.get('job_url', ''))

        if not check_job_suitability(title, description):
            continue

        text_data = [MY_PROFILE, description]
        count_matrix = vectorizer.fit_transform(text_data)
        score = cosine_similarity(count_matrix)[0][1] * 100

        if score >= MIN_MATCH_SCORE:
            sent_count += 1
            detected_email = extract_email_from_text(description)
            email_status_text = "❌ No email address found in posting."
            
            if score >= AUTO_EMAIL_THRESHOLD:
                action_title = "🔥 <b>HIGH MATCH (>= 25%) - AUTO APPLY</b>"
                if detected_email:
                    is_sent_successfully = send_cv_via_email(company, title, detected_email, is_direct_target=False)
                    if is_sent_successfully:
                        email_status_text = f"✅ <b>CV sent to: {detected_email}!</b>"
            else:
                action_title = "ℹ️ Standard Low-Match Alert"

            notification_text = (
                f"{action_title}\n\n"
                f"🏢 <b>Company:</b> {html.escape(company)}\n"
                f"💼 <b>Role Title:</b> {html.escape(title)}\n"
                f"📊 <b>AI Match Score:</b> {score:.1f}%\n"
                f"📨 <b>Real Email Status:</b> {email_status_text}\n\n"
                f"🔗 <a href='{job_url}'><b>Open Posting</b></a>"
            )
            send_telegram_message(notification_text)
            time.sleep(3)

    print(f"✅ Sweep completed successfully.")

if __name__ == "__main__":
    run_torino_job_system()