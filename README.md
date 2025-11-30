# Sistema de Reservaciones de Restaurante con Visión Artificial

Sistema web moderno de reservaciones para restaurantes que integra tecnología de visión artificial (YOLOv8) para detectar automáticamente la ocupación de mesas. Permite a los clientes realizar reservaciones en línea mientras proporciona a los administradores un panel de gestión completo.

## Tabla de Contenidos

- [Descripción General](#descripción-general)
- [Características Principales](#características-principales)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Stack Tecnológico](#stack-tecnológico)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Requisitos Previos](#requisitos-previos)
- [Instalación y Configuración](#instalación-y-configuración)
- [Uso](#uso)
- [API Endpoints](#api-endpoints)
- [Base de Datos](#base-de-datos)
- [Módulo de Visión Artificial](#módulo-de-visión-artificial)
- [Despliegue](#despliegue)
- [Contribución](#contribución)

## Descripción General

Este proyecto es un sistema completo de gestión de reservaciones para restaurantes desarrollado como parte del curso de Desarrollo de Software VIII. Combina tecnologías web modernas con inteligencia artificial para ofrecer:

- **Para Clientes**: Interfaz web intuitiva para hacer reservaciones en línea
- **Para Administradores**: Panel de control para gestionar reservaciones, mesas y usuarios
- **Automatización con IA**: Detección automática del estado de las mesas usando cámaras y YOLOv8

## Características Principales

### 🎯 Sistema de Reservaciones para Clientes

- ✅ Formulario de reservación en línea con validación en tiempo real
- ✅ Verificación de disponibilidad de mesas
- ✅ Asignación automática de mesas según capacidad
- ✅ Confirmación y cancelación de reservaciones
- ✅ Gestión de franjas horarias (8:00 AM - 8:30 PM en intervalos de 30 min)

### 🔐 Panel de Administración

- ✅ Autenticación segura basada en JWT
- ✅ CRUD completo de reservaciones
- ✅ Gestión de mesas y tipos de mesas
- ✅ Estadísticas en tiempo real:
  - Total de reservaciones (hoy/total/pendientes)
  - Estado de ocupación de mesas
  - Reservaciones por estado
- ✅ Gestión de usuarios administrativos (solo superadmin)

### 🤖 Integración de Visión Artificial

- ✅ Detección de objetos basada en YOLOv8
- ✅ Modelo personalizado entrenado para detectar mesas
- ✅ Detección de personas usando el dataset COCO
- ✅ Soporte para cámaras IP
- ✅ Actualización automática del estado de mesas:
  - Personas detectadas → "ocupada"
  - Sin personas + sin reservación → "disponible"
  - Sin personas + reservación activa → "reservada"

### 🎨 Interfaz Web Moderna

- ✅ Diseño responsivo (mobile-first)
- ✅ Soporte para tema claro/oscuro
- ✅ Accesible (compatible con WCAG AA)
- ✅ Optimizado para SEO
- ✅ Carga rápida con Astro

### 🔒 Características de Seguridad

- ✅ Hash de contraseñas con bcrypt
- ✅ Autenticación con tokens JWT (expiración en 30 min)
- ✅ Control de acceso basado en roles (admin, superadmin, staff)
- ✅ Configuración CORS
- ✅ Protección contra inyección SQL mediante ORM
- ✅ Validación de entrada con Pydantic

## Arquitectura del Sistema

El proyecto sigue una **arquitectura de tres capas** con clara separación de responsabilidades:

```
┌─────────────────────────────────────────────────┐
│           Frontend (Astro + React)              │
│     Interfaz web responsiva para usuarios      │
└─────────────────┬───────────────────────────────┘
                  │ HTTP/REST API
┌─────────────────▼───────────────────────────────┐
│         Backend (FastAPI + Python)              │
│   API RESTful con lógica de negocio            │
└─────┬───────────────────────────────────────┬───┘
      │                                       │
      │ SQLAlchemy ORM                       │ HTTP POST
      │                                       │
┌─────▼──────────────────┐    ┌──────────────▼────┐
│  PostgreSQL Database   │    │  Módulo de Visión │
│  Almacenamiento datos  │    │  Artificial (AI)  │
└────────────────────────┘    └───────────────────┘
```

**Componentes:**
1. **Frontend**: Interfaz de usuario construida con Astro y React
2. **Backend**: API RESTful desarrollada con FastAPI
3. **Base de Datos**: PostgreSQL para persistencia de datos
4. **Módulo de IA**: Sistema de visión por computadora con YOLOv8

## Stack Tecnológico

### Backend

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Python** | 3.13+ | Lenguaje de programación |
| **FastAPI** | 0.115.6+ | Framework web moderno |
| **Uvicorn** | 0.34.0+ | Servidor ASGI |
| **SQLAlchemy** | 2.0.0+ | ORM para base de datos |
| **PostgreSQL** | 18.0 | Base de datos relacional |
| **Psycopg2** | 2.9.0+ | Adaptador PostgreSQL |
| **Pydantic** | 2.10.4+ | Validación de datos |
| **Python-Jose** | 3.3.0+ | Manejo de JWT |
| **Passlib** | 1.7.4+ | Hash de contraseñas (bcrypt) |
| **Ultralytics** | 8.3.55+ | Framework YOLOv8 |
| **OpenCV** | 4.10.0+ | Visión por computadora |

### Frontend

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Astro** | 5.16.0 | Framework de sitios estáticos |
| **React** | 19.2.0 | Biblioteca UI |
| **TypeScript** | - | Tipado estático |
| **Tailwind CSS** | 4.1.17 | Framework CSS |
| **Shadcn UI** | - | Biblioteca de componentes |
| **React Hook Form** | 7.66.1 | Gestión de formularios |
| **Zod** | 3.25.76 | Validación de esquemas |
| **Lucide React** | 0.554.0 | Iconos |

## Estructura del Proyecto

```
proyecto_semestral/
├── back-end/                          # Backend API (FastAPI)
│   ├── app/
│   │   ├── models/                    # Modelos SQLAlchemy ORM
│   │   │   ├── mesa.py               # Modelo de Mesa
│   │   │   ├── reservacion.py        # Modelo de Reservación
│   │   │   ├── tipo_mesa.py          # Modelo de Tipo de Mesa
│   │   │   └── usuario_admin.py      # Modelo de Usuario Admin
│   │   ├── routers/                   # Endpoints de API
│   │   │   ├── auth.py               # Autenticación (JWT)
│   │   │   ├── reservaciones.py      # Reservaciones públicas
│   │   │   ├── admin.py              # Operaciones de admin
│   │   │   ├── mesas.py              # Gestión de mesas
│   │   │   ├── tipos_mesa.py         # Tipos de mesa
│   │   │   └── vision.py             # Integración IA
│   │   ├── schemas/                   # Esquemas de validación Pydantic
│   │   ├── services/                  # Lógica de negocio
│   │   ├── utils/                     # Utilidades
│   │   ├── config.py                  # Configuración
│   │   ├── database.py                # Conexión a BD
│   │   └── main.py                    # Inicialización FastAPI
│   ├── proyecto_vision_artificial/    # Módulo YOLOv8
│   │   ├── detectar_imagen.py        # Script de detección
│   │   ├── yolov8n.pt                # Modelo YOLO pre-entrenado
│   │   └── Entrenamiendo_mesas/      # Modelo personalizado
│   │       └── weights/best.pt       # Pesos entrenados
│   ├── .env.example                   # Plantilla de variables de entorno
│   ├── pyproject.toml                 # Dependencias Python
│   ├── main.py                        # Punto de entrada
│   └── create_admin.py                # Script crear usuario admin
├── front-end/                         # Frontend (Astro + React)
│   ├── src/
│   │   ├── components/
│   │   │   ├── react/                # Componentes React interactivos
│   │   │   └── ui/                   # Componentes Shadcn UI
│   │   ├── layouts/
│   │   │   └── Layout.astro          # Layout base
│   │   ├── lib/                       # Utilidades y validaciones
│   │   ├── pages/                     # Rutas
│   │   │   ├── index.astro           # Página principal
│   │   │   ├── reservar.astro        # Página de reservaciones
│   │   │   ├── servicios.astro       # Página de servicios
│   │   │   └── sobre-nosotros.astro  # Página acerca de
│   │   └── styles/
│   │       └── global.css            # Estilos globales
│   ├── astro.config.mjs              # Configuración Astro
│   ├── tailwind.config.ts            # Configuración Tailwind
│   └── package.json                  # Dependencias Node
├── reservationsdb.sql                # Esquema de base de datos
├── stak.md                           # Documento stack tecnológico
└── README.md                         # Este archivo
```

## Requisitos Previos

### Backend
- Python 3.13 o superior
- PostgreSQL 18.0 o superior
- uv (gestor de paquetes Python)

### Frontend
- Node.js 18 o superior
- npm, yarn o pnpm

### Visión Artificial (Opcional)
- Cámara IP o webcam
- Raspberry Pi / Jetson (para despliegue en edge)

## Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd proyecto_semestral
```

### 2. Configurar Backend

```bash
# Navegar al directorio del backend
cd back-end

# Copiar archivo de configuración
cp .env.example .env

# Editar .env con tus credenciales de base de datos
# DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/reservationsdb
# SECRET_KEY=tu-clave-secreta-aqui

# Instalar dependencias
uv pip install -e .
```

### 3. Configurar Base de Datos

```bash
# Crear base de datos
psql -U postgres

# En el shell de PostgreSQL:
CREATE DATABASE reservationsdb;
\q

# Ejecutar script de schema
psql -U postgres -d reservationsdb -f ../reservationsdb.sql
```

### 4. Crear Usuario Administrador

```bash
# Ejecutar script de creación de admin
python create_admin.py
```

Esto creará un usuario por defecto:
- **Email**: admin@example.com
- **Contraseña**: admin123

⚠️ **Importante**: Cambia estas credenciales en producción.

### 5. Iniciar Backend

```bash
# Opción 1: Usar main.py
python main.py

# Opción 2: Usar uvicorn directamente
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

El backend estará disponible en:
- API: http://localhost:8000
- Documentación interactiva: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 6. Configurar Frontend

```bash
# Navegar al directorio del frontend
cd ../front-end

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev
```

El frontend estará disponible en: http://localhost:4321

### 7. Configurar Módulo de Visión Artificial (Opcional)

```bash
cd ../back-end/proyecto_vision_artificial

# Editar detectar_imagen.py y configurar IP_WEBCAM
# IP_WEBCAM = "http://tu-ip-de-camara:puerto/video"

# Ejecutar detección
python detectar_imagen.py

# Presiona 'q' para salir
```

## Uso

### Para Clientes

1. Visita http://localhost:4321
2. Navega a la sección "Reservar"
3. Completa el formulario con:
   - Nombre y apellido
   - Correo electrónico
   - Teléfono
   - Número de personas
   - Fecha y hora deseada
4. El sistema asignará automáticamente una mesa disponible
5. Recibirás confirmación de tu reservación

### Para Administradores

1. **Autenticación**:
   ```bash
   POST http://localhost:8000/api/v1/auth/login
   Content-Type: application/json

   {
     "email": "admin@example.com",
     "password": "admin123"
   }
   ```

2. **Usar el token JWT** en las siguientes peticiones:
   ```
   Authorization: Bearer <tu-token-jwt>
   ```

3. **Gestionar Reservaciones**:
   - Listar: `GET /api/v1/admin/reservaciones`
   - Actualizar: `PUT /api/v1/admin/reservaciones/{id}`
   - Eliminar: `DELETE /api/v1/admin/reservaciones/{id}`

4. **Ver Estadísticas**:
   ```bash
   GET /api/v1/admin/dashboard/estadisticas
   ```

## API Endpoints

### Endpoints Públicos

#### Autenticación
```
POST /api/v1/auth/login
```
Inicia sesión y obtiene un token JWT.

#### Reservaciones (Público)
```
POST   /api/v1/reservaciones/              # Crear reservación
GET    /api/v1/reservaciones/disponibilidad # Verificar disponibilidad
GET    /api/v1/reservaciones/{id}          # Obtener detalles
DELETE /api/v1/reservaciones/{id}          # Cancelar reservación
```

#### Estado de Mesas (Público)
```
GET /api/v1/vision/estado-general          # Estado de todas las mesas
```

### Endpoints Protegidos (Requieren JWT)

#### Admin - Reservaciones
```
GET    /api/v1/admin/reservaciones         # Listar todas (filtros: estado, fecha)
GET    /api/v1/admin/reservaciones/{id}    # Detalles de reservación
PUT    /api/v1/admin/reservaciones/{id}    # Actualizar reservación
DELETE /api/v1/admin/reservaciones/{id}    # Eliminar permanentemente
```

#### Admin - Usuarios (Solo Superadmin)
```
POST /api/v1/admin/usuarios                # Crear usuario admin
GET  /api/v1/admin/usuarios                # Listar usuarios admin
PUT  /api/v1/admin/usuarios/{id}           # Actualizar usuario admin
```

#### Admin - Dashboard
```
GET /api/v1/admin/dashboard/estadisticas   # Obtener estadísticas
```

#### Gestión de Mesas
```
GET    /api/v1/mesas/                      # Listar mesas (público)
POST   /api/v1/mesas/                      # Crear mesa (auth)
GET    /api/v1/mesas/{id}                  # Detalles de mesa
PUT    /api/v1/mesas/{id}                  # Actualizar mesa (auth)
DELETE /api/v1/mesas/{id}                  # Eliminar mesa (auth)
```

#### Tipos de Mesa
```
GET    /api/v1/tipos-mesa/                 # Listar tipos
POST   /api/v1/tipos-mesa/                 # Crear tipo (auth)
PUT    /api/v1/tipos-mesa/{id}             # Actualizar tipo (auth)
DELETE /api/v1/tipos-mesa/{id}             # Eliminar tipo (auth)
```

#### Visión Artificial (Protegido)
```
POST /api/v1/vision/actualizar-estado-mesas # Actualizar estados desde IA
```

### Ejemplos de Uso

#### 1. Crear Reservación

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/reservaciones/" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan",
    "apellido": "Pérez",
    "correo": "juan@example.com",
    "telefono": "6000-0000",
    "cantidad_personas": 4,
    "fecha": "2025-12-01",
    "hora": "19:00:00"
  }'
```

**Response (201 Created):**
```json
{
  "id_reserva": 1,
  "nombre": "Juan",
  "apellido": "Pérez",
  "correo": "juan@example.com",
  "telefono": "6000-0000",
  "cantidad_personas": 4,
  "fecha": "2025-12-01",
  "hora": "19:00:00",
  "id_mesa": 3,
  "estado": "pendiente",
  "created_at": "2025-11-29T14:30:00",
  "updated_at": "2025-11-29T14:30:00"
}
```

---

#### 2. Verificar Disponibilidad

**Request:**
```bash
curl "http://localhost:8000/api/v1/reservaciones/disponibilidad?fecha=2025-12-01&hora=19:00:00&cantidad_personas=4"
```

**Response (200 OK):**
```json
{
  "disponible": true,
  "mesas_disponibles": [
    {
      "id_mesa": 3,
      "id_tipo_mesa": 2,
      "estado": "disponible",
      "tipo_mesa": {
        "id_tipo_mesa": 2,
        "descripcion": "Mesa para 4 personas",
        "cantidad_sillas": 4
      }
    },
    {
      "id_mesa": 5,
      "id_tipo_mesa": 3,
      "estado": "disponible",
      "tipo_mesa": {
        "id_tipo_mesa": 3,
        "descripcion": "Mesa para 6 personas",
        "cantidad_sillas": 6
      }
    }
  ],
  "mensaje": "Hay 2 mesa(s) disponible(s) para esta fecha y hora"
}
```

---

#### 3. Login Admin

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }'
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBleGFtcGxlLmNvbSIsImV4cCI6MTYzMjg1MjQwMH0.xyz123...",
  "token_type": "bearer"
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Credenciales incorrectas"
}
```

---

#### 4. Listar Reservaciones (Admin)

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/admin/reservaciones?estado=pendiente" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response (200 OK):**
```json
[
  {
    "id_reserva": 1,
    "nombre": "Juan",
    "apellido": "Pérez",
    "correo": "juan@example.com",
    "telefono": "6000-0000",
    "cantidad_personas": 4,
    "fecha": "2025-12-01",
    "hora": "19:00:00",
    "id_mesa": 3,
    "estado": "pendiente",
    "created_at": "2025-11-29T14:30:00",
    "updated_at": "2025-11-29T14:30:00",
    "mesa": {
      "id_mesa": 3,
      "estado": "reservada",
      "tipo_mesa": {
        "descripcion": "Mesa para 4 personas",
        "cantidad_sillas": 4
      }
    }
  },
  {
    "id_reserva": 2,
    "nombre": "María",
    "apellido": "González",
    "correo": "maria@example.com",
    "telefono": "6111-1111",
    "cantidad_personas": 2,
    "fecha": "2025-12-01",
    "hora": "20:00:00",
    "id_mesa": 1,
    "estado": "pendiente",
    "created_at": "2025-11-29T15:00:00",
    "updated_at": "2025-11-29T15:00:00",
    "mesa": {
      "id_mesa": 1,
      "estado": "reservada",
      "tipo_mesa": {
        "descripcion": "Mesa para 2 personas",
        "cantidad_sillas": 2
      }
    }
  }
]
```

---

#### 5. Obtener Estadísticas (Admin)

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/admin/dashboard/estadisticas" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response (200 OK):**
```json
{
  "total_reservaciones": 45,
  "reservaciones_hoy": 8,
  "reservaciones_pendientes": 12,
  "mesas_disponibles": 5,
  "mesas_ocupadas": 3,
  "mesas_reservadas": 4,
  "reservaciones_por_estado": {
    "pendiente": 12,
    "confirmada": 20,
    "cancelada": 8,
    "completada": 5
  },
  "ocupacion_porcentaje": 58.33
}
```

---

#### 6. Estado General de Mesas

**Request:**
```bash
curl "http://localhost:8000/api/v1/vision/estado-general"
```

**Response (200 OK):**
```json
{
  "total_mesas": 12,
  "mesas": [
    {
      "id_mesa": 1,
      "estado": "disponible",
      "tipo_mesa": {
        "descripcion": "Mesa para 2 personas",
        "cantidad_sillas": 2
      },
      "updated_at": "2025-11-29T14:00:00"
    },
    {
      "id_mesa": 2,
      "estado": "ocupada",
      "tipo_mesa": {
        "descripcion": "Mesa para 4 personas",
        "cantidad_sillas": 4
      },
      "updated_at": "2025-11-29T14:25:00"
    },
    {
      "id_mesa": 3,
      "estado": "reservada",
      "tipo_mesa": {
        "descripcion": "Mesa para 4 personas",
        "cantidad_sillas": 4
      },
      "updated_at": "2025-11-29T14:30:00"
    }
  ],
  "resumen": {
    "disponible": 5,
    "ocupada": 3,
    "reservada": 4
  }
}
```

---

#### 7. Actualizar Reservación (Admin)

**Request:**
```bash
curl -X PUT "http://localhost:8000/api/v1/admin/reservaciones/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "estado": "confirmada",
    "id_mesa": 3
  }'
```

**Response (200 OK):**
```json
{
  "id_reserva": 1,
  "nombre": "Juan",
  "apellido": "Pérez",
  "correo": "juan@example.com",
  "telefono": "6000-0000",
  "cantidad_personas": 4,
  "fecha": "2025-12-01",
  "hora": "19:00:00",
  "id_mesa": 3,
  "estado": "confirmada",
  "created_at": "2025-11-29T14:30:00",
  "updated_at": "2025-11-29T16:00:00"
}
```

---

#### 8. Cancelar Reservación (Cliente)

**Request:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/reservaciones/1"
```

**Response (200 OK):**
```json
{
  "mensaje": "Reservación cancelada exitosamente",
  "id_reserva": 1,
  "estado": "cancelada"
}
```

---

#### 9. Actualizar Estado de Mesas desde Visión Artificial

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/vision/actualizar-estado-mesas" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "detecciones": [
      {
        "id_mesa": 1,
        "personas_detectadas": 0
      },
      {
        "id_mesa": 2,
        "personas_detectadas": 3
      },
      {
        "id_mesa": 3,
        "personas_detectadas": 0
      }
    ]
  }'
```

**Response (200 OK):**
```json
{
  "mensaje": "Estados de mesas actualizados correctamente",
  "mesas_actualizadas": 3,
  "detalle": [
    {
      "id_mesa": 1,
      "estado_anterior": "ocupada",
      "estado_nuevo": "disponible",
      "razon": "Sin personas detectadas, sin reservación activa"
    },
    {
      "id_mesa": 2,
      "estado_anterior": "disponible",
      "estado_nuevo": "ocupada",
      "razon": "Personas detectadas: 3"
    },
    {
      "id_mesa": 3,
      "estado_anterior": "reservada",
      "estado_nuevo": "reservada",
      "razon": "Sin personas detectadas, pero tiene reservación activa"
    }
  ]
}
```

---

### Códigos de Estado HTTP

| Código | Significado | Cuándo se usa |
|--------|-------------|---------------|
| **200** | OK | Operación exitosa |
| **201** | Created | Recurso creado exitosamente |
| **400** | Bad Request | Datos de entrada inválidos |
| **401** | Unauthorized | Token JWT inválido o ausente |
| **403** | Forbidden | Sin permisos para la operación |
| **404** | Not Found | Recurso no encontrado |
| **409** | Conflict | Conflicto (ej: mesa ya reservada) |
| **422** | Unprocessable Entity | Error de validación Pydantic |
| **500** | Internal Server Error | Error del servidor |

## Base de Datos

### Esquema de Tablas

#### tipo_mesa
Tipos de mesas disponibles (2 personas, 4 personas, etc.)

```sql
- id_tipo_mesa (PK)
- descripcion (VARCHAR 50)
- cantidad_sillas (INTEGER)
```

#### mesas
Mesas físicas del restaurante

```sql
- id_mesa (PK)
- id_tipo_mesa (FK → tipo_mesa)
- estado (ENUM: disponible, ocupada, reservada)
- updated_at (TIMESTAMP)
```

#### reservaciones
Reservaciones de clientes

```sql
- id_reserva (PK)
- nombre (VARCHAR 100)
- apellido (VARCHAR 100)
- correo (VARCHAR 150)
- telefono (VARCHAR 50)
- cantidad_personas (INTEGER)
- fecha (DATE)
- hora (TIME)
- id_mesa (FK → mesas, SET NULL)
- estado (ENUM: pendiente, confirmada, cancelada, completada)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

#### usuarios_admin
Usuarios administrativos del sistema

```sql
- id_usuario (PK)
- nombre (VARCHAR 120)
- email (VARCHAR 150, UNIQUE)
- password_hash (TEXT)
- rol (ENUM: admin, superadmin, staff)
- is_active (BOOLEAN)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

### Diagrama de Relaciones

```
┌─────────────┐
│  tipo_mesa  │
└──────┬──────┘
       │
       │ 1:N
       │
┌──────▼──────┐        ┌──────────────┐
│    mesas    │◄───────│ reservaciones│
└─────────────┘  0:N   └──────────────┘

┌──────────────┐
│usuarios_admin│
└──────────────┘
```

## Módulo de Visión Artificial

### Funcionamiento

El módulo de visión artificial utiliza YOLOv8 para detectar:
- **Mesas**: Modelo personalizado entrenado
- **Personas**: Modelo COCO pre-entrenado

### Algoritmo de Actualización de Estado

```python
Para cada mesa detectada:
  Si personas_detectadas > 0:
    mesa.estado = "ocupada"
  Sino:
    Si tiene_reservacion_activa_hoy:
      mesa.estado = "reservada"
    Sino:
      mesa.estado = "disponible"
```

### Configuración de Cámara

1. Edita `proyecto_vision_artificial/detectar_imagen.py`
2. Configura la URL de tu cámara IP:
   ```python
   IP_WEBCAM = "http://192.168.1.100:8080/video"
   ```
3. Asegúrate de estar en la misma red

### Modelos Disponibles

- **Pre-entrenado**: `yolov8n.pt` - Detección general
- **Personalizado**: `Entrenamiendo_mesas/weights/best.pt` - Detección de mesas

## Despliegue

### Stack de Producción Recomendado

- **OS**: Ubuntu Server 22.04 LTS
- **Web Server**: Caddy (reverse proxy)
- **Edge AI**: Raspberry Pi / NVIDIA Jetson
- **Database**: PostgreSQL (servidor dedicado)
- **Backend**: FastAPI con Gunicorn
- **Frontend**: Build estático servido por Caddy

### Build de Producción

#### Backend
```bash
cd back-end
uv pip install -e .

# Usar Gunicorn en producción
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Frontend
```bash
cd front-end
npm run build

# Los archivos estáticos estarán en ./dist/
# Servir con Caddy, Nginx o cualquier servidor web
```

### Variables de Entorno de Producción

```env
DATABASE_URL=postgresql://user:password@db-server:5432/reservationsdb
SECRET_KEY=<generar-clave-segura-aleatoria>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_V1_PREFIX=/api/v1
PROJECT_NAME=Sistema de Reservaciones
ALLOWED_ORIGINS=https://tu-dominio.com
```

### Consideraciones de Seguridad

- ✅ Usar HTTPS en producción
- ✅ Cambiar credenciales por defecto
- ✅ Configurar firewall (solo puertos necesarios)
- ✅ Mantener dependencias actualizadas
- ✅ Implementar rate limiting
- ✅ Configurar backups automáticos de BD
- ✅ Monitorear logs y errores

## Desarrollo

### Estructura de Código

#### Backend - Patrón de Capas

```
Request → Router → Schema (validación) → Service (lógica) → Model (BD) → Response
```

#### Frontend - Arquitectura de Componentes

```
Pages (Astro) → Components (React) → UI Components (Shadcn)
```

### Agregar Nueva Funcionalidad

#### Backend

1. Crear modelo en `app/models/`
2. Crear esquema en `app/schemas/`
3. Implementar lógica en `app/services/`
4. Crear router en `app/routers/`
5. Registrar router en `app/main.py`

#### Frontend

1. Crear componente en `src/components/`
2. Agregar validación en `src/lib/validations.ts`
3. Crear página en `src/pages/`
4. Actualizar navegación si es necesario

### Convenciones de Código

- **Backend**: PEP 8 (Python)
- **Frontend**: ESLint + Prettier
- **Commits**: Mensajes descriptivos en español
- **Nombres**: Español para variables de negocio, inglés para código técnico

## Contribución

### Proceso de Contribución

1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

### Reportar Bugs

Incluir:
- Descripción del bug
- Pasos para reproducir
- Comportamiento esperado vs actual
- Screenshots (si aplica)
- Versión del sistema

## Roadmap

### Características Futuras

- [ ] Sistema de notificaciones por email
- [ ] WebSocket para actualizaciones en tiempo real
- [ ] Dashboard administrativo (UI frontend)
- [ ] Componente de calendario para disponibilidad
- [ ] Soporte multi-idioma (i18n)
- [ ] Toggle de modo oscuro
- [ ] Progressive Web App (PWA)
- [ ] Exportación de reservaciones a PDF
- [ ] Análisis y reportes avanzados
- [ ] Integración con sistemas de pago
- [ ] App móvil nativa

## Licencia

Este proyecto es parte de un trabajo académico para el curso Desarrollo de Software VIII.

## Contacto y Soporte

Para preguntas o soporte:
- Crear un issue en el repositorio
- Contactar al equipo de desarrollo

---

**Proyecto desarrollado con ❤️ para Desarrollo de Software VIII**
