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

  useEffect(() => {
    loadMesas();
    // Actualizar cada 10 segundos
    const interval = setInterval(loadMesas, 10000);
    return () => clearInterval(interval);
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
          <div className="text-sm font-medium text-gray-700">
            Total: <span className="font-bold text-gray-900">{mesas.length}</span> mesas
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={loadMesas}
            disabled={loading}
            className="border-gray-300"
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
                    Mesa #{mesa.numero_mesa || mesa.id_mesa}
                  </h3>

                  {mesa.tipo_mesa && (
                    <div className="flex items-center text-sm text-gray-600 mb-2">
                      <Users className="h-4 w-4 mr-1.5" />
                      <span className="font-medium">{mesa.tipo_mesa.cantidad_sillas} personas</span>
                    </div>
                  )}

                  {mesa.tipo_mesa?.descripcion && (
                    <div className="text-xs text-gray-500 mt-2 pt-2 border-t border-gray-100">
                      {mesa.tipo_mesa.descripcion}
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
              Mesa #{selectedMesa?.numero_mesa || selectedMesa?.id_mesa}
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

              {selectedMesa.tipo_mesa && (
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <p className="text-sm font-semibold text-gray-900">
                    {selectedMesa.tipo_mesa.descripcion}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    Capacidad: {selectedMesa.tipo_mesa.cantidad_sillas} personas
                  </p>
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
