import matplotlib.pyplot as plt
from datetime import date, datetime
import july
from july.utils import date_range
from wrapped import load_person_data
import boto3


def generate_heatmap(items: list, user_id: str) -> str:
    """Generate heatmap for given user data and return filename"""
    data = load_person_data(items, user_id)
    d = {}
    for dt in data:
        d[dt] = d.get(dt, 0) + 1

    plt.figure(figsize=(10, 4))
    today = date.today()
    dt_range = date_range(date(today.year, 1, 1), date(today.year, 12, 31))
    data = [d.get(dt, 0) for dt in dt_range]
    july.heatmap(dt_range, data, title="Poop Activity", cmap="github", colorbar=True)

    filename = f"/tmp/heatmap_{datetime.now().timestamp()}.png"
    plt.savefig(filename, dpi=200)
    plt.close()

    return filename


def get_presigned_url(filename: str) -> str:
    s3_client = boto3.client("s3")
    bucket_name = "s3-poop-bot"
    object_key = f"heatmaps/{filename.split('/')[-1]}"
    s3_client.upload_file(filename, bucket_name, object_key)
    url = s3_client.generate_presigned_url(
        "get_object", Params={"Bucket": bucket_name, "Key": object_key}, ExpiresIn=3600
    )
    return url
