# ReservaFácil - Sistema de Reservas Online

Sistema de reservas moderno y eficiente construido con Astro, React y Shadcn UI. Diseño limpio, responsivo y listo para conectar con un backend API.

## 📋 Tabla de Contenidos

- [Características](#características)
- [Tecnologías](#tecnologías)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Instalación](#instalación)
- [Comandos Disponibles](#comandos-disponibles)
- [Páginas Implementadas](#páginas-implementadas)
- [Componentes](#componentes)
- [Formulario de Reservas](#formulario-de-reservas)
- [Integración con API](#integración-con-api)
- [Personalización](#personalización)
- [Deployment](#deployment)

## ✨ Características

- **🎨 Diseño Moderno**: UI limpia y profesional basada en Shadcn UI
- **📱 Totalmente Responsivo**: Optimizado para móviles, tablets y desktop
- **⚡ Alto Rendimiento**: Construido con Astro para máxima velocidad
- **♿ Accesible**: Cumple con estándares de accesibilidad web
- **🔒 Validaciones Robustas**: Validación de formularios con Zod
- **🎯 TypeScript**: Type-safety en todo el proyecto
- **🧩 Componentes Reutilizables**: Sistema de componentes modulares
- **🌐 SEO Optimizado**: Meta tags y estructura semántica

## 🛠 Tecnologías

- **[Astro](https://astro.build)** - Framework web moderno
- **[React](https://react.dev)** - Librería UI para componentes interactivos
- **[TypeScript](https://www.typescriptlang.org)** - JavaScript con tipos
- **[Tailwind CSS](https://tailwindcss.com)** - Framework CSS utility-first
- **[Shadcn UI](https://ui.shadcn.com)** - Componentes UI de alta calidad
- **[React Hook Form](https://react-hook-form.com)** - Gestión de formularios
- **[Zod](https://zod.dev)** - Validación de esquemas TypeScript

## 📂 Estructura del Proyecto

```
front-end/
├── public/               # Archivos estáticos
├── src/
│   ├── components/
│   │   ├── react/       # Componentes React interactivos
│   │   │   └── ReservationForm.tsx
│   │   ├── ui/          # Componentes UI de Shadcn
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── label.tsx
│   │   │   ├── card.tsx
│   │   │   ├── select.tsx
│   │   │   └── textarea.tsx
│   │   ├── Navigation.astro
│   │   └── Footer.astro
│   ├── layouts/
│   │   └── Layout.astro  # Layout principal
│   ├── lib/
│   │   ├── utils.ts      # Utilidades (cn helper)
│   │   └── validations.ts # Esquemas de validación Zod
│   ├── pages/            # Rutas de la aplicación
│   │   ├── index.astro   # Landing page
│   │   ├── servicios.astro
│   │   ├── sobre-nosotros.astro
│   │   └── reservar.astro
│   └── styles/
│       └── global.css    # Estilos globales y variables CSS
├── astro.config.mjs      # Configuración de Astro
├── tailwind.config.ts    # Configuración de Tailwind
├── tsconfig.json         # Configuración de TypeScript
└── package.json
```

## 🚀 Instalación

### Prerequisitos

- Node.js 18+
- npm, yarn, o pnpm

### Pasos

1. **Clonar o navegar al directorio del proyecto**

```bash
cd front-end
```

2. **Instalar dependencias**

```bash
npm install
```

3. **Iniciar servidor de desarrollo**

```bash
npm run dev
```

4. **Abrir en el navegador**

```
http://localhost:4321
```

## 📜 Comandos Disponibles

| Comando | Acción |
|---------|--------|
| `npm install` | Instala las dependencias |
| `npm run dev` | Inicia servidor de desarrollo en `localhost:4321` |
| `npm run build` | Construye el sitio para producción en `./dist/` |
| `npm run preview` | Vista previa local del build de producción |
| `npm run astro ...` | Ejecuta comandos del CLI de Astro |

## 📄 Páginas Implementadas

### 1. Landing Page (`/`)
- Hero section con CTA
- Sección de características destacadas
- Estadísticas y métricas
- Call-to-action final

### 2. Servicios (`/servicios`)
- Listado de servicios ofrecidos
- Tarjetas con características de cada servicio
- Iconografía ilustrativa
- CTA para reservar

### 3. Sobre Nosotros (`/sobre-nosotros`)
- Misión y valores de la empresa
- Presentación del equipo
- Estadísticas de la empresa
- CTA de conversión

### 4. Reservar (`/reservar`)
- Formulario de reserva completo
- Validaciones en tiempo real
- Información importante sobre el servicio
- Preguntas frecuentes (FAQ)

## 🧩 Componentes

### Componentes Astro

#### `Layout.astro`
Layout principal con meta tags, estilos globales y estructura HTML base.

```astro
---
import Layout from '../layouts/Layout.astro';

<Layout title="Título de la página" description="Descripción opcional">
  <!-- Contenido -->
</Layout>
```

#### `Navigation.astro`
Barra de navegación responsiva con menú móvil.

#### `Footer.astro`
Footer con enlaces, información de contacto y copyright.

### Componentes React

#### `ReservationForm.tsx`
Formulario completo de reservas con:
- Validaciones con Zod y React Hook Form
- Estados de carga y éxito/error
- Integración lista para API
- UI responsiva con Shadcn

### Componentes UI (Shadcn)

Componentes base reutilizables:
- `Button` - Botones con variantes (default, destructive, outline, etc.)
- `Input` - Campos de entrada de texto
- `Label` - Etiquetas para formularios
- `Select` - Selectores dropdown
- `Textarea` - Áreas de texto
- `Card` - Contenedores con Header, Content y Footer

## 📝 Formulario de Reservas

### Campos del Formulario

El formulario recopila la siguiente información:

| Campo | Tipo | Validación | Requerido |
|-------|------|-----------|-----------|
| Nombre | text | 2-100 caracteres | Sí |
| Email | email | Formato válido | Sí |
| Teléfono | tel | 7-15 dígitos | Sí |
| Fecha | date | Fecha >= hoy | Sí |
| Hora | select | 08:00 - 20:30 | Sí |
| Servicio | select | cita/espacio/evento/premium | Sí |
| Personas | select | 1-6+ | Sí |
| Notas | textarea | Máx 500 caracteres | No |

### Validaciones Implementadas

Las validaciones están definidas en `src/lib/validations.ts` usando Zod:

```typescript
export const reservationSchema = z.object({
  nombre: z.string().min(2).max(100),
  email: z.string().email(),
  telefono: z.string().min(7).max(15),
  fecha: z.string().min(1),
  hora: z.string().min(1),
  servicio: z.string().min(1),
  personas: z.string().min(1),
  notas: z.string().max(500).optional(),
})
```

### Estados del Formulario

1. **Inicial**: Formulario vacío listo para completar
2. **Validando**: Validaciones en tiempo real mientras el usuario escribe
3. **Submitting**: Durante el envío de datos (botón disabled)
4. **Success**: Mensaje de éxito y reset del formulario
5. **Error**: Mensaje de error y opción de reintentar

## 🔌 Integración con API

El formulario está preparado para conectarse a un backend. Ver documentación detallada en el archivo que crearás luego sobre integración con API.

### Ubicación del código

El código de integración está en:
```
src/components/react/ReservationForm.tsx (líneas 31-46)
```

### Ejemplo básico de integración

```typescript
const response = await fetch('/api/reservations', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(data),
})
```

## 🎨 Personalización

### Colores y Tema

Los colores del tema se definen en `src/styles/global.css` usando variables CSS:

```css
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 222.2 47.4% 11.2%;
  /* ... más variables */
}
```

Modifica estas variables para cambiar el esquema de colores completo.

### Configuración de Tailwind

Personaliza Tailwind en `tailwind.config.ts`:

```typescript
export default {
  theme: {
    extend: {
      colors: {
        // Tus colores personalizados
      }
    }
  }
}
```

### Contenido

El contenido de las páginas se puede modificar directamente en:
- `/` - `src/pages/index.astro`
- `/servicios` - `src/pages/servicios.astro`
- `/sobre-nosotros` - `src/pages/sobre-nosotros.astro`
- `/reservar` - `src/pages/reservar.astro`

## 🚀 Deployment

### Build para Producción

```bash
npm run build
```

Esto genera una carpeta `dist/` con el sitio estático optimizado.

### Opciones de Deployment

#### Vercel (Recomendado)
1. Conecta tu repositorio en [vercel.com](https://vercel.com)
2. Vercel detectará automáticamente que es un proyecto Astro
3. Deploy automático en cada push

#### Netlify
1. Conecta tu repositorio en [netlify.com](https://netlify.com)
2. Build command: `npm run build`
3. Publish directory: `dist`

#### Cloudflare Pages
1. Conecta tu repositorio en Cloudflare Pages
2. Build command: `npm run build`
3. Output directory: `dist`

#### GitHub Pages
```bash
npm run build
# Sube la carpeta dist/ a gh-pages branch
```

### Variables de Entorno en Producción

Si usas variables de entorno, configúralas en tu plataforma de deployment:

```env
API_URL=https://tu-api.com
API_KEY=tu_clave_api
```

## 📱 Responsividad

El sitio es completamente responsivo con breakpoints:
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

## ♿ Accesibilidad

- Navegación por teclado
- Labels asociados a inputs
- Contraste de colores WCAG AA
- Estructura semántica HTML5
- Alt text en imágenes (cuando se agreguen)

## 🧪 Testing (Pendiente)

Para agregar tests en el futuro:

```bash
# Instalar dependencias de testing
npm install --save-dev @testing-library/react vitest

# Ejecutar tests
npm run test
```

## 📈 Próximas Mejoras

- [ ] Sistema de autenticación de usuarios
- [ ] Dashboard de administración
- [ ] Sistema de notificaciones en tiempo real
- [ ] Calendario interactivo de disponibilidad
- [ ] Exportación de reservas a PDF
- [ ] Multi-idioma (i18n)
- [ ] Modo oscuro
- [ ] PWA (Progressive Web App)

## 🤝 Contribución

Este es un proyecto académico. Si deseas contribuir:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Proyecto académico - Universidad - Desarrollo de Software VIII

## 👥 Autores

- **Tu Nombre** - Proyecto Semestral DSVIII

## 🙏 Agradecimientos

- Shadcn UI por los componentes base
- Astro por el framework increíble
- Comunidad de desarrollo web

---

**Nota**: Este proyecto está en desarrollo activo. Para conectar con el backend, revisa el archivo de documentación de API que crearás próximamente.
