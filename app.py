import streamlit as st
import pandas as pd
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.client_credential import ClientCredential
from datetime import datetime
import io


# === CONFIGURAÇÕES DE CONEXÃO ===
site_url = "https://fincareconsulting.sharepoint.com/sites/GrupoZelus"
client_id = "SEU_CLIENT_ID"
client_secret = "SEU_CLIENT_SECRET"
library_name = "CLIENTES"  # Nome da biblioteca

# === CONEXÃO COM SHAREPOINT ===
def conectar_sharepoint():
    ctx = ClientContext(site_url).with_credentials(ClientCredential(client_id, client_secret))
    return ctx


# === LISTAR PASTAS ===
def listar_pastas(folder):
    folder.expand(["Folders"]).get().execute_query()
    pastas = []
    for subfolder in folder.folders:
        pastas.append({
            "name": subfolder.properties["Name"],
            "serverRelativeUrl": subfolder.properties["ServerRelativeUrl"]
        })
    return pastas


# === INTERFACE STREAMLIT ===
st.set_page_config(page_title="Backup Grupo Zelus", page_icon="🗂️")
st.title("🗂️ Sistema de Backup Grupo Zelus")
st.subheader("Navegue nas pastas da biblioteca CLIENTES e realize backups")

# === Upload do arquivo ===
uploaded_file = st.file_uploader("Selecione o arquivo para backup")

# === Conectar e navegar nas pastas ===
ctx = conectar_sharepoint()
root_folder = ctx.web.get_folder_by_server_relative_url(f"/sites/GrupoZelus/{library_name}")
ctx.load(root_folder).execute_query()

st.markdown("### 🌐 Selecione a pasta de destino:")

# === Navegação dinâmica ===
current_folder = root_folder
path_selecionado = "/sites/GrupoZelus/CLIENTES"

navegando = True
while navegando:
    pastas = listar_pastas(current_folder)
    if not pastas:
        st.info(f"📂 Pasta final: `{path_selecionado}`")
        navegando = False
        break

    nomes_pastas = [p["name"] for p in pastas]
    escolha = st.selectbox(f"Pasta dentro de `{path_selecionado}`:", ["-- SELECIONAR --"] + nomes_pastas)

    if escolha == "-- SELECIONAR --":
        navegando = False
    else:
        pasta_escolhida = next((p for p in pastas if p["name"] == escolha), None)
        path_selecionado = pasta_escolhida["serverRelativeUrl"]
        current_folder = ctx.web.get_folder_by_server_relative_url(path_selecionado)
        ctx.load(current_folder).execute_query()

st.markdown(f"✅ **Pasta destino selecionada:** `{path_selecionado}`")

# === Observação ===
observacao = st.text_area("Digite o motivo do backup:")

# === Botão de execução ===
if st.button("🚀 Realizar Backup"):

    if not uploaded_file:
        st.error("⚠️ Você precisa selecionar um arquivo.")
    elif not observacao.strip():
        st.error("⚠️ A observação é obrigatória.")
    else:
        try:
            nome_arquivo = uploaded_file.name
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_backup = f'BACKUP_{timestamp}_{nome_arquivo}'

            file_content = uploaded_file.getvalue()

            target_folder = ctx.web.get_folder_by_server_relative_url(path_selecionado)
            target_folder.upload_file(nome_backup, file_content).execute_query()

            st.success(f"✅ Backup `{nome_backup}` enviado com sucesso para `{path_selecionado}`")

            # === Registrar no diário de bordo (opcional) ===
            # Aqui você pode implementar o mesmo processo pra salvar um arquivo de diário no SharePoint

        except Exception as e:
            st.error(f"❌ Ocorreu um erro no backup: {e}")
