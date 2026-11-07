# Conecta UNMSM — Especificación: oportunidades académicas documentadas

## Contexto y objetivo
Las personas de la UNMSM necesitan orientación desde una sola descripción de su situación para identificar oportunidades **reales, trazables y compatibles** con su perfil (pregrado, posgrado o docencia), especialmente las difundidas por OCGRI, VRAP, VRIP y unidades académicas. Bienestar FISI, Clínica y transporte siguen presentes como apoyos complementarios. El producto no garantiza admisiones, citas, fondos ni que las convocatorias estén abiertas.

## Actores
Personas que consultan como visitantes; usuarios que optan por una cuenta; equipo que revisa fuentes académicas antes de publicar.

## Historias de usuario
- H1: Como estudiante de posgrado quiero describir mi necesidad de viajar y ver programas de movilidad académica y becas documentadas acordes con mi perfil.
- H2: Como estudiante de pregrado quiero averiguar convocatorias sin recibir programas exclusivos para docentes o para otra facultad.
- H3: Como docente quiero conocer oportunidades pertinentes y comprobar las bases de su convocatoria.
- H4: Como estudiante de FISI quiero seguir recibiendo orientación sobre Bienestar, Clínica y transporte cuando corresponda.
- H5: Como curador de contenidos quiero descubrir anuncios publicados sin que ingresen automáticamente al catálogo accesible.

## Requisitos funcionales — EARS
- **RF-AC-01:** CUANDO la persona abra el formulario, EL SISTEMA mostrará como ejemplo de entrada «Soy un estudiante y...» sin exigir que comience de esa manera.
- **RF-AC-02:** CUANDO la persona seleccione una facultad de las 20 listadas, EL SISTEMA considerará servicios documentados exclusivos de esa facultad y los centrales explícitamente universales, sin atribuir a una facultad programas de otra.
- **RF-AC-03:** CUANDO se mencione una beca, intercambio, investigación, actividad o convocatoria académica, EL SISTEMA filtrará los registros por la categoría correspondiente y por el perfil declarado o aclarado.
- **RF-AC-04:** SI el perfil es necesario para distinguir entre pregrado, posgrado y docentes, ENTONCES EL SISTEMA solicitará como máximo una aclaración antes de seleccionar oportunidades.
- **RF-AC-05:** CUANDO se muestre una oportunidad, EL SISTEMA incluirá un enlace de fuente cuando conste y mostrará advertencias sobre vigencia, requisitos y límites documentales pertinentes.
- **RF-AC-06:** SI un anuncio no permite confirmar la inscripción vigente, ENTONCES EL SISTEMA evitará declararlo «abierto», «disponible» o «vacante confirmada».
- **RF-AC-07:** CUANDO se ejecute la exploración de fuentes web permitidas, EL SISTEMA generará una cola de candidatos pendientes de revisión sin insertarlos automáticamente en la tabla pública de Supabase.
- **RF-AC-08:** CUANDO se solicite personalización, EL SISTEMA enviará a Gemini como máximo seis candidatos elegibles y aceptará únicamente un máximo de tres IDs pertenecientes a esa selección.
- **RF-AC-09:** CUANDO se pregunte por bienestar, clínica o transporte, EL SISTEMA conservará esas rutas complementarias solo dentro de la cobertura sustentada y sin inventar citas, paradas ni horarios.
- **RF-AC-10:** SI falla Gemini o Supabase, ENTONCES EL SISTEMA mostrará un modo informativo explícito y utilizará exclusivamente un respaldo documental revisado cuando esté disponible.
- **RF-AC-11:** MIENTRAS el usuario sea visitante, EL SISTEMA permitirá consultas sin autenticación y no guardará sus descripciones; solo se habilitará historial voluntario tras validación de sesión.

## Requisitos no funcionales
La interfaz y documentación están en español; IDs/código en inglés. No almacenar consultas libres ni credenciales. El navegador no recibe claves de Gemini. No producir resultados desde datos `prueba_ficticia` en operación normal. El scraping respeta dominios permitidos y reglas `robots.txt`; la accesibilidad de fuentes externas no se garantiza.

## Casos límite
- Un convenio es **no necesariamente** una beca; si se consulta financiación, no convertir convenio en beca.
- La misma oportunidad puede aceptar posgrado **y** docentes. Verificar la audiencia conjunta sin duplicar una convocatoria.
- Una publicación del ciclo 2027 puede tener plazos parciales vencidos y otros sin publicar: estado por confirmar.
- Consulta «Soy un estudiante y quiero viajar»: aclarar pregrado o posgrado si esa diferencia cambia la selección.
- Publicación OGCRI inaccesible o robots bloqueado: marcar fallo, no crear información.
- Otras facultades no heredan Bienestar FISI ni una oferta específica de Medicina.

## Fuera de alcance
Postular automáticamente, notificar convocatorias, pagar, agendar citas, triaje clínico, scraping autónomo que publique, cuentas institucionales acreditadas, verificación en tiempo real de cupos y becas, búsqueda vectorial o agentes autónomos.

## Criterios de finalización
RF-AC con pruebas automatizadas o revisión manual registrada; SQL idempotente; sin credenciales; documentación de fuentes; flujo de ejemplo académicamente pertinente y un fallo controlado; demostrar que noticias descubiertas no quedan publicadas automáticamente.

## Dudas abiertas
- [NECESITA ACLARACIÓN] ¿Quién actualizará cada semana las convocatorias y marcará fechas vencidas? Esto no bloquea la primera publicación con advertencias.
- [NECESITA ACLARACIÓN] ¿La organización autoriza incorporar esta base de laboratorio en el repositorio de competencia? Revisar antes de entregar.
