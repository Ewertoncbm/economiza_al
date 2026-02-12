import os
import time
import requests

BASE_URL = "http://api.sefaz.al.gov.br/sfz-economiza-alagoas-api/api/public/"

def get_token() -> str:
    return os.getenv("ECONOMIZA_APPTOKEN", "").strip()

def economiza_search(descricao: str, latitude: float, longitude: float, raio_km: int, dias: int, pagina: int = 1, registros: int = 200):
    token = get_token()
    if not token:
        raise RuntimeError("ECONOMIZA_APPTOKEN não configurado no .env")

    url = BASE_URL.rstrip("/") + "/produto/pesquisa"
    payload = {
        "produto": {"descricao": descricao},
        "estabelecimento": {
            "geolocalizacao": {
                "latitude": latitude,
                "longitude": longitude,
                "raio": raio_km
            }
        },
        "dias": dias,
        "pagina": pagina,
        "registrosPorPagina": registros
    }

    headers = {"AppToken": token, "Content-Type": "application/json", "Accept": "application/json"}
    r = requests.post(url, json=payload, headers=headers, timeout=20)
    r.raise_for_status()
    time.sleep(0.15)
    return r.json()

def extract_offers(api_json: dict):
    conteudo = api_json.get("conteudo") or api_json.get("registrosPagina") or api_json.get("registros") or []
    out = []
    for item in conteudo:
        prod = item.get("produto", {}) or {}
        est = item.get("estabelecimento", {}) or {}
        venda = prod.get("venda", {}) or {}

        end = est.get("endereco", {}) or {}
        out.append({
            "produto_api": prod.get("descricao", ""),
            "gtin": prod.get("gtin", ""),
            "data_venda": venda.get("dataVenda", ""),
            "valor_venda": venda.get("valorVenda", None),
            "cnpj": est.get("cnpj", ""),
            "razao_social": est.get("razaoSocial", ""),
            "nome_fantasia": est.get("nomeFantasia", ""),
            "municipio": end.get("municipio", ""),
            "bairro": end.get("bairro", ""),
            "logradouro": end.get("logradouro", ""),
            "numero": end.get("numero", ""),
        })
    return out
