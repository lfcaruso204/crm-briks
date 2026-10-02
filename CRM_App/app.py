""" CRM Briks — visualização, busca e filtro de clientes/cartões de visita. 
Rodar com: streamlit run app.py (ou clicando em Iniciar_CRM.bat) """ 

from pathlib import Path 
import streamlit as st 
import config 
import db 
import plotly.express as px 
import pandas as pd 

st.set_page_config( 
    page_title="Briks CRM", 
    page_icon="📊", 
    layout="wide" 
) 

# --------------------------------------------------------------------------- # 
# Cabeçalho com logo, Título original e Espaço reservado para o Donut Chart # 
# --------------------------------------------------------------------------- # 
col_logo, col_titulo, col_grafico = st.columns([1.2, 3.8, 2.5]) 
with col_logo: 
    if config.LOGO_PATH.exists(): 
        st.image(str(config.LOGO_PATH), width=140) 

with col_titulo: 
    st.markdown("## CRM de Clientes — Cartões de Visita") 

with col_grafico: 
    espaco_grafico = st.empty() 

if not config.DB_PATH.exists(): 
    st.error( 
        f"Banco de dados não encontrado em {config.DB_PATH}.\n\n" 
        "Rode primeiro: python migrate.py" 
    ) 
    st.stop() 

# --------------------------------------------------------------------------- # 
# Busca livre + filtros por rótulo + Botão Limpar Filtros                 # 
# --------------------------------------------------------------------------- # 
st.subheader("Buscar e filtrar") 

def acao_limpar_filtros():
    st.session_state["busca_texto_input"] = ""
    st.session_state["filtro_empresa"] = []
    st.session_state["filtro_pais"] = []
    st.session_state["filtro_produtos"] = []
    st.session_state["filtro_pasta"] = []

# Linha superior: Campo Buscar + Botão de Limpar
col_busca_texto, col_btn_limpar = st.columns([6, 1.5])
with col_busca_texto:
    texto_busca = st.text_input( 
        "Buscar (nome, cargo, empresa, produtos, subproduto, e-mail)", 
        placeholder="Digite para filtrar...", 
        key="busca_texto_input"
    ) 
with col_btn_limpar:
    st.markdown("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True)
    st.button("🧹 Limpar todos os filtros", on_click=acao_limpar_filtros, use_container_width=True)

# Linha inferior de filtros: Empresa, País, Produtos, Pasta
col_f1, col_f2, col_f3, col_f4 = st.columns(4) 
with col_f1: 
    empresas_sel = st.multiselect("Empresa", db.valores_distintos("empresa"), key="filtro_empresa") 
with col_f2: 
    paises_sel = st.multiselect("País", db.valores_distintos("pais"), key="filtro_pais") 
with col_f3: 
    produtos_sel = st.multiselect("Produtos", db.valores_distintos("produtos"), key="filtro_produtos") 
with col_f4: 
    pastas_sel = st.multiselect("Pasta", db.valores_distintos("pasta"), key="filtro_pasta") 

# Realiza a listagem dos dados base no banco SQLite 
df = db.listar_clientes( 
    texto_busca=texto_busca, 
    pastas=pastas_sel, 
    empresas=empresas_sel, 
    paises=paises_sel, 
) 

# Tratamento para mapear a coluna 'notes' para 'subproduto'
if not df.empty and "notes" in df.columns:
    df = df.rename(columns={"notes": "subproduto"})

# Filtra dinamicamente na memória permitindo a seleção de múltiplos produtos (busca parcial)
if produtos_sel and not df.empty: 
    mascara = df["produtos"].fillna("").apply(lambda x: any(p in str(x) for p in produtos_sel))
    df = df[mascara] 

st.caption(f"{len(df)} cliente(s) encontrado(s)") 

# --------------------------------------------------------------------------- # 
# PROCESSAMENTO E RENDERIZAÇÃO DO DONUT CHART (Apenas os 5 Principais + Outros) # 
# --------------------------------------------------------------------------- # 
if not df.empty and "produtos" in df.columns: 
    df_produtos = df["produtos"].dropna().astype(str).str.strip() 
    df_produtos = df_produtos[df_produtos != ""] 
    if not df_produtos.empty: 
        contagem_prod = df_produtos.value_counts().reset_index() 
        contagem_prod.columns = ["Produto", "Quantidade"] 
        
        if len(contagem_prod) > 5: 
            principais = contagem_prod.head(5).copy() 
            soma_restante = contagem_prod.iloc[5:]["Quantidade"].sum() 
            linha_restante = pd.DataFrame([{"Produto": "Outros", "Quantidade": soma_restante}]) 
            contagem_prod = pd.concat([principais, linha_restante], ignore_index=True) 
 
        fig = px.pie( 
            contagem_prod, 
            values="Quantidade", 
            names="Produto", 
            hole=0.4, 
            color_discrete_sequence=px.colors.qualitative.Safe 
        ) 
        fig.update_layout( 
            margin=dict(l=10, r=10, t=10, b=10), 
            height=150, 
            showlegend=True, 
            legend=dict( 
                orientation="v", 
                yanchor="middle", 
                y=0.5, 
                xanchor="left", 
                x=1.1, 
                font=dict(size=10) 
            ) 
        ) 
        fig.update_traces(textposition='auto', textinfo='value') 
        espaco_grafico.plotly_chart(fig, use_container_width=True, key="donut_chart_topo") 
    else: 
        espaco_grafico.caption("Sem produtos cadastrados para gerar o gráfico.") 
else: 
    espaco_grafico.caption("Aguardando dados dos produtos...") 

st.markdown("---") 

# --------------------------------------------------------------------------- # 
# Tabela estática com Checkbox nativo de seleção + painel de imagem do cartão # 
# --------------------------------------------------------------------------- # 
def caminho_imagem(imagem_rel: str, reduzida: bool = True) -> Path | None: 
    if not imagem_rel: 
        return None 
    rel = Path(str(imagem_rel).replace("\\", "/")) 
    caminho_original = config.IMAGES_DIR / rel 
    if reduzida: 
        caminho_reduzida = config.IMAGES_DIR / rel.parent / "reducidas" / rel.name 
        if caminho_reduzida.exists(): 
            return caminho_reduzida 
    return caminho_original if caminho_original.exists() else None 

# CORRIGIDO AQUI: Adicionado a proporção explícita de tamanho das colunas [3, 2]
col_tabela, col_imagem = st.columns([3, 2]) 

with col_tabela: 
    colunas_exibidas = [ 
        "id", "empresa", "pais", "produtos", "subproduto", "nome", "cargo", "email", "telefone", "website", "pasta"
    ] 
    
    evento = st.dataframe( 
        df[colunas_exibidas] if not df.empty else df, 
        use_container_width=True, 
        hide_index=True, 
        on_select="rerun", 
        selection_mode="single-row", 
        key="tabela_clientes", 
    ) 

    linhas_selecionadas = evento.selection.rows if evento and evento.selection else [] 
    
    if linhas_selecionadas and linhas_selecionadas[0] < len(df):
        cliente_focado = df.iloc[linhas_selecionadas[0]]
        empresa_bt = cliente_focado['empresa'] or '(Sem Empresa)'
        nome_bt = cliente_focado['nome'] or '(Sem Nome)'
        
        if st.button(f"✏️ Editar dados de {empresa_bt} — {nome_bt}"):
            st.session_state["sel_editar"] = int(cliente_focado["id"])
            st.toast("ID carregado na aba Editar existente!", icon="👇")

with col_imagem: 
    st.markdown("**Cartão de visita**") 
    
    if not linhas_selecionadas or linhas_selecionadas[0] >= len(df): 
        st.info("Marque o checkbox de uma linha na tabela para ver o cartão correspondente.") 
        linha_selecionada_dados = None
    else: 
        linha_selecionada_dados = df.iloc[linhas_selecionadas[0]] 
        st.markdown(f"**{linha_selecionada_dados['nome'] or '(sem nome)'}** — {linha_selecionada_dados['empresa'] or ''}") 
        img_path = caminho_imagem(linha_selecionada_dados["imagem"]) 
        if img_path: 
            st.image(str(img_path), use_container_width=True) 
        else: 
            st.warning("Imagem do cartão não encontrada no disco.") 
        if linha_selecionada_dados.get("subproduto"): 
            st.caption(f"Subproduto: {linha_selecionada_dados['subproduto']}") 
        if linha_selecionada_dados.get("revisar"): 
            st.caption(f"Revisar: {linha_selecionada_dados['revisar']}") 


# --------------------------------------------------------------------------- # 
# Gerenciar registros (Ordem: Editar, Inserir, Excluir)                       # 
# --------------------------------------------------------------------------- # 
with st.expander("Gerenciar registros (editar / inserir / excluir)"): 
    aba_editar, aba_inserir, aba_excluir = st.tabs( 
        ["Editar existente", "Inserir novo", "Excluir"] 
    ) 
    campos = [c if c != "notes" else "subproduto" for c in db.EDITABLE_COLUMNS if c not in ("imagem", "imagem_reduzida_link")] 
    
    with aba_editar: 
        ids_disponiveis = df["id"].tolist() if not df.empty else [] 
        if not ids_disponiveis: 
            st.info("Nenhum cliente disponível para edição com os filtros atuais.") 
        else: 
            id_editar = st.selectbox("ID do cliente a editar", ids_disponiveis, key="sel_editar") 
            
            if id_editar is not None: 
                if "id_sendo_editado" not in st.session_state or st.session_state["id_sendo_editado"] != id_editar:
                    st.session_state["id_sendo_editado"] = id_editar
                    dados_banco = db.obter_cliente(int(id_editar))
                    if dados_banco and "notes" in dados_banco:
                        dados_banco["subproduto"] = dados_banco.pop("notes")
                    st.session_state["dados_cliente_atual"] = dados_banco
                
                dados_atuais = st.session_state["dados_cliente_atual"]
                
                with st.form("form_editar"): 
                    valores_editados = {} 
                    col_edit1, col_edit2 = st.columns(2) 
                    
                    for idx, c in enumerate(campos): 
                        with col_edit1 if idx % 2 == 0 else col_edit2: 
                            rotulo = "Pasta / Categoria" if c == "pasta" else ("Subproduto" if c == "subproduto" else c.capitalize())
                            valor_inicial = dados_atuais.get(c) or ""
                            
                            valores_editados[c] = st.text_input(
                                rotulo, 
                                value=str(valor_inicial), 
                                key=f"edt_{c}"
                            ) 
                    
                    st.markdown("---")
                    arquivo_imagem_edt = st.file_uploader(
                        "Substituir imagem do cartão (Opcional)", 
                        type=["jpg", "jpeg", "png"], 
                        key="edt_upload_imagem"
                    )

                    if st.form_submit_button("Salvar alterações"): 
                        payload_editado = {}
                        for k, v in valores_editados.items():
                            chave_final = "notes" if k == "subproduto" else k
                            payload_editado[chave_final] = v.strip()
                        
                        if arquivo_imagem_edt:
                            subpasta_alvo = payload_editado.get("pasta", "Geral").strip() or "Geral"
                            diretorio_destino = config.IMAGES_DIR / subpasta_alvo
                            diretorio_destino.mkdir(parents=True, exist_ok=True)
                            
                            caminho_arquivo_final = diretorio_destino / arquivo_imagem_edt.name
                            with open(caminho_arquivo_final, "wb") as f:
                                f.write(arquivo_imagem_edt.getbuffer())
                                
                            payload_editado["imagem"] = f"{subpasta_alvo}/{arquivo_imagem_edt.name}"
                        
                        db.editar_cliente(int(id_editar), payload_editado) 
                        
                        if "id_sendo_editado" in st.session_state:
                            del st.session_state["id_sendo_editado"]
                        if "dados_cliente_atual" in st.session_state:
                            del st.session_state["dados_cliente_atual"]
                            
                        st.success("Cliente atualizado com sucesso.") 
                        st.rerun() 

    with aba_inserir: 
        with st.form("form_inserir", clear_on_submit=True): 
            novos_valores = {} 
            col_form1, col_form2 = st.columns(2) 
            for idx, c in enumerate(campos): 
                with col_form1 if idx % 2 == 0 else col_form2: 
                    rotulo = "Pasta / Categoria" if c == "pasta" else ("Subproduto" if c == "subproduto" else c.capitalize())
                    novos_valores[c] = st.text_input(rotulo, key=f"ins_{c}") 
            
            st.markdown("---")
            arquivo_imagem = st.file_uploader(
                "Upload do Cartão de Visita (Imagem)", 
                type=["jpg", "jpeg", "png"], 
                key="ins_upload_imagem"
            )
            
            if st.form_submit_button("Inserir cliente"): 
                if not any(novos_valores.values()) and not arquivo_imagem: 
                    st.error("Por favor, preencha pelo menos um campo para inserir.") 
                else: 
                    payload_db = {}
                    for k, v in novos_valores.items():
                        chave_final = "notes" if k == "subproduto" else k
                        if v.strip():
                            payload_db[chave_final] = v.strip()
                    
                    if arquivo_imagem:
                        subpasta_alvo = payload_db.get("pasta", "Geral").strip() or "Geral"
                        diretorio_destino = config.IMAGES_DIR / subpasta_alvo
                        diretorio_destino.mkdir(parents=True, exist_ok=True)
                        
                        caminho_arquivo_final = diretorio_destino / arquivo_imagem.name
                        with open(caminho_arquivo_final, "wb") as f:
                            f.write(arquivo_imagem.getbuffer())
                            
                        payload_db["imagem"] = f"{subpasta_alvo}/{arquivo_imagem.name}"
                    
                    novo_id = db.inserir_cliente(payload_db) 
                    st.success(f"Cliente inserido com sucesso! ID: {novo_id}.") 
                    st.rerun() 

    with aba_excluir: 
        ids_disponiveis = df["id"].tolist() if not df.empty else [] 
        if not ids_disponiveis: 
            st.info("Nenhum cliente disponível para exclusão com os filtros atuais.") 
        else: 
            id_excluir = st.selectbox("ID do cliente a excluir", ids_disponiveis, key="sel_excluir") 
            confirmar = st.checkbox("Confirmo que quero excluir definitivamente este cliente", key="chk_deletar") 
            
            if st.button("Excluir cliente", disabled=not confirmar, type="primary", key="btn_deletar"): 
                db.deletar_cliente(int(id_excluir)) 
                
                if "id_sendo_editado" in st.session_state and st.session_state["id_sendo_editado"] == id_excluir:
                    del st.session_state["id_sendo_editado"]
                    if "dados_cliente_atual" in st.session_state:
                        del st.session_state["dados_cliente_atual"]
                        
                st.success("Cliente excluído com sucesso.") 
                st.rerun()





#%%
# PowerShell
# "C:\Anaconda\envs\crm_env\Scripts\streamlit.exe" run "C:\Users\Luca Caruso\Desktop\Projetos\Case Ricex\RICEX_CRM_CARTOES\CRM_App\app.py"

# conda activate crm_env
# cd "C:\Users\Luca Caruso\Desktop\Projetos\Case Ricex\RICEX_CRM_CARTOES\CRM_App"
# streamlit run app.py
