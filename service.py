import requests
import time
import schedule
from dotenv import load_dotenv
import os

load_dotenv()



# --- CONFIGURATION ---
DELTA_API_URL = "https://api.india.delta.exchange/v2/tickers"
TELEGRAM_BOT_TOKEN = os.getenv('TOKEN')
TELEGRAM_USER_ID = os.getenv('USER_ID')

def get_market_data():
    params1={'contract_types':'perpetual_futures'}
    response = requests.get(DELTA_API_URL,params=params1)
    response.raise_for_status()
    return response.json()['result']

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_USER_ID,
        "text": message
    }
    requests.post(url, data=payload)

def check_gainers():
    tickers = get_market_data()
    gainers = []
    for ticker in tickers:
        try:
            change = float(ticker.get('mark_change_24h', 0))
            if change >= 100.0:  # 100% gain means +1.0 in pct_24h
                gainers.append(ticker.get('symbol', 'NA'))
        except Exception:
            continue
    if gainers:
        message = "Coins that gained >100% in 24h:\n" + "\n".join(gainers)
        send_telegram_message(message)
    else:
        message="No coin gained above 100%!"
        send_telegram_message(message)

# Schedule to run every hour
schedule.every(1).hours.do(check_gainers)

if __name__ == "__main__":
    check_gainers()
    while True:
        schedule.run_pending()
        time.sleep(60)
