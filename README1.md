# FloraVision - Pricing Engine + Agente Inteligente
Anny De La Rosa

## ¿Qué hace este módulo?

Este módulo recibe los resultados del modelo de visión por computadora y toma decisiones automáticas sobre el precio y estado de cada flor.

El agente sigue un ciclo de 4 pasos:

1. **Percibe** — recibe el tipo de flor, las probabilidades de deterioro y la cantidad de tallos
2. **Razona** — evalúa el estado según las reglas del negocio
3. **Actúa** — decide si mantener precio, aplicar descuento o retirar la flor
4. **Reporta** — al final del día genera un resumen automático de pérdidas y ganancias

## Reglas de deterioro

| Estado | Deterioro | Descuento |
|--------|-----------|-----------|
| Fresca | 0% — 30%  | Sin desc. |
| Leve   | 30% — 60% | 20%       |
| Severo | 60% — 70% | 50%       |
| Perdida|mas de 70% | Retirar   |


## Como conectar con el resto del proyecto

Cuando el modelo de vision detecte una flor, llama al agente asi:

```python
from agente_floravision import AgenteFloraVision

agente = AgenteFloraVision()

# tipo_flor: string con el nombre de la flor
# probabilidades: [prob_fresca, prob_deteriorada, prob_perdida]
# cantidad: numero de tallos evaluados

agente.percibir("rosa", [0.1, 0.8, 0.1], 5)
```

# Al final del dia, para generar el reporte:

```python
agente.generar_reporte()
```

## Flores disponibles

Las siguientes flores estan configuradas con precios base en pesos dominicanos (RD$). El dueno puede editarlos en el archivo segun temporada:
Estos precios son ejemplos.

- Rosa — RD$ 50.00
- Girasol — RD$ 40.00
- Margarita — RD$ 25.00
- Clavel — RD$ 30.00
- Lirio — RD$ 60.00
- Orquidea — RD$ 120.00
- Tulipan — RD$ 70.00

## Ejemplo de reporte generado

```
        REPORTE DIARIO - FLORAVISION
        Fecha: 2025-05-06

Total de tallos evaluados: 50
En buen estado:            24 tallos
Con descuento:             19 tallos
Perdidas:                   7 tallos

Ingresos a precio normal:  RD$ 1,100.00
Ingresos con descuento:    RD$ 256.00
Perdidas del dia:          RD$ 965.00
Total recuperable hoy:     RD$ 1,356.00
```
