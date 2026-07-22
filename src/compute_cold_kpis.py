import polars as pl
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf

def compute_cognitive_cost_kpis(data_path: str):
    # Cargamos los datos procesados
    df = pl.read_csv(data_path)
    
    # Calcular parámetros para estandarizar la Productividad 
    mean_prod = df["Productivity_Score"].mean() # promedio de la productivity_score
    std_prod = df["Productivity_Score"].std() # desviación estandar, para ver que tanto estan los datos dispersos respecto a la media de productivity_score
    
    # 2. Feature Engineering de Costo Atencional 
    df = df.with_columns([
        # Crear el Z-score de productividad (z = (X - Media) / Desv. Estándar)
        ((pl.col("Productivity_Score") - mean_prod) / std_prod).alias("productivity_score_z"),
        
        # Intervalo entre desbloqueos en minutos (16 horas activas = 960 min)
        (960.0 / pl.col("Screen_Unlocks_Per_Day")).alias("uninterrupted_window_min"),
        
        # Tiempo de vida medio del foco en minutos
        (0.6931 * (960.0 / pl.col("Screen_Unlocks_Per_Day"))).alias("focus_half_life_min"),
        
        # Horas perdidas por latencia de re-enfoque (15 min por desbloqueo)
        ((pl.col("Screen_Unlocks_Per_Day") * 15.0) / 60.0).alias("refocus_latency_hours")
    ])
    
    # Crear variable binaria de éxito (Z >= 0 significa rendimiento superior a la media poblacional)
    df = df.with_columns([
        (pl.col("productivity_score_z") >= 0).cast(pl.Int32).alias("high_productivity_flag")
    ])
    
    # Segmentación por Regímenes (Subcrítico vs. Saturado P85 usando la columna real 'IFA')
    subcritical = df.filter(pl.col("IFA") < 30.03)
    saturated = df.filter(pl.col("IFA") >= 30.03)
    
    # MÉTRICAS EN FRÍO
    # Regimen 1: Subcrítico (IFA < 30.03)
    avg_window_sub = subcritical["uninterrupted_window_min"].mean()
    half_life_sub = subcritical["focus_half_life_min"].mean()
    latency_hours_sub = subcritical["refocus_latency_hours"].mean()
    prob_high_prod_sub = subcritical["high_productivity_flag"].mean() * 100
    
    # Regimen 2: Saturado (IFA >= 30.03)
    avg_window_sat = saturated["uninterrupted_window_min"].mean()
    half_life_sat = saturated["focus_half_life_min"].mean()
    latency_hours_sat = saturated["refocus_latency_hours"].mean()
    prob_high_prod_sat = saturated["high_productivity_flag"].mean() * 100

    # Modelo Logístico para Probabilidad de Rendimiento
    df_pd = df.to_pandas()
    # Ecuación ajustada al nombre real de la columna "IFA"
    logit_model = smf.logit("high_productivity_flag ~ IFA", data=df_pd).fit(disp=0)
    
    # Probabilidades puntuales
    eval_points = pl.DataFrame({"IFA": [10.0, 20.0, 30.03, 40.0, 50.0]})
    eval_pd = eval_points.to_pandas()
    eval_pd["prob_success_%"] = logit_model.predict(eval_pd) * 100

    #  RESULTADOS
    print(" IMPACTO EN FRÍO: COSTO COGNITIVO Y POSIBILIDADES DE COLAPSO")
    
    print(f"\n1. TIEMPO DE VIDA MEDIO DE LA ATENCIÓN (HALF-LIFE):")
    print(f"   - Régimen Normal (IFA < 30.03) : {half_life_sub:5.2f} minutos continuos.")
    print(f"   - Régimen Saturado (IFA >= 30.03): {half_life_sat:5.2f} minutos continuos.")
    print(f"   --> Caída del {((half_life_sub - half_life_sat)/half_life_sub)*100:.1f}% en la estabilidad del foco.")

    print(f"\n2. VENTANA DE ATENCIÓN CONTINUA vs. LATENCIA DE GLORIA MARK:")
    print(f"   - Ventana media (Saturado)               : {avg_window_sat:5.2f} minutos.")
    print(f"   - Impuesto de re-enfoque acumulado (Sat.): {latency_hours_sat:5.2f} horas/día perdidas.")

    print(f"\n3. PROBABILIDAD DE MANTENER RENDIMIENTO ACADÉMICO ACEPTABLE:")
    print(f"   - Régimen Subcrítico (IFA < 30.03) : {prob_high_prod_sub:5.1f}% de posibilidad de éxito.")
    print(f"   - Régimen Saturado   (IFA >= 30.03) : {prob_high_prod_sat:5.1f}% de posibiidad de éxito.")
    print(f"   --> Caída absoluta de {prob_high_prod_sub - prob_high_prod_sat:.1f} puntos porcentuales.")

    print("\n4. CURVA DE DECAIMIENTO DE POSIBILIDAD DE ÉXITO ACADÉMICO:")
    for idx, row in eval_pd.iterrows():
        print(f"   - Para IFA = {row['IFA']:5.2f} pts --> posibilidad de éxito: {row['prob_success_%']:5.1f}%")

if __name__ == "__main__":
    compute_cognitive_cost_kpis("data/processed/estudiantes_clean.csv")