# 🌸 FloraVision — Resumen Ejecutivo para Presentación de Diapositivas

> **Descripción General:**  
> **FloraVision** es un sistema integral de **Visión por Computadora**, **Clasificación por Inteligencia Artificial** y **Gestión Autónoma de Inventario Floral y Pricing Dinámico**. Su objetivo principal es automatizar el control de calidad, reducir pérdidas financieras en productos perecederos y optimizar la venta de flores según su estado de salud.

---

## 📌 Estructura Sugerida para la Presentación de Diapositivas

---

### 🎬 Diapositiva 1: Portada
* **Título:** FloraVision: Sistema Inteligente de Monitoreo Floral, Inferencia de IA y Pricing Dinámico
* **Subtítulo:** Automatización del control de marchitamiento y gestión de inventario en tiempo real
* **Puntos clave:**
  - Proyecto de Inteligencia Artificial y Visión por Computadora aplicado al sector agro-comercial.
  - Integración de Deep Learning, OpenCV, Aprendizaje por Refuerzo y Base de Datos SQLite.

---

### ❓ Diapositiva 2: El Problema Comercial
* **El Reto:**
  - Las flores son productos **altamente perecederos** con una vida útil corta.
  - El marchitamiento no detectado a tiempo produce **pérdidas financieras directas**.
  - La evaluación visual humana es **subjetiva, imprecisa y lenta**.
  - No existen mecanismos automáticos para aplicar **descuentos dinámicos** antes de que la flor se pierda por completo.

---

### 💡 Diapositiva 3: La Solución FloraVision
* **Propuesta de Valor:**
  - **Medición Objetiva:** Diagnóstico del porcentaje exacto de marchitamiento mediante procesamiento digital de imágenes (OpenCV + HSV).
  - **Clasificación Automática:** Identificación instantánea de la especie floral mediante redes neuronales de Inteligencia Artificial (MobileNetV2).
  - **Recomendación Inteligente:** Un Agente de Software calcula automáticamente precios normales, ofertas de venta rápida o retiro de inventario.
  - **Aprendizaje Continuo:** El sistema aprende en caliente de las correcciones del operario mediante Aprendizaje por Refuerzo (dHash + Fine-Tuning).

---

### 🛠️ Diapositiva 4: Arquitectura y Stack Tecnológico
* **Frontend y UI:** Streamlit con diseño personalizado en tonos Borgoña (#5C0030), Rosa y Dorado.
* **Procesamiento de Imagen:** OpenCV (conversión HSV, suavizado Gaussiano, umbralización de saturación y cálculo de contornos).
* **Modelo de Inteligencia Artificial:** TensorFlow / Keras (MobileNetV2 / Transfer Learning) + Algoritmo de Huella dHash (Perceptual Hashing de 64 bits).
* **Persistencia de Datos:** Base de Datos SQLite3 (floravision.db) para almacenar el inventario real, alertas y registro de refuerzo.

---

### 👁️ Diapositiva 5: Proceso de Detección e Inferencia
1. **Captura:** Entrada por cámara web en tiempo real o carga de archivos de imagen.
2. **Segmentación HSV:** Separa el color característico de la flor (pétalos) y partes verdes sanas (hojas/tallo) del fondo.
3. **Cálculo de Área y Marchitamiento:**
   Porcentaje de Marchitamiento = (Área Marchita / Área Total de la Planta) * 100
4. **Clasificación de IA:** Predice la especie floral (Rosa, Girasol, Orquídea, Tulipán, Margarita, Clavel, Lirio) con su nivel de confianza.

---

### 🧠 Diapositiva 6: Aprendizaje por Refuerzo (Reinforcement Learning)
* **¿Qué ocurre si la IA se equivoca?**
  - El usuario puede corregir la especie predicha desde la interfaz (ej. seleccionar Girasol en lugar de Margarita).
* **Mecanismo Dual de Aprendizaje:**
  1. **Memoria dHash Perceptual (Respuesta Instantánea):** Guarda el fingerprint de la imagen en feedback_memory.json y SQLite3. Si esa imagen o una similar vuelve a analizarse, se identifica con 100% de confianza.
  2. **Fine-Tuning Neuronal (TensorFlow):** Ejecuta 5 iteraciones de entrenamiento en caliente (train_on_batch) actualizando los pesos del modelo .keras / .h5.

---

### ⚖️ Diapositiva 7: Reglas de Salud y Pricing Dinámico
El sistema clasifica cada planta en 3 categorías según su nivel de deterioro:

| Estado de Salud | % de Marchitamiento | Clasificación / Badge | Acción Comercial & Precio |
| :--- | :---: | :---: | :--- |
| **🟢 Saludable / Fresca** | **0.0% — 49.9%** | Saludable | **Precio Base 100%** (Sin Descuento). |
| **🟡 En Riesgo** | **50.0% — 79.9%** | Riesgo | **Oferta 30% OFF** (Venta Rápida Recomendada). |
| **🔴 Enferma / Pérdida** | **>= 80.0%** | Enferma | **Descuento 100% (No apta venta)** -> Retiro del stock. |

---

### 📦 Diapositiva 8: Inventario Categorizado por Especie y BD SQLite3
* **Diseño del Inventario:**
  - El inventario inicia **completamente limpio desde 0** y solo se alimenta de las flores que el usuario escanea y confirma con el botón "+ Agregar al Inventario".
  - **Organización por Especie:** Cada flor (Rosa 🌹, Girasol 🌻, etc.) posee su propio apartado exclusivo.
  - **Subdivisiones desplegables:** Al hacer clic en una flor, la pantalla despliega 3 columnas de división: **🟢 Stock Sano**, **🟡 Stock en Riesgo** y **🔴 Stock Enfermo**.
* **Persistencia:** Almacenado en floravision.db con opción de vaciado total ("Vaciar Inventario").

---

### 💻 Diapositiva 9: Módulos de la Aplicación (Navegación)
1. **Inicio:** Resumen semanal de stock, barra de distribución de salud y calendario interactivo.
2. **Detección Inteligente:** Procesamiento OpenCV en tiempo real, inferencia IA, panel de refuerzo y guardado en inventario.
3. **Inventario Categorizado:** Visualización de categorías, filtros por precio y estado de salud, divisiones por calidad y foto de referencia.
4. **Dashboard:** Métricas ejecutivas (KPIs), gráficas interactivas con Matplotlib y análisis financiero.
5. **Alertas:** Centro de notificaciones para notificar plantas que requieren venta urgente.

---

### 🚀 Diapositiva 10: Conclusiones e Impacto
* **Reducción del Desperdicio:** Maximiza ingresos vendiendo flores con deterioro leve antes de que se pudran.
* **Automatización:** Elimina la necesidad de inspección manual y reduce errores de tipado de especies.
* **Escalabilidad:** Sistema desacoplado listo para integrarse a cámaras industriales de punto de venta.
