import requests
import datetime
import os
import time
from dotenv import load_dotenv

load_dotenv()

NYT_S_COOKIE = os.getenv("NYT_S_COOKIE")
webhook_url = os.getenv("WEBHOOK_URL")


def get_wordle_puzzle():
    today = datetime.datetime.now()
    formatted_data = today.strftime("%Y-%m-%d")
    url = f"https://www.nytimes.com/svc/wordle/v2/{formatted_data}.json"
    response = requests.get(url)
    return response.json()


def get_user_stats(puzzle_id: str):
    url = f"https://www.nytimes.com/svc/games/state/wordleV2/latests?puzzle_ids={puzzle_id}"
    headers = {
        "Cookie": f"NYT-S={NYT_S_COOKIE}",
    }
    response = requests.get(url, headers=headers)
    return response.json()


def send_reminder():
    payload = {
        'content': '<@395923896039243788>', # Mention a user if you want using discord id.
        'embeds': [
            {
                'title': 'Wordle Reminder',
                'description': 'Don’t forget to complete the NYT Wordle today! 🗺️',
                'color': 0x2ECC71
            }
        ]
    }

    response = requests.post(webhook_url, json=payload)
    if response.status_code == 204:
        print('Reminder sent successfully!')
    else:
        print(f'Failed to send reminder: {response.status_code}, {response.text}')


def check_wordle():
    puzzle = get_wordle_puzzle()
    puzzle_id = puzzle.get("id")
    if not puzzle_id:
        return
    stats = get_user_stats(puzzle_id)
    for state in stats["states"]:
        if state["game"] == "wordleV2":
            game_data = state["game_data"]
            has_completed = game_data.get("status") != "IN_PROGRESS"
            if not has_completed:
                send_reminder()


while True:
    now = datetime.datetime.now()
    if (now.hour in [21, 22, 23]) and now.minute == 0:
        check_wordle()
        time.sleep(60)

    time.sleep(30)
