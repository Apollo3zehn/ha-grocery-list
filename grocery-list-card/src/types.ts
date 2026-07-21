// Type definitions mirroring the backend WebSocket snapshot + model shapes
// (see custom_components/grocery_list/coordinator.py::snapshot and models.py).
// Keep these in sync with the Python `to_dict()` methods.

export interface Quantity {
  value: number;
  unit: string;
}

export interface Item {
  name: string;
  category: string | null;
  qty: Quantity | null;
  checked: boolean;
}

export interface ListSnapshot {
  slug: string;
  title: string;
  items: Item[];
  // Named categories in display order (uncategorized is rendered last and is
  // not included). Mirrors the backend GroceryList.ordered_categories().
  category_order: string[];
}

// A cleared item preserved in the browsable archive (see models.py::ArchivedItem).
export interface ArchivedItem {
  item: Item;
  archived_ts: string;
  reason: string;
}

// Full snapshot pushed on subscribe and on every change.
export interface Snapshot {
  identity: string;
  sync_state: SyncState;
  last_synced_commit: string | null;
  can_undo: boolean;
  can_redo: boolean;
  lists: ListSnapshot[];
  // Category names in use, derived from items and sorted alphabetically.
  categories: string[];
  // Per-slug archive of cleared items, newest-first.
  archives: Record<string, ArchivedItem[]>;
}

export type SyncState =
  | "synced"
  | "pending"
  | "syncing"
  | "offline"
  | "error"
  | "local";

export interface Unit {
  id: string;
  default: boolean;
  labels: Record<string, string>;
}

export interface GetUnitsResult {
  units: Unit[];
  default_unit: string;
}

// Lovelace card config (from the dashboard YAML/UI editor).
export interface GroceryCardConfig {
  type: string;
  entry_id: string;
  // Optional slug to pin the card to a single list; otherwise a switcher shows.
  slug?: string;
  title?: string;
}

// Minimal shape of the HA `hass` object we depend on.
export interface HomeAssistant {
  connection: {
    subscribeMessage: (
      callback: (msg: unknown) => void,
      subscribeMsg: Record<string, unknown>
    ) => Promise<() => Promise<void>>;
    sendMessagePromise: <T>(msg: Record<string, unknown>) => Promise<T>;
  };
  language?: string;
  locale?: { language: string };
}
