import os
import re
import pandas as pd

def _read_excel_any(source):
    return pd.read_excel(source)

def _extract_items_from_layout(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extrai itens do layout 'mensal' (como o seu), procurando células 'Vl. Total'
    e pegando o produto na coluna anterior e o valor na linha seguinte.
    """
    records = []
    cols = list(df.columns)

    for c_idx, col in enumerate(cols):
        for r in range(len(df) - 1):
            cell = df.iat[r, c_idx]
            if isinstance(cell, str) and "Vl. Total" in cell:
                # Produto está na coluna anterior
                if c_idx - 1 < 0:
                    continue
                produto = df.iat[r, c_idx - 1]
                valor = df.iat[r + 1, c_idx]
                records.append({"produto": produto, "valor": valor})

    out = pd.DataFrame(records)
    out["produto"] = out["produto"].astype(str)
    out["valor"] = pd.to_numeric(out["valor"], errors="coerce")
    out = out.dropna(subset=["valor"])
    return out

def load_feiras_excel(source) -> pd.DataFrame:
    df = _read_excel_any(source)
    df.columns = df.columns.astype(str)
    items = _extract_items_from_layout(df)
    return items

def load_latest_from_inbound(inbound_dir: str):
    if not os.path.isdir(inbound_dir):
        return None
    files = [os.path.join(inbound_dir, f) for f in os.listdir(inbound_dir) if f.lower().endswith(".xlsx")]
    if not files:
        return None
    files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return files[0]
