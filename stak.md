┌─────────────────────────────────────────┐
│         STACK TECNOLÓGICO               │
├─────────────────────────────────────────┤
│ Frontend:  React o Astro                │
│ Backend:   FastAPI (Python)             │
│ Database:  PostgreSQL                   │
│ Server:    Caddy                        │
│ OS:        Ubuntu Server 22.04 LTS      │
│ Edge AI:   YOLOv8 (Raspberry Pi/Jetson) │
└─────────────────────────────────────────┘
```

---

## 🎨 Frontend: React vs Astro

Te ayudo a decidir:

### **React** - Aplicación Web Interactiva

**Mejor si:**
- ✅ Dashboard con actualizaciones en tiempo real
- ✅ Muchas interacciones (drag & drop, formularios complejos)
- ✅ WebSockets para ver mesas actualizándose
- ✅ App tipo SPA (Single Page Application)

**Stack típico:**
```
React 18
├── Vite (build tool)
├── TailwindCSS (estilos)
├── React Router (navegación)
├── Zustand/Redux (estado global)
├── React Query (data fetching)
└── WebSocket (tiempo real)
```

---

### **Astro** - Sitio Web Ultra Rápido

**Mejor si:**
- ✅ Necesitas SEO perfecto
- ✅ Sitio principalmente informativo
- ✅ Quieres velocidad máxima
- ✅ Mezcla de contenido estático + dinámico

**Stack típico:**
```
Astro 4
├── React Islands (solo donde necesites interactividad)
├── TailwindCSS
└── View Transitions
```

**Puedes mezclar:** Astro para landing page + React para el dashboard

---

## 💡 Mi Recomendación para Tu Proyecto

### **Usa React** para:

**1. Dashboard del Staff** (interno)
- Necesita actualizaciones en tiempo real
- Muchas interacciones
- No necesita SEO

**2. Sistema de Reservas de Clientes** (público)
- Formularios interactivos
- Selección de mesas/horarios
- Validación en tiempo real

**Usa Astro** para:
- Landing page del restaurante (opcional)
- Páginas informativas (menú, ubicación, etc)

---

## 📁 Estructura del Proyecto Completa
```
restaurant-system/
│
├── frontend/                    # React App
│   ├── public/
│   │   └── assets/
│   ├── src/
│   │   ├── components/
│   │   │   ├── MesaCard.jsx
│   │   │   ├── ReservaForm.jsx
│   │   │   └── Dashboard.jsx
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Reservas.jsx
│   │   │   └── Admin.jsx
│   │   ├── services/
│   │   │   └── api.js          # Llamadas al backend
│   │   ├── hooks/
│   │   │   └── useWebSocket.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── backend/                     # FastAPI
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── mesa.py
│   │   │   ├── reserva.py
│   │   │   └── usuario.py
│   │   ├── schemas/
│   │   │   ├── mesa.py
│   │   │   ├── reserva.py
│   │   │   └── usuario.py
│   │   ├── routers/
│   │   │   ├── mesas.py
│   │   │   ├── reservas.py
│   │   │   ├── vision.py
│   │   │   └── auth.py
│   │   └── services/
│   │       └── websocket.py
│   ├── requirements.txt
│   ├── .env
│   └── alembic/                # Migraciones DB
│
├── edge/                        # Código para Raspberry Pi
│   ├── vision_system.py
│   ├── config.json
│   └── requirements.txt
│
└── deployment/
    ├── Caddyfile
    └── systemd/
        └── restaurant-api.service
    