import unittest
from unittest.mock import Mock, patch

from src.youtube_client import (
    YOUTUBE_REQUEST_TIMEOUT,
    YouTubeAPIError,
    _env_flag,
    _youtube_get,
    extract_video_id,
    format_duration,
    parse_iso_duration_to_seconds,
    youtube_watch_url,
)


class YouTubeClientTest(unittest.TestCase):
    def test_extracts_video_id_from_short_url(self):
        self.assertEqual(
            extract_video_id("https://youtu.be/zYmH-59KakM?si=abc"),
            "zYmH-59KakM",
        )

    def test_extracts_video_id_from_watch_url(self):
        self.assertEqual(
            extract_video_id("https://www.youtube.com/watch?v=zYmH-59KakM"),
            "zYmH-59KakM",
        )

    def test_extracts_video_id_from_shorts_url(self):
        self.assertEqual(
            extract_video_id("https://youtube.com/shorts/zYmH-59KakM"),
            "zYmH-59KakM",
        )

    def test_formats_watch_url(self):
        self.assertEqual(
            youtube_watch_url("zYmH-59KakM"),
            "https://www.youtube.com/watch?v=zYmH-59KakM",
        )

    def test_parses_iso_duration(self):
        self.assertEqual(parse_iso_duration_to_seconds("PT1H02M03S"), 3723)
        self.assertEqual(format_duration("PT1H02M03S"), "1:02:03")
        self.assertEqual(format_duration("PT2M05S"), "2:05")

    @patch.dict("os.environ", {}, clear=True)
    def test_env_flag_uses_default_when_missing(self):
        self.assertTrue(_env_flag("YOUTUBE_FORCE_IPV4", True))
        self.assertFalse(_env_flag("YOUTUBE_FORCE_IPV4", False))

    @patch.dict("os.environ", {"YOUTUBE_FORCE_IPV4": "false"})
    def test_env_flag_accepts_false_values(self):
        self.assertFalse(_env_flag("YOUTUBE_FORCE_IPV4", True))

    @patch("requests.get")
    def test_youtube_get_uses_configured_timeout(self, mock_get):
        response = Mock(ok=True)
        response.json.return_value = {"items": []}
        mock_get.return_value = response

        self.assertEqual(_youtube_get("api-key", "search", {"part": "snippet"}), {"items": []})
        self.assertEqual(mock_get.call_args.kwargs["timeout"], YOUTUBE_REQUEST_TIMEOUT)

    @patch("requests.get")
    def test_youtube_get_wraps_network_errors(self, mock_get):
        import requests

        mock_get.side_effect = requests.Timeout("slow network")

        with self.assertRaises(YouTubeAPIError) as error:
            _youtube_get("api-key", "search", {"part": "snippet"})

        self.assertIn("No pude conectar con YouTube Data API", str(error.exception))


if __name__ == "__main__":
    unittest.main()
