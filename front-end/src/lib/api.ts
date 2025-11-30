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
