import unittest

from src.summarizer import bullet_summary, combine_texts, extract_keywords, normalize_text


class SummarizerTest(unittest.TestCase):
    def test_normalizes_text_spacing(self):
        self.assertEqual(normalize_text(" hola\n\n mundo  "), "hola mundo")

    def test_combines_non_empty_texts(self):
        self.assertEqual(combine_texts(["uno", "", "  dos  "]), "uno\ndos")

    def test_extracts_keywords_without_stopwords(self):
        keywords = extract_keywords("python youtube python datos datos datos", limit=2)
        self.assertEqual(keywords, ["datos", "python"])

    def test_bullet_summary_returns_sentences(self):
        text = (
            "Python permite crear aplicaciones de datos rapidamente. "
            "Streamlit ayuda a construir interfaces web simples. "
            "YouTube Data API entrega metadata oficial de videos."
        )
        bullets = bullet_summary(text, max_sentences=2)
        self.assertTrue(1 <= len(bullets) <= 2)


if __name__ == "__main__":
    unittest.main()
