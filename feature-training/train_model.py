# -*- coding: utf-8 -*-
"""
train_model.py — FloraVision (feature/model-training)
Script de entrenamiento y transferencia de conocimiento (Transfer Learning)
para la clasificación de especies de flores y evaluación de estado.

Carga un modelo preentrenado (MobileNetV2 o ResNet50), aplica Data Augmentation,
entrena con el dataset y exporta el modelo final entrenado a un archivo (.h5 / .keras).

Uso:
    python train_model.py --epochs 10 --batch-size 16 --model-type mobilenet --sample-dataset
"""

import os
import sys

# Forzar codificación UTF-8 en stdout y stderr para evitar UnicodeEncodeError en Windows (CP1252)
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import argparse
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, optimizers, callbacks

# ---------------------------------------------------------------------------
# CONFIGURACIÓN Y CONSTANTES
# ---------------------------------------------------------------------------
CLASES_FLORES = ["rosa", "girasol", "margarita", "clavel", "lirio", "orquidea", "tulipan"]
IMG_SIZE = (224, 224)
BATCH_SIZE_DEF = 16
EPOCHS_DEF = 10

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR_DEF = BASE_DIR / "dataset"
MODEL_OUTPUT_H5 = BASE_DIR / "modelo_flores.h5"
MODEL_OUTPUT_KERAS = BASE_DIR / "modelo_flores.keras"
PLOT_OUTPUT = BASE_DIR / "feature-training" / "training_metrics.png"


# ---------------------------------------------------------------------------
# GENERACIÓN AUTOMÁTICA DE DATASET DE MUESTRA (SI NO EXISTE)
# ---------------------------------------------------------------------------
def preparar_dataset_muestra(target_dir: Path):
    """
    Crea la estructura de carpetas de dataset y llena cada clase con imágenes de muestra
    o imágenes sintéticas aumentadas si no se encuentra un dataset físico previo.
    """
    print(f"📁 Preparando estructura de dataset en: {target_dir}")
    source_img_dir = BASE_DIR / "feature-capture" / "imagenes_prueba"
    
    for c in CLASES_FLORES:
        folder = target_dir / c
        folder.mkdir(parents=True, exist_ok=True)
    
    # Buscar imágenes fuente disponibles
    sample_files = list(source_img_dir.glob("*.jpg")) + list(source_img_dir.glob("*.png"))
    
    if not sample_files:
        print("⚠️ No se encontraron imágenes base en feature-capture/imagenes_prueba.")
        print("💡 Creando imágenes sintéticas de prueba para verificación del pipeline...")
        for idx, clase in enumerate(CLASES_FLORES):
            folder = target_dir / clase
            for i in range(5):
                img_data = np.random.randint(50, 255, size=(224, 224, 3), dtype=np.uint8)
                tf.keras.utils.save_img(folder / f"sample_{i+1}.jpg", img_data)
        print("✅ Dataset sintético de prueba creado exitosamente.")
        return

    # Copiar/distribuir imágenes de muestra entre clases para asegurar datos de entrenamiento
    for idx, clase in enumerate(CLASES_FLORES):
        folder = target_dir / clase
        existing = list(folder.glob("*.*"))
        if len(existing) < 3:
            for i, src in enumerate(sample_files):
                dest = folder / f"muestra_{i+1}_{src.name}"
                if not dest.exists():
                    tf.keras.utils.save_img(
                        dest, 
                        tf.keras.utils.img_to_array(tf.keras.utils.load_img(src, target_size=IMG_SIZE))
                    )
    print("✅ Dataset de muestra inicializado correctamente.")


# ---------------------------------------------------------------------------
# PIPELINE DE DATA AUGMENTATION
# ---------------------------------------------------------------------------
def obtener_capa_data_augmentation():
    """
    Crea un secuencial de Data Augmentation para robustecer la generalización del modelo.
    Incluye giros horizontales, rotaciones, zooms y variaciones de brillo/contraste.
    """
    return keras.Sequential([
        layers.RandomFlip("horizontal_and_vertical", name="aug_flip"),
        layers.RandomRotation(0.2, name="aug_rotation"),
        layers.RandomZoom(0.15, name="aug_zoom"),
        layers.RandomTranslation(height_factor=0.1, width_factor=0.1, name="aug_translation"),
        layers.RandomContrast(0.2, name="aug_contrast"),
    ], name="data_augmentation")


# ---------------------------------------------------------------------------
# CONSTRUCCIÓN DE MODELO CON TRANSFER LEARNING
# ---------------------------------------------------------------------------
def construir_modelo_flores(model_type: str = "mobilenet", num_classes: int = len(CLASES_FLORES)):
    """
    Construye la arquitectura basada en MobileNetV2 o ResNet50.
    
    Parámetros
    ----------
    model_type : str ('mobilenet' o 'resnet')
    num_classes : int (número de clases a predecir)
    """
    inputs = layers.Input(shape=(IMG_SIZE[0], IMG_SIZE[1], 3), name="input_image")
    
    # 1. Data Augmentation
    x = obtener_capa_data_augmentation()(inputs)
    
    # 2. Carga y Normalización del modelo preentrenado en ImageNet
    try:
        if model_type.lower() == "resnet":
            print("🏗️ Cargando modelo base: ResNet50 (preentrenado en ImageNet)...")
            x = tf.keras.applications.resnet50.preprocess_input(x)
            base_model = tf.keras.applications.ResNet50(
                weights="imagenet",
                include_top=False,
                input_tensor=x
            )
        else:
            print("🏗️ Cargando modelo base: MobileNetV2 (preentrenado en ImageNet)...")
            x = tf.keras.applications.mobilenet_v2.preprocess_input(x)
            base_model = tf.keras.applications.MobileNetV2(
                weights="imagenet",
                include_top=False,
                input_tensor=x
            )
    except Exception as err_weights:
        print(f"⚠️ Detectado archivo de pesos corrupto o incompleto en caché ({err_weights}). Limpiando caché...")
        keras_models_dir = Path.home() / ".keras" / "models"
        if keras_models_dir.exists():
            for f_h5 in keras_models_dir.glob("*.h5"):
                try:
                    f_h5.unlink()
                except Exception:
                    pass
        print("🔄 Reintentando descarga limpia de los pesos del modelo...")
        if model_type.lower() == "resnet":
            x = tf.keras.applications.resnet50.preprocess_input(x)
            base_model = tf.keras.applications.ResNet50(weights="imagenet", include_top=False, input_tensor=x)
        else:
            x = tf.keras.applications.mobilenet_v2.preprocess_input(x)
            base_model = tf.keras.applications.MobileNetV2(weights="imagenet", include_top=False, input_tensor=x)

    # Congelar capas del modelo preentrenado inicialmente
    base_model.trainable = False

    # 3. Cabezal de Clasificación Personalizado
    x = base_model.output
    x = layers.GlobalAveragePooling2D(name="global_avg_pool")(x)
    x = layers.BatchNormalization(name="batch_norm")(x)
    x = layers.Dense(256, activation="relu", name="dense_256")(x)
    x = layers.Dropout(0.3, name="dropout_1")(x)
    x = layers.Dense(128, activation="relu", name="dense_128")(x)
    x = layers.Dropout(0.2, name="dropout_2")(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="predictions")(x)

    model = models.Model(inputs=inputs, outputs=outputs, name=f"FloraVision_{model_type.upper()}")
    return model, base_model


# ---------------------------------------------------------------------------
# ENTRENAMIENTO Y OPTIMIZACIÓN
# ---------------------------------------------------------------------------
def entrenar_modelo(dataset_dir: Path, model_type: str = "mobilenet", epochs: int = EPOCHS_DEF, batch_size: int = BATCH_SIZE_DEF):
    """
    Carga datos, compila y entrena el modelo en 2 fases (Transfer Learning + Fine-tuning).
    """
    if not dataset_dir.exists():
        preparar_dataset_muestra(dataset_dir)
        
    print(f"📊 Cargando dataset desde: {dataset_dir}")
    
    clases_target = [c.lower() for c in CLASES_FLORES]
    try:
        train_ds = tf.keras.utils.image_dataset_from_directory(
            dataset_dir,
            class_names=clases_target,
            validation_split=0.2,
            subset="training",
            seed=123,
            image_size=IMG_SIZE,
            batch_size=batch_size,
            label_mode="categorical"
        )

        val_ds = tf.keras.utils.image_dataset_from_directory(
            dataset_dir,
            class_names=clases_target,
            validation_split=0.2,
            subset="validation",
            seed=123,
            image_size=IMG_SIZE,
            batch_size=batch_size,
            label_mode="categorical"
        )
    except ValueError as err:
        print(f"⚠️ Error al cargar dataset: {err}")
        print("🔄 Recreando dataset de muestra seguro...")
        preparar_dataset_muestra(dataset_dir)
        train_ds = tf.keras.utils.image_dataset_from_directory(
            dataset_dir, class_names=clases_target, validation_split=0.2, subset="training", seed=123,
            image_size=IMG_SIZE, batch_size=batch_size, label_mode="categorical"
        )
        val_ds = tf.keras.utils.image_dataset_from_directory(
            dataset_dir, class_names=clases_target, validation_split=0.2, subset="validation", seed=123,
            image_size=IMG_SIZE, batch_size=batch_size, label_mode="categorical"
        )

    # Optimización de I/O de TensorFlow
    train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=tf.data.AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=tf.data.AUTOTUNE)

    # Crear modelo
    model, base_model = construir_modelo_flores(model_type=model_type, num_classes=len(CLASES_FLORES))
    
    # Compilar FASE 1: Entrenar solo la cabeza clasificadora
    print("\n🚀 FASE 1: Entrenamiento del cabezal de clasificación (Capas base congeladas)...")
    model.compile(
        optimizer=optimizers.Adam(learning_rate=1e-3),
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )
    model.summary()

    cb_list = [
        callbacks.EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True),
        callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, verbose=1),
        callbacks.ModelCheckpoint(filepath=str(MODEL_OUTPUT_H5), monitor="val_accuracy", save_best_only=True)
    ]

    history_phase1 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        callbacks=cb_list
    )

    # Compilar FASE 2: Fine-Tuning de capas superiores del modelo base
    print("\n⚡ FASE 2: Fine-Tuning (Descongelando capas superiores del backbone)...")
    base_model.trainable = True
    
    # Mantener congeladas las primeras capas del backbone
    fine_tune_at = len(base_model.layers) // 2
    for layer in base_model.layers[:fine_tune_at]:
        layer.trainable = False

    model.compile(
        optimizer=optimizers.Adam(learning_rate=1e-5),  # Tasa de aprendizaje muy baja para fine-tuning
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    fine_tune_epochs = max(2, epochs // 2)
    history_phase2 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=fine_tune_epochs,
        callbacks=cb_list
    )

    # -----------------------------------------------------------------------
    # EXPORTACIÓN DEL MODELO Y MÉTRICAS
    # -----------------------------------------------------------------------
    print(f"\n💾 Guardando modelo final entrenado en:")
    print(f"   • H5 format:    {MODEL_OUTPUT_H5}")
    print(f"   • Keras format: {MODEL_OUTPUT_KERAS}")

    model.save(MODEL_OUTPUT_H5)
    try:
        model.save(MODEL_OUTPUT_KERAS)
    except Exception as e:
        print(f"ℹ️ (Guardado .keras opcional omitido: {e})")

    guardar_grafica_metricas(history_phase1, history_phase2)
    print("✅ Proceso de entrenamiento concluido exitosamente.")
    return model


def guardar_grafica_metricas(h1, h2):
    """Genera y guarda un gráfico con la evolución de Pérdida y Precisión."""
    acc = h1.history['accuracy'] + h2.history['accuracy']
    val_acc = h1.history['val_accuracy'] + h2.history['val_accuracy']
    loss = h1.history['loss'] + h2.history['loss']
    val_loss = h1.history['val_loss'] + h2.history['val_loss']

    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(acc, label='Precisión Entrenamiento')
    plt.plot(val_acc, label='Precisión Validación')
    plt.axvline(x=len(h1.history['accuracy'])-1, color='gray', linestyle='--', label='Inicio Fine-Tuning')
    plt.title('Evolución de la Precisión (Accuracy)')
    plt.xlabel('Época')
    plt.ylabel('Precisión')
    plt.legend()
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.plot(loss, label='Pérdida Entrenamiento')
    plt.plot(val_loss, label='Pérdida Validación')
    plt.axvline(x=len(h1.history['loss'])-1, color='gray', linestyle='--', label='Inicio Fine-Tuning')
    plt.title('Evolución de la Pérdida (Loss)')
    plt.xlabel('Época')
    plt.ylabel('Pérdida')
    plt.legend()
    plt.grid(True)

    PLOT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(PLOT_OUTPUT)
    plt.close()
    print(f"📈 Gráfica de rendimiento guardada en: {PLOT_OUTPUT}")


# ---------------------------------------------------------------------------
# CLI MAIN ENTRYPOINT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FloraVision — Entrenamiento de Modelo IA (feature/model-training)")
    parser.add_argument("--epochs", type=int, default=EPOCHS_DEF, help="Número de épocas de entrenamiento (default: 10)")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE_DEF, help="Tamaño de lote (batch size, default: 16)")
    parser.add_argument("--model-type", type=str, choices=["mobilenet", "resnet"], default="mobilenet", help="Arquitectura preentrenada (mobilenet / resnet)")
    parser.add_argument("--dataset-dir", type=str, default=str(DATASET_DIR_DEF), help="Ruta al directorio de dataset")
    parser.add_argument("--sample-dataset", action="store_true", help="Forzar preparación de dataset de muestra antes de entrenar")

    args = parser.parse_args()
    ds_path = Path(args.dataset_dir)
    
    if args.sample_dataset or not ds_path.exists():
        preparar_dataset_muestra(ds_path)

    entrenar_modelo(
        dataset_dir=ds_path,
        model_type=args.model_type,
        epochs=args.epochs,
        batch_size=args.batch_size
    )
