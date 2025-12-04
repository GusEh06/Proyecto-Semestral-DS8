const API_BASE_URL = 'http://localhost:8000/api/v1';
const TOKEN_KEY = 'admin_token';
const USER_KEY = 'admin_user';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface UserData {
  email: string;
  rol: string;
  nombre?: string;
  exp?: number;
}

export class AuthError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'AuthError';
  }
}

/**
 * Realiza el login del administrador
 */
export async function login(credentials: LoginCredentials): Promise<LoginResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: credentials.email,
        password: credentials.password,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new AuthError(
        response.status,
        errorData.detail || 'Credenciales inválidas'
      );
    }

    const data: LoginResponse = await response.json();

    // Guardar token
    saveToken(data.access_token);

    // Decodificar y guardar datos del usuario
    const userData = decodeToken(data.access_token);
    if (userData) {
      saveUser(userData);
    }

    return data;
  } catch (error) {
    if (error instanceof AuthError) {
      throw error;
    }
    throw new AuthError(0, 'Error de conexión con el servidor');
  }
}

/**
 * Cierra la sesión del usuario
 */
export function logout(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }
}

/**
 * Guarda el token en localStorage
 */
export function saveToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(TOKEN_KEY, token);
  }
}

/**
 * Obtiene el token almacenado
 */
export function getToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(TOKEN_KEY);
  }
  return null;
}

/**
 * Guarda los datos del usuario en localStorage
 */
export function saveUser(user: UserData): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }
}

/**
 * Obtiene los datos del usuario almacenados
 */
export function getUser(): UserData | null {
  if (typeof window !== 'undefined') {
    const userData = localStorage.getItem(USER_KEY);
    if (userData) {
      try {
        return JSON.parse(userData);
      } catch {
        return null;
      }
    }
  }
  return null;
}

/**
 * Verifica si el usuario está autenticado
 */
export function isAuthenticated(): boolean {
  const token = getToken();
  if (!token) return false;

  const userData = getUser();
  if (!userData) return false;

  // Verificar si el token ha expirado
  if (userData.exp) {
    const now = Math.floor(Date.now() / 1000);
    if (now >= userData.exp) {
      logout();
      return false;
    }
  }

  return true;
}

/**
 * Decodifica un JWT token (solo funciona con tokens no encriptados)
 * Para producción, considera usar una librería como jose o jwt-decode
 */
export function decodeToken(token: string): UserData | null {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;

    const payload = parts[1];
    const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
    const data = JSON.parse(decoded);

    return {
      email: data.sub || data.email,
      rol: data.rol || 'admin',
      nombre: data.nombre,
      exp: data.exp,
    };
  } catch (error) {
    console.error('Error decoding token:', error);
    return null;
  }
}

/**
 * Obtiene los headers con autenticación para requests API
 */
export function getAuthHeaders(): HeadersInit {
  const token = getToken();
  if (!token) {
    return {
      'Content-Type': 'application/json',
    };
  }

  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  };
}
