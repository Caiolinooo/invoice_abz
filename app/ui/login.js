/**
 * Login page functionality
 */

// Check if already logged in
document.addEventListener('DOMContentLoaded', () => {
    // Check if user is already authenticated
    const token = localStorage.getItem('auth_token');
    if (token) {
        // Verify token is still valid
        verifyToken(token).then(valid => {
            if (valid) {
                // Redirect to main page
                window.location.href = '/ui/history.html';
            }
        });
    }
    
    // Apply translations
    if (typeof applyTranslations === 'function') {
        applyTranslations();
    }
});

/**
 * Handle login form submission
 */
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const loginButton = document.getElementById('loginButton');
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    
    // Disable button and show loading
    loginButton.disabled = true;
    loginButton.innerHTML = `
        <span class="loading-spinner"></span>
        <span>${t('logging_in')}</span>
    `;
    
    // Hide previous errors
    errorMessage.classList.remove('show');
    
    try {
        // Call login API
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || t('login_failed'));
        }
        
        // Store token and user info
        localStorage.setItem('auth_token', data.access_token);
        localStorage.setItem('user_info', JSON.stringify(data.user));
        
        // Show success message
        showSuccess(t('login_success'));
        
        // Redirect to main page after short delay
        setTimeout(() => {
            window.location.href = '/ui/history.html';
        }, 500);
        
    } catch (error) {
        console.error('Login error:', error);
        
        // Show error message
        errorText.textContent = error.message;
        errorMessage.classList.add('show');
        
        // Re-enable button
        loginButton.disabled = false;
        loginButton.innerHTML = `
            <span class="material-icons">login</span>
            <span>${t('login_button')}</span>
        `;
    }
}

/**
 * Verify if token is still valid
 */
async function verifyToken(token) {
    try {
        const response = await fetch('/api/auth/verify', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        return response.ok;
    } catch (error) {
        console.error('Token verification error:', error);
        return false;
    }
}

/**
 * Show success message (temporary)
 */
function showSuccess(message) {
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    
    errorMessage.style.background = '#d1fae5';
    errorMessage.style.color = '#065f46';
    errorText.textContent = message;
    errorMessage.classList.add('show');
}

/**
 * Change language
 */
function changeLanguage(lang) {
    if (typeof setLanguage === 'function') {
        setLanguage(lang);
        applyTranslations();
    }
}

// Initialize language selector
document.addEventListener('DOMContentLoaded', () => {
    const languageSelect = document.getElementById('languageSelect');
    const currentLang = getCurrentLanguage();
    languageSelect.value = currentLang;
});

