const API_BASE = 'https://simulation-server-634070185639.us-central1.run.app';

// --- DATA: Human Readable Success Messages ---
const MESSAGES = {
    '/simulate/bug/attribute_error': {
        title: 'Shopping Cart Updated',
        msg: 'Success! Item "Banana" has been added to your cart.',
        icon: '🛒'
    },
    '/simulate/bug/name_error': {
        title: 'Profile Loaded',
        msg: 'Welcome back, Alice! Your profile data has been retrieved.',
        icon: '👤'
    },
    '/simulate/bug/value_error': {
        title: 'Payment Processed',
        msg: 'Payment of $50 has been successfully processed.',
        icon: '💳'
    },
    '/simulate/bug/file_not_found': {
        title: 'Configuration Valid',
        msg: 'System settings loaded successfully from config file.',
        icon: '⚙️'
    },
    '/simulate/bug/module_not_found': {
        title: 'Plugin Enabled',
        msg: 'PDF Export Plugin has been loaded and initialized.',
        icon: '🔌'
    },
    '/simulate/bug/unbound_local': {
        title: 'Counter Updated',
        msg: 'Visitor count incremented successfully.',
        icon: '🔢'
    },
    '/simulate/bug/json_decode': {
        title: 'Webhook Parsed',
        msg: 'Incoming webhook payload successfully decoded and processed.',
        icon: '📨'
    },
    '/simulate/bug/permission_error': {
        title: 'Access Granted',
        msg: 'Security audit log accessed successfully.',
        icon: '🔒'
    },
    '/simulate/division_by_zero': {
        title: 'Calculation Info',
        msg: 'Division operation completed (or crashed as expected).',
        icon: '➗'
    },
    '/simulate/unhandled/index_error': { title: 'Index Op', msg: 'List operation attempted.', icon: '📉' },
    '/simulate/unhandled/key_error': { title: 'Key Lookup', msg: 'Dictionary lookup attempted.', icon: '🔑' },
    '/simulate/unhandled/type_error': { title: 'Type Check', msg: 'Type operation attempted.', icon: '🔣' },
    '/simulate/unhandled/recursion_error': { title: 'Recursion Test', msg: 'Recursive depth test.', icon: '🔄' },
    '/simulate/unhandled/syntax_error': { title: 'Syntax Check', msg: 'Code evaluation attempted.', icon: '📝' },
    '/todos': {
        title: 'Task List Fetched',
        msg: 'Retrieved latest todo items from database.',
        icon: '📋'
    }
};

// --- DOM ELEMENTS ---
const statusBadge = document.getElementById('connection-status');
const logContainer = document.getElementById('log-container');
const modalOverlay = document.getElementById('result-modal');
const themeBtn = document.getElementById('theme-btn');

// --- THEME LOGIC ---
let isDark = false;
function toggleTheme() {
    isDark = !isDark;
    document.body.setAttribute('data-theme', isDark ? 'dark' : 'light');
    themeBtn.innerText = isDark ? '☀️ Light' : '🌙 Dark';
}

// --- API HANDLING ---
async function callApi(endpoint, method, label, payload = null, btnId = null) {
    const start = Date.now();
    log('info', `➡️ Sending ${method} request to ${endpoint}...`);

    const btn = btnId ? document.getElementById(btnId) : null;
    if (btn) btn.style.opacity = '0.7';

    try {
        const options = {
            method: method,
            headers: { 'Content-Type': 'application/json' }
        };
        if (payload) options.body = JSON.stringify(payload);

        const response = await fetch(`${API_BASE}${endpoint}`, options);
        const duration = Date.now() - start;

        let data;
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
            data = await response.json();
        } else {
            data = await response.text();
        }

        if (response.ok) {
            // SUCCESS
            log('success', `✅ ${label} Completed in ${duration}ms`);

            // Get custom message or default
            const custom = MESSAGES[endpoint] || { title: 'Success', msg: 'Operation completed successfully.', icon: '✅' };

            showModal(
                `${custom.icon} ${custom.title}`,
                custom.msg,
                JSON.stringify(data, null, 2),
                true
            );

            // Mark button as fixed
            if (btn) {
                btn.classList.remove('broken');
                btn.classList.add('fixed-success');
                const desc = btn.querySelector('.btn-desc');
                if (desc) desc.textContent = 'Active';
            }

        } else {
            // ERROR
            log('error', `🔥 ${label} Failed (${duration}ms)`);

            showModal(
                `❌ System Error: ${label}`,
                `The request failed with status ${response.status}. \nThis indicates a bug in the backend code for this feature.`,
                JSON.stringify(data, null, 2),
                false
            );
        }

    } catch (error) {
        log('error', `💥 connection_refused: ${error.message}`);
        showModal('💥 Network Error', 'Could not reach the backend server.', error.message, false);
    } finally {
        if (btn) btn.style.opacity = '1';
    }
}

// --- HEALTH CHECK ---
async function checkHealth() {
    try {
        const res = await fetch(`${API_BASE}/`);
        if (res.ok) {
            statusBadge.innerHTML = '<span class="dot"></span> Online';
            statusBadge.className = 'status-badge connected';
        } else { throw new Error('Failed'); }
    } catch (e) {
        statusBadge.innerHTML = '<span class="dot"></span> Offline';
        statusBadge.className = 'status-badge disconnected';
        log('system', `📡 Connecting to backend...`);
    }
}

// --- UI HELPERS ---
function showModal(title, message, code, isSuccess) {
    document.getElementById('modal-title').innerText = title;
    document.getElementById('modal-title').style.color = isSuccess ? 'var(--success)' : 'var(--danger)';

    document.getElementById('modal-body').innerText = message;
    document.getElementById('modal-code').innerText = code;

    modalOverlay.classList.add('active');
}

function closeModal() {
    modalOverlay.classList.remove('active');
}

modalOverlay.addEventListener('click', (e) => {
    if (e.target === modalOverlay) closeModal();
});

function log(type, message) {
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    const time = new Date().toLocaleTimeString('en-US', { hour12: false });

    entry.innerHTML = `
        <span class="log-time">${time}</span>
        <span class="log-msg">${message}</span>
    `;
    logContainer.prepend(entry);
}

function clearLog() {
    logContainer.innerHTML = '';
}

// Start
checkHealth();
setInterval(checkHealth, 30000);
