# -*- coding: utf-8 -*-
"""
database.py — FloraVision
Módulo de Gestión de Base de Datos SQLite para Persistencia de Inventario, Alertas y Feedback de Refuerzo.
"""

import sqlite3
import os
import datetime
from pathlib import Path

# Ruta por defecto de la base de datos en la raíz del proyecto
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "floravision.db")


class DatabaseManager:
    """Administrador de Base de Datos SQLite3 para FloraVision."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._inicializar_tablas()

    def _get_connection(self):
        """Abre y retorna una conexión con SQLite3 configurada con Row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _inicializar_tablas(self):
        """Crea la estructura de tablas relacionales si no existen aún."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 1. Tabla de Inventario de Flores
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_flor TEXT NOT NULL,
                cantidad INTEGER DEFAULT 1,
                estado TEXT NOT NULL,
                badge TEXT NOT NULL,
                precio_base REAL NOT NULL,
                descuento INTEGER DEFAULT 0,
                precio_final REAL NOT NULL,
                porcentaje_marchito REAL DEFAULT 0.0,
                timestamp TEXT,
                fecha TEXT,
                imagen_b64 TEXT,
                decision TEXT,
                recomendacion TEXT,
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # 2. Tabla de Feedback de Aprendizaje por Refuerzo
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback_refuerzo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                especie_predicha TEXT,
                especie_correcta TEXT,
                loss REAL DEFAULT 0.0,
                timestamp TEXT,
                fecha TEXT,
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # 3. Tabla de Alertas del Agente
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS alertas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mensaje TEXT NOT NULL,
                timestamp TEXT,
                leida INTEGER DEFAULT 0,
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            conn.commit()

    # ------------------------------------------------------------------
    # OPERACIONES DE INVENTARIO
    # ------------------------------------------------------------------
    def guardar_flor(self, datos: dict) -> int:
        """Inserta un registro de flor escaneada en la base de datos."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO inventario (
                tipo_flor, cantidad, estado, badge, precio_base, descuento,
                precio_final, porcentaje_marchito, timestamp, fecha,
                imagen_b64, decision, recomendacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datos.get("tipo_flor", "Rosa"),
                datos.get("cantidad", 1),
                datos.get("estado", "Fresca"),
                datos.get("badge", "Saludable"),
                float(datos.get("precio_base", 50.0)),
                int(datos.get("descuento", 0)),
                float(datos.get("precio_final", 50.0)),
                float(datos.get("porcentaje_marchito", 0.0)),
                datos.get("timestamp", datetime.datetime.now().strftime("%H:%M:%S")),
                datos.get("fecha", str(datetime.date.today())),
                datos.get("imagen_b64", ""),
                datos.get("decision", "mantener"),
                datos.get("recomendacion", "")
            ))
            conn.commit()
            return cursor.lastrowid

    def obtener_inventario(self) -> list[dict]:
        """Retorna la lista completa de flores registradas en la base de datos."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM inventario ORDER BY id ASC")
            filas = cursor.fetchall()
            return [dict(f) for f in filas]

    def vaciar_inventario(self):
        """Elimina todos los registros de la tabla de inventario y alertas."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM inventario")
            cursor.execute("DELETE FROM alertas")
            conn.commit()

    # ------------------------------------------------------------------
    # OPERACIONES DE REFUERZO Y ALERTAS
    # ------------------------------------------------------------------
    def guardar_feedback(self, especie_predicha: str, especie_correcta: str, loss: float = 0.0):
        """Registra un evento de aprendizaje por refuerzo."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO feedback_refuerzo (especie_predicha, especie_correcta, loss, timestamp, fecha)
            VALUES (?, ?, ?, ?, ?)
            """, (
                especie_predicha,
                especie_correcta,
                float(loss),
                datetime.datetime.now().strftime("%H:%M:%S"),
                str(datetime.date.today())
            ))
            conn.commit()

    def guardar_alerta(self, mensaje: str, timestamp: str | None = None):
        """Guarda una alerta del agente inteligente."""
        ts = timestamp or datetime.datetime.now().strftime("%H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO alertas (mensaje, timestamp) VALUES (?, ?)", (mensaje, ts))
            conn.commit()

    def obtener_alertas(self) -> list[str]:
        """Retorna las alertas guardadas."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT mensaje FROM alertas ORDER BY id ASC")
            return [row["mensaje"] for row in cursor.fetchall()]
