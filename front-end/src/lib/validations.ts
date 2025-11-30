import { z } from "zod"

export const reservationSchema = z.object({
  nombre: z.string().min(2, {
    message: "El nombre debe tener al menos 2 caracteres",
  }).max(100, {
    message: "El nombre no puede exceder 100 caracteres",
  }),
  apellido: z.string().min(2, {
    message: "El apellido debe tener al menos 2 caracteres",
  }).max(100, {
    message: "El apellido no puede exceder 100 caracteres",
  }),
  email: z.string().email({
    message: "Por favor ingresa un email válido",
  }),
  telefono: z.string().min(7, {
    message: "El teléfono debe tener al menos 7 dígitos",
  }).max(15, {
    message: "El teléfono no puede exceder 15 dígitos",
  }),
  personas: z.string().min(1, {
    message: "Por favor indica el número de personas",
  }),
  fecha: z.date({
    required_error: "Por favor selecciona una fecha",
  }),
  hora: z.string().min(1, {
    message: "Por favor selecciona una hora",
  }),
})

export type ReservationFormData = z.infer<typeof reservationSchema>
