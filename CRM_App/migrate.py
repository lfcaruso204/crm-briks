"""
Migra a aba 'ALL' de allcards.xlsx para o banco SQLite crm.db.

Uso:
    python migrate.py            # só cria o banco se ele ainda não existir
    python migrate.py --force    # recria o banco do zero (apaga edições feitas no CRM)

Suposição: por padrão o script NUNCA sobrescreve um crm.db já existente,
para não perder dados inseridos/editados manualmente pelo CRM depois da
primeira importação. Use --force só quando quiser resincronizar tudo a
partir do Excel.
"""
import argparse
import sqlite3
import sys

import pandas as pd

import config


def carregar_excel() -> pd.DataFrame:
    if not config.EXCEL_PATH.exists():
        sys.exit(f"Arquivo não encontrado: {config.EXCEL_PATH}")

    df = pd.read_excel(config.EXCEL_PATH, sheet_name=config.EXCEL_SHEET)
    df = df.rename(columns=config.COLUMN_MAP)

    colunas_esperadas = list(config.COLUMN_MAP.values())
    faltando = [c for c in colunas_esperadas if c not in df.columns]
    if faltando:
        sys.exit(f"Colunas ausentes na aba '{config.EXCEL_SHEET}': {faltando}")

    df = df[colunas_esperadas]
    df = df.where(pd.notnull(df), None)
    return df


def criar_banco(df: pd.DataFrame) -> None:
    colunas = list(config.COLUMN_MAP.values())
    campos_sql = ", ".join(
        f"{c} INTEGER PRIMARY KEY" if c == "id" else f"{c} TEXT" for c in colunas
    )

    conn = sqlite3.connect(config.DB_PATH)
    try:
        conn.execute(f"DROP TABLE IF EXISTS {config.TABLE_NAME}")
        conn.execute(f"CREATE TABLE {config.TABLE_NAME} ({campos_sql})")
        conn.commit()
        # 'id' vira INTEGER PRIMARY KEY (= rowid), garantindo que
        # db.inserir_cliente()/lastrowid e 'id' fiquem sempre sincronizados.
        df.to_sql(config.TABLE_NAME, conn, if_exists="append", index=False)
        conn.commit()
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Recria o banco mesmo se crm.db já existir (apaga dados atuais).",
    )
    args = parser.parse_args()

    if config.DB_PATH.exists() and not args.force:
        print(
            f"{config.DB_PATH.name} já existe — nada foi alterado.\n"
            "Use 'python migrate.py --force' para reimportar do Excel "
            "(isso apaga qualquer edição feita pelo CRM)."
        )
        return

    df = carregar_excel()
    criar_banco(df)
    print(f"OK: {len(df)} registros importados para {config.DB_PATH}")


if __name__ == "__main__":
    main()
