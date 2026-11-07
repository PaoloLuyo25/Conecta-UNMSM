'use strict';
/* Datos no confiables solo con textContent. Tokens exclusivamente en cookies HttpOnly. */
const $ = (id) => document.getElementById(id);
const form = $('consult-form');
const result = $('result');
const messageInput = $('message');
const state = {
  message: '', facultyCode: 'FISI', applicantType: 'sin_especificar', previousIds: [], clarificationUsed: false,
  busy: false, controller: null, sequence: 0, authenticated: false,
  historyEnabled: false, routeTicket: null, routeRequestId: null, routeSaved: false,
  entered: false, pendingSaveAfterAuth: false
};

function node(tag, text, className) {
  const element = document.createElement(tag);
  if (text !== undefined && text !== null) element.textContent = String(text);
  if (className) element.className = className;
  return element;
}
function hide(element, hidden) { element.classList.toggle('hidden', hidden); }
function enterWorkspace() {
  state.entered = true;
  hide($('welcome-screen'), true);
  hide($('app-main'), false);
}
function openAuth(message = '') {
  const overlay = $('auth-overlay');
  hide(overlay, false);
  document.body.classList.add('auth-open');
  if (message) accountMessage(message);
  $('account-panel').focus();
}
function closeAuth() {
  hide($('auth-overlay'), true);
  document.body.classList.remove('auth-open');
  state.pendingSaveAfterAuth = false;
  $('header-auth-button').focus();
}
$('welcome-guest').addEventListener('click', enterWorkspace);
$('welcome-login').addEventListener('click', () => openAuth());
$('header-auth-button').addEventListener('click', () => openAuth());
$('close-auth-button').addEventListener('click', closeAuth);
$('auth-overlay').addEventListener('click', event => {
  if (event.target === $('auth-overlay')) closeAuth();
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && !$('auth-overlay').classList.contains('hidden')) closeAuth();
});
function status(text) { $('state-badge').textContent = text; }
function warnings(items) {
  $('alerts').replaceChildren();
  for (const warning of items || []) {
    $('alerts').append(node('div', warning, 'alert'));
  }
}
function setBusy(active) {
  state.busy = active;
  $('submit').disabled = active;
  $('refine-button').disabled = active;
  $('submit-label').textContent = active ? 'Buscando tu ruta…' : 'Encontrar mi ruta ↗';
  hide($('loading-spinner'), !active);
  result.setAttribute('aria-busy', String(active));
  $('sr-status').textContent = active ? 'Buscando opciones' : '';
}
function fact(parent, label, value) {
  if (!value || (Array.isArray(value) && !value.length)) return;
  const line = node('div', null, 'fact');
  line.append(node('strong', label));
  line.append(node('span', Array.isArray(value) ? value.join(' · ') : value));
  parent.append(line);
}
function serviceCard(service, index) {
  const card = node('article', null, 'service-card');
  card.append(node('div', `OPCIÓN ${index + 1}`, 'service-number'));
  card.append(node('h3', service.name));
  const tags = node('div', null, 'tags');
  tags.append(node('span', service.category_code?.replaceAll('_', ' ') || 'Servicio', 'tag'));
  tags.append(node('span', service.faculty_code === 'CENTRAL' ? 'Servicio central' : `Ámbito ${service.faculty_code}`, 'tag'));
  card.append(tags);
  card.append(node('p', service.description));
  if (service.why_text) card.append(node('div', service.why_text, 'reason'));
  const facts = node('div', null, 'facts');
  fact(facts, 'Dirigido a', service.audience);
  fact(facts, 'Modalidad', service.modality);
  fact(facts, 'Pasos', service.official_steps);
  fact(facts, 'Requisitos', service.requirements);
  fact(facts, 'Ubicación', service.location);
  fact(facts, 'Horarios', service.hours);
  fact(facts, 'Contacto', [service.contact?.email, service.contact?.phone].filter(Boolean));
  fact(facts, 'Zona', service.route_region);
  fact(facts, 'Paradas', service.stops);
  fact(facts, 'Revisión', service.verified_at || 'Por confirmar');
  card.append(facts);
  if (service.source_url) {
    try {
      const url = new URL(service.source_url);
      if (url.protocol === 'https:' || url.protocol === 'http:') {
        const link = node('a', 'Consultar fuente documentada ↗');
        link.href = url.href; link.target = '_blank'; link.rel = 'noopener noreferrer';
        facts.append(link);
      }
    } catch (_) { /* URL inválida: se omite sin romper la UI. */ }
  }
  for (const warning of service.warnings || []) card.append(node('p', warning, 'warning-small'));
  return card;
}
function initialResult() {
  const art = node('div', '✳', 'empty-art');
  art.setAttribute('aria-hidden', 'true');
  result.replaceChildren(art, node('h3', 'Tu camino empieza aquí'),
    node('p', 'Escribe una necesidad para explorar opciones respaldadas por el catálogo.'));
  result.className = 'empty-state';
}
function newQuery() {
  state.sequence += 1;
  if (state.controller) state.controller.abort();
  state.controller = null;
  setBusy(false);
  form.reset();
  state.message = ''; state.facultyCode = 'FISI'; state.applicantType = 'sin_especificar';
  state.previousIds = []; state.clarificationUsed = false;
  $('clarification-form').reset();
  $('refine-value').value = '';
  state.routeTicket = null; state.routeRequestId = null; state.routeSaved = false;
  $('save-route-status').textContent = '';
  $('counter').textContent = '0 / 800';
  $('meta').textContent = '';
  warnings([]);
  hide($('clarification'), true);
  hide($('refine'), true);
  initialResult();
  status('Listo');
  hide($('history-choice'), true);
  messageInput.focus();
}
function render(data) {
  warnings(data.warnings);
  result.replaceChildren();
  hide($('clarification'), true);
  hide($('refine'), data.mode === 'question');
  state.previousIds = (data.services || []).map(s => s.id);
  state.routeTicket = data.route_ticket || null;
  state.routeRequestId = null;
  state.routeSaved = Boolean(data.history_saved);
  $('save-route-status').textContent = data.history_saved ? 'Ruta guardada.' : '';
  updateSaveRoute();
  if (data.mode === 'question') {
    status('Una pregunta más');
    $('clarification-question').textContent = data.question || '¿Puedes precisar tu consulta?';
    $('clarification-answer').value = '';
    hide($('clarification'), false);
    result.append(node('p', 'Responde esta aclaración para continuar.'));
  } else if (data.services?.length) {
    status('Opciones encontradas');
    result.append(node('p', data.mode === 'degraded'
      ? 'No fue posible personalizar las opciones; confirma su vigencia.'
      : 'Revisa las fuentes, requisitos y advertencias de cada ficha.', 'subtle'));
    const cards = node('div', null, 'cards');
    data.services.forEach((service, i) => cards.append(serviceCard(service, i)));
    result.append(cards);
    if (data.history_saved) $('sr-status').textContent = 'Tu ruta se guardó correctamente.';
  } else {
    status('Sin coincidencias');
    result.append(node('h3', 'No hay una ruta confirmada'));
    result.append(node('p', 'No se encontraron servicios verificables para esta consulta.'));
  }
  result.className = data.services?.length ? '' : 'empty-state';
  $('meta').textContent = `Catálogo: ${data.catalog_source || 'desconocido'} · Revisión: ${data.catalog_verified_at || 'por confirmar'} · ${data.ai_used ? 'Selección con IA' : 'Sin personalización de IA'}`;
}
async function ask(payload) {
  if (state.busy) return;
  const seq = ++state.sequence;
  const controller = new AbortController();
  state.controller = controller;
  state.routeTicket = null; state.routeRequestId = null; state.routeSaved = false;
  hide($('history-choice'), true);
  setBusy(true);
  hide($('clarification'), true);
  const timeout = setTimeout(() => controller.abort(), 35000);
  try {
    const response = await fetch('/api/route', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      credentials: 'same-origin', body: JSON.stringify(payload), signal: controller.signal
    });
    if (seq !== state.sequence) return;
    const data = await response.json();
    if (seq !== state.sequence) return;
    if (!response.ok) throw new Error(response.status === 422
      ? 'Revisa la longitud o el formato de tu consulta.' : 'No fue posible completar la búsqueda.');
    render(data);
  } catch (error) {
    if (seq !== state.sequence) return;
    warnings([error.name === 'AbortError' ? 'La búsqueda tardó demasiado. Inténtalo de nuevo.' : error.message]);
    status('Intenta de nuevo');
    result.replaceChildren(node('p', 'No pudimos recuperar opciones. Puedes volver a intentarlo.'));
    result.className = 'empty-state';
    hide($('refine'), false);
  } finally {
    clearTimeout(timeout);
    if (seq === state.sequence) { state.controller = null; setBusy(false); }
  }
}
function requestPayload(answer = null, used = false) {
  const wantsSave = false; // Guardado explícito POST /api/history/save después de generar la ruta.
  const payload = {
    faculty_code: state.facultyCode, applicant_type: state.applicantType, message: state.message,
    clarification_answer: answer, clarification_used: used,
    previous_service_ids: state.previousIds,
    save_to_history: wantsSave
  };
  if (wantsSave) payload.client_request_id = crypto.randomUUID();
  return payload;
}
messageInput.addEventListener('input', () => { $('counter').textContent = `${messageInput.value.length} / 800`; });
$('new-query-button').addEventListener('click', newQuery);
form.addEventListener('submit', (event) => {
  event.preventDefault();
  if (state.busy) return;
  state.message = messageInput.value.trim();
  state.facultyCode = $('faculty').value; state.applicantType = $('applicant-type').value;
  state.clarificationUsed = false;
  state.previousIds = [];
  state.routeTicket = null; state.routeSaved = false; state.routeRequestId = null;
  hide($('history-choice'), true);
  if (!state.message || state.message.length > 800) return;
  const payload = requestPayload();
  ask(payload);
});
$('clarification-form').addEventListener('submit', (event) => {
  event.preventDefault();
  if (state.busy) return;
  const answer = $('clarification-answer').value.trim();
  if (!answer || answer.length > 400) return;
  state.clarificationUsed = true;
  ask(requestPayload(answer, true));
});
$('refine-button').addEventListener('click', () => {
  if (state.busy) return;
  const restriction = $('refine-value').value.trim();
  if (!restriction || !state.message) return;
  const updated = `${state.message}. Restricción actualizada: ${restriction}`;
  if (updated.length > 800) { warnings(['El texto completo supera 800 caracteres.']); return; }
  state.message = updated; messageInput.value = updated;
  messageInput.dispatchEvent(new Event('input'));
  $('refine-value').value = '';
  ask(requestPayload());
});
for (const button of document.querySelectorAll('[data-example]')) {
  button.addEventListener('click', () => {
    messageInput.value = button.dataset.example;
    messageInput.dispatchEvent(new Event('input'));
    messageInput.focus();
  });
}
function updateSaveRoute() {
  hide($('history-choice'), !(state.historyEnabled && state.routeTicket));
  $('save-route-button').disabled = state.routeSaved;
  if (state.routeTicket && state.historyEnabled && !state.authenticated) {
    $('save-route-status').textContent = 'Para guardar, inicia sesión o crea una cuenta.';
  } else if (state.routeTicket && !state.routeSaved) {
    $('save-route-status').textContent = '';
  }
}
$('save-route-button').addEventListener('click', async () => {
  if (!state.historyEnabled || !state.routeTicket || state.routeSaved) return;
  if (!state.authenticated) {
    state.pendingSaveAfterAuth = true;
    openAuth('Inicia sesión o crea una cuenta para guardar esta ruta. Al entrar, la guardaremos automáticamente.');
    return;
  }
  await saveExistingRoute();
});
async function saveExistingRoute() {
  if (!state.historyEnabled || !state.authenticated || !state.routeTicket || state.routeSaved) return;
  const ticket = state.routeTicket;
  const sequence = state.sequence;
  if (!state.routeRequestId) state.routeRequestId = crypto.randomUUID();
  $('save-route-button').disabled = true;
  $('save-route-status').textContent = 'Guardando…';
  try {
    await api('/api/history/save', {method: 'POST', body: JSON.stringify({
      route_ticket: ticket, client_request_id: state.routeRequestId
    })});
    if (sequence !== state.sequence || ticket !== state.routeTicket) return;
    state.routeSaved = true;
    $('save-route-status').textContent = 'Ruta guardada correctamente.';
    await showHistory();
  } catch (error) {
    if (sequence !== state.sequence || ticket !== state.routeTicket) return;
    $('save-route-status').textContent = error.message;
  } finally {
    if (sequence === state.sequence && ticket === state.routeTicket) {
      $('save-route-button').disabled = state.routeSaved;
    }
  }
}
$('faculty').addEventListener('change', () => {
  state.facultyCode = $('faculty').value; state.applicantType = $('applicant-type').value;
  state.previousIds = [];
  state.routeTicket = null; state.routeRequestId = null; state.routeSaved = false;
  hide($('history-choice'), true);
  result.replaceChildren(node('p', 'Cambiaste el ámbito: consulta de nuevo para ver servicios elegibles.'));
  status('Ámbito actualizado');
  hide($('clarification'), true);
  hide($('refine'), true);
});


$('applicant-type').addEventListener('change', () => {
  state.applicantType = $('applicant-type').value;
  state.previousIds = [];
  state.routeTicket = null; state.routeRequestId = null; state.routeSaved = false;
  hide($('history-choice'), true);
  hide($('clarification'), true);
  hide($('refine'), true);
  result.replaceChildren(node('p', 'Cambiaste el público: consulta de nuevo para recalcular la ruta.'));
  status('Público actualizado');
});

async function api(path, options = {}) {
  const response = await fetch(path, {credentials: 'same-origin', ...options,
    headers: {'Content-Type': 'application/json', ...(options.headers || {})}});
  const body = await response.json();
  if (!response.ok) throw new Error(body?.detail || 'No se completó la operación.');
  return body;
}
function accountMessage(text) { $('account-status').textContent = text; }
function authView() {
  hide($('login-form'), state.authenticated);
  hide($('account-actions'), !state.authenticated);
  $('header-auth-button').textContent = state.authenticated ? 'Mis rutas / Mi cuenta' : 'Iniciar sesión';
  $('account-title').textContent = state.authenticated ? 'Tus rutas guardadas' : 'Inicia sesión o crea tu cuenta';
  updateSaveRoute();
  if (!state.authenticated) $('history-items').replaceChildren();
}
async function authStatus() {
  try {
    const me = await api('/api/auth/me');
    state.authenticated = Boolean(me.authenticated);
    authView();
    if (state.authenticated) {
      enterWorkspace(); // Si ya existe una sesión válida, no mostramos la bienvenida.
      await showHistory();
    }
  } catch (_) { state.authenticated = false; authView(); }
}
async function initAccount() {
  try {
    const features = await api('/api/features');
    state.historyEnabled = Boolean(features.history_enabled);
    hide($('history-unavailable'), state.historyEnabled);
    hide($('history-available'), !state.historyEnabled);
    if (state.historyEnabled) await authStatus();
    else authView();
  } catch (_) {
    $('history-unavailable').textContent = 'No se pudo comprobar la disponibilidad del historial. Las consultas siguen funcionando sin guardar datos.';
  }
}
async function passwordAccess(mode) {
  const email = $('login-email').value.trim().toLowerCase();
  $('login-email').value = email;
  const passwordInput = $('login-password');
  if (!/^[^@\s]+@unmsm\.edu\.pe$/.test(email)) {
    accountMessage('Utiliza un correo que termine en @unmsm.edu.pe.');
    return;
  }
  if (!$('login-form').reportValidity()) return;
  const payload = JSON.stringify({email, password: passwordInput.value});
  const buttons = $('login-form').querySelectorAll('button');
  buttons.forEach(button => { button.disabled = true; });
  try {
    await api(mode === 'signup' ? '/api/auth/signup' : '/api/auth/login', {
      method: 'POST', body: payload
    });
    state.authenticated = true;
    passwordInput.value = '';
    authView();
    accountMessage(mode === 'signup'
      ? 'Cuenta creada. Tu sesión está activa; ya puedes guardar rutas.'
      : 'Sesión iniciada. Ya puedes guardar rutas.');
    enterWorkspace();
    const shouldSave = state.pendingSaveAfterAuth && Boolean(state.routeTicket) && !state.routeSaved;
    state.pendingSaveAfterAuth = false;
    closeAuth();
    if (shouldSave) await saveExistingRoute();
    else await showHistory();
  } catch (error) {
    accountMessage(error.message);
  } finally {
    buttons.forEach(button => { button.disabled = false; });
  }
}
$('login-form').addEventListener('submit', async event => {
  event.preventDefault();
  await passwordAccess('login');
});
$('register-button').addEventListener('click', async () => {
  await passwordAccess('signup');
});
$('logout').addEventListener('click', async () => {
  try { await api('/api/auth/logout', {method: 'POST', body: '{}'}); }
  catch (_) { /* El usuario ve la sesión hasta que se confirme el cierre. */ return accountMessage('No se pudo cerrar sesión.'); }
  state.authenticated = false;
  state.routeSaved = false; state.routeRequestId = null;
  $('login-password').value = '';
  authView(); accountMessage('Sesión cerrada. Puedes seguir consultando como visitante.');
  closeAuth();
});
async function showHistory() {
  try {
    const data = await api('/api/history?limit=20&offset=0');
    $('history-items').replaceChildren();
    if (!data.items.length) $('history-items').append(node('p', 'Aún no hay rutas guardadas.'));
    for (const entry of data.items) {
      const container = node('article', null, 'history-entry');
      container.append(node('h3', 'Ruta del ' + new Date(entry.created_at).toLocaleDateString('es-PE')));
      container.append(node('p', `Ámbito: ${entry.faculty_code} · Catálogo: ${entry.catalog_source}`));
      if (entry.needs_revalidation) container.append(node('p', 'Algunos servicios ya no están vigentes o disponibles para este ámbito.', 'alert'));
      const cards = node('div', null, 'cards');
      entry.services.forEach((service, i) => cards.append(serviceCard(service, i)));
      container.append(cards);
      const button = node('button', 'Eliminar esta ruta', 'secondary danger');
      button.type = 'button';
      button.addEventListener('click', async () => {
        if (!confirm('¿Eliminar esta ruta de tu historial?')) return;
        try { await api('/api/history/' + encodeURIComponent(entry.id), {method: 'DELETE'}); await showHistory(); }
        catch (error) { accountMessage(error.message); }
      });
      container.append(button);
      $('history-items').append(container);
    }
  } catch (error) { accountMessage(error.message); }
}
$('show-history').addEventListener('click', showHistory);
$('delete-history').addEventListener('click', async () => {
  if (!confirm('¿Borrar permanentemente todas tus rutas guardadas?')) return;
  try { await api('/api/history', {method: 'DELETE'}); await showHistory(); accountMessage('Historial eliminado.'); }
  catch (error) { accountMessage(error.message); }
});
initAccount();
