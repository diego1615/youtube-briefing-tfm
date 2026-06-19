import unittest
from unittest.mock import Mock, patch

from src.ollama_client import (
    OLLAMA_DEFAULT_BASE_URL,
    OllamaError,
    build_news_brief_prompt,
    choose_default_model,
    clean_model_response,
    completion_model_names,
    generate_ollama_text,
    is_truthy_env,
    normalize_base_url,
)


class OllamaClientTest(unittest.TestCase):
    def test_normalizes_base_url(self):
        self.assertEqual(normalize_base_url("http://localhost:11434/"), "http://localhost:11434")
        self.assertEqual(normalize_base_url(""), OLLAMA_DEFAULT_BASE_URL)

    def test_truthy_env_accepts_false_values(self):
        self.assertTrue(is_truthy_env(None, True))
        self.assertFalse(is_truthy_env("false", True))
        self.assertFalse(is_truthy_env("0", True))
        self.assertTrue(is_truthy_env("yes", False))

    def test_filters_completion_models(self):
        models = [
            {"name": "embed:latest", "capabilities": ["embedding"]},
            {"name": "qwen3.5:4b", "capabilities": ["completion", "tools"]},
            {"name": "legacy:latest"},
        ]
        self.assertEqual(completion_model_names(models), ["qwen3.5:4b", "legacy:latest"])

    def test_choose_default_model_prefers_configured_model(self):
        self.assertEqual(
            choose_default_model(["llama3.2:3b", "qwen3.5:4b"], preferred="llama3.2:3b"),
            "llama3.2:3b",
        )

    def test_build_news_brief_prompt_contains_required_sections(self):
        prompt = build_news_brief_prompt(
            "noticias Uruguay",
            [
                {
                    "title": "Titulo de prueba",
                    "channel_title": "Canal",
                    "description": "Descripcion del video.",
                    "url": "https://youtube.com/watch?v=abc",
                }
            ],
        )
        self.assertIn("Tema buscado: noticias Uruguay", prompt)
        self.assertIn("Titulo de prueba", prompt)
        self.assertIn("## Resumen ejecutivo", prompt)
        self.assertIn("## Recomendacion de consumo", prompt)

    def test_clean_model_response_removes_think_blocks(self):
        text = clean_model_response("<think>razonamiento interno</think>\n## Resumen ejecutivo\nListo")
        self.assertEqual(text, "## Resumen ejecutivo\nListo")

    @patch("requests.post")
    def test_generate_ollama_text_returns_response(self, mock_post):
        response = Mock(ok=True)
        response.json.return_value = {"response": "Brief generado"}
        mock_post.return_value = response

        text = generate_ollama_text("http://localhost:11434", "qwen3.5:4b", "prompt")

        self.assertEqual(text, "Brief generado")
        self.assertEqual(mock_post.call_args.kwargs["json"]["stream"], False)
        self.assertEqual(mock_post.call_args.kwargs["json"]["think"], False)

    @patch("requests.post")
    def test_generate_ollama_text_wraps_network_errors(self, mock_post):
        import requests

        mock_post.side_effect = requests.ConnectionError("offline")

        with self.assertRaises(OllamaError) as error:
            generate_ollama_text("http://localhost:11434", "qwen3.5:4b", "prompt")

        self.assertIn("No pude conectar con Ollama local", str(error.exception))


if __name__ == "__main__":
    unittest.main()
