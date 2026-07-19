// Minimal i18n for the card. English + German, matching the integration's
// supported locales. The active language is picked from `hass.locale.language`
// / `hass.language`, falling back to English.

type Dict = Record<string, string>;

const EN: Dict = {
  add_placeholder: "Add an item\u2026",
  add: "Add",
  qty: "Qty",
  unit: "Unit",
  category: "Category",
  uncategorized: "Uncategorized",
  clear_checked: "Clear checked",
  undo: "Undo",
  redo: "Redo",
  sync: "Sync",
  save: "Save",
  cancel: "Cancel",
  delete: "Delete",
  edit: "Edit",
  empty_list: "Nothing here yet. Add your first item above.",
  sync_synced: "Synced",
  sync_pending: "Pending",
  sync_syncing: "Syncing\u2026",
  sync_offline: "Offline",
  sync_error: "Sync error",
  manage_categories: "Manage categories",
  categories: "Categories",
  new_category: "New category",
  category_name_en: "Name (English)",
  category_name_de: "Name (German)",
  add_category: "Add category",
  no_categories: "No categories yet. Create one above.",
  move_up: "Move up",
  move_down: "Move down",
  close: "Close",
  delete_category_confirm: "Delete this category? Its items become uncategorized.",
  archive: "Archive",
  view_archive: "View archive",
  no_archive: "Nothing archived yet. Cleared items appear here.",
  archived_on: "Archived",
};

const DE: Dict = {
  add_placeholder: "Artikel hinzuf\u00fcgen\u2026",
  add: "Hinzuf\u00fcgen",
  qty: "Menge",
  unit: "Einheit",
  category: "Kategorie",
  uncategorized: "Ohne Kategorie",
  clear_checked: "Erledigte entfernen",
  undo: "R\u00fcckg\u00e4ngig",
  redo: "Wiederholen",
  sync: "Sync",
  save: "Speichern",
  cancel: "Abbrechen",
  delete: "L\u00f6schen",
  edit: "Bearbeiten",
  empty_list: "Noch nichts hier. F\u00fcge oben deinen ersten Artikel hinzu.",
  sync_synced: "Synchronisiert",
  sync_pending: "Ausstehend",
  sync_syncing: "Synchronisiere\u2026",
  sync_offline: "Offline",
  sync_error: "Sync-Fehler",
  manage_categories: "Kategorien verwalten",
  categories: "Kategorien",
  new_category: "Neue Kategorie",
  category_name_en: "Name (Englisch)",
  category_name_de: "Name (Deutsch)",
  add_category: "Kategorie hinzuf\u00fcgen",
  no_categories: "Noch keine Kategorien. Erstelle oben eine.",
  move_up: "Nach oben",
  move_down: "Nach unten",
  close: "Schlie\u00dfen",
  delete_category_confirm: "Diese Kategorie l\u00f6schen? Ihre Artikel werden dann ohne Kategorie angezeigt.",
};

const TABLES: Record<string, Dict> = { en: EN, de: DE };

export function resolveLang(raw: string | undefined): "en" | "de" {
  if (raw && raw.toLowerCase().startsWith("de")) return "de";
  return "en";
}

export function makeT(lang: string) {
  const table = TABLES[lang] ?? EN;
  return (key: string): string => table[key] ?? EN[key] ?? key;
}
