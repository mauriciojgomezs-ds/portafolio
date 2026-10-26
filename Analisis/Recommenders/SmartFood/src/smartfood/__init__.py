"""Exports disponibles sin cargar todos los modelos al importar SmartFood."""

from importlib import import_module

_EXPORTS = {'ejecutar_diagnostico': 'diagnostico', 'inspeccion_visual_md': 'inspeccion_md', 'inspeccion_visual': 'inspeccion', 'limpiar_columnas': 'limpieza', 'normalize_text': 'limpieza', 'limpiar_valores_texto': 'limpieza', 'wrapped_print': 'limpieza', 'recomendar_por_perfil_usuario': 'recomendaciones_base', 'calcular_similitud_coseno': 'recomendaciones_nmf', 'obtener_mas_similares': 'recomendaciones_nmf', 'generar_recomendaciones': 'recomendaciones_nmf', 'visualizar_recomendaciones': 'recomendaciones_nmf', 'predecir_rating': 'recomendaciones_nmf', 'evaluar_modelo': 'recomendaciones_nmf', 'evaluar_nmf_con_mascara': 'recomendaciones_nmf', 'grid_nmf': 'recomendaciones_nmf', 'graficar_resultados_grid': 'recomendaciones_nmf', 'entrenar_y_exportar_nmf': 'recomendaciones_nmf', 'entrenar_y_exportar_nmf_desde_grid': 'recomendaciones_nmf', 'evaluar_viabilidad_modelo_general': 'reporte', 'recomendar_similares_por_receta': 'recomendaciones_svm', 'recomendar_por_keywords': 'recomendaciones_svm', 'recomendar_por_calorias': 'recomendaciones_svm', 'exportar_recomendaciones_svm_en_lote': 'recomendaciones_svm', 'ranking_recetas_nuevas': 'recomendaciones_svm', 'ranking_por_categoria': 'recomendaciones_svm', 'exportar_recomendaciones_svm_por_usuario': 'recomendaciones_svm', 'similitud_recetas_tfidf': 'recomendaciones_svm', 'evaluar_threshold': 'recomendaciones_svm'}

__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(f".{_EXPORTS[name]}", __name__), name)
    globals()[name] = value
    return value
