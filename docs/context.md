> **CAMBIO LAB v3 autorizado por José:** el piloto FISI permanece como foco, pero estudiantes de otras facultades pueden consultar fichas CENTRAL cuya accesibilidad universal esté **documentada**. Los registros sintéticos de transporte no son evidencia institucional y solo sirven para simular este caso.

# Contexto de producto y límites — Conecta UNMSM

## Decidido
- Competencia ENEISOFT XVI 2026, eje **Bienestar Universitario**.
- Producto: **Conecta UNMSM**. Alcance demostrable: **FISI**; aspiración: incorporar facultades futuras.
- Usuarios primarios: estudiantes que desean localizar el apoyo pertinente y entender cómo acceder.
- Propuesta de valor: **no** un directorio ni un chatbot libre, sino una ruta contextual, explicable, adaptativa y basada en evidencia institucional.
- Primer flujo: describir necesidad → aclaración si decisiva → seleccionar servicios documentados → pasos y fuente → actualizar ruta ante cambio significativo.
- Tiempo disponible: 6,5 h netas; equipo: José, Paolo y Daniela. El coach externo NO es participante confirmado.

## Categorías para registrar (solicitud actual; NO disponibilidad confirmada)
| `category_code` sugerido | Categoría | Restricción específica |
|---|---|---|
| `bienestar` | Unidad de Bienestar FISI | No asumir subsidio, afiliación a seguros o requisitos de otro programa. |
| `unayoe` | UNAYOE | No prometer citas ni atención psicológica como diagnóstico. |
| `clinica_general` | Clínica Universitaria / atención general | No atribuir servicio a FISI si lo brinda unidad central. |
| `salud_mental` | Centro/servicio de salud mental | Nombre, dependencia, servicios, canal y vigencia PENDIENTES de verificar. |
| `transporte_externo` | Transporte externo norte, sur, centro, este | Rutas/horarios/paradas/costos PENDIENTES; no ofrecer ubicación GPS ni ETA inventadas. |

**Importante:** estas son *familias de información prevista*, NO registros ya verificados. Una oficina puede prestar varios servicios; no crear duplicados artificiales. El nombre «clínica de salud mental» aún NO equivale a un nombre institucional confirmado.

## Funciones comprometidas para el MVP
1. Formulario en español con contexto FISI y campo de situación.
2. Pregunta de aclaración opcional, como máximo una ronda por consulta.
3. Selección ordenada de 1–3 servicios existentes, incluyendo necesidad y restricción relevantes.
4. Ruta con pasos concretos únicamente cuando los haya documentados; fuente y vigencia visibles.
5. Recalcular correctamente cuando cambia un dato relevante; si no cambia el resultado, explicar por qué.
6. Modo degradado ante fallos de IA/datos, sin engañar al usuario.

## No comprometido
- Crear/confirmar citas, tramitar pagos, aplicar a becas, hacer denuncias, dar diagnósticos ni ofrecer atención médica.
- Seguimiento de estados de trámites, perfiles, login, formularios sensibles, notificaciones, plataforma administrativa o aprobación institucional.
- Gestión en vivo de transporte, geolocalización y rutas seguras.
- Interpretación automática de comunicados y suspensión autónoma de servicios: idea futura que requiere revisión humana.

## Riesgo que determina éxito
**La fidelidad del catálogo**, no la cantidad de componentes. La implementación debe aceptar cero registros elegibles sin inventar información y permitir desarrollo con datos de prueba **etiquetados ficticios** antes de incorporar los datos reales posteriores.

## Regla de interacción clínica
Conecta NO evalúa riesgo psicológico ni decide urgencia. Mantener visible una opción para solicitar orientación sobre ayuda urgente, con consejo de acudir a asistencia humana y contactos oficiales **solo si están verificados**, sin clasificar automáticamente al usuario ni esperar respuesta del LLM.
