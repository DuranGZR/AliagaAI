export type DataStatus = "loading" | "ready" | "empty" | "error";

export type DataState<T> = {
  status: DataStatus;
  data: T;
  checkedAt?: string;
  errorMessage?: string;
};

type EmptyCheck<T> = (value: T) => boolean;

export function isEmptyValue<T>(value: T): boolean {
  if (Array.isArray(value)) return value.length === 0;
  return value == null;
}

function messageFromError(error: unknown): string {
  if (error instanceof Error && error.message) return error.message;
  return "Veri kaynagina ulasilamadi";
}

export async function loadDataState<T>(
  request: () => Promise<T>,
  fallback: T,
  isEmpty: EmptyCheck<T> = isEmptyValue
): Promise<DataState<T>> {
  try {
    const data = await request();
    return {
      status: isEmpty(data) ? "empty" : "ready",
      data,
      checkedAt: new Date().toISOString(),
    };
  } catch (error) {
    return {
      status: "error",
      data: fallback,
      checkedAt: new Date().toISOString(),
      errorMessage: messageFromError(error),
    };
  }
}

export function readyState<T>(data: T): DataState<T> {
  return {
    status: isEmptyValue(data) ? "empty" : "ready",
    data,
    checkedAt: new Date().toISOString(),
  };
}

export function formatCheckedAt(value?: string | null): string {
  if (!value) return "Kontrol bekleniyor";
  const date = new Date(value);
  if (!Number.isFinite(date.getTime())) return "Kontrol bekleniyor";
  return date.toLocaleString("tr-TR", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatFreshness(value?: string | null, staleHours = 24): string {
  if (!value) return "Guncelleme bekleniyor";
  const date = new Date(value);
  if (!Number.isFinite(date.getTime())) return "Guncelleme bekleniyor";
  const label = formatCheckedAt(value);
  const ageMs = Date.now() - date.getTime();
  return ageMs > staleHours * 60 * 60 * 1000 ? `Son veri ${label}` : `Guncel ${label}`;
}

export function isStale(value?: string | null, staleHours = 24): boolean {
  if (!value) return false;
  const date = new Date(value);
  if (!Number.isFinite(date.getTime())) return false;
  return Date.now() - date.getTime() > staleHours * 60 * 60 * 1000;
}

export function summarizeSources(states: Array<DataState<unknown>>): {
  ready: number;
  empty: number;
  error: number;
  total: number;
} {
  return states.reduce(
    (acc, item) => {
      acc.total += 1;
      if (item.status === "ready") acc.ready += 1;
      if (item.status === "empty") acc.empty += 1;
      if (item.status === "error") acc.error += 1;
      return acc;
    },
    { ready: 0, empty: 0, error: 0, total: 0 }
  );
}

