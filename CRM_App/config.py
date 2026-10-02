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

EXCEL_PATH = IMAGES_DIR / "export_updated_database.xlsx"
EXCEL_SHEET = "export_updated_database"

DB_PATH = Path(__file__).parent / "crm_upd2.db"
LOGO_PATH = IMAGES_DIR / "brikslogo1.png"

TABLE_NAME = "clientes"

# Mapa: nome da coluna no Excel -> nome da coluna no banco (sem acento,
# minúsculo, compatível com SQL).
COLUMN_MAP = {
    "ID": "id",
    "Pasta": "pasta",
    "Nome": "nome",
    "Cargo": "cargo",
    "Empresa": "empresa",
    "Telefone": "telefone",
    "Email": "email",
    "Website": "website",
    "País": "pais",
    "Produtos": "produtos",
    "Imagem": "imagem",
    "Imagem_Reduzida_Link": "imagem_reduzida_link",
    "Revisar": "revisar",
    "Notes": "notes",
}

# Colunas de texto usadas na busca livre (campo de digitação).
SEARCH_COLUMNS = ["nome", "cargo", "empresa", "produtos", "notes", "email"]

# Colunas usadas nos filtros de seleção (rótulos clicáveis).
FILTER_COLUMNS = ["pasta", "empresa", "pais"]
