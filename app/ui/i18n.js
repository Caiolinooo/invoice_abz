/**
 * Internationalization (i18n) System
 * Complete translations for Portuguese and English
 */

const translations = {
    'pt-BR': {
        // Common
        'loading': 'Carregando...',
        'error': 'Erro',
        'success': 'Sucesso',
        'warning': 'Aviso',
        'info': 'Informação',
        'save': 'Salvar',
        'cancel': 'Cancelar',
        'delete': 'Excluir',
        'edit': 'Editar',
        'view': 'Visualizar',
        'download': 'Baixar',
        'upload': 'Enviar',
        'search': 'Buscar',
        'filter': 'Filtrar',
        'clear': 'Limpar',
        'refresh': 'Atualizar',
        'reset': 'Redefinir',
        'apply': 'Aplicar',
        'close': 'Fechar',
        'back': 'Voltar',
        'next': 'Próximo',
        'previous': 'Anterior',
        'home': 'Início',
        'settings': 'Configurações',
        'history': 'Histórico',
        'help': 'Ajuda',
        'about': 'Sobre',
        'contact': 'Contato',
        'yes': 'Sim',
        'no': 'Não',
        
        // Header & Navigation
        'invoice_system': 'Sistema de Invoices',
        'api_docs': 'Documentação da API',
        'employee_hub': 'Portal do Funcionário',
        
        // Main Page
        'invoice_converter': 'Conversor de Invoice',
        'ready': 'Pronto',
        'processing': 'Processando',
        'import_file': '1) Importar Arquivo',
        'import_description': 'Faça upload do arquivo ABZ com dados de charge rate para iniciar o processo de geração de invoices.',
        'abz_file_label': 'ABZ - Charge Rate.xlsx',
        'abz_file_help': 'Planilha com dados de charge rate, incluindo Brazilian Payroll Additionals e Expenses',
        'select_file': 'Selecionar arquivo',
        'no_file': 'Nenhum arquivo',
        'import_action': 'Importar',
        'session_label': 'Sessão:',
        'preview_adjustments': '2) Preview e Ajustes',
        'preview_description': 'Visualize e ajuste os dados antes de gerar os invoices. Você pode modificar quantidades, valores unitários e call-offs.',
        'load_preview': 'Carregar Preview',
        'generate_invoices': '3) Gerar Invoices',
        'generate_description': 'Configure os dados finais e gere os invoices em formato Excel e PDF.',
        'invoice_date': 'Data do Invoice',
        'invoice_date_help': 'Data que aparecerá nos invoices gerados',
        'invoice_number': 'Número do Invoice',
        'invoice_number_help': 'Número base para os invoices (será incrementado automaticamente)',
        'call_off': 'Call-Off',
        'call_off_help': 'Referência do call-off para todos os invoices',
        'generate_action': 'Gerar Invoices',
        'generate_help': 'Clique para gerar todos os invoices com as configurações acima',
        'download_pdf': 'Baixar ZIP (PDF)',
        'download_all': 'Baixar ZIP (Tudo)',
        
        // Table Headers
        'employee': 'Colaborador',
        'service_description': 'Descrição do Serviço',
        'unit_price': 'Preço Unitário',
        'quantity': 'Quantidade',
        'service_total': 'Total do Serviço',
        'additional': 'Adicional',
        'expenses': 'Despesas',
        'override_qty': 'Sobrescrever Qtd',
        'override_unit': 'Sobrescrever Unitário',
        'override_calloff': 'Sobrescrever Call-Off',
        'invoice_number_short': 'Invoice #',
        'position': 'Cargo',
        'date': 'Data',
        'amount': 'Valor',
        'status': 'Status',
        'files': 'Arquivos',
        'actions': 'Ações',
        
        // History Page
        'invoice_history': 'Histórico de Invoices',
        'track_manage_invoices': 'Rastreie e gerencie todos os invoices gerados',
        'total_invoices': 'Total de Invoices',
        'total_revenue': 'Faturamento Total',
        'current_month': 'Mês Atual',
        'last_month': 'Último Mês',
        'total_amount_gbp': 'Valor Total (GBP)',
        'last_30_days': 'Últimos 30 Dias',
        'pending': 'Pendentes',
        'employee_name': 'Nome do Funcionário',
        'search_employee': 'Buscar por nome do funcionário',
        'invoice_preview': 'Preview da Invoice',
        'invoice_details': 'Detalhes da Invoice',
        'service_lines': 'Linhas de Serviço',
        'description': 'Descrição',
        'total': 'Total',
        'grand_total': 'TOTAL GERAL',
        'brazilian_payroll_additional': 'Adicional de Folha Brasileira',
        'file_not_available': 'Arquivo não disponível',
        'download_excel': 'Baixar Excel',
        'failed_load_invoice': 'Falha ao carregar detalhes da invoice',
        'regenerate_pdf': 'Regenerar PDF',
        'confirm_regenerate_pdf': 'Regenerar PDF para esta invoice?',
        'regenerating_pdf': 'Regenerando PDF...',
        'pdf_regenerated': 'PDF regenerado com sucesso!',
        'failed_regenerate_pdf': 'Falha ao regenerar PDF',
        'all_statuses': 'Todos os Status',
        'date_from': 'Data Inicial',
        'date_to': 'Data Final',
        'apply_filters': 'Aplicar Filtros',
        'clear': 'Limpar',
        'loading_invoices': 'Carregando invoices...',
        'no_invoices_found': 'Nenhum invoice encontrado',
        'view_excel': 'Ver Excel',
        'view_pdf': 'Ver PDF',
        'generation_started_background': 'Geração iniciada em segundo plano. Você pode navegar para outras páginas.',
        'generation_failed': 'Falha na geração',
        'generation_error': 'Erro na geração',
        'failed_to_load_results': 'Falha ao carregar resultados',
        'failed_load_statistics': 'Falha ao carregar estatísticas',
        'failed_load_invoices': 'Falha ao carregar invoices',

        // Login Page
        'invoice_system': 'Sistema de Invoices',
        'login_subtitle': 'Sistema de Gerenciamento de Invoices',
        'email': 'Email',
        'password': 'Senha',
        'email_placeholder': 'seu@email.com',
        'password_placeholder': '••••••••',
        'login_button': 'Entrar',
        'logging_in': 'Entrando...',
        'login_success': 'Login realizado com sucesso!',
        'login_failed': 'Falha no login',
        'login_footer': 'Apenas usuários com permissão de Gerente ou Admin podem acessar',
        'logout': 'Sair',

        // Settings Page
        'settings_title': 'Configurações',
        'configure_preferences': 'Configure as preferências do seu sistema de invoices',
        'general': 'Geral',
        'email': 'Email',
        'templates': 'Templates',
        'company_information': 'Informações da Empresa',
        'configure_company_details': 'Configure os detalhes da sua empresa que aparecem nos invoices',
        'company_name': 'Nome da Empresa',
        'company_name_help': 'Nome que aparece nos invoices',
        'default_currency': 'Moeda Padrão',
        'default_currency_help': 'Moeda padrão para novos invoices',
        'company_address': 'Endereço da Empresa',
        'company_address_help': 'Endereço completo que aparece nos invoices',

        // Database Management
        'database_management': 'Gerenciamento do Banco de Dados',
        'manage_database_reset': 'Gerencie seu banco de dados de invoices e redefina todos os dados',
        'danger_zone': 'Zona de Perigo',
        'danger_zone_warning': 'Esta ação irá deletar permanentemente todos os invoices, sessões e redefinir a sequência de numeração dos invoices. Esta ação não pode ser desfeita.',
        'password_required': 'Senha Obrigatória',
        'enter_password_confirm': 'Digite a senha do sistema para prosseguir',
        'reset_all_data': 'Redefinir Todos os Dados',
        'company_address_placeholder': 'Digite o endereço da sua empresa',
        'save_changes': 'Salvar Alterações',
        'email_configuration': 'Configuração de Email',
        'configure_smtp': 'Configure as configurações SMTP para envio automático de invoices',
        'smtp_server': 'Servidor SMTP',
        'smtp_server_help': 'Servidor SMTP do seu provedor de email',
        'smtp_port': 'Porta SMTP',
        'smtp_port_help': 'Geralmente 587 para TLS ou 465 para SSL',
        'username': 'Usuário',
        'username_help': 'Seu endereço de email',
        'password': 'Senha',
        'password_help': 'Sua senha de email ou senha de aplicativo',
        'auto_send_emails': 'Enviar invoices automaticamente por email',
        'auto_send_help': 'Quando habilitado, os invoices serão enviados automaticamente após a geração',
        'test_connection': 'Testar Conexão',
        'template_management': 'Gerenciamento de Templates',
        'manage_templates': 'Gerencie templates de invoice e opções de formatação',
        'loading_templates': 'Carregando templates...',
        'upload_template': 'Enviar Template',
        
        // Status
        'generated': 'Gerado',
        'sent': 'Enviado',
        'paid': 'Pago',
        'cancelled': 'Cancelado',
        
        // Messages
        'select_file_error': 'Selecione o arquivo XLSX',
        'importing': 'Importando...',
        'import_failed': 'Falha ao importar',
        'import_error': 'Erro na importação',
        'imported_success': 'Importado. Clique em Preview.',
        'loading_preview': 'Carregando preview...',
        'preview_ready': 'Preview pronto. Faça ajustes se necessário.',
        'need_import_first': 'Importe o arquivo primeiro',
        'need_preview_first': 'Importe e faça o preview primeiro',
        'generating': 'Gerando invoices...',
        'generated_success': 'Invoices gerados.',
        'generated_warnings': 'Gerado com avisos',
        'pdf_pending': 'PDF pendente',
        'warnings_label': 'Avisos:',
        'settings_saved': 'Configurações salvas com sucesso',
        'settings_error': 'Erro ao salvar configurações',
        'connection_test_success': 'Conexão testada com sucesso',
        'connection_test_error': 'Erro ao testar conexão',
        
        // Footer
        'footer_copyright': '© {year} ABZ Group. Todos os direitos reservados.',
        'system_version': 'Sistema de Conversão de Invoices v2.0.0',
        'employee_portal': 'Portal do Funcionário',
        
        // Time
        'year': new Date().getFullYear().toString()
    },
    
    'en': {
        // Common
        'loading': 'Loading...',
        'error': 'Error',
        'success': 'Success',
        'warning': 'Warning',
        'info': 'Information',
        'save': 'Save',
        'cancel': 'Cancel',
        'delete': 'Delete',
        'edit': 'Edit',
        'view': 'View',
        'download': 'Download',
        'upload': 'Upload',
        'search': 'Search',
        'filter': 'Filter',
        'clear': 'Clear',
        'refresh': 'Refresh',
        'reset': 'Reset',
        'apply': 'Apply',
        'close': 'Close',
        'back': 'Back',
        'next': 'Next',
        'previous': 'Previous',
        'home': 'Home',
        'settings': 'Settings',
        'history': 'History',
        'help': 'Help',
        'about': 'About',
        'contact': 'Contact',
        'yes': 'Yes',
        'no': 'No',
        
        // Header & Navigation
        'invoice_system': 'Invoice System',
        'api_docs': 'API Documentation',
        'employee_hub': 'Employee Hub',
        
        // Main Page
        'invoice_converter': 'Invoice Converter',
        'ready': 'Ready',
        'processing': 'Processing',
        'import_file': '1) Import File',
        'import_description': 'Upload the ABZ file with charge rate data to start the invoice generation process.',
        'abz_file_label': 'ABZ - Charge Rate.xlsx',
        'abz_file_help': 'Spreadsheet with charge rate data, including Brazilian Payroll Additionals and Expenses',
        'select_file': 'Select file',
        'no_file': 'No file',
        'import_action': 'Import',
        'session_label': 'Session:',
        'preview_adjustments': '2) Preview and Adjustments',
        'preview_description': 'Preview and adjust the data before generating invoices. You can modify quantities, unit prices, and call-offs.',
        'load_preview': 'Load Preview',
        'generate_invoices': '3) Generate Invoices',
        'generate_description': 'Configure final data and generate invoices in Excel and PDF format.',
        'invoice_date': 'Invoice Date',
        'invoice_date_help': 'Date that will appear on generated invoices',
        'invoice_number': 'Invoice Number',
        'invoice_number_help': 'Base number for invoices (will be incremented automatically)',
        'call_off': 'Call-Off',
        'call_off_help': 'Call-off reference for all invoices',
        'generate_action': 'Generate Invoices',
        'generate_help': 'Click to generate all invoices with the above settings',
        'download_pdf': 'Download ZIP (PDF)',
        'download_all': 'Download ZIP (All)',
        
        // Table Headers
        'employee': 'Employee',
        'service_description': 'Service Description',
        'unit_price': 'Unit Price',
        'quantity': 'Quantity',
        'service_total': 'Service Total',
        'additional': 'Additional',
        'expenses': 'Expenses',
        'override_qty': 'Override Qty',
        'override_unit': 'Override Unit',
        'override_calloff': 'Override Call-Off',
        'invoice_number_short': 'Invoice #',
        'position': 'Position',
        'date': 'Date',
        'amount': 'Amount',
        'status': 'Status',
        'files': 'Files',
        'actions': 'Actions',
        
        // History Page
        'invoice_history': 'Invoice History',
        'track_manage_invoices': 'Track and manage all generated invoices',
        'total_invoices': 'Total Invoices',
        'total_revenue': 'Total Revenue',
        'current_month': 'Current Month',
        'last_month': 'Last Month',
        'total_amount_gbp': 'Total Amount (GBP)',
        'last_30_days': 'Last 30 Days',
        'pending': 'Pending',
        'employee_name': 'Employee Name',
        'search_employee': 'Search by employee name',
        'all_statuses': 'All Statuses',
        'date_from': 'Date From',
        'date_to': 'Date To',
        'apply_filters': 'Apply Filters',
        'clear': 'Clear',
        'loading_invoices': 'Loading invoices...',
        'no_invoices_found': 'No invoices found',
        'view_excel': 'View Excel',
        'view_pdf': 'View PDF',
        'generation_started_background': 'Generation started in background. You can navigate to other pages.',
        'generation_failed': 'Generation failed',
        'invoice_preview': 'Invoice Preview',
        'invoice_details': 'Invoice Details',
        'service_lines': 'Service Lines',
        'description': 'Description',
        'total': 'Total',
        'grand_total': 'GRAND TOTAL',
        'brazilian_payroll_additional': 'Brazilian Payroll Additional',
        'file_not_available': 'File not available',
        'download_excel': 'Download Excel',
        'failed_load_invoice': 'Failed to load invoice details',
        'regenerate_pdf': 'Regenerate PDF',
        'confirm_regenerate_pdf': 'Regenerate PDF for this invoice?',
        'regenerating_pdf': 'Regenerating PDF...',
        'pdf_regenerated': 'PDF regenerated successfully!',
        'failed_regenerate_pdf': 'Failed to regenerate PDF',
        'generation_error': 'Generation error',
        'failed_to_load_results': 'Failed to load results',
        'failed_load_statistics': 'Failed to load statistics',
        'failed_load_invoices': 'Failed to load invoices',

        // Login Page
        'invoice_system': 'Invoice System',
        'login_subtitle': 'Invoice Management System',
        'email': 'Email',
        'password': 'Password',
        'email_placeholder': 'your@email.com',
        'password_placeholder': '••••••••',
        'login_button': 'Sign In',
        'logging_in': 'Signing in...',
        'login_success': 'Login successful!',
        'login_failed': 'Login failed',
        'login_footer': 'Only users with Manager or Admin permission can access',
        'logout': 'Logout',

        // Settings Page
        'settings_title': 'Settings',
        'configure_preferences': 'Configure your invoice system preferences',
        'general': 'General',
        'email': 'Email',
        'templates': 'Templates',
        'company_information': 'Company Information',
        'configure_company_details': 'Configure your company details that appear on invoices',
        'company_name': 'Company Name',
        'company_name_help': 'Name that appears on invoices',
        'default_currency': 'Default Currency',
        'default_currency_help': 'Default currency for new invoices',
        'company_address': 'Company Address',
        'company_address_help': 'Full address that appears on invoices',
        'company_address_placeholder': 'Enter your company address',
        'save_changes': 'Save Changes',
        'email_configuration': 'Email Configuration',
        'configure_smtp': 'Configure SMTP settings for automatic invoice sending',
        'smtp_server': 'SMTP Server',
        'smtp_server_help': 'Your email provider\'s SMTP server',
        'smtp_port': 'SMTP Port',
        'smtp_port_help': 'Usually 587 for TLS or 465 for SSL',
        'username': 'Username',
        'username_help': 'Your email address',
        'password': 'Password',
        'password_help': 'Your email password or app password',
        'auto_send_emails': 'Automatically send invoices via email',
        'auto_send_help': 'When enabled, invoices will be sent automatically after generation',
        'test_connection': 'Test Connection',
        'template_management': 'Template Management',
        'manage_templates': 'Manage invoice templates and formatting options',
        'loading_templates': 'Loading templates...',
        'upload_template': 'Upload Template',
        
        // Status
        'generated': 'Generated',
        'sent': 'Sent',
        'paid': 'Paid',
        'cancelled': 'Cancelled',
        
        // Messages
        'select_file_error': 'Select the XLSX file',
        'importing': 'Importing...',
        'import_failed': 'Import failed',
        'import_error': 'Import error',
        'imported_success': 'Imported. Click Preview.',
        'loading_preview': 'Loading preview...',
        'preview_ready': 'Preview ready. Make adjustments if necessary.',
        'need_import_first': 'Import the file first',
        'need_preview_first': 'Import and preview first',
        'generating': 'Generating invoices...',
        'generated_success': 'Invoices generated.',
        'generated_warnings': 'Generated with warnings',
        'pdf_pending': 'PDF pending',
        'warnings_label': 'Warnings:',
        'settings_saved': 'Settings saved successfully',
        'settings_error': 'Error saving settings',
        'connection_test_success': 'Connection tested successfully',
        'connection_test_error': 'Error testing connection',

        // Database Management
        'database_management': 'Database Management',
        'manage_database_reset': 'Manage your invoice database and reset all data',
        'danger_zone': 'Danger Zone',
        'danger_zone_warning': 'This action will permanently delete all invoices, sessions, and reset the invoice numbering sequence. This cannot be undone.',
        'password_required': 'Password Required',
        'enter_password_confirm': 'Enter the system password to proceed',
        'reset_all_data': 'Reset All Data',

        // Footer
        'footer_copyright': '© {year} ABZ Group. All rights reserved.',
        'system_version': 'Invoice Conversion System v2.0.0',
        'employee_portal': 'Employee Portal',
        
        // Time
        'year': new Date().getFullYear().toString()
    }
};

// Current language
let currentLanguage = localStorage.getItem('language') || 'pt-BR';

// Translation function
function t(key, params = {}) {
    let translation = translations[currentLanguage]?.[key] || translations['pt-BR']?.[key] || key;
    
    // Replace parameters
    Object.keys(params).forEach(param => {
        translation = translation.replace(`{${param}}`, params[param]);
    });
    
    return translation;
}

// Set language
function setLanguage(lang) {
    if (translations[lang]) {
        currentLanguage = lang;
        localStorage.setItem('language', lang);
        updatePageTexts();
        
        // Update language selector
        const langSelector = document.getElementById('langSel');
        if (langSelector) {
            langSelector.value = lang;
        }
    }
}

// Get current language
function getCurrentLanguage() {
    return currentLanguage;
}

// Update all texts on the page
function updatePageTexts() {
    // Update elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        const translation = t(key);
        
        if (element.tagName === 'INPUT' && (element.type === 'text' || element.type === 'email')) {
            element.placeholder = translation;
        } else {
            element.textContent = translation;
        }
    });
    
    // Update year in footer
    const yearElement = document.getElementById('year');
    if (yearElement) {
        yearElement.textContent = new Date().getFullYear();
    }
    
    // Update footer copyright
    const footerCopy = document.getElementById('footerCopy');
    if (footerCopy) {
        footerCopy.innerHTML = t('footer_copyright', { year: new Date().getFullYear() });
    }

    // Update system version
    const footerVersion = document.getElementById('footerVersion');
    if (footerVersion) {
        footerVersion.textContent = t('system_version');
    }

    // Update employee portal link
    const footerPortal = document.getElementById('footerPortal');
    if (footerPortal) {
        footerPortal.textContent = t('employee_portal');
    }

    // Update invoice number placeholder with current language
    if (typeof loadSeqAndHint === 'function') {
        loadSeqAndHint();
    }
}

// Initialize i18n system
function initI18n() {
    // Set up language selector
    const langSelector = document.getElementById('langSel');
    if (langSelector) {
        langSelector.value = currentLanguage;
        langSelector.addEventListener('change', (e) => {
            setLanguage(e.target.value);
        });
    }
    
    // Initial text update
    updatePageTexts();
}

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initI18n);
} else {
    initI18n();
}
