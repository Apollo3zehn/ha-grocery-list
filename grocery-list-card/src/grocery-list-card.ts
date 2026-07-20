import { LitElement, html, nothing, type TemplateResult } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import { GroceryApi } from "./api";
import { cardStyles } from "./styles";
import { makeT, resolveLang } from "./i18n";
import type {
  ArchivedItem,
  Category,
  GetUnitsResult,
  GroceryCardConfig,
  HomeAssistant,
  Item,
  ListSnapshot,
  Snapshot,
  Unit,
} from "./types";

// Sentinel key used to group items that have no category.
const NO_CAT = "__none__";

@customElement("grocery-list-card")
export class GroceryListCard extends LitElement {
  static styles = cardStyles;

  @property({ attribute: false }) hass!: HomeAssistant;

  @state() private _config?: GroceryCardConfig;
  @state() private _snapshot?: Snapshot;
  @state() private _units: Unit[] = [];
  @state() private _defaultUnit = "pcs";
  @state() private _activeSlug?: string;
  @state() private _editingId: string | null = null;
  @state() private _editValue = "";

  // New-item draft state (the add bar).
  @state() private _draftName = "";
  @state() private _draftQty = 1;
  @state() private _draftUnit = "";
  @state() private _draftCategory: string | null = null;

  // Category manager sheet state.
  @state() private _catManagerOpen = false;
  @state() private _archiveOpen = false;
  @state() private _newCatEn = "";
  @state() private _newCatDe = "";

  private _api?: GroceryApi;
  private _unsub?: () => Promise<void>;
  private _subscribedEntry?: string;

  setConfig(config: GroceryCardConfig): void {
    // Do NOT throw on a missing entry_id: the Lovelace card picker instantiates
    // the element to render a preview before any config exists, and throwing
    // aborts the custom-element upgrade ("Custom element not found"). Instead we
    // accept the config and render a friendly "needs configuration" state.
    const cfg: GroceryCardConfig =
      config ?? { type: "custom:grocery-list-card", entry_id: "" };
    this._config = cfg;
    if (cfg.slug) this._activeSlug = cfg.slug;
    // Re-subscribe if the entry changed.
    if (this._subscribedEntry && this._subscribedEntry !== cfg.entry_id) {
      this._teardown();
    }
    this._maybeSubscribe();
  }

  // Lovelace: provide the visual editor element.
  static getConfigElement(): HTMLElement {
    return document.createElement("grocery-list-card-editor");
  }

  // Lovelace: default config used for the picker preview + when the user first
  // adds the card. Auto-selects the first grocery_list config entry if present.
  static async getStubConfig(hass: HomeAssistant): Promise<GroceryCardConfig> {
    let entryId = "";
    try {
      const entries = await hass.connection.sendMessagePromise<
        Array<{ entry_id: string; domain: string }>
      >({ type: "config_entries/get", domain: "grocery_list" });
      const match = entries.find((e) => e.domain === "grocery_list");
      if (match) entryId = match.entry_id;
    } catch (_e) {
      // Fall back to an empty entry_id; the editor lets the user pick.
    }
    return { type: "custom:grocery-list-card", entry_id: entryId };
  }

  // HA calls this to size the card in masonry view.
  getCardSize(): number {
    const items = this._activeList()?.items.length ?? 0;
    return 2 + Math.ceil(items / 3);
  }

  connectedCallback(): void {
    super.connectedCallback();
    this._maybeSubscribe();
  }

  disconnectedCallback(): void {
    super.disconnectedCallback();
    this._teardown();
  }

  updated(changed: Map<string, unknown>): void {
    if (changed.has("hass")) this._maybeSubscribe();
  }

  private get _lang(): string {
    return resolveLang(this.hass?.locale?.language ?? this.hass?.language);
  }

  private async _maybeSubscribe(): Promise<void> {
    if (!this.hass || !this._config || !this._config.entry_id) return;
    if (this._subscribedEntry === this._config.entry_id) return;
    this._teardown();
    this._subscribedEntry = this._config.entry_id;
    this._api = new GroceryApi(this.hass, this._config.entry_id);
    try {
      const res: GetUnitsResult = await this._api.getUnits();
      this._units = res.units;
      this._defaultUnit = res.default_unit;
      if (!this._draftUnit) this._draftUnit = res.default_unit;
    } catch (_e) {
      // Units are non-critical; fall back to a bare default.
      this._units = [];
    }
    this._unsub = await this._api.subscribe((snap) => {
      this._snapshot = snap;
      if (!this._activeSlug && snap.lists.length) {
        this._activeSlug = snap.lists[0].slug;
      }
    }, this._lang);
  }

  private _teardown(): void {
    if (this._unsub) {
      void this._unsub();
      this._unsub = undefined;
    }
    this._subscribedEntry = undefined;
  }

  private _activeList(): ListSnapshot | undefined {
    const snap = this._snapshot;
    if (!snap) return undefined;
    return (
      snap.lists.find((l) => l.slug === this._activeSlug) ?? snap.lists[0]
    );
  }

  // ----- Rendering -------------------------------------------------------

  render() {
    const tt = makeT(this._lang);
    if (!this._config?.entry_id) {
      return html`<ha-card>
        <div class="gl-empty">
          <p><strong>${tt("needs_config")}</strong></p>
          <p>${tt("needs_config_hint")}</p>
        </div>
      </ha-card>`;
    }
    if (!this._snapshot) {
      return html`<ha-card><div class="gl-empty">\u2026</div></ha-card>`;
    }
    const t = makeT(this._lang);
    const list = this._activeList();
    return html`
      <ha-card>
        ${this._renderHeader(t)}
        ${this._snapshot.lists.length > 1 ? this._renderSwitcher() : nothing}
        ${this._renderAddBar(t)}
        ${list ? this._renderGroups(list, t) : nothing}
        ${this._renderFooter(t)}
      </ha-card>
      ${this._catManagerOpen ? this._renderCategoryManager(t) : nothing}
      ${this._archiveOpen ? this._renderArchive(t) : nothing}
    `;
  }

  private _renderHeader(t: (k: string) => string): TemplateResult {
    const snap = this._snapshot!;
    const list = this._activeList();
    const title = this._config?.title ?? list?.title ?? "Grocery";
    const st = snap.sync_state;
    return html`
      <div class="gl-header">
        <h2 class="gl-title">${title}</h2>
        <div class="gl-toolbar">
          <span class="gl-badge ${st}">${t("sync_" + st)}</span>
          <button
            class="gl-icon-btn"
            title=${t("undo")}
            ?disabled=${!snap.can_undo}
            @click=${() => this._api?.undo()}
          >\u21b6</button>
          <button
            class="gl-icon-btn"
            title=${t("redo")}
            ?disabled=${!snap.can_redo}
            @click=${() => this._api?.redo()}
          >\u21b7</button>
          <button
            class="gl-icon-btn"
            title=${t("sync")}
            @click=${() => this._api?.sync()}
          >\u21bb</button>
          <button
            class="gl-icon-btn"
            title=${t("view_archive")}
            @click=${() => (this._archiveOpen = true)}
          >\u{1F5C4}</button>
          <button
            class="gl-icon-btn"
            title=${t("manage_categories")}
            @click=${() => (this._catManagerOpen = true)}
          >\u2699</button>
        </div>
      </div>
    `;
  }

  private _renderSwitcher(): TemplateResult {
    const snap = this._snapshot!;
    return html`
      <div class="gl-switcher">
        ${snap.lists.map(
          (l) => html`
            <button
              class="gl-tab ${l.slug === this._activeSlug ? "active" : ""}"
              @click=${() => (this._activeSlug = l.slug)}
            >
              ${l.title}
            </button>
          `
        )}
      </div>
    `;
  }

  private _renderAddBar(t: (k: string) => string): TemplateResult {
    return html`
      <div class="gl-add">
        <input
          class="gl-name"
          .value=${this._draftName}
          placeholder=${t("add_placeholder")}
          @input=${(e: Event) =>
            (this._draftName = (e.target as HTMLInputElement).value)}
          @keydown=${(e: KeyboardEvent) => {
            if (e.key === "Enter") this._commitAdd();
          }}
        />
        <button class="gl-add-btn" @click=${() => this._commitAdd()}>
          ${t("add")}
        </button>
      </div>
      <div class="gl-qtyrow">
        <div class="gl-stepper">
          <button @click=${() => this._bumpQty(-1)}>\u2212</button>
          <input
            type="number"
            .value=${String(this._draftQty)}
            @input=${(e: Event) =>
              (this._draftQty =
                parseFloat((e.target as HTMLInputElement).value) || 0)}
          />
          <button @click=${() => this._bumpQty(1)}>+</button>
        </div>
        <select
          class="gl-unit"
          .value=${this._draftUnit}
          @change=${(e: Event) =>
            (this._draftUnit = (e.target as HTMLSelectElement).value)}
        >
          ${this._units.map(
            (u) => html`<option value=${u.id}>
              ${u.labels[this._lang] ?? u.labels.en ?? u.id}
            </option>`
          )}
        </select>
        <select
          class="gl-cat"
          .value=${this._draftCategory ?? NO_CAT}
          @change=${(e: Event) => {
            const v = (e.target as HTMLSelectElement).value;
            this._draftCategory = v === NO_CAT ? null : v;
          }}
        >
          <option value=${NO_CAT}>${t("uncategorized")}</option>
          ${this._categories().map(
            (c) => html`<option value=${c.id}>${this._catLabel(c)}</option>`
          )}
        </select>
      </div>
    `;
  }

  private _renderGroups(
    list: ListSnapshot,
    t: (k: string) => string
  ): TemplateResult {
    if (!list.items.length) {
      return html`<div class="gl-empty">${t("empty_list")}</div>`;
    }
    // Group by category, order groups by the category order, uncategorized last.
    const cats = this._categories();
    const order = new Map<string, number>();
    cats.forEach((c, i) => order.set(c.id, i));
    const groups = new Map<string, Item[]>();
    for (const it of list.items) {
      const key = it.category ?? NO_CAT;
      const arr = groups.get(key);
      if (arr) arr.push(it);
      else groups.set(key, [it]);
    }
    const keys = [...groups.keys()].sort((a, b) => {
      if (a === NO_CAT) return 1;
      if (b === NO_CAT) return -1;
      return (order.get(a) ?? 999) - (order.get(b) ?? 999);
    });
    return html`
      ${keys.map((key) => {
        const items = this._sortSunk(groups.get(key)!);
        const label =
          key === NO_CAT
            ? t("uncategorized")
            : this._snapshot!.category_labels[key] ?? key;
        return html`
          <div class="gl-group">
            <div class="gl-group-title">${label}</div>
            <ul class="gl-items">
              ${items.map((it) => this._renderItem(it, list.slug, t))}
            </ul>
          </div>
        `;
      })}
    `;
  }

  // Checked items sink to the bottom of their own category (PLAN requirement).
  private _sortSunk(items: Item[]): Item[] {
    return [...items].sort((a, b) => {
      if (a.checked !== b.checked) return a.checked ? 1 : -1;
      return a.created_ts.localeCompare(b.created_ts);
    });
  }

  private _renderItem(
    it: Item,
    slug: string,
    t: (k: string) => string
  ): TemplateResult {
    if (this._editingId === it.id) {
      return html`<li class="gl-item">${this._renderEdit(it, slug, t)}</li>`;
    }
    const qty = it.qty
      ? `${this._fmtNum(it.qty.value)} ${this._unitLabel(it.qty.unit)}`
      : "";
    return html`
      <li class="gl-item ${it.checked ? "checked" : ""}">
        <button
          class="gl-check ${it.checked ? "on" : ""}"
          @click=${() => this._api?.setChecked(slug, it.id, !it.checked)}
        >
          ${it.checked ? "\u2713" : ""}
        </button>
        <div
          class="gl-item-main"
          @click=${() => this._beginEdit(it)}
        >
          <div class="gl-item-name">${it.name}</div>
          ${qty ? html`<div class="gl-item-qty">${qty}</div>` : nothing}
        </div>
        <button
          class="gl-icon-btn"
          title=${t("delete")}
          @click=${() => this._api?.deleteItem(slug, it.id)}
        >\u2715</button>
      </li>
    `;
  }

  private _renderEdit(
    it: Item,
    slug: string,
    t: (k: string) => string
  ): TemplateResult {
    return html`
      <div class="gl-edit-row">
        <input
          .value=${this._editValue}
          @input=${(e: Event) =>
            (this._editValue = (e.target as HTMLInputElement).value)}
          @keydown=${(e: KeyboardEvent) => {
            if (e.key === "Enter") this._saveEdit(slug, it);
            if (e.key === "Escape") this._cancelEdit();
          }}
        />
        <button
          class="gl-icon-btn"
          title=${t("save")}
          @click=${() => this._saveEdit(slug, it)}
        >\u2713</button>
        <button
          class="gl-icon-btn"
          title=${t("cancel")}
          @click=${() => this._cancelEdit()}
        >\u2715</button>
      </div>
    `;
  }

  private _renderFooter(t: (k: string) => string): TemplateResult {
    const list = this._activeList();
    const hasChecked = !!list?.items.some((i) => i.checked);
    return html`
      <div class="gl-footer">
        <button
          class="gl-clear-btn"
          ?disabled=${!hasChecked}
          @click=${() => list && this._api?.clearChecked(list.slug)}
        >
          ${t("clear_checked")}
        </button>
      </div>
    `;
  }

  private _renderArchive(t: (k: string) => string): TemplateResult {
    const slug = this._activeSlug;
    const entries: ArchivedItem[] =
      (slug && this._snapshot?.archives?.[slug]) || [];
    return html`
      <div
        class="gl-overlay"
        @click=${(e: Event) => {
          if (e.target === e.currentTarget) this._archiveOpen = false;
        }}
      >
        <div class="gl-sheet">
          <div class="gl-sheet-header">
            <h3>${t("archive")}</h3>
            <button
              class="gl-icon-btn"
              title=${t("close")}
              @click=${() => (this._archiveOpen = false)}
            >\u2715</button>
          </div>

          ${entries.length
            ? html`<ul class="gl-archive-list">
                ${entries.map((a) => this._renderArchiveRow(a, t))}
              </ul>`
            : html`<div class="gl-empty">${t("no_archive")}</div>`}
        </div>
      </div>
    `;
  }

  private _renderArchiveRow(
    a: ArchivedItem,
    t: (k: string) => string
  ): TemplateResult {
    const qty = a.item.qty
      ? `${this._fmtNum(a.item.qty.value)} ${this._unitLabel(a.item.qty.unit)}`
      : "";
    return html`
      <li class="gl-archive-row">
        <span class="gl-archive-name">${a.item.name}</span>
        ${qty ? html`<span class="gl-archive-qty">${qty}</span>` : nothing}
        <span class="gl-archive-ts"
          >${t("archived_on")} ${this._fmtArchiveTs(a.archived_ts)}</span
        >
      </li>
    `;
  }

  private _fmtArchiveTs(ts: string): string {
    const d = new Date(ts);
    if (isNaN(d.getTime())) return ts;
    return d.toLocaleDateString(this._lang, {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  }

  private _renderCategoryManager(t: (k: string) => string): TemplateResult {
    const cats = this._categories();
    return html`
      <div
        class="gl-overlay"
        @click=${(e: Event) => {
          if (e.target === e.currentTarget) this._closeCatManager();
        }}
      >
        <div class="gl-sheet">
          <div class="gl-sheet-header">
            <h3>${t("categories")}</h3>
            <button
              class="gl-icon-btn"
              title=${t("close")}
              @click=${() => this._closeCatManager()}
            >\u2715</button>
          </div>

          ${cats.length
            ? html`<ul class="gl-catlist">
                ${cats.map((c, i) => this._renderCatRow(c, i, cats.length, t))}
              </ul>`
            : html`<div class="gl-empty">${t("no_categories")}</div>`}

          <div class="gl-cat-new">
            <input
              .value=${this._newCatEn}
              placeholder=${t("category_name_en")}
              @input=${(e: Event) =>
                (this._newCatEn = (e.target as HTMLInputElement).value)}
            />
            <input
              .value=${this._newCatDe}
              placeholder=${t("category_name_de")}
              @input=${(e: Event) =>
                (this._newCatDe = (e.target as HTMLInputElement).value)}
            />
            <button class="gl-add-btn" @click=${() => this._commitNewCategory()}>
              ${t("add_category")}
            </button>
          </div>
        </div>
      </div>
    `;
  }

  private _renderCatRow(
    c: Category,
    index: number,
    total: number,
    t: (k: string) => string
  ): TemplateResult {
    return html`
      <li class="gl-catrow">
        <span class="gl-lang-tag">EN</span>
        <input
          class="gl-cat-label"
          .value=${c.labels.en ?? ""}
          @change=${(e: Event) =>
            this._renameCategory(c, "en", (e.target as HTMLInputElement).value)}
        />
        <span class="gl-lang-tag">DE</span>
        <input
          class="gl-cat-label"
          .value=${c.labels.de ?? ""}
          @change=${(e: Event) =>
            this._renameCategory(c, "de", (e.target as HTMLInputElement).value)}
        />
        <button
          class="gl-icon-btn"
          title=${t("move_up")}
          ?disabled=${index === 0}
          @click=${() => this._moveCategory(index, -1)}
        >\u2191</button>
        <button
          class="gl-icon-btn"
          title=${t("move_down")}
          ?disabled=${index === total - 1}
          @click=${() => this._moveCategory(index, 1)}
        >\u2193</button>
        <button
          class="gl-icon-btn"
          title=${t("delete")}
          @click=${() => this._deleteCategory(c, t)}
        >\u2715</button>
      </li>
    `;
  }

  // ----- Helpers ---------------------------------------------------------

  private _categories(): Category[] {
    return this._snapshot?.categories ?? [];
  }

  private _catLabel(c: Category): string {
    return c.labels[this._lang] ?? c.labels.en ?? c.id;
  }

  private _unitLabel(id: string): string {
    const u = this._units.find((x) => x.id === id);
    if (!u) return id;
    return u.labels[this._lang] ?? u.labels.en ?? id;
  }

  private _fmtNum(n: number): string {
    return Number.isInteger(n) ? String(n) : n.toFixed(2).replace(/0+$/, "");
  }

  private _bumpQty(delta: number): void {
    this._draftQty = Math.max(0, Math.round((this._draftQty + delta) * 100) / 100);
  }

  private _beginEdit(it: Item): void {
    this._editingId = it.id;
    this._editValue = it.name;
  }

  private _cancelEdit(): void {
    this._editingId = null;
    this._editValue = "";
  }

  private _saveEdit(slug: string, it: Item): void {
    const name = this._editValue.trim();
    if (name && name !== it.name) {
      void this._api?.updateItem(slug, it.id, { name });
    }
    this._cancelEdit();
  }

  private _commitAdd(): void {
    const name = this._draftName.trim();
    const list = this._activeList();
    if (!name || !list || !this._api) return;
    void this._api.addItem(list.slug, name, {
      category: this._draftCategory,
      qty_value: this._draftQty || null,
      qty_unit: this._draftQty ? this._draftUnit || this._defaultUnit : null,
    });
    // Reset the name but keep qty/unit/category for fast repeated entry.
    this._draftName = "";
  }

  // ----- Category manager handlers --------------------------------------

  private _closeCatManager(): void {
    this._catManagerOpen = false;
    this._newCatEn = "";
    this._newCatDe = "";
  }

  private _commitNewCategory(): void {
    const en = this._newCatEn.trim();
    const de = this._newCatDe.trim();
    if (!en && !de) return;
    const labels: Record<string, string> = {};
    if (en) labels.en = en;
    if (de) labels.de = de;
    // Ensure at least an English label so the en-fallback always resolves.
    if (!labels.en) labels.en = de;
    void this._api?.createCategory(labels);
    this._newCatEn = "";
    this._newCatDe = "";
  }

  private _renameCategory(c: Category, lang: string, value: string): void {
    const next = value.trim();
    if (next === (c.labels[lang] ?? "")) return;
    const labels = { ...c.labels };
    if (next) labels[lang] = next;
    else delete labels[lang];
    // Never allow the English label to disappear (it is the fallback).
    if (!labels.en) labels.en = next || labels.de || c.id;
    void this._api?.updateCategory(c.id, { labels });
  }

  private _moveCategory(index: number, delta: number): void {
    const ids = this._categories().map((c) => c.id);
    const target = index + delta;
    if (target < 0 || target >= ids.length) return;
    [ids[index], ids[target]] = [ids[target], ids[index]];
    void this._api?.reorderCategories(ids);
  }

  private _deleteCategory(c: Category, t: (k: string) => string): void {
    if (!window.confirm(t("delete_category_confirm"))) return;
    void this._api?.deleteCategory(c.id);
  }
}

// Visual config editor for the card. Lets the user pick a Grocery List
// integration instance (config entry) from a dropdown instead of hunting for
// an entry_id, plus optional list slug and title.
@customElement("grocery-list-card-editor")
export class GroceryListCardEditor extends LitElement {
  @property({ attribute: false }) hass!: HomeAssistant;
  @state() private _config: GroceryCardConfig = {
    type: "custom:grocery-list-card",
    entry_id: "",
  };
  @state() private _entries: Array<{ entry_id: string; title: string }> = [];

  setConfig(config: GroceryCardConfig): void {
    this._config = config ?? {
      type: "custom:grocery-list-card",
      entry_id: "",
    };
  }

  connectedCallback(): void {
    super.connectedCallback();
    void this._loadEntries();
  }

  private async _loadEntries(): Promise<void> {
    if (!this.hass) return;
    try {
      const entries = await this.hass.connection.sendMessagePromise<
        Array<{ entry_id: string; domain: string; title: string }>
      >({ type: "config_entries/get", domain: "grocery_list" });
      this._entries = entries
        .filter((e) => e.domain === "grocery_list")
        .map((e) => ({ entry_id: e.entry_id, title: e.title }));
    } catch (_e) {
      this._entries = [];
    }
  }

  private get _lang(): string {
    return resolveLang(
      this.hass?.locale?.language ?? this.hass?.language
    );
  }

  private _emit(next: GroceryCardConfig): void {
    this._config = next;
    this.dispatchEvent(
      new CustomEvent("config-changed", {
        detail: { config: next },
        bubbles: true,
        composed: true,
      })
    );
  }

  render(): TemplateResult {
    const t = makeT(this._lang);
    return html`
      <div class="gl-editor">
        <label>${t("select_list_entry")}</label>
        ${this._entries.length
          ? html`<select
              .value=${this._config.entry_id}
              @change=${(e: Event) =>
                this._emit({
                  ...this._config,
                  entry_id: (e.target as HTMLSelectElement).value,
                })}
            >
              <option value="" ?selected=${!this._config.entry_id}></option>
              ${this._entries.map(
                (en) => html`<option
                  value=${en.entry_id}
                  ?selected=${en.entry_id === this._config.entry_id}
                >
                  ${en.title || en.entry_id}
                </option>`
              )}
            </select>`
          : html`<p>${t("no_entries")}</p>`}
        <label>${t("title")}</label>
        <input
          .value=${this._config.title ?? ""}
          @input=${(e: Event) => {
            const v = (e.target as HTMLInputElement).value;
            this._emit({ ...this._config, title: v || undefined });
          }}
        />
      </div>
    `;
  }
}

// Register the card in HA's picker.
(window as any).customCards = (window as any).customCards || [];
(window as any).customCards.push({
  type: "grocery-list-card",
  name: "Grocery List Card",
  description: "A slick, mobile-first grocery list with categories and sync.",
  preview: true,
  documentationURL:
    "https://codeberg.org/Apollo3zehn/ha-grocery-list",
});
