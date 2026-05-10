# ── confirmar  →  try/except/else
"""
Confirmar la reserva si está PENDIENTE.
Usamos try/except/else para mostrar el flujo.
"""
    def confirmar(self) -> bool:
       
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


