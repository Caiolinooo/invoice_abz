/**
 * Invoice History JavaScript
 */

let currentPage = 0;
const pageSize = 20;
let currentFilters = {};

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
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
        const response = await fetch('/api/invoices/stats');
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

        const response = await fetch(`/api/invoices?${params}`);
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

        // Get translated status
        const getStatusText = (status) => {
            if (typeof t === 'function') {
                return t(status) || capitalizeFirst(status);
            }
            return capitalizeFirst(status);
        };

        // Build file links with better styling
        const buildFileLinks = () => {
            const links = [];

            // XLSX download and view buttons
            if (invoice.file_path_xlsx) {
                const excelTitle = typeof t === 'function' ? t('download_excel') : 'Download Excel';
                const viewTitle = typeof t === 'function' ? t('view_details') : 'View Details';
                links.push(`<a href="/api/invoices/${invoice.id}/download" title="${excelTitle}" class="file-link excel-link">
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
                links.push(`<a href="/api/invoices/${invoice.id}/pdf" target="_blank" title="${pdfTitle}" class="file-link pdf-link">
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

        const response = await fetch(`/api/invoices/${invoiceId}/status`, {
            method: 'PUT',
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

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
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
        const response = await fetch(`/api/invoices/${invoiceId}/view`);
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
            <div style="padding: 1.5rem 2rem; background: #f9fafb; border-top: 1px solid #e5e7eb; display: flex; gap: 1rem; justify-content: flex-end; border-radius: 0 0 1rem 1rem;">
                ${invoice.file_exists ? `<a href="/api/invoices/${invoiceId}/download" class="btn btn-primary" style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 0.5rem; font-weight: 600; transition: all 0.2s;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(102, 126, 234, 0.4)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
                    <span class="material-icons" style="font-size: 18px;">download</span>
                    ${t('download_excel')}
                </a>` : `<span style="color: #9ca3af;">${t('file_not_available')}</span>`}
                <button onclick="this.closest('.modal').remove()" class="btn btn-secondary" style="padding: 0.75rem 1.5rem; background: white; color: #374151; border: 1px solid #d1d5db; border-radius: 0.5rem; font-weight: 600; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.background='#f3f4f6'" onmouseout="this.style.background='white'">${t('close')}</button>
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

// Regenerate PDF for pending invoice
async function regeneratePDF(invoiceId) {
    if (!confirm(t('confirm_regenerate_pdf') || 'Regenerate PDF for this invoice?')) {
        return;
    }

    try {
        showInfo(t('regenerating_pdf') || 'Regenerating PDF...');

        const response = await fetch(`/api/invoices/${invoiceId}/regenerate-pdf`, {
            method: 'POST'
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
