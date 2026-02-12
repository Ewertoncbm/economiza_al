import re

def normalize_item(s: str) -> str:
    s = str(s).lower().strip()

    # Remove trechos comuns de nota fiscal e códigos
    s = re.sub(r"\(c[oó]digo:.*?\)", "", s)
    s = re.sub(r"\s+", " ", s)

    # Normalizações simples PT-BR
    s = s.replace("maca", "maçã")  # ajuda quando vem sem cedilha
    s = s.replace(" kg", "kg")

    return s.strip()

def refine_category(prod_norm: str) -> str:
    p = prod_norm

    # Hortifruti
    if any(x in p for x in ["banana", "maçã", "tomate", "cebola", "batata", "alface", "laranja", "uva", "mamão"]):
        return "Hortifruti"

    # Açougue
    if any(x in p for x in ["carne", "frango", "file", "filé", "peito", "muss", "lingui", "bovina", "suína", "peixe"]):
        return "Açougue"

    # Mercearia (secos)
    if any(x in p for x in ["arroz", "feijão", "macarr", "farinha", "açúcar", "acucar", "café", "cafe", "óleo", "oleo", "sal"]):
        return "Mercearia"

    # Laticínios
    if any(x in p for x in ["leite", "queijo", "manteiga", "iogurte"]):
        return "Laticínios"

    # Padaria
    if any(x in p for x in ["pão", "pao", "bolo", "massa", "biscoito"]):
        return "Padaria"

    # Bebidas
    if any(x in p for x in ["água", "agua", "refriger", "suco", "cerveja"]):
        return "Bebidas"

    # Limpeza
    if any(x in p for x in ["sabão", "sabao", "detergente", "lixo", "desinfetante", "água sanit", "agua sanit", "sacola", "esponja", "amaciante"]):
        return "Limpeza"

    # Higiene / bebê
    if any(x in p for x in ["fralda", "toalha umed", "sabonete", "shampoo", "creme dental", "papel higiên", "papel higien"]):
        return "Higiene & Bebê"

    return "Outros"
