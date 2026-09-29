# CRM Briks

CRM de clientes e cartões de visita: visualização, busca, filtros e cadastro,
com banco SQLite e interface em Streamlit.

## Estrutura

```
CRM_App/            código do app (app.py, db.py, config.py, migrate.py, imagens.py)
CRM_App/crm.db       banco SQLite já populado (gerado a partir de allcards.xlsx)
imagens_unidas/      allcards.xlsx, brikslogo1.png e as imagens dos cartões por pasta
```

## Rodar localmente

Windows: dê duplo clique em `CRM_App/Iniciar_CRM.bat`.

Manual:
```
cd CRM_App
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy (Streamlit Community Cloud)

- **Main file path:** `CRM_App/app.py`
- **Requirements:** `requirements.txt` (raiz do repositório)

## Importante — armazenamento no app hospedado

O banco (`crm.db`) e as imagens ficam dentro do próprio repositório. Isso é
ótimo para *visualizar, buscar e filtrar* os 615+ registros a partir de
qualquer lugar.

Porém, o Streamlit Community Cloud usa um sistema de arquivos **temporário**:
qualquer cliente inserido, editado, excluído ou imagem enviada *durante o uso
do app hospedado* fica salvo apenas enquanto aquele container estiver ativo.
Ao dormir por inatividade ou ser reimplantado, o app volta a ler exatamente o
que está no GitHub — as alterações feitas só na nuvem se perdem.

Fluxo recomendado enquanto isso:
1. Cadastros e edições "de verdade" são feitos localmente (`Iniciar_CRM.bat`),
   onde tudo é gravado direto em `crm.db` e em `imagens_unidas`.
2. De vez em quando, sobe essas mudanças pro GitHub (`git add` / `commit` /
   `push`) para que o app na nuvem reflita os dados atualizados.

Se no futuro for necessário editar direto pelo app hospedado com persistência
permanente, isso exige trocar o SQLite local por um banco externo (ex.:
Supabase/Postgres, Turso) e as imagens por um bucket (ex.: S3, Cloudinary) —
não é o caso hoje, mas fica registrado como próximo passo possível.
