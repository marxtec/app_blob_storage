import streamlit as st
from azure.storage.blob import BlobServiceClient
import os

# =======================
# CONFIGURACIÓN
# =======================
BLOB_CONNECTION_STRING = os.environ.get("BLOB_CONNECTION_STRING")
CONTAINER_NAME = os.environ.get("CONTAINER_NAME", "archivos")

if not BLOB_CONNECTION_STRING:
    st.error("❌ Falta la variable de entorno BLOB_CONNECTION_STRING")
    st.stop()

# =======================
# CLIENTE BLOB
# =======================
@st.cache_resource
def get_blob_client():
    return BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)

blob_service = get_blob_client()
container = blob_service.get_container_client(CONTAINER_NAME)

# =======================
# INTERFAZ
# =======================
st.set_page_config(page_title="Blob Storage App", page_icon="☁️")
st.title("☁️ Azure Blob Storage — Subir y Descargar Archivos:D")

# --- SUBIR ARCHIVO ---
st.subheader("📤 Subir archivo")
archivo = st.file_uploader("Selecciona un archivo")

if archivo:
    if st.button("Subir a Blob Storage"):
        with st.spinner("Subiendo..."):
            container.upload_blob(
                name=archivo.name,
                data=archivo.read(),
                overwrite=True
            )
        st.success(f"✅ '{archivo.name}' subido correctamente.")

# --- LISTAR Y DESCARGAR ---
st.subheader("📂 Archivos en el contenedor")

try:
    blobs = list(container.list_blobs())
    if not blobs:
        st.info("No hay archivos aún.")
    else:
        for blob in blobs:
            col1, col2 = st.columns([3, 1])
            col1.write(blob.name)
            if col2.button("Descargar", key=blob.name):
                with st.spinner("Descargando..."):
                    data = container.get_blob_client(blob.name).download_blob().readall()
                st.download_button(
                    label=f"💾 Guardar {blob.name}",
                    data=data,
                    file_name=blob.name,
                    key=f"dl_{blob.name}"
                )
except Exception as e:
    st.error(f"Error al listar archivos: {e}")
