| UNIVERSIDAD DE SANTIAGO DE CHILE Facultad de Ingeniería Departamento de Ingeniería Informática |  |
| --- | --- |

Sistema de consolidación y seguimiento económico de eventos masivos

Hito 1: Negocio, procesos y modelo conceptual formal

Taller de Base de Datos

Semestre 2 de 2026

Integrantes

Pablo Berríos

Julio Paz

Fernando Ríos

Docente

José Guerra

Santiago, Chile

2026

## 1. Contexto de negocio y alcance

La Productora de Eventos organiza conciertos en teatros, centros de eventos, estadios y parques. Booking negocia con artistas y propone el modelo económico inicial; Marketing promociona el show, Producción realiza el montaje, Auspicios obtiene aportes de marcas y Legal revisa contratos y permisos. Finanzas administra presupuestos, contabilidad y tesorería. RRHH gestiona contrataciones, especialmente prestadores a honorarios por proyecto.

La información está distribuida entre SAP Business One, el sistema de compras, Rinde Gastos, documentos de servicios extranjeros pagados con tarjeta y plataformas de ticketeras. Contabilidad reúne y carga antecedentes y Tesorería los revisa. Un mismo gasto puede aparecer en más de una fuente, mientras otros quedan fuera del control presupuestario de compras. Esto retrasa los informes, expone a duplicación de costos y dificulta explicar desviaciones respecto del modelo de Booking o comparar shows similares.

El sistema propuesto utiliza un código común de proyecto y una identidad única para cada gasto económico. Conserva el presupuesto original y sus revisiones. Distingue costos incurridos de pagos y ventas de entradas de transferencias de caja. Una desviación genera una alerta documentada; no reescribe la línea base ni convierte el gasto en inexistente.

| Dentro del alcance | Fuera del alcance |
| --- | --- |
| Eventos, artistas, recintos y contrapartes. | Venta, emisión y control de acceso de entradas. |
| Presupuesto original y revisiones completas por categoría. | Reemplazar SAP, contabilidad tributaria o ejecutar pagos. |
| Gastos y respaldos de compras, tarjeta, rendiciones y honorarios; pagos asociados. | Gestión integral de compras, nómina permanente, reclutamiento y firma de contratos. |
| Ingresos monetarios por auspicios; cortes de ventas, liquidaciones y adelantos. | Campañas de marketing, aportes en especie y desarrollo de integraciones productivas. |
| Conciliación, seguimiento económico y consultas históricas. | Gestión de compromisos aún no incurridos; se consideran en las revisiones completas del presupuesto. |

Condiciones de operación: todas las fuentes usan el código de proyecto; los importes se comparan en CLP y netos de impuestos recuperables; cada línea documental identifica su fuente, documento y número de línea. Un evento puede usar varias ticketeras y cada par tiene una liquidación final. La autenticación corporativa entrega identidades y roles de preparador y revisor; su administración queda fuera del alcance.

## 1.1. Objetivos y gobernanza

Objetivo general: diseñar una base relacional que consolide la información económica de cada show, preserve su evolución presupuestaria y permita consultar resultados comparables sin duplicar operaciones.

| ID | Objetivo SMART y mecanismo | Meta y plazo |
| --- | --- | --- |
| O1 | Reducir el tiempo de preparación del corte mediante fuentes unificadas y consultas de datos validados. | De 120 a ≤84 minutos (−30 %) al terminar ocho semanas de operación. |
| O2 | Asegurar trazabilidad mediante documento, evento, categoría y revisión independiente. | 100 % de gastos validados completos desde la cuarta semana; cero duplicados en 20 casos de control al terminar el piloto de ocho semanas. |
| O3 | Conservar la línea base y revisiones para explicar desviaciones e historia. | 100 % de eventos con presupuesto original y revisiones validadas conservadas desde la cuarta semana. |

## Mapa de interesados

| Interesado | Interés y participación | Influencia |
| --- | --- | --- |
| Gerencia y Finanzas | Rentabilidad y exposición; aprueban alcance e indicadores. | Alta |
| Contabilidad y Tesorería | Conciliación y caja; validan proceso, reglas y resultados. | Alta |
| Booking y Producción | Proyección y ejecución; aportan presupuesto y antecedentes. | Alta |
| RRHH, Auspicios, Marketing y Legal | Costos por proyecto, ingresos y respaldos; consultados en el diseño. | Media |
| Ticketeras y prestadores | Entregan cortes, liquidaciones y documentos. | Media |

## Priorización MoSCoW

| Prioridad | Requisitos |
| --- | --- |
| Must | M1 eventos y catálogos; M2 presupuestos versionados; M3 gasto único y documentos; M4 revisión separada; M5 pagos; M6 ingresos y ticketing; M7 seguimiento y consultas históricas. |
| Should | S1 alertas de desviación; S2 filtros por artista, recinto y tipo de show. |
| Could | C1 exportar reportes y comparar series de indicadores. |
| Won’t | W1 venta de entradas, nómina completa, ejecución bancaria e integraciones productivas. |

## 1.2. RACI y límites del proceso

R ejecuta; A responde y aprueba; C es consultado; I es informado. El patrocinador es Gerencia; el usuario clave es Finanzas; arquitecto y desarrollador pertenecen al equipo del proyecto. Cada actividad tiene exactamente un A.

| Actividad | Sponsor | Finanzas | Arq. BD | Dev. BD | Contab. | Tesorería |
| --- | --- | --- | --- | --- | --- | --- |
| Validar alcance | A | R | C | I | C | C |
| Acordar importes y reglas | I | A | C | I | R | C |
| Diseñar modelos | I | A | R | C | C | C |
| Implementar restricciones | I | C | A | R | C | C |
| Probar conciliación | I | A | C | R | R | C |
| Evaluar piloto | A | R | C | C | C | C |
| Preparar entrega | I | C | A | R | I | I |

## 2. Arquitectura de procesos — SIPOC

| Proveedor | Entrada | Proceso | Salida | Cliente |
| --- | --- | --- | --- | --- |
| Booking / Finanzas | Modelo inicial y revisiones. | Identificar show y conservar presupuesto. | Línea base y revisiones validadas. | Finanzas / Gerencia |
| Áreas / RRHH / compras | Documentos, rendiciones y honorarios. | Recibir, identificar y conciliar gasto. | Gastos únicos y observaciones. | Contabilidad / Tesorería |
| Ticketeras / Auspicios | Cortes, liquidaciones, adelantos y aportes. | Registrar ingresos y movimientos de caja. | Ingresos y transferencias separados. | Finanzas / Tesorería |
| Contabilidad / Tesorería | Registros revisados. | Validar y consolidar seguimiento. | Resultado y desviaciones. | Gerencia / responsables |

El proceso comienza con la identificación del show y su presupuesto. Cada antecedente se concilia y revisa antes de incorporarse al consolidado. Los casos incompletos o de identidad incierta permanecen fuera del resultado. El cierre del ciclo produce una consulta económica con ingresos, costos y caja diferenciados. Las tareas del BPMN siguiente se utilizan sin cambios de ID en la matriz CRUD.

## 2.1. BPMN-lite del proceso principal

Piscina: Productora de Eventos. Carriles: Área originadora, Contabilidad y Tesorería. G1, G2 y G3 son XOR. La ruta conforme recorre T01–T10; T11 registra excepciones. La información corregida reinicia la recepción. El ciclo de recepción se repite por cada antecedente del evento.

## 2.2. Catálogo de reglas DCA

| ID / disparador | Condición | Acción del motor |
| --- | --- | --- |
| RGN01 · Resolver origen (G1). | Proyecto inexistente o incompleto; código distinto del gasto vinculado. | Rechazar vínculo; dejar PENDIENTE y registrar PROYECTO_INVALIDO. |
| RGN02 · Cargar documento (G1). | Repetida la combinación fuente, documento y línea. | Impedir inserción con UNIQUE y remitir al origen existente. |
| RGN03 · Conciliar gasto (G2). | La revisión encuentra un gasto ya registrado o identidad incierta. | Vincular al existente; ante duda, conservar pendiente y solicitar aclaración. |
| RGN04 · Revisar gasto (G3). | Falta respaldo, categoría de gasto, monto positivo o revisor autorizado distinto del preparador. | Rechazar validación; registrar observación y excluir del consolidado. |
| RGN05 · Cambiar presupuesto. | Versión validada. | Rechazar modificación de versión y líneas; exigir nueva revisión. |
| RGN06 · Registrar pago. | Gasto no validado, monto ≤0 o pagos acumulados superiores al gasto. | Rechazar; bloquear el gasto y verificar saldo en una transacción. |
| RGN07 · Registrar honorarios. | tipo_gasto=HONORARIOS y contraparte no es PersonaNatural o falta contrato. | Rechazar el gasto por CONTRATACION_INVALIDA. |
| RGN08 · Registrar ticketing. | Corte repetido o negativo; liquidación repetida por par; movimiento imputado a otro par o sobre el neto final. | Rechazar operación; un adelanto queda sin imputar hasta existir liquidación. |
| RGN09 · Registrar ingreso. | Categoría de gasto o concepto de entradas ya representado en ticketing. | Rechazar para evitar clasificación o ingreso duplicado. |
| RGN10 · Consolidar show. | Costo incurrido o estimación revisada supera la línea base. | Emitir alerta con causa; conservar presupuesto original y gasto validado. |

Correspondencia: G1 → RGN01–02; G2 → RGN03; G3 → RGN04. RGN05–10 protegen las tareas de presupuesto, movimientos y seguimiento. PK, FK, UNIQUE y CHECK resguardan identidad, referencias y dominios. Triggers y transacciones controlan inmutabilidad, revisión y saldos. RGN03 incorpora una decisión humana documentada: la unicidad por fuente no detecta por sí sola el mismo gasto entre sistemas.

## 2.3. Matriz CRUD con trazabilidad

C crea, R consulta, U modifica y — no interviene. Anular información financiera corresponde a U. Los tres bloques son una misma matriz: las filas son exactamente T01–T11 del BPMN y las columnas cubren las 18 tablas resultantes, incluyendo subtipos, entidad débil, relación M:N y multivalorado.

| Tarea | Evento | Recinto | Artista | Evento– Artista | Categoría | Versión presup. |
| --- | --- | --- | --- | --- | --- | --- |
| T01 | CRU | R | CRU | CRU | R | CRU |
| T02 | — | — | — | — | — | — |
| T03 | R | — | — | — | — | — |
| T04 | R | — | — | — | — | — |
| T05 | R | — | — | — | R | — |
| T06 | R | — | — | — | R | — |
| T07 | R | — | — | — | R | — |
| T08 | R | — | — | — | R | — |
| T09 | R | — | — | — | R | — |
| T10 | R | R | R | R | R | R |
| T11 | — | — | — | — | — | — |

| Tarea | Contraparte | Persona natural | Organización | Causas desviación | Línea presup. | Gasto |
| --- | --- | --- | --- | --- | --- | --- |
| T01 | CRU | CRU | CRU | — | CRU | — |
| T02 | — | — | — | — | — | — |
| T03 | — | — | — | — | — | — |
| T04 | — | — | — | — | — | — |
| T05 | R | R | R | — | — | R |
| T06 | CRU | CRU | CRU | — | — | CR |
| T07 | R | R | R | — | — | R |
| T08 | R | R | R | — | — | RU |
| T09 | CRU | CRU | CRU | — | — | R |
| T10 | R | R | R | CRU | R | R |
| T11 | — | — | — | — | — | U |

| Tarea | Origen | Pago | Ingreso | Corte venta | Liquidación | Movimiento |
| --- | --- | --- | --- | --- | --- | --- |
| T01 | — | — | — | — | — | — |
| T02 | — | — | — | — | — | — |
| T03 | C | — | — | — | — | — |
| T04 | RU | — | — | — | — | — |
| T05 | R | — | — | — | — | — |
| T06 | U | — | — | — | — | — |
| T07 | R | — | — | — | — | — |
| T08 | RU | — | — | — | — | — |
| T09 | — | C | CU | C | C | CU |
| T10 | R | R | R | R | R | R |
| T11 | U | — | — | — | — | — |

Evento–Artista representa la participación; Causas de desviación materializa el multivalorado del evento. Los subtipos comparten operaciones de su contraparte. T01 consulta recintos y categorías. T02 entrega el respaldo sin escribir en BD. T10 registra causas al revisar desviaciones; no persiste totales derivados.

## 2.4. KPIs y lectura económica

## KPI 1 — Desviación del costo incurrido

Objetivo: detectar sobrecostos respecto de Booking. Fórmula: 100 × (costo incurrido − presupuesto original de costos) / presupuesto original de costos. Fuentes: GASTO(codigo_proyecto, estado, monto_clp), VERSION_PRESUPUESTO(id_version, codigo_proyecto, numero, estado), LINEA_PRESUPUESTO(id_version, id_categoria, monto_clp) y CATEGORIA(id_categoria, naturaleza). Umbral: ≤5 %; una desviación mayor genera alerta para revisión semanal de Finanzas. Antes de concluir el evento el indicador es provisional. Si el presupuesto original es cero se informa “sin base” y el costo se revisa como excepción.

## KPI 2 — Cobertura documental del gasto validado

Objetivo: comprobar trazabilidad. Fórmula: 100 × gastos VALIDADO con al menos un origen VINCULADO, misma asignación de evento y preparador distinto del revisor / total de gastos VALIDADO. Fuentes: GASTO(id_gasto, codigo_proyecto, estado, preparado_por, revisado_por), REGISTRO_ORIGEN(id_gasto, codigo_proyecto, estado, referencia_documento). Meta: 100 % desde la cuarta semana. Si no existen gastos validados se informa “sin base”, no 100 %. Se cuenta cada gasto una vez, aunque tenga varios documentos.

## Criterios de cálculo del seguimiento

Costo incurrido = suma de gastos validados; pagos = suma de PAGO_GASTO. Saldo de gasto = monto del gasto menos sus pagos. Presupuesto original = líneas de costos o ingresos de la versión validada número 1; estimación revisada = líneas de la última versión validada. Cada revisión estima el total del evento, incluyendo lo incurrido: no se suma otra vez el costo real a esa estimación.

Ticketing: para cada evento y ticketera se toma el último corte acumulado disponible; nunca se suman cortes sucesivos. Una liquidación final sustituye el neto estimado de ese par. Ingreso económico = ticketing neto más ingresos monetarios validados de otros conceptos. Resultado económico = ingreso económico menos costo incurrido. Antes de liquidar se presenta como seguimiento provisional. Adelantos y saldos transferidos afectan caja y no agregan otro ingreso.

Ejemplos de control: una compra de 50 registrada en compras y SAP produce un costo de 50. Una liquidación neta de 100 con adelanto de 30 produce ingreso de 100 y saldo de ticketera de 70. Se valida además que dos pagos concurrentes no excedan el saldo de un mismo gasto.

## 3. Diseño conceptual extendido

El modelo contiene 13 entidades fuertes conectadas al evento: Recinto, Artista, Evento, Contraparte, Categoria, VersionPresupuesto, Gasto, RegistroOrigen, PagoGasto, Ingreso, CorteVenta, Liquidacion y MovimientoTicketera. LineaPresupuesto es débil: existe e identifica sus líneas únicamente dentro de una versión. PersonaNatural y Organizacion especializan Contraparte de manera total y disjunta.

| Grupo | Identificación y razón del diseño |
| --- | --- |
| Evento y catálogos | Código de proyecto único. Recinto identifica ubicación y capacidad; Artista conserva identidad reutilizable. Evento–Artista es M:N y guarda orden y honorario estimado. |
| Presupuesto | VersionPresupuesto tiene id propio y número único por evento. LineaPresupuesto usa clave parcial nro_linea; su clave completa es (id_version, nro_linea). Categoria permite clasificar costos e ingresos. |
| Contrapartes y honorarios | PersonaNatural y Organizacion comparten la clave de Contraparte. Los honorarios son gastos de persona natural con referencia de contrato; sueldos permanentes quedan fuera del alcance. |
| Gasto y documento | Gasto representa la operación económica. RegistroOrigen representa una línea documental; varias líneas de diferentes fuentes pueden acreditar un solo gasto. Una línea se vincula a cero o un gasto mientras se concilia. |
| Ingreso y caja | PagoGasto registra abonos; Ingreso registra conceptos distintos de entradas. CorteVenta conserva fotografías acumuladas; Liquidacion determina el neto final y MovimientoTicketera registra adelantos o saldos. |

El EER completo se presenta en una sola lámina: cada entidad aparece una vez, con sus atributos, todas las relaciones, cardinalidades y especialización. Las FKs se expresan como relaciones conceptuales. El SVG y el PDF ampliado permiten revisar el detalle.

Notación Chen: rectángulo = entidad fuerte; doble rectángulo = débil; rombo = relación; doble rombo = relación identificadora; óvalo = atributo; subrayado = clave; subrayado discontinuo = clave parcial; doble óvalo = multivalorado; óvalo discontinuo = derivado; triángulo ISA = especialización.

## 3.1. Modelo entidad–relación completo

Abrir modelo entidad–relación completo en formato ampliado

Evento tiene causas_desviacion multivaluado. Las causas identificadas en T10 se almacenan una vez por evento. resultado_final y saldo_gasto son derivados; la dirección es compuesta y Evento–Artista posee atributos de relación.

## 4.1. Esquema relacional — Eventos y presupuestos

Notación: * = FK; ? = opcional; PK = clave primaria; UQ = clave alternativa. Los atributos son atómicos; los importes se expresan en CLP. Una relación 1:N propaga la clave al lado N; M:N crea una tabla con PK compuesta; cada subtipo comparte PK y FK con su supertipo.

RECINTO(id_recinto, nombre, tipo_recinto, calle, numero, comuna, ciudad, capacidad)

PK: (id_recinto).

ARTISTA(id_artista, nombre_artistico, tipo_acto)

PK: (id_artista).

EVENTO(codigo_proyecto, id_recinto*, nombre, tipo_show, fecha_show, aforo_plan, estado)

PK: (codigo_proyecto).

FK: (id_recinto) → RECINTO(id_recinto).

EVENTO_ARTISTA(codigo_proyecto*, id_artista*, orden_presentacion, honorario_estimado_clp)

PK: (codigo_proyecto, id_artista).

FK: (codigo_proyecto) → EVENTO(codigo_proyecto).

FK: (id_artista) → ARTISTA(id_artista).

CONTRAPARTE(id_contraparte, nombre, identificador, pais)

PK: (id_contraparte); UQ: (pais, identificador).

PERSONA_NATURAL(id_contraparte*, nombres, apellidos)

PK: (id_contraparte).

FK: (id_contraparte) → CONTRAPARTE(id_contraparte).

ORGANIZACION(id_contraparte*, razon_social)

PK: (id_contraparte).

FK: (id_contraparte) → CONTRAPARTE(id_contraparte).

CAUSA_DESVIACION_EVENTO(codigo_proyecto*, causa)

PK: (codigo_proyecto, causa).

FK: (codigo_proyecto) → EVENTO(codigo_proyecto).

CATEGORIA(id_categoria, codigo, nombre, naturaleza)

PK: (id_categoria); UQ: (codigo).

VERSION_PRESUPUESTO(id_version, codigo_proyecto*, numero, fecha_corte, estado, preparado_por, validado_por?, fecha_validacion?)

PK: (id_version); UQ: (codigo_proyecto, numero).

FK: (codigo_proyecto) → EVENTO(codigo_proyecto).

## 4.2. Esquema relacional — Costos, ingresos y caja

LINEA_PRESUPUESTO(id_version*, nro_linea, id_categoria*, descripcion, monto_clp)

PK: (id_version, nro_linea).

FK: (id_version) → VERSION_PRESUPUESTO(id_version).

FK: (id_categoria) → CATEGORIA(id_categoria).

GASTO(id_gasto, codigo_proyecto*, id_contraparte*, id_categoria*, fecha_incurrido, monto_clp, tipo_gasto, referencia_contrato?, descripcion, estado, preparado_por, revisado_por?, fecha_revision?, motivo_anulacion?)

PK: (id_gasto).

FK: (codigo_proyecto) → EVENTO(codigo_proyecto).

FK: (id_contraparte) → CONTRAPARTE(id_contraparte).

FK: (id_categoria) → CATEGORIA(id_categoria).

REGISTRO_ORIGEN(id_registro, fuente, id_externo, nro_linea, codigo_recibido?, codigo_proyecto*?, fecha_documento, monto_documentado_clp, referencia_documento, estado, observacion?, cargado_por, revisado_por?, id_gasto*?)

PK: (id_registro); UQ: (fuente, id_externo, nro_linea).

FK: (codigo_proyecto) → EVENTO(codigo_proyecto).

FK: (id_gasto) → GASTO(id_gasto).

PAGO_GASTO(id_pago, id_gasto*, fecha_pago, monto_clp, referencia, registrado_por)

PK: (id_pago); UQ: (referencia).

FK: (id_gasto) → GASTO(id_gasto).

INGRESO(id_ingreso, codigo_proyecto*, id_contraparte*, id_categoria*, fecha, monto_reconocido_clp, concepto, estado, registrado_por)

PK: (id_ingreso).

FK: (codigo_proyecto) → EVENTO(codigo_proyecto).

FK: (id_contraparte) → CONTRAPARTE(id_contraparte).

FK: (id_categoria) → CATEGORIA(id_categoria).

CORTE_VENTA(id_corte_venta, codigo_proyecto*, id_ticketera*, instante, entradas_acumuladas, bruto_acumulado_clp, neto_estimado_acumulado_clp)

PK: (id_corte_venta); UQ: (codigo_proyecto, id_ticketera, instante).

FK: (codigo_proyecto) → EVENTO(codigo_proyecto).

FK: (id_ticketera) → ORGANIZACION(id_contraparte).

LIQUIDACION(id_liquidacion, codigo_proyecto*, id_ticketera*, fecha, neto_final_clp, referencia)

PK: (id_liquidacion); UQ: (codigo_proyecto, id_ticketera).

FK: (codigo_proyecto) → EVENTO(codigo_proyecto).

FK: (id_ticketera) → ORGANIZACION(id_contraparte).

MOVIMIENTO_TICKETERA(id_movimiento, codigo_proyecto*, id_ticketera*, fecha, tipo, monto_clp, referencia, id_liquidacion*?)

PK: (id_movimiento); UQ: (id_ticketera, referencia).

FK: (codigo_proyecto) → EVENTO(codigo_proyecto).

FK: (id_ticketera) → ORGANIZACION(id_contraparte).

FK: (id_liquidacion) → LIQUIDACION(id_liquidacion).

La FK comprueba existencia; las coincidencias de evento entre origen, gasto, liquidación y movimiento requieren restricciones transaccionales. Los estados son dominios cerrados. Un corte puede disminuir por devoluciones; la liquidación es única por evento/ticketera. No se almacenan saldos ni resultados derivados.

## 4.3. Modelo relacional gráfico completo

Abrir modelo relacional completo en formato ampliado

## 5. Consultas formales — Selección y diferencia

Semántica de conjuntos: σ selecciona; π proyecta; ρ renombra; ⋈ es join natural; ⋈θ es theta join; − es diferencia; ÷ es división. Los subíndices entre llaves indican atributos o predicados. p, t, d1 y d2 son parámetros. Las proyecciones previas al join natural conservan solo las claves comunes deseadas.

## Consulta 1 — Gastos fuera del canal de compras

Obtener gastos validados del evento p con al menos un antecedente de Rinde Gastos o tarjeta. Los documentos repetidos sobre la misma operación no multiplican el resultado.

R ← π_{id_gasto}(σ_{estado='VINCULADO' ∧ (fuente='RINDE_GASTOS' ∨ fuente='TARJETA')}(REGISTRO_ORIGEN))

G ← σ_{codigo_proyecto=p ∧ estado='VALIDADO'}(GASTO)

Resultado ← π_{id_gasto,descripcion,monto_clp}(G ⋈ R)

## Consulta 2 — Gastos sin ningún pago

Obtener gastos validados del evento p que no registran pagos. Esta consulta de ausencia no devuelve pagos parciales ni calcula saldos.

G ← σ_{codigo_proyecto=p ∧ estado='VALIDADO'}(GASTO)

I ← π_{id_gasto}(G) − π_{id_gasto}(PAGO_GASTO)

Resultado ← π_{id_gasto,descripcion,monto_clp}(G ⋈ I)

La diferencia opera sobre relaciones del mismo esquema (id_gasto). Si G tiene gastos g1 y g2 y solo g1 aparece en pagos, el resultado devuelve g2. Un pago parcial de g1 basta para excluirlo de esta consulta.

## 5.1. Consultas formales — Theta join y división

## Consulta 3 — Honorarios en conciertos de estadio

Obtener las personas y gastos a honorarios validados de shows en estadios dentro del intervalo [d1,d2). El monto corresponde al costo incurrido, no prueba que esté pagado.

E ← ρ_E(π_{codigo_proyecto,id_recinto,nombre}(σ_{fecha_show≥d1 ∧ fecha_show<d2}(EVENTO)))

R ← ρ_R(π_{id_recinto}(σ_{tipo_recinto='ESTADIO'}(RECINTO)))

G ← ρ_G(π_{codigo_proyecto,id_contraparte,monto_clp}(σ_{tipo_gasto='HONORARIOS' ∧ estado='VALIDADO'}(GASTO)))

P ← ρ_P(PERSONA_NATURAL)

J ← ((E ⋈_{E.id_recinto=R.id_recinto} R) ⋈_{E.codigo_proyecto=G.codigo_proyecto} G) ⋈_{G.id_contraparte=P.id_contraparte} P

Resultado ← π_{E.codigo_proyecto,E.nombre,P.nombres,P.apellidos,G.monto_clp}(J)

## Consulta 4 — Contrapartes presentes en TODOS los shows seleccionados

Encontrar contrapartes con al menos un gasto validado en todos los eventos cerrados de tipo t del período [d1,d2). El conjunto S debe ser no vacío; si no hay eventos se informa “sin eventos comparables”.

S ← π_{codigo_proyecto}(σ_{estado='CERRADO' ∧ tipo_show=t ∧ fecha_show≥d1 ∧ fecha_show<d2}(EVENTO))

V ← π_{id_contraparte,codigo_proyecto}(σ_{estado='VALIDADO'}(GASTO))

R ← V ⋈ S; Q ← R ÷ S

Resultado ← π_{id_contraparte,nombre}(CONTRAPARTE ⋈ Q)

R tiene esquema (id_contraparte, codigo_proyecto), S tiene (codigo_proyecto) y Q tiene (id_contraparte). Con S={EV01,EV02} y R={(CP01,EV01),(CP01,EV02),(CP02,EV01)}, R ÷ S={CP01}. Repetir gastos de CP02 en EV01 no satisface la cobertura de EV02.

## 6. Conclusión y referencias

La base propuesta reúne información económica dispersa mediante el código de proyecto y distingue la operación de sus documentos. La revisión independiente reduce el riesgo de duplicar costos; las versiones permiten explicar cambios respecto del presupuesto original. Los honorarios por show participan como gastos trazables y el ticketing separa recaudación, ingreso final y caja.

El diseño conecta gobernanza, proceso, reglas, CRUD y métricas con un EER y su transformación formal. Las consultas permiten identificar gastos de canales externos, obligaciones sin pagos, costos de honorarios y contrapartes presentes en toda una cartera comparable. La implementación posterior deberá materializar las restricciones transaccionales y comprobarlas con los casos de control descritos.

## Referencias del curso

[1] Taller de Base de Datos. Enunciado Hito 1: Negocio, Procesos y Modelo Conceptual Formal. USACH, semestre 2-2026.

[2] Taller de Base de Datos. Clases 1, partes 1, 2, C, D y E: modelado de datos y fundamentos relacionales. USACH, semestre 2-2026.

[3] Taller de Base de Datos. Clase 2A y clase 3: negocio, requisitos y procesos. USACH, semestre 2-2026.

[4] Taller de Base de Datos. Clases 4 y 4B; repasos 1 y 2. USACH, semestre 2-2026.
