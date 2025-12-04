# 🚀 CÓMO EJECUTAR EL SCRIPT SQL

## ✅ Frontend y Backend SIGUEN CORRIENDO

**No necesitas detener nada.** El script se ejecuta directamente en PostgreSQL.

---

## 📝 OPCIÓN 1: Desde la Terminal (Recomendado)

### **Abre una NUEVA terminal** (no la del frontend ni backend)

```bash
# Navega a la carpeta del proyecto
cd C:\Users\Gus\Documents\U\Desarrollo_de_Software_VIII\proyecto_semestral

# Ejecuta el script
psql -U postgres -d restaurante_db -f poblar_base_datos.sql
```

**Eso es todo.** Verás la salida con el resumen.

---

## 📝 OPCIÓN 2: Copiar y Pegar en pgAdmin o DBeaver

1. Abre **pgAdmin** o **DBeaver**
2. Conéctate a la base de datos `restaurante_db`
3. Abre un nuevo Query Tool / SQL Editor
4. Abre el archivo `poblar_base_datos.sql`
5. Selecciona todo (Ctrl+A)
6. Ejecuta (F5 o botón Run)

---

## 📝 OPCIÓN 3: Desde psql interactivo

```bash
# Conectarse a la base de datos
psql -U postgres -d restaurante_db

# Dentro de psql, ejecutar:
\i poblar_base_datos.sql

# O la ruta completa:
\i C:/Users/Gus/Documents/U/Desarrollo_de_Software_VIII/proyecto_semestral/poblar_base_datos.sql
```

---

## 📊 QUÉ HACE EL SCRIPT

El script `poblar_base_datos.sql` inserta:

### ✅ **5 Tipos de Mesa**
- Mesa pequeña para 2 personas
- Mesa estándar para 4 personas
- Mesa familiar para 6 personas
- Mesa grande para 8 personas
- Mesa VIP para 10 personas

### ✅ **20 Mesas Distribuidas**
- 5 mesas para 2 personas
- 8 mesas para 4 personas
- 4 mesas para 6 personas
- 2 mesas para 8 personas
- 1 mesa VIP para 10 personas

### ✅ **14 Reservaciones de Ejemplo**
- 4 confirmadas para HOY
- 2 pendientes para HOY
- 3 para MAÑANA
- 2 para PASADO MAÑANA
- 2 COMPLETADAS (ayer)
- 1 CANCELADA

### ⚙️ **Inteligente:**
- ✅ Verifica si ya existen datos (no duplica)
- ✅ Muestra mensajes de lo que hace
- ✅ Actualiza automáticamente el estado de mesas reservadas
- ✅ Muestra un resumen al final

---

## 🎯 SALIDA ESPERADA

Verás algo como esto:

```
NOTICE:  ✓ Insertados 5 tipos de mesa
NOTICE:  ✓ Insertadas 20 mesas
NOTICE:  ✓ Insertadas 14 reservaciones de ejemplo

========================================
         RESUMEN DE LA BASE DE DATOS
========================================

Tipos de mesa: 5
Total de mesas: 20
  - Disponibles: 14
  - Ocupadas: 0
  - Reservadas: 6

Total de reservaciones: 14
Usuarios administradores: 0

⚠ IMPORTANTE: No hay usuarios admin
   Ejecuta: cd back-end && python create_admin.py

========================================
✓ Base de datos poblada correctamente
========================================

       Tipo de Mesa        | Capacidad | Cantidad
---------------------------+-----------+----------
 Mesa pequeña para 2...    |         2 |        5
 Mesa estándar para 4...   |         4 |        8
 Mesa familiar para 6...   |         6 |        4
 Mesa grande para 8...     |         8 |        2
 Mesa VIP para 10...       |        10 |        1

   Estado    | Cantidad
-------------+----------
 disponible  |       14
 reservada   |        6
```

---

## ⚠️ CREAR USUARIO ADMIN

**El script NO crea usuarios admin** (porque las contraseñas deben hashearse con bcrypt).

Después de ejecutar el script SQL, ejecuta:

```bash
cd back-end
python create_admin.py
```

Esto crea:
```
Email: admin@example.com
Password: admin123
Rol: superadmin
```

---

## 🔄 VERIFICAR EN EL DASHBOARD

Una vez ejecutado el script:

1. **Ve al dashboard:** http://localhost:4321/admin/login
2. **Login:** admin@example.com / admin123
3. **Deberías ver:**
   - 📊 Dashboard con 14 reservaciones
   - 🍽️ 20 mesas en la página de Mesas
   - 📅 14 reservaciones en la tabla

---

## 🧹 SI QUIERES EMPEZAR DESDE CERO

Si ya ejecutaste el script y quieres empezar de nuevo:

1. Edita `poblar_base_datos.sql`
2. **Descomenta estas líneas** (quitar los `--`):

```sql
-- TRUNCATE TABLE reservaciones CASCADE;
-- TRUNCATE TABLE mesas CASCADE;
-- TRUNCATE TABLE tipo_mesa CASCADE;
```

3. Vuelve a ejecutar el script

---

## ❓ SI HAY ERRORES

### Error: "database does not exist"
```bash
createdb restaurante_db
```

### Error: "relation does not exist"
```bash
# Primero ejecuta el schema:
psql -U postgres -d restaurante_db -f reservationsdb.sql

# Luego el script de datos:
psql -U postgres -d restaurante_db -f poblar_base_datos.sql
```

### Error: "permission denied"
```bash
# Usa el usuario correcto de PostgreSQL
psql -U tu_usuario -d restaurante_db -f poblar_base_datos.sql
```

---

## ✅ CHECKLIST RÁPIDO

- [ ] Frontend corriendo en http://localhost:4321 ✅
- [ ] Backend corriendo en http://localhost:8000 ✅
- [ ] Ejecutar: `psql -U postgres -d restaurante_db -f poblar_base_datos.sql`
- [ ] Ejecutar: `cd back-end && python create_admin.py`
- [ ] Refrescar el dashboard: http://localhost:4321/admin/dashboard
- [ ] Ver estadísticas y datos

---

## 🎉 ¡LISTO!

Tu base de datos ahora tiene:
- ✅ 5 tipos de mesa
- ✅ 20 mesas listas
- ✅ 14 reservaciones de ejemplo
- ✅ 1 usuario admin (después de create_admin.py)

**Todo sin detener el frontend ni el backend.** 🚀
