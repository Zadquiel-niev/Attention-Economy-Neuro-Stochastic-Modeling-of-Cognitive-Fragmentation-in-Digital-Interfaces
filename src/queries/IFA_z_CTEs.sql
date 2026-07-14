WITH stats AS (
    SELECT 
        AVG(IFA) as avg_ifa, 
        STDEV(IFA) as std_ifa
    FROM estudiantes_clean
)
SELECT 
    s.*,
    (s.IFA - stats.avg_ifa) / NULLIF(stats.std_ifa, 0) as IFA_z
FROM estudiantes_clean s, stats;
