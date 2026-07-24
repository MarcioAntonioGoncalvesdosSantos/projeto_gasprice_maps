import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import database


def _normalize_event(request):
    if isinstance(request, dict):
        return request
    if request is None:
        return {}

    query_params = {}
    if hasattr(request, "query_params"):
        query_params = dict(request.query_params or {})

    body = getattr(request, "body", "")
    if isinstance(body, (bytes, bytearray)):
        body = body.decode("utf-8")

    return {
        "httpMethod": getattr(request, "method", "GET"),
        "queryStringParameters": query_params,
        "body": body or "",
    }


def handler(request, response=None):
    database.init_db()
    event = _normalize_event(request)

    method = (event or {}).get("httpMethod", "GET")
    if method == "POST":
        try:
            body = (event or {}).get("body") or "{}"
            data = json.loads(body)
            nome = data.get("nome")
            bandeira = data.get("bandeira", "Bandeira Branca")
            cidade = data.get("cidade")
            endereco = data.get("endereco", "")
            bairro = data.get("bairro", "")
            combustivel = data.get("combustivel")
            preco = float(data.get("preco", 0))

            if not nome or not cidade or not combustivel or preco <= 0:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Preencha todos os campos obrigatórios corretamente."}),
                }

            result = database.cadastrar_ou_atualizar_posto(
                nome, bandeira, cidade, endereco, bairro, combustivel, preco
            )
            return {
                "statusCode": 200,
                "body": json.dumps({"status": "success", "message": "Preço cadastrado com sucesso!", "result": result}),
            }
        except Exception as exc:
            return {"statusCode": 500, "body": json.dumps({"error": str(exc)})}

    params = (event or {}).get("queryStringParameters") or {}
    cidade = params.get("cidade")
    combustivel = params.get("combustivel")
    resultados = database.buscar_postos(cidade=cidade, combustivel=combustivel)
    return {"statusCode": 200, "body": json.dumps(resultados)}
