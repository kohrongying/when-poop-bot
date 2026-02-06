import matplotlib.pyplot as plt
from datetime import date, datetime
import july
from july.utils import date_range


def generate_heatmap(dates):
    today = date.today()
    first_day = date(today.year, 1, 1)
    last_day = date(today.year, 12, 31)
    dt_range = date_range(first_day, last_day)

    data = [
        "2020-01-15",
        "2020-01-15",
        "2020-02-20",
        "2020-03-10",
        "2020-03-10",
        "2020-03-10",
        "2020-04-25",
        "2020-05-30",
        "2020-06-15",
        "2020-07-04",
        "2020-08-18",
        "2020-09-22",
        "2020-10-31",
        "2020-11-11",
        "2020-12-25",
        "2020-12-31",
    ]
    d = [datetime.fromisoformat(x).date().day for x in data]
    plt.figure(figsize=(10, 4))
    july.heatmap(dt_range, d, title="Poop Activity", cmap="github")
    filename = f"heatmap_{datetime.now().timestamp()}.png"
    plt.savefig(filename, dpi=200)
    plt.close()
    return filename


# if __name__ == "__main__":
#     generate_heatmap([])
