import os
import re
import smtplib
import time
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
from jobspy import scrape_jobs
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ==================== [ CONFIGURATION & ACCOUNTS ] ====================
SENDER_EMAIL = "luna.shaftar@gmail.com"
SENDER_PASSWORD = "wvhfhkwiujskehgh"
CV_FILE_PATH = "Khawla_shaftar_FlowCV_Resume_2026-05-25.pdf"

MAX_APPLICATIONS_PER_DAY = 50
MIN_MATCH_SCORE = 5.0
AUTO_EMAIL_THRESHOLD = 25.0

ITALIAN_AGENCIES = [
    {"name": "Adecco Torino", "email": "torino.oropa@adecco.it"},
    {"name": "Randstad Torino Tech", "email": "torino.technical@randstad.it"},
    {"name": "Manpower Torino", "email": "torino.gramsci@manpower.it"},
    {"name": "Synergie Italia Torino", "email": "torino1@synergie-italia.it"},
    {"name": "Gi Group Torino", "email": "torino.marconi@gigroup.com"},
    {"name": "Umana Torino", "email": "infoto@umana.it"},
    {"name": "Openjobmetis Torino", "email": "torino@openjobmetis.it"},
    {"name": "Orienta Torino", "email": "torino@orienta.net"},
    {"name": "Ali Spa Torino", "email": "info.to@alispa.it"},
]

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
    {"name": "Neosperience (Torino Careers)", "email": "careers@neosperience.com"},
    {"name": "Speed2Net Torino", "email": "info@speed2net.it"},
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

BLACKLIST_KEYWORDS = [
    "senior",
    "sr.",
    "lead architect",
    "manager",
    "head",
    "principal",
    "expert",
]
# =====================================================================


def send_cv_via_email(
    company_name, job_title, recipient_email, is_direct_target=False
):
  if not os.path.exists(CV_FILE_PATH):
    print(f"❌ Error: CV file '{CV_FILE_PATH}' not found!")
    return False

  msg = MIMEMultipart()
  msg["From"] = SENDER_EMAIL
  msg["To"] = recipient_email

  if is_direct_target:
    msg["Subject"] = (
        "Candidatura spontanea Junior Full-Stack Developer - Khawla Shaftar"
    )
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
    msg["Subject"] = f"Application for {job_title} - Khawla Shaftar"
    body = f"""Dear Hiring Team at {company_name},

I hope this email finds you well. 

I recently came across your opening for the {job_title} position. Given my background as a Junior Full-Stack Developer and Technical Project Lead, I am highly interested in contributing to your team.

Please find my attached resume for your review. I would welcome the opportunity to discuss how my technical stack can align with your current goals.

Best regards,
Khawla Shaftar
Phone: 3278073506
Website: https://lunashaftar-ship-it.github.io/website
"""

  msg.attach(MIMEText(body, "plain"))

  try:
    with open(CV_FILE_PATH, "rb") as attachment:
      part = MIMEBase("application", "octet-stream")
      part.set_payload(attachment.read())
      encoders.encode_base64(part)
      part.add_header(
          "Content-Disposition",
          f"attachment; filename= {os.path.basename(CV_FILE_PATH)}",
      )
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


def ask_user_approval(company_name, email, job_title=""):
  print("\n" + "=" * 50)
  print(f"🏢 Company: {company_name}")
  if job_title:
    print(f"💼 Role: {job_title}")
  print(f"📩 Target Email: {email}")
  print("=" * 50)

  choice = (
      input("Do you want to send the CV to this company? (y/n/q to quit): ")
      .strip()
      .lower()
  )
  if choice == "y":
    return True
  elif choice == "q":
    print("Exiting program...")
    exit()
  return False


def run_torino_job_system():
  print(
      "🚀 Interactive System active. Reviewing Torino Agencies & Tech"
      " Companies..."
  )

  # 1. PROCESS TORINO AGENCIES (Interactive)
  for agency in ITALIAN_AGENCIES:
    if ask_user_approval(agency["name"], agency["email"]):
      success = send_cv_via_email(
          agency["name"], "", agency["email"], is_direct_target=True
      )
      if success:
        print(f"✅ CV Successfully Sent to {agency['name']}!")
      else:
        print(f"❌ Failed to send to {agency['name']}.")
    else:
      print("⏭️ Skipped.")

  # 2. PROCESS TORINO TECH COMPANIES (Interactive)
  for company in TORINO_TECH_COMPANIES:
    if ask_user_approval(company["name"], company["email"]):
      success = send_cv_via_email(
          company["name"], "", company["email"], is_direct_target=True
      )
      if success:
        print(f"✅ CV Successfully Sent to {company['name']}!")
      else:
        print(f"❌ Failed to send to {company['name']}.")
    else:
      print("⏭️ Skipped.")

  # 3. SCRAPE ONLINE LIVE POSTINGS (Interactive Review)
  print("\n🌍 Scraping online portals for live Full-Stack job posts...")
  target_countries = ["italy", "france", "germany"]
  all_scraped_jobs = []

  for country in target_countries:
    try:
      jobs_df = scrape_jobs(
          site_name=["linkedin", "indeed"],
          search_term="Full-Stack Developer",
          location="Torino",
          results_wanted=10,
          hours_old=168,
          country_indeed=country,
      )
      if jobs_df is not None and not jobs_df.empty:
        all_scraped_jobs.extend(jobs_df.to_dict(orient="records"))
      time.sleep(2)
    except Exception as e:
      print(f"⚠️ Scraping error for {country}: {e}")
      continue

  if not all_scraped_jobs:
    print("✅ Finished online sweep.")
    return

  vectorizer = TfidfVectorizer()

  for row in all_scraped_jobs:
    title = str(row.get("title", ""))
    company = str(row.get("company", ""))
    description = str(row.get("description", ""))
    job_url = str(row.get("job_url", ""))

    text_data = [MY_PROFILE, description]
    count_matrix = vectorizer.fit_transform(text_data)
    score = cosine_similarity(count_matrix)[0][1] * 100

    if score >= MIN_MATCH_SCORE:
      detected_email = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", description)
      email_to_use = (
          detected_email.group(0) if detected_email else "No email found in text"
      )

      print("\n" + "~" * 50)
      print(f"🔥 Found Online Job Match!")
      print(f"🏢 Company: {company}")
      print(f"💼 Role: {title}")
      print(f"📊 AI Match Score: {score:.1f}%")
      print(f"📩 Extracted Email: {email_to_use}")
      print(f"🔗 URL: {job_url}")
      print("~" * 50)

      if detected_email:
        choice = (
            input("Send CV to this job? (y/n/q to quit): ").strip().lower()
        )
        if choice == "y":
          success = send_cv_via_email(
              company, title, email_to_use, is_direct_target=False
          )
          if success:
            print("✅ CV Sent successfully!")
          else:
            print("❌ Failed to send.")
        elif choice == "q":
          break
      else:
        print("ℹ️ No direct email found for this posting, skipping auto-send.")

  print(f"\n✅ All tasks completed.")


if __name__ == "__main__":
  run_torino_job_system()

