import sqlite3

def crear_base_de_datos():
    try:
        # Conecta (o crea) el archivo en la carpeta actual
        conn = sqlite3.connect('historial_bcv.db')
        cursor = conn.cursor()

        # Creamos la tabla
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT UNIQUE,
                monto REAL,
                variacion REAL
            )
        ''')
        
        conn.commit()
        conn.close()
        print("¡Éxito! El archivo 'historial_bcv.db' ha sido creado.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    crear_base_de_datos()