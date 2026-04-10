from datetime import date
import boto3
from moto import mock_aws
from july.utils import date_range
from heatmap import generate_heatmap, get_presigned_url


class TestGenerateHeatmap:
    def test_generate_heatmap_creates_file(self, mocker):
        mock_plt = mocker.patch("heatmap.plt")
        mock_july = mocker.patch("heatmap.july.heatmap")
        
        # Mock datetime.now() to return a consistent timestamp
        mock_datetime = mocker.patch("heatmap.datetime")
        mock_timestamp = 1736035200  # Consistent timestamp for testing
        mock_datetime.now.return_value.timestamp.return_value = mock_timestamp
        
        mock_today = mocker.patch("heatmap.date")
        mock_today.today.return_value = date(2025, 1, 5)
        mock_today.side_effect = [date(2025, 1, 1), date(2025, 12, 31)]

        # GIVEN
        items = [
            {"PoopTimestamp": "2025-01-01T10:00:00+00:00", "UserId": "123"},
            {"PoopTimestamp": "2025-01-02T11:00:00+00:00", "UserId": "123"},
            {"PoopTimestamp": "2025-01-02T11:00:00+00:00", "UserId": "123"},
            {"PoopTimestamp": "2025-01-04T11:00:00+00:00", "UserId": "123"},
        ]
        user_id = "123"

        # WHEN
        result = generate_heatmap(items, user_id)

        # Verify the result is a filename with the mocked timestamp
        assert result == f'/tmp/heatmap_{mock_timestamp}.png'

        # Verify matplotlib functions were called
        mock_plt.figure.assert_called_once_with(figsize=(10, 4))
        mock_plt.savefig.assert_called_once()
        savefig_call = mock_plt.savefig.call_args
        assert savefig_call[1]["dpi"] == 200
        mock_plt.close.assert_called_once()

        # Verify july.heatmap was called
        dt_range = date_range(date(2025, 1, 1), date(2025, 12, 31))
        items = [1, 2, 0, 1] + [0] * (len(dt_range) - 4)
        mock_july.assert_called_once()
        july_call = mock_july.call_args
        assert july_call[1]["title"] == "Poop Activity"
        assert july_call[1]["cmap"] == "github"
        assert july_call[1]["colorbar"]
        assert july_call[0][0] == dt_range 
        assert july_call[0][1] == items


    def test_generate_heatmap_empty_data(self, mocker):
        """Test generate_heatmap with empty data."""
        # Mock the dependencies
        mock_load_person_data = mocker.patch("heatmap.load_person_data")
        mock_plt = mocker.patch("heatmap.plt")
        mock_july_heatmap = mocker.patch("heatmap.july.heatmap")

        mock_dates = []
        mock_load_person_data.return_value = mock_dates

        items = []
        user_id = "999"

        # Should not raise error
        result = generate_heatmap(items, user_id)

        assert isinstance(result, str)
        assert result.startswith("/tmp/heatmap_")

        # July heatmap should still be called
        mock_july_heatmap.assert_called_once()


class TestGetPresignedUrl:

    def test_get_presigned_url_returns_valid_url(self, mocker):
        mock = mocker.patch("boto3.client")
        mock_s3 = mock.return_value
        mock_url = "https://s3-poop-bot/mock-presigned-url.com"
        mock_s3.generate_presigned_url.return_value = mock_url
        
        filename = "/tmp/heatmap_1234567890.png"

        # WHEN
        result = get_presigned_url(filename)

        # THEN: Verify the result is a URL
        assert result == mock_url
        mock_s3.generate_presigned_url.assert_called_once_with(
            "get_object", 
            Params={
                "Bucket": "s3-poop-bot",
                "Key": f"heatmaps/heatmap_1234567890.png"
            }, 
            ExpiresIn=3600
        )

    @mock_aws
    def test_get_presigned_url_uploads_file_to_s3(self):
        # Create S3 bucket with moto
        s3_client = boto3.client("s3", region_name="ap-southeast-1")
        s3_client.create_bucket(
            Bucket="s3-poop-bot",
            CreateBucketConfiguration={"LocationConstraint": "ap-southeast-1"},
        )
        
        # Create a temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
            f.write(b"fake image data")
            filename = f.name

        # WHEN
        url = get_presigned_url(filename)

        # Verify the file was uploaded
        assert url.startswith("https://s3-poop-bot.s3.amazonaws.com/heatmaps/")
        response = s3_client.list_objects_v2(Bucket="s3-poop-bot")
        assert "Contents" in response
        assert len(response["Contents"]) > 0
