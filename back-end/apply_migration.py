"""
Script para aplicar migraciones SQL
"""
import psycopg2
from app.config import settings

def apply_migration(migration_file: str):
    """Aplica un archivo de migración SQL"""

    # Extraer parámetros de conexión de DATABASE_URL
    # Format: postgresql://user:password@host:port/database
    db_url = settings.DATABASE_URL

    print(f"[INFO] Aplicando migracion: {migration_file}")
    print(f"[INFO] Conectando a base de datos...")

    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(settings.DATABASE_URL)
        conn.autocommit = True

        print("[OK] Conectado exitosamente")

        # Leer archivo SQL
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        print(f"[INFO] Ejecutando SQL...")

        # Ejecutar migración
        cursor = conn.cursor()
        cursor.execute(sql_content)

        # Obtener mensajes de NOTICE
        for notice in conn.notices:
            print(f"   {notice.strip()}")

        # Mostrar resultados si hay
        if cursor.description:
            rows = cursor.fetchall()
            if rows:
                print("\n[INFO] Estructura de la tabla 'mesas':")
                print("-" * 60)
                for row in rows:
                    print(f"   {row[0]:<20} {row[1]:<20} {row[2]}")
                print("-" * 60)

        cursor.close()
        conn.close()

        print("\n[OK] Migracion aplicada exitosamente")

    except psycopg2.Error as e:
        print(f"\n[ERROR] Error aplicando migracion: {e}")
        return False
    except FileNotFoundError:
        print(f"\n[ERROR] Archivo de migracion no encontrado: {migration_file}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
        return False

    return True

if __name__ == "__main__":
    migration_file = "migrations/001_add_personas_actuales.sql"
    apply_migration(migration_file)
