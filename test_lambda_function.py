import unittest
import uuid
from datetime import datetime, timezone, timedelta, date

from constants import POOP_TRIVIA
from lambda_function import get_group_by_user_count, get_biggest_poop_day, longest_poop_streak, collective_most_poops

user1 = 'user1'
user2 = 'user2'
user3 = 'user3'


class MyTestCase(unittest.TestCase):
    def test_get_group_by_user_count(self):
        items = [
            create_test_item(user1, datetime(2023, 11, 19, 18, 30, 25, 697633, tzinfo=timezone.utc).isoformat()),
            create_test_item(user2, datetime(2023, 11, 19, 18, 30, 25, 697633, tzinfo=timezone.utc).isoformat()),
            create_test_item(user3, datetime(2023, 11, 19, 18, 30, 25, 697633, tzinfo=timezone.utc).isoformat()),
            create_test_item(user1, datetime(2023, 11, 20, 18, 30, 25, 697633, tzinfo=timezone.utc).isoformat()),
            create_test_item(user2, datetime(2023, 11, 20, 18, 30, 25, 697633, tzinfo=timezone.utc).isoformat()),
            create_test_item(user1, datetime(2023, 11, 21, 18, 30, 25, 697633, tzinfo=timezone.utc).isoformat()),
            create_test_item(user1, datetime(2023, 11, 22, 18, 30, 25, 697633, tzinfo=timezone.utc).isoformat())
        ]
        result = get_group_by_user_count(items)
        self.assertEqual(result, [(user1, 4), (user2, 2), (user3, 1)])  # add assertion here

    def test_get_biggest_poop_day(self):
        items = [
            create_test_item(user1, datetime(2023, 11, 19, 18, 30, 25, 697633, tzinfo=timezone.utc).isoformat()),
            create_test_item(user1, datetime(2023, 11, 19, 18, 30, 25, 697633, tzinfo=timezone.utc).isoformat()),
            create_test_item(user2, datetime(2023, 11, 20, 18, 30, 25, 697633, tzinfo=timezone.utc).isoformat()),
            create_test_item(user1, datetime(2023, 11, 19, 18, 30, 25, 697633, tzinfo=timezone.utc).isoformat()),
            create_test_item(user1, datetime(2023, 11, 19, 18, 30, 25, 697633, tzinfo=timezone.utc).isoformat()),
            create_test_item(user1, datetime(2023, 11, 28, 18, 30, 25, 697633, tzinfo=timezone.utc).isoformat())
        ]
        result = get_biggest_poop_day(items)
        self.assertEqual(result, [(user1, 4, date(2023, 11, 20))])  # add assertion here

    def test_get_longest_streak(self):
        items = [
            create_test_item(user1, datetime(2023, 11, 19, 18, 30, 25, 697633, tzinfo=timezone.utc).isoformat()),
            create_test_item(user1, datetime(2023, 11, 20, 18, 30, 25, 697633, tzinfo=timezone.utc).isoformat()),
            create_test_item(user1, datetime(2023, 11, 21, 18, 30, 25, 697633, tzinfo=timezone.utc).isoformat()),
            create_test_item(user1, datetime(2023, 11, 22, 18, 30, 25, 697633, tzinfo=timezone.utc).isoformat()),
            create_test_item(user2, datetime(2023, 11, 23, 18, 30, 25, 697633, tzinfo=timezone.utc).isoformat()),
            create_test_item(user1, datetime(2023, 11, 28, 18, 30, 25, 697633, tzinfo=timezone.utc).isoformat())
        ]
        result = longest_poop_streak(items)
        self.assertEqual(result, [(user1, 4), (user2, 1)])  # add assertion here

    def test_collective_most_poops(self):
        items = [
            create_test_item(user1, datetime(2023, 11, 19, 18, 30, 25, 697633, tzinfo=timezone.utc).isoformat()),
            create_test_item(user1, datetime(2023, 11, 20, 18, 30, 25, 697633, tzinfo=timezone.utc).isoformat()),
            create_test_item(user1, datetime(2023, 11, 28, 18, 30, 25, 697633, tzinfo=timezone.utc).isoformat()),
            create_test_item(user1, datetime(2023, 11, 23, 18, 30, 25, 697633, tzinfo=timezone.utc).isoformat()),
            create_test_item(user2, datetime(2023, 11, 23, 18, 30, 25, 697633, tzinfo=timezone.utc).isoformat()),
            create_test_item(user3, datetime(2023, 11, 23, 18, 30, 25, 697633, tzinfo=timezone.utc).isoformat()),
            create_test_item(user1, datetime(2023, 11, 28, 18, 30, 25, 697633, tzinfo=timezone.utc).isoformat())
        ]
        result = collective_most_poops(items)
        self.assertEqual(result, (date(2023, 11, 24), [(user1, 1), (user2, 1), (user3, 1)]))

def create_test_item(user_id: str, timestamp: str):
    return {
        'PoopTimestamp': timestamp or '2025-11-19T18:30:25.697633Z',
        'UserId': user_id,
        'TTL': 1766169025,
        'ChatId': 'TEST_CHAT_ID',
        'RecordId': str(uuid.uuid4()),
        'Username': user_id
    }


if __name__ == '__main__':
    unittest.main()
