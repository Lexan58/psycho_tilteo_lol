from database import connect_db

def add_match():
    champion = input("Campeón: ")
    role = input("Rol: ")
    kda = input("KDA (ej: 3/7/4): ")
    result = input("Resultado (W/L): ")
    while True:
        try:
            tilt = int(input("Nivel de tilt (0–5): "))
            if 0 <= tilt <= 5:
                break
            print("❌ El tilt debe estar entre 0 y 5.")
        except ValueError:
            print("❌ Ingresa un número válido.")

    note = input("Nota opcional: ")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO matches (date, champion, role, kda, result, tilt_level, note)
        VALUES (datetime('now'), ?, ?, ?, ?, ?, ?)
    """, (champion, role, kda, result, tilt, note))

    conn.commit()
    conn.close()
    print("✔ Partida registrada.")
