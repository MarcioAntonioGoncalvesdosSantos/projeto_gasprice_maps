import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


class DummyVercelRequest:
    def __init__(self, method="GET", query_params=None, body=""):
        self.method = method
        self.query_params = query_params or {}
        self.body = body.encode("utf-8") if isinstance(body, str) else body

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class ApiHandlerTests(unittest.TestCase):
    def setUp(self):
        self.db_path = os.path.join(tempfile.gettempdir(), "gasprice-test.db")
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.environ["GASPRICE_DB_PATH"] = self.db_path

        import importlib
        import database

        importlib.reload(database)
        database.init_db()

    def test_get_postos_returns_json(self):
        from api import postos

        response = postos.handler(
            {"httpMethod": "GET", "queryStringParameters": {"cidade": "São Paulo", "combustivel": "gasolina"}},
            {},
        )

        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertIsInstance(body, list)
        self.assertGreaterEqual(len(body), 1)

    def test_get_estatisticas_returns_json(self):
        from api import estatisticas

        response = estatisticas.handler({"httpMethod": "GET"}, {})

        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertIn("total_postos", body)
        self.assertIn("combustiveis", body)

    def test_vercel_request_signature_is_supported(self):
        from api import cidades

        request = DummyVercelRequest(method="GET", query_params={})
        response = cidades.handler(request, None)

        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertIsInstance(body, list)

    def test_load_dotenv_parses_env_file(self):
        import database

        env_file = os.path.join(tempfile.gettempdir(), "gasprice-dotenv-test.env")
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(
                "# comentário\n"
                "GASPRICE_TESTE_UM=valor1\n"
                'GASPRICE_TESTE_DOIS="valor 2"\n'  # aspas são removidas
            )
        try:
            os.environ.pop("GASPRICE_TESTE_UM", None)
            os.environ.pop("GASPRICE_TESTE_DOIS", None)
            database._load_dotenv(env_file)
            self.assertEqual(os.environ.get("GASPRICE_TESTE_UM"), "valor1")
            self.assertEqual(os.environ.get("GASPRICE_TESTE_DOIS"), "valor 2")
        finally:
            os.environ.pop("GASPRICE_TESTE_UM", None)
            os.environ.pop("GASPRICE_TESTE_DOIS", None)
            os.unlink(env_file)


if __name__ == "__main__":
    unittest.main()
