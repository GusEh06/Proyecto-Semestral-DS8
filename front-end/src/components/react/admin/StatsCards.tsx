import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { getEstadisticasDashboard, type EstadisticasDashboard, ApiError } from '@/lib/api';
import { getToken } from '@/lib/auth';
import {
  Calendar,
  CheckCircle,
  Clock,
  Table2,
  TrendingUp,
  Loader2,
} from 'lucide-react';

export default function StatsCards() {
  const [stats, setStats] = useState<EstadisticasDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStats();
    // Actualizar cada 30 segundos
    const interval = setInterval(loadStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadStats = async () => {
    try {
      const token = getToken();
      if (!token) {
        window.location.href = '/admin/login';
        return;
      }

      const data = await getEstadisticasDashboard(token);
      setStats(data);
      setError(null);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Error al cargar las estadísticas');
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="p-4 text-red-500 bg-red-50 border border-red-200 rounded-lg">
        {error || 'Error al cargar las estadísticas'}
      </div>
    );
  }

  const mainStats = [
    {
      title: 'Total Reservaciones',
      value: stats.total_reservaciones,
      icon: Calendar,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      title: 'Reservaciones Hoy',
      value: stats.reservaciones_hoy,
      icon: TrendingUp,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      title: 'Pendientes',
      value: stats.reservaciones_pendientes,
      icon: Clock,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100',
    },
    {
      title: 'Confirmadas Hoy',
      value: stats.reservaciones_confirmadas_hoy,
      icon: CheckCircle,
      color: 'text-emerald-600',
      bgColor: 'bg-emerald-100',
    },
  ];

  const mesasStats = [
    {
      title: 'Total Mesas',
      value: stats.total_mesas,
      subtitle: 'En el restaurante',
    },
    {
      title: 'Disponibles',
      value: stats.mesas_disponibles,
      subtitle: 'Listas para usar',
      color: 'text-green-600',
    },
    {
      title: 'Ocupadas',
      value: stats.mesas_ocupadas,
      subtitle: 'En uso',
      color: 'text-red-600',
    },
    {
      title: 'Reservadas',
      value: stats.mesas_reservadas,
      subtitle: 'Próximas',
      color: 'text-blue-600',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Main Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {mainStats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title} className="border-gray-200 shadow-sm hover:shadow-md transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">
                  {stat.title}
                </CardTitle>
                <div className={`${stat.bgColor} p-2.5 rounded-lg shadow-sm`}>
                  <Icon className={`h-5 w-5 ${stat.color}`} />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-gray-900">{stat.value}</div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Mesas Stats */}
      <Card className="border-gray-200 shadow-sm">
        <CardHeader className="bg-gradient-to-r from-gray-50 to-white">
          <CardTitle className="flex items-center text-gray-900">
            <div className="p-2 bg-blue-100 rounded-lg mr-3">
              <Table2 className="h-5 w-5 text-blue-600" />
            </div>
            Estado de Mesas
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {mesasStats.map((stat) => (
              <div key={stat.title} className="text-center">
                <div className={`text-3xl font-bold ${stat.color || 'text-gray-900'}`}>
                  {stat.value}
                </div>
                <div className="text-sm font-semibold text-gray-700 mt-2">
                  {stat.title}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {stat.subtitle}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Reservaciones por Estado */}
      <Card className="border-gray-200 shadow-sm">
        <CardHeader className="bg-gradient-to-r from-gray-50 to-white">
          <CardTitle className="text-gray-900">Reservaciones por Estado</CardTitle>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="space-y-4">
            {Object.entries(stats.reservaciones_por_estado || {}).map(([estado, count]) => {
              const colors = {
                pendiente: { bg: 'bg-yellow-100', bar: 'bg-yellow-500', text: 'text-yellow-700' },
                confirmada: { bg: 'bg-green-100', bar: 'bg-green-500', text: 'text-green-700' },
                cancelada: { bg: 'bg-red-100', bar: 'bg-red-500', text: 'text-red-700' },
                completada: { bg: 'bg-blue-100', bar: 'bg-blue-500', text: 'text-blue-700' },
              };

              const color = colors[estado as keyof typeof colors];
              const percentage = stats.total_reservaciones > 0
                ? (count / stats.total_reservaciones) * 100
                : 0;

              return (
                <div key={estado}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-semibold text-gray-700 capitalize">{estado}</span>
                    <span className={`text-sm font-bold ${color.text}`}>
                      {count} ({percentage.toFixed(0)}%)
                    </span>
                  </div>
                  <div className={`w-full ${color.bg} rounded-full h-3 shadow-inner`}>
                    <div
                      className={`${color.bar} h-3 rounded-full transition-all duration-500 shadow-sm`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
