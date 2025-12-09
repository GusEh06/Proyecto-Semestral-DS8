# 🗄️ GUÍA DE CONFIGURACIÓN DE LA BASE DE DATOS

## 📋 ÍNDICE

1. [Requisitos Previos](#requisitos-previos)
2. [Configuración Paso a Paso](#configuración-paso-a-paso)
3. [Datos Necesarios](#datos-necesarios)
4. [Verificación](#verificación)
5. [Solución de Problemas](#solución-de-problemas)

---

## ✅ REQUISITOS PREVIOS

Antes de configurar la base de datos, asegúrate de tener:

- ✅ PostgreSQL 12+ instalado y corriendo
- ✅ Acceso a un usuario de PostgreSQL con permisos de creación de BD
- ✅ Backend del proyecto con las variables de entorno configuradas

---

## 🚀 CONFIGURACIÓN PASO A PASO

### **PASO 1: Crear la Base de Datos**

Abre PostgreSQL y crea la base de datos:

```sql
CREATE DATABASE restaurante_db;
```

O desde la línea de comandos:

```bash
createdb restaurante_db
```

---

### **PASO 2: Ejecutar el Schema Principal**

Este archivo crea todas las tablas necesarias:

```bash
psql -U postgres -d restaurante_db -f reservationsdb.sql
```

**Tablas que se crean:**
- ✅ `tipo_mesa` - Tipos de mesas (2, 4, 6, 8, 10 personas)
- ✅ `mesas` - Mesas físicas del restaurante
- ✅ `reservaciones` - Reservaciones de clientes
- ✅ `usuarios_admin` - Usuarios administrativos

---

### **PASO 3: Insertar Datos de Ejemplo**

Ejecuta el script de datos iniciales:

```bash
psql -U postgres -d restaurante_db -f seed_database.sql
```

**Datos que se insertan:**
- ✅ 5 tipos de mesa (2, 4, 6, 8, 10 personas)
- ✅ 20 mesas distribuidas por capacidad:
  - 5 mesas para 2 personas
  - 8 mesas para 4 personas
  - 4 mesas para 6 personas
  - 2 mesas para 8 personas
  - 1 mesa VIP para 10 personas
- ✅ 11 reservaciones de ejemplo (hoy, mañana, pasado mañana)

---

### **PASO 4: Crear Usuario Administrador**

Ejecuta el script de Python para crear el usuario admin:

```bash
cd back-end
python create_admin.py
```

**Credenciales creadas:**
```
Email: admin@example.com
Password: admin123
Rol: superadmin
```

---

### **PASO 5: Configurar Variables de Entorno**

Edita el archivo `.env` en el backend:

```bash
cd back-end
cp .env.example .env
```

Configura la conexión a la base de datos en `.env`:

```env
DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/restaurante_db

# O en formato separado:
DB_HOST=localhost
DB_PORT=5432
DB_NAME=restaurante_db
DB_USER=postgres
DB_PASSWORD=tu_password

# JWT Secret
SECRET_KEY=tu_clave_secreta_muy_segura_cambiala_en_produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 📊 DATOS NECESARIOS (Resumen)

### **OBLIGATORIOS para que funcione el sistema:**

#### 1️⃣ **TIPOS DE MESA**
```sql
tipo_mesa
├── id_tipo_mesa (PK)
├── descripcion (ej: "Mesa para 4 personas")
└── cantidad_sillas (ej: 4)
```

**Mínimo:** 2-3 tipos diferentes
**Recomendado:** 4-5 tipos (2, 4, 6, 8, 10 personas)

---

#### 2️⃣ **MESAS**
```sql
mesas
├── id_mesa (PK)
├── id_tipo_mesa (FK → tipo_mesa)
├── estado (disponible/ocupada/reservada)
└── updated_at
```

**Mínimo:** 5-10 mesas
**Recomendado:** 15-30 mesas distribuidas por tipo

---

#### 3️⃣ **USUARIO ADMINISTRADOR**
```sql
usuarios_admin
├── id_usuario (PK)
├── nombre
├── email (UNIQUE)
├── password_hash
├── rol (admin/superadmin/staff)
└── is_active
```

**Mínimo:** 1 usuario superadmin
**Recomendado:** 2-3 usuarios con diferentes roles

---

#### 4️⃣ **RESERVACIONES** (Opcional - se generan automáticamente)
```sql
reservaciones
├── id_reserva (PK)
├── nombre
├── apellido
├── correo
├── telefono
├── cantidad_personas
├── fecha
├── hora
├── id_mesa (FK → mesas, nullable)
├── estado (pendiente/confirmada/cancelada/completada)
└── created_at, updated_at
```

**Opcional:** Puedes empezar sin reservaciones o usar las de ejemplo del script.

---

## 🔍 VERIFICACIÓN

### **Verificar que TODO está correcto:**

```sql
-- Conectarse a la base de datos
psql -U postgres -d restaurante_db

-- 1. Verificar tipos de mesa
SELECT * FROM tipo_mesa;
-- Deberías ver: 5 tipos (2, 4, 6, 8, 10 personas)

-- 2. Verificar mesas
SELECT COUNT(*) as total_mesas FROM mesas;
-- Deberías ver: 20 mesas (si usaste seed_database.sql)

-- 3. Verificar distribución de mesas
SELECT
    t.descripcion,
    COUNT(m.id_mesa) as cantidad
FROM tipo_mesa t
LEFT JOIN mesas m ON t.id_tipo_mesa = m.id_tipo_mesa
GROUP BY t.id_tipo_mesa, t.descripcion
ORDER BY t.cantidad_sillas;

-- 4. Verificar estados de mesas
SELECT estado, COUNT(*) as cantidad
FROM mesas
GROUP BY estado;

-- 5. Verificar reservaciones
SELECT COUNT(*) as total_reservaciones FROM reservaciones;
-- Deberías ver: 11 reservaciones (si usaste seed_database.sql)

-- 6. Verificar usuarios admin
SELECT email, rol, is_active FROM usuarios_admin;
-- Deberías ver: admin@example.com

-- 7. Verificar reservaciones por fecha
SELECT fecha, COUNT(*) as cantidad
FROM reservaciones
GROUP BY fecha
ORDER BY fecha;
```

**Resultado esperado:**

```
✓ 5 tipos de mesa
✓ 20 mesas (5+8+4+2+1)
✓ 20 mesas disponibles
✓ 11 reservaciones de ejemplo
✓ 1 usuario administrador (superadmin)
```

---

## 🎯 DATOS MÍNIMOS VS RECOMENDADOS

| Dato | Mínimo | Recomendado | Con seed_database.sql |
|------|--------|-------------|----------------------|
| **Tipos de mesa** | 2 | 4-5 | ✅ 5 |
| **Mesas** | 5 | 15-30 | ✅ 20 |
| **Reservaciones** | 0 | 5-10 | ✅ 11 |
| **Usuarios admin** | 1 | 2-3 | ✅ 1 (crear con script) |

---

## 🔧 SOLUCIÓN DE PROBLEMAS

### **Problema: "Database does not exist"**
```bash
# Crear la base de datos
createdb restaurante_db
```

### **Problema: "Permission denied"**
```bash
# Dar permisos al usuario
psql -U postgres
GRANT ALL PRIVILEGES ON DATABASE restaurante_db TO tu_usuario;
```

### **Problema: "Relation already exists"**
```sql
-- Si necesitas reiniciar las tablas
DROP TABLE IF EXISTS reservaciones CASCADE;
DROP TABLE IF EXISTS mesas CASCADE;
DROP TABLE IF EXISTS tipo_mesa CASCADE;
DROP TABLE IF EXISTS usuarios_admin CASCADE;

-- Luego volver a ejecutar reservationsdb.sql
```

### **Problema: "Backend no conecta a la BD"**

1. Verifica que PostgreSQL esté corriendo:
```bash
# Windows
pg_ctl status

# Linux/Mac
sudo systemctl status postgresql
```

2. Verifica la configuración en `back-end/.env`:
```env
DATABASE_URL=postgresql://usuario:password@localhost:5432/restaurante_db
```

3. Prueba la conexión manualmente:
```bash
psql -U postgres -d restaurante_db -c "SELECT 1;"
```

### **Problema: "No puedo hacer login en el dashboard"**

1. Verifica que el usuario admin existe:
```sql
SELECT * FROM usuarios_admin WHERE email = 'admin@example.com';
```

2. Si no existe, créalo:
```bash
cd back-end
python create_admin.py
```

3. Verifica que el backend esté corriendo:
```bash
curl http://localhost:8000/docs
```

---

##  COMANDOS RÁPIDOS DE REFERENCIA

```bash
# 1. Crear BD
createdb restaurante_db

# 2. Ejecutar schema
psql -U postgres -d restaurante_db -f reservationsdb.sql

# 3. Insertar datos de ejemplo
psql -U postgres -d restaurante_db -f seed_database.sql

# 4. Crear usuario admin
cd back-end && python create_admin.py

# 5. Verificar datos
psql -U postgres -d restaurante_db -c "SELECT COUNT(*) FROM mesas;"

# 6. Iniciar backend
cd back-end && uvicorn app.main:app --reload

# 7. Iniciar frontend
cd front-end && npm run dev
```

---

## 🎉 CONFIGURACIÓN COMPLETA

Si seguiste todos los pasos, ahora tienes:

✅ Base de datos PostgreSQL creada
✅ Tablas con schema correcto
✅ 5 tipos de mesa
✅ 20 mesas listas para usar
✅ 11 reservaciones de ejemplo
✅ 1 usuario administrador (superadmin)
✅ Backend configurado y conectado
✅ Frontend corriendo

**¡Tu sistema está listo para funcionar! 🚀**

---

## 🔗 PRÓXIMOS PASOS

1. **Acceder al sistema:**
   - Frontend público: http://localhost:4321
   - Dashboard admin: http://localhost:4321/admin/login
   - API Docs: http://localhost:8000/docs

2. **Hacer una reserva de prueba:**
   - Ir a http://localhost:4321/reservar
   - Llenar el formulario
   - Verificar en el dashboard admin

3. **Explorar el dashboard:**
   - Login: admin@example.com / admin123
   - Ver estadísticas
   - Gestionar mesas
   - Gestionar reservaciones

---

## 📧 CREDENCIALES IMPORTANTES

### **Base de Datos:**
```
Host: localhost
Port: 5432
Database: restaurante_db
User: postgres
Password: [tu password de postgres]
```

### **Dashboard Admin:**
```
URL: http://localhost:4321/admin/login
Email: admin@example.com
Password: admin123
```

### **API Backend:**
```
URL: http://localhost:8000
Docs: http://localhost:8000/docs
```

---

## ⚠️ IMPORTANTE PARA PRODUCCIÓN

**NO usar en producción:**
- ❌ Password "admin123"
- ❌ Database en localhost sin SSL
- ❌ SECRET_KEY débil

**Cambiar en producción:**
- ✅ Password fuerte para admin
- ✅ Database en servidor seguro con SSL
- ✅ SECRET_KEY generado con: `openssl rand -hex 32`
- ✅ Variables de entorno seguras
- ✅ HTTPS en frontend y backend

---

**¡Listo! Tu base de datos está completamente configurada.** 🎉
