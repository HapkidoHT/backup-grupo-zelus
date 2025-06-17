import streamlit as st
import pandas as pd
from datetime import datetime
import getpass
import os


st.set_page_config(page_title="Sistema de Backup Grupo Zelus", page_icon="🗂️")

st.title("🗂️ Sistema de Backup Grupo Zelus")
st.subheader("Realize backup de arquivos e registre no diário de bordo")

# Upload do arquivo
uploaded_file = st.file_uploader("Selecione o arquivo para backup")

# Observação
observacao = st.text_area("Digite o motivo do backup:")

# Botão de executar
if st.button("🚀 Realizar Backup"):

    if not uploaded_file:
        st.error("⚠️ Você precisa selecionar um arquivo.")
    elif not observacao.strip():
        st.error("⚠️ A observação é obrigatória.")
    else:
        try:
            usuario = getpass.getuser()
            data_atual = datetime.now().strftime('%d/%m/%Y')
            hora_atual = datetime.now().strftime('%H:%M:%S')

            # Simular local onde o backup é salvo na nuvem (ex.: pasta no SharePoint)
            nome_arquivo = uploaded_file.name
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_backup = f'BACKUP_{timestamp}_{nome_arquivo}'

            pasta_backup = 'backups_salvos'
            os.makedirs(pasta_backup, exist_ok=True)

            caminho_backup = os.path.join(pasta_backup, nome_backup)

            with open(caminho_backup, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.success(f"✅ Backup realizado com sucesso: {nome_backup}")

            # Simula diário de bordo no SharePoint (local temporário no servidor)
            caminho_diario = os.path.join(pasta_backup, "diario_de_bordo.xlsx")

            if os.path.exists(caminho_diario):
                df = pd.read_excel(caminho_diario)
            else:
                df = pd.DataFrame(columns=['Usuário', 'Data', 'Hora', 'Arquivo Origem', 'Backup Gerado', 'Observação'])

            novo_registro = pd.DataFrame([{
                'Usuário': usuario,
                'Data': data_atual,
                'Hora': hora_atual,
                'Arquivo Origem': nome_arquivo,
                'Backup Gerado': caminho_backup,
                'Observação': observacao
            }])

            df = pd.concat([df, novo_registro], ignore_index=True)

            with pd.ExcelWriter(caminho_diario, engine='openpyxl', mode='w') as writer:
                df.to_excel(writer, index=False)

            st.success("📝 Registro atualizado no diário de bordo!")

        except Exception as e:
            st.error(f"❌ Erro no backup: {e}")

