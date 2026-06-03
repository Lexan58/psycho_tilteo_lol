# core/ml_predictor.py
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from core.database import get_matches_dataframe
from core.player_profile import PLAYER_PROFILE

class TiltPredictorIO:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False
        self.feature_columns = []

    def _prepare_data(self, df: pd.DataFrame):
        """Pipeline de Feature Engineering para transformar el historial en datos numéricos."""
        # 1. Crear variables temporales
        df["date"] = pd.to_datetime(df["date"])
        df["hour"] = df["date"].dt.hour
        
        # 2. Variable de racha (derrotas previas en las últimas 3 partidas)
        # Convertimos a binario invertido: 1 si es Loss, 0 si es Win
        df["is_loss"] = df["result"].apply(lambda x: 1 if x == "Loss" else 0)
        df["recent_losses"] = df["is_loss"].shift(-1).rolling(window=3, min_periods=0).sum().fillna(0)

        # 3. Variable de stress champion
        stress_champs = PLAYER_PROFILE.get("stress_champions", [])
        df["is_stress_champion"] = df["champion"].apply(lambda x: 1 if x in stress_champs else 0)

        # 4. Definir variable Objetivo (Target): 1 = Alta probabilidad de Tilt (Tilt >= 5), 0 = Controlado
        df["target_tilt"] = df["tilt_level"].apply(lambda x: 1 if x >= 5 else 0)

        # Seleccionar características base para la IA
        features = df[["hour", "recent_losses", "is_stress_champion", "champion", "role"]].copy()
        
        # Convertir variables categóricas (Campeón y Rol) a columnas numéricas (One-Hot Encoding)
        features = pd.get_dummies(features, columns=["champion", "role"])
        
        return features, df["target_tilt"]

    def train_model(self) -> bool:
        """Extrae los datos guardados en SQLite y entrena la IA."""
        df = get_matches_dataframe()
        
        # Necesitamos un mínimo de partidas calificadas para que la IA no alucine
        # Idealmente 15 o 20 (¡las cuales ya tienes!)
        if df.empty or len(df[df["tilt_level"] > 0]) < 10:
            self.is_trained = False
            return False
            
        # Filtrar solo las partidas que ya tienen una calificación real del usuario
        df_calificadas = df[df["tilt_level"] > 0].copy()
        
        X, y = self._prepare_data(df_calificadas)
        self.feature_columns = X.columns.tolist()
        
        self.model.fit(X, y)
        self.is_trained = True
        return True

    def predict_prematch_risk(self, next_champion: str, next_role: str) -> dict:
        """
        Evalúa el escenario actual antes de entrar a la grieta.
        Predice la probabilidad de sufrir un colapso por tilt.
        """
        if not self.is_trained:
            # Intenta entrenar en caliente si no se ha hecho
            if not self.train_model():
                return {"success": False, "message": "Datos insuficientes para predecir."}

        df = get_matches_dataframe()
        current_hour = datetime.now().hour
        
        # Calcular pérdidas recientes del historial real
        df["is_loss"] = df["result"].apply(lambda x: 1 if x == "Loss" else 0)
        recent_losses = df["is_loss"].head(3).sum() if not df.empty else 0
        
        is_stress_champ = 1 if next_champion in PLAYER_PROFILE.get("stress_champions", []) else 0

        # Crear el vector de entrada con la misma estructura exacta que el set de entrenamiento
        input_data = pd.DataFrame([{
            "hour": current_hour,
            "recent_losses": recent_losses,
            "is_stress_champion": is_stress_champ,
            f"champion_{next_champion}": 1,
            f"role_{next_role}": 1
        }])
        
        # Reindexar para asegurar que tenga todas las columnas que el modelo conoce (rellenando con 0)
        input_data = input_data.reindex(columns=self.feature_columns, fill_value=0)
        
        # Calcular probabilidades probabilísticas
        probabilities = self.model.predict_proba(input_data)[0]
        tilt_probability = probabilities[1] * 100 # Probabilidad de la clase 1 (Tilt Alto)

        # Diagnóstico de factores de riesgo
        risk_factors = []
        if current_hour >= 22 or current_hour <= 4:
            risk_factors.append("⏰ Ventana horaria de fatiga biológica.")
        if recent_losses >= 2:
            risk_factors.append(f"📉 Arreastras una racha negativa de {recent_losses} derrotas seguidas (Efecto Bola de Nieve).")
        if is_stress_champ:
            risk_factors.append(f"⚠️ El campeón seleccionado ({next_champion}) posee una alta carga de exigencia psicológica.")

        return {
            "success": True,
            "probability": round(tilt_probability, 1),
            "factors": risk_factors
        }