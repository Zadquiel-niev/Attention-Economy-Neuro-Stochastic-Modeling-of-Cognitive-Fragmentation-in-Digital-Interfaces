import numpy as np
import matplotlib.pyplot as plt

def lambda_intensity(t_hours):
    
    """
    Función de intensidad diurna lambda(t) con 3 picos gaussianos de fricción
    t_hours en [0, 17] (equivalente a 6:00 AM a 11:00 PM)
    """
    lambda_0 = 3.5  # Tasa base
    
    # Pico 1: Matutino (9:30 AM -> t = 3.5h)
    pico_1 = 12.0 * np.exp(-((t_hours - 3.5) ** 2) / (2 * (1.2 ** 2)))
    
    # Pico 2: Tarde (3:30 PM -> t = 9.5h)
    pico_2 = 15.5 * np.exp(-((t_hours - 9.5) ** 2) / (2 * (1.5 ** 2)))
    
    # Pico 3: Nocturno (9:30 PM -> t = 15.5h)
    pico_3 = 18.2 * np.exp(-((t_hours - 15.5) ** 2) / (2 * (1.0 ** 2)))
    
    return lambda_0 + pico_1 + pico_2 + pico_3

def simulate_nhpp_thinning(t_max=17.0, lambda_max=40.0):
    """
    Simulación estocástica de Poisson No Homogéneo mediante el Algoritmo de Thinning
    """
    t = 0.0
    events = []
    
    while t < t_max:
        
        # Generar siguiente tiempo de llegada potencial desde proceso homogéneo envolvente
        u1 = np.random.uniform(0, 1)
        t += -np.log(u1) / lambda_max
        
        if t >= t_max:
            break
            
        # Aceptar con probabilidad lambda(t) / lambda_max
        u2 = np.random.uniform(0, 1)
        if u2 <= lambda_intensity(t) / lambda_max:
            events.append(t)
            
    return np.array(events)

def run_nhpp_simulation():
    np.random.seed(42)
    
    #  Definir Vector de Tiempo
    t_grid = np.linspace(0, 17, 500)
    intensity_grid = lambda_intensity(t_grid)
    
    #  Simular Trayectorias de Llegada Acumulada N(t)
    sim_sub = simulate_nhpp_thinning(lambda_max=20.0) # Subcrítico ajustado
    sim_sat = simulate_nhpp_thinning(lambda_max=45.0) # Saturado
    
    #  Graficación de Intensity y N(t)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), dpi=300, sharex=True)
    
    # Panel Superior: Tasa de Intensidad lambda(t)
    ax1.plot(t_grid, intensity_grid, color="#d62728", linewidth=2.5, label=r"Tasa de Intensidad $\lambda(t)$ (Eventos/Hora)")
    ax1.set_title("Proceso de Poisson No Homogéneo (NHPP) - Dinámica Intra-diaria de Interrupciones", fontsize=12, fontweight="bold")
    ax1.set_ylabel(r"Intensidad $\lambda(t)$ [Eventos/Hora]", fontsize=10)
    ax1.grid(True, linestyle=":", alpha=0.6)
    ax1.legend(loc="upper left")
    
    # Panel Inferior: Trayectorias Acumuladas N(t)
    ax2.step(sim_sub, np.arange(1, len(sim_sub) + 1), where='post', color="#1f77b4", label=f"Régimen Subcrítico (Total: {len(sim_sub)} interrupciones)")
    ax2.step(sim_sat, np.arange(1, len(sim_sat) + 1), where='post', color="#d62728", label=f"Régimen Saturado (Total: {len(sim_sat)} interrupciones)")
    
    ax2.set_xlabel("Jornada Diaria Activa (Horas desde las 06:00 AM hasta las 11:00 PM)", fontsize=10)
    ax2.set_ylabel(r"Interrupciones Acumuladas $N(t)$", fontsize=10)
    ax2.set_xticks([0, 3.5, 9.5, 15.5, 17])
    ax2.set_xticklabels(["06:00 AM", "09:30 AM", "03:30 PM", "09:30 PM", "11:00 PM"])
    ax2.grid(True, linestyle=":", alpha=0.6)
    ax2.legend(loc="upper left")
    
    plt.tight_layout()
    plt.savefig("reports/assets/simulacion_poisson_no_homogeneo.png")
    plt.close()
    
  
    print(" RESULTADOS DE LA SIMULACIÓN DE POISSON NO HOMOGÉNEO (NHPP)")
    print(f"- Total Interrupciones Simuladas en Régimen Subcrítico : {len(sim_sub)} eventos/día.")
    print(f"- Total Interrupciones Simuladas en Régimen Saturado   : {len(sim_sat)} eventos/día.")
    print(" Gráfico guardado en: assets/simulacion_poisson_no_homogeneo.png\n")

if __name__ == "__main__":
    run_nhpp_simulation()