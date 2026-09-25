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
CV_FILE_PATH = "CV_Khawla_Shaftar.pdf"

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
Name: Khawla Shaftar
Target Roles: Junior Full-Stack Developer, Junior Web Developer, Junior Frontend Developer, Junior Backend Developer, Junior Ai Developer, Junior Software Engineer, Junior Data Engineer, Junior Data Analyst
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
    msg["Subject"] = "Application for a 6-Month Web Development Internship - Khawla Shaftar"
  else:
    msg["Subject"] = f"Application for {job_title} - Khawla Shaftar"

  body = f"""Dear HR Team,

I am writing to express my interest in a 6-month internship opportunity as a Junior Web Developer at {company_name}.

I recently completed an intensive digital web development training program at Enaip Piemonte, where I gained strong foundations in modern tech stacks—including TypeScript, Tailwind CSS, Prisma ORM, and relational databases—along with core skills in HTML, CSS, JavaScript, and Python. During my studies, I also led a student development team as a Technical Project Lead, managing Agile workflows, project roadmaps, and AI-integrated coding practices.

The internship can be easily set up through official educational and employment support channels (such as GOL or Enaip frameworks), and I am fully flexible regarding the arrangement, focusing primarily on gaining hands-on experience and contributing to real-world projects.

I have attached my updated CV for your review. I would welcome the opportunity to discuss how my background and enthusiasm could add value to your team.

Thank you for your time and consideration.

Best regards,

Khawla Shaftar
Phone: +39 3278073506
Portfolio: https://lunashaftar-ship-it.github.io/website
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
