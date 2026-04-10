import random
from datetime import datetime, timedelta, timezone, date
from collections import Counter, namedtuple

default_tz = timezone(timedelta(hours=8))


def build_summary(items):
    summary = format_group_by_user_count(items)
    summary += "\n\n"
    summary += format_biggest_poop_day(items)
    summary += "\n\n"
    summary += format_longest_poop_streak(items)
    summary += "\n\n"
    summary += format_collective_most_poops(items)
    return summary


### GROUP BY USER COUNT ###


def get_group_by_user_count(items) -> list[tuple[str, int]]:
    user_counts = Counter(item["Username"] for item in items)
    return user_counts.most_common()


def format_group_by_user_count(items) -> str:
    result = get_group_by_user_count(items)
    result_msg = f"💩💩💩 Counter as follows in the past 30 days\n\n"
    for item in result:
        result_msg += f"{item[0]}: {item[1]} 💩\n"
    return result_msg


### BIGGEST POOP DAY ###

PoopMonster = namedtuple("PoopMonster", ["username", "num_poops", "date"])


def get_biggest_poop_day(items, tz=default_tz) -> list[PoopMonster]:
    items = map_items_to_timezone(items, tz)
    counts: dict[str, list[date]] = {}
    for item in items:
        user_poop_list = counts.get(item["Username"], [])
        user_poop_list.append(item)
        counts[item["Username"]] = user_poop_list

    user_biggest_counts: dict[str, tuple[date, int]] = {}
    for user in counts:
        date_counts = Counter(item["Date"] for item in counts[user])
        user_biggest_counts[user] = date_counts.most_common()[0]

    max_poop = 0
    result = []

    for user in user_biggest_counts:
        num_poops_on_that_day = user_biggest_counts[user][1]
        that_day = user_biggest_counts[user][0]
        if num_poops_on_that_day > max_poop:
            result = [PoopMonster(user, num_poops_on_that_day, that_day)]
            max_poop = num_poops_on_that_day
        elif num_poops_on_that_day == max_poop:
            result.append(PoopMonster(user, num_poops_on_that_day, that_day))

    return result


def format_biggest_poop_day(items):
    result = get_biggest_poop_day(items)
    result_msg = "💩💩💩 Poop monster\n\n"
    monster_emoji = ["👻", "👹", "👺", "👽", "👾"]
    for item in result:
        dt = item.date.strftime("%d %B")
        result_msg += f"{item.username} pooped {item.num_poops} times on {dt}. What a poop monster {random.choice(monster_emoji)}!\n"

    return result_msg


### POOP STREAK ###

PoopStreak = namedtuple("PoopStreak", ["username", "streak_length"])


def longest_streak(df: list[date]) -> int:
    if len(df) == 0:
        return 0

    hashset = {}
    for dt in df:
        hashset[dt] = True

    streak = 1
    max_streak = 1
    for key in hashset:
        if (key - timedelta(days=1)) not in hashset:
            while (key + timedelta(days=streak)) in hashset:
                streak += 1
            max_streak = max(max_streak, streak)
    return max_streak


def longest_poop_streak(items, tz=default_tz) -> list[PoopStreak]:
    items = map_items_to_timezone(items, tz)
    counts: dict[str, list[date]] = {}
    for item in items:
        user_poop_list = counts.get(item["Username"], [])
        user_poop_list.append(item["Date"])
        counts[item["Username"]] = user_poop_list

    return [PoopStreak(user, longest_streak(counts[user])) for user in counts]


def format_longest_poop_streak(items) -> str:
    result = longest_poop_streak(items)
    result_msg = "💩💩💩 Poooooooop streaaaakkkkkk!\n\n"
    for item in result:
        result_msg += f"{item.username}: {item.streak_length} day(s)\n"
    return result_msg


### COLLECTIVE MOST POOPS ###

CollectiveMostPoop = namedtuple("CollectiveMostPoop", ["date", "users_and_counts"])


def collective_most_poops(items, tz=default_tz) -> CollectiveMostPoop:
    items = map_items_to_timezone(items, tz)
    counts: dict[date, list[str]] = {}
    for item in items:
        date_list = counts.get(item["Date"], [])
        date_list.append(item["Username"])
        counts[item["Date"]] = date_list

    max_count = 0
    arr = []
    result_dt = None
    for date_key in counts:
        num_poops = len(counts[date_key])
        if num_poops > max_count:
            max_count = num_poops
            arr = counts[date_key]
            result_dt = date_key
    return CollectiveMostPoop(result_dt, Counter(arr).most_common())


def format_collective_most_poops(items) -> str:
    result = collective_most_poops(items)
    result_msg = f"💩💩💩 Strongest bowel movement on {result.date.strftime('%d %B')}\n"
    temp = [f"{item[0]}: {item[1]}" for item in result.users_and_counts]
    result_msg += f"({','.join(temp)})"
    return result_msg


### UTILS ###


def map_items_to_timezone(items, tz) -> list[dict]:
    return [map_to_timezone(item, tz) for item in items]


def map_to_timezone(item, tz) -> dict:
    item["Date"] = datetime.fromisoformat(item["PoopTimestamp"]).astimezone(tz).date()
    return item
