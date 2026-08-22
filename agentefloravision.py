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
# ---------------------------------------------------------------------------
# REGLAS DE DETERIORO Y DESCUENTOS
# (nombre, deterioro_min, deterioro_max, pct_descuento)
# Umbrales actualizados: < 50% = Fresca/Saludable, 50%-80% = Riesgo, >= 80% = Pérdida/Enferma
# ---------------------------------------------------------------------------
REGLAS = [
    ("Fresca",           0.00, 0.50,   0),
    ("Deterioro leve",   0.50, 0.80,  30),
    ("Pérdida",          0.80, 1.01, 100),
]

# Mapeo de estado → badge semántico para el frontend
ESTADO_A_BADGE = {
    "Fresca":           "Saludable",
    "Deterioro leve":   "Riesgo",
    "Pérdida":          "Enferma",
}

MAPEO_NORMALIZACION = {
    "rosa": "rosa",
    "erosa": "rosa",
    "rosas": "rosa",
    "girasol": "girasol",
    "girasoles": "girasol",
    "margarita": "margarita",
    "margaritas": "margarita",
    "clavel": "clavel",
    "claveles": "clavel",
    "lirio": "lirio",
    "lirios": "lirio",
    "orquidea": "orquidea",
    "orquídea": "orquidea",
    "orquideas": "orquidea",
    "tulipan": "tulipan",
    "tulipán": "tulipan",
    "tulipanes": "tulipan",
}

MAPEO_NORMALIZACION_CAPITALIZADO = {
    "rosa": "Rosa",
    "erosa": "Rosa",
    "rosas": "Rosa",
    "girasol": "Girasol",
    "girasoles": "Girasol",
    "margarita": "Margarita",
    "margaritas": "Margarita",
    "clavel": "Clavel",
    "claveles": "Clavel",
    "lirio": "Lirio",
    "lirios": "Lirio",
    "orquidea": "Orquídea",
    "orquídea": "Orquídea",
    "orquideas": "Orquídea",
    "tulipan": "Tulipán",
    "tulipán": "Tulipán",
    "tulipanes": "Tulipán",
}


# ---------------------------------------------------------------------------
# FUNCIÓN DE CÁLCULO DE PRECIO
# ---------------------------------------------------------------------------
def calcular_precio(tipo_flor: str, probabilidades: list) -> dict | None:
    """
    Recibe el tipo de flor y las probabilidades o nivel de deterioro [prob_fresca, prob_deteriorada, prob_perdida].
    Normaliza automáticamente errores tipográficos comunes (ej. 'erosa' -> 'rosa', 'girasoles' -> 'girasol').
    """
    tipo_clean = tipo_flor.lower().strip() if tipo_flor else "rosa"
    tipo_flor_norm = MAPEO_NORMALIZACION.get(tipo_clean, tipo_clean)

    if tipo_flor_norm not in PRECIOS_BASE:
        return None

    precio_base = PRECIOS_BASE[tipo_flor_norm]
    
    # Nivel de deterioro (0.0 a 1.0)
    if isinstance(probabilidades, (float, int)):
        nivel_deterioro = float(probabilidades)
        if nivel_deterioro > 1.0:
            nivel_deterioro /= 100.0
    elif len(probabilidades) >= 3:
        if probabilidades[2] > 0.5:
            nivel_deterioro = 0.85
        elif probabilidades[1] > 0.5:
            nivel_deterioro = 0.58
        else:
            nivel_deterioro = 1.0 - probabilidades[0]
    else:
        nivel_deterioro = float(probabilidades[0])

    estado, descuento = "Pérdida", 100

    for nombre, minimo, maximo, pct in REGLAS:
        if minimo <= nivel_deterioro < maximo:
            estado, descuento = nombre, pct
            break

    precio_final = precio_base * (1 - descuento / 100)
    nombre_cap = MAPEO_NORMALIZACION_CAPITALIZADO.get(tipo_flor_norm, tipo_flor_norm.capitalize())

    return {
        "tipo_flor":       nombre_cap,
        "precio_base":     precio_base,
        "nivel_deterioro": nivel_deterioro,
        "estado":          estado,
        "badge":           ESTADO_A_BADGE.get(estado, "Riesgo"),
        "descuento":       descuento,
        "precio_final":    precio_final,
        "porcentaje_marchito": nivel_deterioro,
    }


from database import DatabaseManager


# ---------------------------------------------------------------------------
# AGENTE FLORAVISION
# ---------------------------------------------------------------------------
class AgenteFloraVision:
    """
    Agente inteligente que gestiona el inventario floral.
    Ciclo: Percibir → Razonar → Actuar → Reportar
    Conectado a Base de Datos SQLite3 (floravision.db) para persistencia de datos.
    """

    def __init__(self):
        self.db = DatabaseManager()
        self.historial: list[dict] = self.db.obtener_inventario()
        self.alertas:   list[str]  = self.db.obtener_alertas()
        self.feedback_log: list[dict] = []

    # ------------------------------------------------------------------
    def recargar_desde_bd(self):
        """Vuelve a cargar los datos almacenados desde SQLite3."""
        self.historial = self.db.obtener_inventario()
        self.alertas   = self.db.obtener_alertas()

    # ------------------------------------------------------------------
    def vaciar_inventario(self):
        """Elimina todos los registros guardados en SQLite3 y en memoria."""
        self.db.vaciar_inventario()
        self.historial = []
        self.alertas = []

    # ------------------------------------------------------------------
    def percibir(self, tipo_flor: str, probabilidades: list, cantidad: int = 1, imagen_b64: str | None = None):
        """
        PASO 1: Recibe información de la cámara/IA.

        Parámetros
        ----------
        tipo_flor     : nombre de la flor
        probabilidades: [prob_fresca, prob_deteriorada, prob_perdida]
        cantidad      : número de tallos evaluados
        imagen_b64    : string Base64 con la foto capturada (opcional)
        """
        resultado = calcular_precio(tipo_flor, probabilidades)
        if resultado is None:
            return None
        resultado["cantidad"]   = cantidad
        resultado["timestamp"]  = datetime.datetime.now().strftime("%H:%M:%S")
        resultado["fecha"]      = str(datetime.date.today())
        if imagen_b64:
            resultado["imagen_b64"] = imagen_b64

        self.razonar(resultado)
        return resultado

    # ------------------------------------------------------------------
    def razonar(self, datos: dict):
        """PASO 2: Evalúa el estado y decide las recomendaciones."""
        estado    = datos["estado"]
        tipo_flor = datos["tipo_flor"]
        ts        = datos["timestamp"]

        if estado == "Fresca":
            datos["decision"]     = "mantener"
            datos["recomendacion"] = f"{tipo_flor} en buen estado. Precio normal: RD$ {datos['precio_final']:.2f}"

        elif estado == "Deterioro leve":
            datos["decision"]     = "descuento"
            datos["recomendacion"] = (
                f"{tipo_flor} en estado de riesgo. "
                f"Descuento {datos['descuento']}% → RD$ {datos['precio_final']:.2f}. Vender hoy."
            )

        else:  # Pérdida
            datos["decision"]     = "retirar"
            datos["recomendacion"] = f"{tipo_flor} no apta para venta. Retirar del inventario."

    # ------------------------------------------------------------------
    def actuar(self, datos: dict):
        """PASO 3: Registra formalmente la decisión en el inventario de SQLite3."""
        row_id = self.db.guardar_flor(datos)
        datos["id"] = row_id
        self.historial.append(datos)

        ts = datos.get("timestamp", "")
        tipo_flor = datos.get("tipo_flor", "")
        estado = datos.get("estado", "")
        if estado == "Deterioro leve":
            alerta = f"[{ts}] RIESGO: {tipo_flor} necesita venderse hoy con {datos.get('descuento', 30)}% descuento."
            self.alertas.append(alerta)
            self.db.guardar_alerta(alerta, ts)
        elif estado == "Pérdida":
            alerta = f"[{ts}] PÉRDIDA: {datos.get('cantidad', 1)} tallo(s) de {tipo_flor} retirados del inventario."
            self.alertas.append(alerta)
            self.db.guardar_alerta(alerta, ts)

    # ------------------------------------------------------------------
    def registrar_feedback(self, especie_predicha: str, especie_correcta: str, loss: float = 0.0):
        """Registra un evento de aprendizaje por refuerzo y lo guarda en SQLite3."""
        self.db.guardar_feedback(especie_predicha, especie_correcta, loss)
        self.feedback_log.append({
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
            "prediccion_ia": especie_predicha,
            "corregida": especie_correcta,
            "recompensa": -1.0 if especie_predicha.lower() != especie_correcta.lower() else 1.0,
            "loss": loss
        })

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
                "correcciones_refuerzo": len(self.feedback_log),
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
            "correcciones_refuerzo": len(self.feedback_log),
        }

    # ------------------------------------------------------------------
    def inventario_agrupado(self) -> dict:
        """
        Agrupa el historial por tipo de flor para la tabla de inventario.
        Normaliza nombres (ej. 'erosa' -> 'Rosa', 'girasoles' -> 'Girasol').
        Retorna dict con listas paralelas: Planta, Cantidad, Estado, Precio, Descuento, Imagen.
        """
        agrupado: dict[str, dict] = {}
        for entrada in self.historial:
            raw_flor = entrada.get("tipo_flor", "Rosa")
            flor_norm = MAPEO_NORMALIZACION_CAPITALIZADO.get(raw_flor.lower().strip(), raw_flor.capitalize())
            
            if flor_norm not in agrupado:
                agrupado[flor_norm] = {
                    "cantidad": 0,
                    "estado": entrada.get("badge", "Saludable"),
                    "precio_final": entrada.get("precio_final", 50.0),
                    "descuento": entrada.get("descuento", 0),
                    "porcentaje_marchito": entrada.get("porcentaje_marchito", 0.0),
                    "imagen_b64": entrada.get("imagen_b64"),
                    "timestamp": entrada.get("timestamp", "--:--"),
                }
            agrupado[flor_norm]["cantidad"] += entrada.get("cantidad", 1)
            
            if entrada.get("imagen_b64"):
                agrupado[flor_norm]["imagen_b64"] = entrada["imagen_b64"]

            orden = {"Saludable": 0, "Riesgo": 1, "Enferma": 2}
            if orden.get(entrada.get("badge", "Saludable"), 0) > orden.get(agrupado[flor_norm]["estado"], 0):
                agrupado[flor_norm]["estado"]              = entrada.get("badge", "Saludable")
                agrupado[flor_norm]["precio_final"]        = entrada.get("precio_final", 50.0)
                agrupado[flor_norm]["descuento"]           = entrada.get("descuento", 0)
                agrupado[flor_norm]["porcentaje_marchito"] = entrada.get("porcentaje_marchito", 0.0)

            agrupado[flor_norm]["timestamp"] = entrada.get("timestamp", "--:--")

        return {
            "Planta":              list(agrupado.keys()),
            "Cantidad":            [v["cantidad"]            for v in agrupado.values()],
            "Estado":              [v["estado"]              for v in agrupado.values()],
            "Precio":              [v["precio_final"]        for v in agrupado.values()],
            "Descuento":           [v["descuento"]           for v in agrupado.values()],
            "PorcentajeMarchito":  [v["porcentaje_marchito"] for v in agrupado.values()],
            "Imagen":              [v["imagen_b64"]          for v in agrupado.values()],
            "Timestamp":           [v["timestamp"]           for v in agrupado.values()],
        }

    # ------------------------------------------------------------------
    def obtener_items_inventario_normalizados(self) -> list[dict]:
        """Retorna una lista de items de inventario consolidados y normalizados."""
        dict_agrupado = self.inventario_agrupado()
        items = []
        for i in range(len(dict_agrupado["Planta"])):
            items.append({
                "tipo_flor": dict_agrupado["Planta"][i],
                "cantidad": dict_agrupado["Cantidad"][i],
                "estado": dict_agrupado["Estado"][i],
                "badge": dict_agrupado["Estado"][i],
                "precio_final": dict_agrupado["Precio"][i],
                "descuento": dict_agrupado["Descuento"][i],
                "porcentaje_marchito": dict_agrupado["PorcentajeMarchito"][i],
                "imagen_b64": dict_agrupado["Imagen"][i],
                "timestamp": dict_agrupado["Timestamp"][i],
                "fecha": str(datetime.date.today()),
            })
        return items