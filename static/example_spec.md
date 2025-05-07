---
project: SistemaGestionBiblioteca
version: 1.0.0
description: Sistema para la gestión de préstamos y reservas de libros en una biblioteca.
---

# Especificación del Software: Sistema de Gestión de Biblioteca

## 1. Visión General

Este sistema permite gestionar el inventario de libros, usuarios y préstamos de una biblioteca. Facilita el seguimiento de libros disponibles, préstamos activos, reservas y notificaciones a usuarios. El objetivo es optimizar la gestión de recursos bibliográficos y mejorar la experiencia de servicio a los usuarios.

## 2. Actores Principales

- Bibliotecario: Personal encargado de la gestión de libros, préstamos y usuarios.
- Usuario: Persona registrada que solicita préstamos y reservas de libros.
- **SistemaNotificaciones** Sistema encargado de enviar notificaciones a los usuarios.
- *Libro* Entidad física que puede ser prestada a los usuarios.
- *Préstamo* Registro de la asignación temporal de un libro a un usuario.
- *Reserva* Solicitud de un usuario para acceder a un libro actualmente no disponible.

## 3. Casos de Uso

### CU-001: Registrar Nuevo Usuario

Actor(es): Bibliotecario
Descripción: Permite al bibliotecario registrar un nuevo usuario en el sistema.
Precondiciones:
- El usuario no debe estar registrado previamente.
Flujo Principal:
1. El Bibliotecario selecciona la opción "Registrar Usuario".
2. El sistema muestra un formulario solicitando datos del usuario.
3. El Bibliotecario ingresa la información requerida: nombre, apellido, identificación, correo electrónico y teléfono.
4. El Bibliotecario envía el formulario.
5. El sistema valida que no exista un usuario con la misma identificación.
6. El sistema crea una nueva instancia de *Usuario* con estado "Activo".
7. El **SistemaNotificaciones** envía un correo al nuevo usuario con sus credenciales.
Flujos Alternativos:
- Si ya existe un usuario con la misma identificación, el sistema muestra un mensaje de error.
Postcondiciones:
- El nuevo usuario queda registrado en el sistema y puede realizar préstamos.

### CU-002: Realizar Préstamo de Libro

Actor(es): Bibliotecario
Descripción: Registra el préstamo de un libro a un usuario.
Precondiciones:
- El usuario debe estar registrado y activo.
- El libro debe estar disponible (no prestado, no reservado).
Flujo Principal:
1. El Bibliotecario busca al *Usuario* por su identificación.
2. El Bibliotecario busca el *Libro* por su código o título.
3. El Bibliotecario selecciona la opción "Realizar Préstamo".
4. El sistema verifica la disponibilidad del *Libro*.
5. El sistema crea un nuevo *Préstamo* asociando el *Libro* con el *Usuario*.
6. El sistema actualiza el estado del *Libro* a "Prestado".
7. El sistema genera un comprobante de préstamo.
8. El **SistemaNotificaciones** envía confirmación al usuario.
Flujos Alternativos:
- Si el libro no está disponible, el sistema ofrece registrar una *Reserva*.
Postcondiciones:
- El libro queda registrado como prestado al usuario.
- Se define una fecha de devolución.

### CU-003: Devolver Libro

Actor(es): Bibliotecario
Descripción: Registra la devolución de un libro previamente prestado.
Precondiciones:
- Debe existir un préstamo activo del libro.
Flujo Principal:
1. El Bibliotecario busca el *Préstamo* por código de libro o identificación de usuario.
2. El sistema muestra la información del préstamo.
3. El Bibliotecario selecciona "Registrar Devolución".
4. El sistema actualiza el estado del *Libro* a "Disponible".
5. El sistema marca el *Préstamo* como "Finalizado".
6. Si existe alguna *Reserva* para este *Libro*, el sistema la activa.
7. El **SistemaNotificaciones** envía confirmación de devolución al usuario.
8. Si se activó una reserva, el **SistemaNotificaciones** avisa al usuario que reservó.
Flujos Alternativos:
- Si el libro tiene daños, el Bibliotecario puede registrar una incidencia.
Postcondiciones:
- El libro queda disponible para nuevos préstamos o es asignado a una reserva activa.

## 4. Modelo de Dominio (Entidades)

### *Usuario*

Descripción: Representa a una persona registrada en el sistema que puede solicitar préstamos.

Atributos:
- [+] id: int
- [+] nombre: str
- [+] apellido: str
- [+] identificacion: str
- [+] email: str
- [+] telefono: str
- [-] fechaRegistro: datetime
- [+] estado: str

Métodos:
- [+] activar() -> void
- [+] desactivar() -> void
- [+] tienePrestamosPendientes() -> bool
- [+] obtenerHistorialPrestamos() -> list[*Préstamo*]

Relaciones:
- ASOCIACION CON *Préstamo* (0..*)
- ASOCIACION CON *Reserva* (0..*)

### *Libro*

Descripción: Representa un ejemplar físico que puede ser prestado.

Atributos:
- [+] id: int
- [+] codigo: str
- [+] titulo: str
- [+] autor: str
- [+] editorial: str
- [+] añoPublicacion: int
- [+] categoria: str
- [+] estado: str
- [-] ubicacion: str

Métodos:
- [+] estaDisponible() -> bool
- [+] prestar() -> bool
- [+] devolver() -> void
- [+] reservar() -> bool
- [+] obtenerHistorialPrestamos() -> list[*Préstamo*]

Relaciones:
- ASOCIACION CON *Préstamo* (0..*)
- ASOCIACION CON *Reserva* (0..*)

### *Préstamo*

Descripción: Registro de la asignación temporal de un libro a un usuario.

Atributos:
- [+] id: int
- [+] fechaPrestamo: datetime
- [+] fechaDevolucionPrevista: datetime
- [+] fechaDevolucionReal: datetime
- [+] estado: str
- [-] observaciones: str

Métodos:
- [+] calcularDiasRetraso() -> int
- [+] finalizar() -> void
- [+] extenderPlazo(dias: int) -> bool
- [+] generarComprobante() -> str

Relaciones:
- COMPOSICION DE *Usuario* (1..1)
- COMPOSICION DE *Libro* (1..1)

### *Reserva*

Descripción: Solicitud de un usuario para tener prioridad sobre un libro no disponible.

Atributos:
- [+] id: int
- [+] fechaSolicitud: datetime
- [+] fechaExpiracion: datetime
- [+] estado: str
- [-] prioridad: int

Métodos:
- [+] activar() -> void
- [+] cancelar() -> void
- [+] convertirEnPrestamo() -> *Préstamo*
- [+] haExpirado() -> bool

Relaciones:
- COMPOSICION DE *Usuario* (1..1)
- COMPOSICION DE *Libro* (1..1)

## 5. Arquitectura del Sistema

Descripción: La arquitectura sigue un patrón de capas con separación de responsabilidades.

Componentes:
- **InterfazUsuario** Capa de presentación que proporciona la interfaz gráfica.
- **GestorPréstamos** Servicio principal que gestiona la lógica de negocio.
- **GestorNotificaciones** Servicio encargado de enviar notificaciones.
- **RepositorioDatos** Capa de acceso a datos que interactúa con la base de datos.
- **ValidadorReglas** Componente encargado de validar las reglas de negocio.

Conexiones:
- **InterfazUsuario** -> **GestorPréstamos** (API REST)
- **GestorPréstamos** -> **RepositorioDatos** (ORM)
- **GestorPréstamos** -> **ValidadorReglas** (Biblioteca)
- **GestorPréstamos** -> **GestorNotificaciones** (Mensajería)
- **GestorNotificaciones** -> **Sistema Email Externo** (SMTP)

## 6. Detalles de Secuencia

### DS-001: Proceso de Préstamo

Participantes:
- Bibliotecario
- *Usuario*
- *Libro*
- *Préstamo*
- **InterfazUsuario**
- **GestorPréstamos**
- **ValidadorReglas**
- **RepositorioDatos**
- **GestorNotificaciones**

Mensajes:
1. Bibliotecario -> **InterfazUsuario**: solicitarPréstamo(idUsuario, codigoLibro)
2. **InterfazUsuario** -> **GestorPréstamos**: procesarPrestamo(idUsuario, codigoLibro)
3. **GestorPréstamos** -> **RepositorioDatos**: buscarUsuario(idUsuario)
4. **RepositorioDatos** -> **GestorPréstamos**: datosUsuario
5. **GestorPréstamos** -> **RepositorioDatos**: buscarLibro(codigoLibro)
6. **RepositorioDatos** -> **GestorPréstamos**: datosLibro
7. **GestorPréstamos** -> **ValidadorReglas**: validarPréstamo(usuario, libro)
8. **ValidadorReglas** -> **GestorPréstamos**: resultadoValidación
9. **GestorPréstamos** -> **RepositorioDatos**: crearPréstamo(préstamo)
10. **GestorPréstamos** -> **RepositorioDatos**: actualizarEstadoLibro(codigoLibro, "Prestado")
11. **GestorPréstamos** -> **GestorNotificaciones**: enviarConfirmación(usuario, préstamo) ASYNC
12. **GestorPréstamos** -> **InterfazUsuario**: resultadoPréstamo
13. **InterfazUsuario** -> Bibliotecario: mostrarConfirmación(resultadoPréstamo)

### DS-002: Proceso de Devolución y Activación de Reserva

Participantes:
- Bibliotecario
- *Libro*
- *Préstamo*
- *Reserva*
- **InterfazUsuario**
- **GestorPréstamos**
- **RepositorioDatos**
- **GestorNotificaciones**

Mensajes:
1. Bibliotecario -> **InterfazUsuario**: registrarDevolución(codigoLibro)
2. **InterfazUsuario** -> **GestorPréstamos**: procesarDevolución(codigoLibro)
3. **GestorPréstamos** -> **RepositorioDatos**: buscarPréstamoActivo(codigoLibro)
4. **RepositorioDatos** -> **GestorPréstamos**: datosPréstamo
5. **GestorPréstamos** -> **RepositorioDatos**: finalizarPréstamo(idPréstamo)
6. **GestorPréstamos** -> **RepositorioDatos**: buscarReservasActivas(codigoLibro)
7. **RepositorioDatos** -> **GestorPréstamos**: listaReservas
8. **GestorPréstamos** -> **RepositorioDatos**: actualizarEstadoLibro(codigoLibro, "Disponible")
9. **GestorPréstamos** -> **GestorNotificaciones**: enviarConfirmaciónDevolución(préstamo) ASYNC
10. **GestorPréstamos** -> **InterfazUsuario**: resultadoDevolución
11. **InterfazUsuario** -> Bibliotecario: mostrarConfirmación(resultadoDevolución)
12. **GestorPréstamos** -> **RepositorioDatos**: activarReserva(idReserva) (Solo si hay reservas)
13. **GestorPréstamos** -> **GestorNotificaciones**: notificarReservaActiva(reserva) ASYNC (Solo si hay reservas) 