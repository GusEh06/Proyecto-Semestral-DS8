# 🎨 EJEMPLOS DE INTEGRACIÓN CON FRONTEND

Este archivo contiene ejemplos de código para integrar el sistema MQTT con diferentes frameworks de frontend.

---

## 📋 Tabla de Contenidos

1. [React/Next.js](#reactnextjs)
2. [Astro](#astro)
3. [Vanilla JavaScript](#vanilla-javascript)
4. [Vue.js](#vuejs)
5. [Svelte](#svelte)

---

## React/Next.js

### 1. Instalación

```bash
npm install mqtt
```

### 2. Hook Personalizado para MQTT

```javascript
// hooks/useMqtt.js
import { useEffect, useState, useRef } from 'react';
import mqtt from 'mqtt';

export const useMqtt = (brokerUrl = 'ws://broker.emqx.io:8083/mqtt') => {
  const [client, setClient] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState([]);
  const clientRef = useRef(null);

  useEffect(() => {
    // Conectar al broker
    const mqttClient = mqtt.connect(brokerUrl, {
      clientId: `restaurant_web_${Math.random().toString(16).slice(3)}`,
      clean: true,
      reconnectPeriod: 1000,
    });

    mqttClient.on('connect', () => {
      console.log('✅ Conectado al broker MQTT');
      setIsConnected(true);
    });

    mqttClient.on('disconnect', () => {
      console.log('❌ Desconectado del broker');
      setIsConnected(false);
    });

    mqttClient.on('message', (topic, payload) => {
      try {
        const data = JSON.parse(payload.toString());
        setMessages(prev => [...prev, { topic, data, timestamp: Date.now() }]);
      } catch (error) {
        console.error('Error parseando mensaje:', error);
      }
    });

    clientRef.current = mqttClient;
    setClient(mqttClient);

    // Cleanup
    return () => {
      if (mqttClient) {
        mqttClient.end();
      }
    };
  }, [brokerUrl]);

  const subscribe = (topic) => {
    if (client && isConnected) {
      client.subscribe(topic, (err) => {
        if (err) {
          console.error('Error suscribiendo a', topic, err);
        } else {
          console.log('📡 Suscrito a:', topic);
        }
      });
    }
  };

  const publish = (topic, message) => {
    if (client && isConnected) {
      client.publish(topic, JSON.stringify(message), { qos: 0 }, (err) => {
        if (err) {
          console.error('Error publicando:', err);
        } else {
          console.log('📤 Mensaje enviado a', topic);
        }
      });
    }
  };

  return { client, isConnected, messages, subscribe, publish };
};
```

### 3. Componente Dashboard

```javascript
// components/RestaurantDashboard.jsx
import { useEffect, useState } from 'react';
import { useMqtt } from '../hooks/useMqtt';

const TOPICS = {
  STATUS: 'restaurante/mesas/status',
  MANUAL: 'restaurante/mesas/manual',
};

export default function RestaurantDashboard() {
  const { isConnected, messages, subscribe, publish } = useMqtt();
  const [mesas, setMesas] = useState([]);

  // Cargar estado inicial desde API/BD
  useEffect(() => {
    fetch('/api/mesas')
      .then(res => res.json())
      .then(data => setMesas(data));
  }, []);

  // Suscribirse a actualizaciones
  useEffect(() => {
    if (isConnected) {
      subscribe(TOPICS.STATUS);
    }
  }, [isConnected, subscribe]);

  // Procesar mensajes MQTT
  useEffect(() => {
    const latestMessage = messages[messages.length - 1];
    if (!latestMessage) return;

    const { topic, data } = latestMessage;

    if (topic === TOPICS.STATUS && data.updated) {
      // Actualizar estado de la mesa en tiempo real
      setMesas(prev => 
        prev.map(mesa => 
          mesa.id_mesa === data.mesa_id 
            ? { ...mesa, estado: data.estado }
            : mesa
        )
      );
    }
  }, [messages]);

  // Función para actualización manual
  const updateMesaManual = (mesaId, nuevoEstado) => {
    const mensaje = {
      mesa_id: mesaId,
      estado: nuevoEstado,
      usuario: 'admin@restaurante.com',
    };
    
    publish(TOPICS.MANUAL, mensaje);
  };

  return (
    <div className="dashboard">
      <div className="status-bar">
        <span className={isConnected ? 'connected' : 'disconnected'}>
          {isConnected ? '🟢 Conectado' : '🔴 Desconectado'}
        </span>
      </div>

      <div className="mesas-grid">
        {mesas.map(mesa => (
          <MesaCard
            key={mesa.id_mesa}
            mesa={mesa}
            onUpdate={updateMesaManual}
          />
        ))}
      </div>
    </div>
  );
}

function MesaCard({ mesa, onUpdate }) {
  const estadoColors = {
    disponible: 'bg-green-500',
    ocupada: 'bg-red-500',
    reservada: 'bg-yellow-500',
  };

  return (
    <div className={`mesa-card ${estadoColors[mesa.estado]}`}>
      <h3>Mesa {mesa.numero_mesa}</h3>
      <p>Capacidad: {mesa.capacidad}</p>
      <p>Estado: {mesa.estado}</p>
      
      {mesa.reservada && (
        <div className="reserva-info">
          🔒 Reservada
        </div>
      )}

      <div className="actions">
        <button onClick={() => onUpdate(mesa.id_mesa, 'ocupada')}>
          Marcar Ocupada
        </button>
        <button onClick={() => onUpdate(mesa.id_mesa, 'disponible')}>
          Marcar Disponible
        </button>
      </div>
    </div>
  );
}
```

### 4. Componente de Reservas

```javascript
// components/ReservaForm.jsx
import { useState } from 'react';
import { useMqtt } from '../hooks/useMqtt';

export default function ReservaForm({ mesasDisponibles }) {
  const { publish, isConnected } = useMqtt();
  const [formData, setFormData] = useState({
    mesa_id: '',
    nombre: '',
    telefono: '',
    email: '',
    num_personas: 2,
    fecha: '',
    hora: '',
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const mensaje = {
      mesa_id: parseInt(formData.mesa_id),
      cliente: {
        nombre: formData.nombre,
        telefono: formData.telefono,
        email: formData.email,
        num_personas: formData.num_personas,
        fecha: formData.fecha,
        hora: formData.hora,
      },
    };

    publish('restaurante/mesas/reservas', mensaje);
    
    // Resetear formulario
    setFormData({
      mesa_id: '',
      nombre: '',
      telefono: '',
      email: '',
      num_personas: 2,
      fecha: '',
      hora: '',
    });
  };

  return (
    <form onSubmit={handleSubmit} className="reserva-form">
      <h2>Nueva Reserva</h2>
      
      <select
        value={formData.mesa_id}
        onChange={(e) => setFormData({...formData, mesa_id: e.target.value})}
        required
      >
        <option value="">Selecciona una mesa</option>
        {mesasDisponibles.map(mesa => (
          <option key={mesa.id_mesa} value={mesa.id_mesa}>
            Mesa {mesa.numero_mesa} (Capacidad: {mesa.capacidad})
          </option>
        ))}
      </select>

      <input
        type="text"
        placeholder="Nombre completo"
        value={formData.nombre}
        onChange={(e) => setFormData({...formData, nombre: e.target.value})}
        required
      />

      <input
        type="tel"
        placeholder="Teléfono"
        value={formData.telefono}
        onChange={(e) => setFormData({...formData, telefono: e.target.value})}
        required
      />

      <input
        type="email"
        placeholder="Email"
        value={formData.email}
        onChange={(e) => setFormData({...formData, email: e.target.value})}
      />

      <input
        type="number"
        min="1"
        max="10"
        placeholder="Número de personas"
        value={formData.num_personas}
        onChange={(e) => setFormData({...formData, num_personas: e.target.value})}
        required
      />

      <input
        type="date"
        value={formData.fecha}
        onChange={(e) => setFormData({...formData, fecha: e.target.value})}
        required
      />

      <input
        type="time"
        value={formData.hora}
        onChange={(e) => setFormData({...formData, hora: e.target.value})}
        required
      />

      <button type="submit" disabled={!isConnected}>
        {isConnected ? 'Reservar' : 'Conectando...'}
      </button>
    </form>
  );
}
```

---

## Astro

### 1. Componente Client-Side

```astro
---
// src/components/MesasMonitor.astro
---

<div id="mesas-container"></div>

<script>
  import mqtt from 'mqtt';

  // Conectar a MQTT
  const client = mqtt.connect('ws://broker.emqx.io:8083/mqtt', {
    clientId: `restaurant_${Math.random().toString(16).slice(3)}`,
  });

  let mesas = [];

  // Cargar estado inicial
  async function loadMesas() {
    const response = await fetch('/api/mesas.json');
    mesas = await response.json();
    renderMesas();
  }

  // Renderizar mesas
  function renderMesas() {
    const container = document.getElementById('mesas-container');
    if (!container) return;

    container.innerHTML = mesas.map(mesa => `
      <div class="mesa ${mesa.estado}">
        <h3>Mesa ${mesa.numero_mesa}</h3>
        <p>${mesa.estado.toUpperCase()}</p>
        <p>Capacidad: ${mesa.capacidad}</p>
      </div>
    `).join('');
  }

  // Configurar MQTT
  client.on('connect', () => {
    console.log('Conectado a MQTT');
    client.subscribe('restaurante/mesas/status');
  });

  client.on('message', (topic, payload) => {
    const data = JSON.parse(payload.toString());
    
    // Actualizar mesa específica
    mesas = mesas.map(mesa => 
      mesa.id_mesa === data.mesa_id 
        ? { ...mesa, estado: data.estado }
        : mesa
    );
    
    renderMesas();
  });

  // Inicializar
  loadMesas();
</script>

<style>
  .mesa {
    padding: 1rem;
    border-radius: 8px;
    margin: 0.5rem;
  }
  .disponible { background: #4ade80; }
  .ocupada { background: #f87171; }
  .reservada { background: #fbbf24; }
</style>
```

---

## Vanilla JavaScript

### Implementación Simple

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Restaurant Monitor</title>
    <script src="https://unpkg.com/mqtt/dist/mqtt.min.js"></script>
    <style>
        .mesas-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 1rem;
            padding: 1rem;
        }
        .mesa {
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
            transition: all 0.3s;
        }
        .disponible { background: #4ade80; }
        .ocupada { background: #f87171; }
        .reservada { background: #fbbf24; }
        .status { 
            position: fixed; 
            top: 10px; 
            right: 10px; 
            padding: 10px;
        }
        .connected { color: green; }
        .disconnected { color: red; }
    </style>
</head>
<body>
    <div id="status" class="status disconnected">🔴 Desconectado</div>
    <div id="mesas-container" class="mesas-grid"></div>

    <script>
        // Estado global
        let mesas = [];

        // Conectar a MQTT
        const client = mqtt.connect('ws://broker.emqx.io:8083/mqtt', {
            clientId: 'restaurant_web_' + Math.random().toString(16).slice(3)
        });

        // Eventos MQTT
        client.on('connect', function() {
            console.log('✅ Conectado a MQTT');
            document.getElementById('status').innerHTML = '🟢 Conectado';
            document.getElementById('status').className = 'status connected';
            
            client.subscribe('restaurante/mesas/status');
        });

        client.on('message', function(topic, message) {
            try {
                const data = JSON.parse(message.toString());
                console.log('📨 Mensaje:', data);
                
                if (data.mesa_id && data.estado) {
                    actualizarMesa(data.mesa_id, data.estado);
                }
            } catch (error) {
                console.error('Error:', error);
            }
        });

        // Cargar mesas iniciales
        async function cargarMesas() {
            try {
                const response = await fetch('/api/mesas');
                mesas = await response.json();
                renderizarMesas();
            } catch (error) {
                console.error('Error cargando mesas:', error);
            }
        }

        // Renderizar mesas
        function renderizarMesas() {
            const container = document.getElementById('mesas-container');
            
            container.innerHTML = mesas.map(mesa => `
                <div class="mesa ${mesa.estado}" data-id="${mesa.id_mesa}">
                    <h3>Mesa ${mesa.numero_mesa}</h3>
                    <p>Estado: <strong>${mesa.estado}</strong></p>
                    <p>Capacidad: ${mesa.capacidad}</p>
                    ${mesa.reservada ? '<p>🔒 Reservada</p>' : ''}
                    <div>
                        <button onclick="cambiarEstado(${mesa.id_mesa}, 'ocupada')">
                            Ocupar
                        </button>
                        <button onclick="cambiarEstado(${mesa.id_mesa}, 'disponible')">
                            Liberar
                        </button>
                    </div>
                </div>
            `).join('');
        }

        // Actualizar mesa específica
        function actualizarMesa(mesaId, nuevoEstado) {
            mesas = mesas.map(mesa => 
                mesa.id_mesa === mesaId 
                    ? { ...mesa, estado: nuevoEstado }
                    : mesa
            );
            renderizarMesas();
        }

        // Cambiar estado de mesa
        function cambiarEstado(mesaId, estado) {
            const mensaje = {
                mesa_id: mesaId,
                estado: estado,
                usuario: 'admin@restaurante.com'
            };
            
            client.publish(
                'restaurante/mesas/manual',
                JSON.stringify(mensaje)
            );
        }

        // Inicializar
        cargarMesas();
    </script>
</body>
</html>
```

---

## Vue.js

### Composable para MQTT

```javascript
// composables/useMqtt.js
import { ref, onMounted, onUnmounted } from 'vue';
import mqtt from 'mqtt';

export function useMqtt(brokerUrl = 'ws://broker.emqx.io:8083/mqtt') {
  const client = ref(null);
  const isConnected = ref(false);
  const messages = ref([]);

  onMounted(() => {
    const mqttClient = mqtt.connect(brokerUrl, {
      clientId: `restaurant_vue_${Math.random().toString(16).slice(3)}`,
    });

    mqttClient.on('connect', () => {
      console.log('Conectado a MQTT');
      isConnected.value = true;
    });

    mqttClient.on('message', (topic, payload) => {
      const data = JSON.parse(payload.toString());
      messages.value.push({ topic, data, timestamp: Date.now() });
    });

    client.value = mqttClient;
  });

  onUnmounted(() => {
    if (client.value) {
      client.value.end();
    }
  });

  const subscribe = (topic) => {
    if (client.value && isConnected.value) {
      client.value.subscribe(topic);
    }
  };

  const publish = (topic, message) => {
    if (client.value && isConnected.value) {
      client.value.publish(topic, JSON.stringify(message));
    }
  };

  return {
    isConnected,
    messages,
    subscribe,
    publish,
  };
}
```

---

## Svelte

### Store MQTT

```javascript
// stores/mqtt.js
import { writable } from 'svelte/store';
import mqtt from 'mqtt';

function createMqttStore() {
  const { subscribe, set, update } = writable({
    isConnected: false,
    messages: [],
    client: null,
  });

  const client = mqtt.connect('ws://broker.emqx.io:8083/mqtt', {
    clientId: `restaurant_svelte_${Math.random().toString(16).slice(3)}`,
  });

  client.on('connect', () => {
    update(state => ({ ...state, isConnected: true, client }));
  });

  client.on('message', (topic, payload) => {
    const data = JSON.parse(payload.toString());
    update(state => ({
      ...state,
      messages: [...state.messages, { topic, data }],
    }));
  });

  return {
    subscribe,
    subscribeTopic: (topic) => client.subscribe(topic),
    publish: (topic, message) => client.publish(topic, JSON.stringify(message)),
  };
}

export const mqttStore = createMqttStore();
```

---

## 📊 API Endpoints Recomendados

### FastAPI Backend

```python
from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2

app = FastAPI()

@app.get("/api/mesas")
async def get_mesas():
    conn = psycopg2.connect(...)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mesas")
    mesas = cursor.fetchall()
    return mesas

@app.get("/api/reservas")
async def get_reservas():
    # Retornar reservas activas
    pass

@app.post("/api/reservas")
async def crear_reserva(reserva: dict):
    # Validar y publicar a MQTT
    pass
```

---

## 🔐 Consideraciones de Seguridad

1. **Usar WebSocket Seguro (WSS) en producción**
```javascript
const client = mqtt.connect('wss://tu-broker-seguro.com:8084/mqtt', {
  username: 'usuario',
  password: 'password',
});
```

2. **Validar mensajes en el frontend**
```javascript
if (data.mesa_id && typeof data.mesa_id === 'number') {
  // Procesar
}
```

3. **Rate Limiting**
```javascript
let lastUpdate = 0;
const RATE_LIMIT = 1000; // 1 segundo

function updateMesa(id, estado) {
  if (Date.now() - lastUpdate < RATE_LIMIT) {
    console.warn('Demasiadas actualizaciones');
    return;
  }
  // Actualizar
  lastUpdate = Date.now();
}
```

---

Estos ejemplos te dan una base sólida para integrar el sistema MQTT con cualquier framework frontend. ¡Adapta según tus necesidades!
