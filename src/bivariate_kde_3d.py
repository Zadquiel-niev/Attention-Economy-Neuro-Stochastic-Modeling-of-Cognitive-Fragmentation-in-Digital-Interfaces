import polars as pl
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from mpl_toolkits.mplot3d import Axes3D

def run_bivariate_kde_3d(data_path: str):
    df = pl.read_csv(data_path)
    
    x = df["IFA"].to_numpy()
    y = df["Productivity_Score"].to_numpy() # O Z-score de productividad
    
    # Ajuste de KDE Bivariado
    
    values = np.vstack([x, y])
    kernel = gaussian_kde(values)
    
    # Crear Grilla de Evaluación
    x_grid = np.linspace(0, 100, 100)
    y_grid = np.linspace(y.min(), y.max(), 100)
    X, Y = np.meshgrid(x_grid, y_grid)
    grid_coords = np.vstack([X.ravel(), Y.ravel()])
    
    Z = kernel(grid_coords).reshape(X.shape)
    
    # Graficación 3D de la Superficie
    
    fig = plt.figure(figsize=(12, 8), dpi=300)
    ax = fig.add_subplot(111, projection='3d')
    
    surf = ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none', alpha=0.85)
    
    # Marcador del Umbral Crítico P85 (IFA = 30.03)
    
    ax.axvline(x=30.03, color='red', linestyle='--', linewidth=2, label='Umbral Crítico P85 (IFA = 30.03)')
    
    ax.set_title("Superficie Bivariada KDE 3D: El Abismo de Productividad f(IFA, Y)", fontsize=13, fontweight='bold', pad=20)
    ax.set_xlabel("Índice de Fragmentación (IFA)", fontsize=10, labelpad=10)
    ax.set_ylabel("Productividad Cognitiva (Z-score)", fontsize=10, labelpad=10)
    ax.set_zlabel("Densidad de Probabilidad f(IFA, Y)", fontsize=10, labelpad=10)
    
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=8, label="Densidad Joint KDE")
    ax.view_init(elev=30, azim=225)
    
    plt.tight_layout()
    plt.savefig("reports/assets/superficie_kde_3d_abismo.png")
    plt.close()
    
    print(" Gráfico de la Superficie 3D guardado en: assets/superficie_kde_3d_abismo.png")

if __name__ == "__main__":
    run_bivariate_kde_3d("data/processed/estudiantes_clean.csv")