import streamlit as st
from tkinter import Tk, filedialog
import shutil
import os
import pandas as pd
from datetime import datetime
import getpass


# === CONFIGURAÇÃO DA PÁGINA ===
st.set_page_config(page_title="Sistema de Backup Grupo Zelus", page_icon="🗂️", layout="centered")

st.title("🗂️ Sistema de Backup Grupo Zelus")
st.subheader("Realize backup de arquivos e registre no diário de bordo")


# === FUNÇÃO PARA SELECIONAR PASTA ===
def selecionar_pasta():
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    pasta = filedialog.askdirectory()
    root.destroy()
    return pasta


# === INICIALIZAÇÃO DE ESTADOS ===
if "pasta_destino" not in st.session_state:
    st.session_state["pasta_destino"] = ""


# === INPUTS ===
uploaded_file = st.file_uploader("Selecione o arquivo para backup", type=None)

st.write("Selecione a pasta onde será salvo o backup:")

# Input de texto, preenchido pelo botão de seleção de pasta
pasta_destino = st.text_input(
    "Pasta de Destino",
    value=st.session_state["pasta_destino"],
    key="input_pasta"
)

# Botão para abrir o explorador de arquivos e selecionar a pasta
if st.button("📂 Selecionar Pasta"):
    pasta = selecionar_pasta()
    if pasta:
        st.session_state["pasta_destino"] = pasta
        st.rerun()  # 🔥 Atualiza a interface para refletir o novo valor


# Observação
observacao = st.text_area("Digite o motivo do backup:")


# === BOTÃO EXECUTAR ===
if st.button("🚀 Realizar Backup"):

    if not uploaded_file:
        st.error("⚠️ Você precisa selecionar um arquivo.")
    elif not st.session_state["pasta_destino"]:
        st.error("⚠️ Você precisa selecionar a pasta de destino.")
    elif not observacao.strip():
        st.error("⚠️ A observação é obrigatória.")
    else:
        try:
            # === GERAR NOME DO BACKUP ===
            nome_arquivo = uploaded_file.name
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_backup = f'BACKUP_{timestamp}_{nome_arquivo}'

            caminho_backup = os.path.join(st.session_state["pasta_destino"], nome_backup)

            # === SALVAR ARQUIVO NA PASTA DESTINO ===
            with open(caminho_backup, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # === CONFIGURAR DIÁRIO DE BORDO ===
            usuario = getpass.getuser()
            caminho_diario = fr'C:\Users\{usuario}\Grupo Zelus\Grupo Zelus - CLIENTES\ZZ1001_DIARIO DE BORDO\diario_de_bordo.xlsx'
            aba_diario = 'Registros'

            data_atual = datetime.now().strftime('%d/%m/%Y')
            hora_atual = datetime.now().strftime('%H:%M:%S')

            # === LEITURA DO DIÁRIO DE BORDO ===
            if os.path.exists(caminho_diario):
                try:
                    df = pd.read_excel(caminho_diario, sheet_name=aba_diario)
                except:
                    df = pd.DataFrame(columns=['Usuário', 'Data', 'Hora', 'Arquivo Origem', 'Backup Gerado', 'Observação'])
            else:
                df = pd.DataFrame(columns=['Usuário', 'Data', 'Hora', 'Arquivo Origem', 'Backup Gerado', 'Observação'])

            # === NOVO REGISTRO ===
            novo_registro = pd.DataFrame([{
                'Usuário': usuario,
                'Data': data_atual,
                'Hora': hora_atual,
                'Arquivo Origem': nome_arquivo,
                'Backup Gerado': caminho_backup,
                'Observação': observacao
            }])

            df = pd.concat([df, novo_registro], ignore_index=True)

            # === SALVAR NO DIÁRIO ===
            with pd.ExcelWriter(caminho_diario, engine='openpyxl', mode='w') as writer:
                df.to_excel(writer, sheet_name=aba_diario, index=False)

            st.success(f"✅ Backup realizado com sucesso em:\n{caminho_backup}")

        except Exception as e:
            st.error(f"❌ Ocorreu um erro: {e}")
