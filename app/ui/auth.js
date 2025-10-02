/**
 * Authentication utilities
 * Handles JWT token management and session verification
 */

/**
 * Get stored authentication token
 */
function getAuthToken() {
    return localStorage.getItem('auth_token');
}

/**
 * Get stored user information
 */
function getUserInfo() {
    const userInfo = localStorage.getItem('user_info');
    return userInfo ? JSON.parse(userInfo) : null;
}

/**
 * Check if user is authenticated
 */
function isAuthenticated() {
    return !!getAuthToken();
}

/**
 * Logout user
 */
async function logout() {
    const token = getAuthToken();
    
    if (token) {
        try {
            // Call logout API
            await fetch('/api/auth/logout', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
        } catch (error) {
            console.error('Logout API error:', error);
        }
    }
    
    // Clear local storage
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_info');
    
    // Redirect to login
    window.location.href = '/ui/login.html';
}

/**
 * Verify current session
 * Redirects to login if not authenticated
 */
async function verifySession() {
    const token = getAuthToken();
    
    if (!token) {
        redirectToLogin();
        return false;
    }
    
    try {
        const response = await fetch('/api/auth/verify', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Invalid token');
        }
        
        const data = await response.json();
        
        // Update user info
        if (data.user) {
            localStorage.setItem('user_info', JSON.stringify(data.user));
        }
        
        return true;
        
    } catch (error) {
        console.error('Session verification failed:', error);
        redirectToLogin();
        return false;
    }
}

/**
 * Redirect to login page
 */
function redirectToLogin() {
    // Don't redirect if already on login page
    if (!window.location.pathname.includes('login.html')) {
        window.location.href = '/ui/login.html';
    }
}

/**
 * Make authenticated API request
 */
async function authenticatedFetch(url, options = {}) {
    const token = getAuthToken();
    
    if (!token) {
        throw new Error('Not authenticated');
    }
    
    // Add Authorization header
    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };
    
    const response = await fetch(url, {
        ...options,
        headers
    });
    
    // Check if token expired
    if (response.status === 401) {
        console.warn('Token expired, redirecting to login');
        redirectToLogin();
        throw new Error('Authentication expired');
    }
    
    return response;
}

/**
 * Refresh authentication token
 */
async function refreshToken() {
    const token = getAuthToken();
    
    if (!token) {
        return false;
    }
    
    try {
        const response = await fetch('/api/auth/refresh', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Token refresh failed');
        }
        
        const data = await response.json();
        
        // Store new token
        localStorage.setItem('auth_token', data.access_token);
        localStorage.setItem('user_info', JSON.stringify(data.user));
        
        return true;
        
    } catch (error) {
        console.error('Token refresh error:', error);
        return false;
    }
}

/**
 * Display user info in header
 */
function displayUserInfo() {
    const userInfo = getUserInfo();
    
    if (!userInfo) {
        return;
    }
    
    // Find user info container
    const userInfoContainer = document.getElementById('userInfo');
    if (userInfoContainer) {
        userInfoContainer.innerHTML = `
            <div class="user-info">
                <span class="material-icons">account_circle</span>
                <span class="user-name">${userInfo.name || userInfo.email}</span>
                <span class="user-role">${userInfo.role}</span>
                <button onclick="logout()" class="btn-logout" title="${t('logout')}">
                    <span class="material-icons">logout</span>
                </button>
            </div>
        `;
    }
}

/**
 * Check user role
 */
function hasRole(requiredRole) {
    const userInfo = getUserInfo();
    
    if (!userInfo) {
        return false;
    }
    
    return userInfo.role === requiredRole;
}

/**
 * Check if user is admin
 */
function isAdmin() {
    return hasRole('Admin');
}

/**
 * Check if user is manager or admin
 */
function isManagerOrAdmin() {
    const userInfo = getUserInfo();
    
    if (!userInfo) {
        return false;
    }
    
    return userInfo.role === 'Admin' || userInfo.role === 'Gerente';
}

/**
 * Initialize authentication on page load
 */
document.addEventListener('DOMContentLoaded', async () => {
    // Skip auth check on login page
    if (window.location.pathname.includes('login.html')) {
        return;
    }
    
    // Verify session
    const isValid = await verifySession();
    
    if (isValid) {
        // Display user info
        displayUserInfo();
        
        // Set up token refresh (every 7 hours)
        setInterval(refreshToken, 7 * 60 * 60 * 1000);
    }
});

/**
 * Add logout button to header
 */
function addLogoutButton() {
    const header = document.querySelector('header');
    if (!header) return;
    
    const userInfo = getUserInfo();
    if (!userInfo) return;
    
    const logoutBtn = document.createElement('div');
    logoutBtn.className = 'user-menu';
    logoutBtn.innerHTML = `
        <span class="user-name">${userInfo.name || userInfo.email}</span>
        <span class="user-role">(${userInfo.role})</span>
        <button onclick="logout()" class="btn-logout">
            <span class="material-icons">logout</span>
            ${t('logout')}
        </button>
    `;
    
    header.appendChild(logoutBtn);
}

