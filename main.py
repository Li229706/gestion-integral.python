import logging
from abc import ABC, abstractmethod

# Configuración del archivo de logs (requisito de la guía)
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# ==========================================
# 1. EXCEPCIONES PERSONALIZADAS
# ==========================================
class ErrorSistemaFJ(Exception):
    """Clase base para excepciones personalizadas del sistema."""
    pass

class ClienteInvalidoError(ErrorSistemaFJ):
    """Se lanza cuando los datos del cliente no cumplen con las validaciones."""
    pass

class ServicioNoDisponibleError(ErrorSistemaFJ):
    """Se lanza cuando se intenta acceder o crear un servicio con parámetros inválidos."""
    pass

class ReservaInvalidaError(ErrorSistemaFJ):
    """Se lanza cuando una reserva no puede procesarse o confirmarse."""
    pass

# ==========================================
# 2. CLASE ABSTRACTA BASE Y CLASE CLIENTE
# ==========================================
class EntidadBase(ABC):
    """Clase abstracta que representa entidades generales del sistema."""
    @abstractmethod
    def obtener_detalles(self):
        pass

class Cliente(EntidadBase):
    def __init__(self, cedula, nombre, correo):
        self.cedula = cedula
        self.nombre = nombre
        self.correo = correo
        self.validar_datos()

    def validar_datos(self):
        # Validaciones estrictas
        if not str(self.cedula).isdigit() or len(str(self.cedula)) < 6:
            logging.error(f"Intento de registro con cédula inválida: {self.cedula}")
            raise ClienteInvalidoError(f"Cédula inválida '{self.cedula}'. Debe ser numérica y tener al menos 6 dígitos.")
        if "@" not in self.correo or "." not in self.correo:
            logging.error(f"Intento de registro con correo inválido: {self.correo}")
            raise ClienteInvalidoError(f"Correo electrónico inválido: '{self.correo}'.")
        logging.info(f"Cliente registrado exitosamente: {self.nombre}")

    def obtener_detalles(self):
        return f"Cliente: {self.nombre} | Cédula: {self.cedula} | Correo: {self.correo}"

# ==========================================
# 3. CLASE ABSTRACTA SERVICIO Y DERIVADAS
# ==========================================
class Servicio(ABC):
    def __init__(self, id_servicio, costo_base):
        self.id_servicio = id_servicio
        self.costo_base = costo_base

    @abstractmethod
    def calcular_costo(self):
        pass

    @abstractmethod
    def obtener_detalles(self):
        pass

# Servicio 1: Reserva de Salas
class ReservaSalas(Servicio):
    def __init__(self, id_servicio, costo_base, capacidad):
        super().__init__(id_servicio, costo_base)
        self.capacidad = capacidad
        if capacidad <= 0:
            raise ServicioNoDisponibleError("La capacidad de la sala debe ser mayor a 0.")

    # Sobrecarga / variante del cálculo de costos
    def calcular_costo(self, descuento=0.0):
        try:
            if descuento < 0 or descuento > 1:
                raise ValueError("El descuento debe estar entre 0.0 y 1.0")
            costo_final = self.costo_base * (1 - descuento)
            return costo_final
        except Exception as e:
            logging.error(f"Error calculando costo en ReservaSalas: {e}")
            raise

    def obtener_detalles(self):
        return f"[Sala] ID: {self.id_servicio} | Capacidad: {self.capacidad} personas | Costo Base: ${self.costo_base}"

# Servicio 2: Alquiler de Equipos
class AlquilerEquipos(Servicio):
    def __init__(self, id_servicio, costo_base, horas):
        super().__init__(id_servicio, costo_base)
        self.horas = horas
        if horas <= 0:
            raise ServicioNoDisponibleError("Las horas de alquiler deben ser mayores a 0.")

    def calcular_costo(self, impuesto=1.19):
        return self.costo_base * self.horas * impuesto

    def obtener_detalles(self):
        return f"[Equipo] ID: {self.id_servicio} | Horas: {self.horas} | Costo Base/Hora: ${self.costo_base}"

# Servicio 3: Asesorías Especializadas
class AsesoriasEspecializadas(Servicio):
    def __init__(self, id_servicio, costo_base, area):
        super().__init__(id_servicio, costo_base)
        self.area = area
        if not area:
            raise ServicioNoDisponibleError("El área de asesoría no puede estar vacía.")

    def calcular_costo(self, nivel_urgencia=1.0):
        return self.costo_base * nivel_urgencia

    def obtener_detalles(self):
        return f"[Asesoría] ID: {self.id_servicio} | Área: {self.area} | Costo Base: ${self.costo_base}"

# ==========================================
# 4. CLASE RESERVA
# ==========================================
class Reserva:
    def __init__(self, cliente, servicio, duracion_dias):
        self.cliente = cliente
        self.servicio = servicio
        self.duracion_dias = duracion_dias
        self.estado = "Pendiente"
        self.validar_reserva()

    def validar_reserva(self):
        if self.duracion_dias <= 0:
            logging.error("Intento de reserva con duración inválida.")
            raise ReservaInvalidaError("La duración de la reserva debe ser mayor a 0 días.")
        self.estado = "Confirmada"
        logging.info(f"Reserva confirmada con éxito para el cliente {self.cliente.nombre}.")

    def procesar_pago(self):
        try:
            # Uso de try/except/else/finally avanzado
            total = self.servicio.calcular_costo()
            print(f" -> Procesando pago de la reserva... Total a pagar: ${total:.2f}")
        except Exception as e:
            logging.error(f"Fallo en el procesamiento del pago: {e}")
            raise ReservaInvalidaError("No se pudo procesar el pago debido a un cálculo inconsistente.") from e
        else:
            print(" -> ¡Pago procesado y aprobado exitosamente!")
        finally:
            print(" -> [LOG INTERNO] Transacción de pago finalizada.\n")

# ==========================================
# 5. SIMULACIÓN DE 10 OPERACIONES (Válidas e Inválidas)
# ==========================================
def ejecutar_simulacion():
    print("==================================================")
    print(" INICIANDO SIMULACIÓN DE OPERACIONES - SOFTWARE FJ")
    print("==================================================\n")

    # Lista para almacenar operaciones exitosas en memoria
    clientes_bd = []
    servicios_bd = []
    reservas_bd = []

    operaciones = [
        # Opción 1: Registro de cliente válido
        lambda: clientes_bd.append(Cliente("10987654", "Camila Gómez", "camila@softwarefj.com")),
        # Opción 2: Registro de cliente INVÁLIDO (cédula con letras)
        lambda: Cliente("ABC12345", "Carlos Pérez", "carlos@mail.com"),
        # Opción 3: Registro de cliente INVÁLIDO (correo sin @)
        lambda: Cliente("11223344", "Ana María", "correosinarp"),
        # Opción 4: Creación de servicio de sala válido
        lambda: servicios_bd.append(ReservaSalas("SALA-01", 150000, 20)),
        # Opción 5: Creación de servicio de equipo INVÁLIDO (horas negativas)
        lambda: AlquilerEquipos("EQ-01", 50000, -3),
        # Opción 6: Creación de asesoría válida
        lambda: servicios_bd.append(AsesoriasEspecializadas("ASES-01", 200000, "Arquitectura de Software")),
        # Opción 7: Reserva exitosa (Cliente 0 y Servicio 0)
        lambda: reservas_bd.append(Reserva(clientes_bd[0], servicios_bd[0], 2)),
        # Opción 8: Reserva INVÁLIDA (Duración de 0 días)
        lambda: Reserva(clientes_bd[0], servicios_bd[1], 0),
        # Opción 9: Procesar pago de una reserva existente
        lambda: reservas_bd[0].procesar_pago(),
        # Opción 10: Creación de servicio de sala INVÁLIDO (capacidad 0)
        lambda: ReservaSalas("SALA-02", 100000, 0)
    ]

    for i, op in enumerate(operaciones, start=1):
        print(f"--- Operación #{i} ---")
        try:
            op()
            print(f"Resultado: Operación #{i} ejecutada correctamente.\n")
        except ErrorSistemaFJ as err:
            print(f" [Controlado] Excepción personalizada atrapada: {err}\n")
        except Exception as ex:
            print(f" [Controlado] Error general atrapado: {ex}\n")

if __name__ == "__main__":
    ejecutar_simulacion()