import time
import html
import requests
import schedule  # مكتبة الجدولة التلقائية
from jobspy import scrape_jobs

# ==================== [ CONFIGURATION ] ====================
TELEGRAM_BOT_TOKEN = "8235854300:AAFOpRtf1fImlWRMxqbtWRdc0uyiOYhQZEw"
TELEGRAM_CHAT_ID = "7084743209"  

BIG_TECH_COMPANIES = ["Apple", "Microsoft", "Amazon", "Google", "Meta"]
# ===========================================================

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

def monitor_big_tech_jobs():
    print("🔍 [AUTOMATIC RUN] Radar checking Big Tech Careers right now...")
    
    try:
        # نبحث عن الوظائف الجديدة جداً في آخر 24 ساعة لضمان عدم التكرار
        jobs_df = scrape_jobs(
            site_name=["linkedin", "indeed"],
            search_term="Developer",
            location="Italy",
            results_wanted=30,
            hours_old=24 
        )
    except Exception as e:
        print(f"⚠️ Scraper error: {e}")
        return

    if jobs_df.empty:
        print("📭 No new Big Tech postings found in this check.")
        return

    for row in jobs_df.to_dict(orient='records'):
        company = str(row.get('company', ''))
        title = str(row.get('title', ''))
        job_url = str(row.get('job_url', ''))
        location = str(row.get('location', 'Italy'))

        if any(tech_giant.lower() in company.lower() for tech_giant in BIG_TECH_COMPANIES):
            valid_keywords = ["software", "developer", "web", "frontend", "backend", "full-stack", "project", "lead", "engineer"]
            if any(key in title.lower() for key in valid_keywords):
                
                notification_text = (
                    f"🌟 <b>AUTOMATIC BIG TECH ALERT</b> 🌟\n\n"
                    f"🏢 <b>Company:</b> <b>{html.escape(company).upper()}</b>\n"
                    f"💼 <b>Role:</b> {html.escape(title)}\n"
                    f"📍 <b>Location:</b> {html.escape(location)}\n\n"
                    f"🔗 <a href='{job_url}'><b>Apply on Official Portal</b></a>"
                )
                
                send_telegram_message(notification_text)
                print(f"🎯 Auto-Alert sent for {company}")
                time.sleep(3)

# ==================== [ AUTOMATION ENGINE ] ====================

# جدولة الكود لكي يعمل تلقائياً كل 4 ساعات دون توقف
schedule.every(4).hours.do(monitor_big_tech_jobs)

# رسالة ترحيبية عند تشغيل السكربت لتأكيد أنه يعمل بنجاح
print("🤖 Big Tech Auto-Radar is now ONLINE and running in the background...")
send_telegram_message("🤖 <b>Big Tech Auto-Radar is now ONLINE!</b>\nI will scan for Apple, Amazon, and Microsoft jobs every 4 hours automatically.")

# تشغيل الفحص الأول فوراً عند تشغيل الكود لأول مرة
monitor_big_tech_jobs()

# حلقة لانهائية تجعل الكود مستيقظاً ويتابع الوقت
while True:
    schedule.run_pending()
    time.sleep(1) # ينام لمدة ثانية واحدة ثم يعيد التحقق من الساعة لتقليل استهلاك المعالج