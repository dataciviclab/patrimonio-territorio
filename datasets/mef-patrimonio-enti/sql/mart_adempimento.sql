-- mart_adempimento: stato di adempimento al censimento immobiliare per regione
SELECT
    anno,
    regione,
    COUNT(*) AS totale_enti,
    COUNT(CASE WHEN obbligo_comunicazione AND invio_comunicazione THEN 1 END) AS obbligo_sì_invio_sì,
    COUNT(CASE WHEN obbligo_comunicazione AND NOT invio_comunicazione THEN 1 END) AS obbligo_sì_invio_no,
    COUNT(CASE WHEN NOT obbligo_comunicazione THEN 1 END) AS senza_obbligo,
    ROUND(100.0 * COUNT(CASE WHEN obbligo_comunicazione AND invio_comunicazione THEN 1 END) / NULLIF(COUNT(CASE WHEN obbligo_comunicazione THEN 1 END), 0), 1) AS pct_adempimento,
    SUM(COALESCE(num_beni_proprieta, 0)) AS totale_beni_proprieta,
    SUM(COALESCE(num_beni_detenzione, 0)) AS totale_beni_detenzione
FROM clean_input
GROUP BY anno, regione
