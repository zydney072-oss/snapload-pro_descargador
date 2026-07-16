import streamlit as st
import yt_dlp
import os

# Asegurar que la carpeta de descargas exista
if not os.path.exists('descargas'):
    os.makedirs('descargas')

# ==========================================
# MOTOR DE DESCARGA PROFESIONAL (ESTILO WEB)
# ==========================================
def descargar_contenido(url, solo_audio=False, solo_imagen=False):
    opciones = {
     'outtmpl': '%(id)s.%(ext)s',
        # Simulamos que somos la app oficial de Android para evitar que nos bloqueen
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        },
        'ignoreerrors': True,
        # Forzamos a yt-dlp a que use extractores que imitan a celulares reales
        'extractor_args': {
            'instagram': ['embed'],
            'youtube': ['player_client=android_embedytdlp,web']
        }
    }
    
    if solo_audio:
        opciones.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    elif solo_imagen:
        opciones.update({
            'skip_download': True,
            'writethumbnail': True,
        'outtmpl': '%(id)s',

                   })
    else:
        # Buscamos el formato mp4 de mejor calidad que no requiera descifrado complejo
        opciones.update({
            'format': 'best[ext=mp4]/best', 
        })
        
    try:
        with yt_dlp.YoutubeDL(opciones) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                return None
                
            if 'entries' in info:
                info = info['entries'][0]
                
            filename = ydl.prepare_filename(info)
            
            if solo_audio:
                filename = os.path.splitext(filename)[0] + ".mp3"
            elif solo_imagen:
                base = os.path.splitext(filename)[0]
                for ext in ['.jpg', '.png', '.webp', '.jpeg']:
                    if os.path.exists(base + ext):
                        return base + ext
                if 'thumbnails' in info and len(info['thumbnails']) > 0:
                    return info['thumbnails'][-1]['url']
                    
            return filename
    except Exception as e:
        print(f"Error interno: {e}") 
        return None

# ==========================================
# INTERFAZ VISUAL (ALINEACIÓN PERFECTA)
# ==========================================
st.set_page_config(page_title="SnapLoad Pro", page_icon="⚡", layout="centered")

st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>⚡ SnapLoad Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Descarga Videos, Audio e Imágenes Públicas de Redes Sociales</p>", unsafe_allow_html=True)
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
    col_link, col_boton = st.columns([22, 1])  # Ajuste fino para pantallas grandes y chicas

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

# 4. Las pestañas de descarga
tab1, tab2, tab3 = st.tabs(["🎥 Video MP4", "🎵 Audio MP3", "🖼️ Imagen / Foto"])

with tab1:
    st.write("Descarga videos completos o Reels en formato MP4.")
    if st.button("🚀 Procesar Video", key="btn_vid"):
        if enlace_usuario:
            with st.spinner("Procesando tu video..."):
                archivo = descargar_contenido(enlace_usuario, solo_audio=False)
                if archivo and os.path.exists(archivo):
                    st.success("✅ ¡Video listo para descargar!")
                    st.video(archivo)
                    with open(archivo, "rb") as file:
                        st.download_button(label="💾 Guardar Video en mi dispositivo", data=file, file_name=os.path.basename(archivo), mime="video/mp4", use_container_width=True)
                else:
                    st.error("❌ No se pudo descargar. Verifica que el enlace sea de un video o Reel público.")
        else:
            st.warning("⚠️ Pega un enlace primero.")

with tab2:
    st.write("Convierte el contenido a Audio MP3.")
    if st.button("🎵 Procesar MP3", key="btn_aud"):
        if enlace_usuario:
            with st.spinner("Extrayendo audio..."):
                archivo = descargar_contenido(enlace_usuario, solo_audio=True)
                if archivo and os.path.exists(archivo):
                    st.success("✅ ¡Audio listo para descargar!")
                    st.audio(archivo)
                    with open(archivo, "rb") as file:
                        st.download_button(label="💾 Guardar MP3 en mi dispositivo", data=file, file_name=os.path.basename(archivo), mime="audio/mp3", use_container_width=True)
                else:
                    st.error("❌ Error de procesamiento. Verifica que el video esté disponible en público.")
        else:
            st.warning("⚠️ Pega un enlace primero.")

with tab3:
    st.write("Extrae la foto o la portada de la publicación.")
    if st.button("🖼️ Procesar Imagen", key="btn_img"):
        if enlace_usuario:
            with st.spinner("Buscando imagen..."):
                archivo = descargar_contenido(enlace_usuario, solo_imagen=True)
                if archivo:
                    st.success("✅ ¡Imagen localizada!")
                    if isinstance(archivo, str) and archivo.startswith("http"):
                        st.image(archivo, use_container_width=True)
                        st.markdown(f"[📥 Haz clic aquí para abrir y guardar la foto]({archivo})")
                    elif os.path.exists(archivo):
                        st.image(archivo, use_container_width=True)
                        with open(archivo, "rb") as file:
                            st.download_button(label="💾 Guardar Imagen en mi dispositivo", data=file, file_name=os.path.basename(archivo), mime="image/jpeg", use_container_width=True)
                else:
                    st.error("❌ No se pudo extraer la imagen de este enlace.")
        else:
            st.warning("⚠️ Pega un enlace primero.")
