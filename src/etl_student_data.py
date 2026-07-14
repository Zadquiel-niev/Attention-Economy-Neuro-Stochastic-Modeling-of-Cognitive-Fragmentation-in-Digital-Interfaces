import polars as pl
import numpy as np

print("Procesando Megaproyecto de Neuro-Data con Polars...")

# 1. Cargo los datos de Mirza
df = pl.read_csv("data/raw/mobile_phone_screen_time_dataset.csv")

# 2. Filtro estricto para estudiantes (nuestra población de estudio)
df_estudiantes = df.filter(pl.col("Occupation") == "Student")

# 3. Selección inteligente de variables (Mantenemos País y Continente para análisis transcultural)
columnas_proyecto = [
    "User_ID", "Country", "Continent", "Age", "Gender", 
    "Daily_Screen_Time_Hours", "Social_Media_Usage_Hours", 
    "App_Notifications_Received", "Screen_Unlocks_Per_Day",
    "Sleep_Hours", "Sleep_Quality", "Stress_Level", "Productivity_Score"
]
df_clean = df_estudiantes.select(columnas_proyecto)

# 4. Cálculo del IFA (Neuro-métrica de fragmentación)
df_clean = df_clean.with_columns([
    (pl.col("Daily_Screen_Time_Hours") * (pl.col("Screen_Unlocks_Per_Day") + 1).log()).alias("IFA")
])

# 5. Segmentación Cualitativa de la Frecuencia de Desbloqueo (Comportamiento Estratégico)
df_clean = df_clean.with_columns([
    pl.when(pl.col("Screen_Unlocks_Per_Day") <= 70).then(pl.lit("Rara vez"))
    .when(pl.col("Screen_Unlocks_Per_Day") <= 140).then(pl.lit("Frecuentemente"))
    .otherwise(pl.lit("Siempre"))
    .alias("Frecuencia_Desbloqueo")
])

# 6. Exportar el Master Dataset
output_path = "estudiantes_clean.csv"
df_clean.write_csv(output_path)

print(f"Dataset maestro de neuro-atención exportado a '{output_path}'")
print(f" Muestra final: {df_clean.height} estudiantes listos para el análisis transcultural.")
