# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 19:04:08 2026

@author: Luca Caruso
"""

import sqlite3
import pandas as pd
from pathlib import Path

def converter_excel_para_db():
    caminho_excel = Path("export_updated_database.xlsx")
    caminho_db = Path("crm.db")
    nome_aba = "export_updated_database"  # Nome exato da sua aba do Excel
    
    if not caminho_excel.exists():
        print(f"❌ Erro: O arquivo Excel '{caminho_excel}' não foi encontrado nesta pasta.")
        return

    print(f"🔄 1/3 - Lendo a aba '{nome_aba}' do arquivo Excel...")
    try:
        # Lê especificamente a aba informada por você
        df = pd.read_excel(caminho_excel, sheet_name=nome_aba)
        print(f"📊 Dataset carregado com sucesso: {len(df)} linhas e {len(df.columns)} colunas.")
    except Exception as e:
        print(f"❌ Erro ao ler a aba do Excel: {e}")
        return

    # ---------------------------------------------------------------------------
    # TRATAMENTO DE SEGURANÇA DAS COLUNAS (Evita o erro KeyError)
    # ---------------------------------------------------------------------------
    # Converte todos os cabeçalhos para minúsculo para evitar erros de digitação (ex: Nome -> nome)
    df.columns = [str(col).strip().lower() for col in df.columns]
    
    # Se a coluna que guarda as fotos veio com outro nome (ex: 'caminho foto', 'link', 'cartao'),
    # altere a linha abaixo substituindo 'foto_do_cartao' pelo nome real dela no seu Excel.
    # Caso ela já se chame 'imagem', o código abaixo apenas garante isso.
    possiveis_nomes_imagem = ["imagem", "imagem_rel", "link_imagem", "foto", "caminho_imagem"]
    coluna_imagem_encontrada = None
    for nome_possivel in possiveis_nomes_imagem:
        if nome_possivel in df.columns:
            coluna_imagem_encontrada = nome_possivel
            break
            
    if coluna_imagem_encontrada and coluna_imagem_encontrada != "imagem":
        df.rename(columns={coluna_imagem_encontrada: "imagem"}, inplace=True)
        print(f"✏️  Coluna '{coluna_imagem_encontrada}' renomeada automaticamente para 'imagem' por compatibilidade.")
    
    # Se a coluna 'imagem' simplesmente NÃO existir no Excel, criamos ela vazia para o app não dar erro
    if "imagem" not in df.columns:
        df["imagem"] = ""
        print("⚠️  Aviso: Coluna 'imagem' não foi detectada no Excel. Criamos uma coluna vazia por compatibilidade.")

    # ---------------------------------------------------------------------------
    # GRAVAÇÃO NO BANCO DE DADOS
    # ---------------------------------------------------------------------------
    print(f"🔌 2/3 - Conectando e gerando o banco de dados oficial '{caminho_db}'...")
    conn = sqlite3.connect(caminho_db)
    
    try:
        # O 'replace' reconstrói a tabela do zero, limpando qualquer estrutura velha que quebre o app
        df.to_sql("clientes", conn, if_exists="replace", index=False)
        print(f"\n" + "="*50)
        print(f"✅ SUCESSO ABSOLUTO! O arquivo '{caminho_db}' foi gerado.")
        print(f"A estrutura possui as colunas: {list(df.columns)}")
        print("="*50)
    except Exception as e:
        print(f"❌ Erro ao salvar no banco SQLite: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    converter_excel_para_db()
