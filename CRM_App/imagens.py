"""
Funções para salvar novas imagens de cartão de visita no banco de imagens
(a pasta imagens_unidas), mantendo a mesma convenção já usada nos dados
existentes: <Pasta>/<arquivo> para a imagem original e
<Pasta>/reducidas/<arquivo> para a versão reduzida.
"""
import re
import unicodedata
from pathlib import Path

from PIL import Image

import config

LARGURA_MAX_REDUZIDA = 800  # px


def _nome_arquivo_seguro(nome: str) -> str:
    """Remove caracteres problemáticos do nome do arquivo, mantendo extensão."""
    nome = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    nome = re.sub(r"[^\w.\-]+", "_", nome).strip("_")
    return nome or "cartao"


def _caminho_sem_conflito(caminho: Path) -> Path:
    """Se já existir um arquivo com esse nome, adiciona _2, _3, ... até achar
    um nome livre, para nunca sobrescrever uma imagem existente."""
    if not caminho.exists():
        return caminho
    contador = 2
    while True:
        candidato = caminho.with_stem(f"{caminho.stem}_{contador}")
        if not candidato.exists():
            return candidato
        contador += 1


def salvar_novo_cartao(uploaded_file, pasta: str) -> str:
    """Salva o arquivo enviado (um UploadedFile do st.file_uploader) dentro
    de imagens_unidas/<pasta>/, cria a versão reduzida em
    imagens_unidas/<pasta>/reducidas/, e devolve o valor a gravar na coluna
    'imagem' (ex.: 'Nacionais/minhaempresa_.jpg').

    Levanta ValueError se 'pasta' estiver vazio.
    """
    pasta = (pasta or "").strip()
    if not pasta:
        raise ValueError("Informe a Pasta antes de enviar a imagem do cartão.")

    pasta_dir = config.IMAGES_DIR / pasta
    pasta_dir.mkdir(parents=True, exist_ok=True)
    reduzida_dir = pasta_dir / "reducidas"
    reduzida_dir.mkdir(parents=True, exist_ok=True)

    nome_arquivo = _nome_arquivo_seguro(uploaded_file.name)
    caminho_original = _caminho_sem_conflito(pasta_dir / nome_arquivo)
    nome_arquivo = caminho_original.name  # pode ter ganho sufixo _2, _3...

    imagem_bytes = uploaded_file.getvalue()
    caminho_original.write_bytes(imagem_bytes)

    # Versão reduzida (mesmo nome, dentro de reducidas/)
    try:
        img = Image.open(caminho_original)
        img = img.convert("RGB")
        if img.width > LARGURA_MAX_REDUZIDA:
            nova_altura = int(img.height * (LARGURA_MAX_REDUZIDA / img.width))
            img = img.resize((LARGURA_MAX_REDUZIDA, nova_altura))
        img.save(reduzida_dir / nome_arquivo, quality=85)
    except Exception:
        # Se a redução falhar por algum motivo, a imagem original já foi
        # salva e o app cai automaticamente para ela (ver app.py).
        pass

    return f"{pasta}/{nome_arquivo}"
