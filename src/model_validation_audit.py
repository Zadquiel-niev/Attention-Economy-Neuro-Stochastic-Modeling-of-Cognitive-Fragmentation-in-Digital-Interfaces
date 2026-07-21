import polars as pl
import numpy as np
import statsmodels.api as sm
from scipy.stats import f
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def auditar_modelo_y_datos(ruta_datos: str):
    print("=" * 75)
    print("  INICIANDO BATERÍA DE AUDITORÍA Y ESTRESAMIENTO ECONOMÉTRICO")
    print("=" * 75)

    # cargamos los datos desde la ruta de datos 
    df = pl.read_csv(ruta_datos)
    
    # Selección de covariables y variable dependiente
    predictoras = [
        'Daily_Screen_Time_Hours', 
        'Social_Media_Usage_Hours', 
        'App_Notifications_Received', 
        'Screen_Unlocks_Per_Day'
    ]
    
    # Estandarización Z-score, o sea la formula clásica de Distribución nORMAL Z estándar
    df_z = df.select([
        ((pl.col(col) - pl.col(col).mean()) / pl.col(col).std()).alias(f"{col}_z")
        for col in predictoras + ['IFA']
    ])

    X = df_z.select([f"{col}_z" for col in predictoras]).to_numpy()
    y = df_z.select("IFA_z").to_numpy().flatten()
    

    # VALIDACIÓN FUERA DE MUESTRA (TRAIN/TEST 90/10 & RMSE) Separamos el 90% de los datos e intentamos predecir el 10% faltante para ver si realmente
    # el R cuadreado ajustado es tan robusto como pensé 0.98
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.10, random_state=42)
    
    X_train_sm = sm.add_constant(X_train)
    X_test_sm = sm.add_constant(X_test)
    
    modelo_train = sm.OLS(y_train, X_train_sm).fit()
    y_pred = modelo_train.predict(X_test_sm)
    
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2_out = r2_score(y_test, y_pred)

    print("\n[PRUEBA 1] VALIDACIÓN FUERA DE MUESTRA (OUT-OF-SAMPLE 90/10)")
    print(f"  * Muestra Entrenada (90%): N = {len(y_train)}")
    print(f"  * Muestra Evaluada (10%):  N = {len(y_test)}")
    print(f"  * RMSE en Prueba:          {rmse:.6f}")
    print(f"  * MAE en Prueba:           {mae:.6f}")
    print(f"  * R² Fuera de Muestra:     {r2_out:.6f}")


    #CRITERIOS DE INFORMACIÓN (AIC & BIC)  El R cuadrado ajustado convencional tiene un defecto grave siempre sube cuando agregas más variables
    #aunque no sirvan para nada entoces usé los Criterios de Información para penalizar la complejidad del modelo
  
    X_full_sm = sm.add_constant(X)
    modelo_full = sm.OLS(y, X_full_sm).fit()
    
    print("\n[PRUEBA 2] CRITERIOS DE INFORMACIÓN Y SELECCIÓN DE MODELO")
    print(f"  * Log-Likelihood:          {modelo_full.llf:.4f}")
    print(f"  * Criterio Akaike (AIC):   {modelo_full.aic:.4f}")
    print(f"  * Criterio Bayesiano (BIC):{modelo_full.bic:.4f}")

    #PRUEBA DE QUIEBRE ESTRUCTURAL (TEST DE CHOW EN UMBRAL IFA = 30.03) el test de Chow Evaluará si existe un cambio de régimen en la estructura de los parámetros al cruzar el umbral
    #Si el test de Chow da un p vaolor < 0.05 confirmaremos que la mente humana reacciona de manera discontinua a la saturación digital
 
    print("\n[PRUEBA 3] PRUEBA DE QUIEBRE ESTRUCTURAL (ESTABILIDAD PARAMÉTRICA)")
    
    ifa_original = df.select("IFA").to_numpy().flatten()
    corte_idx = int(np.sum(ifa_original < 30.03))
    
    indices_ordenados = np.argsort(ifa_original)
    X_ordenado = X_full_sm[indices_ordenados]
    y_ordenado = y[indices_ordenados]
    
    y1, y2 = y_ordenado[:corte_idx], y_ordenado[corte_idx:]
    X1, X2 = X_ordenado[:corte_idx], X_ordenado[corte_idx:]
    
    m1 = sm.OLS(y1, X1).fit()
    m2 = sm.OLS(y2, X2).fit()
    
    # Cálculo manual del estadístico de Chow
    rss_pool = modelo_full.ssr
    rss1 = m1.ssr
    rss2 = m2.ssr
    k = X_full_sm.shape[1]
    N = len(y)
    
    f_stat = ((rss_pool - (rss1 + rss2)) / k) / ((rss1 + rss2) / (N - 2 * k))
    p_val_chow = 1 - f.cdf(f_stat, k, N - 2 * k)

    print(f"  * Punto de Corte Evaluado:  IFA = 30.03 (N1={len(y1)}, N2={len(y2)})")
    print(f"  * Estadístico F (Chow):     {f_stat:.4f}")
    print(f"  * p-valor del Quiebre:      {p_val_chow:.4e}")
    
    if p_val_chow < 0.05:
        print("  => CONCLUSIÓN: Se RECHAZA la homogeneidad. La estructura de parámetros CAMBIA al cruzar el umbral (Comportamiento no lineal empírico).")
    else:
        print("  => CONCLUSIÓN: No se rechaza homogeneidad. Estructura linealmente constante en toda la muestra.")

    print("\n" + "=" * 75)

if __name__ == "__main__":
    auditar_modelo_y_datos('data/processed/estudiantes_clean.csv')