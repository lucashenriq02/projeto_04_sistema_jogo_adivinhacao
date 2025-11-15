"""
Projeto 04 — Sistema de Jogo de Adivinhação
Python 3.13.2+

Como executar:
  1) Salve este arquivo como jogo_adivinhacao.py
  2) (Opcional) Crie e ative um venv
  3) python jogo_adivinhacao.py

Arquivos gerados (persistência simples usando JSON em .txt):
  dados/jogadores.txt    -> dicionário {usuario: {...}}
  dados/partidas.txt     -> lista de partidas [{...}, ...]
  relatorios/            -> relatórios em texto (ranking e estatísticas)
"""
from __future__ import annotations

import json
import os
import random
from datetime import datetime
from functools import reduce
from typing import Dict, List, Tuple, Optional

# ============================================
# Configurações do jogo
# ============================================
MIN_NUMERO = 1
MAX_NUMERO = 100
MAX_TENTATIVAS = 10
PONTUACAO_BASE = 100
PENALIDADE_TENTATIVA = 10  # desconto por tentativa usada (após a primeira)

# Exemplo de uso de tuple (Módulo 1)
INTERVALO_PADRAO: Tuple[int, int] = (MIN_NUMERO, MAX_NUMERO)

# Pastas/arquivos
BASE_DADOS = os.path.join(os.getcwd(), "dados")
BASE_RELATORIOS = os.path.join(os.getcwd(), "relatorios")
ARQ_JOGADORES = os.path.join(BASE_DADOS, "jogadores.txt")
ARQ_PARTIDAS = os.path.join(BASE_DADOS, "partidas.txt")

# Estruturas em memória
jogadores: Dict[str, Dict] = {}
partidas: List[Dict] = []
contador_partidas: int = 1

# ============================================
# Utilitários de persistência
# ============================================

def _garantir_pastas() -> None:
    """Garante que as pastas de dados e relatórios existam."""
    os.makedirs(BASE_DADOS, exist_ok=True)
    os.makedirs(BASE_RELATORIOS, exist_ok=True)


def _carregar_arquivos() -> None:
    """Carrega jogadores e partidas dos arquivos JSON simples."""
    global jogadores, partidas, contador_partidas
    _garantir_pastas()

    if os.path.exists(ARQ_JOGADORES):
        try:
            with open(ARQ_JOGADORES, "r", encoding="utf-8") as f:
                jogadores = json.load(f)
        except Exception:
            # Tratamento simples: se der erro, começa vazio
            jogadores = {}
    else:
        jogadores = {}

    if os.path.exists(ARQ_PARTIDAS):
        try:
            with open(ARQ_PARTIDAS, "r", encoding="utf-8") as f:
                partidas = json.load(f)
        except Exception:
            partidas = []
    else:
        partidas = []

    # Atualiza contador de partidas
    if partidas:
        contador_partidas = max(p.get("id", 0) for p in partidas) + 1
    else:
        contador_partidas = 1


def _salvar_jogadores() -> None:
    """Salva o dicionário de jogadores em arquivo."""
    with open(ARQ_JOGADORES, "w", encoding="utf-8") as f:
        json.dump(jogadores, f, ensure_ascii=False, indent=2)


def _salvar_partidas() -> None:
    """Salva a lista de partidas em arquivo."""
    with open(ARQ_PARTIDAS, "w", encoding="utf-8") as f:
        json.dump(partidas, f, ensure_ascii=False, indent=2)


# ============================================
# FUNÇÕES DE JOGADORES
# ============================================

def cadastrar_jogador(nome: str, usuario: str) -> Dict:
    """Cadastra um novo jogador.

    Args:
        nome: Nome completo
        usuario: Nome de usuário único

    Returns:
        dict: dados do jogador
    """
    if not usuario or not nome:
        raise ValueError("Nome e usuário são obrigatórios.")

    if usuario in jogadores:
        raise ValueError("Usuário já cadastrado.")

    jogador = {
        "nome": nome,
        "usuario": usuario,
        "data_cadastro": datetime.now().date().isoformat(),
    }
    jogadores[usuario] = jogador
    _salvar_jogadores()
    return jogador


def login_jogador(usuario: str) -> Optional[Dict]:
    """Retorna dados do jogador se existir."""
    return jogadores.get(usuario)


# ============================================
# FUNÇÕES DE JOGO
# ============================================

def gerar_numero_secreto() -> int:
    """Gera um número aleatório no intervalo configurado."""
    return random.randint(MIN_NUMERO, MAX_NUMERO)


essa_entrada_invalida = "Entrada inválida. Digite um número inteiro no intervalo."


def validar_numero(entrada: str) -> Optional[int]:
    """Valida se entrada é um número no intervalo permitido.

    Returns:
        int ou None se for inválido.
    """
    try:
        numero = int(entrada)
        if MIN_NUMERO <= numero <= MAX_NUMERO:
            return numero
        return None
    except ValueError:
        return None


def exibir_dica(numero_escolhido: int, numero_secreto: int) -> None:
    """Exibe dica simples se o número é maior ou menor que o secreto."""
    if numero_escolhido < numero_secreto:
        print("➡️  Tente um número MAIOR.")
    elif numero_escolhido > numero_secreto:
        print("⬅️  Tente um número MENOR.")


def calcular_pontuacao(total_tentativas: int, vitoria: bool) -> int:
    """Calcula pontuação da partida.

    Pontuação: 100 - (tentativas-1)*10. Derrota => 0. Mínimo 0.
    """
    if not vitoria:
        return 0
    pontos = PONTUACAO_BASE - max(0, total_tentativas - 1) * PENALIDADE_TENTATIVA
    return max(0, pontos)


def jogar_partida(usuario: str) -> Dict:
    """Executa uma partida interativa no terminal.

    Args:
        usuario: usuário logado

    Returns:
        dict: dados da partida jogada
    """
    global contador_partidas

    if usuario not in jogadores:
        raise ValueError("Usuário não cadastrado. Cadastre-se antes de jogar.")

    numero_secreto = gerar_numero_secreto()
    tentativas: List[int] = []
    vitoria: bool = False  # uso explícito de bool

    print(f"\n🎯 Novo jogo! Adivinhe um número entre {MIN_NUMERO} e {MAX_NUMERO}.")
    for i in range(1, MAX_TENTATIVAS + 1):
        entrada = input(f"Tentativa {i}/{MAX_TENTATIVAS}: ")
        numero = validar_numero(entrada)
        if numero is None:
            print(essa_entrada_invalida)
            continue

        tentativas.append(numero)

        if numero == numero_secreto:
            print("✅ Você acertou! Parabéns!")
            vitoria = True
            break
        else:
            exibir_dica(numero, numero_secreto)

    total_tentativas = len(tentativas)
    pontuacao = calcular_pontuacao(total_tentativas, vitoria)

    partida = {
        "id": contador_partidas,
        "jogador": usuario,
        "numero_secreto": numero_secreto,
        "tentativas": tentativas,
        "total_tentativas": total_tentativas,
        "pontuacao": pontuacao,
        "resultado": "Vitória" if vitoria else "Derrota",
        "data": datetime.now().date().isoformat(),
    }

    partidas.append(partida)
    contador_partidas += 1
    _salvar_partidas()

    print(f"\nResultado: {partida['resultado']} | Pontuação: {pontuacao}")
    return partida


# ============================================
# ESTATÍSTICAS
# ============================================

def _partidas_do_usuario(usuario: str) -> List[Dict]:
    """Retorna todas as partidas de um usuário (list comprehension)."""
    return [p for p in partidas if p.get("jogador") == usuario]


def calcular_taxa_vitoria(usuario: str) -> float:
    """Calcula taxa de vitórias (%) de um jogador."""
    ps = _partidas_do_usuario(usuario)
    if not ps:
        return 0.0
    vitorias = sum(1 for p in ps if p.get("resultado") == "Vitória")
    return (vitorias / len(ps)) * 100


def media_tentativas(usuario: str) -> float:
    """Calcula média de tentativas por partida de um jogador."""
    ps = _partidas_do_usuario(usuario)
    if not ps:
        return 0.0
    return sum(p.get("total_tentativas", 0) for p in ps) / len(ps)


def calcular_estatisticas_jogador(usuario: str) -> Dict:
    """Calcula estatísticas completas de um jogador."""
    ps = _partidas_do_usuario(usuario)
    dados = jogadores.get(usuario, {})
    total = len(ps)
    vitorias = sum(1 for p in ps if p.get("resultado") == "Vitória")
    derrotas = total - vitorias
    taxa = (vitorias / total) * 100 if total else 0.0
    media = sum(p.get("total_tentativas", 0) for p in ps) / total if total else 0.0
    melhor = max((p.get("pontuacao", 0) for p in ps), default=0)
    soma = sum(p.get("pontuacao", 0) for p in ps)

    return {
        usuario: {
            "nome": dados.get("nome", usuario),
            "total_partidas": total,
            "vitorias": vitorias,
            "derrotas": derrotas,
            "taxa_vitoria": round(taxa, 1),
            "media_tentativas": round(media, 2),
            "melhor_pontuacao": melhor,
            "pontuacao_total": soma,
        }
    }


def estatisticas_resumidas() -> Dict[str, int]:
    """Exemplo de dict comprehension.

    Retorna {usuario: total_partidas}
    """
    return {user: len(_partidas_do_usuario(user)) for user in jogadores}


def estatisticas_funcionais(usuario: str) -> Dict[str, float]:
    """Demonstra uso de map, filter, reduce e lambda.

    Retorna informações funcionais sobre as pontuações do usuário.
    """
    ps = _partidas_do_usuario(usuario)

    # map: extrair pontuações
    pontuacoes = list(map(lambda p: p.get("pontuacao", 0), ps))

    # filter: considerar apenas vitórias
    vitorias = list(filter(lambda p: p.get("resultado") == "Vitória", ps))

    # reduce: somatório das pontuações
    soma_total = reduce(lambda a, b: a + b, pontuacoes, 0)

    media = soma_total / len(pontuacoes) if pontuacoes else 0
    maior = max(pontuacoes) if pontuacoes else 0

    return {
        "soma_total": soma_total,
        "media_pontuacao": round(media, 1),
        "maior_pontuacao": maior,
        "total_vitorias": len(vitorias),
    }


# ============================================
# RANKINGS
# ============================================

def ranking_pontuacao_media(limite: int = 10) -> List[Tuple[str, float]]:
    """Gera ranking por pontuação média."""
    resultados: List[Tuple[str, float]] = []
    for usuario in jogadores.keys():
        ps = _partidas_do_usuario(usuario)
        if not ps:
            continue
        media = sum(p["pontuacao"] for p in ps) / len(ps)
        resultados.append((usuario, round(media, 2)))
    resultados.sort(key=lambda x: x[1], reverse=True)
    return resultados[:limite]


def ranking_vitorias(limite: int = 10) -> List[Tuple[str, int]]:
    """Gera ranking por número de vitórias."""
    resultados: List[Tuple[str, int]] = []
    for usuario in jogadores.keys():
        ps = _partidas_do_usuario(usuario)
        vitorias = sum(1 for p in ps if p["resultado"] == "Vitória")
        resultados.append((usuario, vitorias))
    resultados.sort(key=lambda x: x[1], reverse=True)
    return resultados[:limite]


def ranking_melhor_pontuacao(limite: int = 10) -> List[Tuple[str, int]]:
    """Gera ranking por melhor pontuação única."""
    resultados: List[Tuple[str, int]] = []
    for usuario in jogadores.keys():
        melhor = max(
            (p.get("pontuacao", 0) for p in _partidas_do_usuario(usuario)),
            default=0,
        )
        resultados.append((usuario, melhor))
    resultados.sort(key=lambda x: x[1], reverse=True)
    return resultados[:limite]


def ranking_menor_tentativas(limite: int = 10) -> List[Tuple[str, int]]:
    """Gera ranking por menor número de tentativas nas vitórias."""
    resultados: List[Tuple[str, int]] = []
    for usuario in jogadores.keys():
        melhor = min(
            (
                p.get("total_tentativas", MAX_TENTATIVAS)
                for p in _partidas_do_usuario(usuario)
                if p.get("resultado") == "Vitória"
            ),
            default=MAX_TENTATIVAS,
        )
        resultados.append((usuario, melhor))
    resultados.sort(key=lambda x: x[1])
    return resultados[:limite]


# ============================================
# RELATÓRIOS
# ============================================

def exibir_estatisticas_jogador(usuario: str) -> None:
    """Exibe e salva estatísticas detalhadas de um jogador."""
    stats = calcular_estatisticas_jogador(usuario)
    if not stats.get(usuario):
        print("Nenhum dado para este jogador.")
        return
    s = stats[usuario]
    print("\n📈 Estatísticas —", s["nome"])
    print(f"Total de partidas: {s['total_partidas']}")
    print(f"Vitórias: {s['vitorias']} | Derrotas: {s['derrotas']}")
    print(f"Taxa de vitória: {s['taxa_vitoria']}%")
    print(f"Média de tentativas: {s['media_tentativas']}")
    print(f"Melhor pontuação: {s['melhor_pontuacao']}")
    print(f"Pontuação total: {s['pontuacao_total']}")

    # Exemplo de uso das estatísticas funcionais (lambda/map/filter/reduce)
    func = estatisticas_funcionais(usuario)
    print("\n📊 Estatísticas funcionais:")
    print(f"Soma total das pontuações: {func['soma_total']}")
    print(f"Média de pontuação: {func['media_pontuacao']}")
    print(f"Maior pontuação: {func['maior_pontuacao']}")
    print(f"Total de vitórias (filter): {func['total_vitorias']}")

    # salva relatório individual
    _garantir_pastas()
    caminho = os.path.join(BASE_RELATORIOS, f"estatisticas_{usuario}.txt")
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(
            {"estatisticas": stats, "funcionais": func},
            f,
            ensure_ascii=False,
            indent=2,
        )


def exibir_ranking() -> None:
    """Exibe rankings principais e salva em relatório geral."""
    print("\n🏆 Ranking — Pontuação média")
    for i, (u, m) in enumerate(ranking_pontuacao_media(), start=1):
        print(f"{i:2d}. {u:12s}  {m:>6.2f}")

    print("\n🏆 Ranking — Número de vitórias")
    for i, (u, v) in enumerate(ranking_vitorias(), start=1):
        print(f"{i:2d}. {u:12s}  {v}")

    print("\n🏆 Ranking — Melhor pontuação única")
    for i, (u, p) in enumerate(ranking_melhor_pontuacao(), start=1):
        print(f"{i:2d}. {u:12s}  {p}")

    print("\n🏆 Ranking — Menor nº de tentativas (vitórias)")
    for i, (u, t) in enumerate(ranking_menor_tentativas(), start=1):
        print(f"{i:2d}. {u:12s}  {t}")

    # salvar relatório geral
    rel = {
        "ranking_pontuacao_media": ranking_pontuacao_media(),
        "ranking_vitorias": ranking_vitorias(),
        "ranking_melhor_pontuacao": ranking_melhor_pontuacao(),
        "ranking_menor_tentativas": ranking_menor_tentativas(),
    }
    _garantir_pastas()
    caminho = os.path.join(BASE_RELATORIOS, "ranking_geral.txt")
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(rel, f, ensure_ascii=False, indent=2)


def historico_partidas(usuario: str, limite: int = 10) -> List[Dict]:
    """Retorna histórico recente de partidas de um jogador (ordenado)."""
    ps = _partidas_do_usuario(usuario)
    # Ordena por data e id (mais recentes primeiro)
    ps_ordenadas = sorted(
        ps, key=lambda p: (p.get("data", ""), p.get("id", 0)), reverse=True
    )
    return ps_ordenadas[:limite]


def datas_disponiveis() -> set:
    """Exemplo de uso de set: retorna conjunto de datas com partidas."""
    return {p.get("data") for p in partidas}


# ============================================
# MENU INTERATIVO (CLI)
# ============================================

def _menu() -> None:
    """Exibe o menu principal do sistema."""
    print("\n===== Sistema de Jogo de Adivinhação =====")
    print("1) Cadastrar jogador")
    print("2) Login")
    print("3) Jogar partida")
    print("4) Estatísticas do jogador")
    print("5) Exibir ranking")
    print("6) Histórico de partidas")
    print("7) Configurações (intervalo/limites)")
    print("8) Datas disponíveis (exemplo de set)")
    print("0) Sair")


def _configuracoes() -> None:
    """Permite alterar intervalo de números e limite de tentativas."""
    global MIN_NUMERO, MAX_NUMERO, MAX_TENTATIVAS
    try:
        print(f"Intervalo atual: {MIN_NUMERO}..{MAX_NUMERO} | Máx tentativas: {MAX_TENTATIVAS}")
        a = input("Novo mínimo (Enter para manter): ").strip()
        b = input("Novo máximo (Enter para manter): ").strip()
        c = input("Novo máximo de tentativas (Enter para manter): ").strip()
        if a:
            MIN_NUMERO = int(a)
        if b:
            MAX_NUMERO = int(b)
        if c:
            MAX_TENTATIVAS = max(1, int(c))
        print("Configurações atualizadas!")
    except Exception:
        print("Valores inválidos. Nenhuma alteração feita.")


# ============================================
# FUNÇÃO PRINCIPAL
# ============================================

def main() -> None:
    """Função principal: laço do menu interativo."""
    _carregar_arquivos()
    usuario_logado: Optional[str] = None

    while True:
        _menu()
        op = input("Escolha uma opção: ").strip()

        if op == "1":
            nome = input("Nome completo: ").strip()
            usuario = input("Usuário (apelido): ").strip()
            try:
                cadastrar_jogador(nome, usuario)
                print("✅ Cadastro realizado!")
            except ValueError as e:
                print("Erro:", e)

        elif op == "2":
            usuario = input("Usuário: ").strip()
            if login_jogador(usuario):
                usuario_logado = usuario
                print(f"👤 Logado como: {usuario_logado}")
            else:
                print("Usuário não encontrado. Cadastre-se primeiro.")

        elif op == "3":
            if not usuario_logado:
                print("Faça login antes de jogar.")
                continue
            try:
                jogar_partida(usuario_logado)
            except ValueError as e:
                print("Erro:", e)

        elif op == "4":
            if not usuario_logado:
                print("Faça login para ver estatísticas.")
                continue
            exibir_estatisticas_jogador(usuario_logado)

        elif op == "5":
            exibir_ranking()

        elif op == "6":
            if not usuario_logado:
                print("Faça login para ver histórico.")
                continue
            hist = historico_partidas(usuario_logado, limite=10)
            if not hist:
                print("Sem partidas registradas.")
            else:
                print("\n🕑 Últimas partidas:")
                for p in hist:
                    print(
                        f"#{p['id']:03d} | {p['data']} | {p['resultado']:<7} | "
                        f"tentativas={p['total_tentativas']:>2} | pontos={p['pontuacao']:>3}"
                    )

        elif op == "7":
            _configuracoes()

        elif op == "8":
            # Exemplo de uso de set no menu
            datas = datas_disponiveis()
            if not datas:
                print("Nenhuma partida registrada ainda.")
            else:
                print("📅 Datas com partidas registradas:")
                for d in sorted(datas):
                    print("-", d)

        elif op == "0":
            print("Até logo! 👋")
            break

        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
