import pandas as pd
from datetime import date, datetime
from results_helper import default_tz, map_to_timezone


def format_yearly_summary(items, user_id: str, username: str) -> str:
    data = load_person_data(items, user_id)
    df = load_into_df(data)
    summary = yearly_summary(df)
    print(summary)
    result_msg = f"📊 Yearly Poop Summary 📊\n\n"
    
    result_msg += f"{username} 💩 a total of *{summary['total_movements']}* times since the start of this year! Wow...\n\n"
    
    result_msg += f"That is an average of *{summary['average_per_day']:.2f}* 💩 per day.\n\n"
    
    result_msg += f"Your greatest achievement is pooping *{summary['max_per_day']}* times on *{', '.join([d.strftime('%-d %b') for d in summary['list_days_with_max']])}*.\n\n"
    
    result_msg += f"Busiest month was *{', '.join([format_to_month(m) for m in summary['months_with_max']])}* with {summary['max_in_month']} poops, calmest was *{', '.join([format_to_month(m) for m in summary['months_with_min']])}* with {summary['min_in_month']} poops\n\n"
    
    result_msg += f"Longest streak is *{summary['longest_streak']}* days!\n\n"
    
    result_msg += "Keep up the good work! 💩💪\n"
    
    return result_msg

def format_to_month(month_num: int) -> str:
    """Returns month name given month number"""
    return datetime(2023, month_num, 1).strftime("%B")

def load_person_data(items, user_id) -> list:
    ret = []
    for item in items:
        if item['UserId'] != user_id:
            continue
        ret.append(map_to_timezone(item, default_tz)['Date'])
    return ret

def load_into_df(items: list[str]) -> pd.DataFrame:
    df = pd.DataFrame(items, columns=["date"])
    df['date'] = pd.to_datetime(df['date'])
    return df

def daily_frequency(df):
    """Return frequency per day"""
    return df.groupby(df['date'].dt.date).size()

def monthly_frequency(df):
    """Return frequency per month"""
    return df.groupby(df['date'].dt.month).size()

def yearly_summary(df):
    """Return total movements and average per day"""
    daily_counts = daily_frequency(df)
    total = daily_counts.sum()
    num_days_till_now = (date.today() - date(date.today().year, 1, 1)).days + 1
    avg_per_day = daily_counts.mean()
    max_per_day = daily_counts.max()
    max_dates = daily_counts[daily_counts == max_per_day].index.tolist()
    monthly_counts = monthly_frequency(df)
    return {
        "total_movements": total,
        "average_per_day": total / num_days_till_now,
        "max_per_day": max_per_day,
        "list_days_with_max": max_dates,
        "max_in_month": monthly_counts.max(),
        "months_with_max": monthly_counts[monthly_counts == monthly_counts.max()].index.tolist(),
        "min_in_month": monthly_counts.min(),
        "months_with_min": monthly_counts[monthly_counts == monthly_counts.min()].index.tolist(),
        "longest_streak": longest_streak(df)
    }
    

def longest_streak(df):
    """Longest streak of consecutive days with movements"""
    days = pd.Series(df['date'].dt.date.unique()).sort_values()
    streaks = []
    current_streak = 1
    for i in range(1, len(days)):
        if (days.iloc[i] - days.iloc[i-1]).days == 1:
            current_streak += 1
        else:
            streaks.append(current_streak)
            current_streak = 1
    streaks.append(current_streak)
    return max(streaks)
