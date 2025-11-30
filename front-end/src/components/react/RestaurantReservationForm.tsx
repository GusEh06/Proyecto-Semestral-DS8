import { useState } from 'react'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { reservationSchema, type ReservationFormData } from '@/lib/validations'
import { crearReservacion, ApiError } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { DayPicker } from 'react-day-picker'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import 'react-day-picker/dist/style.css'

const TIME_SLOTS = [
  '12:00 PM', '12:30 PM', '1:00 PM', '1:30 PM',
  '2:00 PM', '2:30 PM', '3:00 PM', '3:30 PM',
  '4:00 PM', '4:30 PM', '5:00 PM', '5:30 PM',
  '6:00 PM', '6:30 PM'
]

// Función para convertir hora de formato 12h a 24h
function convertTo24Hour(time12h: string): string {
  const [time, modifier] = time12h.split(' ')
  let [hours, minutes] = time.split(':')

  if (hours === '12') {
    hours = '00'
  }

  if (modifier === 'PM') {
    hours = String(parseInt(hours, 10) + 12)
  }

  return `${hours.padStart(2, '0')}:${minutes}:00`
}

export function RestaurantReservationForm() {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitStatus, setSubmitStatus] = useState<{
    type: 'success' | 'error' | null
    message: string
  }>({ type: null, message: '' })

  const {
    register,
    handleSubmit,
    control,
    watch,
    formState: { errors },
    reset,
  } = useForm<ReservationFormData>({
    resolver: zodResolver(reservationSchema),
  })

  const selectedDate = watch('fecha')
  const selectedTime = watch('hora')

  const onSubmit = async (data: ReservationFormData) => {
    setIsSubmitting(true)
    setSubmitStatus({ type: null, message: '' })

    try {
      // Preparar datos para enviar al backend
      const reservacionData = {
        nombre: data.nombre,
        apellido: data.apellido,
        correo: data.email,
        telefono: data.telefono,
        cantidad_personas: parseInt(data.personas),
        fecha: format(data.fecha, 'yyyy-MM-dd'),
        hora: convertTo24Hour(data.hora),
      }

      console.log('Enviando reserva:', reservacionData)

      // Llamar a la API
      const response = await crearReservacion(reservacionData)

      console.log('Respuesta de la API:', response)

      setSubmitStatus({
        type: 'success',
        message: `¡Reserva confirmada! Tu número de reserva es #${response.id_reserva}. Te enviaremos un correo de confirmación a ${response.correo}.`,
      })
      reset()
    } catch (error) {
      console.error('Error:', error)

      let errorMessage = 'Hubo un error al procesar tu reserva. Por favor intenta nuevamente.'

      if (error instanceof ApiError) {
        errorMessage = error.message
      }

      setSubmitStatus({
        type: 'error',
        message: errorMessage,
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="w-full max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-2">Completa tu Reserva</h2>
        <p className="text-sm text-red-600">Todos los campos son obligatorios</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Nombre y Apellido */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="nombre" className="text-blue-600">Nombre</Label>
            <Input
              id="nombre"
              placeholder="Ingrese su nombre"
              {...register('nombre')}
              className={errors.nombre ? 'border-red-500' : ''}
            />
            {errors.nombre && (
              <p className="text-sm text-red-600">{errors.nombre.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="apellido" className="text-blue-600">Apellido</Label>
            <Input
              id="apellido"
              placeholder="Ingrese su apellido"
              {...register('apellido')}
              className={errors.apellido ? 'border-red-500' : ''}
            />
            {errors.apellido && (
              <p className="text-sm text-red-600">{errors.apellido.message}</p>
            )}
          </div>
        </div>

        {/* Email y Teléfono */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="email" className="text-blue-600">Correo Electrónico</Label>
            <Input
              id="email"
              type="email"
              placeholder="ejemplo@correo.com"
              {...register('email')}
              className={errors.email ? 'border-red-500' : ''}
            />
            {errors.email && (
              <p className="text-sm text-red-600">{errors.email.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="telefono" className="text-blue-600">Teléfono o Celular</Label>
            <Input
              id="telefono"
              type="tel"
              placeholder="+507 0000-0000"
              {...register('telefono')}
              className={errors.telefono ? 'border-red-500' : ''}
            />
            {errors.telefono && (
              <p className="text-sm text-red-600">{errors.telefono.message}</p>
            )}
          </div>
        </div>

        {/* Cantidad de Personas */}
        <div className="space-y-2">
          <Label htmlFor="personas" className="text-blue-600">Cantidad de Personas</Label>
          <Input
            id="personas"
            type="number"
            min="1"
            max="20"
            placeholder="2"
            {...register('personas')}
            className={errors.personas ? 'border-red-500' : ''}
          />
          {errors.personas && (
            <p className="text-sm text-red-600">{errors.personas.message}</p>
          )}
        </div>

        {/* Calendario */}
        <div className="space-y-2">
          <p className="text-center text-sm">
            Selecciona una fecha para consultar{' '}
            <span className="text-blue-600">disponibilidad del día</span>
          </p>
          <Controller
            control={control}
            name="fecha"
            render={({ field }) => (
              <div className="flex justify-center">
                <DayPicker
                  mode="single"
                  selected={field.value}
                  onSelect={field.onChange}
                  disabled={{ before: new Date() }}
                  locale={es}
                  className="border rounded-lg p-4"
                  classNames={{
                    day_selected: 'bg-blue-600 text-white hover:bg-blue-700',
                    day_today: 'font-bold text-blue-600',
                  }}
                />
              </div>
            )}
          />
          {errors.fecha && (
            <p className="text-sm text-red-600 text-center">{errors.fecha.message}</p>
          )}
        </div>

        {/* Selección de Hora */}
        {selectedDate && (
          <div className="space-y-3">
            <p className="text-center text-sm">
              Selecciona la hora para tu reserva
            </p>
            <Controller
              control={control}
              name="hora"
              render={({ field }) => (
                <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
                  {TIME_SLOTS.map((time) => (
                    <button
                      key={time}
                      type="button"
                      onClick={() => field.onChange(time)}
                      className={`
                        px-4 py-2 rounded border text-sm font-medium transition-colors
                        ${field.value === time
                          ? 'bg-blue-600 text-white border-blue-600'
                          : 'bg-white text-gray-700 border-gray-300 hover:border-blue-600'
                        }
                      `}
                    >
                      {time}
                    </button>
                  ))}
                </div>
              )}
            />
            {errors.hora && (
              <p className="text-sm text-red-600 text-center">{errors.hora.message}</p>
            )}
          </div>
        )}

        {/* Submit Status Messages */}
        {submitStatus.type && (
          <div
            className={`p-4 rounded-md text-center ${
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
          className="w-full bg-black text-white hover:bg-gray-800 h-12 text-base font-medium"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Procesando...' : 'Confirmar Reserva'}
        </Button>
      </form>
    </div>
  )
}
