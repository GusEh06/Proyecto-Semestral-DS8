import { useEffect, useState } from 'react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select } from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';
import {
  getReservacionesAdmin,
  actualizarReservacion,
  eliminarReservacion,
  type ReservacionAdmin,
  ApiError,
} from '@/lib/api';
import { getToken } from '@/lib/auth';
import {
  Loader2,
  RefreshCw,
  Eye,
  Edit,
  Trash2,
  Filter,
  X,
} from 'lucide-react';

export default function ReservationsTable() {
  const [reservaciones, setReservaciones] = useState<ReservacionAdmin[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filtroEstado, setFiltroEstado] = useState<string>('');
  const [filtroFecha, setFiltroFecha] = useState<string>('');
  const [selectedReservacion, setSelectedReservacion] = useState<ReservacionAdmin | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [actionType, setActionType] = useState<'view' | 'edit' | 'delete'>('view');
  const [updating, setUpdating] = useState(false);
  const [nuevoEstado, setNuevoEstado] = useState<string>('');

  useEffect(() => {
    loadReservaciones();
    // Actualizar cada 30 segundos
    const interval = setInterval(loadReservaciones, 30000);
    return () => clearInterval(interval);
  }, [filtroEstado, filtroFecha]);

  const loadReservaciones = async () => {
    try {
      const token = getToken();
      if (!token) {
        window.location.href = '/admin/login';
        return;
      }

      const data = await getReservacionesAdmin(
        token,
        filtroEstado || undefined,
        filtroFecha || undefined
      );
      setReservaciones(data);
      setError(null);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Error al cargar las reservaciones');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleView = (reservacion: ReservacionAdmin) => {
    setSelectedReservacion(reservacion);
    setActionType('view');
    setDialogOpen(true);
  };

  const handleEdit = (reservacion: ReservacionAdmin) => {
    setSelectedReservacion(reservacion);
    setNuevoEstado(reservacion.estado);
    setActionType('edit');
    setDialogOpen(true);
  };

  const handleDelete = (reservacion: ReservacionAdmin) => {
    setSelectedReservacion(reservacion);
    setActionType('delete');
    setDialogOpen(true);
  };

  const handleUpdateEstado = async () => {
    if (!selectedReservacion) return;

    setUpdating(true);
    try {
      const token = getToken();
      if (!token) {
        window.location.href = '/admin/login';
        return;
      }

      await actualizarReservacion(token, selectedReservacion.id_reserva, {
        estado: nuevoEstado,
      });
      await loadReservaciones();
      setDialogOpen(false);
      setSelectedReservacion(null);
    } catch (err) {
      if (err instanceof ApiError) {
        alert(err.message);
      } else {
        alert('Error al actualizar la reservación');
      }
    } finally {
      setUpdating(false);
    }
  };

  const handleConfirmDelete = async () => {
    if (!selectedReservacion) return;

    setUpdating(true);
    try {
      const token = getToken();
      if (!token) {
        window.location.href = '/admin/login';
        return;
      }

      await eliminarReservacion(token, selectedReservacion.id_reserva);
      await loadReservaciones();
      setDialogOpen(false);
      setSelectedReservacion(null);
    } catch (err) {
      if (err instanceof ApiError) {
        alert(err.message);
      } else {
        alert('Error al eliminar la reservación');
      }
    } finally {
      setUpdating(false);
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

  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), "d 'de' MMMM, yyyy", { locale: es });
    } catch {
      return dateString;
    }
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

  const clearFilters = () => {
    setFiltroEstado('');
    setFiltroFecha('');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <>
      <div className="space-y-4">
        {/* Filtros */}
        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-semibold text-gray-900 flex items-center">
              <Filter className="h-5 w-5 mr-2 text-blue-600" />
              Filtros
            </h3>
            {(filtroEstado || filtroFecha) && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearFilters}
                className="text-gray-600 hover:text-gray-900"
              >
                <X className="h-4 w-4 mr-1" />
                Limpiar filtros
              </Button>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="filtro-estado">Estado</Label>
              <select
                id="filtro-estado"
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                value={filtroEstado}
                onChange={(e) => setFiltroEstado(e.target.value)}
              >
                <option value="">Todos</option>
                <option value="pendiente">Pendiente</option>
                <option value="confirmada">Confirmada</option>
                <option value="cancelada">Cancelada</option>
                <option value="completada">Completada</option>
              </select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="filtro-fecha">Fecha</Label>
              <Input
                id="filtro-fecha"
                type="date"
                value={filtroFecha}
                onChange={(e) => setFiltroFecha(e.target.value)}
              />
            </div>

            <div className="flex items-end">
              <Button
                variant="outline"
                onClick={loadReservaciones}
                disabled={loading}
                className="w-full"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Actualizar
              </Button>
            </div>
          </div>
        </div>

        {error && (
          <div className="p-4 text-red-500 bg-red-50 border border-red-200 rounded-lg">
            {error}
          </div>
        )}

        {/* Tabla */}
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Cliente</TableHead>
                <TableHead>Contacto</TableHead>
                <TableHead>Fecha/Hora</TableHead>
                <TableHead>Personas</TableHead>
                <TableHead>Mesa</TableHead>
                <TableHead>Estado</TableHead>
                <TableHead className="text-right">Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {reservaciones.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center text-muted-foreground py-8">
                    No hay reservaciones que coincidan con los filtros
                  </TableCell>
                </TableRow>
              ) : (
                reservaciones.map((reservacion) => (
                  <TableRow key={reservacion.id_reserva}>
                    <TableCell className="font-medium">
                      #{reservacion.id_reserva}
                    </TableCell>
                    <TableCell>
                      {reservacion.nombre} {reservacion.apellido}
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        <div>{reservacion.correo}</div>
                        <div className="text-muted-foreground">
                          {reservacion.telefono}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        <div>{formatDate(reservacion.fecha)}</div>
                        <div className="text-muted-foreground">
                          {formatTime(reservacion.hora)}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>{reservacion.cantidad_personas}</TableCell>
                    <TableCell>
                      {reservacion.id_mesa ? `Mesa #${reservacion.id_mesa}` : '-'}
                    </TableCell>
                    <TableCell>
                      <Badge variant={getBadgeVariant(reservacion.estado) as any}>
                        {reservacion.estado}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleView(reservacion)}
                          title="Ver detalles"
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleEdit(reservacion)}
                          title="Editar estado"
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleDelete(reservacion)}
                          title="Eliminar"
                        >
                          <Trash2 className="h-4 w-4 text-red-500" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>

        <div className="text-sm text-muted-foreground">
          Mostrando {reservaciones.length} reservaciones
        </div>
      </div>

      {/* Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          {actionType === 'view' && selectedReservacion && (
            <>
              <DialogHeader>
                <DialogTitle className="text-xl font-bold text-gray-900">
                  Detalles de Reservación #{selectedReservacion.id_reserva}
                </DialogTitle>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-xs font-semibold text-gray-500 uppercase">Cliente</Label>
                    <p className="text-sm font-medium text-gray-900 mt-1">
                      {selectedReservacion.nombre} {selectedReservacion.apellido}
                    </p>
                  </div>
                  <div>
                    <Label className="text-xs font-semibold text-gray-500 uppercase">Estado</Label>
                    <div className="mt-1">
                      <Badge variant={getBadgeVariant(selectedReservacion.estado) as any}>
                        {selectedReservacion.estado}
                      </Badge>
                    </div>
                  </div>
                </div>
                <div className="pt-2 border-t border-gray-100">
                  <Label className="text-xs font-semibold text-gray-500 uppercase">Correo</Label>
                  <p className="text-sm text-gray-700 mt-1">{selectedReservacion.correo}</p>
                </div>
                <div>
                  <Label className="text-xs font-semibold text-gray-500 uppercase">Teléfono</Label>
                  <p className="text-sm text-gray-700 mt-1">{selectedReservacion.telefono}</p>
                </div>
                <div className="grid grid-cols-2 gap-4 pt-2 border-t border-gray-100">
                  <div>
                    <Label className="text-xs font-semibold text-gray-500 uppercase">Fecha</Label>
                    <p className="text-sm font-medium text-gray-900 mt-1">{formatDate(selectedReservacion.fecha)}</p>
                  </div>
                  <div>
                    <Label className="text-xs font-semibold text-gray-500 uppercase">Hora</Label>
                    <p className="text-sm font-medium text-gray-900 mt-1">{formatTime(selectedReservacion.hora)}</p>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-xs font-semibold text-gray-500 uppercase">Personas</Label>
                    <p className="text-sm font-medium text-gray-900 mt-1">{selectedReservacion.cantidad_personas}</p>
                  </div>
                  <div>
                    <Label className="text-xs font-semibold text-gray-500 uppercase">Mesa</Label>
                    <p className="text-sm font-medium text-gray-900 mt-1">
                      {selectedReservacion.id_mesa ? `Mesa #${selectedReservacion.id_mesa}` : 'Sin asignar'}
                    </p>
                  </div>
                </div>
              </div>
              <DialogFooter className="bg-gray-50 px-6 py-4 -mx-6 -mb-6 mt-4">
                <Button variant="outline" onClick={() => setDialogOpen(false)} className="border-gray-300">
                  Cerrar
                </Button>
              </DialogFooter>
            </>
          )}

          {actionType === 'edit' && selectedReservacion && (
            <>
              <DialogHeader>
                <DialogTitle className="text-xl font-bold text-gray-900">Cambiar Estado de Reservación</DialogTitle>
                <DialogDescription className="text-gray-600">
                  Reservación #{selectedReservacion.id_reserva} - {selectedReservacion.nombre} {selectedReservacion.apellido}
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-blue-800">
                    <span className="font-semibold">Estado actual:</span>{' '}
                    <Badge variant={getBadgeVariant(selectedReservacion.estado) as any} className="ml-2">
                      {selectedReservacion.estado}
                    </Badge>
                  </p>
                </div>
                <div>
                  <Label htmlFor="nuevo-estado" className="text-sm font-semibold text-gray-700">Nuevo Estado</Label>
                  <select
                    id="nuevo-estado"
                    className="w-full px-3 py-2.5 border border-gray-300 rounded-lg mt-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    value={nuevoEstado}
                    onChange={(e) => setNuevoEstado(e.target.value)}
                  >
                    <option value="pendiente">Pendiente</option>
                    <option value="confirmada">Confirmada</option>
                    <option value="cancelada">Cancelada</option>
                    <option value="completada">Completada</option>
                  </select>
                </div>
              </div>
              <DialogFooter className="bg-gray-50 px-6 py-4 -mx-6 -mb-6 mt-4 gap-2">
                <Button
                  variant="outline"
                  onClick={() => setDialogOpen(false)}
                  disabled={updating}
                  className="border-gray-300"
                >
                  Cancelar
                </Button>
                <Button
                  onClick={handleUpdateEstado}
                  disabled={updating || nuevoEstado === selectedReservacion.estado}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {updating ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Actualizando...
                    </>
                  ) : (
                    'Guardar Cambios'
                  )}
                </Button>
              </DialogFooter>
            </>
          )}

          {actionType === 'delete' && selectedReservacion && (
            <>
              <DialogHeader>
                <DialogTitle className="text-xl font-bold text-gray-900">Eliminar Reservación</DialogTitle>
                <DialogDescription className="text-gray-600">
                  ¿Estás seguro de que deseas eliminar esta reservación? Esta acción no se puede deshacer.
                </DialogDescription>
              </DialogHeader>
              <div className="py-4">
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 space-y-2">
                  <p className="text-sm font-semibold text-red-900">
                    Reservación #{selectedReservacion.id_reserva}
                  </p>
                  <p className="text-sm text-red-800">
                    <span className="font-medium">Cliente:</span> {selectedReservacion.nombre} {selectedReservacion.apellido}
                  </p>
                  <p className="text-sm text-red-800">
                    <span className="font-medium">Fecha:</span> {formatDate(selectedReservacion.fecha)} - {formatTime(selectedReservacion.hora)}
                  </p>
                </div>
              </div>
              <DialogFooter className="bg-gray-50 px-6 py-4 -mx-6 -mb-6 mt-4 gap-2">
                <Button
                  variant="outline"
                  onClick={() => setDialogOpen(false)}
                  disabled={updating}
                  className="border-gray-300"
                >
                  Cancelar
                </Button>
                <Button
                  variant="destructive"
                  onClick={handleConfirmDelete}
                  disabled={updating}
                  className="bg-red-600 hover:bg-red-700"
                >
                  {updating ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Eliminando...
                    </>
                  ) : (
                    'Eliminar'
                  )}
                </Button>
              </DialogFooter>
            </>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}
