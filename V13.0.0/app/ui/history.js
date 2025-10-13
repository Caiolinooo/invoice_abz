/**
 * Invoice History JavaScript
 */

let currentPage = 0;
const pageSize = 20;
let currentFilters = {};

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

// Get translated status text
function getStatusText(status) {
    if (typeof t === 'function') {
        return t(status) || capitalizeFirst(status);
    }
    return capitalizeFirst(status);
}

// Capitalize first letter
function capitalizeFirst(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Check authentication first
    if (!checkAuth()) {
        return;
    }

    // Wait for i18n to be ready
    if (typeof initI18n === 'function') {
        initI18n();
    }
    loadStats();
    loadInvoices();
});

// Load statistics
async function loadStats() {
    try {
        const token = getAuthToken();
        const response = await fetch('/api/invoices/stats', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        // Check for authentication errors
        if (response.status === 401) {
            console.error('Authentication failed - redirecting to login');
            alert(t('session_expired') || 'Session expired. Please login again.');
            window.location.href = '/ui/login.html';
            return;
        }

        if (!response.ok) throw new Error('Failed to load stats');

        const stats = await response.json();

        console.log('[DEBUG] Stats received:', stats);

        // Helper function to set value with tooltip
        const setValueWithTooltip = (elementId, compactValue, fullValue) => {
            const element = document.getElementById(elementId);
            element.textContent = compactValue;
            element.title = fullValue; // Tooltip showing full value
            element.style.cursor = 'help';
        };

        // Update all stat cards with compact formatting for large numbers
        document.getElementById('totalInvoices').textContent = stats.total_invoices || 0;

        // Format currency values with tooltips
        const totalAmountFull = formatCurrency(stats.total_amount || 0);
        const totalAmountCompact = formatCurrencyCompact(stats.total_amount || 0);
        setValueWithTooltip('totalAmount', totalAmountCompact, totalAmountFull);

        const currentMonthFull = formatCurrency(stats.current_month_amount || 0);
        const currentMonthCompact = formatCurrencyCompact(stats.current_month_amount || 0);
        setValueWithTooltip('currentMonthAmount', currentMonthCompact, currentMonthFull);

        const lastMonthFull = formatCurrency(stats.last_month_amount || 0);
        const lastMonthCompact = formatCurrencyCompact(stats.last_month_amount || 0);
        setValueWithTooltip('lastMonthAmount', lastMonthCompact, lastMonthFull);

        document.getElementById('recentInvoices').textContent = stats.recent_invoices || 0;

        // Calculate pending invoices from status breakdown
        const pending = (stats.status_breakdown?.generated || 0) + (stats.status_breakdown?.sent || 0);
        document.getElementById('pendingInvoices').textContent = pending;

    } catch (error) {
        console.error('Error loading stats:', error);
        showError(t('failed_load_statistics'));
    }
}

// Load invoices with current filters and pagination
async function loadInvoices() {
    try {
        showLoading(true);
        hideError();

        const params = new URLSearchParams({
            skip: currentPage * pageSize,
            limit: pageSize,
            ...currentFilters
        });

        console.log('[DEBUG] Loading invoices with params:', params.toString());

        const token = getAuthToken();
        const response = await fetch(`/api/invoices?${params}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        // Check for authentication errors
        if (response.status === 401) {
            console.error('Authentication failed - redirecting to login');
            alert(t('session_expired') || 'Session expired. Please login again.');
            window.location.href = '/ui/login.html';
            return;
        }

        if (!response.ok) throw new Error('Failed to load invoices');

        const data = await response.json();
        console.log('[DEBUG] Received data:', data);

        // API returns array directly, not wrapped in object
        const invoices = Array.isArray(data) ? data : (data.invoices || []);
        console.log('[DEBUG] Invoices to display:', invoices.length);

        displayInvoices(invoices);
        
    } catch (error) {
        console.error('Error loading invoices:', error);
        showError(t('failed_load_invoices') + ': ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Display invoices in table
function displayInvoices(invoices) {
    const tbody = document.getElementById('invoicesTableBody');
    tbody.innerHTML = '';

    if (invoices.length === 0) {
        const noInvoicesText = typeof t === 'function' ? t('no_invoices_found') : 'No invoices found';
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                    ${noInvoicesText}
                </td>
            </tr>
        `;
        return;
    }
    
    invoices.forEach(invoice => {
        const row = document.createElement('tr');

        // Build file links with better styling
        const buildFileLinks = () => {
            const links = [];

            // XLSX download and view buttons
            if (invoice.file_path_xlsx) {
                const excelTitle = typeof t === 'function' ? t('download_excel') : 'Download Excel';
                const viewTitle = typeof t === 'function' ? t('view_details') : 'View Details';
                links.push(`<a href="javascript:void(0)" onclick="downloadFile('/api/invoices/${invoice.id}/download', '${invoice.employee_name.replace(/'/g, "\\'")}_Invoice_${invoice.invoice_number}.xlsx')" title="${excelTitle}" class="file-link excel-link">
                    <span class="material-icons" style="font-size: 16px;">download</span>
                    <span>XLSX</span>
                </a>`);
                links.push(`<button onclick="viewInvoice(${invoice.id})" title="${viewTitle}" class="file-link excel-link" style="border: none; background: none; cursor: pointer;">
                    <span class="material-icons" style="font-size: 16px;">visibility</span>
                    <span>View</span>
                </button>`);
            }

            // PDF button - use dedicated endpoint
            if (invoice.file_path_pdf) {
                const pdfTitle = typeof t === 'function' ? t('view_pdf') : 'View PDF';
                links.push(`<a href="javascript:void(0)" onclick="openPDF('/api/invoices/${invoice.id}/pdf')" title="${pdfTitle}" class="file-link pdf-link">
                    <span class="material-icons" style="font-size: 16px;">picture_as_pdf</span>
                    <span>PDF</span>
                </a>`);
            } else if (invoice.status === 'pending' || invoice.status === 'pdf_pending') {
                // Show regenerate button for pending PDFs
                const regenerateTitle = typeof t === 'function' ? t('regenerate_pdf') : 'Regenerate PDF';
                links.push(`<button onclick="regeneratePDF(${invoice.id})" title="${regenerateTitle}" class="file-link pdf-link" style="border: none; background: #fbbf24; cursor: pointer; color: white;">
                    <span class="material-icons" style="font-size: 16px;">refresh</span>
                    <span>PDF</span>
                </button>`);
            }

            if (links.length === 0) {
                const processingText = typeof t === 'function' ? t('processing') : 'Processing...';
                return `<span class="text-muted">${processingText}</span>`;
            }
            return links.join(' ');
        };

        row.innerHTML = `
            <td>${invoice.invoice_number}</td>
            <td>${invoice.employee_name}</td>
            <td>${invoice.employee_position || '-'}</td>
            <td>${formatDate(invoice.invoice_date)}</td>
            <td>${formatCurrency(invoice.total_amount)}</td>
            <td>
                <span class="status-badge status-${invoice.status}">
                    ${getStatusText(invoice.status)}
                </span>
            </td>
            <td>
                <div style="display: flex; gap: 0.5rem; align-items: center;">
                    ${buildFileLinks()}
                </div>
            </td>
            <td>
                <select onchange="updateInvoiceStatus(${invoice.id}, this.value)" style="padding: 0.25rem; border-radius: 0.25rem; border: 1px solid var(--border);">
                    <option value="generated" ${invoice.status === 'generated' ? 'selected' : ''}>${getStatusText('generated')}</option>
                    <option value="sent" ${invoice.status === 'sent' ? 'selected' : ''}>${getStatusText('sent')}</option>
                    <option value="paid" ${invoice.status === 'paid' ? 'selected' : ''}>${getStatusText('paid')}</option>
                    <option value="cancelled" ${invoice.status === 'cancelled' ? 'selected' : ''}>${getStatusText('cancelled')}</option>
                </select>
            </td>
        `;
        tbody.appendChild(row);
    });
    
    updatePagination(invoices.length === pageSize);
}

// Update invoice status
async function updateInvoiceStatus(invoiceId, newStatus) {
    try {
        console.log('[DEBUG] Updating invoice status:', { invoiceId, newStatus });

        const formData = new FormData();
        formData.append('status', newStatus);

        const token = getAuthToken();
        const response = await fetch(`/api/invoices/${invoiceId}/status`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        console.log('[DEBUG] Update response status:', response.status);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('[DEBUG] Update failed:', errorText);
            throw new Error('Failed to update status');
        }

        const result = await response.json();
        console.log('[DEBUG] Update result:', result);

        // Reload stats and current page
        loadStats();
        loadInvoices();

        showSuccess('Status updated successfully');

    } catch (error) {
        console.error('Error updating status:', error);
        showError('Failed to update status: ' + error.message);
        // Reload to reset the select
        loadInvoices();
    }
}

// Apply filters
function applyFilters() {
    currentFilters = {};
    currentPage = 0;

    const employee = document.getElementById('filterEmployee').value.trim();
    const status = document.getElementById('filterStatus').value;
    const dateFrom = document.getElementById('filterDateFrom').value;
    const dateTo = document.getElementById('filterDateTo').value;

    if (employee) currentFilters.employee_name = employee;
    if (status) currentFilters.status = status;
    if (dateFrom) currentFilters.date_from = dateFrom;
    if (dateTo) currentFilters.date_to = dateTo;

    console.log('[DEBUG] Applying filters:', currentFilters);

    loadInvoices();
}

// Clear filters
function clearFilters() {
    document.getElementById('filterEmployee').value = '';
    document.getElementById('filterStatus').value = '';
    document.getElementById('filterDateFrom').value = '';
    document.getElementById('filterDateTo').value = '';
    
    currentFilters = {};
    currentPage = 0;
    
    loadInvoices();
}

// Update pagination
function updatePagination(hasMore) {
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = '';
    
    // Previous button
    const prevBtn = document.createElement('button');
    prevBtn.textContent = 'Previous';
    prevBtn.disabled = currentPage === 0;
    prevBtn.onclick = () => {
        if (currentPage > 0) {
            currentPage--;
            loadInvoices();
        }
    };
    pagination.appendChild(prevBtn);
    
    // Page info
    const pageInfo = document.createElement('span');
    pageInfo.textContent = `Page ${currentPage + 1}`;
    pageInfo.style.padding = '0.5rem 1rem';
    pageInfo.style.display = 'flex';
    pageInfo.style.alignItems = 'center';
    pagination.appendChild(pageInfo);
    
    // Next button
    const nextBtn = document.createElement('button');
    nextBtn.textContent = 'Next';
    nextBtn.disabled = !hasMore;
    nextBtn.onclick = () => {
        if (hasMore) {
            currentPage++;
            loadInvoices();
        }
    };
    pagination.appendChild(nextBtn);
    
    pagination.style.display = 'flex';
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

function formatCurrency(amount) {
    if (!amount) return '£0.00';

    // For large amounts, use compact notation
    if (amount >= 1000000) {
        return new Intl.NumberFormat('en-GB', {
            style: 'currency',
            currency: 'GBP',
            notation: 'compact',
            maximumFractionDigits: 2
        }).format(amount);
    }

    // For smaller amounts, use standard notation
    return new Intl.NumberFormat('en-GB', {
        style: 'currency',
        currency: 'GBP',
        maximumFractionDigits: 2
    }).format(amount);
}

// Format currency for stat cards (more compact)
function formatCurrencyCompact(amount) {
    if (!amount) return '£0';

    // For very large amounts (millions)
    if (amount >= 1000000) {
        const millions = amount / 1000000;
        return `£${millions.toFixed(2)}M`;
    }

    // For large amounts (thousands)
    if (amount >= 100000) {
        const thousands = amount / 1000;
        return `£${thousands.toFixed(1)}K`;
    }

    // For medium amounts
    if (amount >= 10000) {
        return new Intl.NumberFormat('en-GB', {
            style: 'currency',
            currency: 'GBP',
            maximumFractionDigits: 0
        }).format(amount);
    }

    // For smaller amounts
    return new Intl.NumberFormat('en-GB', {
        style: 'currency',
        currency: 'GBP',
        maximumFractionDigits: 2
    }).format(amount);
}

function showLoading(show) {
    const loading = document.getElementById('loadingMessage');
    const table = document.getElementById('invoicesTable');
    const pagination = document.getElementById('pagination');
    
    if (show) {
        loading.style.display = 'block';
        table.style.display = 'none';
        pagination.style.display = 'none';
    } else {
        loading.style.display = 'none';
        table.style.display = 'table';
    }
}

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        hideError();
    }, 5000);
}

function hideError() {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.style.display = 'none';
}

function showSuccess(message) {
    // Create temporary success message
    const successDiv = document.createElement('div');
    successDiv.className = 'error'; // Reuse error styling
    successDiv.style.background = '#D4EDDA';
    successDiv.style.color = '#155724';
    successDiv.style.borderColor = '#C3E6CB';
    successDiv.textContent = message;
    
    const container = document.querySelector('.container');
    container.insertBefore(successDiv, container.firstChild);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        successDiv.remove();
    }, 3000);
}

// View invoice details
async function viewInvoice(invoiceId) {
    try {
        const token = getAuthToken();
        const response = await fetch(`/api/invoices/${invoiceId}/view`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        // Check for authentication errors
        if (response.status === 401) {
            console.error('Authentication failed - redirecting to login');
            alert(t('session_expired') || 'Session expired. Please login again.');
            window.location.href = '/ui/login.html';
            return;
        }

        if (!response.ok) throw new Error('Failed to load invoice details');

        const invoice = await response.json();

        // Create modal dialog
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(4px);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            animation: fadeIn 0.2s ease-in-out;
        `;

        const modalContent = document.createElement('div');
        modalContent.style.cssText = `
            background: white;
            padding: 0;
            border-radius: 1rem;
            max-width: 900px;
            width: 95%;
            max-height: 90vh;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            animation: slideUp 0.3s ease-out;
        `;

        // Build service lines table
        let serviceLinesHTML = '';
        if (invoice.service_lines && invoice.service_lines.length > 0) {
            let servicesTotal = 0;
            const serviceRows = invoice.service_lines.map(line => {
                servicesTotal += line.final_price || 0;
                return `
                    <tr>
                        <td style="padding: 0.75rem; border-bottom: 1px solid #e5e7eb;">${line.description}</td>
                        <td style="padding: 0.75rem; border-bottom: 1px solid #e5e7eb; text-align: right;">${line.unit_price !== null ? '£' + line.unit_price.toFixed(2) : '-'}</td>
                        <td style="padding: 0.75rem; border-bottom: 1px solid #e5e7eb; text-align: center;">${line.quantity !== null ? line.quantity : '-'}</td>
                        <td style="padding: 0.75rem; border-bottom: 1px solid #e5e7eb; text-align: right; font-weight: 600;">£${(line.final_price || 0).toFixed(2)}</td>
                    </tr>
                `;
            }).join('');

            // Add Additional and Expenses rows if present
            if (invoice.additional_total > 0) {
                serviceRows += `
                    <tr style="background-color: #fef3c7;">
                        <td style="padding: 0.75rem; border-bottom: 1px solid #e5e7eb; font-weight: 600;">${t('brazilian_payroll_additional')}</td>
                        <td style="padding: 0.75rem; border-bottom: 1px solid #e5e7eb; text-align: right;">-</td>
                        <td style="padding: 0.75rem; border-bottom: 1px solid #e5e7eb; text-align: center;">-</td>
                        <td style="padding: 0.75rem; border-bottom: 1px solid #e5e7eb; text-align: right; font-weight: 600; color: #d97706;">£${invoice.additional_total.toFixed(2)}</td>
                    </tr>
                `;
            }

            if (invoice.expenses_total > 0) {
                serviceRows += `
                    <tr style="background-color: #fef3c7;">
                        <td style="padding: 0.75rem; border-bottom: 1px solid #e5e7eb; font-weight: 600;">${t('expenses')}</td>
                        <td style="padding: 0.75rem; border-bottom: 1px solid #e5e7eb; text-align: right;">-</td>
                        <td style="padding: 0.75rem; border-bottom: 1px solid #e5e7eb; text-align: center;">-</td>
                        <td style="padding: 0.75rem; border-bottom: 1px solid #e5e7eb; text-align: right; font-weight: 600; color: #d97706;">£${invoice.expenses_total.toFixed(2)}</td>
                    </tr>
                `;
            }

            const grandTotal = servicesTotal + invoice.additional_total + invoice.expenses_total;

            serviceLinesHTML = `
                <div style="margin-top: 1.5rem; padding: 0 2rem;">
                    <h3 style="margin: 0 0 1rem 0; color: #374151; font-size: 1.1rem;">${t('service_lines')}</h3>
                    <div style="overflow-x: auto; border: 1px solid #e5e7eb; border-radius: 0.5rem;">
                        <table style="width: 100%; border-collapse: collapse; font-size: 0.9rem;">
                            <thead>
                                <tr style="background-color: #f9fafb;">
                                    <th style="padding: 0.75rem; text-align: left; font-weight: 600; color: #6b7280; border-bottom: 2px solid #e5e7eb;">${t('description')}</th>
                                    <th style="padding: 0.75rem; text-align: right; font-weight: 600; color: #6b7280; border-bottom: 2px solid #e5e7eb;">${t('unit_price')}</th>
                                    <th style="padding: 0.75rem; text-align: center; font-weight: 600; color: #6b7280; border-bottom: 2px solid #e5e7eb;">${t('quantity')}</th>
                                    <th style="padding: 0.75rem; text-align: right; font-weight: 600; color: #6b7280; border-bottom: 2px solid #e5e7eb;">${t('total')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${serviceRows}
                                <tr style="background-color: #f3f4f6; font-weight: 700;">
                                    <td colspan="3" style="padding: 1rem; text-align: right; border-top: 2px solid #d1d5db;">${t('grand_total')}:</td>
                                    <td style="padding: 1rem; text-align: right; color: #059669; font-size: 1.1rem; border-top: 2px solid #d1d5db;">£${grandTotal.toFixed(2)}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }

        modalContent.innerHTML = `
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; color: white; border-radius: 1rem 1rem 0 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h2 style="margin: 0 0 0.5rem 0; font-size: 1.5rem;">${t('invoice_preview')}</h2>
                        <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">${invoice.invoice_number || 'N/A'}</p>
                    </div>
                    <button onclick="this.closest('.modal').remove()" style="background: rgba(255,255,255,0.2); border: none; width: 40px; height: 40px; border-radius: 50%; font-size: 1.5rem; cursor: pointer; color: white; transition: all 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.3)'" onmouseout="this.style.background='rgba(255,255,255,0.2)'">×</button>
                </div>
            </div>

            <!-- Content -->
            <div style="max-height: calc(90vh - 200px); overflow-y: auto; padding: 2rem;">
                <!-- Info Grid -->
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 1.5rem;">
                    <div style="padding: 1rem; background: #f9fafb; border-radius: 0.5rem; border-left: 4px solid #667eea;">
                        <div style="font-size: 0.75rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">${t('employee')}</div>
                        <div style="font-weight: 600; color: #111827;">${invoice.employee_name || 'N/A'}</div>
                    </div>
                    <div style="padding: 1rem; background: #f9fafb; border-radius: 0.5rem; border-left: 4px solid #667eea;">
                        <div style="font-size: 0.75rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">${t('position')}</div>
                        <div style="font-weight: 600; color: #111827;">${invoice.employee_position || 'N/A'}</div>
                    </div>
                    <div style="padding: 1rem; background: #f9fafb; border-radius: 0.5rem; border-left: 4px solid #667eea;">
                        <div style="font-size: 0.75rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">${t('date')}</div>
                        <div style="font-weight: 600; color: #111827;">${formatDate(invoice.invoice_date)}</div>
                    </div>
                    <div style="padding: 1rem; background: #f9fafb; border-radius: 0.5rem; border-left: 4px solid #667eea;">
                        <div style="font-size: 0.75rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">${t('call_off')}</div>
                        <div style="font-weight: 600; color: #111827;">${invoice.call_off || 'N/A'}</div>
                    </div>
                    <div style="padding: 1rem; background: #ecfdf5; border-radius: 0.5rem; border-left: 4px solid #10b981;">
                        <div style="font-size: 0.75rem; color: #065f46; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">${t('amount')}</div>
                        <div style="font-weight: 700; color: #059669; font-size: 1.25rem;">${formatCurrency(invoice.total_amount)} ${invoice.currency || 'GBP'}</div>
                    </div>
                    <div style="padding: 1rem; background: #f9fafb; border-radius: 0.5rem; border-left: 4px solid #667eea;">
                        <div style="font-size: 0.75rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">${t('status')}</div>
                        <div><span class="status-badge status-${invoice.status}">${getStatusText(invoice.status)}</span></div>
                    </div>
                </div>

                ${serviceLinesHTML}
            </div>

            <!-- Footer -->
            <div style="padding: 1.5rem 2rem; background: #f9fafb; border-top: 1px solid #e5e7eb; display: flex; gap: 1rem; justify-content: space-between; align-items: center; border-radius: 0 0 1rem 1rem;">
                <!-- Left side buttons -->
                <div style="display: flex; gap: 1rem;">
                    ${invoice.file_exists ? `
                        <a href="/api/invoices/${invoiceId}/download" class="btn btn-primary" style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; text-decoration: none; border-radius: 0.5rem; font-weight: 600; transition: all 0.2s;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(16, 185, 129, 0.4)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
                            <span class="material-icons" style="font-size: 18px;">download</span>
                            ${t('download_excel') || 'Baixar Excel'}
                        </a>
                        <a href="javascript:void(0)" onclick="openPDF('/api/invoices/${invoiceId}/pdf')" class="btn btn-primary" style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; text-decoration: none; border-radius: 0.5rem; font-weight: 600; transition: all 0.2s; cursor: pointer;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(239, 68, 68, 0.4)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
                            <span class="material-icons" style="font-size: 18px;">picture_as_pdf</span>
                            ${t('download_pdf') || 'Baixar PDF'}
                        </a>
                    ` : `<span style="color: #9ca3af;">${t('file_not_available') || 'Arquivo não disponível'}</span>`}
                </div>

                <!-- Right side buttons -->
                <div style="display: flex; gap: 1rem;">
                    <button onclick="editInvoice(${invoiceId})" class="btn btn-secondary" style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 0.5rem; font-weight: 600; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(102, 126, 234, 0.4)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
                        <span class="material-icons" style="font-size: 18px;">edit</span>
                        ${t('edit') || 'Editar'}
                    </button>
                    <button onclick="this.closest('.modal').remove()" class="btn btn-secondary" style="padding: 0.75rem 1.5rem; background: white; color: #374151; border: 1px solid #d1d5db; border-radius: 0.5rem; font-weight: 600; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.background='#f3f4f6'" onmouseout="this.style.background='white'">
                        ${t('close') || 'Fechar'}
                    </button>
                </div>
            </div>
        `;

        modal.className = 'modal';
        modal.appendChild(modalContent);
        document.body.appendChild(modal);

        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });

    } catch (error) {
        console.error('Error viewing invoice:', error);
        showError(t('failed_load_invoice'));
    }
}

// Edit invoice - open edit modal
async function editInvoice(invoiceId) {
    try {
        // Close current modal
        const currentModal = document.querySelector('.modal');
        if (currentModal) {
            currentModal.remove();
        }

        // Fetch invoice details
        const token = getAuthToken();
        const response = await fetch(`/api/invoices/${invoiceId}/view`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.status === 401) {
            alert(t('session_expired') || 'Session expired. Please login again.');
            window.location.href = '/ui/login.html';
            return;
        }

        if (!response.ok) throw new Error('Failed to load invoice details');

        const invoice = await response.json();
        console.log('Invoice data for editing:', invoice);
        console.log('Service lines:', invoice.service_lines);

        // Format date for input field (YYYY-MM-DD)
        let formattedDate = '';
        if (invoice.invoice_date) {
            const date = new Date(invoice.invoice_date);
            formattedDate = date.toISOString().split('T')[0];
        }

        // Create edit modal
        const modal = document.createElement('div');
        const modalContent = document.createElement('div');
        modalContent.className = 'modal-content';
        modalContent.style.maxWidth = '900px';
        modalContent.style.maxHeight = '90vh';
        modalContent.style.overflow = 'auto';

        // Build service lines HTML for editing
        const serviceLines = invoice.service_lines || [];
        const serviceLinesHTML = `
            <div style="margin-top: 2rem;">
                <h3 style="font-size: 1.25rem; font-weight: 700; color: #1f2937; margin-bottom: 1rem;">${t('service_lines') || 'Linhas de Serviço'}</h3>
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background: #f3f4f6; border-bottom: 2px solid #e5e7eb;">
                                <th style="padding: 0.75rem; text-align: left; font-weight: 600; color: #374151; width: 40%;">${t('description') || 'Descrição'}</th>
                                <th style="padding: 0.75rem; text-align: right; font-weight: 600; color: #374151; width: 20%;">${t('unit_price') || 'Preço Unit.'}</th>
                                <th style="padding: 0.75rem; text-align: right; font-weight: 600; color: #374151; width: 20%;">${t('quantity') || 'Quantidade'}</th>
                                <th style="padding: 0.75rem; text-align: right; font-weight: 600; color: #374151; width: 20%;">${t('total') || 'Total'}</th>
                            </tr>
                        </thead>
                        <tbody id="editServiceLines">
                            ${serviceLines.length > 0 ? serviceLines.map((line, index) => `
                                <tr style="border-bottom: 1px solid #e5e7eb;">
                                    <td style="padding: 0.75rem;">
                                        <input type="text" value="${(line.description || '').replace(/"/g, '&quot;')}"
                                               data-line="${index}" data-field="description"
                                               style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem; font-size: 0.875rem;">
                                    </td>
                                    <td style="padding: 0.75rem;">
                                        <input type="number" value="${line.unit_price || 0}"
                                               data-line="${index}" data-field="unit_price" step="0.01"
                                               style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem; text-align: right; font-size: 0.875rem;">
                                    </td>
                                    <td style="padding: 0.75rem;">
                                        <input type="number" value="${line.quantity || 0}"
                                               data-line="${index}" data-field="quantity" step="0.01"
                                               style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem; text-align: right; font-size: 0.875rem;">
                                    </td>
                                    <td style="padding: 0.75rem; text-align: right; font-weight: 600; color: #059669;">
                                        <span data-line-total="${index}">${formatCurrency(line.amount || 0)}</span>
                                    </td>
                                </tr>
                            `).join('') : `
                                <tr>
                                    <td colspan="4" style="padding: 2rem; text-align: center; color: #9ca3af;">
                                        ${t('no_service_lines') || 'Nenhuma linha de serviço encontrada'}
                                    </td>
                                </tr>
                            `}
                        </tbody>
                    </table>
                </div>
                <button onclick="addServiceLine()" style="margin-top: 1rem; padding: 0.5rem 1rem; background: #667eea; color: white; border: none; border-radius: 0.375rem; cursor: pointer; font-weight: 600; display: inline-flex; align-items: center; gap: 0.5rem;">
                    <span class="material-icons" style="font-size: 18px;">add</span>
                    ${t('add_line') || 'Adicionar Linha'}
                </button>
            </div>
        `;

        modalContent.innerHTML = `
            <!-- Header -->
            <div style="padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 1rem 1rem 0 0;">
                <h2 style="font-size: 1.875rem; font-weight: 700; margin: 0;">${t('edit_invoice') || 'Editar Invoice'}</h2>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">${invoice.invoice_number || ''}</p>
            </div>

            <!-- Content -->
            <div style="padding: 2rem;">
                <!-- Basic Info -->
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem; margin-bottom: 2rem;">
                    <div>
                        <label style="display: block; font-size: 0.875rem; font-weight: 600; color: #374151; margin-bottom: 0.5rem;">
                            ${t('invoice_number') || 'Número da Invoice'}
                        </label>
                        <input type="text" id="editInvoiceNumber" value="${invoice.invoice_number || ''}"
                               style="width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 0.5rem; background: #f9fafb;" readonly>
                    </div>
                    <div>
                        <label style="display: block; font-size: 0.875rem; font-weight: 600; color: #374151; margin-bottom: 0.5rem;">
                            ${t('invoice_date') || 'Data da Invoice'}
                        </label>
                        <input type="date" id="editInvoiceDate" value="${formattedDate}"
                               style="width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 0.5rem;">
                    </div>
                    <div>
                        <label style="display: block; font-size: 0.875rem; font-weight: 600; color: #374151; margin-bottom: 0.5rem;">
                            ${t('employee_name') || 'Nome do Colaborador'}
                        </label>
                        <input type="text" id="editEmployeeName" value="${invoice.employee_name || ''}"
                               style="width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 0.5rem;">
                    </div>
                    <div>
                        <label style="display: block; font-size: 0.875rem; font-weight: 600; color: #374151; margin-bottom: 0.5rem;">
                            ${t('position') || 'Cargo'}
                        </label>
                        <input type="text" id="editPosition" value="${invoice.employee_position || ''}"
                               style="width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 0.5rem;">
                    </div>
                    <div>
                        <label style="display: block; font-size: 0.875rem; font-weight: 600; color: #374151; margin-bottom: 0.5rem;">
                            ${t('call_off') || 'Call-Off'}
                        </label>
                        <input type="text" id="editCallOff" value="${invoice.call_off || ''}"
                               style="width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 0.5rem;">
                    </div>
                    <div>
                        <label style="display: block; font-size: 0.875rem; font-weight: 600; color: #374151; margin-bottom: 0.5rem;">
                            ${t('currency') || 'Moeda'}
                        </label>
                        <select id="editCurrency" style="width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 0.5rem;">
                            <option value="GBP" ${invoice.currency === 'GBP' ? 'selected' : ''}>GBP (£)</option>
                            <option value="USD" ${invoice.currency === 'USD' ? 'selected' : ''}>USD ($)</option>
                            <option value="EUR" ${invoice.currency === 'EUR' ? 'selected' : ''}>EUR (€)</option>
                            <option value="BRL" ${invoice.currency === 'BRL' ? 'selected' : ''}>BRL (R$)</option>
                        </select>
                    </div>
                </div>

                ${serviceLinesHTML}

                <!-- Total -->
                <div style="margin-top: 2rem; padding: 1.5rem; background: #f9fafb; border-radius: 0.5rem; border-left: 4px solid #10b981;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 1.25rem; font-weight: 700; color: #374151;">${t('total') || 'Total'}</span>
                        <span id="editTotalAmount" style="font-size: 1.5rem; font-weight: 700; color: #059669;">${formatCurrency(invoice.total_amount)} ${invoice.currency || 'GBP'}</span>
                    </div>
                </div>
            </div>

            <!-- Footer -->
            <div style="padding: 1.5rem 2rem; background: #f9fafb; border-top: 1px solid #e5e7eb; display: flex; gap: 1rem; justify-content: flex-end; border-radius: 0 0 1rem 1rem;">
                <button onclick="saveInvoiceChanges(${invoiceId})" class="btn btn-primary" style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; border: none; border-radius: 0.5rem; font-weight: 600; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(16, 185, 129, 0.4)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
                    <span class="material-icons" style="font-size: 18px;">save</span>
                    ${t('save_changes') || 'Salvar Alterações'}
                </button>
                <button onclick="this.closest('.modal').remove()" class="btn btn-secondary" style="padding: 0.75rem 1.5rem; background: white; color: #374151; border: 1px solid #d1d5db; border-radius: 0.5rem; font-weight: 600; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.background='#f3f4f6'" onmouseout="this.style.background='white'">
                    ${t('cancel') || 'Cancelar'}
                </button>
            </div>
        `;

        modal.className = 'modal';
        modal.appendChild(modalContent);
        document.body.appendChild(modal);

        // Add event listeners to recalculate totals
        const inputs = modalContent.querySelectorAll('input[data-field="unit_price"], input[data-field="quantity"]');
        inputs.forEach(input => {
            input.addEventListener('input', () => recalculateTotals());
        });

        // Add event listener to currency change
        const currencySelect = document.getElementById('editCurrency');
        if (currencySelect) {
            currencySelect.addEventListener('change', () => recalculateTotals());
        }

        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });

    } catch (error) {
        console.error('Error editing invoice:', error);
        alert(t('failed_load_invoice') || 'Falha ao carregar detalhes da invoice');
    }
}

// Add new service line
function addServiceLine() {
    const tbody = document.getElementById('editServiceLines');
    const currentLines = tbody.querySelectorAll('tr').length;
    const newIndex = currentLines;

    // Remove "no service lines" message if exists
    const noDataRow = tbody.querySelector('td[colspan="4"]');
    if (noDataRow) {
        noDataRow.parentElement.remove();
    }

    const newRow = document.createElement('tr');
    newRow.style.borderBottom = '1px solid #e5e7eb';
    newRow.innerHTML = `
        <td style="padding: 0.75rem;">
            <input type="text" value=""
                   data-line="${newIndex}" data-field="description"
                   placeholder="${t('description') || 'Descrição'}"
                   style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem; font-size: 0.875rem;">
        </td>
        <td style="padding: 0.75rem;">
            <input type="number" value="0"
                   data-line="${newIndex}" data-field="unit_price" step="0.01"
                   style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem; text-align: right; font-size: 0.875rem;">
        </td>
        <td style="padding: 0.75rem;">
            <input type="number" value="0"
                   data-line="${newIndex}" data-field="quantity" step="0.01"
                   style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem; text-align: right; font-size: 0.875rem;">
        </td>
        <td style="padding: 0.75rem; text-align: right; font-weight: 600; color: #059669;">
            <span data-line-total="${newIndex}">${formatCurrency(0)}</span>
        </td>
    `;

    tbody.appendChild(newRow);

    // Add event listeners to new inputs
    const inputs = newRow.querySelectorAll('input[data-field="unit_price"], input[data-field="quantity"]');
    inputs.forEach(input => {
        input.addEventListener('input', () => recalculateTotals());
    });
}

// Recalculate all totals
function recalculateTotals() {
    const modal = document.querySelector('.modal');
    if (!modal) return;

    let grandTotal = 0;
    const rows = modal.querySelectorAll('#editServiceLines tr');

    rows.forEach((row, index) => {
        const unitPriceInput = row.querySelector(`input[data-field="unit_price"]`);
        const quantityInput = row.querySelector(`input[data-field="quantity"]`);
        const totalSpan = row.querySelector(`span[data-line-total]`);

        if (unitPriceInput && quantityInput && totalSpan) {
            const unitPrice = parseFloat(unitPriceInput.value) || 0;
            const quantity = parseFloat(quantityInput.value) || 0;
            const lineTotal = unitPrice * quantity;

            totalSpan.textContent = formatCurrency(lineTotal);
            grandTotal += lineTotal;
        }
    });

    const currency = document.getElementById('editCurrency')?.value || 'GBP';
    const totalElement = document.getElementById('editTotalAmount');
    if (totalElement) {
        totalElement.textContent = formatCurrency(grandTotal) + ' ' + currency;
    }
}

// Save invoice changes
async function saveInvoiceChanges(invoiceId) {
    try {
        const modal = document.querySelector('.modal');

        // Collect data from form
        const employeeName = document.getElementById('editEmployeeName').value;
        const position = document.getElementById('editPosition').value;
        const invoiceDate = document.getElementById('editInvoiceDate').value;
        const callOff = document.getElementById('editCallOff').value;
        const currency = document.getElementById('editCurrency').value;

        // Collect service lines
        const serviceLines = [];
        const serviceLineInputs = document.querySelectorAll('#editServiceLines tr');
        serviceLineInputs.forEach((row, index) => {
            const description = row.querySelector(`input[data-line="${index}"][data-field="description"]`)?.value;
            const unitPrice = parseFloat(row.querySelector(`input[data-line="${index}"][data-field="unit_price"]`)?.value) || 0;
            const quantity = parseFloat(row.querySelector(`input[data-line="${index}"][data-field="quantity"]`)?.value) || 0;

            if (description) {
                serviceLines.push({
                    description,
                    unit_price: unitPrice,
                    quantity,
                    final: unitPrice * quantity
                });
            }
        });

        // Calculate total
        const totalAmount = serviceLines.reduce((sum, line) => sum + line.final, 0);

        // Prepare data for regeneration
        const data = {
            invoice_id: invoiceId,
            employee_name: employeeName,
            position: position,
            invoice_date: invoiceDate,
            call_off: callOff,
            currency: currency,
            service_lines: serviceLines,
            total_amount: totalAmount
        };

        // Show loading
        const saveButton = modal.querySelector('button[onclick*="saveInvoiceChanges"]');
        const originalText = saveButton.innerHTML;
        saveButton.disabled = true;
        saveButton.innerHTML = '<span class="material-icons" style="font-size: 18px; animation: spin 1s linear infinite;">refresh</span> ' + (t('saving') || 'Salvando...');

        // Send to server to regenerate invoice
        const token = getAuthToken();
        const response = await fetch(`/api/invoices/${invoiceId}/regenerate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(data)
        });

        if (response.status === 401) {
            alert(t('session_expired') || 'Session expired. Please login again.');
            window.location.href = '/ui/login.html';
            return;
        }

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to save changes');
        }

        // Success
        alert(t('invoice_updated_success') || 'Invoice atualizada com sucesso!');
        modal.remove();

        // Reload invoices list
        loadInvoices();

    } catch (error) {
        console.error('Error saving invoice changes:', error);
        alert(t('failed_save_invoice') || 'Falha ao salvar alterações: ' + error.message);

        // Restore button
        const saveButton = document.querySelector('button[onclick*="saveInvoiceChanges"]');
        if (saveButton) {
            saveButton.disabled = false;
            saveButton.innerHTML = '<span class="material-icons" style="font-size: 18px;">save</span> ' + (t('save_changes') || 'Salvar Alterações');
        }
    }
}

// Regenerate PDF for pending invoice
async function regeneratePDF(invoiceId) {
    if (!confirm(t('confirm_regenerate_pdf') || 'Regenerate PDF for this invoice?')) {
        return;
    }

    try {
        showInfo(t('regenerating_pdf') || 'Regenerating PDF...');

        const token = getAuthToken();
        const response = await fetch(`/api/invoices/${invoiceId}/regenerate-pdf`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to regenerate PDF');
        }

        const result = await response.json();

        showSuccess(t('pdf_regenerated') || 'PDF regenerated successfully!');

        // Reload invoices to show updated status
        setTimeout(() => {
            loadInvoices();
        }, 1000);

    } catch (error) {
        console.error('Error regenerating PDF:', error);
        showError(t('failed_regenerate_pdf') || `Failed to regenerate PDF: ${error.message}`);
    }
}

// Download file with authentication
async function downloadFile(url, filename) {
    try {
        const token = getAuthToken();
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

// Open PDF in new tab with authentication
async function openPDF(url) {
    try {
        const token = getAuthToken();
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
            throw new Error('Failed to load PDF');
        }

        // Get the blob
        const blob = await response.blob();

        // Create object URL and open in new tab
        const pdfUrl = window.URL.createObjectURL(blob);
        window.open(pdfUrl, '_blank');

        // Note: We don't revoke the URL immediately because the new tab needs it
        // The browser will clean it up when the tab is closed
    } catch (error) {
        console.error('PDF open error:', error);
        alert(t('pdf_open_failed') || 'Failed to open PDF');
    }
}
