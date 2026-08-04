import json
import os
import sqlite3
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_dotenv(path=None):
    """Carrega variáveis de ambiente de um arquivo .env (sem sobrescrever as já definidas)."""
    dotenv_path = path or os.path.join(BASE_DIR, ".env")
    if not os.path.exists(dotenv_path):
        return
    with open(dotenv_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            if key and key not in os.environ:
                os.environ[key] = value


_load_dotenv()

DEFAULT_DB_PATH = os.environ.get("GASPRICE_DB_PATH")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY")
USE_SUPABASE = bool(SUPABASE_URL and SUPABASE_KEY)

if DEFAULT_DB_PATH:
    DB_NAME = DEFAULT_DB_PATH
elif os.path.exists(os.path.join(BASE_DIR, "gasprice.db")):
    DB_NAME = os.path.join(BASE_DIR, "gasprice.db")
else:
    DB_NAME = os.path.join("/tmp", "gasprice.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_NAME), exist_ok=True)
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def _supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }


def _supabase_request(method, path, payload=None, params=None):
    if not USE_SUPABASE:
        raise RuntimeError("Supabase não está configurado")

    url = f"{SUPABASE_URL}/rest/v1/{path}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params, doseq=True)}"

    data = None
    headers = _supabase_headers()
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        # Retorna o registro criado (com o id gerado) ao inserir no PostgREST
        if method == "POST":
            headers["Prefer"] = "return=representation"

    request = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(request) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else []
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8")
        raise RuntimeError(f"Supabase error {exc.code}: {error_body}") from exc
    except URLError as exc:
        raise RuntimeError(f"Erro de conexão com Supabase: {exc.reason}") from exc


def init_db():
    if USE_SUPABASE:
        return

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS postos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            bandeira TEXT NOT NULL,
            cidade TEXT NOT NULL,
            endereco TEXT NOT NULL,
            bairro TEXT NOT NULL,
            latitude REAL,
            longitude REAL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS precos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            posto_id INTEGER NOT NULL,
            tipo_combustivel TEXT NOT NULL,
            preco REAL NOT NULL,
            data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (posto_id) REFERENCES postos (id)
        )
    ''')

    cursor.execute('SELECT COUNT(*) FROM postos')
    if cursor.fetchone()[0] == 0:
        seed_data(cursor)

    conn.commit()
    conn.close()
    print("Banco de dados inicializado com sucesso!")


def seed_data(cursor):
    postos_iniciais = [
        ("Auto Posto Estrela", "Shell", "São Paulo", "Rua das Flores, 50", "Centro", -23.55052, -46.633308),
        ("Posto Econômico", "Bandeira Branca", "São Paulo", "Rodovia Sul, KM 12", "Vila Nova", -23.561414, -46.655881),
        ("Posto Central", "Petrobras", "São Paulo", "Av. Principal, 100", "Jardins", -23.56789, -46.645321),
        ("Posto Ipiranga Express", "Ipiranga", "São Paulo", "Av. Brasil, 1500", "Pinheiros", -23.57011, -46.68022),
        ("Posto Ale Cidade", "ALE", "Campinas", "Av. Francisco Glicério, 800", "Centro", -22.90556, -47.06083),
        ("Posto Anhanguera", "Bandeira Branca", "Campinas", "Rod. Anhanguera, KM 98", "Industrial", -22.88000, -47.05000),
        ("Posto Beira Mar", "Shell", "Santos", "Av. Bartolomeu de Gusmão, 45", "Aparecida", -23.97889, -46.31222)
    ]

    for p in postos_iniciais:
        cursor.execute('''
            INSERT INTO postos (nome, bandeira, cidade, endereco, bairro, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', p)

    precos_iniciais = [
        (1, "gasolina", 5.35),
        (1, "etanol", 3.65),
        (1, "diesel", 5.89),
        (2, "gasolina", 5.29),
        (2, "etanol", 3.59),
        (2, "diesel", 5.75),
        (2, "gnv", 4.39),
        (3, "gasolina", 5.49),
        (3, "etanol", 3.79),
        (3, "diesel", 5.95),
        (4, "gasolina", 5.42),
        (4, "etanol", 3.72),
        (4, "diesel", 5.85),
        (4, "gnv", 4.49),
        (5, "gasolina", 5.39),
        (5, "etanol", 3.69),
        (5, "diesel", 5.80),
        (6, "gasolina", 5.25),
        (6, "etanol", 3.55),
        (6, "diesel", 5.70),
        (7, "gasolina", 5.45),
        (7, "etanol", 3.75),
        (7, "diesel", 5.90),
        (7, "gnv", 4.59),
    ]

    for pr in precos_iniciais:
        cursor.execute('''
            INSERT INTO precos (posto_id, tipo_combustivel, preco)
            VALUES (?, ?, ?)
        ''', pr)


def buscar_postos(cidade=None, combustivel=None):
    if USE_SUPABASE:
        # Embedding do PostgREST: traz o posto junto de cada preço em UMA
        # requisição (evita N+1 chamadas ao Supabase).
        params = {
            "select": "id,tipo_combustivel,preco,data_atualizacao,postos(id,nome,bandeira,cidade,endereco,bairro)"
        }
        if combustivel:
            params["tipo_combustivel"] = f"eq.{combustivel.strip()}"
        if cidade:
            params["postos.cidade"] = f"ilike.*{cidade.strip()}*"

        precos = _supabase_request("GET", "precos", params=params)
        result = []
        for item in precos:
            posto = item.get("postos") or {}
            if not posto:
                continue
            result.append({
                "id": item["id"],
                "nome": posto.get("nome"),
                "bandeira": posto.get("bandeira"),
                "cidade": posto.get("cidade"),
                "endereco": posto.get("endereco"),
                "bairro": posto.get("bairro"),
                "combustivel": item.get("tipo_combustivel"),
                "preco": item.get("preco"),
                "data_atualizacao": item.get("data_atualizacao"),
            })
        result.sort(key=lambda r: r["preco"])
        return result

    conn = get_connection()
    cursor = conn.cursor()

    query = '''
        SELECT p.id, p.nome, p.bandeira, p.cidade, p.endereco, p.bairro, pr.tipo_combustivel, pr.preco, pr.data_atualizacao
        FROM postos p
        JOIN precos pr ON p.id = pr.posto_id
        WHERE 1=1
    '''
    params = []

    if cidade:
        query += " AND LOWER(p.cidade) LIKE LOWER(?)"
        params.append(f"%{cidade.strip()}%")

    if combustivel:
        query += " AND LOWER(pr.tipo_combustivel) = LOWER(?)"
        params.append(combustivel.strip())

    query += " ORDER BY pr.preco ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "id": r["id"],
            "nome": r["nome"],
            "bandeira": r["bandeira"],
            "cidade": r["cidade"],
            "endereco": r["endereco"],
            "bairro": r["bairro"],
            "combustivel": r["tipo_combustivel"],
            "preco": r["preco"],
            "data_atualizacao": r["data_atualizacao"]
        })
    return result


def obter_estatisticas():
    if USE_SUPABASE:
        precos = _supabase_request("GET", "precos", params={"select": "tipo_combustivel,preco"})
        total_postos = len(_supabase_request("GET", "postos", params={"select": "id"}))

        stats = {"total_postos": total_postos, "combustiveis": {}}
        grouped = {}
        for item in precos:
            fuel = item.get("tipo_combustivel")
            if not fuel:
                continue
            if fuel not in grouped:
                grouped[fuel] = []
            grouped[fuel].append(float(item.get("preco", 0)))

        for fuel, prices in grouped.items():
            stats["combustiveis"][fuel] = {
                "menor": round(min(prices), 2),
                "maior": round(max(prices), 2),
                "media": round(sum(prices) / len(prices), 2),
                "qtd": len(prices),
            }
        return stats

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT tipo_combustivel, MIN(preco) as menor, MAX(preco) as maior, AVG(preco) as media, COUNT(*) as qtd
        FROM precos
        GROUP BY tipo_combustivel
    ''')
    rows = cursor.fetchall()

    cursor.execute('SELECT COUNT(*) FROM postos')
    total_postos = cursor.fetchone()[0]

    conn.close()

    stats = {
        "total_postos": total_postos,
        "combustiveis": {}
    }
    for r in rows:
        stats["combustiveis"][r["tipo_combustivel"]] = {
            "menor": round(r["menor"], 2),
            "maior": round(r["maior"], 2),
            "media": round(r["media"], 2),
            "qtd": r["qtd"]
        }
    return stats


def listar_cidades():
    if USE_SUPABASE:
        postos = _supabase_request("GET", "postos", params={"select": "cidade"})
        return sorted({p.get("cidade") for p in postos if p.get("cidade")})

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT cidade FROM postos ORDER BY cidade ASC")
    cidades = [r["cidade"] for r in cursor.fetchall()]
    conn.close()
    return cidades


def cadastrar_ou_atualizar_posto(nome, bandeira, cidade, endereco, bairro, combustivel, preco):
    if USE_SUPABASE:
        postos = _supabase_request(
            "GET",
            "postos",
            params={"select": "id,nome,bandeira,cidade,endereco,bairro"},
        )
        posto = None
        for item in postos:
            if str(item.get("nome", "")).strip().lower() == nome.strip().lower() and str(item.get("cidade", "")).strip().lower() == cidade.strip().lower():
                posto = item
                break

        if posto is None:
            created = _supabase_request(
                "POST",
                "postos",
                payload={
                    "nome": nome.strip(),
                    "bandeira": bandeira.strip(),
                    "cidade": cidade.strip(),
                    "endereco": endereco.strip(),
                    "bairro": bairro.strip(),
                },
            )
            if isinstance(created, list) and created:
                posto = created[0]
            elif isinstance(created, dict):
                posto = created
            else:
                raise RuntimeError("Não foi possível criar o posto no Supabase")

        posto_id = posto["id"]
        precos = _supabase_request(
            "GET",
            "precos",
            params={"select": "id,posto_id,tipo_combustivel,preco", "posto_id": f"eq.{posto_id}"},
        )
        preco_row = None
        for item in precos:
            if str(item.get("tipo_combustivel", "")).strip().lower() == combustivel.strip().lower():
                preco_row = item
                break

        timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        if preco_row is None:
            _supabase_request(
                "POST",
                "precos",
                payload={
                    "posto_id": posto_id,
                    "tipo_combustivel": combustivel.strip(),
                    "preco": preco,
                    "data_atualizacao": timestamp,
                },
            )
        else:
            _supabase_request(
                "PATCH",
                f"precos?id=eq.{preco_row['id']}",
                payload={"preco": preco, "data_atualizacao": timestamp},
            )
        return {"status": "success", "posto_id": posto_id}

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id FROM postos WHERE LOWER(nome) = LOWER(?) AND LOWER(cidade) = LOWER(?)
    ''', (nome.strip(), cidade.strip()))
    row = cursor.fetchone()

    if row:
        posto_id = row["id"]
    else:
        cursor.execute('''
            INSERT INTO postos (nome, bandeira, cidade, endereco, bairro)
            VALUES (?, ?, ?, ?, ?)
        ''', (nome.strip(), bandeira.strip(), cidade.strip(), endereco.strip(), bairro.strip()))
        posto_id = cursor.lastrowid

    cursor.execute('''
        SELECT id FROM precos WHERE posto_id = ? AND LOWER(tipo_combustivel) = LOWER(?)
    ''', (posto_id, combustivel.strip()))
    preco_row = cursor.fetchone()

    if preco_row:
        cursor.execute('''
            UPDATE precos SET preco = ?, data_atualizacao = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (preco, preco_row["id"]))
    else:
        cursor.execute('''
            INSERT INTO precos (posto_id, tipo_combustivel, preco)
            VALUES (?, ?, ?)
        ''', (posto_id, combustivel.strip(), preco))

    conn.commit()
    conn.close()
    return {"status": "success", "posto_id": posto_id}


if __name__ == "__main__":
    init_db()
