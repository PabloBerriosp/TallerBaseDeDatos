# Taller de Base de Datos — Hito 1

**Sistema de consolidación y seguimiento económico de eventos masivos**  
Universidad de Santiago de Chile · Semestre 2 de 2026  
Integrantes: Pablo Berríos, Julio Paz y Fernando Ríos · Docente: José Guerra

El proyecto integra información económica de conciertos: versiones presupuestarias, gastos y sus respaldos, pagos, ingresos, ventas de entradas y liquidaciones. Mantiene una identidad por gasto para evitar duplicar costos y distingue el resultado económico de los movimientos de caja. Las causas de desviación presupuestaria permiten explicar cambios respecto del modelo de Booking.

## Entregables

| Carpeta | Contenido |
| --- | --- |
| `informe/` | Informe de 16 páginas en PDF, fuente editable Word y versión de texto Markdown. |
| `diagramas/bpmn/` | Proceso BPMN-lite en PNG de alta resolución y SVG editable. |
| `diagramas/eer/` | EER completo en una sola lámina PNG/SVG, con todas las relaciones, atributos e ISA; PDF A0 horizontal. Las tres láminas anteriores se conservan como detalle adicional. |
| `diagramas/relacional/` | Modelo relacional completo en PNG, SVG y PDF A1 horizontal de una página. |
| `fuentes/` | Definición de las 18 tablas en JSON, tipos SQL propuestos, trazado de conectores y escudo institucional. |
| `fuentes/scripts/` | Scripts Python editables para regenerar los diagramas. |
| `consultas/` | Cuatro consultas de álgebra relacional, incluida división. |

## Edición

El informe se puede editar en [Google Docs](https://docs.google.com/document/d/10YTneW6CfLN2tug6HjoBff-TBpN5N1X93UIoitroPQA) o con `informe/informe_hito1.docx`. Los SVG son archivos vectoriales editables y conservan nitidez al ampliar. El esquema estructurado está en `fuentes/modelo_relacional.json`.

Los PNG principales tienen estas dimensiones: BPMN 1200 × 1480; EER completo 7500 × 4275; modelo relacional 6195 × 2457 píxeles. El EER usa distribución Chen con líneas rectas y atributos alrededor de cada entidad. Para revisar todas las relaciones use `diagramas/eer/eer_completo.svg`.

## Regenerar diagramas

Los scripts usan las fuentes Arial de Windows y se ejecutan desde la raíz del repositorio, con Python 3:

```powershell
python -m pip install -r fuentes/requirements.txt
python fuentes/scripts/generar_bpmn_eer.py
python fuentes/scripts/generar_modelo_relacional.py
python fuentes/scripts/generar_eer_completo.py
```

La regeneración de diagramas no modifica automáticamente el informe: las figuras actualizadas deben insertarse en Word o Google Docs y luego exportarse a PDF.

## Alcance de este hito

Este repositorio entrega el diseño de negocio, procesos y datos. Los tipos SQL son propuestas de diseño; todavía no se incluye una implementación del motor ni scripts DDL.
