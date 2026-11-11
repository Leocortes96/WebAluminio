# Tarea 5 · Google Ads: landings, medición y campañas

## 1. Estado actual de la medición (auditoría pública)

- Ambos sitios cargan **el mismo** contenedor `GTM-KHKH35V5`: los datos de los dos dominios se mezclan.
- La versión publicada del contenedor solo tiene un HTML personalizado de Matomo. **No hay GA4, ni etiqueta de conversión de Google Ads, ni disparadores de WhatsApp o teléfono.** Hoy no se mide ninguna conversión.
- En el `<head>` hay un gtag escrito a mano con el ID de ejemplo `G-XXXXXXXXXX`: no mide nada y genera errores.
- `/gracias/` existe en ambos sitios. El sitio nuevo no tiene enlaces `tel:`; el de WhatsApp (`wa.me/573148849505`) está en todas las páginas.
- Ninguna página tiene meta descripción (ver Tarea 4).

## 2. Landings: páginas antiguas frente a nuevas

| Página antigua (Ads) | Landing nueva propuesta | Lista para Ads |
|---|---|---|
| `/portafolio/ventanas-antiruido/` | `/portafolio/ventanas-antirruido/` y `/portafolio/linea-silencio-by-disenos-proyectos/` | Sí, después de la Tarea 4 |
| `/portafolio/divisiones-de-bano/` | `/portafolio/divisiones-de-bano-en-vidrio-templado/` | Sí, después de la Tarea 4 |
| `/portafolio/divisiones-para-oficinas/` | `/portafolio/divisiones-en-vidrio/` | Sí, después de la Tarea 4 |
| `/portafolio/pasamanos/` | `/portafolio/pasamanos-en-acero-inoxidable-y-vidrio/` | Sí, después de la Tarea 4 |
| `/portafolio/acero-inoxidable/` | `/portafolio/barandas-en-acero-inoxidable/` o `/portafolio/acero-inoxidable/` | Sí |
| `/portafolio/fachadas-comerciales/` | `/portafolio/fachadas-arquitectonicas/` | Sí |
| `/portafolio/vidrio/` | `/portafolio/soluciones-en-vidrio/` | Genérica: mejor para remarketing |
| `/portafolio/aluminio/` | `/portafolio/soluciones-en-aluminio/` | Sí |
| `/portafolio/instalaciones-y-asesorias/` | `/portafolio/remodelaciones-integrales/` | Pendiente de confirmar |
| — (nueva) | `/portafolio/puertas-y-ventanas-para-casas-campestres/` | Sí |

Antes de pautar, corrige en el sitio nuevo:

- Las menciones a "Imperio Industrias".
- Los contadores que muestran 0.
- Los años de experiencia, que no coinciden entre páginas.
- La afirmación "reduce hasta un 90 %", que no está verificada.

## 3. Checklist GA4 / GTM / conversiones

**Limpieza**
- [ ] Quitar el gtag `G-XXXXXXXXXX` escrito a mano del `<head>` en ambos sitios.
- [ ] Separar la medición: crear un contenedor GTM nuevo para disenosyproyectos.com, o filtrar por `Page Hostname` en todos los disparadores.

**GA4**
- [ ] Crear la propiedad GA4 del sitio nuevo y su flujo web.
- [ ] En GTM, crear la etiqueta *Google Tag* con el ID `G-…` y el disparador *Initialization – All Pages*.
- [ ] Activar la medición mejorada (scroll y clics salientes).

**Conversiones**
- [ ] **Formulario:** en Elementor › Formulario › Acciones después del envío, agregar *Redirect* a `/gracias/`. Crear el evento `generate_lead` en GTM con el disparador *Page View* y la condición `Page Path` igual a `/gracias/`.
- [ ] **WhatsApp:** disparador *Clic – Solo enlaces* con `Click URL` que coincida con la regex `wa\.me|api\.whatsapp\.com`. Enviar el evento `click_whatsapp`.
- [ ] **Teléfono:** agregar enlaces `tel:+573148849505` en el encabezado, el pie y los botones móviles. Disparador con `Click URL` que empiece por `tel:` y evento `click_telefono`.
- [ ] En GA4, marcar los tres eventos como **eventos clave**.

**Google Ads**
- [ ] Crear tres acciones de conversión en Google Ads: formulario (principal), WhatsApp (principal) y teléfono (secundaria si hay pocas).
- [ ] En GTM, agregar *Conversion Linker* en todas las páginas y una *Google Ads Conversion Tracking* por cada acción, con los mismos disparadores.
- [ ] Vincular Google Ads con GA4 y activar el etiquetado automático (gclid).
- [ ] Activar las **conversiones mejoradas para clientes potenciales** con el correo o el teléfono del formulario.
- [ ] Configurar el **modo de consentimiento v2** (banner de cookies).
- [ ] Probar con Tag Assistant: enviar un formulario y hacer clic en WhatsApp y en teléfono. Verificar en GA4 › DebugView y en el estado de la conversión en Ads. Después, publicar el contenedor.
- [ ] Purgar la caché de LiteSpeed después de cualquier cambio en el sitio.

## 4. Estructura inicial de campañas

- **Tipo:** Search.
- **Ubicación:** Pereira, Manizales, Armenia y municipios cercanos (Dosquebradas, Villamaría, Chinchiná, Santa Rosa de Cabal), con la opción "Presencia".
- **Puja:** empezar con *Maximizar clics* y un CPC máximo durante 2 a 4 semanas. Pasar a *Maximizar conversiones* al llegar a unas 15 conversiones al mes.
- **Prioridad:** una campaña por línea de producto, para controlar el presupuesto. Las de mayor intención van primero.

| Prioridad | Campaña | Grupos de anuncios | Palabras clave de ejemplo (frase o exacta) | Landing |
|---|---|---|---|---|
| 1 | Ventanas antirruido | Antirruido · Acústicas · Línea Silencio | "ventanas antirruido", "ventanas acústicas", "aislar ruido ventana", "ventanas insonorizadas Pereira" | ventanas-antirruido / linea-silencio |
| 2 | Divisiones de baño | Vidrio templado · Corredizas | "divisiones de baño", "división de baño en vidrio templado", "cabina de baño en vidrio" | divisiones-de-bano-en-vidrio-templado |
| 3 | Pasamanos y barandas | Pasamanos vidrio · Barandas inox | "pasamanos en vidrio", "pasamanos acero inoxidable", "barandas en acero inoxidable" | pasamanos… / barandas… |
| 4 | Divisiones de oficina | Oficinas · Consultorios | "divisiones en vidrio para oficina", "divisiones de oficina" | divisiones-en-vidrio |
| 5 | Ventanas y puertas en aluminio | Ventanas · Puertas · Campestres | "ventanas en aluminio", "puertas en aluminio y vidrio", "ventanas para casa campestre" | soluciones-en-aluminio / puertas-y-ventanas-… |
| 6 | Fachadas | Fachada flotante · Locales | "fachadas en vidrio", "fachada flotante", "fachada para local comercial" | fachadas-arquitectonicas |
| 7 | Remodelaciones | Integrales | "remodelación de apartamentos", "remodelaciones Manizales" | remodelaciones-integrales |

**Palabras clave negativas compartidas:** gratis, empleo, trabajo, vacantes, curso, cómo hacer, DIY, usado, segunda mano, Homecenter, Easy, precio por mayor, pdf, Bogotá, Medellín, Cali.

**Recursos:**
- Recurso de llamada con +57 314 884 9505.
- Recurso de WhatsApp o mensaje.
- Enlaces de sitio: Línea Silencio, Proyectos, Contáctenos, Divisiones de baño.
- Textos destacados: "Visita técnica", "Fábrica propia", "Instalación profesional", "Eje Cafetero".
- Recurso de ubicación desde el Perfil de Empresa de Google.

**Anuncios:** usar un RSA por grupo, con la palabra clave y la ciudad en los títulos, y textos tomados de los títulos SEO y las metas de la Tarea 4.

**Remarketing (fase 2):** después de 30 días con GA4, crear una audiencia de visitantes que no convirtieron para Demand Gen o Display.
