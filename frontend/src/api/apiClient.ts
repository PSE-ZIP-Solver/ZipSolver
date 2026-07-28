const API_BASE_URL =
    import.meta.env.VITE_API_URL ??
    "";

export async function apiFetch<T>(
    endpoint: string,
    options?: RequestInit,
): Promise<T> {
    const response = await fetch(
        `${API_BASE_URL}${endpoint}`,
        options,
    );

    if (!response.ok) {
        throw new Error(`API Error ${response.status}`);
    }

    return response.json();
}