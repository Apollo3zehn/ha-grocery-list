// Thin wrapper around the HA WebSocket connection for the grocery_list domain.
// Every method maps 1:1 to a `grocery_list/*` command registered by the backend
// (see custom_components/grocery_list/websocket_api.py). The wrapper injects the
// `type` and `entry_id` so callers pass only the meaningful arguments.

import type {
  GetUnitsResult,
  HomeAssistant,
  Item,
  Snapshot,
} from "./types";

export class GroceryApi {
  constructor(
    private readonly hass: HomeAssistant,
    private readonly entryId: string
  ) {}

  // Subscribe to snapshots. The callback fires once immediately (initial
  // snapshot) and again on every change. Returns an unsubscribe function.
  async subscribe(
    onSnapshot: (snap: Snapshot) => void,
    locale = "en"
  ): Promise<() => Promise<void>> {
    return this.hass.connection.subscribeMessage(
      (msg) => onSnapshot(msg as Snapshot),
      {
        type: "grocery_list/subscribe",
        entry_id: this.entryId,
        locale,
      }
    );
  }

  private send<T>(type: string, extra: Record<string, unknown> = {}): Promise<T> {
    return this.hass.connection.sendMessagePromise<T>({
      type: `grocery_list/${type}`,
      entry_id: this.entryId,
      ...extra,
    });
  }

  addItem(
    slug: string,
    name: string,
    opts: { category?: string | null; qty_value?: number | null; qty_unit?: string | null } = {}
  ): Promise<{ item: Item }> {
    return this.send("add_item", { slug, name, ...opts });
  }

  updateItem(
    slug: string,
    itemId: string,
    changes: Partial<Pick<Item, "name" | "category">> & {
      qty_value?: number | null;
      qty_unit?: string | null;
    }
  ): Promise<{ item: Item }> {
    return this.send("update_item", { slug, item_id: itemId, ...changes });
  }

  setChecked(slug: string, itemId: string, checked: boolean): Promise<{ item: Item }> {
    return this.send("set_checked", { slug, item_id: itemId, checked });
  }

  deleteItem(slug: string, itemId: string): Promise<{ deleted: string }> {
    return this.send("delete_item", { slug, item_id: itemId });
  }

  clearChecked(slug: string): Promise<{ cleared: number }> {
    return this.send("clear_checked", { slug });
  }

  createList(
    title: string,
    slug?: string | null
  ): Promise<{ list: { slug: string; title: string } }> {
    return this.send("create_list", { title, slug: slug ?? null });
  }

  renameList(
    slug: string,
    title: string
  ): Promise<{ list: { slug: string; title: string } }> {
    return this.send("rename_list", { slug, title });
  }

  deleteList(slug: string): Promise<{ deleted: string }> {
    return this.send("delete_list", { slug });
  }

  createCategory(
    name: string,
    icon?: string | null
  ): Promise<{ category: unknown }> {
    return this.send("create_category", { name, icon });
  }

  updateCategory(
    catId: string,
    changes: { name?: string; icon?: string | null; order?: number }
  ): Promise<{ category: unknown }> {
    return this.send("update_category", { cat_id: catId, ...changes });
  }

  deleteCategory(catId: string): Promise<{ deleted: string }> {
    return this.send("delete_category", { cat_id: catId });
  }

  reorderCategories(orderedIds: string[]): Promise<{ ok: boolean }> {
    return this.send("reorder_categories", { ordered_ids: orderedIds });
  }

  undo(): Promise<{ undone: boolean }> {
    return this.send("undo");
  }

  redo(): Promise<{ redone: boolean }> {
    return this.send("redo");
  }

  sync(): Promise<{ sync_state: string }> {
    return this.send("sync");
  }

  // Global (no entry_id needed) — but harmless to include; backend ignores it.
  getUnits(): Promise<GetUnitsResult> {
    return this.hass.connection.sendMessagePromise<GetUnitsResult>({
      type: "grocery_list/get_units",
    });
  }
}
