from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IMAGES_DIR = (BASE_DIR.parent / "imagens_unidas").resolve()

EXCEL_PATH = IMAGES_DIR / "NovaTabela.xlsx"
EXCEL_SHEET = "NovaTabela"

DB_PATH = Path("crm.db")
LOGO_PATH = IMAGES_DIR / "brikslogo1.png"

TABLE_NAME = "clientes"

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
    "subproduto": "notes",
}

SEARCH_COLUMNS = ["nome", "cargo", "empresa", "produtos", "notes", "email"]
FILTER_COLUMNS = ["pasta", "empresa", "pais"]


