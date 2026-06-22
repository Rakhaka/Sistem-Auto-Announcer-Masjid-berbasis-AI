const TOKEN_KEY = 'announcer_token';

function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
}

function clearToken() {
    localStorage.removeItem(TOKEN_KEY);
}

function isLoggedIn() {
    return !!getToken();
}

function logout() {
    clearToken();
    window.location.href = 'login.html';
}

async function login(username, password) {
    const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Login gagal');
    }
    const data = await res.json();
    setToken(data.token);
    return data;
}
