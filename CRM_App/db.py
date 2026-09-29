"""
Funções de acesso ao banco SQLite (crm.db): listar/buscar, inserir,
editar e deletar clientes. Usado pelo app.py, mas pode ser importado
e usado isoladamente (ex.: num script ou notebook).
"""
import sqlite3
from typing import Iterable, Optional

import pandas as pd

import config

ALL_COLUMNS = list(config.COLUMN_MAP.values())
EDITABLE_COLUMNS = [c for c in ALL_COLUMNS if c != "id"]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def listar_clientes(
    texto_busca: str = "",
    pastas: Optional[Iterable[str]] = None,
    empresas: Optional[Iterable[str]] = None,
    paises: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """Lista clientes, aplicando busca livre e filtros de seleção.

    texto_busca: procurado (case-insensitive) em nome, cargo, empresa,
    produtos, notes e email.
    pastas / empresas / paises: listas de valores exatos para filtrar
    (equivalente a um multiselect). Vazio ou None = sem filtro nessa coluna.
    """
    clauses = []
    params: list = []

    if texto_busca:
        termo = f"%{texto_busca.strip()}%"
        busca_or = " OR ".join(f"{col} LIKE ?" for col in config.SEARCH_COLUMNS)
        clauses.append(f"({busca_or})")
        params.extend([termo] * len(config.SEARCH_COLUMNS))

    def add_in_clause(coluna: str, valores: Optional[Iterable[str]]):
        valores = list(valores) if valores else []
        if valores:
            placeholders = ",".join("?" for _ in valores)
            clauses.append(f"{coluna} IN ({placeholders})")
            params.extend(valores)

    add_in_clause("pasta", pastas)
    add_in_clause("empresa", empresas)
    add_in_clause("pais", paises)

    query = f"SELECT * FROM {config.TABLE_NAME}"
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY id"

    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)


def obter_cliente(cliente_id: int) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute(
            f"SELECT * FROM {config.TABLE_NAME} WHERE id = ?", (cliente_id,)
        ).fetchone()
        return dict(row) if row else None


def valores_distintos(coluna: str) -> list:
    if coluna not in ALL_COLUMNS:
        raise ValueError(f"Coluna inválida: {coluna}")
    with get_connection() as conn:
        rows = conn.execute(
            f"SELECT DISTINCT {coluna} FROM {config.TABLE_NAME} "
            f"WHERE {coluna} IS NOT NULL AND {coluna} != '' "
            f"ORDER BY {coluna}"
        ).fetchall()
        return [r[0] for r in rows]


def inserir_cliente(dados: dict) -> int:
    """Insere um novo cliente. 'dados' pode conter qualquer subconjunto das
    colunas editáveis; o id é gerado automaticamente. Retorna o novo id."""
    colunas = [c for c in EDITABLE_COLUMNS if c in dados]
    if not colunas:
        raise ValueError("Nenhum dado válido para inserir.")
    placeholders = ",".join("?" for _ in colunas)
    valores = [dados[c] for c in colunas]

    with get_connection() as conn:
        cur = conn.execute(
            f"INSERT INTO {config.TABLE_NAME} ({','.join(colunas)}) "
            f"VALUES ({placeholders})",
            valores,
        )
        conn.commit()
        return cur.lastrowid


def editar_cliente(cliente_id: int, dados: dict) -> bool:
    """Atualiza campos de um cliente existente. Retorna True se algum
    registro foi alterado."""
    colunas = [c for c in EDITABLE_COLUMNS if c in dados]
    if not colunas:
        raise ValueError("Nenhum dado válido para atualizar.")
    set_clause = ",".join(f"{c} = ?" for c in colunas)
    valores = [dados[c] for c in colunas] + [cliente_id]

    with get_connection() as conn:
        cur = conn.execute(
            f"UPDATE {config.TABLE_NAME} SET {set_clause} WHERE id = ?",
            valores,
        )
        conn.commit()
        return cur.rowcount > 0


def deletar_cliente(cliente_id: int) -> bool:
    """Remove um cliente pelo id. Retorna True se algum registro foi removido."""
    with get_connection() as conn:
        cur = conn.execute(
            f"DELETE FROM {config.TABLE_NAME} WHERE id = ?", (cliente_id,)
        )
        conn.commit()
        return cur.rowcount > 0
