import unittest

from src.youtube_client import (
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


if __name__ == "__main__":
    unittest.main()

