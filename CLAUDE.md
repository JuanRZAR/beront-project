# Reglas de trabajo de BÉRONT

## 1. Arquitectura
Cumplir docs/ARCHITECTURE.md.
No cambiar arquitectura, contratos estructurales, stack ni límites de módulos
sin aprobación previa y explícita del propietario.
Si una instrucción nueva contradice la arquitectura, señalar la contradicción
y resolverla antes de implementar.

## 2. Organización de archivos
Crear archivos únicamente en las ubicaciones y patrones autorizados por
docs/ARCHITECTURE.md.
Proponer y obtener aprobación antes de añadir una ubicación nueva.
No crear carpetas auxiliares fuera de esa organización.

## 3. Separación de capas
El dominio no depende de Flask, SQLAlchemy, Pydantic ni del frontend.
Los modelos de tablas pertenecen a infraestructura/modelos y se usan para metadata y Alembic.
El acceso a datos de la aplicación utiliza funciones PostgreSQL mediante pg_call.py,
invocado por repositorios de infraestructura; no utilizar sesiones ORM para leer o escribir.
Los repositorios traducen resultados SQL a entidades o DTO de aplicación.
Los controladores no contienen reglas comerciales ni llamadas SQL directas.
No acceder directamente a los modelos internos de otro módulo.

## 4. Comentarios
Usar comentarios breves y técnicos solo para lógica no evidente,
decisiones de seguridad o workarounds justificados.
No añadir comentarios narrativos, históricos o que repitan el código.
No explicar en comentarios que un cambio se hizo por una petición o un bug.

## 5. Git
No ejecutar commit, push, merge, creación de ramas ni operaciones que
modifiquen el historial o el remoto sin solicitud explícita del propietario.
No inicializar Git ni usar generadores que lo hagan automáticamente.
Crear los .gitignore aprobados no autoriza otras operaciones de Git.

## 6. Archivos temporales
Eliminar al terminar los scripts, pruebas exploratorias y datos temporales
creados para la tarea.
Mantener las pruebas permanentes aprobadas.
No eliminar archivos del usuario, fotografías reales ni datos de negocio
como parte de una limpieza.
Usar directorios temporales del sistema o ubicaciones aprobadas.

## 7. Autorización
Aplicar decoradores reutilizables de autenticación y permisos en cada
endpoint protegido.
Verificar autorización y acceso al recurso en el backend.
Proteger rutas, páginas y controles en el frontend según la sesión
y los permisos devueltos por el backend.
Nunca considerar el frontend una barrera de seguridad suficiente.

## 8. Orden de desarrollo
No implementar el frontend de una funcionalidad mientras su backend
no esté completo de punta a punta.
Esto incluye dominio, casos de uso, repositorios, endpoints, validaciones,
permisos, errores, migraciones necesarias y pruebas.
No dejar backend pendiente para después.

## 9. Diseño
Crear los prototipos dentro de design/.
No implementar una vista del producto sin aprobación explícita de su
prototipo vigente.
Registrar las aprobaciones en docs/DESIGN_APPROVALS.md.
La aprobación de arquitectura no equivale a aprobación visual.
Respetar los tokens y la identidad visual aprobados.

## 10. UX/UI, accesibilidad y responsividad
Aplica a los diseños ya aceptados (de forma retroactiva), a los prototipos nuevos
y al proyecto final. Son obligatorios los estándares de UX/UI, usabilidad,
accesibilidad y diseño responsivo y adaptativo.

Versiones por dispositivo:
- Cada prototipo incluye versiones adaptadas para Android, iPhone (iOS), tablets,
  laptops, computadoras de escritorio, monitores LCD, televisores y otros
  dispositivos compatibles.
- Si una propuesta tiene alternativas (A, B, C, etc.), cada una dispone de sus propias
  versiones responsivas y conserva su identidad visual, estructura y funcionalidades.
  No basta con adaptar la alternativa elegida ni mostrar solo la versión de escritorio.

Rangos de ancho de referencia (dp, pt o píxeles CSS según la plataforma):
compacto (menos de 600), mediano (600-839), expandido (840-1199),
grande (1200-1599) y extragrande (1600 en adelante). Pueden ajustarse según el
contenido real y el framework. El diseño se adapta a resoluciones, orientaciones y
métodos de interacción (táctil, puntero, teclado, control remoto), reorganizando
los elementos sin desbordamientos, superposiciones ni pérdida de funcionalidades.

Implementación responsiva:
- Respetar la arquitectura, los patrones, las convenciones y las tecnologías del
  proyecto. En aplicaciones nativas, usar los mecanismos adaptativos del framework.
- Priorizar componentes reutilizables, Design Tokens centralizados, CSS Grid, Flexbox,
  unidades relativas, clamp() y Container Queries cuando correspondan.
- Usar Media Queries solo cuando estén justificadas; evitar su proliferación,
  duplicación y dispersión.
- No introducir parches CSS acumulativos, valores arbitrarios, !important injustificado,
  estilos redundantes ni cambios arquitectónicos innecesarios.
- Reutilizar componentes y estilos compartidos sin perder las diferencias visuales
  entre alternativas.

Accesibilidad:
- Botón o panel de accesibilidad visible, consistente y funcional en todas las
  versiones, con ajuste del tamaño del texto, mejora del contraste y reducción de
  animaciones, sin sustituir las herramientas nativas de accesibilidad.
- Cumplir WCAG 2.2 nivel AA: legibilidad, navegación por teclado, lectores de pantalla,
  controles táctiles accesibles, foco visible, etiquetas y contraste, y navegación con
  control remoto en televisores.
- Mantener coherencia visual, jerarquía de contenidos y experiencia consistente entre
  dispositivos.

Proceso:
- Usar la skill interna /design, cuando esté disponible, al crear, evaluar, mejorar e
  implementar diseños.
- Antes de modificar una interfaz, analizar la arquitectura y las soluciones existentes
  para evitar duplicaciones, regresiones y cambios innecesarios.
- Verificar los tamaños y navegadores definidos en la arquitectura y los rangos de
  referencia, en cada prototipo y alternativa, antes de darlos por terminados.
  No dar una vista por terminada si falla en alguno de ellos.

## 11. Iconografía
Usar exclusivamente iconos SVG revisados.
No utilizar emojis en interfaz, código, commits ni documentación.
Las fotografías de productos no se consideran iconos.

## 12. Incertidumbres
Preguntar antes de implementar una decisión de negocio ambigua o un cambio
no cubierto por la arquitectura aprobada.
No inventar productos reales, precios, teléfonos, políticas comerciales
ni credenciales.
Las decisiones técnicas ya aprobadas no requieren confirmación repetida.

## 13. Esquema de base de datos
Los modelos SQLAlchemy son la única fuente de verdad del esquema.
Modificar el esquema exclusivamente mediante migraciones Alembic
generadas desde los modelos y revisadas antes de aplicarlas.
No alterar tablas manualmente.
No usar create_all para crear el esquema, tampoco en pruebas.
No editar migraciones ya aplicadas; crear una nueva migración correctiva.

## 14. Inventario y carrito
Usar Decimal para dinero y mililitros.
El backend determina precios, totales y disponibilidad.
La marca manual de agotado prevalece sobre existencias positivas.
El carrito y el checkout incompleto no vencen, no reservan y no descuentan inventario.
Crear un pedido pendiente no equivale a confirmar un pago.
Solo la validación del pago por el administrador permite registrar una salida de inventario.
La primera aprobación con existencias obtiene el stock. Un pago real sin existencias
queda como incidencia para coordinar por WhatsApp, sin movimientos parciales ni saldos negativos.
Conservar la cotización firmada de una transferencia ya realizada aunque cambien precios
o disponibilidad antes de enviar el comprobante; registrarla no confirma la venta.
Los estados y transiciones del pedido se configuran en PostgreSQL y en el panel,
sin permitir que una etiqueta de estado omita las comprobaciones de pago e inventario.
Registrar ajustes de existencias con motivo, actor e idempotencia.
El propietario autorizó pedidos persistentes, revisión manual de transferencias,
pago coordinado por WhatsApp y seguimiento; no introducir cobros automáticos.

## 15. Seguridad y dependencias
Aplicar las diez categorías OWASP documentadas.
No guardar secretos en código, documentación, registros ni ejemplos.
No exponer contraseñas, cookies o tokens en mensajes de error.
Mantener uv.lock y bun.lock.
Justificar dependencias nuevas y consultar las que alteren la arquitectura
o añadan capacidades no aprobadas.

## 16. Verificación y cierre
Ejecutar las comprobaciones pertinentes antes de declarar terminado.
Informar qué cambió, qué se verificó y cualquier limitación real.
No afirmar que una prueba pasó si no se ejecutó.
Actualizar documentación cuando cambie un contrato aprobado.
Trabajar solo en ejecución local durante esta etapa.

## 17. Servidores locales y migraciones
No detener, reiniciar ni reemplazar los servidores de backend y frontend que el
propietario tenga levantados.
Para revisar o probar, usar el backend del propietario y levantar otro servidor de
frontend en un puerto libre; detenerlo al terminar.
Las pruebas que necesiten datos propios (existencias, pedidos) usan una base y
servidores temporales, nunca la base del propietario.
Las migraciones Alembic que requieran los cambios propios se generan desde los
modelos, se revisan y se aplican a la base local sin pedir confirmación adicional;
siguen vigentes las reglas del apartado 13.
