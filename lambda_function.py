import random
import boto3
import json
import base64
from datetime import datetime, timedelta, timezone
import uuid
from boto3.dynamodb.conditions import Key, Attr

from constants import POOP_TRIVIA
from results_helper import (
    format_group_by_user_count,
    format_biggest_poop_day,
    format_longest_poop_streak,
    format_collective_most_poops,
)

print('Loading function')
dynamodb = boto3.resource('dynamodb', region_name="ap-southeast-1")
table = dynamodb.Table('poop-bot')

## poop wrapped - average poop per month, fav day to poop
## image - poop /heatmap (calmap, calplot for pandas/matplotlib)



def status_code_200():
    return {
        "statusCode": 200,
    }


def lambda_handler(event, context):
    decoded_body = base64.b64decode(event['body'])
    # print(decoded_body)
    update = json.loads(decoded_body)
    if 'message' not in update:
        print('Message not in update, returning.')
        return status_code_200()
    if 'text' not in update['message']:
        print('Text not in update["message"], returning.')
        return status_code_200()

    text = update['message']['text']
    if text is None:
        print('Text is None in update["message"], returning.')
        return status_code_200()

    chat_id = str(update['message']['chat']['id'])
    user_id = str(update['message']['from']['id'])
    username = update['message']['from']['username']
    print(f'[{chat_id}] {username} ({user_id}) said: {text}')
    if '/poop' in text:
        add_item(chat_id, user_id, username)
        return build_response(chat_id, f'OHYEA {username} has 💩!!!')
    elif '/unpoop' in text:
        item = delete_user_last_item(chat_id, user_id)
        if item == 0:
            return build_response(chat_id, f'{username} has not pooped! 😡')
        return build_response(chat_id, f'Erasing last 💩 for {username}')
    elif '/results' in text:
        summary = get_summary(chat_id)
        return build_response(chat_id, summary)
    elif '/trivia' in text:
        trivia = random.choice(POOP_TRIVIA)
        return build_response(chat_id, f'{trivia}\n\nForward to a friend to remind them to 💩!')
    return status_code_200()


def build_response(chat_id, text):
    body = {
        'method': 'sendMessage',
        'chat_id': chat_id,
        'parse_mode': 'HTML',
        'text': text,
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response


def add_item(chat_id: str, user_id: str, username: str):
    future_time = datetime.now(timezone.utc) + timedelta(days=395)
    # Convert to Unix epoch timestamp (in seconds)
    ttl_epoch = int(future_time.timestamp())

    table.put_item(
        Item={
            'ChatId': chat_id,
            'RecordId': str(uuid.uuid4()),
            'PoopTimestamp': datetime.now(timezone.utc).isoformat(),
            'UserId': user_id,
            'Username': username,
            'TTL': ttl_epoch
        }
    )


def delete_user_last_item(chat_id: str, user_id: str):
    response = table.query(
        IndexName='ChatId-PoopTimestamp-index',
        KeyConditionExpression=Key('ChatId').eq(chat_id),
        FilterExpression=Attr('UserId').eq(user_id),
        ScanIndexForward=False,  # Sort in descending order to get the latest item
        Limit=1  # Limit to 1 item
    )

    items = response.get('Items', [])
    if items:
        item_to_delete = items[0]
        table.delete_item(
            Key={
                'ChatId': item_to_delete['ChatId'],
                'RecordId': item_to_delete['RecordId']
            }
        )
        return 1
    return 0

def get_items_last_30_days(chat_id: str):
    items = []
    last_evaluated_key = None
    cutoff_timestamp = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
    while True:
        query_params = {
            "KeyConditionExpression": Key('ChatId').eq(chat_id),
            "FilterExpression": Attr("PoopTimestamp").gte(cutoff_timestamp)
        }

        if last_evaluated_key:
            query_params["ExclusiveStartKey"] = last_evaluated_key

        response = table.query(**query_params)
        
        items.extend(response.get("Items", []))
        last_evaluated_key = response.get("LastEvaluatedKey")
        if not last_evaluated_key:
            break


    return items

def get_summary(chat_id: str):
    items = get_items_last_30_days(chat_id)
    summary = ''
    if items:
        # Builds Counter, grouped by username
        summary += format_group_by_user_count(items)
        # Fun analytics

        summary += '\n\n'
        summary += format_biggest_poop_day(items)
        summary += '\n\n'
        summary += format_longest_poop_streak(items)
        summary += '\n\n'
        summary += format_collective_most_poops(items)
        return summary
    return 'No poops detected, poop first!'

