"""
Análise de Dados do Sistema de Jogo de Adivinhação
--------------------------------------------------

Agora as imagens são salvas em:

analise_de_dados/
    ├── analise_1/
    ├── analise_2/
    ├── analise_3/
    └── ...

Cada execução cria uma nova pasta "analise_X".
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ============================================
# LOCALIZAÇÃO DOS ARQUIVOS
# ============================================

BASE = os.getcwd()
ARQ_PARTIDAS = os.path.join(BASE, "dados", "partidas.txt")

# Pasta principal das análises
PASTA_ANALISE = os.path.join(BASE, "analise_de_dados")
os.makedirs(PASTA_ANALISE, exist_ok=True)

# ============================================
# GERAR PRÓXIMA PASTA analise_X
# ============================================

def gerar_pasta_analise():
    pastas = [p for p in os.listdir(PASTA_ANALISE) if p.startswith("analise_")]
    if not pastas:
        novo_numero = 1
    else:
        numeros = [int(p.split("_")[1]) for p in pastas]
        novo_numero = max(numeros) + 1

    nome_pasta = f"analise_{novo_numero}"
    caminho = os.path.join(PASTA_ANALISE, nome_pasta)
    os.makedirs(caminho, exist_ok=True)
    return caminho

PASTA_ATUAL = gerar_pasta_analise()

print(f"\n📁 Salvando gráficos em: {PASTA_ATUAL}\n")

# ============================================
# CARREGAR ARQUIVO
# ============================================

with open(ARQ_PARTIDAS, "r", encoding="utf-8") as f:
    dados = json.load(f)

df = pd.DataFrame(dados)

print("\n=== DATAFRAME INICIAL ===")
print(df.head(), "\n")

# ============================================
# LIMPEZA DE DADOS
# ============================================

# Remover coluna 'tentativas' (contém listas → causa erro no drop_duplicates)
if "tentativas" in df.columns:
    df = df.drop(columns=["tentativas"])

# Converter data para datetime
df["data"] = pd.to_datetime(df["data"], errors="coerce")

# Remover duplicatas
df = df.drop_duplicates()

# Remover linhas totalmente vazias
df = df.dropna(how="all")

# Converter pontuacao/total_tentativas para int
df["pontuacao"] = df["pontuacao"].astype(int)
df["total_tentativas"] = df["total_tentativas"].astype(int)

print("=== DATAFRAME LIMPO ===")
print(df.head(), "\n")

# ============================================
# ANÁLISES ESTATÍSTICAS
# ============================================

print("=== ESTATÍSTICAS DESCRITIVAS ===")
print(df.describe(), "\n")

# Criar coluna binária para vitórias
df["vitoria_bin"] = (df["resultado"] == "Vitória").astype(int)

# Agrupamento por jogador
stats_por_jogador = df.groupby("jogador").agg({
    "pontuacao": ["mean", "max", "sum"],
    "total_tentativas": "mean",
    "vitoria_bin": "sum"
})

print("=== ESTATÍSTICAS POR JOGADOR ===")
print(stats_por_jogador, "\n")

# ============================================
# GRÁFICOS — SALVANDO NA PASTA ATUAL
# ============================================

# 1) Histograma de pontuações
plt.figure(figsize=(8, 5))
plt.hist(df["pontuacao"], bins=7)
plt.title("Histograma de Pontuações")
plt.xlabel("Pontuação")
plt.ylabel("Frequência")
plt.savefig(os.path.join(PASTA_ATUAL, "hist_pontuacoes.png"))
plt.close()

# 2) Gráfico de barras (Vitórias por jogador)
plt.figure(figsize=(8, 5))
df.groupby("jogador")["vitoria_bin"].sum().plot(kind="bar")
plt.title("Vitórias por Jogador")
plt.ylabel("Vitórias")
plt.savefig(os.path.join(PASTA_ATUAL, "barras_vitorias.png"))
plt.close()

# 3) Boxplot de pontuações
plt.figure(figsize=(8, 5))
sns.boxplot(x=df["pontuacao"])
plt.title("Boxplot das Pontuações")
plt.savefig(os.path.join(PASTA_ATUAL, "boxplot_pontuacoes.png"))
plt.close()

# 4) Heatmap de correlação
plt.figure(figsize=(8, 5))
sns.heatmap(df[["pontuacao", "total_tentativas", "vitoria_bin"]].corr(), annot=True, cmap="Blues")
plt.title("Heatmap de Correlação")
plt.savefig(os.path.join(PASTA_ATUAL, "heatmap_correlacao.png"))
plt.close()

print("\n✅ Gráficos gerados e salvos em:")
print(PASTA_ATUAL)
