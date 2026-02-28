import os
import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import urllib3
import random #Nuevo para Anti-cache


# Desactiva advertencias de certificados SSL (común en la web del BCV)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuración mediante Variables de Entorno (GitHub Secrets)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CANAL_TELEGRAM = os.getenv("TELEGRAM_CHAT_ID")

def obtener_datos_bcv():
    """Extrae la tasa y la fecha de vigencia directamente desde la web del BCV."""
    #Añade un parametro aleatoreo para forzar la actualizacion del servidor
    url_bcv = f"https://www.bcv.org.ve/?t={random.randint(1000, 9999)}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }

    try:
        # Petición a la web del BCV con timeout de 20 segundos
        response = requests.get(url, verify=False, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. EXTRAER LA FECHA DE VALOR (Vigencia)
        # Usamos el atributo 'content' que contiene la fecha en formato ISO (YYYY-MM-DD)
        span_fecha = soup.find("span", {"class": "date-display-single"})
        if span_fecha and span_fecha.has_attr('content'):
            fecha_valor = span_fecha['content'].split('T')[0]
        else:
            # Fallback en caso de que el atributo no esté
            fecha_valor = None
        
        # 2. EXTRAER EL MONTO DEL DÓLAR
        # Buscamos el contenedor específico del dólar y su valor en negrita
        tasa_raw = soup.find("div", {"id": "dolar"}).find("strong").text.strip()
        tasa_limpia = float(tasa_raw.replace(',', '.'))

        return fecha_valor, tasa_limpia
    except Exception as e:
        print(f"Error realizando el scraping: {e}")
        return None, None

def procesar_tasa():
    """Valida la fecha contra la DB, guarda si es nueva y notifica a Telegram."""
    fecha_web, monto_actual = obtener_datos_bcv()
    
    if not fecha_web or not monto_actual:
        print("No se pudieron obtener los datos de la web.")
        return

    # Conexión a la base de datos local
    conn = sqlite3.connect('historial_bcv.db')
    cursor = conn.cursor()

    # VALIDACIÓN: ¿Ya existe esta fecha de vigencia en nuestra base de datos?
    cursor.execute("SELECT monto FROM tasas WHERE fecha = ?", (fecha_web,))
    resultado = cursor.fetchone()

    if resultado:
        # Si la fecha ya existe, el script termina aquí sin notificar
        print(f"La tasa para la fecha {fecha_web} ya está registrada ({resultado[0]}).")
        conn.close()
        return

    # SI ES NUEVA: Buscamos la última tasa registrada para calcular la variación
    cursor.execute("SELECT monto FROM tasas ORDER BY id DESC LIMIT 1")
    ultima_tasa_db = cursor.fetchone()
    tasa_anterior = ultima_tasa_db[0] if ultima_tasa_db else monto_actual
    variacion = monto_actual - tasa_anterior

    # GUARDAR EN LA BASE DE DATOS
    cursor.execute("INSERT INTO tasas (fecha, monto, variacion) VALUES (?, ?, ?)", 
                   (fecha_web, monto_actual, variacion))
    conn.commit()
    conn.close()

    # ENVIAR NOTIFICACIÓN A TELEGRAM
    enviar_telegram(fecha_web, monto_actual, variacion)
    print(f"Éxito: Nueva tasa guardada y notificada para el {fecha_web}.")

def enviar_telegram(fecha, tasa, var):
    """Construye y envía el mensaje formateado al canal de Telegram."""
    # Selección de emoji según la variación
    emoji_var = "🟢" if var > 0 else "🔴" if var < 0 else "⚪"
    
    # Formateo del mensaje con Markdown
    mensaje = (
        f"📢 *ACTUALIZACIÓN BCV*\n\n"
        f"📅 *Vigencia:* {fecha}\n"
        f"💵 *Tasa:* {tasa:.4f} Bs\n"
        f"{emoji_var} *Variación:* {var:+.4f}\n\n"
        f"📍 _Tasa oficial del Banco Central de Venezuela_"
    )
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CANAL_TELEGRAM,
        "text": mensaje,
        "parse_mode": "Markdown"
    }
    
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Error enviando mensaje a Telegram: {e}")

if __name__ == "__main__":
    procesar_tasa()