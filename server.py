import http.server
import socketserver
import json
import urllib.parse
import os
import database

PORT = 8000

class GasPriceHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        if path == "/api/postos":
            cidade = query_params.get("cidade", [None])[0]
            combustivel = query_params.get("combustivel", [None])[0]
            
            resultados = database.buscar_postos(cidade=cidade, combustivel=combustivel)
            self._send_json(resultados)

        elif path == "/api/estatisticas":
            stats = database.obter_estatisticas()
            self._send_json(stats)

        elif path == "/api/cidades":
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT cidade FROM postos ORDER BY cidade ASC")
            cidades = [r["cidade"] for r in cursor.fetchall()]
            conn.close()
            self._send_json(cidades)

        else:
            # Servir arquivos estáticos (html, css, js)
            super().do_GET()

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/api/postos":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            try:
                data = json.loads(body.decode('utf-8'))
                nome = data.get("nome")
                bandeira = data.get("bandeira", "Bandeira Branca")
                cidade = data.get("cidade")
                endereco = data.get("endereco", "")
                bairro = data.get("bairro", "")
                combustivel = data.get("combustivel")
                preco = float(data.get("preco", 0))

                if not nome or not cidade or not combustivel or preco <= 0:
                    self._send_json({"error": "Preencha todos os campos obrigatórios corretamente."}, status=400)
                    return

                res = database.cadastrar_ou_atualizar_posto(nome, bandeira, cidade, endereco, bairro, combustivel, preco)
                self._send_json({"status": "success", "message": "Preço cadastrado com sucesso!", "result": res})

            except Exception as e:
                self._send_json({"error": str(e)}, status=500)
        else:
            self.send_error(404, "Endpoint não encontrado")

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def end_headers(self):
        # Desabilitar cache para APIs e arquivos durante desenvolvimento
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

def run_server():
    database.init_db()
    handler = GasPriceHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Servidor GasPrice rodando na porta {PORT} -> http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor finalizado.")

if __name__ == "__main__":
    run_server()
