const API_BASE = '/api'
const PROSPECT_BASE = '/api/prospect'
const API_KEY = import.meta.env.VITE_API_KEY || 'dev-secret'

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(path, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-Api-Key': API_KEY,
      ...options.headers,
    },
  })
  if (!res.ok) {
    const error = await res.text()
    throw new Error(error || res.statusText)
  }
  return res.json()
}

export const api = {
  get: <T>(path: string) => request<T>(`${API_BASE}${path}`),
  post: <T>(path: string, body?: unknown) =>
    request<T>(`${API_BASE}${path}`, { method: 'POST', body: body ? JSON.stringify(body) : undefined }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(`${API_BASE}${path}`, { method: 'PATCH', body: body ? JSON.stringify(body) : undefined }),
  delete: <T>(path: string) => request<T>(`${API_BASE}${path}`, { method: 'DELETE' }),
  upload: async <T>(path: string, file: File): Promise<T> => {
    const formData = new FormData()
    formData.append('file', file)
    const res = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: { 'X-Api-Key': API_KEY },
      body: formData,
    })
    if (!res.ok) throw new Error(await res.text())
    return res.json()
  },
}

export const prospectApi = {
  get: <T>(path: string) => request<T>(`${PROSPECT_BASE}${path}`),
  post: <T>(path: string, body?: unknown) =>
    request<T>(`${PROSPECT_BASE}${path}`, { method: 'POST', body: body ? JSON.stringify(body) : undefined }),
}
