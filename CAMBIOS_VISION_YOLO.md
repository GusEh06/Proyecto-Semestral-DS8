# 🔧 Correcciones Sistema de Visión YOLO + Backend + Frontend

## 📋 Resumen de Cambios

Se corrigieron **7 problemas críticos** de inconsistencia entre YOLO, Backend y Frontend:

### ✅ Problemas Resueltos

1. **Campo faltante en BD**: Agregado `personas_actuales` al modelo Mesa
2. **Respuesta incorrecta**: POST `/actualizar-estado-mesas` ahora devuelve `{"success": true}`
3. **Endpoint faltante**: Creado GET `/vision/estado-general`
4. **Datos incorrectos en SSE**: Broadcast ahora incluye `personas_actuales`
5. **Frontend mostraba capacidad**: Ahora muestra personas detectadas en tiempo real
6. **Mesas fantasma**: Sistema elimina automáticamente mesas no detectadas
7. **Métrica inconsistente**: Corrección en lógica de envíos exitosos/fallidos

---

## 🗂️ Archivos Modificados

### Backend
- ✏️ `back-end/app/models/mesa.py` - Agregado campo `personas_actuales`
- ✏️ `back-end/app/routers/vision.py` - 3 cambios:
  - Nuevo endpoint GET `/vision/estado-general`
  - POST `/actualizar-estado-mesas` actualizado (response + lógica)
  - Limpieza automática de mesas fantasma

### Frontend
- ✏️ `front-end/src/lib/api.ts` - Interfaz `Mesa` actualizada
- ✏️ `front-end/src/components/react/admin/MesasGrid.tsx` - UI muestra personas reales

### Base de Datos
- 🆕 `back-end/migrations/001_add_personas_actuales.sql` - Script de migración

---

## 🚀 Instrucciones de Implementación

### Paso 1: Aplicar Migración de Base de Datos

```bash
# Opción A: Usando psql (recomendado)
cd back-end
psql -U postgres -d restaurante_db -f migrations/001_add_personas_actuales.sql

# Opción B: Desde pgAdmin
# 1. Abrir pgAdmin
# 2. Conectar a restaurante_db
# 3. Query Tool → Abrir migrations/001_add_personas_actuales.sql
# 4. Ejecutar (F5)

# Opción C: Desde Python (alternativa)
python -c "
from app.database import engine
from app.models.mesa import Mesa
Mesa.__table__.create(engine, checkfirst=True)
"
```

**⚠️ IMPORTANTE**: Ejecutar la migración **ANTES** de arrancar el backend.

### Paso 2: Reiniciar Backend

```bash
cd back-end

# Si usas uvicorn directamente
uvicorn app.main:app --reload

# Si usas un script de inicio
python main.py
```

### Paso 3: Reiniciar Frontend

```bash
cd front-end

# Si usas Astro (puerto 4321)
npm run dev

# Si usas otro framework
npm start
```

### Paso 4: Verificar Sistema de Visión

**El sistema de visión NO requiere cambios**, pero ahora recibirá respuestas correctas:

**Antes (ERROR):**
```json
{
  "ok": true,  // ← Sistema esperaba "success"
  "resultados": [...]
}
```

**Ahora (CORRECTO):**
```json
{
  "success": true,  // ✅ Correcto
  "resultados": [
    {
      "id_mesa": 1,
      "estado_anterior": "disponible",
      "estado_nuevo": "ocupada",
      "personas_detectadas": 1  // ✅ Siempre incluido
    }
  ]
}
```

---

## 🔍 Verificación de Funcionamiento

### 1. Verificar Base de Datos

```sql
-- Verificar que la columna existe
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'mesas';

-- Debería mostrar:
-- id_mesa, id_tipo_mesa, estado, personas_actuales, updated_at
```

### 2. Verificar Endpoint GET

```bash
# Debe devolver mesas con personas_actuales
curl http://localhost:8000/api/v1/vision/estado-general

# Respuesta esperada:
# [
#   {
#     "id_mesa": 1,
#     "estado": "ocupada",
#     "personas_actuales": 1,  // ← NUEVO
#     "id_tipo_mesa": 1,
#     "tipo_mesa": { ... }
#   }
# ]
```

### 3. Verificar Endpoint POST

```bash
curl -X POST http://localhost:8000/api/v1/vision/actualizar-estado-mesas \
  -H "Content-Type: application/json" \
  -d '{
    "detecciones": [
      {"id_mesa": 1, "personas_detectadas": 2}
    ]
  }'

# Respuesta esperada:
# {
#   "success": true,  // ← CAMBIADO de "ok"
#   "resultados": [...]
# }
```

### 4. Verificar Frontend

1. Abrir navegador en `http://localhost:4321/admin/dashboard`
2. Verificar que muestra:
   - **"2 personas"** (YOLO detectó) ✅
   - **NO** "Mesa para 4 personas" (capacidad) ❌
3. Al hacer hover o abrir modal:
   - **Personas detectadas: 2** (REAL)
   - **Capacidad máxima: 4** (INFO)

### 5. Verificar Limpieza de Mesas Fantasma

**Escenario de prueba:**

1. YOLO detecta Mesa 1 y 2 → Se crean en BD
2. YOLO solo detecta Mesa 1 → Mesa 2 se elimina automáticamente
3. Frontend solo muestra Mesa 1 ✅

**Consola del backend mostrará:**
```
🗑️  Mesa #2 eliminada (ya no detectada por YOLO)
```

---

## 📊 Flujo de Datos Correcto

```
┌─────────────────────────────────────────────────────────────────┐
│                    SISTEMA DE VISIÓN (YOLO)                     │
│  Detecta: Mesa 1 → 1 persona                                    │
└────────────────────────────┬────────────────────────────────────┘
                             │ POST /actualizar-estado-mesas
                             │ {detecciones: [{id_mesa: 1, personas_detectadas: 1}]}
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                            │
│  1. Guarda: personas_actuales = 1                               │
│  2. Calcula: estado = "ocupada" (porque personas > 0)           │
│  3. Responde: {success: true, resultados: [...]}  ✅            │
│  4. Broadcast SSE: {personas_actuales: 1}                       │
└────────────────────────────┬────────────────────────────────────┘
                             │ Server-Sent Events (SSE)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                             │
│  Recibe: {id_mesa: 1, personas_actuales: 1}                     │
│  Muestra: "1 persona"  ✅                                        │
│  (NO muestra: cantidad_sillas)                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🐛 Solución a Problemas Conocidos

### Error: "✗ Error inesperado: 'success'"
**Causa**: Sistema de visión esperaba `success` pero recibía `ok`
**Solución**: ✅ Corregido en línea 129 de `vision.py`

### Frontend muestra "2 personas" cuando YOLO detectó 1
**Causa**: Mostraba `cantidad_sillas` en lugar de `personas_actuales`
**Solución**: ✅ Corregido en línea 231 de `MesasGrid.tsx`

### Mesas viejas siguen apareciendo después de cambiar de habitación
**Causa**: No había limpieza de mesas no detectadas
**Solución**: ✅ Implementado en líneas 90-106 de `vision.py`

### Endpoint /vision/estado-general devuelve 404
**Causa**: Endpoint no existía
**Solución**: ✅ Creado en líneas 23-45 de `vision.py`

### Campo personas_actuales no existe en BD
**Causa**: Modelo no tenía el campo
**Solución**: ✅ Ejecutar migración `001_add_personas_actuales.sql`

---

## 📝 Notas Importantes

1. **NO eliminar tipo_mesa.cantidad_sillas**: Se mantiene como información de capacidad
2. **Respetar reservas**: Las mesas con reservas activas NO se eliminan automáticamente
3. **Estado "reservada"**: Prevalece sobre personas detectadas si hay reserva confirmada
4. **SSE en tiempo real**: El frontend se actualiza automáticamente sin necesidad de refrescar

---

## 🎯 Resultado Final

| Aspecto | Antes ❌ | Ahora ✅ |
|---------|---------|---------|
| **YOLO detecta** | 1 persona | 1 persona |
| **BD guarda** | ❌ (no había campo) | 1 en `personas_actuales` |
| **Backend responde** | `{"ok": true}` | `{"success": true}` |
| **Frontend muestra** | "2 personas" (capacidad) | "1 persona" (real) |
| **Mesas fantasma** | ❌ Se acumulan | ✅ Se eliminan automáticamente |
| **Endpoint estado-general** | ❌ 404 Not Found | ✅ Devuelve datos correctos |

---

## 🆘 Soporte

Si encuentras problemas después de aplicar los cambios:

1. **Verificar logs del backend**: Buscar errores al arrancar
2. **Verificar migración**: Ejecutar query SQL de verificación
3. **Limpiar caché del navegador**: Ctrl + Shift + R
4. **Revisar consola del navegador**: F12 → Console
5. **Verificar conexión SSE**: Debe mostrar "✅ Conectado al servidor en tiempo real"

---

**Fecha de cambios**: 2025-12-08
**Versión**: 1.0.0
**Estado**: ✅ Listo para producción
