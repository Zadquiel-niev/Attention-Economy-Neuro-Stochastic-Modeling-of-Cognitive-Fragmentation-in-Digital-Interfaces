import polars as pl
import numpy as np
import statsmodels.api as sm
import statsmodels.stats.api as sms
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import durbin_watson

def ejecutar_pipeline_neuro_econometrico(ruta_datos: str):
    """
    Ejecuta un pipeline econometrico avanzado para identificar y cuantificar los
    determinantes tecnologicos del Indice de Fragmentacion de la Atencion (IFA).
    Utiliza Polars para la carga eficiente de datos en memoria y el escalado Z-score.
    """
    print("Inicializando pipeline neuro-econometrico...")
    
    # Ingesta de datos de alto rendimiento
    try:
        df = pl.read_csv(ruta_datos)
        print(f"Dataset cargado correctamente. Dimensiones: ({df.height}, {df.width})")
    except Exception as e:
        print(f"[ERROR] Error al leer el dataset: {str(e)}")
        return

    # Especificacion estructural de variables
    predictores = [
        'Daily_Screen_Time_Hours', 
        'Social_Media_Usage_Hours', 
        'App_Notifications_Received', 
        'Screen_Unlocks_Per_Day'
    ]
    variable_dependiente = 'IFA'
    todas_las_variables = predictores + [variable_dependiente]

    # Estandarizacion parametrica vectorial (Z-score: (x - media) / desviacion)
    df_z = df.select([
        ((pl.col(nombre) - pl.col(nombre).mean()) / pl.col(nombre).std()).alias(f"{nombre}_z")
        for nombre in todas_las_variables
    ])

    # 4. Extraccion de matrices e inicializacion del intercepto
    X = df_z.select([f"{col}_z" for col in predictores]).to_numpy()
    X = sm.add_constant(X)  # Agrega el vector columna de unos para el intercepto Beta_0
    y = df_z.select(f"{variable_dependiente}_z").to_numpy().flatten()

    #  Estimacion por Minimos Cuadrados Ordinarios (OLS) Multivariante
    print("Ajustando modelo de Minimos Cuadrados Ordinarios (OLS)")
    model = sm.OLS(y, X).fit()

    # Reporte metrico estructurado
    print("\n" + "="*70)
    print("REPORTE DIAGNOSTICO ECONOMETRICO: DETERMINANTES DE FRAGMENTACION COGNITIVA")
    print("="*70)
    print(f"Bondad de Ajuste (R-cuadrado Ajustado): {model.rsquared_adj:.4f}")
    print(f"Estadistico F del Modelo:               {model.fvalue:.4f}")
    print(f"Prob (Estadistico F):                  {model.f_pvalue:.4e}")
    print("-"*70)

    print("MATRIZ DE COEFICIENTES (PESOS BETA ESTANDARIZADOS):")
    etiquetas_features = ['Intercepto', 'Daily_Screen_Time_Hours', 'Social_Media_Usage_Hours', 'App_Notifications_Received', 'Screen_Unlocks_Per_Day']
    for idx, etiqueta in enumerate(etiquetas_features):
        coef = model.params[idx]
        p_val = model.pvalues[idx]
        t_stat = model.tvalues[idx]
        print(f"  * {etiqueta:<30} | Beta: {coef:>8.4f} | t-stat: {t_stat:>8.2f} | P>|t|: {p_val:.4e}")
    
    print("-"*70)
    print("ESPECIFICACIÓN ESTADISTICA Y PRUEBAS DIAGNOSTICAS:")
    
    # Supuesto 4: Verificacion de Multicolinealidad mediante VIF
    print("  [SUPUESTO 4] Factores de Inflación de la Varianza (VIF):")
    for i in range(1, X.shape[1]):
        vif_val = variance_inflation_factor(X, i)
        print(f"    - {predictores[i-1]:<28} : VIF = {vif_val:.4f}")

    # Supuesto 5: Independencia de Residuos mediante Durbin-Watson
    dw_stat = durbin_watson(model.resid)
    print(f"  [SUPUESTO 5] Autocorrelacion de Residuos (Durbin-Watson): DW = {dw_stat:.4f}")
    
    print("="*70 + "\n")
    return model

if __name__ == "__main__":
    ejecutar_pipeline_neuro_econometrico('data/processed/estudiantes_clean.csv')
