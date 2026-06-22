const CACHE_PREFIX = 'ann_cache_';

function getCacheKey(url) {
    const clean = url.split('?')[0];
    return CACHE_PREFIX + clean.replace(/[^a-z0-9]/gi, '_');
}

function getFromCache(url) {
    const key = getCacheKey(url);
    const raw = localStorage.getItem(key);
    if (!raw) return null;
    try {
        const entry = JSON.parse(raw);
        if (entry.expires > Date.now()) return entry.data;
    } catch {}
    return null;
}

function setCache(url, data, ttlMs) {
    const key = getCacheKey(url);
    const entry = { data, expires: Date.now() + ttlMs };
    localStorage.setItem(key, JSON.stringify(entry));
}

function invalidateCache(url) {
    const key = getCacheKey(url);
    localStorage.removeItem(key);
}

async function apiFetch(url, options = {}) {
    const token = getToken();
    const headers = options.headers || {};
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = headers['Content-Type'] || 'application/json';
    }
    const res = await fetch(url, { ...options, headers });
    if (res.status === 401) {
        clearToken();
        window.location.href = 'login.html';
        throw new Error('Unauthorized');
    }
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || 'Request gagal');
    }
    return res.json();
}

function apiGet(url) {
    return apiFetch(url);
}

function apiGetCached(url, ttlMs = 30000) {
    const cached = getFromCache(url);
    if (cached !== null) {
        return Promise.resolve(cached);
    }
    return apiFetch(url).then(data => {
        setCache(url, data, ttlMs);
        return data;
    });
}

function apiGetWithCacheRefresh(url, renderFn, ttlMs = 30000) {
    const cached = getFromCache(url);
    if (cached !== null) {
        renderFn(cached);
    }
    return apiFetch(url).then(data => {
        setCache(url, data, ttlMs);
        renderFn(data);
        return data;
    });
}

function apiPost(url, body) {
    const prefix = url.split('/').slice(0, -1).join('/');
    const patterns = ['/api/audio-list', '/api/schedules', '/api/logs', '/api/recent-logs'];
    patterns.forEach(p => invalidateCache(p));
    invalidateCache(prefix);
    return apiFetch(url, {
        method: 'POST',
        body: body instanceof FormData ? body : JSON.stringify(body),
    });
}

function apiPut(url, body) {
    const prefix = url.split('/').slice(0, -2).join('/');
    const patterns = ['/api/audio-list', '/api/schedules', '/api/logs'];
    patterns.forEach(p => invalidateCache(p));
    invalidateCache(prefix);
    return apiFetch(url, {
        method: 'PUT',
        body: JSON.stringify(body),
    });
}

function apiDelete(url) {
    const patterns = ['/api/audio-list', '/api/schedules', '/api/logs', '/api/recent-logs'];
    patterns.forEach(p => invalidateCache(p));
    return apiFetch(url, { method: 'DELETE' });
}

function uploadFile(url, file) {
    const token = getToken();
    const formData = new FormData();
    formData.append('file', file);
    invalidateCache('/api/audio-list');
    return fetch(url, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData,
    }).then(async res => {
        if (res.status === 401) { clearToken(); window.location.href = 'login.html'; }
        if (!res.ok) throw new Error((await res.json()).detail || 'Upload gagal');
        return res.json();
    });
}
