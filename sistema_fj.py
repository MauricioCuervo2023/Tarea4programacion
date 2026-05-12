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

        self.__empresa   = empresa 

        self.__clientes:  List[Cliente]  = [] 

        self.__servicios: List[Servicio] = [] 

        self.__reservas:  List[Reserva]  = [] 

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

            print(f"  ✘ Error al registrar cliente '{nombre}': {e}") 

            return None 

        except ValueError as e: 

            logger.error(f"registrar_cliente — valor inválido: {e}") 

            print(f"  ✘ Valor inválido: {e}") 

            return None 

        else: 

            self.__clientes.append(cliente) 

            logger.info(f"Cliente registrado: {cliente.nombre} [{cliente.id}]") 

            print(f"  ✔ Cliente '{cliente.nombre}' registrado. ID: {cliente.id}") 

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

            print(f"  ✘ {e}") 

            return False 

        else: 

            self.__servicios.append(servicio) 

            logger.info(f"Servicio registrado: {servicio.nombre} [{servicio.id}]") 

            print(f"  ✔ Servicio '{servicio.nombre}' registrado. ID: {servicio.id}") 

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

            print(f"  ✘ Reserva rechazada: {e}") 

            return None 

        except CalculoCostoError as e: 

            logger.error(f"crear_reserva FALLÓ (error de costo): {e}") 

            print(f"  ✘ Error de costo: {e}") 

            return None 

        except Exception as e: 

            logger.critical( 

                f"crear_reserva — error inesperado: {e}", exc_info=True 

            ) 

            print(f"  ✘ Error inesperado: {e}") 

            return None 

        else: 

            self.__reservas.append(reserva) 

            print( 

                f"  ✔ Reserva creada [{reserva.id}] — " 

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

        print(f"  CLIENTES REGISTRADOS ({len(self.__clientes)})") 

        print(f"{'─'*50}") 

        if not self.__clientes: 

            print("  (Sin clientes)") 

            return 

        for c in self.__clientes: 

            print(f"  • {c.nombre} | {c.email} | Reservas: {len(c.historial)}") 

 

    def listar_servicios(self) -> None: 

        print(f"\n{'─'*50}") 

        print(f"  SERVICIOS REGISTRADOS ({len(self.__servicios)})") 

        print(f"{'─'*50}") 

        if not self.__servicios: 

            print("  (Sin servicios)") 

            return 

        for s in self.__servicios: 

            estado = "✔" if s.disponible else "✘" 

            print(f"  {estado} [{s.__class__.__name__}] {s.nombre} — ${s.precio_base:,.0f}/u") 

 

    def listar_reservas(self) -> None: 

        print(f"\n{'─'*50}") 

        print(f"  RESERVAS REGISTRADAS ({len(self.__reservas)})") 

        print(f"{'─'*50}") 

        if not self.__reservas: 

            print("  (Sin reservas)") 

            return 

        for r in self.__reservas: 

            print(f"  • {r}") 

 

    def resumen(self) -> None: 

        print(f"\n{'═'*55}") 

        print(f"  RESUMEN — {self.__empresa}") 

        print(f"{'═'*55}") 

        print(f"  Clientes registrados : {len(self.__clientes)}") 

        print(f"  Servicios registrados: {len(self.__servicios)}") 

        print(f"  Reservas totales     : {len(self.__reservas)}") 

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

        print(f"    → Confirmadas : {confirmadas}") 

        print(f"    → Completadas : {completadas}") 

        print(f"    → Canceladas  : {canceladas}") 

        print(f"{'═'*55}\n") 

 

# ───────────────────────────────────────────────────────────── 

# SIMULACIÓN DE 10+ OPERACIONES 

# ───────────────────────────────────────────────────────────── 

def ejecutar_simulacion() -> None: 

    print("\n" + "═" * 60) 

    print("  SIMULACIÓN — SISTEMA INTEGRAL SOFTWARE FJ") 

    print("═" * 60) 

 

    sistema = SistemaGestor("Software FJ") 

 

    # ─── Crear servicios disponibles 

    sala_innovacion   = ReservaSala("Sala Innovación", 80_000, 20, "proyector + TV") 

    sala_juntas       = ReservaSala("Sala Juntas A",   60_000, 10, "básico") 

    laptop_asus       = AlquilerEquipo("Laptop ASUS ProArt", 45_000, 

                                       "Laptop", "ASUS-2024-X001") 

    camara_sony       = AlquilerEquipo("Cámara Sony A7", 35_000, 

                                       "Cámara", "SONY-A7-4455") 

    asesoria_cloud    = AsesoriaEspecializada("Consultoría Cloud AWS", 120_000, 

                                              "Cloud Computing", "Dr. López", "expert") 

    asesoria_mobile   = AsesoriaEspecializada("Asesoría App Móvil", 90_000, 

                                              "Desarrollo Mobile", "Ing. García", "senior") 

 

    print("\n► PASO 1 — Registrar servicios") 

    for srv in [sala_innovacion, sala_juntas, laptop_asus, 

                camara_sony, asesoria_cloud, asesoria_mobile]: 

        sistema.registrar_servicio(srv) 

 

    # ─── OP 1-4: Clientes válidos 

    print("\n► PASO 2 — Registrar clientes (válidos e inválidos)") 

    c1 = sistema.registrar_cliente("Ana Martínez",    "ana.martinez@gmail.com",   "3001234567") 

    c2 = sistema.registrar_cliente("Carlos Rueda",    "carlos.rueda@empresa.co",  "3117654321") 

    c3 = sistema.registrar_cliente("Sofía Herrera",   "sofia.herrera@hotmail.com","6012345678") 

    c4 = sistema.registrar_cliente("Luis Cardona",    "lcardona@softwarefj.co",   "3209876543") 

 

    # ─── OP 5: Cliente con email inválido (debe fallar) 

    print("\n  [OP-5] Intentando registrar cliente con email inválido...") 

    c_malo_email = sistema.registrar_cliente("Pedro Malo", "pedro_sin_arroba", "3001111111") 

 

    # ─── OP 6: Cliente con teléfono inválido (debe fallar) 

    print("\n  [OP-6] Intentando registrar cliente con teléfono inválido...") 

    c_malo_tel = sistema.registrar_cliente("María Error", "maria@ok.com", "ABC123") 

 

    # ─── OP 7: Reserva válida — sala con 15 personas, 3 horas, 10 % desc 

    print("\n► PASO 3 — Crear reservas") 

    print("\n  [OP-7] Reserva de sala con personas extra y descuento:") 

    r1 = sistema.crear_reserva(c1, sala_innovacion, 3, 

                               descuento=0.10, personas=15) 

    if r1: 

        r1.confirmar() 

        r1.procesar() 

 

    # ─── OP 8: Reserva válida — alquiler de laptop 10 días (descuento semanal auto) 

    print("\n  [OP-8] Alquiler de laptop 10 días (descuento semanal automático):") 

    r2 = sistema.crear_reserva(c2, laptop_asus, 10) 

    if r2: 

        r2.confirmar() 

 

    # ─── OP 9: Reserva válida — asesoría expert 2 horas 

    print("\n  [OP-9] Asesoría Cloud expert 2 horas:") 

    r3 = sistema.crear_reserva(c3, asesoria_cloud, 2, descuento=0.05) 

    if r3: 

        r3.confirmar() 

        r3.procesar() 

 

    # ─── OP 10: Intentar reservar servicio deshabilitado (debe fallar) 

    print("\n  [OP-10] Deshabilitando 'Cámara Sony' e intentando reservar...") 

    camara_sony.deshabilitar() 

    r_deshabilitado = sistema.crear_reserva(c4, camara_sony, 5) 

 

    # ─── OP 11: Duración inválida (negativa) 

    print("\n  [OP-11] Reserva con duración negativa:") 

    r_duracion_mala = sistema.crear_reserva(c1, sala_juntas, -2) 

 

    # ─── OP 12: Cancelar reserva ya confirmada 

    print("\n  [OP-12] Cancelar reserva confirmada:") 

    r4 = sistema.crear_reserva(c4, asesoria_mobile, 1) 

    if r4: 

        r4.confirmar() 

        exito = r4.cancelar("Cliente solicitó reagendar") 

        print(f"  {'✔' if exito else '✘'} Cancelación {'exitosa' if exito else 'fallida'}") 

 

    # ─── OP 13: Intentar confirmar reserva ya cancelada 

    print("\n  [OP-13] Intentar confirmar una reserva cancelada:") 

    if r4: 

        resultado = r4.confirmar() 

        print(f"  {'✔' if resultado else '✘'} Confirmación {'aceptada' if resultado else 'rechazada (correcto)'}") 

 

    # ─── OP 14: Descuento fuera de rango (debe lanzar error) 

    print("\n  [OP-14] Reserva con descuento inválido (1.5 = 150%):") 

    r_desc_malo = sistema.crear_reserva(c2, sala_juntas, 2, descuento=1.5) 

 

    # ─── OP 15: Asesoría con duración excesiva 

    print("\n  [OP-15] Asesoría con duración de 12 horas (máx 8):") 

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
