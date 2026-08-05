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
        data = json.load(f)
    return datetime.strptime(data["last_sent_date"], "%Y-%m-%d")


def save_last_date(dt):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {"last_sent_date": dt.strftime("%Y-%m-%d")},
            f,
            indent=2
        )


def send_to_telegram(pdf_bytes, filename, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"

    files = {
        "document": (filename, pdf_bytes, "application/pdf")
    }

    data = {
    "chat_id": CHANNEL_ID,
    "caption": caption,
    "parse_mode": "HTML"
    }

    response = requests.post(
        url,
        data=data,
        files=files,
        timeout=120
    )

    response.raise_for_status()


def main():
    current = load_last_date() + relativedelta(days=1)

    while True:

        date_str = current.strftime("%Y-%m-%d")

        download_url = (
            f"{BASE_API}/daily-{date_str}?dl=1"
        )

        print("Checking:", download_url)

        response = requests.get(
            download_url,
            timeout=120,
            allow_redirects=True
        )

        if response.status_code != 200:
            print("No PDF Found.")
            break

        content_type = response.headers.get(
            "Content-Type",
            ""
        ).lower()

        if (
            "pdf" not in content_type
            and not response.content.startswith(b"%PDF")
        ):
            print("Response is not PDF.")
            break

        caption = (
    f"📚 Daily Current Affairs\n"
    f"📅 {date_str}\n\n"
    f'🌐 <a href="https://khakhi-ni-khumari.lovable.app">Visit Website</a>'
)

        send_to_telegram(
            response.content,
            f"Daily_Current_Affairs_{date_str}.pdf",
            caption
        )

        save_last_date(current)

        print("Sent:", date_str)

        current += relativedelta(days=1)


if __name__ == "__main__":
    main()
