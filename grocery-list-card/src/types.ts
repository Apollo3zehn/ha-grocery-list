// Type definitions mirroring the backend WebSocket snapshot + model shapes
// (see custom_components/grocery_list/coordinator.py::snapshot and models.py).
// Keep these in sync with the Python `to_dict()` methods.

export enum QuantityUnitId {
  Pcs = "pcs",
  G = "g",
  Kg = "kg",
  Ml = "ml",
  L = "l",
  Pack = "pack",
  Bottle = "bottle",
  Can = "can",
  Bunch = "bunch",
}

export const DEFAULT_QUANTITY_UNIT = QuantityUnitId.Pcs;

export interface Quantity {
  value: number;
  unit: QuantityUnitId;
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
  id: QuantityUnitId;
  default: boolean;
  labels: Record<string, string>;
}

export interface GetUnitsResult {
  units: Unit[];
  default_unit: QuantityUnitId;
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
