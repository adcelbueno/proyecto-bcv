import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime

def obtener_tasa_bcv():
    url = "https://www.bcv.org.ve/"
    try:
        # 1. Descargar el contenido de la página
        # verify=False se usa a veces si el BCV tiene problemas de certificados SSL
        response = requests.get(url, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 2. Buscar el contenedor del Dólar (ID específico del BCV)
        # El BCV usa el ID 'dolar' para su tasa oficial
        tasa_elemento = soup.find('div', id='dolar').find('strong')
        tasa_texto = tasa_elemento.text.strip().replace(',', '.')
        tasa_valor = float(tasa_texto)

        print(f"Tasa capturada hoy: {tasa_valor}")
        return tasa_valor
    except Exception as e:
        print(f"Error al obtener la tasa: {e}")
        return None

def guardar_en_bd(tasa_hoy):
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')
    conn = sqlite3.connect('historial_bcv.db')
    cursor = conn.cursor()

    # 1. Buscar la última tasa para calcular la variación
    cursor.execute("SELECT monto FROM tasas ORDER BY id DESC LIMIT 1")
    ultimo_registro = cursor.fetchone()
    
    tasa_ayer = ultimo_registro[0] if ultimo_registro else tasa_hoy
    variacion = tasa_hoy - tasa_ayer

    # 2. Guardar el nuevo registro
    try:
        cursor.execute("INSERT INTO tasas (fecha, monto, variacion) VALUES (?, ?, ?)", 
                       (fecha_hoy, tasa_hoy, variacion))
        conn.commit()
        print(f"Datos guardados. Variación: {variacion:.4f}")
    except sqlite3.IntegrityError:
        print("Aviso: Ya existe un registro para la fecha de hoy.")
    
    conn.close()

if __name__ == "__main__":
    tasa = obtener_tasa_bcv()
    if tasa:
        guardar_en_bd(tasa)