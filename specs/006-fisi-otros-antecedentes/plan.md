# Plan técnico

1. **Daniela — UI:** selector de dos ámbitos y mensajes de espera, cancelación, guardado y cuentas; DOM seguro con `textContent`.
2. **José — backend/Supabase:** conservar el filtro de facultad, añadir consulta de antecedentes verificables por país sin incorporar registros cerrados a la selección abierta, añadir campo `historical_services` y `country_context` en la respuesta JSON, preparar UPSERT SQL revisado sin cambiar RLS.
3. **Paolo — ranking/IA:** filtro determinista de país, investigación formativa prioritariamente VRAP y máximo seis candidatos a Gemini; el caso sin convocatoria de país no delega la invención de plazos al LLM.
4. **Scraping:** feeds permitidos OGCRI/VRAP/VRIP, historial paginado con límites, `robots.txt`, solicitud acotada, cola manual `pending` y publicación SQL bajo revisión humana.
5. **Compatibilidad:** mantener `/api/route`, `/api/history/save`, Auth y rutas de bienestar, clínica y transporte existentes. Sin nombres de versión visibles en la interfaz.
