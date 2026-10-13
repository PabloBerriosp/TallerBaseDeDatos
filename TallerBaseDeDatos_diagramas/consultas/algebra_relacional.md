Semántica de conjuntos: σ selecciona; π proyecta; ρ renombra; ⋈ es join natural; ⋈θ es theta join; − es diferencia; ÷ es división. Los subíndices entre llaves indican atributos o predicados. p, t, d1 y d2 son parámetros. Las proyecciones previas al join natural conservan solo las claves comunes deseadas.

Consulta 1 — Gastos fuera del canal de compras

Obtener gastos validados del evento p con al menos un antecedente de Rinde Gastos o tarjeta. Los documentos repetidos sobre la misma operación no multiplican el resultado.

R ← π_{id_gasto}(σ_{estado='VINCULADO' ∧ (fuente='RINDE_GASTOS' ∨ fuente='TARJETA')}(REGISTRO_ORIGEN))

G ← σ_{codigo_proyecto=p ∧ estado='VALIDADO'}(GASTO)

Resultado ← π_{id_gasto,descripcion,monto_clp}(G ⋈ R)

Consulta 2 — Gastos sin ningún pago

Obtener gastos validados del evento p que no registran pagos. Esta consulta de ausencia no devuelve pagos parciales ni calcula saldos.

G ← σ_{codigo_proyecto=p ∧ estado='VALIDADO'}(GASTO)

I ← π_{id_gasto}(G) − π_{id_gasto}(PAGO_GASTO)

Resultado ← π_{id_gasto,descripcion,monto_clp}(G ⋈ I)

La diferencia opera sobre relaciones del mismo esquema (id_gasto). Si G tiene gastos g1 y g2 y solo g1 aparece en pagos, el resultado devuelve g2. Un pago parcial de g1 basta para excluirlo de esta consulta.

Consulta 3 — Honorarios en conciertos de estadio

Obtener las personas y gastos a honorarios validados de shows en estadios dentro del intervalo [d1,d2). El monto corresponde al costo incurrido, no prueba que esté pagado.

E ← ρ_E(π_{codigo_proyecto,id_recinto,nombre}(σ_{fecha_show≥d1 ∧ fecha_show<d2}(EVENTO)))

R ← ρ_R(π_{id_recinto}(σ_{tipo_recinto='ESTADIO'}(RECINTO)))

G ← ρ_G(π_{codigo_proyecto,id_contraparte,monto_clp}(σ_{tipo_gasto='HONORARIOS' ∧ estado='VALIDADO'}(GASTO)))

P ← ρ_P(PERSONA_NATURAL)

J ← ((E ⋈_{E.id_recinto=R.id_recinto} R) ⋈_{E.codigo_proyecto=G.codigo_proyecto} G) ⋈_{G.id_contraparte=P.id_contraparte} P

Resultado ← π_{E.codigo_proyecto,E.nombre,P.nombres,P.apellidos,G.monto_clp}(J)

Consulta 4 — Contrapartes presentes en TODOS los shows seleccionados

Encontrar contrapartes con al menos un gasto validado en todos los eventos cerrados de tipo t del período [d1,d2). El conjunto S debe ser no vacío; si no hay eventos se informa “sin eventos comparables”.

S ← π_{codigo_proyecto}(σ_{estado='CERRADO' ∧ tipo_show=t ∧ fecha_show≥d1 ∧ fecha_show<d2}(EVENTO))

V ← π_{id_contraparte,codigo_proyecto}(σ_{estado='VALIDADO'}(GASTO))

R ← V ⋈ S; Q ← R ÷ S

Resultado ← π_{id_contraparte,nombre}(CONTRAPARTE ⋈ Q)

R tiene esquema (id_contraparte, codigo_proyecto), S tiene (codigo_proyecto) y Q tiene (id_contraparte). Con S={EV01,EV02} y R={(CP01,EV01),(CP01,EV02),(CP02,EV01)}, R ÷ S={CP01}. Repetir gastos de CP02 en EV01 no satisface la cobertura de EV02.