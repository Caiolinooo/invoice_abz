const $ = (sel) => document.querySelector(sel);
const statusEl = $('#status');
let SESSION_ID = null;
let PREVIEW = null;

// i18n
const I18N = {
  'pt-BR': {
    title: 'Conversor Invoice', ready: 'Pronto',
    hImport: '1) Importar Arquivos', lblAbz: 'ABZ - Charge Rate.xlsx', lblAnfin: 'AN-FIN - Medição.xlsx', lblSession: 'Sessão:', btnImport: 'Importar',
    btnPick: 'Selecionar arquivo', noFile: 'Nenhum arquivo', datePlaceholder: 'dd/mm/aaaa',
    hPreview: '2) Preview e Ajustes', btnPreview: 'Carregar Preview',
    thColab: 'Colaborador', thServiceDesc: 'Descrição Serviço', thUnitPrice: 'Unit Price', thQty: 'Qty', thTotalServ: 'Total Serviço', thAdditional: 'Additional', thExpenses: 'Expenses', thOverrideQty: 'Override Qty', thOverrideUnit: 'Override Unit',
    hGenerate: '3) Gerar Invoices', lblInvoiceDate: 'Invoice Date', lblInvoiceNo: 'Invoice No', lblCallOff: 'Call-Off', btnGenerate: 'Gerar Invoices',
    zipPdf: 'Baixar ZIP (PDFs)', zipAll: 'Baixar ZIP (Tudo)',
    errSelectTwo: 'Selecione os 2 arquivos XLSX', importing: 'Importando...', importFail: 'Falha ao importar', importError: 'Erro no import', imported: 'Importado. Clique em Preview.',
    loadingPreview: 'Carregando preview...', previewReady: 'Preview pronto. Faça ajustes se necessário.',
    needImportFirst: 'Importe os arquivos primeiro', needPreviewFirst: 'Importe e faça o preview primeiro',
    generating: 'Gerando invoices...', generatedOk: 'Invoices geradas.', generatedWithWarnings: 'Gerado com avisos',
    pdfPending: 'PDF pendente', warningsLabel: 'Avisos:'
  },
  'en': {
    title: 'Invoice Converter', ready: 'Ready',
    hImport: '1) Import Files', lblAbz: 'ABZ - Charge Rate.xlsx', lblAnfin: 'AN-FIN - Measurement.xlsx', lblSession: 'Session:', btnImport: 'Import',
    btnPick: 'Select file', noFile: 'No file', datePlaceholder: 'dd/mm/yyyy',
    hPreview: '2) Preview and Adjustments', btnPreview: 'Load Preview',
    thColab: 'Employee', thServiceDesc: 'Service Description', thUnitPrice: 'Unit Price', thQty: 'Qty', thTotalServ: 'Service Total', thAdditional: 'Additional', thExpenses: 'Expenses', thOverrideQty: 'Override Qty', thOverrideUnit: 'Override Unit',
    hGenerate: '3) Generate Invoices', lblInvoiceDate: 'Invoice Date', lblInvoiceNo: 'Invoice No', lblCallOff: 'Call-Off', btnGenerate: 'Generate Invoices',
    zipPdf: 'Download ZIP (PDFs)', zipAll: 'Download ZIP (All)',
    errSelectTwo: 'Select both XLSX files', importing: 'Importing...', importFail: 'Import failed', importError: 'Import error', imported: 'Imported. Click Preview.',
    loadingPreview: 'Loading preview...', previewReady: 'Preview ready. Adjust if necessary.',
    needImportFirst: 'Import the files first', needPreviewFirst: 'Import and load preview first',
    generating: 'Generating invoices...', generatedOk: 'Invoices generated.', generatedWithWarnings: 'Generated with warnings',
    pdfPending: 'PDF pending', warningsLabel: 'Warnings:'
  }
};
function getLang(){ return localStorage.getItem('lang') || 'pt-BR'; }
function t(k){ const lang = getLang(); return (I18N[lang] && I18N[lang][k]) || (I18N['pt-BR'][k] || k); }
function applyI18n(){
  document.title = t('title');
  const set = (id,k)=>{ const el=$(id); if(el) el.textContent=t(k); };
  set('#appTitle','title'); set('#status','ready');
  set('#hImport','hImport'); set('#lblAbz','lblAbz'); set('#lblAnfin','lblAnfin'); set('#lblSession','lblSession');
  const bi=$('#btnImport'); if(bi) bi.textContent=t('btnImport');
  // file pick buttons + filenames
  const bpa=$('#btnPickAbz'); if(bpa) bpa.textContent=t('btnPick');
  const bpf=$('#btnPickAnfin'); if(bpf) bpf.textContent=t('btnPick');
  const fn1=$('#fileAbzName'); if(fn1) fn1.textContent=fn1.dataset.fn || t('noFile');
  const fn2=$('#fileAnfinName'); if(fn2) fn2.textContent=fn2.dataset.fn || t('noFile');

  set('#hPreview','hPreview'); const bp=$('#btnPreview'); if(bp) bp.textContent=t('btnPreview');
  set('#thColab','thColab'); set('#thServiceDesc','thServiceDesc'); set('#thUnitPrice','thUnitPrice'); set('#thQty','thQty'); set('#thTotalServ','thTotalServ'); set('#thAdditional','thAdditional'); set('#thExpenses','thExpenses'); set('#thOverrideQty','thOverrideQty'); set('#thOverrideUnit','thOverrideUnit');
  set('#hGenerate','hGenerate'); set('#lblInvoiceDate','lblInvoiceDate'); set('#lblInvoiceNo','lblInvoiceNo'); set('#lblCallOff','lblCallOff');
  const bg=$('#btnGenerate'); if(bg) bg.textContent=t('btnGenerate');
  const l1=$('#lnkZipPdf'); if(l1){ l1.textContent=t('zipPdf'); }
  const l2=$('#lnkZipAll'); if(l2){ l2.textContent=t('zipAll'); }
  const sel=$('#langSel'); if(sel){ sel.value=getLang(); }
  const idate=$('#invoiceDate'); if(idate){ idate.placeholder=t('datePlaceholder'); }
}
$('#langSel')?.addEventListener('change', (e)=>{ localStorage.setItem('lang', e.target.value); applyI18n(); });

function setStatus(txt) { statusEl.textContent = txt; }
// file pick helpers
function bindFilePickers(){
  const btnA=$('#btnPickAbz'); const inpA=$('#fileAbz'); const nameA=$('#fileAbzName');
  if(btnA && inpA && nameA){
    btnA.addEventListener('click', ()=> inpA.click());
    inpA.addEventListener('change', ()=>{
      const fn = (inpA.files && inpA.files[0]) ? inpA.files[0].name : '';
      nameA.dataset.fn = fn;
      nameA.textContent = fn || t('noFile');
    });
  }
  const btnF=$('#btnPickAnfin'); const inpF=$('#fileAnfin'); const nameF=$('#fileAnfinName');
  if(btnF && inpF && nameF){
    btnF.addEventListener('click', ()=> inpF.click());
    inpF.addEventListener('change', ()=>{
      const fn = (inpF.files && inpF.files[0]) ? inpF.files[0].name : '';
      nameF.dataset.fn = fn;
      nameF.textContent = fn || t('noFile');
    });
  }
}


function rowHtml(name, items) {
  const service = items[0] || {};
  const add = (items.find(i => (i.description||'').toLowerCase().includes('additional')) || {}).final || 0;
  const exp = (items.find(i => (i.description||'').toLowerCase().includes('expenses')) || {}).final || 0;

  return `
    <tr class="border-b">
      <td class="p-2 font-medium">${name}</td>
      <td class="p-2">${service.description||''}</td>
      <td class="p-2 text-right">${service.unit_price??''}</td>
      <td class="p-2 text-right">${service.quantity??''}</td>
      <td class="p-2 text-right">${(service.final??'')}</td>
      <td class="p-2 text-right">${add}</td>
      <td class="p-2 text-right">${exp}</td>
      <td class="p-2"><input class="border rounded px-2 py-1 w-24" data-k="quantity" data-name="${name}" placeholder="ex: 0" /></td>
      <td class="p-2"><input class="border rounded px-2 py-1 w-24" data-k="unit_price" data-name="${name}" placeholder="ex: 300" /></td>
    </tr>
  `;
}

async function doImport() {
  const f1 = $('#fileAbz').files[0];
  const f2 = $('#fileAnfin').files[0];
  if (!f1 || !f2) { alert(t('errSelectTwo')); return; }
  setStatus(t('importing'));
  const fd = new FormData();
  fd.append('abz', f1);
  fd.append('anfin', f2);
  const r = await fetch('/api/import', { method: 'POST', body: fd });
  if (!r.ok) { setStatus(t('importFail')); alert(t('importError')); return; }
  const data = await r.json();
  SESSION_ID = data.session_id;
  $('#sessionId').textContent = SESSION_ID;
  setStatus(t('imported'));
}

async function loadPreview() {
  if (!SESSION_ID) { alert(t('needImportFirst')); return; }
  setStatus(t('loadingPreview'));
  const r = await fetch(`/api/preview?session_id=${SESSION_ID}`);
  const data = await r.json();
  PREVIEW = data.preview;
  const tbody = $('#tbody');
  tbody.innerHTML = '';
  Object.entries(PREVIEW).forEach(([name, v]) => {
    tbody.insertAdjacentHTML('beforeend', rowHtml(name, v.items||[]));
  });
  setStatus(t('previewReady'));
}

function collectOverrides() {
  const inputs = Array.from(document.querySelectorAll('input[data-name]'));
  const map = {};
  for (const el of inputs) {
    const name = el.dataset.name;
    const k = el.dataset.k;
    const val = el.value.trim();
    if (!val) continue;
    map[name] = map[name] || {};
    map[name][k] = parseFloat(val);
  }
  return map;
}

let _pollTimer = null;
async function pollProgress() {
  const box = $('#progress');
  box.classList.remove('hidden');
  const update = async () => {
    if (!SESSION_ID) return;
    try {
      const r = await fetch(`/api/progress?session_id=${SESSION_ID}`);
      if (!r.ok) return;
      const p = await r.json();
      const pct = (p.percent ?? 0);
      let stage = p.stage || '';
      if (getLang()==='en') {
        stage = stage
          .replace('Verificando LibreOffice', 'Checking LibreOffice')
          .replace('Instalando LibreOffice via winget (silencioso)', 'Installing LibreOffice via winget (silent)')
          .replace('Falha ao instalar via winget. Tentando via Chocolatey', 'Winget install failed. Trying Chocolatey')
          .replace('Falha ao instalar via Chocolatey.', 'Chocolatey install failed.')
          .replace('LibreOffice disponvel', 'LibreOffice available')
          .replace('LibreOffice n e3o disponvel', 'LibreOffice not available')
          .replace('Iniciando gera e7 e3o', 'Starting generation')
          .replace('Convertendo PDF', 'Converting PDF')
          .replace('Conclu eddo', 'Finished')
          .replace('Gerando', 'Generating');
      }
      const cur = p.current ?? 0, tot = p.total ?? 0;
      const warn = Array.isArray(p.warnings) && p.warnings.length ? ('\n' + t('warningsLabel') + '\n- ' + p.warnings.join('\n- ')) : '';
      box.textContent = `${pct}% — ${stage}${cur&&tot?` (${cur}/${tot})`:''}${warn}`;
      if (p.done) {
        clearInterval(_pollTimer); _pollTimer = null;
      }
    } catch {}
  };
  await update();
  _pollTimer = setInterval(update, 1500);
}

async function generate() {
  if (!SESSION_ID) { alert(t('needPreviewFirst')); return; }
  setStatus(t('generating'));
  const body = {
    session_id: SESSION_ID,
    invoice_date: $('#invoiceDate').value || null,
    invoice_no: $('#invoiceNo').value || null,
    call_off: $('#callOff').value || null,
    overrides: collectOverrides()
  };
  // dispara a geração, mas não aguarda para já mostrar progresso
  const reqPromise = fetch('/api/generate/pdf', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  // inicia polling de progresso
  pollProgress();

  const r = await reqPromise;
  const data = await r.json();
  const box = $('#result');
  box.innerHTML = '';
  (data.files||[]).forEach(f => {
    const aX = f.url_xlsx ? `<a class="text-blue-700 underline" href="${f.url_xlsx}" target="_blank">XLSX</a>` : '';
    const aP = f.url_pdf ? `<a class="text-blue-700 underline ml-2" href="${f.url_pdf}" target="_blank">PDF</a>` : `<span class=\"text-slate-500 ml-2\">${t('pdfPending')}</span>`;
    box.insertAdjacentHTML('beforeend', `<div>• ${f.name}: ${aX} ${aP}</div>`);
  });
  if (data.session_id) {
    const base = `/api/session/${data.session_id}`;
    const l1 = $('#lnkZipPdf');
    l1.href = `${base}/zip?kind=pdf`; l1.classList.remove('hidden'); l1.textContent=t('zipPdf');
    const l2 = $('#lnkZipAll');
    l2.href = `${base}/zip?kind=all`; l2.classList.remove('hidden'); l2.textContent=t('zipAll');
  }
  setStatus((data.warnings && data.warnings.length) ? `${t('generatedWithWarnings')}: ${data.warnings.join(' | ')}` : t('generatedOk'));
  // esconde progresso após terminar
  const pbox = $('#progress'); pbox.classList.add('hidden'); pbox.textContent='';
}

$('#btnImport').addEventListener('click', doImport);
$('#btnPreview').addEventListener('click', loadPreview);
$('#btnGenerate').addEventListener('click', generate);

// inicializa seletores de arquivo e idioma
bindFilePickers();
applyI18n();
