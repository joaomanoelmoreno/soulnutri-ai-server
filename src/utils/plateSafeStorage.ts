export type SafePlateItem = {
  id: string;
  name: string;
  category?: string;
  description?: string;
  ingredients?: string[];
  confidence?: number;
  [key: string]: any;
};

export type SafePlateState = {
  items: SafePlateItem[];
  updatedAt: number | null;
};

const STORAGE_KEY = "soulnutri_safe_plate";

export function getSafePlate(): SafePlateState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return { items: [], updatedAt: null };
    }

    const parsed = JSON.parse(raw);

    if (!parsed || !Array.isArray(parsed.items)) {
      return { items: [], updatedAt: null };
    }

    return {
      items: parsed.items,
      updatedAt: parsed.updatedAt ?? null,
    };
  } catch {
    return { items: [], updatedAt: null };
  }
}

export function saveSafePlate(plate: SafePlateState) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(plate));
  } catch {
    // não quebrar o fluxo principal
  }
}

export function addItemToSafePlate(item: SafePlateItem): SafePlateState {
  const current = getSafePlate();

  const next: SafePlateState = {
    items: [...current.items, item],
    updatedAt: Date.now(),
  };

  saveSafePlate(next);
  return next;
}

export function updateItemInSafePlate(
  itemId: string,
  updates: Partial<SafePlateItem>
): SafePlateState {
  const current = getSafePlate();

  const next: SafePlateState = {
    items: current.items.map((item) =>
      item.id === itemId ? { ...item, ...updates } : item
    ),
    updatedAt: Date.now(),
  };

  saveSafePlate(next);
  return next;
}

export function removeItemFromSafePlate(itemId: string): SafePlateState {
  const current = getSafePlate();

  const next: SafePlateState = {
    items: current.items.filter((item) => item.id !== itemId),
    updatedAt: Date.now(),
  };

  saveSafePlate(next);
  return next;
}

export function clearSafePlate() {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // ignorar
  }
}

export async function runNonBlocking<T>(
  task: () => Promise<T>
): Promise<{ ok: true; data: T } | { ok: false; error: unknown }> {
  try {
    const data = await task();
    return { ok: true, data };
  } catch (error) {
    return { ok: false, error };
  }
}
