from datetime import datetime, timedelta, timezone, date
import boto3
import uuid
from boto3.dynamodb.conditions import Key, Attr


class DbService:
    def __init__(self):
        dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-1")
        self.table = dynamodb.Table("poop-bot")

    def add_item(self, chat_id: str, user_id: str, username: str):
        future_time = datetime.now(timezone.utc) + timedelta(days=395)
        # Convert to Unix epoch timestamp (in seconds)
        ttl_epoch = int(future_time.timestamp())

        self.table.put_item(
            Item={
                "ChatId": chat_id,
                "RecordId": str(uuid.uuid4()),
                "PoopTimestamp": datetime.now(timezone.utc).isoformat(),
                "UserId": user_id,
                "Username": username,
                "TTL": ttl_epoch,
            }
        )

    def delete_user_last_item(self, chat_id: str, user_id: str):
        response = self.table.query(
            IndexName="ChatId-PoopTimestamp-index",
            KeyConditionExpression=Key("ChatId").eq(chat_id),
            FilterExpression=Attr("UserId").eq(user_id),
            ScanIndexForward=False,  # Sort in descending order to get the latest item
            Limit=1,  # Limit to 1 item
        )

        items = response.get("Items", [])
        if items:
            item_to_delete = items[0]
            self.table.delete_item(
                Key={
                    "ChatId": item_to_delete["ChatId"],
                    "RecordId": item_to_delete["RecordId"],
                }
            )
            return 1
        return 0

    def get_items_last_num_days(self, chat_id: str, num_days: int):
        items = []
        last_evaluated_key = None
        cutoff_timestamp = (
            datetime.now(timezone.utc) - timedelta(days=num_days)
        ).strftime("%Y-%m-%d")
        while True:
            query_params = {
                "KeyConditionExpression": Key("ChatId").eq(chat_id),
                "FilterExpression": Attr("PoopTimestamp").gte(cutoff_timestamp),
            }

            if last_evaluated_key:
                query_params["ExclusiveStartKey"] = last_evaluated_key

            response = self.table.query(**query_params)

            items.extend(response.get("Items", []))
            last_evaluated_key = response.get("LastEvaluatedKey")
            if not last_evaluated_key:
                break
        return items

    def get_items_from_year_to_date(self, chat_id: str):
        today = date.today()
        start_of_year = date(today.year, 1, 1)
        days_from_start = (today - start_of_year).days + 1  # +1 to include Jan 1
        return self.get_items_last_num_days(chat_id, num_days=days_from_start)
