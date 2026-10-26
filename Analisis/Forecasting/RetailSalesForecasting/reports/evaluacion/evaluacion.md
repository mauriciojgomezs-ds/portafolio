# Pronóstico semanal de compras: evaluacion

El modelo **no mejora** el MAE del baseline: **220296.11** frente a **59811.14**, en **10 semanas de test**. El protocolo es a un paso; incorpora ventas reales previas al avanzar. Mide compras positivas, no ventas netas ni beneficios. Un único bloque corto no permite concluir robustez entre temporadas.
