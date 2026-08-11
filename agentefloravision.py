# -*- coding: utf-8 -*-
"""
agentefloravision.py — FloraVision
Agente inteligente de pricing y gestión de inventario floral.

Ciclo del agente:
    Percibir → Razonar → Actuar → Reportar

Uso desde Streamlit (floravision.py):
    from agentefloravision import AgenteFloraVision
    agente = AgenteFloraVision()
    agente.percibir("rosa", [0.1, 0.8, 0.1], cantidad=5)
    reporte = agente.obtener_reporte_dict()
"""

import datetime

# ---------------------------------------------------------------------------
# PRECIOS BASE (editables por el dueño según temporada) — en RD$
# ---------------------------------------------------------------------------
PRECIOS_BASE = {
    "rosa":      50,
    "girasol":   40,
    "margarita": 25,
    "clavel":    30,
    "lirio":     60,
    "orquidea":  120,
    "tulipan":   70,
}

# ---------------------------------------------------------------------------
# REGLAS DE DETERIORO Y DESCUENTOS
# (nombre, deterioro_min, deterioro_max, pct_descuento)
# ---------------------------------------------------------------------------
REGLAS = [
    ("Fresca",           0.00, 0.25,   0),
    ("Deterioro leve",   0.25, 0.50,  20),
    ("Deterioro severo", 0.50, 0.75,  50),
    ("Pérdida",          0.75, 1.01, 100),
]

# Mapeo de estado → badge semántico para el frontend
ESTADO_A_BADGE = {
    "Fresca":           "Saludable",
    "Deterioro leve":   "Riesgo",
    "Deterioro severo": "Riesgo",
    "Pérdida":          "Enferma",
}


# ---------------------------------------------------------------------------
# FUNCIÓN DE CÁLCULO DE PRECIO
# ---------------------------------------------------------------------------
def calcular_precio(tipo_flor: str, probabilidades: list) -> dict | None:
    """
    Recibe el tipo de flor y las probabilidades o nivel de deterioro [prob_fresca, prob_deteriorada, prob_perdida].
    """
    tipo_flor = tipo_flor.lower()
    if tipo_flor not in PRECIOS_BASE:
        return None

    precio_base = PRECIOS_BASE[tipo_flor]
    
    # Nivel de deterioro (0.0 a 1.0)
    if len(probabilidades) >= 3:
        # Suma ponderada de deterioro
        nivel_deterioro = probabilidades[1] * 0.5 + probabilidades[2] * 1.0
    else:
        nivel_deterioro = probabilidades[0]

    estado, descuento = "Pérdida", 100

    for nombre, minimo, maximo, pct in REGLAS:
        if minimo <= nivel_deterioro < maximo:
            estado, descuento = nombre, pct
            break

    precio_final = precio_base * (1 - descuento / 100)

    return {
        "tipo_flor":       tipo_flor.capitalize(),
        "precio_base":     precio_base,
        "nivel_deterioro": nivel_deterioro,
        "estado":          estado,
        "badge":           ESTADO_A_BADGE.get(estado, "Riesgo"),
        "descuento":       descuento,
        "precio_final":    precio_final,
    }


# ---------------------------------------------------------------------------
# AGENTE FLORAVISION
# ---------------------------------------------------------------------------
class AgenteFloraVision:
    """
    Agente inteligente que gestiona el inventario floral.
    Ciclo: Percibir → Razonar → Actuar → Reportar
    """

    def __init__(self):
        self.historial: list[dict] = []
        self.alertas:   list[str]  = []

    # ------------------------------------------------------------------
    def percibir(self, tipo_flor: str, probabilidades: list, cantidad: int = 1):
        """
        PASO 1: Recibe información de la cámara/IA.

        Parámetros
        ----------
        tipo_flor     : nombre de la flor
        probabilidades: [prob_fresca, prob_deteriorada, prob_perdida]
        cantidad      : número de tallos evaluados
        """
        resultado = calcular_precio(tipo_flor, probabilidades)
        if resultado is None:
            return None
        resultado["cantidad"]  = cantidad
        resultado["timestamp"] = datetime.datetime.now().strftime("%H:%M:%S")
        resultado["fecha"]     = str(datetime.date.today())
        self.razonar(resultado)
        return resultado

    # ------------------------------------------------------------------
    def razonar(self, datos: dict):
        """PASO 2: Evalúa el estado y decide qué hacer."""
        estado    = datos["estado"]
        tipo_flor = datos["tipo_flor"]
        ts        = datos["timestamp"]

        if estado == "Fresca":
            datos["decision"]     = "mantener"
            datos["recomendacion"] = f"{tipo_flor} en buen estado. Precio normal: RD$ {datos['precio_final']:.2f}"

        elif estado == "Deterioro leve":
            datos["decision"]     = "descuento"
            datos["recomendacion"] = (
                f"{tipo_flor} con deterioro leve. "
                f"Descuento {datos['descuento']}% → RD$ {datos['precio_final']:.2f}. Vender hoy."
            )

        elif estado == "Deterioro severo":
            datos["decision"]     = "descuento_urgente"
            datos["recomendacion"] = (
                f"{tipo_flor} con deterioro severo. "
                f"Descuento {datos['descuento']}% → RD$ {datos['precio_final']:.2f}. Vender URGENTE."
            )
            self.alertas.append(
                f"[{ts}] URGENTE: {tipo_flor} necesita venderse hoy con 50% descuento."
            )

        else:  # Pérdida
            datos["decision"]     = "retirar"
            datos["recomendacion"] = f"{tipo_flor} no apta para venta. Retirar del inventario."
            self.alertas.append(
                f"[{ts}] PÉRDIDA: {datos['cantidad']} tallo(s) de {tipo_flor} retirados."
            )

        self.actuar(datos)

    # ------------------------------------------------------------------
    def actuar(self, datos: dict):
        """PASO 3: Registra la decisión en el historial."""
        self.historial.append(datos)

    # ------------------------------------------------------------------
    def obtener_reporte_dict(self) -> dict:
        """
        PASO 4: Devuelve el resumen del día como dict (para el frontend).
        """
        if not self.historial:
            return {
                "total_tallos": 0,
                "frescas": 0, "con_descuento": 0, "perdidas": 0,
                "dinero_normal": 0.0,
                "dinero_recuperable": 0.0,
                "dinero_perdido": 0.0,
                "alertas": [],
                "historial": [],
            }

        perdidas      = [f for f in self.historial if f["decision"] == "retirar"]
        con_descuento = [f for f in self.historial if "descuento" in f["decision"]]
        frescas       = [f for f in self.historial if f["decision"] == "mantener"]

        return {
            "total_tallos":      sum(f["cantidad"] for f in self.historial),
            "frescas":           sum(f["cantidad"] for f in frescas),
            "con_descuento":     sum(f["cantidad"] for f in con_descuento),
            "perdidas":          sum(f["cantidad"] for f in perdidas),
            "dinero_normal":     sum(f["precio_final"] * f["cantidad"] for f in frescas),
            "dinero_recuperable":sum(f["precio_final"] * f["cantidad"] for f in con_descuento),
            "dinero_perdido":    sum(f["precio_base"]  * f["cantidad"] for f in perdidas),
            "alertas":           list(self.alertas),
            "historial":         list(self.historial),
        }

    # ------------------------------------------------------------------
    def inventario_agrupado(self) -> dict:
        """
        Agrupa el historial por tipo de flor para la tabla de inventario.
        Retorna dict con listas paralelas: Planta, Cantidad, Estado, Precio.
        """
        agrupado: dict[str, dict] = {}
        for entrada in self.historial:
            flor = entrada["tipo_flor"]
            if flor not in agrupado:
                agrupado[flor] = {
                    "cantidad": 0,
                    "estado": entrada["badge"],
                    "precio_final": entrada["precio_final"],
                    "descuento": entrada["descuento"],
                }
            agrupado[flor]["cantidad"]    += entrada["cantidad"]
            # Conservar el peor estado detectado
            orden = {"Saludable": 0, "Riesgo": 1, "Enferma": 2}
            if orden.get(entrada["badge"], 0) > orden.get(agrupado[flor]["estado"], 0):
                agrupado[flor]["estado"]      = entrada["badge"]
                agrupado[flor]["precio_final"] = entrada["precio_final"]
                agrupado[flor]["descuento"]    = entrada["descuento"]

        return {
            "Planta":      list(agrupado.keys()),
            "Cantidad":    [v["cantidad"]    for v in agrupado.values()],
            "Estado":      [v["estado"]      for v in agrupado.values()],
            "Precio":      [v["precio_final"] for v in agrupado.values()],
            "Descuento":   [v["descuento"]   for v in agrupado.values()],
        }