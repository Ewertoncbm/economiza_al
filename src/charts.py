import matplotlib.pyplot as plt
import pandas as pd

def plot_top_freq(summary: pd.DataFrame, top_n: int = 15):
    top = summary.sort_values("frequencia", ascending=False).head(top_n)
    fig = plt.figure()
    plt.barh(top["produto_norm"][::-1], top["frequencia"][::-1])
    plt.title(f"Top {top_n} itens mais comprados (frequência)")
    plt.tight_layout()
    return fig

def plot_avg_by_category(summary: pd.DataFrame):
    cat = summary.groupby("categoria")["preco_medio"].mean().sort_values()
    fig = plt.figure()
    plt.barh(cat.index, cat.values)
    plt.title("Preço médio (histórico) por categoria")
    plt.tight_layout()
    return fig
