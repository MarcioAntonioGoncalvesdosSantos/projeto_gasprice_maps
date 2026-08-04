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

    return {
        "httpMethod": getattr(request, "method", "GET"),
        "queryStringParameters": dict(getattr(request, "query_params", {}) or {}),
        "body": getattr(request, "body", "") or "",
    }


def handler(request, response=None):
    database.init_db()
    cidades = database.listar_cidades()
    return {"statusCode": 200, "body": json.dumps(cidades)}
