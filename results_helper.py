import random
from datetime import datetime, timedelta, timezone
from collections import Counter, defaultdict

default_tz = timezone(timedelta(hours=8))

def get_group_by_user_count(items):
    user_counts = Counter(item['Username'] for item in items)
    return user_counts.most_common()


def format_group_by_user_count(items):
    result = get_group_by_user_count(items)
    result_msg = f'💩💩💩 Counter as follows in the past 30 days\n\n'
    for item in result:
        result_msg += f'{item[0]}: {item[1]} 💩\n'
    return result_msg


def get_biggest_poop_day(items, tz=default_tz):
    items = map_items_to_timezone(items, tz)
    counts = {}
    for item in items:
        user_poop_list = counts.get(item['Username'], [])
        user_poop_list.append(item)
        counts[item['Username']] = user_poop_list
    user_biggest_counts = {}
    for user in counts:
        date_counts = Counter(item['Date'] for item in counts[user])
        user_biggest_counts[user] = date_counts.most_common()[0]
    max_poop = 0
    result = []
    for user in user_biggest_counts:
        num_poops_on_that_day = user_biggest_counts[user][1]
        that_day = user_biggest_counts[user][0]
        if num_poops_on_that_day > max_poop:
            result = [(user, num_poops_on_that_day, that_day)]
            max_poop = num_poops_on_that_day
        elif num_poops_on_that_day >= max_poop:
            result.append((user, num_poops_on_that_day, that_day))
            max_poop = num_poops_on_that_day
    return result


def format_biggest_poop_day(items):
    result = get_biggest_poop_day(items)
    result_msg = f'💩💩💩 Poop monster \n\n'
    monster_emoji = ['👻', '👹', '👺', '👽', '👾']
    for item in result:
        user = item[0]
        num_poops = item[1]
        dt = item[2].strftime('%d %B')
        result_msg += f'{user} pooped {num_poops} times on {dt}. What a poop monster {random.choice(monster_emoji)}!\n'

    return result_msg


def longest_poop_streak(items, tz=default_tz):
    items = map_items_to_timezone(items, tz)
    counts = {}
    for item in items:
        user_poop_list = counts.get(item['Username'], [])
        user_poop_list.append(item['Date'])
        counts[item['Username']] = user_poop_list
    max_streaks = []
    for user in counts:
        max_streaks.append((user, longest_streak(counts[user])))
    return max_streaks


def format_longest_poop_streak(items):
    result = longest_poop_streak(items)
    result_msg = '💩💩💩 Poooooooop streaaaakkkkkk!\n\n'
    for item in result:
        result_msg += f'{item[0]}: {item[1]} day(s)\n'
    return result_msg


def collective_most_poops(items, tz=default_tz):
    items = map_items_to_timezone(items, tz)
    counts = {}
    for item in items:
        date_list = counts.get(item['Date'], [])
        date_list.append(item['Username'])
        counts[item['Date']] = date_list
    max_count = 0
    arr = []
    result_dt = None
    for date in counts:
        num_poops = len(counts[date])
        if num_poops > max_count:
            max_count = num_poops
            arr = counts[date]
            result_dt = date
    return (result_dt, Counter(arr).most_common())


def format_collective_most_poops(items):
    result = collective_most_poops(items)
    result_msg = f'💩💩💩 Strongest bowel movement on {result[0].strftime("%d %B")}\n'
    temp = [f'{item[0]}: {item[1]}' for item in result[1]]
    result_msg += f'({",".join(temp)})'
    return result_msg


def map_items_to_timezone(items, tz):
    return [map_to_timezone(item, tz) for item in items]

def map_to_timezone(item, tz):
    item['Date'] = datetime.fromisoformat(item['PoopTimestamp']).astimezone(tz).date()
    return item

def longest_streak(dates):
    if not dates:
        return 0

    dates = sorted(set(d.date() if isinstance(d, datetime) else d for d in dates))

    max_streak = current_streak = 1

    for i in range(1, len(dates)):
        if dates[i] - dates[i - 1] == timedelta(days=1):
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 1

    return max_streak
