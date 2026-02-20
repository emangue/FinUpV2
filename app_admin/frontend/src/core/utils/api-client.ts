export async function fetchWithAuth(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const headers: HeadersInit = {
    ...(!(options.body instanceof FormData) && {
      "Content-Type": "application/json",
    }),
    ...options.headers,
  }

  let response: Response
  try {
    response = await fetch(url, {
      ...options,
      headers,
      credentials: "include",
    })
  } catch (err) {
    const msg =
      err instanceof TypeError && err.message === "Failed to fetch"
        ? "Backend inacessível. Verifique se está rodando em http://localhost:8000"
        : String(err)
    throw new Error(msg)
  }

  if (response.status === 401 && typeof window !== "undefined") {
    window.location.href = "/login"
  }

  return response
}

export async function fetchJsonWithAuth<T>(
  url: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetchWithAuth(url, options)
  if (!response.ok) {
    const text = await response.text()
    throw new Error(`HTTP ${response.status}: ${text}`)
  }
  return response.json()
}
