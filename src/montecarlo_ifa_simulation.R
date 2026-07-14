library(ggplot2)
library(dplyr)

datos <- read.csv('estudiantes_clean.csv')

# 1. Corrección de multicolinealidad e inyección de no-linealidad
datos <- datos %>% 
  mutate(Other_Screen_Time = pmax(0, Daily_Screen_Time_Hours - Social_Media_Usage_Hours)) %>%
  filter(IFA > 0)

modelo_robust <- lm(log(IFA) ~ Other_Screen_Time * Social_Media_Usage_Hours + 
                      App_Notifications_Received + Screen_Unlocks_Per_Day, data = datos)

sigma_res <- sigma(modelo_robust)

# 2. Simulación Montecarlo no paramétrica (Resampling conjunto)
set.seed(42)
n_iteraciones <- 10000
indices_bootstrap <- sample(1:nrow(datos), n_iteraciones, replace = TRUE)

perfiles_simulados <- datos[indices_bootstrap, c("Other_Screen_Time", "Social_Media_Usage_Hours", 
                                                 "App_Notifications_Received", "Screen_Unlocks_Per_Day")]

# 3. Proyección estocástica con ruido multiplicativo
ruido_exogeno <- rnorm(n_iteraciones, mean = 0, sd = sigma_res)
pred_log <- predict(modelo_robust, newdata = perfiles_simulados)
perfiles_simulados$IFA_proyectado <- exp(pred_log + ruido_exogeno)

# 4. Normalización de la escala (0 - 100)
min_ifa <- min(perfiles_simulados$IFA_proyectado)
max_ifa <- max(perfiles_simulados$IFA_proyectado)
perfiles_simulados$IFA_score <- ((perfiles_simulados$IFA_proyectado - min_ifa) / (max_ifa - min_ifa)) * 100

# 5. Extracción de métricas críticas
umbral_critico <- quantile(perfiles_simulados$IFA_score, 0.85)
casos_colapso <- perfiles_simulados %>% filter(IFA_score >= umbral_critico)

cat("\n--- RESULTADOS METODOLÓGICAMENTE BLINDADOS ---\n")
cat("Umbral Crítico Estocástico (Percentil 85):", round(umbral_critico, 2), "puntos.\n")
cat("Media de Desbloqueos en Riesgo Alto:", round(mean(casos_colapso$Screen_Unlocks_Per_Day), 0), "al día.\n")
cat("Media de Horas Redes en Riesgo Alto:", round(mean(casos_colapso$Social_Media_Usage_Hours), 1), "horas.\n")

# 6. Visualización limpia
grafico_final <- ggplot(perfiles_simulados, aes(x = IFA_score)) +
  geom_density(fill = "#2C3E50", alpha = 0.5, color = "#2C3E50", linewidth = 1) +
  geom_vline(xintercept = umbral_critico, color = "#E74C3C", linetype = "dashed", linewidth = 1.2) +
  labs(
    title = "Distribución del Índice de Fragmentación Atencional (IFA)",
    subtitle = "Simulación Montecarlo basada en remuestreo empírico y modelo log-lineal",
    x = "IFA Score (0 - 100)",
    y = "Densidad de Frecuencia Estocástica"
  ) +
  theme_minimal()

ggsave("grafico_montecarlo_final.png", plot = grafico_final, width = 8, height = 5, dpi = 300)