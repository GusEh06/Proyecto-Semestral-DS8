import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import StatsCards from './StatsCards';
import MesasGrid from './MesasGrid';
import ReservationsTable from './ReservationsTable';
import {
  getReservacionesAdmin,
  type ReservacionAdmin,
  ApiError,
} from '@/lib/api';
import { getToken } from '@/lib/auth';
import {
  Calendar,
  Clock,
  Wifi,
  WifiOff,
  AlertCircle,
  TrendingUp,
  Loader2,
} from 'lucide-react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

export default function Dashboard() {
  const [reservacionesHoy, setReservacionesHoy] = useState<ReservacionAdmin[]>([]);
  const [loading, setLoading] = useState(true);
  const [edgeStatus, setEdgeStatus] = useState<'online' | 'offline' | 'unknown'>('unknown');

  useEffect(() => {
    loadReservacionesHoy();
    checkEdgeStatus();

    // Actualizar cada 10 segundos
    const interval = setInterval(() => {
      loadReservacionesHoy();
      checkEdgeStatus();
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  const loadReservacionesHoy = async () => {
    try {
      const token = getToken();
      if (!token) return;

      const hoy = new Date().toISOString().split('T')[0];
      const data = await getReservacionesAdmin(token, undefined, hoy);

      // Ordenar por hora
      const sorted = data.sort((a, b) => a.hora.localeCompare(b.hora));
      setReservacionesHoy(sorted);
    } catch (err) {
      console.error('Error cargando reservaciones de hoy:', err);
    } finally {
      setLoading(false);
    }
  };

  const checkEdgeStatus = () => {
    // Simulación - en producción esto vendría del backend
    // Por ahora asumimos online si hay actualizaciones recientes
    setEdgeStatus('online');
  };

  const formatTime = (timeString: string) => {
    try {
      const [hours, minutes] = timeString.split(':');
      const hour = parseInt(hours);
      const ampm = hour >= 12 ? 'PM' : 'AM';
      const displayHour = hour % 12 || 12;
      return `${displayHour}:${minutes} ${ampm}`;
    } catch {
      return timeString;
    }
  };

  const getBadgeVariant = (estado: string) => {
    switch (estado) {
      case 'pendiente':
        return 'warning';
      case 'confirmada':
        return 'success';
      case 'cancelada':
        return 'destructive';
      case 'completada':
        return 'info';
      default:
        return 'default';
    }
  };

  const getProximasReservas = () => {
    const ahora = new Date();
    const horaActual = `${ahora.getHours().toString().padStart(2, '0')}:${ahora.getMinutes().toString().padStart(2, '0')}`;

    return reservacionesHoy
      .filter(r => r.hora >= horaActual && r.estado !== 'cancelada')
      .slice(0, 5);
  };

  return (
    <div className="space-y-6">
      {/* Info Bar */}
      <div className="flex items-center justify-between bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
        <div>
          <p className="text-gray-600 text-sm">
            {format(new Date(), "EEEE, d 'de' MMMM yyyy", { locale: es })}
          </p>
        </div>

        {/* Estado del Edge Device */}
        <div className="flex items-center gap-3 border-l border-gray-200 pl-4">
          <div className="relative">
            {edgeStatus === 'online' ? (
              <>
                <Wifi className="h-5 w-5 text-green-600" />
                <span className="absolute -top-1 -right-1 h-2.5 w-2.5 bg-green-500 rounded-full animate-pulse"></span>
              </>
            ) : edgeStatus === 'offline' ? (
              <WifiOff className="h-5 w-5 text-red-600" />
            ) : (
              <Loader2 className="h-5 w-5 text-gray-400 animate-spin" />
            )}
          </div>
          <div>
            <p className="text-xs text-gray-600 font-medium">Dispositivo Edge</p>
            <p className={`text-sm font-semibold ${
              edgeStatus === 'online' ? 'text-green-600' :
              edgeStatus === 'offline' ? 'text-red-600' :
              'text-gray-600'
            }`}>
              {edgeStatus === 'online' ? 'Conectado' :
               edgeStatus === 'offline' ? 'Desconectado' :
               'Verificando...'}
            </p>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <StatsCards />

      {/* Row: Próximas Reservas + Alertas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Próximas Reservas de Hoy */}
        <Card className="border-gray-200 shadow-sm">
          <CardHeader className="bg-gradient-to-r from-blue-50 to-white">
            <CardTitle className="flex items-center text-gray-900">
              <div className="p-2 bg-blue-100 rounded-lg mr-3">
                <Calendar className="h-5 w-5 text-blue-600" />
              </div>
              Próximas Reservas de Hoy
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            {loading ? (
              <div className="flex items-center justify-center h-40">
                <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
              </div>
            ) : getProximasReservas().length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Clock className="h-12 w-12 mx-auto mb-3 text-gray-400" />
                <p>No hay reservas próximas para hoy</p>
              </div>
            ) : (
              <div className="space-y-3">
                {getProximasReservas().map((reserva) => (
                  <div
                    key={reserva.id_reserva}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200 hover:shadow-sm transition-shadow"
                  >
                    <div className="flex items-center gap-3">
                      <div className="bg-blue-100 p-2 rounded-lg">
                        <Clock className="h-4 w-4 text-blue-600" />
                      </div>
                      <div>
                        <p className="font-semibold text-gray-900 text-sm">
                          {reserva.nombre} {reserva.apellido}
                        </p>
                        <p className="text-xs text-gray-600">
                          {reserva.cantidad_personas} {reserva.cantidad_personas === 1 ? 'persona' : 'personas'}
                          {reserva.id_mesa && ` • Mesa #${reserva.id_mesa}`}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-bold text-blue-600">
                        {formatTime(reserva.hora)}
                      </p>
                      <Badge variant={getBadgeVariant(reserva.estado) as any} className="text-xs mt-1">
                        {reserva.estado}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Alertas y Notificaciones */}
        <Card className="border-gray-200 shadow-sm">
          <CardHeader className="bg-gradient-to-r from-yellow-50 to-white">
            <CardTitle className="flex items-center text-gray-900">
              <div className="p-2 bg-yellow-100 rounded-lg mr-3">
                <AlertCircle className="h-5 w-5 text-yellow-600" />
              </div>
              Centro de Notificaciones
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="space-y-3">
              {/* Notificación: Edge Device Status */}
              <div className={`p-3 rounded-lg border ${
                edgeStatus === 'online'
                  ? 'bg-green-50 border-green-200'
                  : 'bg-red-50 border-red-200'
              }`}>
                <div className="flex items-start gap-2">
                  {edgeStatus === 'online' ? (
                    <TrendingUp className="h-4 w-4 text-green-600 mt-0.5" />
                  ) : (
                    <AlertCircle className="h-4 w-4 text-red-600 mt-0.5" />
                  )}
                  <div>
                    <p className={`text-sm font-semibold ${
                      edgeStatus === 'online' ? 'text-green-900' : 'text-red-900'
                    }`}>
                      {edgeStatus === 'online'
                        ? 'Sistema de Detección Activo'
                        : 'Sistema de Detección Desconectado'}
                    </p>
                    <p className={`text-xs ${
                      edgeStatus === 'online' ? 'text-green-700' : 'text-red-700'
                    } mt-0.5`}>
                      {edgeStatus === 'online'
                        ? 'Las mesas se están actualizando automáticamente en tiempo real.'
                        : 'El dispositivo Edge no está enviando actualizaciones.'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Notificación: Reservas de Hoy */}
              {reservacionesHoy.length > 0 && (
                <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-start gap-2">
                    <Calendar className="h-4 w-4 text-blue-600 mt-0.5" />
                    <div>
                      <p className="text-sm font-semibold text-blue-900">
                        {reservacionesHoy.length} {reservacionesHoy.length === 1 ? 'Reserva' : 'Reservas'} para Hoy
                      </p>
                      <p className="text-xs text-blue-700 mt-0.5">
                        {reservacionesHoy.filter(r => r.estado === 'confirmada').length} confirmadas, {' '}
                        {reservacionesHoy.filter(r => r.estado === 'pendiente').length} pendientes
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Mensaje informativo si no hay alertas */}
              {reservacionesHoy.length === 0 && edgeStatus === 'online' && (
                <div className="text-center py-6 text-gray-500">
                  <AlertCircle className="h-10 w-10 mx-auto mb-2 text-gray-400" />
                  <p className="text-sm">Todo está funcionando correctamente</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Vista de Mesas en Tiempo Real */}
      <Card className="border-gray-200 shadow-sm">
        <CardHeader className="bg-gradient-to-r from-gray-50 to-white">
          <CardTitle className="text-gray-900">
            Estado de Mesas en Tiempo Real
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-6">
          <MesasGrid />
        </CardContent>
      </Card>

      {/* Tabla de Todas las Reservaciones */}
      <Card className="border-gray-200 shadow-sm">
        <CardHeader className="bg-gradient-to-r from-gray-50 to-white">
          <CardTitle className="text-gray-900">
            Gestión de Reservaciones
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-6">
          <ReservationsTable />
        </CardContent>
      </Card>
    </div>
  );
}
