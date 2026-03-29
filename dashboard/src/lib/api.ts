export function getApiBase(): string {
  return (process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000").replace(
    /\/$/,
    "",
  );
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public body?: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function parseJsonSafe(res: Response): Promise<unknown> {
  const text = await res.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export async function apiFetch<T = unknown>(
  path: string,
  token: string,
  init?: RequestInit,
): Promise<T> {
  const url = `${getApiBase()}${path.startsWith("/") ? path : `/${path}`}`;
  const headers = new Headers(init?.headers);
  headers.set("Authorization", `Bearer ${token}`);
  if (!headers.has("Content-Type") && init?.body != null) {
    headers.set("Content-Type", "application/json");
  }
  const res = await fetch(url, { ...init, headers });
  const data = await parseJsonSafe(res);
  if (!res.ok) {
    let detail: string;
    if (typeof data === "object" && data !== null && "detail" in data) {
      const raw = (data as { detail: unknown }).detail;
      if (typeof raw === "string") {
        detail = raw;
      } else if (Array.isArray(raw)) {
        detail = raw
          .map((e: { msg?: string }) => e.msg ?? JSON.stringify(e))
          .join("; ");
      } else {
        detail = JSON.stringify(raw);
      }
    } else if (typeof data === "string") {
      detail = data;
    } else {
      detail = res.statusText;
    }
    throw new ApiError(detail || "Request failed", res.status, JSON.stringify(data));
  }
  return data as T;
}
