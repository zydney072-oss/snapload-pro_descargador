import streamlit as st
import requests
import os

# ==========================================
# MOTOR DE DESCARGA INDESTRUCTIBLE (VÍA API)
# ==========================================
def descargar_contenido_api(url):
    # Aseguramos que la carpeta de descargas exista
    if not os.path.exists('descargas'):
        os.makedirs('descargas')
        
    # Usamos una API pública y gratuita de descarga de videos (Cobalt API)
    api_url = "https://api.cobalt.tools/api/json"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # Configuramos la petición para la API
    payload = {
        "url": url,
        "vCodec": "h264", # Forzamos formato mp4 compatible con web
        "isAudioOnly": False
    }
    
    try:
        # 1. Le pedimos el video procesado a la API
        respuesta = requests.post(api_url, json=payload, headers=headers)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            # Si la API nos devuelve un enlace directo de descarga
            if "url" in datos:
                video_url = datos["url"]
                
                # 2. Descargamos el archivo temporalmente en nuestro servidor
                nombre_archivo = os.path.join("descargas", "video_descargado.mp4")
                descarga_file = requests.get(video_url, stream=True)
                
                with open(nombre_archivo, 'wb') as f:
                    for chunk in descarga_file.iter_content(chunk_size=1024*1024):
                        if chunk:
                            f.write(chunk)
                            
                return nombre_archivo
    except Exception as e:
        print(f"Error en API: {e}")
    return None

# ==========================================
# INTERFAZ VISUAL (ALINEACIÓN PERFECTA)
# ==========================================
st.set_page_config(page_title="SnapLoad Pro", page_icon="⚡", layout="centered")

st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>⚡ SnapLoad Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Descarga de forma segura desde YouTube, TikTok, Facebook e Instagram</p>", unsafe_allow_html=True)
st.write("---")

# TRUCO CSS: Alineación vertical perfecta
st.markdown("""
    <style>
    div[data-testid="stButton"] {
        margin-top: 0px;
    }
    </style>
""", unsafe_allow_html=True)

def limpiar_enlace():
    st.session_state["url_input"] = ""

# Contenedor para la barra de búsqueda y el botón alineados
with st.container():
    col_link, col_boton = st.columns([22, 1])

    with col_link:
        enlace_usuario = st.text_input(
            "🔗 Pega el enlace aquí:", 
            placeholder="Pega tu enlace de Instagram, TikTok, Facebook o YouTube...", 
            key="url_input",
            label_visibility="collapsed"
        )

    with col_boton:
        if st.button("🧹", on_click=limpiar_enlace, help="Limpiar barra", use_container_width=True):
            st.rerun()

# Pestaña de Descarga Única Estabilizada
st.write("Descarga videos completos o Reels de forma garantizada.")
if st.button("🚀 Procesar Video", key="btn_vid", use_container_width=True):
    if enlace_usuario:
        with st.spinner("Procesando tu video a través de un túnel seguro... Esto puede tardar unos segundos..."):
            archivo = descargar_contenido_api(enlace_usuario)
            if archivo and os.path.exists(archivo):
                st.success("✅ ¡Video listo para descargar!")
                st.video(archivo)
                with open(archivo, "rb") as file:
                    st.download_button(
                        label="💾 Guardar Video en mi dispositivo", 
                        data=file, 
                        file_name="SnapLoad_Video.mp4", 
                        mime="video/mp4", 
                        use_container_width=True
                    )
            else:
                st.error("❌ El servidor de la red social bloqueó la petición directa. Intenta con otro enlace o inténtalo más tarde.")
    else:
        st.warning("⚠️ Pega un enlace primero.")
