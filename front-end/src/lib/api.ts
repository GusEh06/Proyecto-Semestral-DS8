const API_BASE_URL = 'http://localhost:8000/api/v1';

export interface ReservacionData {
  nombre: string;
  apellido: string;
  correo: string;
  telefono: string;
  cantidad_personas: number;
  fecha: string; // YYYY-MM-DD
  hora: string; // HH:MM:SS en formato 24h
}

export interface ReservacionResponse {
  id_reserva: number;
  nombre: string;
  apellido: string;
  correo: string;
  telefono: string;
  cantidad_personas: number;
  fecha: string;
  hora: string;
  id_mesa: number | null;
  estado: string;
  created_at: string;
  updated_at: string;
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

export async function crearReservacion(data: ReservacionData): Promise<ReservacionResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/reservaciones/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        response.status,
        errorData.detail || `Error ${response.status}: ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(0, 'Error de conexión con el servidor');
  }
}

export async function consultarDisponibilidad(
  fecha: string,
  hora: string,
  cantidad_personas: number
) {
  try {
    const params = new URLSearchParams({
      fecha,
      hora,
      cantidad_personas: cantidad_personas.toString(),
    });

    const response = await fetch(
      `${API_BASE_URL}/reservaciones/disponibilidad?${params}`
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        response.status,
        errorData.detail || `Error ${response.status}: ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(0, 'Error de conexión con el servidor');
  }
}

// ==================== ADMIN ENDPOINTS ====================

export interface EstadisticasDashboard {
  total_reservaciones: number;
  reservaciones_hoy: number;
  reservaciones_pendientes: number;
  reservaciones_confirmadas_hoy: number;
  total_mesas: number;
  mesas_disponibles: number;
  mesas_ocupadas: number;
  mesas_reservadas: number;
  reservaciones_por_estado: {
    pendiente: number;
    confirmada: number;
    cancelada: number;
    completada: number;
  };
}

export interface Mesa {
  id_mesa: number;
  numero_mesa?: number;
  id_tipo_mesa: number;
  estado: 'disponible' | 'ocupada' | 'reservada';
  personas_actuales: number;
  updated_at: string;
  tipo_mesa?: {
    descripcion: string;
    cantidad_sillas: number;
  };
}

export interface ReservacionAdmin extends ReservacionResponse {
  mesa?: Mesa;
}

/**
 * Obtiene las estadísticas del dashboard (requiere autenticación)
 */
export async function getEstadisticasDashboard(token: string): Promise<EstadisticasDashboard> {
  try {
    const response = await fetch(`${API_BASE_URL}/admin/dashboard/estadisticas`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        response.status,
        errorData.detail || `Error ${response.status}: ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(0, 'Error de conexión con el servidor');
  }
}

/**
 * Obtiene todas las reservaciones (requiere autenticación)
 */
export async function getReservacionesAdmin(
  token: string,
  estado?: string,
  fecha?: string
): Promise<ReservacionAdmin[]> {
  try {
    const params = new URLSearchParams();
    if (estado) params.append('estado', estado);
    if (fecha) params.append('fecha', fecha);

    const url = `${API_BASE_URL}/admin/reservaciones${params.toString() ? '?' + params.toString() : ''}`;

    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        response.status,
        errorData.detail || `Error ${response.status}: ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(0, 'Error de conexión con el servidor');
  }
}

/**
 * Actualiza una reservación (requiere autenticación)
 */
export async function actualizarReservacion(
  token: string,
  id: number,
  data: Partial<ReservacionData> & { estado?: string }
): Promise<ReservacionResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/admin/reservaciones/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        response.status,
        errorData.detail || `Error ${response.status}: ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(0, 'Error de conexión con el servidor');
  }
}

/**
 * Elimina una reservación (requiere autenticación)
 */
export async function eliminarReservacion(token: string, id: number): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/admin/reservaciones/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        response.status,
        errorData.detail || `Error ${response.status}: ${response.statusText}`
      );
    }
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(0, 'Error de conexión con el servidor');
  }
}

/**
 * Obtiene el estado general de todas las mesas
 */
export async function getEstadoMesas(token?: string): Promise<Mesa[]> {
  try {
    const headers: HeadersInit = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/vision/estado-general`, {
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        response.status,
        errorData.detail || `Error ${response.status}: ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(0, 'Error de conexión con el servidor');
  }
}

/**
 * Actualiza el estado de una mesa manualmente (requiere autenticación)
 */
export async function actualizarEstadoMesa(
  token: string,
  id: number,
  estado: 'disponible' | 'ocupada' | 'reservada'
): Promise<Mesa> {
  try {
    const response = await fetch(`${API_BASE_URL}/mesas/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ estado }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        response.status,
        errorData.detail || `Error ${response.status}: ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(0, 'Error de conexión con el servidor');
  }
}
