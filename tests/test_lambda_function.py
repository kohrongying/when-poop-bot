import pytest
import json
import base64
from datetime import datetime, timedelta, timezone
from moto import mock_aws
import boto3
import uuid
from lambda_function import lambda_handler

TEST_USERNAME = "testuser"
TEST_USER_ID = "789"
TEST_CHAT_ID = "123456"


@pytest.fixture
def sample_telegram_event(text="/poop"):
    update = {
        "message": {
            "text": text,
            "chat": {"id": TEST_CHAT_ID},
            "from": {"id": TEST_USER_ID, "username": TEST_USERNAME},
        }
    }
    body = json.dumps(update).encode()
    encoded_body = base64.b64encode(body).decode()
    return {"body": encoded_body}


@pytest.fixture(scope="session")
def make_telegram_event():
    def _make_event(
        text="/poop", chat_id=TEST_CHAT_ID, user_id=TEST_USER_ID, username=TEST_USERNAME
    ):
        event = {
            "message": {
                "text": text,
                "chat": {"id": chat_id},
                "from": {"id": user_id, "username": username},
            }
        }
        body = json.dumps(event).encode()
        encoded_body = base64.b64encode(body).decode()
        return {"body": encoded_body}

    yield _make_event


@pytest.fixture(autouse=True)
def ddb_table():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-1")

        table = dynamodb.create_table(
            TableName="poop-bot",
            KeySchema=[
                {"AttributeName": "ChatId", "KeyType": "HASH"},
                {"AttributeName": "RecordId", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "ChatId", "AttributeType": "S"},
                {"AttributeName": "RecordId", "AttributeType": "S"},
                {"AttributeName": "PoopTimestamp", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "ChatId-PoopTimestamp-index",
                    "KeySchema": [
                        {"AttributeName": "ChatId", "KeyType": "HASH"},
                        {"AttributeName": "PoopTimestamp", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
        )
        yield table


@pytest.fixture
def s3_client():
    with mock_aws():
        yield boto3.client("s3", region_name="ap-southeast-1")


@mock_aws
class TestLambdaHandlerBasic:
    """Test basic lambda handler functionality."""

    def test_lambda_handler_missing_message(self):
        """Test handler when message is missing."""
        from lambda_function import lambda_handler

        event = {"body": base64.b64encode(json.dumps({}).encode()).decode()}
        response = lambda_handler(event, None)
        assert response["statusCode"] == 200

    def test_lambda_handler_missing_text(self):
        """Test handler when text is missing."""
        from lambda_function import lambda_handler

        update = {
            "message": {
                "chat": {"id": 123456},
                "from": {"id": 789, "username": "testuser"},
            }
        }
        body = json.dumps(update).encode()
        encoded_body = base64.b64encode(body).decode()
        event = {"body": encoded_body}
        response = lambda_handler(event, None)
        assert response["statusCode"] == 200

    def test_lambda_handler_none_text(self):
        """Test handler when text is None."""
        from lambda_function import lambda_handler

        update = {
            "message": {
                "text": None,
                "chat": {"id": 123456},
                "from": {"id": 789, "username": "testuser"},
            }
        }
        body = json.dumps(update).encode()
        encoded_body = base64.b64encode(body).decode()
        event = {"body": encoded_body}
        response = lambda_handler(event, None)
        assert response["statusCode"] == 200


class TestPoopCommand:
    def test_poop_command(self, make_telegram_event, ddb_table):
        # GIVEN a /poop command event and WHEN
        response = lambda_handler(make_telegram_event(), None)

        # Verify message is sent
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["method"] == "sendMessage"
        assert "OHYEA testuser has 💩" in body["text"]

        # Verify item was added to DynamoDB
        items = ddb_table.scan()["Items"]
        assert len(items) == 1
        assert items[0]["UserId"] == TEST_USER_ID
        assert items[0]["Username"] == TEST_USERNAME
        assert items[0]["ChatId"] == TEST_CHAT_ID
        assert uuid.UUID(items[0]["RecordId"])
        assert datetime.fromisoformat(items[0]["PoopTimestamp"]) is not None


class TestUnpoopCommand:
    def test_unpoop_removes_last_item(self, make_telegram_event, ddb_table):
        from dynamodb import DbService

        # GIVEN user has existing items and a /unpoop command event
        DbService().add_item(TEST_CHAT_ID, TEST_USER_ID, TEST_USERNAME)

        items_before = ddb_table.scan()["Items"]
        assert len(items_before) == 1

        event = make_telegram_event(text="/unpoop")

        # WHEN
        response = lambda_handler(event, None)

        # THEN
        assert response["statusCode"] == 200
        response_body = json.loads(response["body"])
        assert "Erasing last 💩 for testuser" in response_body["text"]

        # Verify item was deleted
        items_after = ddb_table.scan()["Items"]
        assert len(items_after) == 0

    def test_unpoop_on_empty_user(self, make_telegram_event, ddb_table):
        # GIVEN user has no existing items and a /unpoop command event
        event = make_telegram_event(text="/unpoop")

        # WHEN
        response = lambda_handler(event, None)

        # THEN
        response_body = json.loads(response["body"])
        assert "testuser has not pooped! 😡" in response_body["text"]


class TestTrivia:
    def test_pooptrivia_command(self, make_telegram_event):
        from constants import POOP_TRIVIA

        # GIVEN
        event = make_telegram_event(text="/pooptrivia")

        # WHEN
        response = lambda_handler(event, None)

        # THEN
        assert response["statusCode"] == 200
        response_body = json.loads(response["body"])
        assert response_body["method"] == "sendMessage"
        assert "Forward to a friend" in response_body["text"]
        assert any(trivia in response_body["text"] for trivia in POOP_TRIVIA)


class TestResultsCommand:
    def test_results_with_data(self, make_telegram_event, ddb_table):
        from dynamodb import DbService

        db_service = DbService()
        # GIVEN

        db_service.add_item(TEST_CHAT_ID, TEST_USER_ID, TEST_USERNAME)
        db_service.add_item(TEST_CHAT_ID, TEST_USER_ID, TEST_USERNAME)
        ANOTHER_USER_ID = "790"
        ANOTHER_USERNAME = "anotheruser"
        db_service.add_item(TEST_CHAT_ID, ANOTHER_USER_ID, ANOTHER_USERNAME)

        event = make_telegram_event(text="/results")

        # WHEN
        response = lambda_handler(event, None)

        # THEN
        assert response["statusCode"] == 200
        response_body = json.loads(response["body"])
        assert response_body["method"] == "sendMessage"
        assert """💩💩💩 Counter as follows in the past 30 days

testuser: 2 💩
anotheruser: 1 💩""" in response_body["text"]

    def test_results_no_data(self, make_telegram_event):

        event = make_telegram_event(text="/results")

        response = lambda_handler(event, None)
        response_body = json.loads(response["body"])
        assert "No poops detected, poop first!" in response_body["text"]


class TestMapCommand:
    def test_poopmap_command_no_data(self, make_telegram_event, ddb_table, s3_client):
        # GIVEN no data and a /poopmap command event
        event = make_telegram_event(text="/poopmap")

        # WHEN
        response = lambda_handler(event, None)

        # THEN
        response_body = json.loads(response["body"])
        assert "No poops detected, poop first!" in response_body["text"]
        
    def test_poopmap_command_return_photo(self, make_telegram_event, ddb_table, s3_client):
        # GIVEN no data and a /poopmap command event
        event = make_telegram_event(text="/poopmap")

        # WHEN
        response = lambda_handler(event, None)

        # THEN
        response_body = json.loads(response["body"])
        assert "No poops detected, poop first!" in response_body["text"]


class TestWrappedCommand:
    def test_poopwrapped_no_data(self, make_telegram_event, ddb_table):
        # GIVEN no data and a /poopwrapped command event
        event = make_telegram_event(text="/poopwrapped")

        # WHEN
        response = lambda_handler(event, None)

        # THEN
        response_body = json.loads(response["body"])
        assert "No poops detected, poop first!" in response_body["text"]


class TestUnknownCommand:
    def test_unknown_command_returns_200(self, make_telegram_event, ddb_table):
        event = make_telegram_event(text="/unknowncommand")

        response = lambda_handler(event, None)
        assert response["statusCode"] == 200
