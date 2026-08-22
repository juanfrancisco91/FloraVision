# -*- coding: utf-8 -*-
"""
analisis_imagen.py — FloraVision
Módulo de análisis de marchitamiento por visión por computadora.

Extrae la lógica HSV de cv_taskbar.py como función pura reutilizable
desde Streamlit sin ventanas OpenCV (no usa cv2.imshow ni VideoCapture).

Uso:
    from feature-capture.analisis_imagen import analizar_marchitamiento
    pct = analizar_marchitamiento(imagen_np)
"""

import cv2 as cv
import numpy as np
import os
import json


# ---------------------------------------------------------------------------
# Parámetros HSV predefinidos por tipo de estado de flor
# (Ajustables según el entorno de luz)
# ---------------------------------------------------------------------------
HSV_SANA = {
    "h_min": 20,  "s_min": 50,  "v_min": 50,
    "h_max": 85,  "s_max": 255, "v_max": 255,
}


def hex_a_rangos_hsv(hex_str: str) -> dict:
    """
    Convierte un código de color HEX (ej. '#E60000') en rangos HSV para OpenCV.
    Retorna un diccionario con h_min, h_max, s_min, s_max, v_min, v_max.
    """
    try:
        clean_hex = hex_str.lstrip("#")
        if len(clean_hex) == 6:
            r = int(clean_hex[0:2], 16)
            g = int(clean_hex[2:4], 16)
            b = int(clean_hex[4:6], 16)
        else:
            r, g, b = 230, 0, 0
    except Exception:
        r, g, b = 230, 0, 0

    pixel_bgr = np.uint8([[[b, g, r]]])
    pixel_hsv = cv.cvtColor(pixel_bgr, cv.COLOR_BGR2HSV)[0][0]

    h, s, v = int(pixel_hsv[0]), int(pixel_hsv[1]), int(pixel_hsv[2])

    h_min = max(0, h - 18)
    h_max = min(179, h + 18)

    s_min = max(30, s - 60)
    s_max = 255
    v_min = max(30, v - 60)
    v_max = 255

    if h <= 10 or h >= 170:
        h_min, h_max = 170, 10

    return {
        "h_min": h_min, "h_max": h_max,
        "s_min": s_min, "s_max": s_max,
        "v_min": v_min, "v_max": v_max,
    }


def analizar_marchitamiento(
    imagen_np: np.ndarray,
    h_min: int = HSV_SANA["h_min"],
    s_min: int = HSV_SANA["s_min"],
    v_min: int = HSV_SANA["v_min"],
    h_max: int = HSV_SANA["h_max"],
    s_max: int = HSV_SANA["s_max"],
    v_max: int = HSV_SANA["v_max"],
    es_bgr: bool = True,
) -> dict:
    """
    Analiza una imagen NumPy y devuelve el porcentaje de marchitamiento.
    """
    # Si la imagen no está en BGR, realizar la conversión correspondiente
    if not es_bgr:
        if imagen_np.shape[2] == 4:          # RGBA → BGR
            imagen_np = cv.cvtColor(imagen_np, cv.COLOR_RGBA2BGR)
        else:                                 # RGB → BGR
            imagen_np = cv.cvtColor(imagen_np, cv.COLOR_RGB2BGR)

    hsv = cv.cvtColor(imagen_np, cv.COLOR_BGR2HSV)
    _, S, _ = cv.split(hsv)

    # --- 1. Máscara de pétalos sanos (color seleccionado de la flor) ---
    if h_min <= h_max:
        bajo  = np.array([h_min, s_min, v_min])
        alto  = np.array([h_max, s_max, v_max])
        mascara_petalos = cv.inRange(hsv, bajo, alto)
    else:
        # Modo dual para rojo (el espacio HSV envuelve el rojo)
        m1 = cv.inRange(hsv, np.array([0,      s_min, v_min]), np.array([h_max,  s_max, v_max]))
        m2 = cv.inRange(hsv, np.array([h_min,  s_min, v_min]), np.array([179,    s_max, v_max]))
        mascara_petalos = cv.bitwise_or(m1, m2)

    # --- 2. Máscara de hojas y tallo sanos (Verde en HSV: H: 35..85, S: 30..255, V: 30..255) ---
    mascara_hojas = cv.inRange(hsv, np.array([35, 30, 30]), np.array([85, 255, 255]))

    # --- 3. Máscara sana total = Pétalos sanos + Hojas/Tallo sanos ---
    mascara_sana = cv.bitwise_or(mascara_petalos, mascara_hojas)

    # --- 4. Molde total de la flor/planta (Saturación y brillo significativos de la planta) ---
    s_suave = cv.GaussianBlur(S, (7, 7), 0)
    _, gris_total = cv.threshold(s_suave, 30, 255, cv.THRESH_BINARY)
    kernel = np.ones((7, 7), np.uint8)
    gris_total = cv.morphologyEx(gris_total, cv.MORPH_CLOSE, kernel)

    # --- 5. Máscara marchita = molde de la planta − partes sanas ---
    mascara_marchita = cv.bitwise_and(gris_total, cv.bitwise_not(mascara_sana))

    # --- Cálculo exacto de áreas por recuento de píxeles ---
    area_total = float(np.count_nonzero(gris_total))
    area_marchita = float(np.count_nonzero(mascara_marchita))

    porcentaje_raw = (area_marchita / area_total * 100.0) if area_total > 0 else 0.0
    porcentaje_marchito = min(100.0, max(0.0, porcentaje_raw))

    return {
        "porcentaje_marchito": round(porcentaje_marchito, 1),
        "area_total":          round(area_total,   1),
        "area_marchita":       round(area_marchita, 1),
    }


def convertir_a_probabilidades(porcentaje_marchito: float) -> list:
    """
    Convierte el porcentaje de marchitamiento (0–100%) al formato de probabilidades
    esperado por AgenteFloraVision: [prob_fresca, prob_deteriorada, prob_perdida].

    Umbrales:
    - 0% a 50%: Fresca / Saludable
    - 50% a 80%: Deteriorada / En Riesgo
    - >= 80%: Pérdida / Enferma
    """
    p = max(0.0, min(100.0, porcentaje_marchito)) / 100.0  # 0.0 a 1.0

    if p < 0.50:
        return [1.0 - p, p * 0.2, 0.0]
    elif p < 0.80:
        frac = (p - 0.50) / 0.30
        return [0.1 * (1.0 - frac), 0.8, 0.1 + 0.8 * frac]
    else:
        return [0.0, 0.1, 0.9]


# ---------------------------------------------------------------------------
# INFERENCIA Y CLASIFICACIÓN CON MODELO DE DEEP LEARNING (MobileNetV2 / ResNet50)
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# INFERENCIA Y CLASIFICACIÓN CON MODELO DE DEEP LEARNING (MobileNetV2 / ResNet50)
# ---------------------------------------------------------------------------
_MODELO_IA_CACHE = None
_FEEDBACK_MEMORY = {}
CLASES_FLORES = ["Rosa", "Girasol", "Margarita", "Clavel", "Lirio", "Orquídea", "Tulipán"]

RUTA_MEMORIA_JSON = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "feedback_memory.json")


def calcular_hash_imagen(imagen_np: np.ndarray) -> str:
    """
    Calcula un Perceptual dHash (difference hash) de 64 bits para una imagen NumPy.
    Invariante ante compresión JPEG, leves cambios de tamaño o contraste.
    """
    try:
        if len(imagen_np.shape) == 3 and imagen_np.shape[2] == 4:
            gris = cv.cvtColor(imagen_np, cv.COLOR_RGBA2GRAY)
        elif len(imagen_np.shape) == 3:
            gris = cv.cvtColor(imagen_np, cv.COLOR_BGR2GRAY)
        else:
            gris = imagen_np

        resized = cv.resize(gris, (9, 8), interpolation=cv.INTER_AREA)
        diff = resized[:, 1:] > resized[:, :-1]
        
        # Generar entero de 64-bit como string
        hash_val = 0
        for i, val in enumerate(diff.flatten()):
            if val:
                hash_val |= (1 << i)
        return str(hash_val)
    except Exception:
        return str(hash(imagen_np.tobytes()))


def cargar_memoria_refuerzo() -> dict:
    """Carga el registro persistente de correcciones humanas por refuerzo desde JSON."""
    global _FEEDBACK_MEMORY
    if _FEEDBACK_MEMORY:
        return _FEEDBACK_MEMORY

    if os.path.exists(RUTA_MEMORIA_JSON):
        try:
            import json
            with open(RUTA_MEMORIA_JSON, "r", encoding="utf-8") as f:
                _FEEDBACK_MEMORY = json.load(f)
        except Exception as e:
            print(f"⚠️ Error cargando feedback_memory.json: {e}")
            _FEEDBACK_MEMORY = {}
    return _FEEDBACK_MEMORY


def guardar_memoria_refuerzo():
    """Guarda la memoria de correcciones por refuerzo en feedback_memory.json."""
    global _FEEDBACK_MEMORY
    try:
        import json
        with open(RUTA_MEMORIA_JSON, "w", encoding="utf-8") as f:
            json.dump(_FEEDBACK_MEMORY, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Error guardando feedback_memory.json: {e}")


def cargar_modelo_ia():
    """
    Intenta cargar el modelo Keras entrenado (.keras o .h5) desde el directorio raíz.
    Devuelve la instancia del modelo o None si aún no se ha entrenado.
    """
    global _MODELO_IA_CACHE
    if _MODELO_IA_CACHE is not None:
        return _MODELO_IA_CACHE

    try:
        import tensorflow as tf
    except Exception as err_tf:
        print(f"⚠️ TensorFlow no disponible: {err_tf}")
        return None

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    posibles_rutas = [
        os.path.join(base_dir, "modelo_flores.keras"),
        os.path.join(base_dir, "feature-training", "modelo_flores.keras"),
        os.path.join(base_dir, "modelo_flores.h5"),
        os.path.join(base_dir, "feature-training", "modelo_flores.h5"),
    ]

    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            try:
                _MODELO_IA_CACHE = tf.keras.models.load_model(ruta, compile=False, safe_mode=False)
                return _MODELO_IA_CACHE
            except Exception as e:
                print(f"⚠️ Error cargando modelo desde {ruta}: {e}")

    return None


def clasificar_flor_ia(imagen_np: np.ndarray) -> dict:
    """
    Clasifica una imagen NumPy RGB/BGR con el modelo Deep Learning preentrenado
    combinado con el registro persistente de Aprendizaje por Refuerzo.
    """
    if imagen_np is None or imagen_np.size == 0:
        return {
            "modelo_activo": False,
            "especie": None,
            "confianza": 0.0,
            "probabilidades": {}
        }

    # 1. VERIFICAR MEMORIA DE APRENDIZAJE POR REFUERZO HUMANO (Perceptual Hash)
    memoria = cargar_memoria_refuerzo()
    h_img_str = calcular_hash_imagen(imagen_np)

    # 1A. Coincidencia directa de Hash
    if h_img_str in memoria:
        especie_memorizada = memoria[h_img_str]
        prob_dict = {cls: (100.0 if cls == especie_memorizada else 0.0) for cls in CLASES_FLORES}
        return {
            "modelo_activo": True,
            "especie": especie_memorizada,
            "confianza": 100.0,
            "corregido_por_refuerzo": True,
            "probabilidades": prob_dict
        }

    # 1B. Coincidencia por distancia Hamming dHash (similitud visual cercana)
    if h_img_str.isdigit():
        h_val = int(h_img_str)
        for saved_hash, saved_especie in memoria.items():
            if saved_hash.isdigit():
                dist = bin(h_val ^ int(saved_hash)).count('1')
                if dist <= 12:  # Alta similitud perceptual de imagen
                    prob_dict = {cls: (100.0 if cls == saved_especie else 0.0) for cls in CLASES_FLORES}
                    return {
                        "modelo_activo": True,
                        "especie": saved_especie,
                        "confianza": 99.0,
                        "corregido_por_refuerzo": True,
                        "probabilidades": prob_dict
                    }

    # 2. INFERENCIA CON MODELO TENSORFLOW / KERAS DEEP LEARNING
    modelo = cargar_modelo_ia()
    if modelo is None:
        return {
            "modelo_activo": False,
            "especie": None,
            "confianza": 0.0,
            "probabilidades": {}
        }

    try:
        if imagen_np.shape[2] == 4:
            img_rgb = cv.cvtColor(imagen_np, cv.COLOR_RGBA2RGB)
        elif len(imagen_np.shape) == 3 and imagen_np.shape[2] == 3:
            img_rgb = cv.cvtColor(imagen_np, cv.COLOR_BGR2RGB)
        else:
            img_rgb = imagen_np

        img_resized = cv.resize(img_rgb, (224, 224))
        img_tensor = np.expand_dims(img_resized, axis=0)

        predictions = modelo.predict(img_tensor, verbose=0)[0]
        idx_max = int(np.argmax(predictions))
        especie_predicha = CLASES_FLORES[idx_max] if idx_max < len(CLASES_FLORES) else "Desconocida"
        confianza_pct = round(float(predictions[idx_max]) * 100, 1)

        prob_dict = {
            cls: round(float(p) * 100, 1)
            for cls, p in zip(CLASES_FLORES, predictions)
        }

        return {
            "modelo_activo": True,
            "especie": especie_predicha,
            "confianza": confianza_pct,
            "probabilidades": prob_dict
        }
    except Exception as err:
        print(f"⚠️ Error en clasificar_flor_ia: {err}")
        return {
            "modelo_activo": False,
            "especie": None,
            "confianza": 0.0,
            "probabilidades": {}
        }


def aprender_por_refuerzo(imagen_np: np.ndarray, especie_correcta: str) -> dict:
    """
    Aplica aprendizaje por refuerzo y fine-tuning en caliente al modelo de IA
    y registra la huella perceptual de la imagen para garantizar que las correcciones
    prevalezcan inmediatamente y persistan en disco.
    """
    import os
    import time

    especie_norm = especie_correcta.capitalize()
    if especie_norm not in CLASES_FLORES:
        coincidencias = [c for c in CLASES_FLORES if c.lower() == especie_correcta.lower()]
        if coincidencias:
            especie_norm = coincidencias[0]
        else:
            return {"exito": False, "mensaje": f"Especie '{especie_correcta}' no válida."}

    # 1. Registrar dHash Perceptual en la Memoria Persistente de Refuerzo
    h_img_str = calcular_hash_imagen(imagen_np)
    cargar_memoria_refuerzo()
    _FEEDBACK_MEMORY[h_img_str] = especie_norm
    guardar_memoria_refuerzo()

    # 2. Guardar la imagen en el dataset físico de feedback
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dir_feedback = os.path.join(base_dir, "dataset", "feedback", especie_norm.lower())
    os.makedirs(dir_feedback, exist_ok=True)

    timestamp_str = int(time.time())
    ruta_img = os.path.join(dir_feedback, f"feedback_{timestamp_str}.jpg")

    try:
        if len(imagen_np.shape) == 3 and imagen_np.shape[2] == 4:
            img_bgr = cv.cvtColor(imagen_np, cv.COLOR_RGBA2BGR)
        elif len(imagen_np.shape) == 3 and imagen_np.shape[2] == 3:
            img_bgr = cv.cvtColor(imagen_np, cv.COLOR_RGB2BGR) if imagen_np.dtype == np.uint8 else imagen_np
        else:
            img_bgr = imagen_np
        cv.imwrite(ruta_img, img_bgr)
    except Exception as e:
        print(f"⚠️ No se pudo guardar imagen de feedback: {e}")

    # 3. Fine-tuning multiepoch en TensorFlow Keras (si está disponible)
    modelo = cargar_modelo_ia()
    loss_val = 0.0

    if modelo is not None:
        try:
            import tensorflow as tf
            if len(imagen_np.shape) == 3 and imagen_np.shape[2] == 4:
                img_rgb = cv.cvtColor(imagen_np, cv.COLOR_RGBA2RGB)
            elif len(imagen_np.shape) == 3:
                img_rgb = cv.cvtColor(imagen_np, cv.COLOR_BGR2RGB)
            else:
                img_rgb = imagen_np

            img_resized = cv.resize(img_rgb, (224, 224))
            img_tensor = np.expand_dims(img_resized, axis=0)

            # Vector Target One-Hot
            idx_target = CLASES_FLORES.index(especie_norm)
            target_one_hot = np.zeros((1, len(CLASES_FLORES)), dtype=np.float32)
            target_one_hot[0, idx_target] = 1.0

            # Recompilar con Tasa de Aprendizaje Efectiva (1e-3)
            modelo.compile(
                optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
                loss="categorical_crossentropy",
                metrics=["accuracy"]
            )

            # Ejecutar 5 iteraciones de entrenamiento en caliente para forzar la actualización de los pesos
            for _ in range(5):
                res_loss = modelo.train_on_batch(img_tensor, target_one_hot)
                loss_val = float(res_loss[0]) if isinstance(res_loss, (list, np.ndarray)) else float(res_loss)

            # Re-guardar el modelo actualizado en disco
            ruta_keras = os.path.join(base_dir, "modelo_flores.keras")
            ruta_h5 = os.path.join(base_dir, "modelo_flores.h5")
            try:
                modelo.save(ruta_keras)
                modelo.save(ruta_h5)
            except Exception as save_err:
                print(f"⚠️ Error al guardar modelo actualizado: {save_err}")
        except Exception as err:
            print(f"⚠️ Error durante el entrenamiento de TF por refuerzo: {err}")

    return {
        "exito": True,
        "mensaje": f"🧠 Aprendizaje por refuerzo aplicado exitosamente. La flor fue memorizada y corregida a {especie_norm}.",
        "loss": loss_val,
        "muestra_guardada": ruta_img
    }


