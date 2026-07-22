import polars as pl
import numpy as np

def compute_behavioral_kpis(data_path: str):
    
    # Cargamos los datos con Polars
    df = pl.read_csv(data_path)
    
    # Segmentación Etaria
    under_20 = df.filter(pl.col("Age") < 20)
    over_22 = df.filter(pl.col("Age") >= 22)
    
    # Tiempo medio de resistencia antes del primer microimpulso (16h activas = 960 min)
    under_20_sat = under_20.filter(pl.col("IFA") >= 30.03)
    over_22_sat = over_22.filter(pl.col("IFA") >= 30.03)
    
    time_to_impulse_u20 = (960.0 / under_20_sat["Screen_Unlocks_Per_Day"]).median()
    time_to_impulse_o22 = (960.0 / over_22_sat["Screen_Unlocks_Per_Day"]).median()
    
    # Cálculo del cambio porcentual positivo en resistencia (sostener la atención)
    pct_more_resistant = ((time_to_impulse_u20 - time_to_impulse_o22) / time_to_impulse_o22) * 100
    
    # Micro-sesiones (< 5 min por ventana de atención)
    df = df.with_columns([
        (960.0 / pl.col("Screen_Unlocks_Per_Day")).alias("window_min")
    ])
    
    micro_session_ratio = (df.filter(pl.col("window_min") < 5.0).height / df.height) * 100


    print(" KPIS DE COMPORTAMIENTO DIARIO Y ATENCIÓN JOVEN (< 20 AÑOS)")
    print(f"\n1. RESISTENCIA ATENCIONAL EN MENORES DE 20 AÑOS (Régimen Saturado):")
    print(f"   - Tiempo medio antes del primer microimpulso (< 20 años)  : {time_to_impulse_u20:.2f} minutos.")
    print(f"   - Tiempo medio antes del primer microimpulso (>= 22 años) : {time_to_impulse_o22:.2f} minutos.")
    print(f"   --> Los menores de 20 años sostienen la atención un {pct_more_resistant:.1f}% MÁS de tiempo antes del microimpulso.")
    print(f"\n2. PREVALENCIA DE FRAGMENTACIÓN EXTREMA POBLACIONAL:")
    print(f"   - El {micro_session_ratio:.1f}% de la población total presenta ventanas atencionales menores a 5 minutos.")

if __name__ == "__main__":
    compute_behavioral_kpis("data/processed/estudiantes_clean.csv")