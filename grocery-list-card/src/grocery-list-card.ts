import { LitElement, html, nothing, type TemplateResult } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import { GroceryApi } from "./api";
import { cardStyles } from "./styles";
import { makeT, resolveLang } from "./i18n";
import type {
  ArchivedItem,
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
// Sentinel value for the "create a new category" option in the dropdowns.
const NEW_CAT = "__new__";

// Composite identity key for an item: mirrors the backend identity_key
// (category, name) -> `${category ?? ""}|${name}`.
function itemKey(it: { category: string | null; name: string }): string {
  return `${it.category ?? ""}|${it.name}`;
}

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
  @state() private _editQty = 0;
  @state() private _editUnit = "";
  @state() private _editCategory: string | null = null;

  // Category names created via the "new category" prompt this session. The
  // backend derives categories from items, so a freshly-typed category has no
  // item yet and would otherwise not appear as a selectable option until an
  // item using it is persisted. We merge these into the option list so the
  // selection sticks immediately.
  @state() private _extraCategories: string[] = [];

  // New-item draft state (the add bar).
  @state() private _draftName = "";
  @state() private _draftQty = 1;
  @state() private _draftUnit = "";
  @state() private _draftCategory: string | null = null;

  // Settings sheet state (lists manager).
  @state() private _settingsOpen = false;
  @state() private _archiveOpen = false;

  // In-card modal dialog (replaces native window.prompt/confirm so the UX is
  // consistent, themable, and works inside the HA frontend). Exactly one
  // dialog is shown at a time; the pending promise resolves on confirm/cancel.
  @state() private _dialog?: {
    kind: "prompt" | "confirm";
    title: string;
    message?: string;
    placeholder?: string;
    confirmLabel: string;
    cancelLabel: string;
    danger?: boolean;
    resolve: (value: string | null | boolean) => void;
  };
  @state() private _dialogValue = "";

  // New-list draft (within the settings sheet).
  @state() private _newListName = "";

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

  // Slug to target for new items. Falls back to the configured slug (or
  // "default") when no list exists yet, so the first add creates the list
  // on the backend via _ensure_list.
  private _targetSlug(): string {
    return (
      this._activeList()?.slug ??
      this._activeSlug ??
      this._config?.slug ??
      "default"
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
        ${list ? html`<div class="gl-scroll">${this._renderGroups(list, t)}</div>` : nothing}
        ${this._renderFooter(t)}
      </ha-card>
      ${this._settingsOpen ? this._renderSettings(t) : nothing}
      ${this._archiveOpen ? this._renderArchive(t) : nothing}
      ${this._dialog ? this._renderDialog() : nothing}
    `;
  }

  private _renderHeader(t: (k: string) => string): TemplateResult {
    const snap = this._snapshot!;
    const list = this._activeList();
    const title = this._config?.title ?? list?.title ?? "Grocery";
    const st = snap.sync_state;
    // The sync badge and manual-sync button are only meaningful when this
    // instance is backed by a git remote. In local-only mode the backend
    // reports sync_state === "local"; hide the git UI entirely in that case.
    const gitConfigured = st !== "local";
    return html`
      <div class="gl-header">
        <h2 class="gl-title">${title}</h2>
        <div class="gl-toolbar">
          ${gitConfigured
            ? html`<span class="gl-badge ${st}"
                >${t("git_prefix")}: ${t("sync_" + st)}</span
              >`
            : nothing}
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
          ${gitConfigured
            ? html`<button
                class="gl-icon-btn"
                title=${t("sync")}
                @click=${() => this._api?.sync()}
              >\u21bb</button>`
            : nothing}
          <button
            class="gl-icon-btn"
            title=${t("view_archive")}
            @click=${() => (this._archiveOpen = true)}
          >
            <svg
              viewBox="0 0 24 24"
              width="20"
              height="20"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <path d="M3 7h18v3H3z" />
              <path d="M5 10v9h14v-9" />
              <path d="M10 13h4" />
            </svg>
          </button>
          <button
            class="gl-icon-btn"
            title=${t("settings")}
            @click=${() => (this._settingsOpen = true)}
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
          @change=${async (e: Event) => {
            const sel = e.target as HTMLSelectElement;
            const v = sel.value;
            if (v === NEW_CAT) {
              // Revert the visible selection until the dialog resolves.
              sel.value = this._draftCategory ?? NO_CAT;
              const name = await this._promptNewCategory(t);
              if (name) this._draftCategory = name;
            } else {
              this._draftCategory = v === NO_CAT ? null : v;
            }
          }}
        >
          <option value=${NO_CAT} ?selected=${this._draftCategory == null}>
            ${t("uncategorized")}
          </option>
          ${this._categories().map(
            (c) => html`<option value=${c} ?selected=${this._draftCategory === c}>
              ${c}
            </option>`
          )}
          <option value=${NEW_CAT}>${t("new_category")}…</option>
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
    // Split unchecked (active shopping) from checked (done). Checked items move
    // to a dedicated section at the very end of the card, themselves grouped by
    // category, so the active list stays focused on what's still needed.
    const unchecked = list.items.filter((i) => !i.checked);
    const checked = list.items.filter((i) => i.checked);
    return html`
      ${this._renderCategoryGroups(unchecked, list, t)}
      ${
        checked.length
          ? html`<div class="gl-checked-section">
              <div class="gl-checked-divider">${t("checked_section")}</div>
              ${this._renderCategoryGroups(checked, list, t)}
            </div>`
          : nothing
      }
    `;
  }

  // Render a set of items grouped by category name. Categories follow the
  // list's saved display order (``category_order``); any category not present
  // in that order is appended alphabetically, and uncategorized is always last.
  // Used for both the active and checked sections.
  private _renderCategoryGroups(
    items: Item[],
    list: ListSnapshot,
    t: (k: string) => string
  ): TemplateResult {
    if (!items.length) return html``;
    const slug = list.slug;
    const groups = new Map<string, Item[]>();
    for (const it of items) {
      const key = it.category ?? NO_CAT;
      const arr = groups.get(key);
      if (arr) arr.push(it);
      else groups.set(key, [it]);
    }
    const order = list.category_order ?? [];
    const rank = new Map<string, number>();
    order.forEach((c, i) => rank.set(c, i));
    const keys = [...groups.keys()].sort((a, b) => {
      if (a === NO_CAT) return 1;
      if (b === NO_CAT) return -1;
      const ra = rank.has(a) ? rank.get(a)! : Infinity;
      const rb = rank.has(b) ? rank.get(b)! : Infinity;
      if (ra !== rb) return ra - rb;
      return a.localeCompare(b);
    });
    return html`
      ${keys.map((key) => {
        const groupItems = [...groups.get(key)!].sort((a, b) =>
          a.name.localeCompare(b.name)
        );
        const label = key === NO_CAT ? t("uncategorized") : key;
        return html`
          <div class="gl-group">
            <div class="gl-group-title">${label}</div>
            <ul class="gl-items">
              ${groupItems.map((it) => this._renderItem(it, slug, t))}
            </ul>
          </div>
        `;
      })}
    `;
  }

  private _renderItem(
    it: Item,
    slug: string,
    t: (k: string) => string
  ): TemplateResult {
    if (this._editingId === itemKey(it)) {
      return html`<li class="gl-item">${this._renderEdit(it, slug, t)}</li>`;
    }
    const qty = it.qty
      ? `${this._fmtNum(it.qty.value)} ${this._unitLabel(it.qty.unit)}`
      : "";
    return html`
      <li class="gl-item ${it.checked ? "checked" : ""}">
        <button
          class="gl-check ${it.checked ? "on" : ""}"
          @click=${() => this._api?.setChecked(slug, it.category, it.name, !it.checked)}
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
          @click=${() => this._api?.deleteItem(slug, it.category, it.name)}
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
      <div class="gl-edit">
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
        <div class="gl-qtyrow">
          <div class="gl-stepper">
            <button @click=${() => this._bumpEditQty(-1)}>\u2212</button>
            <input
              type="number"
              .value=${String(this._editQty)}
              @input=${(e: Event) =>
                (this._editQty =
                  parseFloat((e.target as HTMLInputElement).value) || 0)}
            />
            <button @click=${() => this._bumpEditQty(1)}>+</button>
          </div>
          <select
            class="gl-unit"
            .value=${this._editUnit}
            @change=${(e: Event) =>
              (this._editUnit = (e.target as HTMLSelectElement).value)}
          >
            ${this._units.map(
              (u) => html`<option value=${u.id}>
                ${u.labels[this._lang] ?? u.labels.en ?? u.id}
              </option>`
            )}
          </select>
          <select
            class="gl-cat"
            @change=${async (e: Event) => {
              const sel = e.target as HTMLSelectElement;
              const v = sel.value;
              if (v === NEW_CAT) {
                // Revert the visible selection until the dialog resolves.
                sel.value = this._editCategory ?? NO_CAT;
                const name = await this._promptNewCategory(t);
                if (name) this._editCategory = name;
              } else {
                this._editCategory = v === NO_CAT ? null : v;
              }
            }}
          >
            <option value=${NO_CAT} ?selected=${this._editCategory == null}>
              ${t("uncategorized")}
            </option>
            ${this._categories().map(
              (c) => html`<option value=${c} ?selected=${this._editCategory === c}>
                ${c}
              </option>`
            )}
            <option value=${NEW_CAT}>${t("new_category")}…</option>
          </select>
        </div>
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
          @click=${() => this._clearCheckedConfirm(t)}
        >
          ${t("clear_checked")}
        </button>
      </div>
    `;
  }

  private async _clearCheckedConfirm(t: (k: string) => string): Promise<void> {
    const list = this._activeList();
    if (!list) return;
    const ok = await this._showConfirm({
      title: t("clear_checked"),
      message: t("clear_checked_confirm"),
      confirmLabel: t("delete"),
      cancelLabel: t("cancel"),
      danger: true,
    });
    if (!ok) return;
    void this._api?.clearChecked(list.slug);
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
        <button
          class="gl-icon-btn"
          title=${t("restore")}
          @click=${() => this._restoreArchived(a)}
        >\u21a9</button>
      </li>
    `;
  }

  private _restoreArchived(a: ArchivedItem): void {
    const slug = this._activeSlug;
    if (!slug) return;
    void this._api?.restoreArchived(slug, a.item.category, a.item.name);
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

  private _renderSettings(t: (k: string) => string): TemplateResult {
    const lists = this._snapshot?.lists ?? [];
    const activeList = this._activeList();
    const catOrder = activeList?.category_order ?? [];
    return html`
      <div
        class="gl-overlay"
        @click=${(e: Event) => {
          if (e.target === e.currentTarget) this._closeSettings();
        }}
      >
        <div class="gl-sheet">
          <div class="gl-sheet-header">
            <h3>${t("settings")}</h3>
            <button
              class="gl-icon-btn"
              title=${t("close")}
              @click=${() => this._closeSettings()}
            >\u2715</button>
          </div>

          <div class="gl-settings-section">
            <div class="gl-section-title">${t("lists")}</div>
            ${lists.length
              ? html`<ul class="gl-catlist">
                  ${lists.map((l) => this._renderListRow(l, lists.length, t))}
                </ul>`
              : html`<div class="gl-empty">${t("no_lists")}</div>`}
            <div class="gl-cat-new">
              <input
                .value=${this._newListName}
                placeholder=${t("list_name")}
                @input=${(e: Event) =>
                  (this._newListName = (e.target as HTMLInputElement).value)}
                @keydown=${(e: KeyboardEvent) => {
                  if (e.key === "Enter") this._commitNewList();
                }}
              />
              <button class="gl-add-btn" @click=${() => this._commitNewList()}>
                ${t("add_list")}
              </button>
            </div>
          </div>

          <div class="gl-settings-section">
            <div class="gl-section-title">
              ${t("categories")}${activeList
                ? html` — <span class="gl-section-title-list"
                    >${activeList.title}</span
                  >`
                : ""}
            </div>
            ${activeList && catOrder.length
              ? html`<ul class="gl-catlist">
                  ${catOrder.map((c, i) =>
                    this._renderCategoryRow(
                      activeList.slug,
                      c,
                      i,
                      catOrder.length,
                      t
                    )
                  )}
                </ul>`
              : html`<div class="gl-empty">${t("no_categories")}</div>`}
          </div>
        </div>
      </div>
    `;
  }

  private _renderCategoryRow(
    slug: string,
    name: string,
    index: number,
    total: number,
    t: (k: string) => string
  ): TemplateResult {
    return html`
      <li class="gl-catrow">
        <span class="gl-cat-label" style="flex:1">${name}</span>
        <button
          class="gl-icon-btn"
          title=${t("move_up")}
          ?disabled=${index <= 0}
          @click=${() => this._moveCategory(slug, index, -1)}
        >\u2191</button>
        <button
          class="gl-icon-btn"
          title=${t("move_down")}
          ?disabled=${index >= total - 1}
          @click=${() => this._moveCategory(slug, index, 1)}
        >\u2193</button>
        <button
          class="gl-icon-btn"
          title=${t("rename_category")}
          @click=${() => this._renameCategoryPrompt(slug, name, t)}
        >\u270e</button>
      </li>
    `;
  }

  private async _renameCategoryPrompt(
    slug: string,
    name: string,
    t: (k: string) => string
  ): Promise<void> {
    const next = await this._showPrompt({
      title: t("rename_category"),
      message: t("rename_category_prompt"),
      initial: name,
      confirmLabel: t("save"),
      cancelLabel: t("cancel"),
    });
    if (next === null) return;
    const newName = next.trim();
    if (!newName || newName === name) return;
    void this._api?.renameCategory(slug, name, newName);
  }

  // Swap the category at `index` with its neighbor (`delta` = -1 up, +1 down)
  // and persist the new order. The backend pushes a fresh snapshot which
  // re-renders both this list and the grouped items.
  private _moveCategory(slug: string, index: number, delta: number): void {
    const order = [...(this._activeList()?.category_order ?? [])];
    const target = index + delta;
    if (index < 0 || index >= order.length) return;
    if (target < 0 || target >= order.length) return;
    [order[index], order[target]] = [order[target], order[index]];
    void this._api?.reorderCategories(slug, order);
  }

  private _renderListRow(
    l: ListSnapshot,
    total: number,
    t: (k: string) => string
  ): TemplateResult {
    return html`
      <li class="gl-catrow">
        <span class="gl-cat-label" style="flex:1">${l.title}</span>
        <button
          class="gl-icon-btn"
          title=${t("rename_list")}
          @click=${() => this._renameListPrompt(l, t)}
        >\u270e</button>
        <button
          class="gl-icon-btn"
          title=${t("delete_list")}
          ?disabled=${total <= 1}
          @click=${() => this._deleteListConfirm(l, t)}
        >\u2715</button>
      </li>
    `;
  }

  // ----- Helpers ---------------------------------------------------------

  private _categories(): string[] {
    const set = new Set<string>(this._snapshot?.categories ?? []);
    for (const c of this._extraCategories) set.add(c);
    return [...set].sort((a, b) => a.localeCompare(b));
  }

  // Remember a newly-typed category so it becomes a selectable option.
  private _registerCategory(name: string): void {
    if (!this._extraCategories.includes(name)) {
      this._extraCategories = [...this._extraCategories, name];
    }
  }

  // Prompt for a new category name (inline creation from the dropdowns) via the
  // in-card dialog. Returns the trimmed name, or null if cancelled/empty. A
  // successful result is registered so it appears as a selectable option.
  private async _promptNewCategory(
    t: (k: string) => string
  ): Promise<string | null> {
    const name = await this._showPrompt({
      title: t("new_category"),
      placeholder: t("category_name"),
      confirmLabel: t("save"),
      cancelLabel: t("cancel"),
    });
    if (name) this._registerCategory(name);
    return name;
  }

  // ----- In-card dialog (prompt / confirm) ------------------------------

  // Show a text-prompt dialog. Resolves to the trimmed string, or null if the
  // user cancels or submits an empty value.
  private _showPrompt(opts: {
    title: string;
    message?: string;
    placeholder?: string;
    initial?: string;
    confirmLabel: string;
    cancelLabel: string;
  }): Promise<string | null> {
    this._dialogValue = opts.initial ?? "";
    return new Promise<string | null>((resolve) => {
      this._dialog = {
        kind: "prompt",
        title: opts.title,
        message: opts.message,
        placeholder: opts.placeholder,
        confirmLabel: opts.confirmLabel,
        cancelLabel: opts.cancelLabel,
        resolve: (v) => resolve(typeof v === "string" ? v : null),
      };
    });
  }

  // Show a confirm dialog. Resolves true on confirm, false on cancel.
  private _showConfirm(opts: {
    title: string;
    message?: string;
    confirmLabel: string;
    cancelLabel: string;
    danger?: boolean;
  }): Promise<boolean> {
    return new Promise<boolean>((resolve) => {
      this._dialog = {
        kind: "confirm",
        title: opts.title,
        message: opts.message,
        confirmLabel: opts.confirmLabel,
        cancelLabel: opts.cancelLabel,
        danger: opts.danger,
        resolve: (v) => resolve(v === true),
      };
    });
  }

  private _dialogConfirm(): void {
    const d = this._dialog;
    if (!d) return;
    this._dialog = undefined;
    if (d.kind === "prompt") {
      const name = this._dialogValue.trim();
      d.resolve(name || null);
    } else {
      d.resolve(true);
    }
  }

  private _dialogCancel(): void {
    const d = this._dialog;
    if (!d) return;
    this._dialog = undefined;
    d.resolve(d.kind === "prompt" ? null : false);
  }

  private _renderDialog(): TemplateResult {
    const d = this._dialog!;
    return html`
      <div
        class="gl-overlay"
        @click=${(e: Event) => {
          if (e.target === e.currentTarget) this._dialogCancel();
        }}
      >
        <div
          class="gl-dialog"
          role="dialog"
          aria-modal="true"
          @keydown=${(e: KeyboardEvent) => {
            if (e.key === "Escape") this._dialogCancel();
            if (e.key === "Enter" && d.kind === "prompt")
              this._dialogConfirm();
          }}
        >
          <h3 class="gl-dialog-title">${d.title}</h3>
          ${d.message
            ? html`<p class="gl-dialog-msg">${d.message}</p>`
            : nothing}
          ${d.kind === "prompt"
            ? html`<input
                class="gl-dialog-input"
                .value=${this._dialogValue}
                placeholder=${d.placeholder ?? ""}
                @input=${(e: Event) =>
                  (this._dialogValue = (e.target as HTMLInputElement).value)}
                autofocus
              />`
            : nothing}
          <div class="gl-dialog-actions">
            <button
              class="gl-btn gl-btn-text"
              @click=${() => this._dialogCancel()}
            >
              ${d.cancelLabel}
            </button>
            <button
              class="gl-btn ${d.danger ? "gl-btn-danger" : "gl-btn-primary"}"
              @click=${() => this._dialogConfirm()}
            >
              ${d.confirmLabel}
            </button>
          </div>
        </div>
      </div>
    `;
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
    this._editingId = itemKey(it);
    this._editValue = it.name;
    this._editQty = it.qty?.value ?? 0;
    this._editUnit = it.qty?.unit ?? this._defaultUnit;
    this._editCategory = it.category;
  }

  private _cancelEdit(): void {
    this._editingId = null;
    this._editValue = "";
    this._editQty = 0;
    this._editUnit = "";
    this._editCategory = null;
  }

  private _bumpEditQty(delta: number): void {
    this._editQty = Math.max(0, Math.round((this._editQty + delta) * 100) / 100);
  }

  private _saveEdit(slug: string, it: Item): void {
    const name = this._editValue.trim();
    if (!name || !this._api) {
      this._cancelEdit();
      return;
    }
    const changes: {
      new_name?: string;
      new_category?: string | null;
      qty_value?: number | null;
      qty_unit?: string | null;
    } = {};
    if (name !== it.name) changes.new_name = name;
    if (this._editCategory !== it.category)
      changes.new_category = this._editCategory;
    const newQty = this._editQty || null;
    const oldQty = it.qty?.value ?? null;
    const newUnit = newQty ? this._editUnit || this._defaultUnit : null;
    const oldUnit = it.qty?.unit ?? null;
    if (newQty !== oldQty || newUnit !== oldUnit) {
      changes.qty_value = newQty;
      changes.qty_unit = newUnit;
    }
    if (Object.keys(changes).length) {
      void this._api.updateItem(slug, it.category, it.name, changes);
    }
    this._cancelEdit();
  }

  private _commitAdd(): void {
    const name = this._draftName.trim();
    if (!name || !this._api) return;
    const slug = this._targetSlug();
    void this._api.addItem(slug, name, {
      category: this._draftCategory,
      qty_value: this._draftQty || null,
      qty_unit: this._draftQty ? this._draftUnit || this._defaultUnit : null,
    });
    // Ensure the newly-created list becomes the active one.
    this._activeSlug = slug;
    // Reset the name but keep qty/unit/category for fast repeated entry.
    this._draftName = "";
  }

  // ----- Settings / list handlers ---------------------------------------

  private _closeSettings(): void {
    this._settingsOpen = false;
    this._newListName = "";
  }

  private async _commitNewList(): Promise<void> {
    const title = this._newListName.trim();
    if (!title || !this._api) return;
    this._newListName = "";
    try {
      const res = await this._api.createList(title);
      // Switch to the newly-created list.
      if (res?.list?.slug) this._activeSlug = res.list.slug;
    } catch (_e) {
      // Backend surfaces errors via the snapshot/sync badge; ignore here.
    }
  }

  private async _renameListPrompt(
    l: ListSnapshot,
    t: (k: string) => string
  ): Promise<void> {
    const next = await this._showPrompt({
      title: t("rename_list"),
      message: t("rename_list_prompt"),
      initial: l.title,
      confirmLabel: t("save"),
      cancelLabel: t("cancel"),
    });
    if (next === null) return;
    const title = next.trim();
    if (!title || title === l.title) return;
    void this._api?.renameList(l.slug, title);
  }

  private async _deleteListConfirm(
    l: ListSnapshot,
    t: (k: string) => string
  ): Promise<void> {
    const ok = await this._showConfirm({
      title: t("delete_list"),
      message: t("delete_list_confirm"),
      confirmLabel: t("delete"),
      cancelLabel: t("cancel"),
      danger: true,
    });
    if (!ok) return;
    void this._api?.deleteList(l.slug);
    // If we deleted the active list, fall back to the first remaining one.
    if (this._activeSlug === l.slug) {
      const remaining = (this._snapshot?.lists ?? []).filter(
        (x) => x.slug !== l.slug
      );
      this._activeSlug = remaining[0]?.slug;
    }
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

// Register the card in HA's picker. The picker runs before `hass` is available,
// so localize the name/description from the browser language (native first,
// English fallback).
const PICKER_I18N: Record<string, { name: string; description: string }> = {
  en: {
    name: "Grocery List Card",
    description: "A slick, mobile-first grocery list with categories and sync.",
  },
  de: {
    name: "Einkaufslisten-Karte",
    description:
      "Eine schicke, mobil-optimierte Einkaufsliste mit Kategorien und Sync.",
  },
};
const pickerLang = resolveLang(
  typeof navigator !== "undefined" ? navigator.language : undefined
);
const pickerText = PICKER_I18N[pickerLang] ?? PICKER_I18N.en;
(window as any).customCards = (window as any).customCards || [];
(window as any).customCards.push({
  type: "grocery-list-card",
  name: pickerText.name,
  description: pickerText.description,
  preview: true,
  documentationURL:
    "https://codeberg.org/Apollo3zehn/ha-grocery-list",
});
