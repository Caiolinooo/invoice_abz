const $ = (sel) => document.querySelector(sel);
const statusEl = $('#status');
let SESSION_ID = null;
let PREVIEW = null;

// utils
function toDDMMYYYY(val){
  if(!val) return null;
  // Browser date input yields yyyy-mm-dd
  const m = /^\d{4}-\d{2}-\d{2}$/.test(val) ? val.match(/^(\d{4})-(\d{2})-(\d{2})$/) : null;
  if(m){ return `${m[3]}/${m[2]}/${m[1]}`; }
  const m2 = val.match(/(\d{2})[\/\-](\d{2})[\/\-](\d{4})/);
  if(m2){ return `${m2[1]}/${m2[2]}/${m2[3]}`; }
  return val.trim();
}

async function loadSeqAndHint(){
  try{
    const r = await fetch('/api/invoice-seq');
    if(!r.ok) return;
    const d = await r.json();
    const last = parseInt(d.last||0,10);
    const el = document.querySelector('#invoiceNo');
    if(el){
      const currentLang = getCurrentLanguage();
      const suggestion = currentLang === 'en' ? 'suggestion' : 'sugestão';
      el.placeholder = `${suggestion}: ${last+1}`;
    }
  }catch{}
}

// Update suggestion when user types a manual invoice number
function setupInvoiceNumberListener() {
  const el = document.querySelector('#invoiceNo');
  if (!el) return;

  el.addEventListener('input', function() {
    const value = this.value.trim();
    if (value && /^\d+$/.test(value)) {
      // User typed a number - this will be used as base for next invoices
      const nextSuggestion = parseInt(value, 10) + 1;
      const currentLang = getCurrentLanguage();
      const nextLabel = currentLang === 'en' ? 'next' : 'próximo';
      this.title = `${nextLabel}: ${nextSuggestion}`;
    } else {
      this.title = '';
    }
  });
}

function setStatus(text, isError = false) {
  const statusIcon = statusEl.querySelector('.material-icons');
  const statusText = statusEl.querySelector('span:last-child');

  if (statusIcon) {
    statusIcon.textContent = isError ? 'error' : 'check_circle';
  }

  if (statusText) {
    statusText.textContent = text;
  }

  statusEl.className = isError ? 'status status-error' : 'status status-ready';
}

// file pick helpers
function bindFilePickers(){
  const btnA=$('#btnPickAbz'); const inpA=$('#fileAbz'); const nameA=$('#fileAbzName');
  const btnAnfin=$('#btnPickAnfin'); const inpAnfin=$('#fileAnfin'); const nameAnfin=$('#fileAnfinName');
  const btnImport = $('#btnImport');

  if(btnA && inpA && nameA){
    btnA.addEventListener('click', ()=> inpA.click());
    inpA.addEventListener('change', ()=>{
      const fn = (inpA.files && inpA.files[0]) ? inpA.files[0].name : '';
      nameA.dataset.fn = fn;
      nameA.textContent = fn || t('no_file');

      // Habilitar/desabilitar botão de importar baseado na seleção do arquivo ABZ
      if(btnImport) {
        btnImport.disabled = !fn;
      }
    });
  }

  // AN-FIN file picker (optional)
  if(btnAnfin && inpAnfin && nameAnfin){
    btnAnfin.addEventListener('click', ()=> inpAnfin.click());
    inpAnfin.addEventListener('change', ()=>{
      const fn = (inpAnfin.files && inpAnfin.files[0]) ? inpAnfin.files[0].name : '';
      nameAnfin.dataset.fn = fn;
      nameAnfin.textContent = fn || t('no_file_optional');
      console.log('[DEBUG] AN-FIN file selected:', fn || 'none');
    });
  }
}

function rowHtml(name, employeeData) {
  const services = employeeData.items || [];

  // Separate service items from additional/expenses
  // FIXED: Include items with unit_price even if quantity is 0 (for dual roles)
  const serviceItems = services.filter(s => s.unit_price !== undefined && s.unit_price !== null);
  const additionalItem = services.find(s => s.description === 'Brazilian Payroll Additional');
  const expensesItem = services.find(s => s.description === 'Expenses');

  // Get totals for Additional and Expenses to show in ALL service rows
  const additionalTotal = additionalItem ? (additionalItem.final || 0) : 0;
  const expensesTotal = expensesItem ? (expensesItem.final || 0) : 0;

  const badge = serviceItems.length > 1 ? `<span class="ml-2 inline-block text-xs rounded-full px-2 py-0.5 bg-blue-100 text-blue-700 border border-blue-300">${serviceItems.length} ${getCurrentLanguage()==='en'?'roles':'funções'}</span>` : '';

  let html = '';
  let rowIndex = 0;

  // If there are service items, show them with Additional and Expenses
  if (serviceItems.length > 0) {
    serviceItems.forEach((service, serviceIdx) => {
      const qty = service.quantity || 0;
      const unitPrice = service.unit_price || 0;
      const hasZeroQuantity = qty === 0 || qty === '0';

      // Highlight row if quantity is zero
      const rowStyle = hasZeroQuantity ? 'background-color: #fef2f2; border-left: 4px solid #ef4444;' : '';
      const qtyStyle = hasZeroQuantity ? 'color: #ef4444; font-weight: 600;' : '';
      const warningIcon = hasZeroQuantity ? '<span style="color: #ef4444; font-weight: bold;" title="⚠️ Quantidade zerada! Preencha o campo de override.">⚠️</span> ' : '';

      // Create unique IDs for cells that need to be updated
      const rowId = `row-${name.replace(/\s+/g, '-')}-${rowIndex}`;
      const unitPriceId = `unit-price-${rowId}`;
      const qtyId = `qty-${rowId}`;
      const totalServiceId = `total-service-${rowId}`;

      html += `
        <tr class="border-b" style="${rowStyle}">
          <td class="p-2 font-medium">${serviceIdx===0 ? (name + (badge||'')) : ''}</td>
          <td class="p-2">${warningIcon}${service.description||''}</td>
          <td class="p-2" id="${unitPriceId}">£${unitPrice.toFixed(2)}</td>
          <td class="p-2" style="${qtyStyle}" id="${qtyId}">${qty}${hasZeroQuantity ? ' ⚠️' : ''}</td>
          <td class="p-2" id="${totalServiceId}">£${(service.final||0).toFixed(2)}</td>
          <td class="p-2">£${additionalTotal.toFixed(2)}</td>
          <td class="p-2">£${expensesTotal.toFixed(2)}</td>
          <td class="p-2"><input class="border rounded px-2 py-1 w-20 ${hasZeroQuantity ? 'border-red-500 border-2' : ''}" data-k="quantity" data-name="${name}" data-line="${rowIndex}" data-unit-price-id="${unitPriceId}" data-qty-id="${qtyId}" data-total-id="${totalServiceId}" placeholder="${hasZeroQuantity ? 'PREENCHER!' : 'ex: 160'}" ${hasZeroQuantity ? 'style="background-color: #fee2e2;"' : ''} /></td>
          <td class="p-2"><input class="border rounded px-2 py-1 w-24" data-k="unit_price" data-name="${name}" data-line="${rowIndex}" data-unit-price-id="${unitPriceId}" data-qty-id="${qtyId}" data-total-id="${totalServiceId}" placeholder="ex: 300" /></td>
          <td class="p-2"><input class="border rounded px-2 py-1 w-24" data-k="additional" data-name="${name}" placeholder="ex: 200.50" ${serviceIdx===0 ? '' : 'disabled style="background-color: #f3f4f6;"'} /></td>
          <td class="p-2"><input class="border rounded px-2 py-1 w-24" data-k="expenses" data-name="${name}" placeholder="ex: 150.00" ${serviceIdx===0 ? '' : 'disabled style="background-color: #f3f4f6;"'} /></td>
          <td class="p-2"><input class="border rounded px-2 py-1 w-40" data-k="call_off" data-name="${name}" data-line="-1" placeholder="ex: P25-122 (por colaborador)" ${serviceIdx===0 ? '' : 'disabled style="background-color: #f3f4f6;"'} /></td>
        </tr>`;
      rowIndex++;
    });
  } else if (additionalTotal > 0 || expensesTotal > 0) {
    // No service items, but has Additional or Expenses - show a row for them with editable fields
    console.log(`[DEBUG] ⚠️  Employee ${name} has NO services, but has Additional (£${additionalTotal}) or Expenses (£${expensesTotal})`);

    // Calculate unit price from Additional + Expenses
    const totalAmount = additionalTotal + expensesTotal;
    const calculatedUnitPrice = totalAmount > 0 ? totalAmount : 0;

    // Create unique IDs for cells that need to be updated
    const rowId = `row-${name.replace(/\s+/g, '-')}-${rowIndex}`;
    const unitPriceId = `unit-price-${rowId}`;
    const qtyId = `qty-${rowId}`;
    const totalServiceId = `total-service-${rowId}`;

    html += `
      <tr class="border-b" style="background-color: #fffbeb;">
        <td class="p-2 font-medium">${name}</td>
        <td class="p-2 text-slate-500" style="font-style: italic;">No services (only Additional/Expenses)</td>
        <td class="p-2" id="${unitPriceId}">£${calculatedUnitPrice.toFixed(2)}</td>
        <td class="p-2" id="${qtyId}">-</td>
        <td class="p-2" id="${totalServiceId}">£0.00</td>
        <td class="p-2" style="font-weight: 600; color: #d97706;">£${additionalTotal.toFixed(2)}</td>
        <td class="p-2" style="font-weight: 600; color: #d97706;">£${expensesTotal.toFixed(2)}</td>
        <td class="p-2"><input class="border rounded px-2 py-1 w-20" data-k="quantity" data-name="${name}" data-line="${rowIndex}" data-unit-price-id="${unitPriceId}" data-qty-id="${qtyId}" data-total-id="${totalServiceId}" placeholder="ex: 160" /></td>
        <td class="p-2"><input class="border rounded px-2 py-1 w-24" data-k="unit_price" data-name="${name}" data-line="${rowIndex}" data-unit-price-id="${unitPriceId}" data-qty-id="${qtyId}" data-total-id="${totalServiceId}" placeholder="ex: 300" /></td>
        <td class="p-2"><input class="border rounded px-2 py-1 w-24" data-k="additional" data-name="${name}" placeholder="ex: 200.50" /></td>
        <td class="p-2"><input class="border rounded px-2 py-1 w-24" data-k="expenses" data-name="${name}" placeholder="ex: 150.00" /></td>
        <td class="p-2"><input class="border rounded px-2 py-1 w-40" data-k="call_off" data-name="${name}" data-line="-1" placeholder="ex: P25-122 (por colaborador)" /></td>
      </tr>`;
  } else {
    // No services, no Additional, no Expenses - show empty row with editable fields to allow manual entry
    console.log(`[DEBUG] ⚠️  Employee ${name} has NO data at all - showing editable row`);
    html += `
      <tr class="border-b" style="background-color: #fef2f2;">
        <td class="p-2 font-medium">${name}</td>
        <td class="p-2 text-slate-500" style="font-style: italic;">No data (add manually)</td>
        <td class="p-2">-</td>
        <td class="p-2">-</td>
        <td class="p-2">£0.00</td>
        <td class="p-2">£0.00</td>
        <td class="p-2">£0.00</td>
        <td class="p-2"><input class="border rounded px-2 py-1 w-20" data-k="quantity" data-name="${name}" data-line="${rowIndex}" placeholder="ex: 160" /></td>
        <td class="p-2"><input class="border rounded px-2 py-1 w-24" data-k="unit_price" data-name="${name}" data-line="${rowIndex}" placeholder="ex: 300" /></td>
        <td class="p-2"><input class="border rounded px-2 py-1 w-24" data-k="additional" data-name="${name}" placeholder="ex: 200.50" /></td>
        <td class="p-2"><input class="border rounded px-2 py-1 w-24" data-k="expenses" data-name="${name}" placeholder="ex: 150.00" /></td>
        <td class="p-2"><input class="border rounded px-2 py-1 w-40" data-k="call_off" data-name="${name}" data-line="-1" placeholder="ex: P25-122 (por colaborador)" /></td>
      </tr>`;
  }

  return html;
}

// CORREÇÃO: Função para forçar limpeza completa
function forceCleanData() {
  console.log('[DEBUG] Forçando limpeza completa de dados antigos');

  // Limpar variáveis globais
  SESSION_ID = null;
  PREVIEW = {};

  // Limpar interface
  const tbody = $('#tbody');
  tbody.innerHTML = '';

  // Limpar localStorage se existir
  if (typeof(Storage) !== "undefined") {
    localStorage.removeItem('session_id');
    localStorage.removeItem('preview_data');
  }

  console.log('[DEBUG] Limpeza completa realizada');
}

async function doImport() {
  const f1 = $('#fileAbz').files[0];
  if (!f1) { alert(t('select_file_error')); return; }

  const f2 = $('#fileAnfin').files[0];  // AN-FIN file (optional)

  console.log('[DEBUG] Starting import process');
  console.log('[DEBUG] ABZ file selected:', f1.name, 'Size:', f1.size, 'bytes');
  if (f2) {
    console.log('[DEBUG] AN-FIN file selected:', f2.name, 'Size:', f2.size, 'bytes');
  } else {
    console.log('[DEBUG] No AN-FIN file selected - expenses will be £0.00');
  }

  // CORREÇÃO: Forçar limpeza antes de importar
  forceCleanData();

  setStatus(t('importing'));
  const fd = new FormData();
  fd.append('abz', f1);
  if (f2) {
    fd.append('anfin', f2);  // Add AN-FIN file if selected
  }

  console.log('[DEBUG] Sending request to /api/import');
  const token = getAuthToken();
  const r = await fetch('/api/import', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: fd
  });

  console.log('[DEBUG] Response status:', r.status, r.statusText);

  if (!r.ok) {
    console.error('[DEBUG] Import failed with status:', r.status);
    setStatus(t('import_failed'));

    // Check if it's an authentication error
    if (r.status === 401) {
      alert(t('session_expired') || 'Session expired. Please login again.');
      window.location.href = '/ui/login.html';
      return;
    }

    // Try to get detailed error message from server
    try {
      const errorData = await r.json();
      if (errorData.detail) {
        alert(`${t('import_error')}\n\n${errorData.detail}`);
      } else {
        alert(t('import_error'));
      }
    } catch (e) {
      alert(t('import_error'));
    }
    return;
  }

  const data = await r.json();
  console.log('[DEBUG] Import response data:', data);

  SESSION_ID = data.session_id;
  console.log('[DEBUG] SESSION_ID set to:', SESSION_ID);

  const sessionEl = $('#sessionId');
  if (sessionEl) sessionEl.textContent = SESSION_ID;
  setStatus(t('imported_success'));

  console.log('[DEBUG] Import completed successfully');

  // Carregar preview automaticamente após o upload
  console.log('[DEBUG] Auto-loading preview after successful import');
  setTimeout(() => {
    loadPreview();
  }, 500); // Pequeno delay para garantir que tudo foi processado
}

async function loadPreview() {
  console.log('[DEBUG] loadPreview called');
  console.log('[DEBUG] Current SESSION_ID:', SESSION_ID);

  // Se não há sessão, mostrar mensagem para fazer upload
  if (!SESSION_ID) {
    console.log('[DEBUG] No SESSION_ID found, showing upload message');
    showUploadMessage();
    return;
  }

  console.log('[DEBUG] Loading preview for session:', SESSION_ID);
  setStatus(t('loading_preview'));

  const token = getAuthToken();
  const r = await fetch(`/api/preview?session_id=${SESSION_ID}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  console.log('[DEBUG] Preview response status:', r.status, r.statusText);

  // Check for authentication errors
  if (r.status === 401) {
    alert(t('session_expired') || 'Session expired. Please login again.');
    window.location.href = '/ui/login.html';
    return;
  }

  if (!r.ok) {
    console.error('[DEBUG] Failed to load preview:', r.status, r.statusText);
    alert('Erro ao carregar preview: ' + r.statusText);
    return;
  }

  const data = await r.json();
  console.log('[DEBUG] Preview data received:', data);

  PREVIEW = data.preview;
  console.log('[DEBUG] PREVIEW set to:', PREVIEW);
  console.log('[DEBUG] Number of employees in preview:', Object.keys(PREVIEW).length);

  // CORREÇÃO: Log detalhado para detectar Expenses
  Object.entries(PREVIEW).forEach(([name, employeeData]) => {
    const items = employeeData.items || [];
    items.forEach(item => {
      if (item.description && item.description.toLowerCase().includes('expense')) {
        console.warn(`[DEBUG] ❌ EXPENSES ENCONTRADO: ${name} - ${item.description} = £${item.final}`);
      }
    });
  });

  const tbody = $('#tbody');
  tbody.innerHTML = '';

  console.log('[DEBUG] ========================================');
  console.log('[DEBUG] RENDERING PREVIEW TABLE');
  console.log('[DEBUG] Total employees:', Object.keys(PREVIEW).length);
  console.log('[DEBUG] ========================================');

  // Check for employees with zero quantity
  let employeesWithZeroQty = [];
  Object.entries(PREVIEW).forEach(([name, employeeData]) => {
    const items = employeeData.items || [];
    const serviceItems = items.filter(s => s.unit_price && s.quantity !== undefined);
    serviceItems.forEach(service => {
      if (service.quantity === 0 || service.quantity === '0') {
        employeesWithZeroQty.push(name);
      }
    });
  });

  Object.entries(PREVIEW).forEach(([name, employeeData]) => {
    console.log('[DEBUG] Processing employee:', name);
    const items = employeeData.items || [];
    console.log('[DEBUG]   Items:', items.length);
    items.forEach(item => {
      console.log('[DEBUG]     -', item.description, ':', item.final);
    });

    const html = rowHtml(name, employeeData);
    console.log('[DEBUG]   Generated HTML length:', html.length);
    if (html.length === 0) {
      console.warn('[DEBUG]   ⚠️  NO HTML GENERATED FOR:', name);
    }
    tbody.insertAdjacentHTML('beforeend', html);
  });

  console.log('[DEBUG] ========================================');
  console.log('[DEBUG] TABLE RENDERING COMPLETE');
  console.log('[DEBUG] Total rows in table:', tbody.querySelectorAll('tr').length);
  console.log('[DEBUG] ========================================');

  // Setup real-time update listeners for override inputs
  setupOverrideListeners();

  // Show warning if there are employees with zero quantity
  if (employeesWithZeroQty.length > 0) {
    const uniqueEmployees = [...new Set(employeesWithZeroQty)];
    const warningMsg = getCurrentLanguage() === 'en'
      ? `⚠️ Warning: ${uniqueEmployees.length} employee(s) have zero quantity. Please fill in the override fields.`
      : `⚠️ Atenção: ${uniqueEmployees.length} colaborador(es) com quantidade zerada. Preencha os campos de sobrescrever.`;

    setStatus(warningMsg);

    // Show alert with employee names
    const employeeList = uniqueEmployees.join(', ');
    const alertMsg = getCurrentLanguage() === 'en'
      ? `⚠️ The following employees have ZERO quantity:\n\n${employeeList}\n\nPlease fill in the "Override" fields (Quantity column) before generating invoices.`
      : `⚠️ Os seguintes colaboradores têm quantidade ZERADA:\n\n${employeeList}\n\nPor favor, preencha os campos de "Sobrescrever" (coluna Quantidade) antes de gerar as invoices.`;

    setTimeout(() => alert(alertMsg), 500);
  } else {
    setStatus(t('preview_ready'));
  }
}

// Setup real-time update listeners for override inputs
function setupOverrideListeners() {
  console.log('[DEBUG] Setting up real-time update listeners');

  // Get all quantity and unit_price inputs
  const quantityInputs = document.querySelectorAll('input[data-k="quantity"]');
  const unitPriceInputs = document.querySelectorAll('input[data-k="unit_price"]');

  console.log('[DEBUG] Found', quantityInputs.length, 'quantity inputs');
  console.log('[DEBUG] Found', unitPriceInputs.length, 'unit_price inputs');

  // Add event listeners to quantity inputs
  quantityInputs.forEach(input => {
    input.addEventListener('input', function() {
      updateRowValues(this);
    });
  });

  // Add event listeners to unit_price inputs
  unitPriceInputs.forEach(input => {
    input.addEventListener('input', function() {
      updateRowValues(this);
    });
  });
}

// Update row values in real-time
function updateRowValues(input) {
  const unitPriceId = input.dataset.unitPriceId;
  const qtyId = input.dataset.qtyId;
  const totalId = input.dataset.totalId;

  // If this input doesn't have the required data attributes, skip
  if (!unitPriceId || !qtyId || !totalId) {
    return;
  }

  // Get the row's inputs
  const name = input.dataset.name;
  const line = input.dataset.line;
  const quantityInput = document.querySelector(`input[data-k="quantity"][data-name="${name}"][data-line="${line}"]`);
  const unitPriceInput = document.querySelector(`input[data-k="unit_price"][data-name="${name}"][data-line="${line}"]`);

  if (!quantityInput || !unitPriceInput) {
    return;
  }

  // Get the displayed cells
  const unitPriceCell = document.getElementById(unitPriceId);
  const qtyCell = document.getElementById(qtyId);
  const totalCell = document.getElementById(totalId);

  // Get original values from the cells (removing £ and parsing)
  let originalUnitPrice = 0;
  let originalQty = 0;

  if (unitPriceCell) {
    const cellText = unitPriceCell.textContent.replace('£', '').trim();
    originalUnitPrice = parseFloat(cellText) || 0;
  }

  if (qtyCell) {
    const cellText = qtyCell.textContent.replace('⚠️', '').trim();
    if (cellText !== '-') {
      originalQty = parseFloat(cellText) || 0;
    }
  }

  // Get override values (if filled)
  const overrideQuantity = quantityInput.value.trim();
  const overrideUnitPrice = unitPriceInput.value.trim();

  // Determine final values to use
  const finalQuantity = overrideQuantity ? parseFloat(overrideQuantity) : originalQty;
  const finalUnitPrice = overrideUnitPrice ? parseFloat(overrideUnitPrice) : originalUnitPrice;

  // Update the displayed cells with final values
  if (unitPriceCell) {
    unitPriceCell.textContent = `£${finalUnitPrice.toFixed(2)}`;
  }

  if (qtyCell) {
    if (finalQuantity > 0) {
      qtyCell.textContent = finalQuantity.toString();
      // Remove warning styling if quantity is filled
      qtyCell.style.color = '';
      qtyCell.style.fontWeight = '';
    } else {
      qtyCell.textContent = '-';
    }
  }

  if (totalCell) {
    const total = finalQuantity * finalUnitPrice;
    totalCell.textContent = `£${total.toFixed(2)}`;
  }

  console.log('[DEBUG] Updated row values:', {
    name,
    line,
    originalQty,
    originalUnitPrice,
    overrideQuantity,
    overrideUnitPrice,
    finalQuantity,
    finalUnitPrice,
    total: finalQuantity * finalUnitPrice
  });
}

function showUploadMessage() {
  console.log('[DEBUG] Showing upload message - no session active');

  // Limpar preview
  PREVIEW = null;
  const tbody = $('#tbody');
  tbody.innerHTML = '';

  // Mostrar mensagem para fazer upload
  setStatus('📁 Faça upload de um arquivo ABZ para visualizar os dados');



  // Adicionar uma linha na tabela explicando que é necessário fazer upload
  tbody.innerHTML = `
    <tr>
      <td colspan="10" style="text-align: center; padding: 2rem; color: #666; font-style: italic;">
        <div style="display: flex; flex-direction: column; align-items: center; gap: 1rem;">
          <span class="material-icons" style="font-size: 3rem; color: #ccc;">upload_file</span>
          <div>
            <strong>Nenhum arquivo carregado</strong><br>
            Faça upload de um arquivo ABZ acima para visualizar os dados dos funcionários
          </div>
        </div>
      </td>
    </tr>
  `;
}

function collectOverrides() {
  const map = {};
  document.querySelectorAll('input[data-k]').forEach(inp => {
    const k = inp.dataset.k;
    const name = inp.dataset.name;
    const line = parseInt(inp.dataset.line, 10);
    const val = inp.value.trim();
    if (!val) return;
    if (!map[name]) map[name] = {};

    // Handle per-employee overrides (call_off, additional, expenses)
    if (k === 'call_off') {
      map[name].call_off = val;
    } else if (k === 'additional') {
      map[name].additional = parseFloat(val);
    } else if (k === 'expenses') {
      map[name].expenses = parseFloat(val);
    } else {
      // Handle per-line overrides (quantity, unit_price)
      if (!map[name].overrides) map[name].overrides = {};
      if (!map[name].overrides[line]) map[name].overrides[line] = {};
      map[name].overrides[line][k] = k === 'quantity' ? parseInt(val, 10) : parseFloat(val);
    }
  });

  // Debug log to verify overrides collection
  console.log('[DEBUG] Collected overrides:', JSON.stringify(map, null, 2));

  return map;
}

let _pollTimer = null;
async function pollProgress() {
  const box = $('#progress');
  box.classList.remove('hidden');
  const update = async () => {
    if (!SESSION_ID) return;
    try {
      const token = getAuthToken();
      const r = await fetch(`/api/progress?session_id=${SESSION_ID}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (!r.ok) return;
      const p = await r.json();
      const pct = (p.percent ?? 0);
      let stage = p.stage || '';
      if (getCurrentLanguage()==='en') {
        const stageMap = {
          'Preparando dados': 'Preparing data',
          'Gerando Excel': 'Generating Excel',
          'Gerando PDF': 'Generating PDF',
          'Finalizando': 'Finalizing'
        };
        stage = stageMap[stage] || stage;
      }
      const cur = p.current ?? 0, tot = p.total ?? 0;
      const warn = Array.isArray(p.warnings) && p.warnings.length ? ('\n' + t('warningsLabel') + '\n- ' + p.warnings.join('\n- ')) : '';

      // Update progress bar
      const progressFill = $('#progressFill');
      const progressText = $('#progressText');

      if (progressFill) {
        progressFill.style.width = `${pct}%`;
      }

      if (progressText) {
        progressText.textContent = `${stage} (${cur}/${tot}) - ${pct.toFixed(1)}%${warn}`;
      }

      if (pct >= 100) {
        clearInterval(_pollTimer);
        _pollTimer = null;
      }
    } catch {}
  };
  _pollTimer = setInterval(update, 1000);
  update();
}

async function generate() {
  if (!SESSION_ID) { alert(t('need_preview_first')); return; }
  setStatus(t('generating'));
  const rawDate = $('#invoiceDate').value;
  const body = {
    session_id: SESSION_ID,
    invoice_date: toDDMMYYYY(rawDate) || null,
    invoice_no: ($('#invoiceNo').value || '').trim() || null,
    call_off: ($('#callOff').value || '').trim() || null,
    overrides: collectOverrides()
  };

  try {
    // Start asynchronous generation
    const token = getAuthToken();
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(body)
    });

    if (!response.ok) {
      // Check for authentication errors
      if (response.status === 401) {
        alert(t('session_expired') || 'Session expired. Please login again.');
        window.location.href = '/ui/login.html';
        return;
      }

      let msg = `HTTP ${response.status}`;
      try {
        const err = await response.json();
        if (err && (err.detail || err.message)) {
          msg += `: ${err.detail || err.message}`;
        }
      } catch {}
      throw new Error(msg);
    }

    const startData = await response.json();
    console.log('Generation started:', startData);

    // Start polling progress immediately
    pollProgress();

    // Show message that generation is running in background
    const backgroundMsg = typeof t === 'function' ? t('generation_started_background') : 'Generation started in background. You can navigate to other pages.';
    setStatus(backgroundMsg);

    // Wait for completion by polling
    await waitForCompletion();

  } catch (error) {
    console.error('Error starting generation:', error);
    const errorMsg = typeof t === 'function' ? t('generation_failed') : 'Generation failed';
    setStatus(errorMsg, true);
    const alertMsg = typeof t === 'function' ? t('generation_error') : 'Generation error';
    alert(alertMsg + ': ' + error.message);
  }
}

async function waitForCompletion() {
  return new Promise((resolve, reject) => {
    const checkCompletion = async () => {
      try {
        const token = getAuthToken();
        const response = await fetch(`/api/progress?session_id=${SESSION_ID}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        if (!response.ok) {
          reject(new Error('Failed to check progress'));
          return;
        }

        const progress = await response.json();

        if (progress.percent >= 100) {
          // Generation completed, load results
          await loadGenerationResults();
          resolve();
        } else {
          // Continue checking
          setTimeout(checkCompletion, 2000);
        }
      } catch (error) {
        reject(error);
      }
    };

    checkCompletion();
  });
}

async function loadGenerationResults() {
  try {
    // Load the generated files from the session
    const token = getAuthToken();
    const response = await fetch(`/api/session/${SESSION_ID}/files`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    // Check for authentication errors
    if (response.status === 401) {
      alert(t('session_expired') || 'Session expired. Please login again.');
      window.location.href = '/ui/login.html';
      return;
    }

    if (!response.ok) {
      // Fallback: try to get results from progress endpoint
      const progressResponse = await fetch(`/api/progress?session_id=${SESSION_ID}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (progressResponse.ok) {
        const progressData = await progressResponse.json();
        if (progressData.files) {
          displayResults({ files: progressData.files, session_id: SESSION_ID });
          return;
        }
      }
      throw new Error('Failed to load results');
    }

    const data = await response.json();
    displayResults(data);

  } catch (error) {
    console.error('Error loading generation results:', error);
    const errorMsg = typeof t === 'function' ? t('failed_to_load_results') : 'Failed to load results';
    setStatus(errorMsg, true);
  }
}

function displayResults(data) {
  const box = $('#result');
  box.innerHTML = '';
  (data.files||[]).forEach(f => {
    const aX = f.url_xlsx ? `<a class="text-blue-700 underline" href="javascript:void(0)" onclick="downloadSessionFile('${f.url_xlsx}', '${f.name}.xlsx')">XLSX</a>` : '';
    const aP = f.url_pdf ? `<a class="text-blue-700 underline ml-2" href="javascript:void(0)" onclick="openSessionPDF('${f.url_pdf}')">PDF</a>` : `<span class="text-slate-500 ml-2">${t('pdfPending')}</span>`;
    box.insertAdjacentHTML('beforeend', `<div>• ${f.name}: ${aX} ${aP}</div>`);
  });

  if (data.session_id) {
    const base = `/api/session/${data.session_id}`;
    const l1 = $('#lnkZipPdf');
    const l2 = $('#lnkZipAll');
    const files = data.files || [];
    const hasPdf = files.some(f => !!f.url_pdf);
    const hasXlsx = files.some(f => !!f.url_xlsx);

    // PDF ZIP only if any PDF exists
    if (hasPdf) {
      l1.href = 'javascript:void(0)';
      l1.onclick = () => downloadSessionFile(`${base}/zip?kind=pdf`, `session_${data.session_id}_pdf.zip`);
      l1.classList.remove('hidden');
      // Update only the text span, preserve the icon
      const textSpan1 = l1.querySelector('span:last-child');
      if (textSpan1) textSpan1.textContent = t('download_pdf');
    } else {
      l1.classList.add('hidden');
      l1.removeAttribute('href');
    }

    // ALL ZIP shown if any file exists (xlsx or pdf)
    if (hasPdf || hasXlsx) {
      l2.href = 'javascript:void(0)';
      l2.onclick = () => downloadSessionFile(`${base}/zip?kind=all`, `session_${data.session_id}_all.zip`);
      l2.classList.remove('hidden');
      // Update only the text span, preserve the icon
      const textSpan2 = l2.querySelector('span:last-child');
      if (textSpan2) textSpan2.textContent = t('download_all');
    } else {
      l2.classList.add('hidden');
      l2.removeAttribute('href');
    }
  }

  const successMsg = (data.warnings && data.warnings.length) ?
    `${t('generated_warnings')}: ${data.warnings.join(' | ')}` :
    t('generated_success');
  setStatus(successMsg);

  // atualiza sugestão do próximo número após gerar
  loadSeqAndHint();

  // esconde progresso após terminar
  const pbox = $('#progress');
  const progressFill = $('#progressFill');
  const progressText = $('#progressText');

  pbox.classList.add('hidden');
  if (progressFill) progressFill.style.width = '0%';
  if (progressText) progressText.textContent = '';
  pbox.textContent='';
}

// Check authentication before loading page
function checkAuth() {
  const token = getAuthToken();
  if (!token) {
    console.log('No auth token found, redirecting to login');
    window.location.href = '/ui/login.html';
    return false;
  }
  return true;
}

// Initialize when DOM is ready
function initializeApp() {
  try {
    // Check authentication first
    if (!checkAuth()) {
      return;
    }

    // Bind event listeners
    const btnImport = $('#btnImport');
    const btnPreview = $('#btnPreview');
    const btnGenerate = $('#btnGenerate');

    if (btnImport) {
      btnImport.addEventListener('click', doImport);
      console.log('btnImport listener added');
    } else {
      console.error('btnImport not found');
    }

    if (btnPreview) {
      btnPreview.addEventListener('click', loadPreview);
      console.log('btnPreview listener added');
    } else {
      console.error('btnPreview not found');
    }

    if (btnGenerate) {
      btnGenerate.addEventListener('click', generate);
      console.log('btnGenerate listener added');
    } else {
      console.error('btnGenerate not found');
    }

    // default today in date picker and show next invoice no suggestion
    const _idEl = document.querySelector('#invoiceDate');
    if(_idEl && _idEl.type==='date'){
      try{
        _idEl.valueAsDate = new Date();
        console.log('Date set successfully');
      } catch(e) {
        console.error('Error setting date:', e);
      }
    }

    // Load invoice sequence
    if (typeof loadSeqAndHint === 'function') {
      loadSeqAndHint();
      console.log('loadSeqAndHint called');
    }

    // inicializa seletores de arquivo e idioma
    bindFilePickers();
    setupInvoiceNumberListener();

    console.log('App initialized successfully');
  } catch (error) {
    console.error('Error initializing app:', error);
  }
}

// Download session file with authentication
async function downloadSessionFile(url, filename) {
  try {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      alert(t('session_expired') || 'Session expired. Please login again.');
      window.location.href = '/ui/login.html';
      return;
    }

    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (response.status === 401) {
      alert(t('session_expired') || 'Session expired. Please login again.');
      window.location.href = '/ui/login.html';
      return;
    }

    if (!response.ok) {
      throw new Error('Download failed');
    }

    // Get the blob
    const blob = await response.blob();

    // Create download link
    const downloadUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();

    // Cleanup
    window.URL.revokeObjectURL(downloadUrl);
    document.body.removeChild(a);
  } catch (error) {
    console.error('Download error:', error);
    alert(t('download_failed') || 'Failed to download file');
  }
}

// Open session PDF in new tab with authentication
async function openSessionPDF(url) {
  console.log('🔍 openSessionPDF called with URL:', url);
  try {
    const token = localStorage.getItem('auth_token');
    console.log('🔍 Token exists:', !!token);

    if (!token) {
      alert(t('session_expired') || 'Session expired. Please login again.');
      window.location.href = '/ui/login.html';
      return;
    }

    console.log('🔍 Fetching PDF from:', url);
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    console.log('🔍 Response status:', response.status);

    if (response.status === 401) {
      alert(t('session_expired') || 'Session expired. Please login again.');
      window.location.href = '/ui/login.html';
      return;
    }

    if (!response.ok) {
      throw new Error('Failed to load PDF');
    }

    // Get the blob
    const blob = await response.blob();
    console.log('🔍 Blob size:', blob.size);

    // Create object URL and open in new tab
    const pdfUrl = window.URL.createObjectURL(blob);
    console.log('🔍 Opening PDF in new tab');
    window.open(pdfUrl, '_blank');
  } catch (error) {
    console.error('❌ PDF open error:', error);
    alert(t('pdf_open_failed') || 'Failed to open PDF');
  }
}

// Wait for DOM and i18n to be ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeApp);
} else {
  // DOM is already ready
  initializeApp();
}