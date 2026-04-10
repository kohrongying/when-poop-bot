import random
import json
import base64
from typing import Any
from dynamodb import DbService
from constants import POOP_TRIVIA
from results_helper import build_summary
from wrapped import format_yearly_summary
from heatmap import generate_heatmap, get_presigned_url
from dataclasses import dataclass


def status_code_200():
    return {
        "statusCode": 200,
    }


@dataclass
class TelegramEvent:
    text: str
    chat_id: str
    user_id: str
    username: str


def get_telegram_event(event) -> TelegramEvent:
    decoded_body = base64.b64decode(event["body"])
    update = json.loads(decoded_body)
    if "message" not in update:
        print("Message not in update, returning.")
        return None
    if "text" not in update["message"]:
        print('Text not in update["message"], returning.')
        return None

    text = update["message"]["text"]
    if text is None:
        print('Text is None in update["message"], returning.')
        return None

    chat_id = str(update["message"]["chat"]["id"])
    user_id = str(update["message"]["from"]["id"])
    username = update["message"]["from"]["username"]
    print(f"[{chat_id}] {username} ({user_id}) said: {text}")

    return TelegramEvent(text=text, chat_id=chat_id, user_id=user_id, username=username)


def lambda_handler(event, context):
    telegram_event = get_telegram_event(event)
    if telegram_event is None:
        return status_code_200()
    text = telegram_event.text

    db_service = DbService()

    if "/unpoop" in text:
        return handle_unpoop_event(db_service, telegram_event)
    elif "/results" in text:
        return handle_results_event(db_service, telegram_event)
    elif "/pooptrivia" in text:
        return handle_trivia_event(telegram_event)
    elif "/poopwrapped" in text:
        return handle_wrapped_event(db_service, telegram_event)
    elif "/poopmap" in text:
        return handle_poopmap_event(db_service, telegram_event)
    elif "/poop" in text:
        return handle_poop_event(db_service, telegram_event)
    return status_code_200()


def build_response(chat_id, text) -> dict[str, Any]:
    body = {
        "method": "sendMessage",
        "chat_id": chat_id,
        "parse_mode": "HTML",
        "text": text,
    }

    return {"statusCode": 200, "body": json.dumps(body)}


def build_photo_response(chat_id, photo, caption) -> dict[str, Any]:
    body = {
        "method": "sendPhoto",
        "chat_id": chat_id,
        "parse_mode": "HTML",
        "caption": caption,
        "photo": photo,
    }

    return {"statusCode": 200, "body": json.dumps(body)}


def handle_poop_event(
    db_service: DbService, telegram_event: TelegramEvent
) -> dict[str, Any]:
    db_service.add_item(
        telegram_event.chat_id, telegram_event.user_id, telegram_event.username
    )
    return build_response(
        telegram_event.chat_id, f"OHYEA {telegram_event.username} has 💩!!!"
    )


def handle_unpoop_event(
    db_service: DbService, telegram_event: TelegramEvent
) -> dict[str, Any]:
    item = db_service.delete_user_last_item(
        telegram_event.chat_id, telegram_event.user_id
    )
    if item == 0:
        return build_response(
            telegram_event.chat_id, f"{telegram_event.username} has not pooped! 😡"
        )
    return build_response(
        telegram_event.chat_id, f"Erasing last 💩 for {telegram_event.username}"
    )


def handle_trivia_event(telegram_event: TelegramEvent) -> dict[str, Any]:
    trivia = random.choice(POOP_TRIVIA)
    return build_response(
        telegram_event.chat_id, f"{trivia}\n\nForward to a friend to remind them to 💩!"
    )


def handle_results_event(
    db_service: DbService, telegram_event: TelegramEvent
) -> dict[str, Any]:
    items = db_service.get_items_last_num_days(telegram_event.chat_id, num_days=30)
    if items:
        summary = build_summary(items)
        return build_response(telegram_event.chat_id, summary)
    return build_response(telegram_event.chat_id, "No poops detected, poop first!")


def handle_wrapped_event(db_service: DbService, telegram_event: TelegramEvent):
    items = db_service.get_items_from_year_to_date(telegram_event.chat_id)
    if items:
        res = format_yearly_summary(
            items, telegram_event.user_id, telegram_event.username
        )
        return build_response(telegram_event.chat_id, res)
    return build_response(telegram_event.chat_id, "No poops detected, poop first!")


def handle_poopmap_event(db_service: DbService, telegram_event: TelegramEvent):
    items = db_service.get_items_from_year_to_date(telegram_event.chat_id)
    if items:
        filename = generate_heatmap(items, telegram_event.user_id)
        presigned_url = get_presigned_url(filename)
        return build_photo_response(
            telegram_event.chat_id, presigned_url, f"{telegram_event.username} Poop Map"
        )
    return build_response(telegram_event.chat_id, "No poops detected, poop first!")
