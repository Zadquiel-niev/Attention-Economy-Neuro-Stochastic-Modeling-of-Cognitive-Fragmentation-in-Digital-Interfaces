import os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from lifelines import CoxPHFitter, KaplanMeierFitter
from lifelines.statistics import proportional_hazard_test


def compute_greenwood_table(durations: np.ndarray, events: np.ndarray) -> pl.DataFrame:
    
    """Cálculo analítico explícito del estimador Kaplan-Meier S(t)

    y su varianza asintótica mediante la Fórmula de Greenwood:
    
    Var{S(t)} = [S(t)]^2 * sum(d_i / (n_i * (n_i - d_i)))
    """
    unique_times = np.sort(np.unique(durations))

    s_t = 1.0
    sum_greenwood = 0.0
    km_records = []

    for t in unique_times:
        
        # d_i: Eventos de interrupción observados en el instante t
        d_i = np.sum((durations == t) & (events == 1))
        # n_i: Sujetos expuestos inmediatamente antes de t
        n_i = np.sum(durations >= t)

        if n_i > 0 and (n_i - d_i) > 0:
            sum_greenwood += d_i / (n_i * (n_i - d_i))
            s_t *= 1.0 - (d_i / n_i)

        var_greenwood = (s_t**2) * sum_greenwood
        se_greenwood = np.sqrt(var_greenwood)

        # Intervalos de Confianza al 95% acotados en [0, 1]
        
        ci_lower = max(0.0, s_t - 1.96 * se_greenwood)
        ci_upper = min(1.0, s_t + 1.96 * se_greenwood)

        km_records.append({
            "time_min": float(t),
            "n_at_risk": int(n_i),
            "events_d_i": int(d_i),
            "S_t": float(s_t),
            "var_greenwood": float(var_greenwood),
            "se_greenwood": float(se_greenwood),
            "ci_95_lower": float(ci_lower),
            "ci_95_upper": float(ci_upper),
        })

    return pl.DataFrame(km_records)


def run_survival_analysis(data_path: str):
    
    #  Definición estricta del directorio de salida según arquitectura del repositorio
    
    output_dir = Path("reports/assets")
    output_dir.mkdir(parents=True, exist_ok=True)

    #  Carga y preprocesamiento de datos
    
    df = pl.read_csv(data_path)

    # Definición operacional del IPID (Intervalo Promedio de Inactividad Digital)
    # Baseline estandarizado: 16 horas de vigilia activa (960 minutos)
    
    df = df.with_columns([
        (960.0 / pl.col("Screen_Unlocks_Per_Day")).alias("duration_min"),
        pl.lit(1).alias("event_observed"),  # Esquema de observación completa (E_i = 1)
        (pl.col("IFA") >= 30.03).cast(pl.Int32).alias("is_saturated"),
    ])

    data_pd = df.to_pandas()

    sub_df = df.filter(pl.col("is_saturated") == 0)
    sat_df = df.filter(pl.col("is_saturated") == 1)

    # Tablas de Greenwood por régimen
    
    gw_sub = compute_greenwood_table(
        sub_df["duration_min"].to_numpy(), sub_df["event_observed"].to_numpy()
    )
    gw_sat = compute_greenwood_table(
        sat_df["duration_min"].to_numpy(), sat_df["event_observed"].to_numpy()
    )

    # Ajuste Kaplan-Meier con Lifelines
    
    kmf_sub = KaplanMeierFitter()
    kmf_sat = KaplanMeierFitter()

    kmf_sub.fit(
        durations=data_pd.loc[data_pd["is_saturated"] == 0, "duration_min"],
        event_observed=data_pd.loc[data_pd["is_saturated"] == 0, "event_observed"],
        label="Régimen Subcrítico (IFA < 30.03)",
    )
    kmf_sat.fit(
        durations=data_pd.loc[data_pd["is_saturated"] == 1, "duration_min"],
        event_observed=data_pd.loc[data_pd["is_saturated"] == 1, "event_observed"],
        label="Régimen Saturado (IFA >= 30.03)",
    )

    # Modelo Semiparamétrico de Riesgos Proporcionales de Cox
    cph = CoxPHFitter()
    cox_data = data_pd[["duration_min", "event_observed", "IFA", "Age"]]
    cph.fit(cox_data, duration_col="duration_min", event_col="event_observed")

    # Extraer parámetros de Cox
    
    coef_ifa = cph.summary.loc["IFA", "coef"]
    se_ifa = cph.summary.loc["IFA", "se(coef)"]
    hr_ifa = np.exp(coef_ifa)
    p_val_ifa = cph.summary.loc["IFA", "p"]
    z_ifa = cph.summary.loc["IFA", "z"]

    # Auditoría formal del Supuesto de Riesgos Proporcionales (Residuos de Schoenfeld)
    
    schoenfeld_test = proportional_hazard_test(cph, cox_data, time_transform="rank")
    p_val_schoenfeld_ifa = schoenfeld_test.summary.loc["IFA", "p"]


    print(" AUDITORÍA DE SUPERVIVENCIA COGNITIVA: KAPLAN-MEIER, GREENWOOD & COX PH")

    print("\n[A] COMPARATIVA DE VIDA MEDIA DEL IPID (S(t) = 0.50):")
    print(
        f"    - Régimen Subcrítico : {kmf_sub.median_survival_time_:.2f} minutos antes de interrupción."
    )
    print(
        f"    - Régimen Saturado   : {kmf_sat.median_survival_time_:.2f} minutos antes de interrupción."
    )

    print("\n[B] TABLA GREENWOOD - RÉGIMEN SATURADO (Muestra de Tiempos Críticos):")
    print(gw_sat.select([
        "time_min",
        "n_at_risk",
        "events_d_i",
        "S_t",
        "se_greenwood",
        "ci_95_lower",
        "ci_95_upper",
    ]).head(8))

    print("\n[C] MODELO DE RIESGOS PROPORCIONALES DE COX:")
    print(f"    - Coeficiente IFA (beta) : {coef_ifa:.4f} (SE: {se_ifa:.4f}, z: {z_ifa:.2f})")
    print(f"    - Hazard Ratio (HR IFA)  : {hr_ifa:.4f} (p-valor: {p_val_ifa:.4e})")
    print(f"    - Impacto +1 IFA         : +{(hr_ifa - 1) * 100:.2f}% de riesgo instantáneo.")
    print(f"    - Impacto Acumulado +10  : +{((hr_ifa**10) - 1) * 100:.2f}% (HR^10 = {hr_ifa**10:.4f}).")

    print("\n[D] VALIDACIÓN DE SUPUESTOS DE COX (Residuos de Schoenfeld):")
    print(f"    - Valor p de Schoenfeld (IFA) : {p_val_schoenfeld_ifa:.4f}")
    if p_val_schoenfeld_ifa > 0.05:
        print("    - Resultado                   : CUMPLE EL SUPUESTO (p > 0.05). Proporcionalidad validada.")
    else:
        print("    - Resultado                   : Violación detectada (p <= 0.05). Revisar estratificación.")
    print("=" * 85)

    # Generación del gráfico de supervivencia
    
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    kmf_sub.plot_survival_function(
        ax=ax, color="#1f77b4", linewidth=2.5, ci_show=True
    )
    kmf_sat.plot_survival_function(
        ax=ax, color="#d62728", linewidth=2.5, ci_show=True
    )

    ax.axhline(
        y=0.5,
        color="black",
        linestyle="--",
        alpha=0.7,
        label="Vida Media t_1/2 (S(t) = 0.50)",
    )
    ax.set_title(
        "Supervivencia Cognitiva S(t) con Intervalos de Confianza de Greenwood (95%)",
        fontsize=13,
        fontweight="bold",
    )
    ax.set_xlabel("Tiempo de Foco Continuo Ininterrumpido (Minutos)", fontsize=11)
    ax.set_ylabel("Probabilidad de Mantener el Foco S(t)", fontsize=11)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(fontsize=10, loc="upper right")

    plot_file = output_dir / "curva_supervivencia_kaplan_meier.png"
    plt.tight_layout()
    plt.savefig(plot_file)
    plt.close()
    print(f" [ÉXITO] Gráfico guardado en: {plot_file}")

if __name__ == "__main__":
    run_survival_analysis("data/processed/estudiantes_clean.csv")