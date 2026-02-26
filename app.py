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

    # Botón Social (Placeholder interactivo)
    st.button("🔗 Compartir Tasa Actual")

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

# Pie de página con autoría
st.markdown(f"""
    <div class="footer">
        Desarrollado por: <b>adnetwork.ve</b> - {datetime.now().year} | Versión 3.0 Web & Mobile
    </div>
    """, unsafe_allow_html=True)