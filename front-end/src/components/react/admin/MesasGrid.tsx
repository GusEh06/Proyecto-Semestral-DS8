import { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';
import { getEstadoMesas, actualizarEstadoMesa, type Mesa, ApiError } from '@/lib/api';
import { getToken } from '@/lib/auth';
import { Table2, Users, Loader2, RefreshCw } from 'lucide-react';

export default function MesasGrid() {
  const [mesas, setMesas] = useState<Mesa[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedMesa, setSelectedMesa] = useState<Mesa | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [updating, setUpdating] = useState(false);
  const [isConnected, setIsConnected] = useState(false); // Estado de conexión SSE

  useEffect(() => {
    // Carga inicial de mesas
    loadMesas();

    // 🔴 CONFIGURAR SERVER-SENT EVENTS (SSE) PARA ACTUALIZACIONES EN TIEMPO REAL
    // ============================================================================
    // EventSource es la API nativa del navegador para SSE
    // Mantiene una conexión abierta con el servidor para recibir actualizaciones automáticas
    const API_BASE = 'http://localhost:8000'; // Debe coincidir con tu backend
    const eventSource = new EventSource(`${API_BASE}/api/v1/mesas/stream-updates`);

    // Evento: Conexión establecida
    eventSource.onopen = () => {
      console.log('[SSE] ✅ Conectado al servidor en tiempo real');
      setIsConnected(true);
      setError(null);
    };

    // Evento: Mensaje recibido del servidor
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        // Manejar diferentes tipos de eventos
        if (data.type === 'connected') {
          console.log('[SSE] 📡', data.message);
        } else if (data.type === 'mesa_update') {
          // 🎯 ACTUALIZACIÓN DE MESAS EN TIEMPO REAL
          console.log('[SSE] 🔄 Mesas actualizadas automáticamente', data.data);
          setMesas(data.data); // Actualizar estado con los nuevos datos
        }
      } catch (err) {
        console.error('[SSE] Error procesando mensaje:', err);
      }
    };

    // Evento: Error de conexión
    eventSource.onerror = (err) => {
      console.error('[SSE] ❌ Error de conexión:', err);
      setIsConnected(false);

      // EventSource reintenta automáticamente, pero si falla muchas veces:
      if (eventSource.readyState === EventSource.CLOSED) {
        console.log('[SSE] 🔌 Conexión cerrada, intentando reconectar...');
        setError('Conexión en tiempo real perdida. Reconectando...');
      }
    };

    // Cleanup: Cerrar conexión cuando el componente se desmonte
    return () => {
      console.log('[SSE] 👋 Cerrando conexión');
      eventSource.close();
      setIsConnected(false);
    };
  }, []);

  const loadMesas = async () => {
    try {
      const token = getToken();
      const data = await getEstadoMesas(token || undefined);
      setMesas(data);
      setError(null);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Error al cargar las mesas');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleMesaClick = (mesa: Mesa) => {
    setSelectedMesa(mesa);
    setDialogOpen(true);
  };

  const handleUpdateEstado = async (nuevoEstado: 'disponible' | 'ocupada' | 'reservada') => {
    if (!selectedMesa) return;

    setUpdating(true);
    try {
      const token = getToken();
      if (!token) {
        window.location.href = '/admin/login';
        return;
      }

      await actualizarEstadoMesa(token, selectedMesa.id_mesa, nuevoEstado);
      await loadMesas();
      setDialogOpen(false);
      setSelectedMesa(null);
    } catch (err) {
      if (err instanceof ApiError) {
        alert(err.message);
      } else {
        alert('Error al actualizar el estado');
      }
    } finally {
      setUpdating(false);
    }
  };

  const getEstadoColor = (estado: string) => {
    switch (estado) {
      case 'disponible':
        return { bg: 'bg-green-100', border: 'border-green-300', text: 'text-green-700' };
      case 'ocupada':
        return { bg: 'bg-red-100', border: 'border-red-300', text: 'text-red-700' };
      case 'reservada':
        return { bg: 'bg-blue-100', border: 'border-blue-300', text: 'text-blue-700' };
      default:
        return { bg: 'bg-gray-100', border: 'border-gray-300', text: 'text-gray-700' };
    }
  };

  const getBadgeVariant = (estado: string) => {
    switch (estado) {
      case 'disponible':
        return 'success';
      case 'ocupada':
        return 'destructive';
      case 'reservada':
        return 'info';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-red-500 bg-red-50 border border-red-200 rounded-lg">
        {error}
      </div>
    );
  }

  return (
    <>
      <div className="space-y-4">
        <div className="flex items-center justify-between bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="text-sm font-medium text-gray-700">
              Total: <span className="font-bold text-gray-900">{mesas.length}</span> mesas
            </div>

            {/* 🔴 INDICADOR DE CONEXIÓN EN TIEMPO REAL */}
            <div className="flex items-center gap-2 text-xs">
              <div className={`h-2 w-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`} />
              <span className={isConnected ? 'text-green-700' : 'text-gray-500'}>
                {isConnected ? 'Tiempo real activo' : 'Conectando...'}
              </span>
            </div>
          </div>

          {/* Botón de actualización manual como fallback */}
          <Button
            variant="outline"
            size="sm"
            onClick={loadMesas}
            disabled={loading}
            className="border-gray-300"
            title="Actualizar manualmente (útil si la conexión en tiempo real falla)"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Actualizar
          </Button>
        </div>

        {/* Grid de Mesas */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {mesas.map((mesa) => {
            const colors = getEstadoColor(mesa.estado);
            return (
              <Card
                key={mesa.id_mesa}
                className={`cursor-pointer transition-all hover:shadow-lg hover:scale-[1.02] border-2 ${colors.border} bg-white`}
                onClick={() => handleMesaClick(mesa)}
              >
                <CardContent className="p-5">
                  <div className="flex items-start justify-between mb-4">
                    <div className={`p-3 ${colors.bg} rounded-lg shadow-sm`}>
                      <Table2 className={`h-6 w-6 ${colors.text}`} />
                    </div>
                    <Badge variant={getBadgeVariant(mesa.estado) as any} className="text-xs">
                      {mesa.estado}
                    </Badge>
                  </div>

                  <h3 className="text-lg font-bold text-gray-900 mb-2">
                    Mesa #{mesa.id_mesa}
                  </h3>

                  {/* Mostrar personas REALES detectadas por YOLO */}
                  <div className="flex items-center text-sm text-gray-600 mb-2">
                    <Users className="h-4 w-4 mr-1.5" />
                    <span className="font-medium">
                      {mesa.personas_actuales} {mesa.personas_actuales === 1 ? 'persona' : 'personas'}
                    </span>
                  </div>

                  {/* Mostrar capacidad de la mesa como info secundaria */}
                  {mesa.tipo_mesa && (
                    <div className="text-xs text-gray-500 mt-2 pt-2 border-t border-gray-100">
                      {mesa.tipo_mesa.descripcion} • Capacidad: {mesa.tipo_mesa.cantidad_sillas}
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>

        {mesas.length === 0 && (
          <div className="text-center py-12 text-muted-foreground">
            No hay mesas registradas
          </div>
        )}
      </div>

      {/* Dialog para cambiar estado */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="text-xl font-bold text-gray-900">
              Mesa #{selectedMesa?.id_mesa}
            </DialogTitle>
            <DialogDescription className="text-gray-600">
              Cambiar el estado de la mesa manualmente
            </DialogDescription>
          </DialogHeader>

          {selectedMesa && (
            <div className="space-y-4 py-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-800">
                  <span className="font-semibold">Estado actual:</span>{' '}
                  <Badge variant={getBadgeVariant(selectedMesa.estado) as any} className="ml-2">
                    {selectedMesa.estado}
                  </Badge>
                </p>
              </div>

              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 space-y-2">
                <p className="text-sm text-gray-900">
                  <span className="font-semibold">Personas detectadas:</span>{' '}
                  {selectedMesa.personas_actuales} {selectedMesa.personas_actuales === 1 ? 'persona' : 'personas'}
                </p>
                {selectedMesa.tipo_mesa && (
                  <>
                    <p className="text-sm text-gray-900">
                      <span className="font-semibold">Tipo:</span> {selectedMesa.tipo_mesa.descripcion}
                    </p>
                    <p className="text-sm text-gray-600">
                      <span className="font-semibold">Capacidad máxima:</span> {selectedMesa.tipo_mesa.cantidad_sillas} personas
                    </p>
                  </>
                )}
              </div>

              {/* Mostrar información de reservación si la mesa está reservada */}
              {selectedMesa.estado === 'reservada' && selectedMesa.reservacion_activa && (
                <div className="bg-blue-50 border border-blue-300 rounded-lg p-4">
                  <h3 className="text-sm font-bold text-blue-900 mb-3">Información de la Reservación</h3>
                  <div className="space-y-2">
                    <div>
                      <p className="text-xs text-blue-700 font-medium">Cliente:</p>
                      <p className="text-sm text-gray-900 font-semibold">
                        {selectedMesa.reservacion_activa.nombre} {selectedMesa.reservacion_activa.apellido}
                      </p>
                    </div>
                    {selectedMesa.reservacion_activa.telefono && (
                      <div>
                        <p className="text-xs text-blue-700 font-medium">Teléfono:</p>
                        <p className="text-sm text-gray-900">
                          {selectedMesa.reservacion_activa.telefono}
                        </p>
                      </div>
                    )}
                    <div>
                      <p className="text-xs text-blue-700 font-medium">Correo:</p>
                      <p className="text-sm text-gray-900">
                        {selectedMesa.reservacion_activa.correo}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-blue-700 font-medium">Personas:</p>
                      <p className="text-sm text-gray-900">
                        {selectedMesa.reservacion_activa.cantidad_personas}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-blue-700 font-medium">Hora:</p>
                      <p className="text-sm text-gray-900">
                        {selectedMesa.reservacion_activa.hora}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              <div className="space-y-3 pt-2">
                <p className="text-sm font-semibold text-gray-700">Cambiar estado a:</p>
                <div className="grid grid-cols-3 gap-3">
                  <Button
                    variant={selectedMesa.estado === 'disponible' ? 'default' : 'outline'}
                    onClick={() => handleUpdateEstado('disponible')}
                    disabled={updating || selectedMesa.estado === 'disponible'}
                    className={selectedMesa.estado === 'disponible' ? 'bg-green-600 hover:bg-green-700' : 'border-gray-300'}
                  >
                    {updating && selectedMesa.estado !== 'disponible' ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Disponible'}
                  </Button>
                  <Button
                    variant={selectedMesa.estado === 'ocupada' ? 'default' : 'outline'}
                    onClick={() => handleUpdateEstado('ocupada')}
                    disabled={updating || selectedMesa.estado === 'ocupada'}
                    className={selectedMesa.estado === 'ocupada' ? 'bg-red-600 hover:bg-red-700' : 'border-gray-300'}
                  >
                    {updating && selectedMesa.estado !== 'ocupada' ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Ocupada'}
                  </Button>
                  <Button
                    variant={selectedMesa.estado === 'reservada' ? 'default' : 'outline'}
                    onClick={() => handleUpdateEstado('reservada')}
                    disabled={updating || selectedMesa.estado === 'reservada'}
                    className={selectedMesa.estado === 'reservada' ? 'bg-blue-600 hover:bg-blue-700' : 'border-gray-300'}
                  >
                    {updating && selectedMesa.estado !== 'reservada' ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Reservada'}
                  </Button>
                </div>
              </div>
            </div>
          )}

          <DialogFooter className="bg-gray-50 px-6 py-4 -mx-6 -mb-6 mt-4">
            <Button
              variant="outline"
              onClick={() => {
                setDialogOpen(false);
                setSelectedMesa(null);
              }}
              disabled={updating}
              className="border-gray-300"
            >
              Cerrar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
