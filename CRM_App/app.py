"""
CRM Briks — visualização, busca e filtro de clientes/cartões de visita.

Rodar com:  streamlit run app.py
(ou clicando em Iniciar_CRM.bat)
"""
from pathlib import Path

import streamlit as st

import config
import db

st.set_page_config(page_title="Briks CRM", layout="wide")


# ---------------------------------------------------------------------------
# Cabeçalho com logo
# ---------------------------------------------------------------------------
col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    if config.LOGO_PATH.exists():
        st.image(str(config.LOGO_PATH), width=140)
with col_titulo:
    st.title("CRM de Clientes — Cartões de Visita")

if not config.DB_PATH.exists():
    st.error(
        f"Banco de dados não encontrado em {config.DB_PATH}.\n\n"
        "Rode primeiro: python migrate.py"
    )
    st.stop()


# ---------------------------------------------------------------------------
# Busca livre + filtros por rótulo
# ---------------------------------------------------------------------------
st.subheader("Buscar e filtrar")

texto_busca = st.text_input(
    "Buscar (nome, cargo, empresa, produtos, notas, e-mail)",
    placeholder="Digite para filtrar...",
)

col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    pastas_sel = st.multiselect("Pasta", db.valores_distintos("pasta"))
with col_f2:
    empresas_sel = st.multiselect("Empresa", db.valores_distintos("empresa"))
with col_f3:
    paises_sel = st.multiselect("País", db.valores_distintos("pais"))

df = db.listar_clientes(
    texto_busca=texto_busca,
    pastas=pastas_sel,
    empresas=empresas_sel,
    paises=paises_sel,
)

st.caption(f"{len(df)} cliente(s) encontrado(s)")


# ---------------------------------------------------------------------------
# Tabela + painel de imagem do cartão
# ---------------------------------------------------------------------------
def caminho_imagem(imagem_rel: str, reduzida: bool = True) -> Path | None:
    """Resolve o caminho local do cartão a partir do valor da coluna
    'imagem' (ex.: 'America do Sul/agritrade_.jpg'). Se reduzida=True,
    procura a versão dentro da subpasta 'reducidas'; se não existir, cai
    para a imagem original."""
    if not imagem_rel:
        return None
    rel = Path(str(imagem_rel).replace("\\", "/"))
    caminho_original = config.IMAGES_DIR / rel
    if reduzida:
        caminho_reduzida = config.IMAGES_DIR / rel.parent / "reducidas" / rel.name
        if caminho_reduzida.exists():
            return caminho_reduzida
    return caminho_original if caminho_original.exists() else None


col_tabela, col_imagem = st.columns([3, 2])

with col_tabela:
    colunas_exibidas = [
        "id", "pasta", "nome", "cargo", "empresa", "telefone",
        "email", "website", "pais", "produtos",
    ]
    evento = st.dataframe(
        df[colunas_exibidas] if not df.empty else df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key="tabela_clientes",
    )

with col_imagem:
    st.markdown("**Cartão de visita**")
    linhas_selecionadas = evento.selection.rows if evento and evento.selection else []
    if not linhas_selecionadas:
        st.info("Selecione uma linha na tabela para ver o cartão.")
    else:
        linha = df.iloc[linhas_selecionadas[0]]
        st.markdown(f"**{linha['nome'] or '(sem nome)'}** — {linha['empresa'] or ''}")
        img_path = caminho_imagem(linha["imagem"])
        if img_path:
            st.image(str(img_path), use_container_width=True)
        else:
            st.warning("Imagem do cartão não encontrada no disco.")
        if linha.get("notes"):
            st.caption(f"Notas: {linha['notes']}")
        if linha.get("revisar"):
            st.caption(f"Revisar: {linha['revisar']}")


# ---------------------------------------------------------------------------
# Gerenciar registros (inserir / editar / excluir)
# ---------------------------------------------------------------------------
with st.expander("Gerenciar registros (inserir / editar / excluir)"):
    aba_inserir, aba_editar, aba_excluir = st.tabs(
        ["Inserir novo", "Editar existente", "Excluir"]
    )

    campos = [c for c in db.EDITABLE_COLUMNS if c not in ("imagem", "imagem_reduzida_link")]

    with aba_inserir:
        with st.form("form_inserir"):
            novos_valores = {c: st.text_input(c.capitalize()) for c in campos}
            if st.form_submit_button("Inserir cliente"):
                novo_id = db.inserir_cliente(
                    {k: v for k, v in novos_valores.items() if v}
                )
                st.success(f"Cliente inserido com id {novo_id}.")
                st.rerun()

    with aba_editar:
        ids_disponiveis = df["id"].tolist() if not df.empty else []
        id_editar = st.selectbox("ID do cliente a editar", ids_disponiveis, key="sel_editar")
        if id_editar is not None:
            atual = db.obter_cliente(int(id_editar))
            with st.form("form_editar"):
                valores_editados = {
                    c: st.text_input(c.capitalize(), value=atual.get(c) or "")
                    for c in campos
                }
                if st.form_submit_button("Salvar alterações"):
                    db.editar_cliente(int(id_editar), valores_editados)
                    st.success("Cliente atualizado.")
                    st.rerun()

    with aba_excluir:
        ids_disponiveis = df["id"].tolist() if not df.empty else []
        id_excluir = st.selectbox("ID do cliente a excluir", ids_disponiveis, key="sel_excluir")
        confirmar = st.checkbox("Confirmo que quero excluir este cliente")
        if st.button("Excluir cliente", disabled=not confirmar):
            db.deletar_cliente(int(id_excluir))
            st.success("Cliente excluído.")
            st.rerun()
