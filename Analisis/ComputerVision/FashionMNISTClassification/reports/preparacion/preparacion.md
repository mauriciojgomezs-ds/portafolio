# Clasificación visual de prendas: preparacion

Se preparan **12,000 imágenes de train**, **3,000 de validación** y el **test oficial completo de 10,000 imágenes**. Desarrollo se deduplica por contenido; se retiran grupos ambiguos y coincidencias exactas con test, conservando test intacto. El muestreo estratificado y sus límites se declaran en config.json. Los píxeles se normalizan por la constante 255, sin ajustar transformaciones con test.
