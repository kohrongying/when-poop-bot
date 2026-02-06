from datetime import date, datetime, timedelta
from collections import Counter
from results_helper import default_tz, map_to_timezone


def format_yearly_summary(items, user_id: str, username: str) -> str:
    data = load_person_data(items, user_id)
    # df = load_into_df(data)
    summary = yearly_summary(data)
    print(summary)
    result_msg = "📊 Yearly Poop Summary 📊\n\n"

    result_msg += f"{username} 💩 a total of *{summary['total_movements']}* times since the start of this year! Wow...\n\n"

    result_msg += (
        f"That is an average of *{summary['average_per_day']:.2f}* 💩 per day.\n\n"
    )

    result_msg += f"Your greatest achievement is pooping *{summary['max_per_day']}* times on *{', '.join([d.strftime('%-d %b') for d in summary['list_days_with_max']])}*.\n\n"

    result_msg += f"Busiest month was *{', '.join([format_to_month(m) for m in summary['months_with_max']])}* with {summary['max_in_month']} poops, calmest was *{', '.join([format_to_month(m) for m in summary['months_with_min']])}* with {summary['min_in_month']} poops\n\n"

    result_msg += f"Longest streak is *{summary['longest_streak']}* days!\n\n"

    result_msg += "Keep up the good work! 💩💪\n"

    return result_msg


def format_to_month(month_num: int) -> str:
    """Returns month name given month number"""
    return datetime(2023, month_num, 1).strftime("%B")


def load_person_data(items, user_id) -> list[date]:
    ret = []
    for item in items:
        if item["UserId"] != user_id:
            continue
        ret.append(map_to_timezone(item, default_tz)["Date"])
    return ret


# def load_into_df(items: list[str]) -> pd.DataFrame:
#     df = pd.DataFrame(items, columns=["date"])
#     df['date'] = pd.to_datetime(df['date'])
#     return df


def daily_frequency(df):
    """Return frequency per day"""
    return Counter(df)


def monthly_frequency(df):
    """Return frequency per month"""
    months = [d.month for d in df]
    return Counter(months)


def yearly_summary(df):
    """Return total movements and average per day"""
    daily_counts = daily_frequency(df)
    total = sum(daily_counts.values())
    num_days_till_now = (date.today() - date(date.today().year, 1, 1)).days + 1
    avg_per_day = total / num_days_till_now if num_days_till_now > 0 else 0
    max_per_day = max(daily_counts.values())
    max_dates = [d for d, count in daily_counts.items() if count == max_per_day]
    monthly_counts = monthly_frequency(df)
    max_in_month = max(monthly_counts.values())
    months_with_max = [m for m, c in monthly_counts.items() if c == max_in_month]
    min_in_month = min(monthly_counts.values())
    months_with_min = [m for m, c in monthly_counts.items() if c == min_in_month]
    return {
        "total_movements": total,
        "average_per_day": avg_per_day,
        "max_per_day": max_per_day,
        "list_days_with_max": max_dates,
        "max_in_month": max_in_month,
        "months_with_max": months_with_max,
        "min_in_month": min_in_month,
        "months_with_min": months_with_min,
        "longest_streak": longest_streak(df),
    }


def longest_streak(df):
    """Longest streak of consecutive days with movements"""
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
