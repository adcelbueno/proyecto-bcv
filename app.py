import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Configuración de la página (Responsiva e Innovadora)
st.set_page_config(
    page_title="Monitor BCV - adnetwork.ve",
    page_icon="💵",
    layout="centered"
)

# Estilo Personalizado para Modo Nocturno Dinámico y Diseño
st.markdown("""
    <style>
    .main { text-align: center; }
    .tasa-box {
        padding: 30px;
        border-radius: 20px;
        background-color: #1a73e810;
        border: 1px solid #1a73e830;
        margin-bottom: 25px;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        text-align: center;
        color: gray;
        font-size: 0.8rem;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

def obtener_datos():
    """Conecta con la DB y extrae el historial."""
    conn = sqlite3.connect('historial_bcv.db')
    df = pd.read_sql_query("SELECT fecha, monto, variacion FROM tasas ORDER BY fecha DESC", conn)
    conn.close()
    return df

# --- LÓGICA DE LA APLICACIÓN ---
df_tasas = obtener_datos()

if not df_tasas.empty:
    ultima_fila = df_tasas.iloc[0]
    
    # Encabezado Principal
    st.title("Tasa Oficial BCV")
    
    # Tarjeta de Tasa Actual
    with st.container():
        st.markdown(f"""
        <div class="tasa-box">
            <h1 style='color: #1a73e8; font-size: 3rem;'>{ultima_fila['monto']:.4f} Bs</h1>
            <p style='font-size: 1.2rem; opacity: 0.8;'>{ultima_fila['fecha']}</p>
        </div>
        """, unsafe_allow_html=True)

   # --- LÓGICA DE COMPARTIR ---
# Preparamos el texto que se enviará
texto_compartir = f"📊 Tasa oficial BCV: {ultima_fila['monto']:.4f} Bs (Vigencia: {ultima_fila['fecha']}). Consulta más en: {st.query_params.get('url', 'MonitorBCV')}"
url_whatsapp = f"https://api.whatsapp.com/send?text={texto_compartir}"

# Diseño del Botón Social Innovador
st.markdown("### 📢 Comparte el valor del día")
col1, col2 = st.columns(2)

with col1:
    st.link_button("🟢 Compartir en WhatsApp", url_whatsapp, use_container_width=True)

with col2:
    # Enlace para Telegram
    url_telegram = f"https://t.me/share/url?url={st.query_params.get('url', '')}&text={texto_compartir}"
    st.link_button("🔵 Compartir en Telegram", url_telegram, use_container_width=True)

    # --- SECCIÓN DINÁMICA: CONSULTA POR CALENDARIO ---
    st.divider()
    st.subheader("📅 Consulta Histórica")
    
    # Selector de fecha dinámico (Ideal para móviles)
    fecha_busqueda = st.date_input("Selecciona una fecha para consultar:", 
                                  value=datetime.now(),
                                  min_value=datetime(2026, 2, 1))
    
    fecha_str = fecha_busqueda.strftime('%Y-%m-%d')
    resultado = df_tasas[df_tasas['fecha'] == fecha_str]

    if not resultado.empty:
        res = resultado.iloc[0]
        st.success(f"Tasa para el {fecha_str}: **{res['monto']:.4f} Bs** (Var: {res['variacion']:+.4f})")
    else:
        st.info("No hay registros para la fecha seleccionada (Fines de semana o feriados).")

    # --- GRÁFICO DE EVOLUCIÓN ---
    st.divider()
    st.subheader("📈 Evolución 10 días")
    st.line_chart(df_tasas.head(10).set_index('fecha')['monto'])

# Pie de página con autoría y versión v3.2
st.markdown(f"""
    <div style='text-align: center; color: #6b7280; padding: 20px; font-size: 0.85rem; font-family: sans-serif;'>
        <hr style='border: 0; height: 1px; background-image: linear-gradient(to right, rgba(0,0,0,0), rgba(0,0,0,0.1), rgba(0,0,0,0)); margin-bottom: 20px;'>
        Desarrollado por: <b style='color: #1a73e8;'>adnetwork.ve</b> - {datetime.now().year}<br>
        v3.2 | High-Frequency Sync (5min)
    </div>
""", unsafe_allow_html=True)