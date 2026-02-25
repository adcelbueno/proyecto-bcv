import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime

# --- CONFIGURACIÓN DEL CANAL ---
TELEGRAM_TOKEN = "8351119219:AAG2-4S4sqhhlQFucVxhPrMyptWvYcoyFic"
# Ahora usamos el nombre del canal con el símbolo @
CANAL_TELEGRAM = "@info_tasas_bcv" 

def enviar_notificacion_canal(mensaje):
    """Envía la tasa a todos los suscriptores del canal simultáneamente"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CANAL_TELEGRAM, 
        "text": mensaje, 
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Notificación enviada al canal con éxito.")
        else:
            print(f"Error de Telegram: {response.text}")
    except Exception as e:
        print(f"Fallo de conexión: {e}")

def obtener_tasa_bcv():
    # ... (Mantenemos tu lógica de scraping que ya funciona) ...
    url = "https://www.bcv.org.ve/"
    try:
        response = requests.get(url, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')
        tasa_elemento = soup.find('div', id='dolar').find('strong')
        tasa_texto = tasa_elemento.text.strip().replace(',', '.')
        return float(tasa_texto)
    except Exception as e:
        print(f"Error capturando tasa: {e}")
        return None

def guardar_y_notificar(tasa_hoy):
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')
    conn = sqlite3.connect('historial_bcv.db')
    cursor = conn.cursor()

    # Buscamos la última tasa para calcular variación
    cursor.execute("SELECT monto FROM tasas ORDER BY id DESC LIMIT 1")
    ultimo = cursor.fetchone()
    tasa_ayer = ultimo[0] if ultimo else 0
    variacion = tasa_hoy - tasa_ayer

    try:
        # Intentamos guardar (la fecha UNIQUE evitará duplicados)
        cursor.execute("INSERT INTO tasas (fecha, monto, variacion) VALUES (?, ?, ?)", 
                       (fecha_hoy, tasa_hoy, variacion))
        conn.commit()
        
        # Lógica de notificación: Enviamos si hay cambio o si es el primer registro
        if variacion != 0 or not ultimo:
            icono = "🟢" if variacion >= 0 else "🔴"
            mensaje = (
                f"📢 *ACTUALIZACIÓN BCV*\n\n"
                f"📅 *Fecha:* {fecha_hoy}\n"
                f"💵 *Tasa:* {tasa_hoy:.4f} Bs\n"
                f"{icono} *Variación:* {variacion:+.4f}\n\n"
                f"📍 _Tasa oficial suministrada por el BCV_"
            )
            enviar_notificacion_canal(mensaje)
            
    except sqlite3.IntegrityError:
        print("La tasa de hoy ya estaba registrada. No se envía duplicado.")
    
    conn.close()

if __name__ == "__main__":
    tasa = obtener_tasa_bcv()
    if tasa:
        guardar_y_notificar(tasa)