/**
 * Settings Page JavaScript
 */

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    loadGeneralSettings();
    loadEmailSettings();
    loadTemplates();
    
    // Setup form handlers
    document.getElementById('generalForm').addEventListener('submit', saveGeneralSettings);
    document.getElementById('emailForm').addEventListener('submit', saveEmailSettings);
});

// Tab switching
function switchTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab and mark button as active
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
}

// Load general settings
async function loadGeneralSettings() {
    try {
        const response = await fetch('/api/configurations?config_type=general');
        if (!response.ok) throw new Error('Failed to load general settings');

        const configs = await response.json();

        // Populate form fields directly from the config object
        document.getElementById('company_name').value = configs.company_name || '';
        document.getElementById('company_address').value = configs.company_address || '';
        document.getElementById('default_currency').value = configs.default_currency || 'GBP';
        
    } catch (error) {
        console.error('Error loading general settings:', error);
        showAlert('error', 'Failed to load general settings: ' + error.message);
    }
}

// Save general settings
async function saveGeneralSettings(event) {
    event.preventDefault();
    
    try {
        const formData = new FormData(event.target);
        const settings = [
            { key: 'company_name', value: formData.get('company_name'), description: 'Company name for invoices', config_type: 'general' },
            { key: 'company_address', value: formData.get('company_address'), description: 'Company address for invoices', config_type: 'general' },
            { key: 'default_currency', value: formData.get('default_currency'), description: 'Default currency for invoices', config_type: 'general' }
        ];
        
        for (const setting of settings) {
            const response = await fetch('/api/configurations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(setting)
            });
            
            if (!response.ok) throw new Error(`Failed to save ${setting.key}`);
        }
        
        showAlert('success', 'General settings saved successfully!');
        
    } catch (error) {
        console.error('Error saving general settings:', error);
        showAlert('error', 'Failed to save general settings: ' + error.message);
    }
}

// Load email settings
async function loadEmailSettings() {
    try {
        const response = await fetch('/api/configurations?config_type=email');
        if (!response.ok) throw new Error('Failed to load email settings');
        
        const configs = await response.json();

        // Populate form fields directly from the config object
        document.getElementById('email_smtp_server').value = configs.smtp_server || '';
        document.getElementById('email_smtp_port').value = configs.smtp_port || '587';
        document.getElementById('email_username').value = configs.smtp_username || '';
        document.getElementById('email_password').value = ''; // Never populate password
        document.getElementById('auto_send_emails').checked = configs.auto_send === true;
        
    } catch (error) {
        console.error('Error loading email settings:', error);
        showAlert('error', 'Failed to load email settings: ' + error.message);
    }
}

// Save email settings
async function saveEmailSettings(event) {
    event.preventDefault();
    
    try {
        const formData = new FormData(event.target);
        const settings = [
            { key: 'email_smtp_server', value: formData.get('email_smtp_server'), description: 'SMTP server for email sending', config_type: 'email' },
            { key: 'email_smtp_port', value: formData.get('email_smtp_port'), description: 'SMTP port for email sending', config_type: 'email' },
            { key: 'email_username', value: formData.get('email_username'), description: 'Email username for SMTP authentication', config_type: 'email' },
            { key: 'auto_send_emails', value: formData.get('auto_send_emails') ? 'true' : 'false', description: 'Automatically send invoices via email', config_type: 'email' }
        ];
        
        // Only save password if it's provided
        const password = formData.get('email_password');
        if (password && password.trim()) {
            settings.push({
                key: 'email_password',
                value: password,
                description: 'Email password for SMTP authentication',
                config_type: 'email'
            });
        }
        
        for (const setting of settings) {
            const response = await fetch('/api/configurations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(setting)
            });
            
            if (!response.ok) throw new Error(`Failed to save ${setting.key}`);
        }
        
        showAlert('success', 'Email settings saved successfully!');
        
    } catch (error) {
        console.error('Error saving email settings:', error);
        showAlert('error', 'Failed to save email settings: ' + error.message);
    }
}

// Test email settings
async function testEmailSettings() {
    try {
        showAlert('info', 'Testing email connection...');
        
        // This would be implemented in the backend
        // For now, just show a placeholder message
        setTimeout(() => {
            showAlert('success', 'Email test functionality will be implemented in the next phase.');
        }, 1000);
        
    } catch (error) {
        console.error('Error testing email settings:', error);
        showAlert('error', 'Failed to test email settings: ' + error.message);
    }
}

// Load templates
async function loadTemplates() {
    try {
        const container = document.getElementById('templatesContainer');
        const loading = document.getElementById('templatesLoading');
        
        loading.style.display = 'block';
        
        // This would fetch templates from the backend
        // For now, show placeholder content
        setTimeout(() => {
            loading.style.display = 'none';
            container.innerHTML = `
                <div class="config-item">
                    <div class="config-info">
                        <div class="config-key">Default Template</div>
                        <div class="config-description">Standard invoice template used for all generations</div>
                    </div>
                    <div class="config-value">Template_Invoice_Geral.xlsx</div>
                </div>
                <div style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                    <span class="material-icons" style="font-size: 3rem; margin-bottom: 1rem;">description</span>
                    <p>Template management will be fully implemented in the next phase.</p>
                    <p>Currently using: DADOS/Template_Invoice_Geral.xlsx</p>
                </div>
            `;
        }, 1000);
        
    } catch (error) {
        console.error('Error loading templates:', error);
        showAlert('error', 'Failed to load templates: ' + error.message);
    }
}

// Upload template
function uploadTemplate() {
    showAlert('info', 'Template upload functionality will be implemented in the next phase.');
}

// Reset database function
async function resetDatabase() {
    const password = document.getElementById('resetPassword').value;

    if (!password) {
        showAlert('error', 'Please enter the password to proceed');
        return;
    }

    // Confirm action
    if (!confirm('⚠️ WARNING: This will permanently delete ALL invoices and sessions!\n\nThis action cannot be undone. Are you absolutely sure?')) {
        return;
    }

    // Second confirmation
    if (!confirm('🚨 FINAL CONFIRMATION: All data will be lost forever!\n\nType YES in the next dialog to proceed.')) {
        return;
    }

    const finalConfirm = prompt('Type "YES" to confirm database reset:');
    if (finalConfirm !== 'YES') {
        showAlert('error', 'Database reset cancelled');
        return;
    }

    try {
        showAlert('info', 'Resetting database... Please wait...');

        const response = await fetch('/api/reset-database', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ password: password })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || 'Failed to reset database');
        }

        // Clear password field
        document.getElementById('resetPassword').value = '';

        // Show success message with details
        const deletedInfo = result.deleted;
        const message = `Database reset successfully!<br><br>Deleted:<br>• ${deletedInfo.sessions} sessions (files)<br>• ${deletedInfo.invoices} invoices (files)<br>• ${deletedInfo.pdfs} PDF files<br>• ${deletedInfo.db_invoices || 0} invoices (database)<br>• ${deletedInfo.db_sessions || 0} sessions (database)`;

        showAlert('success', message);

        // Optionally reload the page after a delay
        setTimeout(() => {
            if (confirm('Database has been reset. Reload the page to see updated statistics?')) {
                window.location.reload();
            }
        }, 3000);

    } catch (error) {
        console.error('Error resetting database:', error);

        // Check if it's a file locking error
        const errorMsg = error.message || '';
        if (errorMsg.includes('WinError 32') || errorMsg.includes('being used by another process') || errorMsg.includes('locked')) {
            showAlert('error', `
                <strong>❌ Database is locked by the server</strong><br><br>
                <strong>Solution: Use the offline reset script</strong><br><br>
                <strong>Steps:</strong><br>
                1. Stop the server (Ctrl+C in terminal)<br>
                2. Run: <code>python reset_database.py</code><br>
                3. Follow the prompts<br>
                4. Restart the server<br><br>
                <em>This is the recommended method for Windows.</em>
            `);
        } else {
            showAlert('error', 'Failed to reset database: ' + error.message);
        }
    }
}

// Utility functions
function showAlert(type, message) {
    const container = document.getElementById('alertContainer');
    
    // Remove existing alerts
    container.innerHTML = '';
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.style.display = 'block';
    
    // Add icon based on type
    let icon = 'info';
    if (type === 'success') icon = 'check_circle';
    else if (type === 'error') icon = 'error';
    else if (type === 'warning') icon = 'warning';
    
    alert.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span class="material-icons">${icon}</span>
            <span>${message}</span>
        </div>
    `;
    
    container.appendChild(alert);
    
    // Auto-hide success and info messages
    if (type === 'success' || type === 'info') {
        setTimeout(() => {
            alert.style.display = 'none';
        }, 5000);
    }
}

// Form validation helpers
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validateRequired(value) {
    return value && value.trim().length > 0;
}
