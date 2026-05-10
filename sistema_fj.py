"""
╔══════════════════════════════════════════════════════════════════════╗
║       SISTEMA INTEGRAL DE GESTIÓN — SOFTWARE FJ                     ║
║       Clientes · Servicios · Reservas                               ║
║                                                                      ║
║  Principios aplicados:                                               ║
║    • Abstracción      • Herencia        • Polimorfismo               ║
║    • Encapsulación    • Excepciones     • Logging a archivo          ║
╚══════════════════════════════════════════════════════════════════════╝
"""

# ─────────────────────────────────────────────────────────────
# IMPORTACIONES
# ─────────────────────────────────────────────────────────────
import os
import re
import uuid
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List


# ─────────────────────────────────────────────────────────────
# CONFIGURACIÓN DEL LOGGER  →  escribe en sistema_fj.log
# ─────────────────────────────────────────────────────────────
LOG_FILE = "sistema_fj.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),          # también muestra en consola
    ],
)
logger = logging.getLogger("SistemaFJ")


# ─────────────────────────────────────────────────────────────
# EXCEPCIONES PERSONALIZADAS
# ─────────────────────────────────────────────────────────────
class ErrorSistemaFJ(Exception):
    """Excepción base del sistema Software FJ."""
    pass


class ClienteInvalidoError(ErrorSistemaFJ):
    """Se lanza cuando los datos de un cliente no superan la validación."""
    pass


class ServicioNoDisponibleError(ErrorSistemaFJ):
    """Se lanza cuando se intenta usar un servicio no disponible."""
    pass


class ReservaInvalidaError(ErrorSistemaFJ):
    """Se lanza cuando los parámetros de una reserva son incorrectos."""
    pass


class DuracionInvalidaError(ReservaInvalidaError):
    """Duración fuera del rango permitido."""
    pass


class CalculoCostoError(ErrorSistemaFJ):
    """Error durante el cálculo de costo de una reserva."""
    pass


class ClienteNoEncontradoError(ErrorSistemaFJ):
    """El cliente buscado no existe en el sistema."""
    pass


class ServicioNoEncontradoError(ErrorSistemaFJ):
    """El servicio buscado no existe en el sistema."""
    pass


# ─────────────────────────────────────────────────────────────
# CLASE ABSTRACTA BASE — Entidad
# ─────────────────────────────────────────────────────────────
class Entidad(ABC):
    """
    Clase abstracta raíz del sistema.
    Provee identidad única y el contrato de obtener_info().
    """

    def __init__(self, nombre: str) -> None:
        if not nombre or not nombre.strip():
            raise ValueError("El nombre de una entidad no puede estar vacío.")
        self._id: str = str(uuid.uuid4())[:8].upper()
        self._nombre: str = nombre.strip()

    # ── Propiedad de solo lectura
    @property
    def id(self) -> str:
        return self._id

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")
        self._nombre = valor.strip()

    @abstractmethod
    def obtener_info(self) -> str:
        """Devuelve una descripción completa de la entidad."""
        ...

    def __str__(self) -> str:
        return f"[{self._id}] {self._nombre}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id!r}, nombre={self._nombre!r})"


# ─────────────────────────────────────────────────────────────
# CLASE CLIENTE
# ─────────────────────────────────────────────────────────────
class Cliente(Entidad):
    """
    Representa un cliente de Software FJ.

    Encapsula datos personales con validaciones estrictas:
      • email con formato válido (regex)
      • teléfono numérico de 7-15 dígitos
      • historial de reservas interno
    """

    _PATRON_EMAIL = re.compile(r"^[\w.\-+]+@[\w\-]+\.[a-z]{2,}$", re.IGNORECASE)

    def __init__(self, nombre: str, email: str, telefono: str) -> None:
        super().__init__(nombre)
        self.email = email          # usa el setter con validación
        self.telefono = telefono
        self.__historial: List[str] = []   # privado doble guión bajo

    # ── Email
    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, valor: str) -> None:
        if not valor or not self._PATRON_EMAIL.match(valor.strip()):
            raise ClienteInvalidoError(
                f"Email inválido: '{valor}'. Formato esperado: usuario@dominio.ext"
            )
        self.__email = valor.strip().lower()

    # ── Teléfono
    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        digitos = re.sub(r"[\s\-\+\(\)]", "", str(valor))
        if not digitos.isdigit() or not (7 <= len(digitos) <= 15):
            raise ClienteInvalidoError(
                f"Teléfono inválido: '{valor}'. Debe contener entre 7 y 15 dígitos."
            )
        self.__telefono = valor.strip()

    # ── Historial (solo lectura pública)
    @property
    def historial(self) -> List[str]:
        return list(self.__historial)     # copia defensiva

    def agregar_reserva(self, referencia: str) -> None:
        self.__historial.append(referencia)

    def obtener_info(self) -> str:
        return (
            f"CLIENTE [{self._id}]\n"
            f"  Nombre   : {self._nombre}\n"
            f"  Email    : {self.__email}\n"
            f"  Teléfono : {self.__telefono}\n"
            f"  Reservas : {len(self.__historial)}"
        )


# ─────────────────────────────────────────────────────────────
# CLASE ABSTRACTA — Servicio
# ─────────────────────────────────────────────────────────────
class Servicio(Entidad, ABC):
    """
    Clase abstracta que representa un servicio de Software FJ.
    Las subclases deben implementar calcular_costo() y describir().
    """

    IMPUESTO_DEFAULT = 0.19   # IVA Colombia 19 %

    def __init__(self, nombre: str, precio_base: float) -> None:
        super().__init__(nombre)
        self.precio_base = precio_base
        self.__disponible: bool = True

    @property
    def precio_base(self) -> float:
        return self.__precio_base

    @precio_base.setter
    def precio_base(self, valor: float) -> None:
        try:
            valor = float(valor)
        except (TypeError, ValueError) as e:
            raise ServicioNoDisponibleError(
                f"Precio base inválido: '{valor}'"
            ) from e
        if valor <= 0:
            raise ServicioNoDisponibleError(
                f"El precio base debe ser positivo. Recibido: {valor}"
            )
        self.__precio_base = valor

    @property
    def disponible(self) -> bool:
        return self.__disponible

    def habilitar(self) -> None:
        self.__disponible = True

    def deshabilitar(self) -> None:
        self.__disponible = False

    def _verificar_disponibilidad(self) -> None:
        if not self.__disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self._nombre}' no está disponible actualmente."
            )

    # ── Métodos abstractos (polimorfismo)
    @abstractmethod
    def calcular_costo(self, duracion: float, descuento: float = 0.0,
                       aplicar_impuesto: bool = True) -> float:
        """
        Calcula el costo total del servicio.

        Parámetros:
            duracion        : cantidad de horas o días según el tipo de servicio
            descuento       : porcentaje de descuento (0.0 – 1.0)
            aplicar_impuesto: si True, añade el IVA configurado
        """
        ...

    @abstractmethod
    def describir(self) -> str:
        """Descripción comercial del servicio."""
        ...

    def _calcular_base(self, duracion: float, descuento: float = 0.0,
                       aplicar_impuesto: bool = True) -> float:
        """
        Helper compartido: precio_base * duracion, descuento e impuesto.
        Lanza CalculoCostoError ante inconsistencias.
        """
        try:
            if not (0.0 <= descuento < 1.0):
                raise CalculoCostoError(
                    f"Descuento inválido: {descuento}. Debe estar entre 0.0 y 0.99."
                )
            subtotal = self.__precio_base * duracion
            subtotal *= (1 - descuento)
            if aplicar_impuesto:
                subtotal *= (1 + self.IMPUESTO_DEFAULT)
            return round(subtotal, 2)
        except CalculoCostoError:
            raise
        except Exception as e:
            raise CalculoCostoError(
                f"Error inesperado al calcular costo de '{self._nombre}'"
            ) from e

    def obtener_info(self) -> str:
        estado = "✔ Disponible" if self.__disponible else "✘ No disponible"
        return (
            f"SERVICIO [{self._id}] — {self.__class__.__name__}\n"
            f"  Nombre       : {self._nombre}\n"
            f"  Precio base  : ${self.__precio_base:,.0f}/unidad\n"
            f"  Estado       : {estado}\n"
            f"  Descripción  : {self.describir()}"
        )


# ─────────────────────────────────────────────────────────────
# SERVICIOS ESPECIALIZADOS
# ─────────────────────────────────────────────────────────────

class ReservaSala(Servicio):
    """
    Reserva de sala de reuniones.
    Unidad: horas. Cargo adicional si la capacidad supera 10 personas.
    """

    TARIFA_EXTRA_PERSONA = 15_000   # COP por persona extra sobre 10

    def __init__(self, nombre: str, precio_hora: float, capacidad: int,
                 equipamiento: str = "básico") -> None:
        super().__init__(nombre, precio_hora)
        if not isinstance(capacidad, int) or capacidad < 1:
            raise ServicioNoDisponibleError("La capacidad debe ser un entero positivo.")
        self.__capacidad = capacidad
        self.__equipamiento = equipamiento

    @property
    def capacidad(self) -> int:
        return self.__capacidad

    def calcular_costo(self, duracion: float, descuento: float = 0.0,
                       aplicar_impuesto: bool = True,
                       personas: int = 1) -> float:
        """
        Calcula el costo de la sala.

        Args extra (sobrecarga de parámetros):
            personas: asistentes; si supera capacidad base (10) agrega tarifa.
        """
        self._verificar_disponibilidad()
        if duracion <= 0:
            raise DuracionInvalidaError("La duración en horas debe ser positiva.")
        if duracion > 24:
            raise DuracionInvalidaError("No se pueden reservar más de 24 horas continuas.")

        base = self._calcular_base(duracion, descuento, aplicar_impuesto)
        extra = max(0, personas - 10) * self.TARIFA_EXTRA_PERSONA
        return round(base + extra, 2)

    def describir(self) -> str:
        return (
            f"Sala '{self._nombre}' · cap. {self.__capacidad} personas · "
            f"equipamiento {self.__equipamiento}"
        )


class AlquilerEquipo(Servicio):
    """
    Alquiler de equipos tecnológicos.
    Unidad: días. Descuento automático a partir del 7.° día.
    """

    DESCUENTO_SEMANA = 0.10   # 10 % si se alquila ≥ 7 días

    def __init__(self, nombre: str, precio_dia: float,
                 tipo_equipo: str, numero_serial: str) -> None:
        super().__init__(nombre, precio_dia)
        if not numero_serial or len(numero_serial) < 4:
            raise ServicioNoDisponibleError(
                "El número serial debe tener al menos 4 caracteres."
            )
        self.__tipo_equipo = tipo_equipo
        self.__numero_serial = numero_serial.upper()

    def calcular_costo(self, duracion: float, descuento: float = 0.0,
                       aplicar_impuesto: bool = True) -> float:
        """
        Calcula el costo del alquiler.
        Aplica descuento adicional automático si duracion >= 7 días.
        """
        self._verificar_disponibilidad()
        if duracion <= 0:
            raise DuracionInvalidaError("La duración en días debe ser positiva.")
        if duracion > 365:
            raise DuracionInvalidaError("El alquiler no puede superar 365 días.")

        desc_efectivo = descuento
        if duracion >= 7:
            desc_efectivo = max(descuento, self.DESCUENTO_SEMANA)

        return self._calcular_base(duracion, desc_efectivo, aplicar_impuesto)

    def describir(self) -> str:
        return (
            f"Equipo '{self._nombre}' · tipo: {self.__tipo_equipo} · "
            f"serial: {self.__numero_serial}"
        )


class AsesoriaEspecializada(Servicio):
    """
    Sesión de asesoría con experto de Software FJ.
    Unidad: horas. El costo varía según el nivel de especialización.
    """

    NIVELES = {"junior": 1.0, "senior": 1.5, "expert": 2.0}

    def __init__(self, nombre: str, tarifa_hora: float,
                 especialidad: str, asesor: str,
                 nivel: str = "senior") -> None:
        super().__init__(nombre, tarifa_hora)
        self.__especialidad = especialidad
        self.__asesor = asesor
        nivel = nivel.lower()
        if nivel not in self.NIVELES:
            raise ServicioNoDisponibleError(
                f"Nivel '{nivel}' inválido. Opciones: {list(self.NIVELES.keys())}"
            )
        self.__nivel = nivel

    def calcular_costo(self, duracion: float, descuento: float = 0.0,
                       aplicar_impuesto: bool = True) -> float:
        """
        Calcula el costo de la asesoría.
        Multiplica tarifa_hora × factor_nivel × horas.
        """
        self._verificar_disponibilidad()
        if duracion <= 0:
            raise DuracionInvalidaError("La duración en horas debe ser positiva.")
        if duracion > 8:
            raise DuracionInvalidaError(
                "Una sesión de asesoría no puede superar 8 horas."
            )
        factor = self.NIVELES[self.__nivel]
        costo_hora_ajustado = self.precio_base * factor
        subtotal = costo_hora_ajustado * duracion * (1 - descuento)
        if aplicar_impuesto:
            subtotal *= (1 + self.IMPUESTO_DEFAULT)
        return round(subtotal, 2)

    def describir(self) -> str:
        return (
            f"Asesoría '{self._nombre}' · {self.__especialidad} · "
            f"asesor: {self.__asesor} · nivel: {self.__nivel}"
        )


# ─────────────────────────────────────────────────────────────
# CLASE RESERVA
# ─────────────────────────────────────────────────────────────
class EstadoReserva:
    PENDIENTE   = "PENDIENTE"
    CONFIRMADA  = "CONFIRMADA"
    CANCELADA   = "CANCELADA"
    EN_PROCESO  = "EN_PROCESO"
    COMPLETADA  = "COMPLETADA"


class Reserva:
    """
    Integra Cliente + Servicio con duración, estado y costos calculados.

    Implementa:
      • confirmar()   → try/except/else
      • cancelar()    → try/except/finally
      • procesar()    → try/except/else/finally
      • calcular_total() → método sobrecargado (descuento, impuesto, personas)
    """

    def __init__(self, cliente: Cliente, servicio: Servicio,
                 duracion: float) -> None:
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("Se requiere un objeto Cliente válido.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("Se requiere un objeto Servicio válido.")
        if duracion is None or duracion <= 0:
            raise DuracionInvalidaError(
                f"Duración inválida: {duracion}. Debe ser un número positivo."
            )

        self.__id      = str(uuid.uuid4())[:8].upper()
        self.__cliente = cliente
        self.__servicio = servicio
        self.__duracion = float(duracion)
        self.__estado   = EstadoReserva.PENDIENTE
        self.__fecha_creacion = datetime.now()
        self.__total: Optional[float] = None
        self.__notas: List[str] = []

        logger.info(
            f"Reserva [{self.__id}] creada — "
            f"cliente: {cliente.nombre} | servicio: {servicio.nombre}"
        )

    # ── Propiedades de solo lectura
    @property
    def id(self) -> str:
        return self.__id

    @property
    def estado(self) -> str:
        return self.__estado

    @property
    def cliente(self) -> Cliente:
        return self.__cliente

    @property
    def servicio(self) -> Servicio:
        return self.__servicio

    @property
    def total(self) -> Optional[float]:
        return self.__total

    # ── calcular_total  (parámetros opcionales = sobrecarga simulada)
    def calcular_total(self, descuento: float = 0.0,
                       aplicar_impuesto: bool = True,
                       **kwargs) -> float:
        """
        Calcula el total de la reserva.

        Acepta **kwargs para pasar parámetros específicos al tipo de servicio
        (p. ej. personas= para ReservaSala). Esto simula sobrecarga de métodos.
        """
        try:
            costo = self.__servicio.calcular_costo(
                self.__duracion, descuento, aplicar_impuesto, **kwargs
            )
        except (CalculoCostoError, DuracionInvalidaError, ServicioNoDisponibleError) as e:
            logger.error(
                f"[Reserva {self.__id}] Error en calcular_total: {e}"
            )
            raise CalculoCostoError(
                f"No se pudo calcular el total de la reserva [{self.__id}]"
            ) from e
        except TypeError as e:
            raise CalculoCostoError(
                f"Parámetros incompatibles con el servicio '{self.__servicio.nombre}'"
            ) from e

        self.__total = costo
        return costo

    # ── confirmar  →  try/except/else
    def confirmar(self) -> bool:
        """
        Confirma la reserva si está PENDIENTE.
        Usa try/except/else para demostrar el flujo.
        """
        try:
            if self.__estado != EstadoReserva.PENDIENTE:
                raise ReservaInvalidaError(
                    f"Solo se pueden confirmar reservas PENDIENTES. "
                    f"Estado actual: {self.__estado}"
                )
            if self.__total is None:
                self.calcular_total()
        except ReservaInvalidaError as e:
            logger.warning(f"[Reserva {self.__id}] No se pudo confirmar: {e}")
            return False
        except CalculoCostoError as e:
            logger.error(f"[Reserva {self.__id}] Error de costo al confirmar: {e}")
            return False
        else:
            self.__estado = EstadoReserva.CONFIRMADA
            self.__cliente.agregar_reserva(self.__id)
            logger.info(
                f"[Reserva {self.__id}] CONFIRMADA — "
                f"total: ${self.__total:,.0f}"
            )
            return True

    # ── cancelar  →  try/except/finally
    def cancelar(self, motivo: str = "Sin motivo especificado") -> bool:
        """
        Cancela la reserva. Registra siempre en finally (sea o no exitoso).
        """
        intento_exitoso = False
        try:
            if self.__estado == EstadoReserva.CANCELADA:
                raise ReservaInvalidaError("La reserva ya está cancelada.")
            if self.__estado == EstadoReserva.COMPLETADA:
                raise ReservaInvalidaError(
                    "No se puede cancelar una reserva ya completada."
                )
            self.__estado = EstadoReserva.CANCELADA
            self.__notas.append(f"Cancelada: {motivo}")
            intento_exitoso = True
        except ReservaInvalidaError as e:
            logger.warning(f"[Reserva {self.__id}] Cancelación rechazada: {e}")
        finally:
            accion = "CANCELADA" if intento_exitoso else "intento de cancelación fallido"
            logger.info(f"[Reserva {self.__id}] → {accion}. Motivo: {motivo}")
        return intento_exitoso

    # ── procesar  →  try/except/else/finally  (estructura completa)
    def procesar(self) -> bool:
        """
        Procesa la reserva confirmada: la marca como COMPLETADA.
        Demuestra try/except/else/finally completo.
        """
        exitoso = False
        try:
            if self.__estado != EstadoReserva.CONFIRMADA:
                raise ReservaInvalidaError(
                    f"Solo se procesan reservas CONFIRMADAS. "
                    f"Estado: {self.__estado}"
                )
            self.__estado = EstadoReserva.EN_PROCESO
            # Simulación de lógica de procesamiento
            if self.__total is None or self.__total < 0:
                raise CalculoCostoError("Total de reserva inválido para procesar.")
        except ReservaInvalidaError as e:
            logger.warning(f"[Reserva {self.__id}] No se procesó: {e}")
        except CalculoCostoError as e:
            logger.error(f"[Reserva {self.__id}] Error de costo al procesar: {e}")
            self.__estado = EstadoReserva.CONFIRMADA  # revertir
        else:
            self.__estado = EstadoReserva.COMPLETADA
            exitoso = True
            logger.info(f"[Reserva {self.__id}] COMPLETADA exitosamente.")
        finally:
            logger.debug(
                f"[Reserva {self.__id}] Procesamiento finalizado — "
                f"estado: {self.__estado}"
            )
        return exitoso

    def obtener_info(self) -> str:
        total_str = f"${self.__total:,.0f}" if self.__total else "No calculado"
        return (
            f"RESERVA [{self.__id}]\n"
            f"  Cliente  : {self.__cliente.nombre}\n"
            f"  Servicio : {self.__servicio.nombre}\n"
            f"  Duración : {self.__duracion} unidades\n"
            f"  Estado   : {self.__estado}\n"
            f"  Total    : {total_str}\n"
            f"  Creada   : {self.__fecha_creacion.strftime('%Y-%m-%d %H:%M')}"
        )

    def __str__(self) -> str:
        return f"Reserva[{self.__id}] {self.__cliente.nombre} → {self.__servicio.nombre} ({self.__estado})"


# ─────────────────────────────────────────────────────────────
# SISTEMA GESTOR CENTRAL
# ─────────────────────────────────────────────────────────────
class SistemaGestor:
    """
    Gestor central de Software FJ.

    Administra las listas internas de clientes, servicios y reservas.
    Captura y registra todos los errores para mantener la aplicación estable.
    """

    def __init__(self, empresa: str = "Software FJ") -> None:
        self.__empresa   = empresa
        self.__clientes:  List[Cliente]  = []
        self.__servicios: List[Servicio] = []
        self.__reservas:  List[Reserva]  = []
        logger.info(f"{'='*60}")
        logger.info(f"Sistema iniciado — {self.__empresa}")
        logger.info(f"{'='*60}")

    # ── Registrar cliente
    def registrar_cliente(self, nombre: str, email: str, telefono: str
                          ) -> Optional[Cliente]:
        try:
            cliente = Cliente(nombre, email, telefono)
        except ClienteInvalidoError as e:
            logger.error(f"registrar_cliente FALLÓ: {e}")
            print(f"  ✘ Error al registrar cliente '{nombre}': {e}")
            return None
        except ValueError as e:
            logger.error(f"registrar_cliente — valor inválido: {e}")
            print(f"  ✘ Valor inválido: {e}")
            return None
        else:
            self.__clientes.append(cliente)
            logger.info(f"Cliente registrado: {cliente.nombre} [{cliente.id}]")
            print(f"  ✔ Cliente '{cliente.nombre}' registrado. ID: {cliente.id}")
            return cliente

    # ── Registrar servicio
    def registrar_servicio(self, servicio: Servicio) -> bool:
        try:
            if not isinstance(servicio, Servicio):
                raise ServicioNoDisponibleError(
                    "El objeto no es una instancia de Servicio."
                )
        except ServicioNoDisponibleError as e:
            logger.error(f"registrar_servicio FALLÓ: {e}")
            print(f"  ✘ {e}")
            return False
        else:
            self.__servicios.append(servicio)
            logger.info(f"Servicio registrado: {servicio.nombre} [{servicio.id}]")
            print(f"  ✔ Servicio '{servicio.nombre}' registrado. ID: {servicio.id}")
            return True

    # ── Crear reserva
    def crear_reserva(self, cliente: Cliente, servicio: Servicio,
                      duracion: float, descuento: float = 0.0,
                      **kwargs) -> Optional[Reserva]:
        try:
            reserva = Reserva(cliente, servicio, duracion)
            total = reserva.calcular_total(descuento=descuento, **kwargs)
        except (ReservaInvalidaError, DuracionInvalidaError) as e:
            logger.error(f"crear_reserva FALLÓ (datos inválidos): {e}")
            print(f"  ✘ Reserva rechazada: {e}")
            return None
        except CalculoCostoError as e:
            logger.error(f"crear_reserva FALLÓ (error de costo): {e}")
            print(f"  ✘ Error de costo: {e}")
            return None
        except Exception as e:
            logger.critical(
                f"crear_reserva — error inesperado: {e}", exc_info=True
            )
            print(f"  ✘ Error inesperado: {e}")
            return None
        else:
            self.__reservas.append(reserva)
            print(
                f"  ✔ Reserva creada [{reserva.id}] — "
                f"Total: ${total:,.0f} COP"
            )
            return reserva

    # ── Buscar cliente por nombre
    def buscar_cliente(self, nombre: str) -> Cliente:
        try:
            resultado = next(
                (c for c in self.__clientes
                 if nombre.lower() in c.nombre.lower()), None
            )
            if resultado is None:
                raise ClienteNoEncontradoError(
                    f"No se encontró ningún cliente con nombre '{nombre}'."
                )
        except ClienteNoEncontradoError:
            raise
        except Exception as e:
            raise ErrorSistemaFJ(
                f"Error inesperado al buscar cliente '{nombre}'"
            ) from e
        return resultado

    # ── Listar todo
    def listar_clientes(self) -> None:
        print(f"\n{'─'*50}")
        print(f"  CLIENTES REGISTRADOS ({len(self.__clientes)})")
        print(f"{'─'*50}")
        if not self.__clientes:
            print("  (Sin clientes)")
            return
        for c in self.__clientes:
            print(f"  • {c.nombre} | {c.email} | Reservas: {len(c.historial)}")

    def listar_servicios(self) -> None:
        print(f"\n{'─'*50}")
        print(f"  SERVICIOS REGISTRADOS ({len(self.__servicios)})")
        print(f"{'─'*50}")
        if not self.__servicios:
            print("  (Sin servicios)")
            return
        for s in self.__servicios:
            estado = "✔" if s.disponible else "✘"
            print(f"  {estado} [{s.__class__.__name__}] {s.nombre} — ${s.precio_base:,.0f}/u")

    def listar_reservas(self) -> None:
        print(f"\n{'─'*50}")
        print(f"  RESERVAS REGISTRADAS ({len(self.__reservas)})")
        print(f"{'─'*50}")
        if not self.__reservas:
            print("  (Sin reservas)")
            return
        for r in self.__reservas:
            print(f"  • {r}")

    def resumen(self) -> None:
        print(f"\n{'═'*55}")
        print(f"  RESUMEN — {self.__empresa}")
        print(f"{'═'*55}")
        print(f"  Clientes registrados : {len(self.__clientes)}")
        print(f"  Servicios registrados: {len(self.__servicios)}")
        print(f"  Reservas totales     : {len(self.__reservas)}")
        confirmadas = sum(
            1 for r in self.__reservas
            if r.estado == EstadoReserva.CONFIRMADA
        )
        completadas = sum(
            1 for r in self.__reservas
            if r.estado == EstadoReserva.COMPLETADA
        )
        canceladas = sum(
            1 for r in self.__reservas
            if r.estado == EstadoReserva.CANCELADA
        )
        print(f"    → Confirmadas : {confirmadas}")
        print(f"    → Completadas : {completadas}")
        print(f"    → Canceladas  : {canceladas}")
        print(f"{'═'*55}\n")


# ─────────────────────────────────────────────────────────────
# SIMULACIÓN DE 10+ OPERACIONES
# ─────────────────────────────────────────────────────────────
def ejecutar_simulacion() -> None:
    print("\n" + "═" * 60)
    print("  SIMULACIÓN — SISTEMA INTEGRAL SOFTWARE FJ")
    print("═" * 60)

    sistema = SistemaGestor("Software FJ")

    # ─── Crear servicios disponibles
    sala_innovacion   = ReservaSala("Sala Innovación", 80_000, 20, "proyector + TV")
    sala_juntas       = ReservaSala("Sala Juntas A",   60_000, 10, "básico")
    laptop_asus       = AlquilerEquipo("Laptop ASUS ProArt", 45_000,
                                       "Laptop", "ASUS-2024-X001")
    camara_sony       = AlquilerEquipo("Cámara Sony A7", 35_000,
                                       "Cámara", "SONY-A7-4455")
    asesoria_cloud    = AsesoriaEspecializada("Consultoría Cloud AWS", 120_000,
                                              "Cloud Computing", "Dr. López", "expert")
    asesoria_mobile   = AsesoriaEspecializada("Asesoría App Móvil", 90_000,
                                              "Desarrollo Mobile", "Ing. García", "senior")

    print("\n► PASO 1 — Registrar servicios")
    for srv in [sala_innovacion, sala_juntas, laptop_asus,
                camara_sony, asesoria_cloud, asesoria_mobile]:
        sistema.registrar_servicio(srv)

    # ─── OP 1-4: Clientes válidos
    print("\n► PASO 2 — Registrar clientes (válidos e inválidos)")
    c1 = sistema.registrar_cliente("Ana Martínez",    "ana.martinez@gmail.com",   "3001234567")
    c2 = sistema.registrar_cliente("Carlos Rueda",    "carlos.rueda@empresa.co",  "3117654321")
    c3 = sistema.registrar_cliente("Sofía Herrera",   "sofia.herrera@hotmail.com","6012345678")
    c4 = sistema.registrar_cliente("Luis Cardona",    "lcardona@softwarefj.co",   "3209876543")

    # ─── OP 5: Cliente con email inválido (debe fallar)
    print("\n  [OP-5] Intentando registrar cliente con email inválido...")
    c_malo_email = sistema.registrar_cliente("Pedro Malo", "pedro_sin_arroba", "3001111111")

    # ─── OP 6: Cliente con teléfono inválido (debe fallar)
    print("\n  [OP-6] Intentando registrar cliente con teléfono inválido...")
    c_malo_tel = sistema.registrar_cliente("María Error", "maria@ok.com", "ABC123")

    # ─── OP 7: Reserva válida — sala con 15 personas, 3 horas, 10 % desc
    print("\n► PASO 3 — Crear reservas")
    print("\n  [OP-7] Reserva de sala con personas extra y descuento:")
    r1 = sistema.crear_reserva(c1, sala_innovacion, 3,
                               descuento=0.10, personas=15)
    if r1:
        r1.confirmar()
        r1.procesar()

    # ─── OP 8: Reserva válida — alquiler de laptop 10 días (descuento semanal auto)
    print("\n  [OP-8] Alquiler de laptop 10 días (descuento semanal automático):")
    r2 = sistema.crear_reserva(c2, laptop_asus, 10)
    if r2:
        r2.confirmar()

    # ─── OP 9: Reserva válida — asesoría expert 2 horas
    print("\n  [OP-9] Asesoría Cloud expert 2 horas:")
    r3 = sistema.crear_reserva(c3, asesoria_cloud, 2, descuento=0.05)
    if r3:
        r3.confirmar()
        r3.procesar()

    # ─── OP 10: Intentar reservar servicio deshabilitado (debe fallar)
    print("\n  [OP-10] Deshabilitando 'Cámara Sony' e intentando reservar...")
    camara_sony.deshabilitar()
    r_deshabilitado = sistema.crear_reserva(c4, camara_sony, 5)

    # ─── OP 11: Duración inválida (negativa)
    print("\n  [OP-11] Reserva con duración negativa:")
    r_duracion_mala = sistema.crear_reserva(c1, sala_juntas, -2)

    # ─── OP 12: Cancelar reserva ya confirmada
    print("\n  [OP-12] Cancelar reserva confirmada:")
    r4 = sistema.crear_reserva(c4, asesoria_mobile, 1)
    if r4:
        r4.confirmar()
        exito = r4.cancelar("Cliente solicitó reagendar")
        print(f"  {'✔' if exito else '✘'} Cancelación {'exitosa' if exito else 'fallida'}")

    # ─── OP 13: Intentar confirmar reserva ya cancelada
    print("\n  [OP-13] Intentar confirmar una reserva cancelada:")
    if r4:
        resultado = r4.confirmar()
        print(f"  {'✔' if resultado else '✘'} Confirmación {'aceptada' if resultado else 'rechazada (correcto)'}")

    # ─── OP 14: Descuento fuera de rango (debe lanzar error)
    print("\n  [OP-14] Reserva con descuento inválido (1.5 = 150%):")
    r_desc_malo = sistema.crear_reserva(c2, sala_juntas, 2, descuento=1.5)

    # ─── OP 15: Asesoría con duración excesiva
    print("\n  [OP-15] Asesoría con duración de 12 horas (máx 8):")
    r_asesor_largo = sistema.crear_reserva(c3, asesoria_mobile, 12)

    # ─── Mostrar info detallada de una reserva completada
    print("\n► PASO 4 — Información detallada de reservas exitosas")
    for r in [r1, r2, r3]:
        if r:
            print("\n" + r.obtener_info())

    # ─── Listados finales
    sistema.listar_clientes()
    sistema.listar_servicios()
    sistema.listar_reservas()
    sistema.resumen()

    print(f"\n📄 Log completo guardado en: {os.path.abspath(LOG_FILE)}")
    print("═" * 60)


# ─────────────────────────────────────────────────────────────
# PUNTO DE ENTRADA
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        ejecutar_simulacion()
    except KeyboardInterrupt:
        print("\n⚠ Simulación interrumpida por el usuario.")
        logger.warning("Simulación interrumpida por el usuario (KeyboardInterrupt).")
    except Exception as e:
        logger.critical(f"Error crítico no controlado: {e}", exc_info=True)
        print(f"\n✘ Error crítico: {e}")
