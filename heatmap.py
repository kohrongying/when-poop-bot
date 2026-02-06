import matplotlib.pyplot as plt
from datetime import date, datetime
import july
from july.utils import date_range
from wrapped import load_person_data


def generate_heatmap(items: list, user_id: str) -> str:
    """Generate heatmap for given user data and return filename"""
    data = load_person_data(items, user_id)
    data = [x.day for x in data]

    plt.figure(figsize=(10, 4))
    today = date.today()
    dt_range = date_range(date(today.year, 1, 1), date(today.year, 12, 31))
    july.heatmap(dt_range, data, title="Poop Activity", cmap="github")

    filename = f"/tmp/heatmap_{datetime.now().timestamp()}.png"
    plt.savefig(filename, dpi=200)
    plt.close()

    return filename
