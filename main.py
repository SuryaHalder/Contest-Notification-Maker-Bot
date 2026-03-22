import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os

# Setup
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CLIST_USERNAME = os.getenv("CLIST_USERNAME")
CLIST_API_KEY = os.getenv("CLIST_API_KEY")

def format_duration(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    hour_part = f"{hours} hour" + ("s" if hours != 1 else "")
    if minutes > 0:
        return f"{hour_part} {minutes} minutes"
    return hour_part

def get_tomorrow_contests():
    """Fetches contests starting TOMORROW (IST) from CLIST."""
    url = f"https://clist.by:443/api/v4/contest/?upcoming=true&resource_id__in=1,2,93&order_by=start&username={CLIST_USERNAME}&api_key={CLIST_API_KEY}"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        contests = data.get("objects", [])
    except Exception as e:
        print(f"API Error: {e}")
        return []
    
    ist = ZoneInfo('Asia/Kolkata')
    
    #getting tommorow time.
    today = datetime.now(ist).date()
    tomorrow = today + timedelta(days=1)
    
    tomorrow_messages = []

    for contest in contests:
        utc_time = datetime.fromisoformat(contest['start']).replace(tzinfo=ZoneInfo('UTC'))
        dt_ist = utc_time.astimezone(ist)
        
        if dt_ist.date() == tomorrow:
            event_name = contest['event']
            if contest['resource_id'] == 2 and not event_name.startswith("CodeChef"):
                event_name = f"CodeChef {event_name}"
            
            day_num = dt_ist.day
            suffix = "th" if 11 <= day_num <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day_num % 10, "th")
            date_str = dt_ist.strftime(f"{day_num}{suffix} %B, %Y at %I:%M %p")
            
            msg = (
                f"{event_name} will start on {date_str} IST.\n"
                f"Contest duration is {format_duration(contest['duration'])}.\n\n"
                f"Contest link: {contest['href']}\n"
                f"Happy Coding! 😀"
            )
            tomorrow_messages.append(msg)
            
    return tomorrow_messages

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, json=payload)

if __name__ == "__main__":
    messages = get_tomorrow_contests()
    
    if messages:
        
        send_telegram_msg("📅 Upcoming Contests for Tomorrow:")
        for m in messages:
            send_telegram_msg(m)
    else:
        send_telegram_msg("No contests scheduled for tomorrow!")
