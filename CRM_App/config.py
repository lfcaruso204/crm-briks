"""
Configurações de caminhos do CRM Briks.

Suposição: esta pasta (CRM_App) fica dentro de RICEX_CRM_CARTOES, ao lado
da pasta imagens_unidas (que contém allcards.xlsx, brikslogo1.png e as
subpastas de imagens de cartões). Se a estrutura de pastas for movida,
ajuste apenas IMAGES_DIR abaixo.
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IMAGES_DIR = (BASE_DIR.parent / "imagens_unidas").resolve()

EXCEL_PATH = IMAGES_DIR / "NovaTabela.xlsx"
EXCEL_SHEET = "NovaTabela"

DB_PATH = Path("crm.db")
LOGO_PATH = IMAGES_DIR / "brikslogo1.png"

TABLE_NAME = "clientes"

# CORRIGIDO: Mapeamento atualizado conforme os novos cabeçalhos do seu Excel
COLUMN_MAP = {
    "id": "id",
    "pasta": "pasta",
    "nome": "nome",
    "cargo": "cargo",
    "empresa": "empresa",
    "telefone": "telefone",
    "email": "email",
    "website": "website",
    "pais": "pais",
    "produtos": "produtos",
    "Imagem": "imagem",
    "Imagem_Reduzida_Link": "imagem_reduzida_link",
    "subproduto": "notes",  # Mapeia a coluna 'subproduto' do Excel para a 'notes' usada no banco e no app.py
}

# Colunas de texto usadas na busca livre (campo de digitação).
SEARCH_COLUMNS = ["nome", "cargo", "empresa", "produtos", "notes", "email"]

# Colunas usadas nos filtros de seleção (rótulos clicáveis).
FILTER_COLUMNS = ["pasta", "empresa", "pais"]

