import os
import json
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

BASE_API = "https://khakhi-ni-khumari.lovable.app/api/public/pdfs"
CONFIG_FILE = "config.json"

def load_last_date():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return datetime.strptime(json.load(f)["last_sent_date"], "%Y-%m-%d")

def save_last_date(dt):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_sent_date": dt.strftime("%Y-%m-%d")}, f, indent=2)

def send_to_telegram(pdf_bytes, filename, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    files = {"document": (filename, pdf_bytes, "application/pdf")}
    data = {"chat_id": CHANNEL_ID, "caption": caption}
    r = requests.post(url, data=data, files=files)
    r.raise_for_status()

def main():
    current = load_last_date() + relativedelta(days=1)

    while True:
        date_str = current.strftime("%Y-%m-%d")
        api = f"{BASE_API}/daily-{date_str}"
        print("Checking:", api)

        r = requests.get(api)
        if r.status_code != 200:
            print("No more PDFs found.")
            break

        # TODO: Adjust these keys to match your API response.
        data = r.json()
        pdf_url = data.get("pdfUrl") or data.get("url")

        if not pdf_url:
            print("PDF URL missing in API response.")
            break

        pdf = requests.get(pdf_url)
        pdf.raise_for_status()

        caption = f"📚 Daily Current Affairs\n📅 {date_str}"
        send_to_telegram(pdf.content, f"daily-{date_str}.pdf", caption)

        save_last_date(current)
        print("Sent:", date_str)

        current += relativedelta(days=1)

if __name__ == "__main__":
    main()
