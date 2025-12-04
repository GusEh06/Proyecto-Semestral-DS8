# Dashboard Administrativo - Documentación

## 📋 Índice

1. [Descripción General](#descripción-general)
2. [Características Implementadas](#características-implementadas)
3. [Estructura de Archivos](#estructura-de-archivos)
4. [Instalación y Configuración](#instalación-y-configuración)
5. [Guía de Uso](#guía-de-uso)
6. [Credenciales de Prueba](#credenciales-de-prueba)
7. [Funcionalidades Detalladas](#funcionalidades-detalladas)

---

## 🎯 Descripción General

El **Dashboard Administrativo** es una interfaz web completa para gestionar el sistema de reservaciones del restaurante. Permite a los administradores:

- Ver estadísticas en tiempo real
- Gestionar reservaciones
- Monitorear el estado de las mesas
- Actualizar estados manualmente cuando sea necesario

El dashboard se actualiza automáticamente cada 10-30 segundos dependiendo de la sección.

---

## ✨ Características Implementadas

### 🔐 Autenticación
- ✅ Login con email y contraseña
- ✅ JWT tokens con expiración (30 minutos)
- ✅ Protección de rutas (redirección automática si no está autenticado)
- ✅ Logout seguro
- ✅ Verificación de token en cada carga de página

### 📊 Dashboard Principal
- ✅ Estadísticas en tiempo real:
  - Total de reservaciones
  - Reservaciones de hoy
  - Reservaciones pendientes
  - Reservaciones confirmadas hoy
- ✅ Estado de mesas (total, disponibles, ocupadas, reservadas)
- ✅ Gráfico de reservaciones por estado
- ✅ Actualización automática cada 30 segundos

### 🍽️ Gestión de Mesas
- ✅ Vista en grid con estado visual de cada mesa
- ✅ Códigos de color por estado:
  - 🟢 Verde: Disponible
  - 🔴 Rojo: Ocupada
  - 🔵 Azul: Reservada
- ✅ Información de capacidad (número de personas)
- ✅ Cambio manual de estado
- ✅ Actualización automática cada 10 segundos

### 📅 Gestión de Reservaciones
- ✅ Tabla completa con todas las reservaciones
- ✅ Filtros por estado y fecha
- ✅ Vista de detalles completos
- ✅ Cambio de estado (pendiente → confirmada → completada)
- ✅ Eliminación de reservaciones
- ✅ Badges visuales por estado
- ✅ Actualización automática cada 30 segundos

### 🎨 UI/UX
- ✅ Diseño responsive (móvil, tablet, desktop)
- ✅ Sidebar colapsable en móvil
- ✅ Componentes modernos con Shadcn UI
- ✅ Animaciones y transiciones suaves
- ✅ Estados de carga
- ✅ Manejo de errores

---

## 📁 Estructura de Archivos

```
front-end/
├── src/
│   ├── components/
│   │   ├── react/
│   │   │   └── admin/
│   │   │       ├── LoginForm.tsx           # Formulario de login
│   │   │       ├── AdminNav.tsx            # Navegación sidebar
│   │   │       ├── StatsCards.tsx          # Tarjetas de estadísticas
│   │   │       ├── MesasGrid.tsx           # Grid de mesas
│   │   │       └── ReservationsTable.tsx   # Tabla de reservaciones
│   │   └── ui/
│   │       ├── badge.tsx                   # Componente Badge
│   │       ├── table.tsx                   # Componente Table
│   │       ├── dialog.tsx                  # Componente Dialog
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── input.tsx
│   │       ├── label.tsx
│   │       └── select.tsx
│   ├── layouts/
│   │   └── AdminLayout.astro               # Layout para páginas admin
│   ├── lib/
│   │   ├── auth.ts                         # Servicio de autenticación
│   │   ├── api.ts                          # Cliente API (con endpoints admin)
│   │   ├── utils.ts
│   │   └── validations.ts
│   ├── pages/
│   │   └── admin/
│   │       ├── index.astro                 # Redirección a dashboard
│   │       ├── login.astro                 # Página de login
│   │       ├── dashboard.astro             # Dashboard principal
│   │       ├── mesas.astro                 # Gestión de mesas
│   │       └── reservaciones.astro         # Gestión de reservaciones
│   └── styles/
│       └── global.css
└── package.json
```

---

## 🚀 Instalación y Configuración

### 1. Instalar Dependencias

```bash
cd front-end
npm install
```

### 2. Configurar Variables de Entorno (Opcional)

Si necesitas cambiar la URL del backend, edita `src/lib/api.ts`:

```typescript
const API_BASE_URL = 'http://localhost:8000/api/v1';
```

### 3. Iniciar el Servidor de Desarrollo

```bash
npm run dev
```

El frontend estará disponible en: `http://localhost:4321`

### 4. Iniciar el Backend

Asegúrate de que el backend esté corriendo en `http://localhost:8000`:

```bash
cd ../back-end
uvicorn app.main:app --reload
```

---

## 📖 Guía de Uso

### Paso 1: Acceder al Login

1. Navega a `http://localhost:4321/admin/login`
2. Verás la página de login con un formulario

### Paso 2: Iniciar Sesión

1. Ingresa tus credenciales de administrador
2. Haz clic en "Iniciar Sesión"
3. Serás redirigido automáticamente al dashboard

### Paso 3: Navegar por el Dashboard

**Sidebar de Navegación:**
- 📊 **Dashboard**: Estadísticas generales
- 📅 **Reservaciones**: Gestión de reservaciones
- 🍽️ **Mesas**: Estado de mesas

**En Móvil:**
- Usa el botón de menú (☰) en la esquina superior izquierda

### Paso 4: Usar las Funcionalidades

#### Dashboard
- Visualiza las métricas principales
- Las estadísticas se actualizan cada 30 segundos

#### Gestión de Mesas
- Haz clic en cualquier mesa para ver detalles
- Cambia el estado manualmente si es necesario
- Los datos se actualizan cada 10 segundos

#### Gestión de Reservaciones
- Usa los filtros para buscar reservaciones específicas
- Haz clic en 👁️ para ver detalles
- Haz clic en ✏️ para cambiar el estado
- Haz clic en 🗑️ para eliminar

### Paso 5: Cerrar Sesión

- Haz clic en el botón "Cerrar Sesión" en el sidebar
- Serás redirigido al login

---

## 🔑 Credenciales de Prueba

Para crear un usuario administrador, usa el script del backend:

```bash
cd back-end
python create_admin.py
```

**Credenciales por defecto:**
```
Email: admin@restaurante.com
Password: admin123
```

---

## 🛠️ Funcionalidades Detalladas

### 1. Autenticación (auth.ts)

**Funciones principales:**
- `login(credentials)` - Inicia sesión y guarda el token
- `logout()` - Cierra sesión y limpia el almacenamiento
- `getToken()` - Obtiene el token guardado
- `isAuthenticated()` - Verifica si el usuario está autenticado
- `getUser()` - Obtiene los datos del usuario

**Almacenamiento:**
- Token JWT: `localStorage.getItem('admin_token')`
- Datos usuario: `localStorage.getItem('admin_user')`

### 2. API Client (api.ts)

**Endpoints Admin:**
- `getEstadisticasDashboard(token)` - Obtiene estadísticas
- `getReservacionesAdmin(token, estado?, fecha?)` - Lista reservaciones
- `actualizarReservacion(token, id, data)` - Actualiza una reservación
- `eliminarReservacion(token, id)` - Elimina una reservación
- `getEstadoMesas(token?)` - Obtiene estado de mesas
- `actualizarEstadoMesa(token, id, estado)` - Actualiza estado de mesa

### 3. Componentes React

#### StatsCards
- Muestra tarjetas de estadísticas
- Actualización automática cada 30 segundos
- Gráficos de barras para estados de reservaciones

#### MesasGrid
- Grid responsive de mesas
- Códigos de color por estado
- Modal para cambiar estado
- Actualización automática cada 10 segundos

#### ReservationsTable
- Tabla completa de reservaciones
- Filtros dinámicos (estado y fecha)
- Acciones: ver, editar, eliminar
- Modals para cada acción
- Actualización automática cada 30 segundos

### 4. AdminLayout

**Características:**
- Verifica autenticación al cargar
- Sidebar con navegación
- Header con título de página
- Responsive (colapsa en móvil)
- Logout integrado

---

## 🎨 Personalización

### Cambiar Colores

Edita `src/styles/global.css` para cambiar los colores del tema.

### Cambiar Intervalos de Actualización

En cada componente, busca:
```typescript
const interval = setInterval(loadData, 30000); // 30 segundos
```

### Agregar Nuevas Páginas

1. Crea el archivo en `src/pages/admin/nueva-pagina.astro`
2. Usa el `AdminLayout`
3. Agrega la ruta en `AdminNav.tsx`

---

## 🐛 Solución de Problemas

### "Error de conexión con el servidor"
- Verifica que el backend esté corriendo
- Revisa la URL en `src/lib/api.ts`

### "Credenciales inválidas"
- Verifica que el usuario exista en la base de datos
- Usa `create_admin.py` para crear uno

### "Token expirado"
- Los tokens expiran en 30 minutos
- Simplemente vuelve a iniciar sesión

### No se muestran los datos
- Abre la consola del navegador (F12)
- Verifica que no haya errores
- Asegúrate de que el backend responda correctamente

---

## 📈 Mejoras Futuras (Opcionales)

- [ ] WebSocket para actualizaciones en tiempo real
- [ ] Notificaciones push
- [ ] Exportación de reportes (PDF/Excel)
- [ ] Gráficos avanzados con Chart.js
- [ ] Sistema de notificaciones por email
- [ ] Historial de cambios (audit log)
- [ ] Modo oscuro completo
- [ ] Búsqueda avanzada
- [ ] Paginación de tablas

---

## 📝 Notas Importantes

1. **Seguridad**: Los tokens se guardan en `localStorage`. Para producción, considera usar cookies httpOnly.

2. **CORS**: Asegúrate de que el backend tenga CORS configurado correctamente.

3. **Actualizaciones automáticas**: Los componentes se actualizan automáticamente, pero puedes usar el botón "Actualizar" para forzar una actualización.

4. **Responsive**: El dashboard funciona en móviles, tablets y desktop.

5. **Navegadores**: Probado en Chrome, Firefox, Safari y Edge modernos.

---

## 🤝 Soporte

Si tienes problemas o preguntas:
1. Revisa esta documentación
2. Verifica los logs del backend
3. Abre la consola del navegador (F12)
4. Revisa la sección de solución de problemas

---

## 📄 Licencia

Este proyecto es parte del sistema de gestión de restaurante.

---

**¡Listo! Tu dashboard administrativo está completamente funcional.** 🎉
