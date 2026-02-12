import pandas as pd

def build_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby(["categoria", "produto_norm"])
          .agg(
              frequencia=("valor", "count"),
              preco_medio=("valor", "mean"),
              preco_min=("valor", "min"),
              preco_max=("valor", "max"),
          )
          .reset_index()
    )

    # Arredondar para ficar bonito
    for c in ["preco_medio", "preco_min", "preco_max"]:
        summary[c] = summary[c].round(2)

    summary = summary.sort_values(["frequencia", "preco_medio"], ascending=[False, False])
    return summary
