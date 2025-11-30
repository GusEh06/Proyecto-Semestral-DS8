import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { reservationSchema, type ReservationFormData } from '@/lib/validations'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'

export function ReservationForm() {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitStatus, setSubmitStatus] = useState<{
    type: 'success' | 'error' | null
    message: string
  }>({ type: null, message: '' })

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ReservationFormData>({
    resolver: zodResolver(reservationSchema),
  })

  const onSubmit = async (data: ReservationFormData) => {
    setIsSubmitting(true)
    setSubmitStatus({ type: null, message: '' })

    try {
      // TODO: Aquí se conectará con la API
      // Por ahora simulamos una llamada a la API
      console.log('Datos de reserva:', data)

      // Simulación de llamada API
      await new Promise((resolve) => setTimeout(resolve, 1500))

      // Ejemplo de cómo se conectará a la API:
      // const response = await fetch('/api/reservations', {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //   },
      //   body: JSON.stringify(data),
      // })
      //
      // if (!response.ok) {
      //   throw new Error('Error al crear la reserva')
      // }
      //
      // const result = await response.json()

      setSubmitStatus({
        type: 'success',
        message: 'Reserva creada exitosamente. Te enviaremos un correo de confirmación.',
      })
      reset()
    } catch (error) {
      setSubmitStatus({
        type: 'error',
        message: 'Hubo un error al procesar tu reserva. Por favor intenta nuevamente.',
      })
      console.error('Error:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  // Generar horarios disponibles
  const timeSlots = []
  for (let hour = 8; hour <= 20; hour++) {
    timeSlots.push(`${hour.toString().padStart(2, '0')}:00`)
    if (hour < 20) {
      timeSlots.push(`${hour.toString().padStart(2, '0')}:30`)
    }
  }

  // Fecha mínima (hoy)
  const today = new Date().toISOString().split('T')[0]

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="text-2xl">Nueva Reserva</CardTitle>
        <CardDescription>
          Completa el formulario para hacer tu reserva
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Información Personal */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Información Personal</h3>

            <div className="space-y-2">
              <Label htmlFor="nombre">Nombre Completo *</Label>
              <Input
                id="nombre"
                placeholder="Juan Pérez"
                {...register('nombre')}
                className={errors.nombre ? 'border-destructive' : ''}
              />
              {errors.nombre && (
                <p className="text-sm text-destructive">{errors.nombre.message}</p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email *</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="juan@ejemplo.com"
                  {...register('email')}
                  className={errors.email ? 'border-destructive' : ''}
                />
                {errors.email && (
                  <p className="text-sm text-destructive">{errors.email.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="telefono">Teléfono *</Label>
                <Input
                  id="telefono"
                  type="tel"
                  placeholder="+507 6000-0000"
                  {...register('telefono')}
                  className={errors.telefono ? 'border-destructive' : ''}
                />
                {errors.telefono && (
                  <p className="text-sm text-destructive">{errors.telefono.message}</p>
                )}
              </div>
            </div>
          </div>

          {/* Detalles de la Reserva */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Detalles de la Reserva</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="fecha">Fecha *</Label>
                <Input
                  id="fecha"
                  type="date"
                  min={today}
                  {...register('fecha')}
                  className={errors.fecha ? 'border-destructive' : ''}
                />
                {errors.fecha && (
                  <p className="text-sm text-destructive">{errors.fecha.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="hora">Hora *</Label>
                <Select
                  id="hora"
                  {...register('hora')}
                  className={errors.hora ? 'border-destructive' : ''}
                >
                  <option value="">Selecciona una hora</option>
                  {timeSlots.map((time) => (
                    <option key={time} value={time}>
                      {time}
                    </option>
                  ))}
                </Select>
                {errors.hora && (
                  <p className="text-sm text-destructive">{errors.hora.message}</p>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="servicio">Servicio *</Label>
                <Select
                  id="servicio"
                  {...register('servicio')}
                  className={errors.servicio ? 'border-destructive' : ''}
                >
                  <option value="">Selecciona un servicio</option>
                  <option value="cita">Reserva de Cita</option>
                  <option value="espacio">Reserva de Espacio</option>
                  <option value="evento">Evento Grupal</option>
                  <option value="premium">Servicio Premium</option>
                </Select>
                {errors.servicio && (
                  <p className="text-sm text-destructive">{errors.servicio.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="personas">Número de Personas *</Label>
                <Select
                  id="personas"
                  {...register('personas')}
                  className={errors.personas ? 'border-destructive' : ''}
                >
                  <option value="">Selecciona</option>
                  <option value="1">1 persona</option>
                  <option value="2">2 personas</option>
                  <option value="3">3 personas</option>
                  <option value="4">4 personas</option>
                  <option value="5">5 personas</option>
                  <option value="6+">6 o más personas</option>
                </Select>
                {errors.personas && (
                  <p className="text-sm text-destructive">{errors.personas.message}</p>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="notas">Notas Adicionales (Opcional)</Label>
              <Textarea
                id="notas"
                placeholder="Alguna solicitud especial o información adicional..."
                {...register('notas')}
                className={errors.notas ? 'border-destructive' : ''}
              />
              {errors.notas && (
                <p className="text-sm text-destructive">{errors.notas.message}</p>
              )}
            </div>
          </div>

          {/* Submit Status Messages */}
          {submitStatus.type && (
            <div
              className={`p-4 rounded-md ${
                submitStatus.type === 'success'
                  ? 'bg-green-50 text-green-800 border border-green-200'
                  : 'bg-red-50 text-red-800 border border-red-200'
              }`}
            >
              {submitStatus.message}
            </div>
          )}

          {/* Submit Button */}
          <Button
            type="submit"
            className="w-full"
            disabled={isSubmitting}
            size="lg"
          >
            {isSubmitting ? 'Procesando...' : 'Confirmar Reserva'}
          </Button>

          <p className="text-sm text-muted-foreground text-center">
            Al confirmar, aceptas nuestros términos y condiciones
          </p>
        </form>
      </CardContent>
    </Card>
  )
}
