function e(e,t,i,n){var r,s=arguments.length,a=s<3?t:null===n?n=Object.getOwnPropertyDescriptor(t,i):n;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)a=Reflect.decorate(e,t,i,n);else for(var o=e.length-1;o>=0;o--)(r=e[o])&&(a=(s<3?r(a):s>3?r(t,i,a):r(t,i))||a);return s>3&&a&&Object.defineProperty(t,i,a),a}"function"==typeof SuppressedError&&SuppressedError;const t=globalThis,i=t.ShadowRoot&&(void 0===t.ShadyCSS||t.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,n=Symbol(),r=new WeakMap;let s=class{constructor(e,t,i){if(this._$cssResult$=!0,i!==n)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o;const t=this.t;if(i&&void 0===e){const i=void 0!==t&&1===t.length;i&&(e=r.get(t)),void 0===e&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),i&&r.set(t,e))}return e}toString(){return this.cssText}};const a=i?e=>e:e=>e instanceof CSSStyleSheet?(e=>{let t="";for(const i of e.cssRules)t+=i.cssText;return(e=>new s("string"==typeof e?e:e+"",void 0,n))(t)})(e):e,{is:o,defineProperty:l,getOwnPropertyDescriptor:c,getOwnPropertyNames:d,getOwnPropertySymbols:g,getPrototypeOf:h}=Object,p=globalThis,u=p.trustedTypes,_=u?u.emptyScript:"",m=p.reactiveElementPolyfillSupport,y=(e,t)=>e,v={toAttribute(e,t){switch(t){case Boolean:e=e?_:null;break;case Object:case Array:e=null==e?e:JSON.stringify(e)}return e},fromAttribute(e,t){let i=e;switch(t){case Boolean:i=null!==e;break;case Number:i=null===e?null:Number(e);break;case Object:case Array:try{i=JSON.parse(e)}catch(e){i=null}}return i}},f=(e,t)=>!o(e,t),b={attribute:!0,type:String,converter:v,reflect:!1,useDefault:!1,hasChanged:f};Symbol.metadata??=Symbol("metadata"),p.litPropertyMetadata??=new WeakMap;let $=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=b){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){const i=Symbol(),n=this.getPropertyDescriptor(e,i,t);void 0!==n&&l(this.prototype,e,n)}}static getPropertyDescriptor(e,t,i){const{get:n,set:r}=c(this.prototype,e)??{get(){return this[t]},set(e){this[t]=e}};return{get:n,set(t){const s=n?.call(this);r?.call(this,t),this.requestUpdate(e,s,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??b}static _$Ei(){if(this.hasOwnProperty(y("elementProperties")))return;const e=h(this);e.finalize(),void 0!==e.l&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(y("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(y("properties"))){const e=this.properties,t=[...d(e),...g(e)];for(const i of t)this.createProperty(i,e[i])}const e=this[Symbol.metadata];if(null!==e){const t=litPropertyMetadata.get(e);if(void 0!==t)for(const[e,i]of t)this.elementProperties.set(e,i)}this._$Eh=new Map;for(const[e,t]of this.elementProperties){const i=this._$Eu(e,t);void 0!==i&&this._$Eh.set(i,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){const t=[];if(Array.isArray(e)){const i=new Set(e.flat(1/0).reverse());for(const e of i)t.unshift(a(e))}else void 0!==e&&t.push(a(e));return t}static _$Eu(e,t){const i=t.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof e?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),void 0!==this.renderRoot&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){const e=new Map,t=this.constructor.elementProperties;for(const i of t.keys())this.hasOwnProperty(i)&&(e.set(i,this[i]),delete this[i]);e.size>0&&(this._$Ep=e)}createRenderRoot(){const e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return((e,n)=>{if(i)e.adoptedStyleSheets=n.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(const i of n){const n=document.createElement("style"),r=t.litNonce;void 0!==r&&n.setAttribute("nonce",r),n.textContent=i.cssText,e.appendChild(n)}})(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,i){this._$AK(e,i)}_$ET(e,t){const i=this.constructor.elementProperties.get(e),n=this.constructor._$Eu(e,i);if(void 0!==n&&!0===i.reflect){const r=(void 0!==i.converter?.toAttribute?i.converter:v).toAttribute(t,i.type);this._$Em=e,null==r?this.removeAttribute(n):this.setAttribute(n,r),this._$Em=null}}_$AK(e,t){const i=this.constructor,n=i._$Eh.get(e);if(void 0!==n&&this._$Em!==n){const e=i.getPropertyOptions(n),r="function"==typeof e.converter?{fromAttribute:e.converter}:void 0!==e.converter?.fromAttribute?e.converter:v;this._$Em=n;const s=r.fromAttribute(t,e.type);this[n]=s??this._$Ej?.get(n)??s,this._$Em=null}}requestUpdate(e,t,i,n=!1,r){if(void 0!==e){const s=this.constructor;if(!1===n&&(r=this[e]),i??=s.getPropertyOptions(e),!((i.hasChanged??f)(r,t)||i.useDefault&&i.reflect&&r===this._$Ej?.get(e)&&!this.hasAttribute(s._$Eu(e,i))))return;this.C(e,t,i)}!1===this.isUpdatePending&&(this._$ES=this._$EP())}C(e,t,{useDefault:i,reflect:n,wrapped:r},s){i&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,s??t??this[e]),!0!==r||void 0!==s)||(this._$AL.has(e)||(this.hasUpdated||i||(t=void 0),this._$AL.set(e,t)),!0===n&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}const e=this.scheduleUpdate();return null!=e&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[e,t]of this._$Ep)this[e]=t;this._$Ep=void 0}const e=this.constructor.elementProperties;if(e.size>0)for(const[t,i]of e){const{wrapped:e}=i,n=this[t];!0!==e||this._$AL.has(t)||void 0===n||this.C(t,void 0,i,n)}}let e=!1;const t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(e=>e.hostUpdate?.()),this.update(t)):this._$EM()}catch(t){throw e=!1,this._$EM(),t}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(e){}firstUpdated(e){}};$.elementStyles=[],$.shadowRootOptions={mode:"open"},$[y("elementProperties")]=new Map,$[y("finalized")]=new Map,m?.({ReactiveElement:$}),(p.reactiveElementVersions??=[]).push("2.1.2");const w=globalThis,k=e=>e,x=w.trustedTypes,A=x?x.createPolicy("lit-html",{createHTML:e=>e}):void 0,S="$lit$",z=`lit$${Math.random().toFixed(9).slice(2)}$`,C="?"+z,E=`<${C}>`,L=document,N=()=>L.createComment(""),j=e=>null===e||"object"!=typeof e&&"function"!=typeof e,U=Array.isArray,P="[ \t\n\f\r]",R=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,M=/-->/g,q=/>/g,O=RegExp(`>|${P}(?:([^\\s"'>=/]+)(${P}*=${P}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),I=/'/g,Q=/"/g,T=/^(?:script|style|textarea|title)$/i,D=(e=>(t,...i)=>({_$litType$:e,strings:t,values:i}))(1),V=Symbol.for("lit-noChange"),H=Symbol.for("lit-nothing"),B=new WeakMap,G=L.createTreeWalker(L,129);function K(e,t){if(!U(e)||!e.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==A?A.createHTML(t):t}const W=(e,t)=>{const i=e.length-1,n=[];let r,s=2===t?"<svg>":3===t?"<math>":"",a=R;for(let t=0;t<i;t++){const i=e[t];let o,l,c=-1,d=0;for(;d<i.length&&(a.lastIndex=d,l=a.exec(i),null!==l);)d=a.lastIndex,a===R?"!--"===l[1]?a=M:void 0!==l[1]?a=q:void 0!==l[2]?(T.test(l[2])&&(r=RegExp("</"+l[2],"g")),a=O):void 0!==l[3]&&(a=O):a===O?">"===l[0]?(a=r??R,c=-1):void 0===l[1]?c=-2:(c=a.lastIndex-l[2].length,o=l[1],a=void 0===l[3]?O:'"'===l[3]?Q:I):a===Q||a===I?a=O:a===M||a===q?a=R:(a=O,r=void 0);const g=a===O&&e[t+1].startsWith("/>")?" ":"";s+=a===R?i+E:c>=0?(n.push(o),i.slice(0,c)+S+i.slice(c)+z+g):i+z+(-2===c?t:g)}return[K(e,s+(e[i]||"<?>")+(2===t?"</svg>":3===t?"</math>":"")),n]};class F{constructor({strings:e,_$litType$:t},i){let n;this.parts=[];let r=0,s=0;const a=e.length-1,o=this.parts,[l,c]=W(e,t);if(this.el=F.createElement(l,i),G.currentNode=this.el.content,2===t||3===t){const e=this.el.content.firstChild;e.replaceWith(...e.childNodes)}for(;null!==(n=G.nextNode())&&o.length<a;){if(1===n.nodeType){if(n.hasAttributes())for(const e of n.getAttributeNames())if(e.endsWith(S)){const t=c[s++],i=n.getAttribute(e).split(z),a=/([.?@])?(.*)/.exec(t);o.push({type:1,index:r,name:a[2],strings:i,ctor:"."===a[1]?ee:"?"===a[1]?te:"@"===a[1]?ie:X}),n.removeAttribute(e)}else e.startsWith(z)&&(o.push({type:6,index:r}),n.removeAttribute(e));if(T.test(n.tagName)){const e=n.textContent.split(z),t=e.length-1;if(t>0){n.textContent=x?x.emptyScript:"";for(let i=0;i<t;i++)n.append(e[i],N()),G.nextNode(),o.push({type:2,index:++r});n.append(e[t],N())}}}else if(8===n.nodeType)if(n.data===C)o.push({type:2,index:r});else{let e=-1;for(;-1!==(e=n.data.indexOf(z,e+1));)o.push({type:7,index:r}),e+=z.length-1}r++}}static createElement(e,t){const i=L.createElement("template");return i.innerHTML=e,i}}function Z(e,t,i=e,n){if(t===V)return t;let r=void 0!==n?i._$Co?.[n]:i._$Cl;const s=j(t)?void 0:t._$litDirective$;return r?.constructor!==s&&(r?._$AO?.(!1),void 0===s?r=void 0:(r=new s(e),r._$AT(e,i,n)),void 0!==n?(i._$Co??=[])[n]=r:i._$Cl=r),void 0!==r&&(t=Z(e,r._$AS(e,t.values),r,n)),t}class Y{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){const{el:{content:t},parts:i}=this._$AD,n=(e?.creationScope??L).importNode(t,!0);G.currentNode=n;let r=G.nextNode(),s=0,a=0,o=i[0];for(;void 0!==o;){if(s===o.index){let t;2===o.type?t=new J(r,r.nextSibling,this,e):1===o.type?t=new o.ctor(r,o.name,o.strings,this,e):6===o.type&&(t=new ne(r,this,e)),this._$AV.push(t),o=i[++a]}s!==o?.index&&(r=G.nextNode(),s++)}return G.currentNode=L,n}p(e){let t=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(e,i,t),t+=i.strings.length-2):i._$AI(e[t])),t++}}class J{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,i,n){this.type=2,this._$AH=H,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=i,this.options=n,this._$Cv=n?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode;const t=this._$AM;return void 0!==t&&11===e?.nodeType&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=Z(this,e,t),j(e)?e===H||null==e||""===e?(this._$AH!==H&&this._$AR(),this._$AH=H):e!==this._$AH&&e!==V&&this._(e):void 0!==e._$litType$?this.$(e):void 0!==e.nodeType?this.T(e):(e=>U(e)||"function"==typeof e?.[Symbol.iterator])(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==H&&j(this._$AH)?this._$AA.nextSibling.data=e:this.T(L.createTextNode(e)),this._$AH=e}$(e){const{values:t,_$litType$:i}=e,n="number"==typeof i?this._$AC(e):(void 0===i.el&&(i.el=F.createElement(K(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===n)this._$AH.p(t);else{const e=new Y(n,this),i=e.u(this.options);e.p(t),this.T(i),this._$AH=e}}_$AC(e){let t=B.get(e.strings);return void 0===t&&B.set(e.strings,t=new F(e)),t}k(e){U(this._$AH)||(this._$AH=[],this._$AR());const t=this._$AH;let i,n=0;for(const r of e)n===t.length?t.push(i=new J(this.O(N()),this.O(N()),this,this.options)):i=t[n],i._$AI(r),n++;n<t.length&&(this._$AR(i&&i._$AB.nextSibling,n),t.length=n)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){const t=k(e).nextSibling;k(e).remove(),e=t}}setConnected(e){void 0===this._$AM&&(this._$Cv=e,this._$AP?.(e))}}class X{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,i,n,r){this.type=1,this._$AH=H,this._$AN=void 0,this.element=e,this.name=t,this._$AM=n,this.options=r,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=H}_$AI(e,t=this,i,n){const r=this.strings;let s=!1;if(void 0===r)e=Z(this,e,t,0),s=!j(e)||e!==this._$AH&&e!==V,s&&(this._$AH=e);else{const n=e;let a,o;for(e=r[0],a=0;a<r.length-1;a++)o=Z(this,n[i+a],t,a),o===V&&(o=this._$AH[a]),s||=!j(o)||o!==this._$AH[a],o===H?e=H:e!==H&&(e+=(o??"")+r[a+1]),this._$AH[a]=o}s&&!n&&this.j(e)}j(e){e===H?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}}class ee extends X{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===H?void 0:e}}class te extends X{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==H)}}class ie extends X{constructor(e,t,i,n,r){super(e,t,i,n,r),this.type=5}_$AI(e,t=this){if((e=Z(this,e,t,0)??H)===V)return;const i=this._$AH,n=e===H&&i!==H||e.capture!==i.capture||e.once!==i.once||e.passive!==i.passive,r=e!==H&&(i===H||n);n&&this.element.removeEventListener(this.name,this,i),r&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}}class ne{constructor(e,t,i){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(e){Z(this,e)}}const re=w.litHtmlPolyfillSupport;re?.(F,J),(w.litHtmlVersions??=[]).push("3.3.3");const se=globalThis;class ae extends ${constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){const t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=((e,t,i)=>{const n=i?.renderBefore??t;let r=n._$litPart$;if(void 0===r){const e=i?.renderBefore??null;n._$litPart$=r=new J(t.insertBefore(N(),e),e,void 0,i??{})}return r._$AI(e),r})(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return V}}ae._$litElement$=!0,ae.finalized=!0,se.litElementHydrateSupport?.({LitElement:ae});const oe=se.litElementPolyfillSupport;oe?.({LitElement:ae}),(se.litElementVersions??=[]).push("4.2.2");const le=e=>(t,i)=>{void 0!==i?i.addInitializer(()=>{customElements.define(e,t)}):customElements.define(e,t)},ce={attribute:!0,type:String,converter:v,reflect:!1,hasChanged:f},de=(e=ce,t,i)=>{const{kind:n,metadata:r}=i;let s=globalThis.litPropertyMetadata.get(r);if(void 0===s&&globalThis.litPropertyMetadata.set(r,s=new Map),"setter"===n&&((e=Object.create(e)).wrapped=!0),s.set(i.name,e),"accessor"===n){const{name:n}=i;return{set(i){const r=t.get.call(this);t.set.call(this,i),this.requestUpdate(n,r,e,!0,i)},init(t){return void 0!==t&&this.C(n,void 0,e,t),t}}}if("setter"===n){const{name:n}=i;return function(i){const r=this[n];t.call(this,i),this.requestUpdate(n,r,e,!0,i)}}throw Error("Unsupported decorator location: "+n)};function ge(e){return(t,i)=>"object"==typeof i?de(e,t,i):((e,t,i)=>{const n=t.hasOwnProperty(i);return t.constructor.createProperty(i,e),n?Object.getOwnPropertyDescriptor(t,i):void 0})(e,t,i)}function he(e){return ge({...e,state:!0,attribute:!1})}class pe{constructor(e,t){this.hass=e,this.entryId=t}async subscribe(e,t="en"){return this.hass.connection.subscribeMessage(t=>e(t),{type:"grocery_list/subscribe",entry_id:this.entryId,locale:t})}send(e,t={}){return this.hass.connection.sendMessagePromise({type:`grocery_list/${e}`,entry_id:this.entryId,...t})}addItem(e,t,i={}){return this.send("add_item",{slug:e,name:t,...i})}updateItem(e,t,i,n){return this.send("update_item",{slug:e,category:t,name:i,...n})}setChecked(e,t,i,n){return this.send("set_checked",{slug:e,category:t,name:i,checked:n})}deleteItem(e,t,i){return this.send("delete_item",{slug:e,category:t,name:i})}clearChecked(e){return this.send("clear_checked",{slug:e})}restoreArchived(e,t,i){return this.send("restore_archived",{slug:e,category:t,name:i})}createList(e,t){return this.send("create_list",{title:e,slug:t??null})}renameList(e,t){return this.send("rename_list",{slug:e,title:t})}deleteList(e){return this.send("delete_list",{slug:e})}reorderCategories(e,t){return this.send("reorder_categories",{slug:e,order:t})}renameCategory(e,t,i){return this.send("rename_category",{slug:e,old:t,new:i})}undo(){return this.send("undo")}redo(){return this.send("redo")}sync(){return this.send("sync")}getUnits(){return this.hass.connection.sendMessagePromise({type:"grocery_list/get_units"})}}const ue=((e,...t)=>{const i=1===e.length?e[0]:t.reduce((t,i,n)=>t+(e=>{if(!0===e._$cssResult$)return e.cssText;if("number"==typeof e)return e;throw Error("Value passed to 'css' function must be a 'css' function result: "+e+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+e[n+1],e[0]);return new s(i,e,n)})`
  :host {
    --gl-gap: 8px;
    --gl-radius: 14px;
    --gl-accent: var(--primary-color, #03a9f4);
    --gl-text: var(--primary-text-color, #212121);
    --gl-muted: var(--secondary-text-color, #727272);
    --gl-divider: var(--divider-color, #e0e0e0);
    --gl-card-bg: var(--card-background-color, #fff);
    display: block;
  }

  ha-card {
    display: flex;
    flex-direction: column;
    gap: var(--gl-gap);
    padding: 12px;
    color: var(--gl-text);
  }

  .gl-header {
    display: flex;
    align-items: center;
    gap: var(--gl-gap);
    justify-content: space-between;
  }

  .gl-title {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0;
    flex: 1 1 auto;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .gl-toolbar {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .gl-badge {
    font-size: 0.72rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 999px;
    color: #fff;
    white-space: nowrap;
  }
  .gl-badge.synced { background: var(--success-color, #4caf50); }
  .gl-badge.pending { background: var(--warning-color, #ff9800); }
  .gl-badge.syncing { background: var(--info-color, #039be5); }
  .gl-badge.offline { background: var(--gl-muted); }
  .gl-badge.error { background: var(--error-color, #f44336); }

  .gl-icon-btn {
    border: none;
    background: transparent;
    color: var(--gl-text);
    width: 38px;
    height: 38px;
    border-radius: 50%;
    font-size: 1.1rem;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }
  .gl-icon-btn:hover { background: rgba(127,127,127,0.12); }
  .gl-icon-btn:disabled { opacity: 0.35; cursor: default; }
  .gl-icon-btn:disabled:hover { background: transparent; }

  .gl-switcher {
    display: flex;
    gap: 4px;
    overflow-x: auto;
    scrollbar-width: none;
  }
  .gl-switcher::-webkit-scrollbar { display: none; }
  .gl-tab {
    border: 1px solid var(--gl-divider);
    background: transparent;
    color: var(--gl-muted);
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.85rem;
    white-space: nowrap;
    cursor: pointer;
  }
  .gl-tab.active {
    background: var(--gl-accent);
    border-color: var(--gl-accent);
    color: #fff;
  }

  .gl-add-fab {
    position: fixed;
    right: 24px;
    bottom: 24px;
    z-index: 4;
    width: 56px;
    height: 56px;
    border: none;
    border-radius: 50%;
    background: var(--gl-accent);
    color: #fff;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.28);
    cursor: pointer;
    font-size: 2rem;
    line-height: 1;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }
  .gl-add-fab:hover { filter: brightness(1.05); }
  .gl-add-backdrop {
    position: fixed;
    inset: 0;
    z-index: 5;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    padding: 16px;
    background: rgba(0, 0, 0, 0.35);
    box-sizing: border-box;
  }
  .gl-add-dialog {
    width: min(460px, 100%);
    max-width: 460px;
    padding: 16px;
    border-radius: calc(var(--gl-radius) + 4px);
    background: var(--gl-card-bg);
    color: var(--gl-text);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.32);
    box-sizing: border-box;
  }
  .gl-add-dialog .gl-dialog-title {
    font-size: 1.05rem;
    font-weight: 700;
    margin-bottom: 12px;
  }
  .gl-add-form {
    display: flex;
    flex-direction: column;
    gap: var(--gl-gap);
  }
  .gl-add-form input.gl-name {
    flex: 1 1 auto;
    min-width: 0;
    border: 1px solid var(--gl-divider);
    border-radius: var(--gl-radius);
    padding: 10px 12px;
    font-size: 1rem;
    background: var(--gl-card-bg);
    color: var(--gl-text);
  }
  .gl-add-actions {
    display: flex;
    justify-content: flex-end;
    gap: var(--gl-gap);
    margin-top: 14px;
  }
  .gl-text-btn,
  .gl-primary-btn {
    border: none;
    border-radius: var(--gl-radius);
    padding: 10px 16px;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
  }
  .gl-text-btn {
    background: transparent;
    color: var(--gl-text);
  }
  .gl-text-btn:hover { background: rgba(127,127,127,0.12); }
  .gl-primary-btn {
    background: var(--gl-accent);
    color: #fff;
  }
  .gl-primary-btn:hover { filter: brightness(1.05); }

  @media (min-width: 520px) {
    .gl-add-backdrop { align-items: center; }
  }

  .gl-qtyrow {
    display: flex;
    gap: var(--gl-gap);
    align-items: center;
    flex-wrap: wrap;
  }
  .gl-stepper {
    display: inline-flex;
    align-items: center;
    border: 1px solid var(--gl-divider);
    border-radius: var(--gl-radius);
    overflow: hidden;
  }
  .gl-stepper button {
    border: none;
    background: transparent;
    color: var(--gl-text);
    width: 34px;
    height: 34px;
    font-size: 1.1rem;
    cursor: pointer;
  }
  .gl-stepper input {
    width: 46px;
    text-align: center;
    border: none;
    font-size: 1rem;
    background: transparent;
    color: var(--gl-text);
  }
  select.gl-unit, select.gl-cat {
    border: 1px solid var(--gl-divider);
    border-radius: var(--gl-radius);
    padding: 8px 10px;
    font-size: 0.9rem;
    background: var(--gl-card-bg);
    color: var(--gl-text);
  }

  .gl-checked-section {
    margin-top: 12px;
    padding-top: 4px;
    border-top: 2px solid var(--gl-divider);
    opacity: 0.85;
  }
  .gl-scroll {
    max-height: 60vh;
    overflow-y: auto;
  }

  .gl-checked-divider {
    font-size: 0.95rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--gl-muted);
    margin: 0 0 2px;
    padding: 0 4px;
    /* Fixed height so category titles inside the checked section can stick
       right below it (see .gl-checked-section .gl-group-title top offset). */
    height: 32px;
    box-sizing: border-box;
    display: flex;
    align-items: center;
    position: sticky;
    top: 0;
    z-index: 3;
    background: var(--gl-card-bg);
  }

  .gl-group { margin-top: 4px; }
  .gl-group-title {
    font-size: 1.05rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    color: var(--gl-text);
    margin: 0 0 2px;
    padding: 6px 4px 4px;
    display: flex;
    align-items: center;
    gap: 6px;
    position: sticky;
    top: 0;
    z-index: 2;
    background: var(--gl-card-bg);
  }
  /* Inside the checked section, category titles must stick just below the
     sticky "CHECKED" divider (its height) instead of at top:0, otherwise the
     divider (higher z-index) overlaps and hides them. */
  .gl-checked-section .gl-group-title {
    top: 32px;
    z-index: 1;
  }

  ul.gl-items { list-style: none; margin: 0; padding: 0; }
  li.gl-item {
    display: flex;
    align-items: center;
    gap: var(--gl-gap);
    padding: 8px 4px;
    border-bottom: 1px solid var(--gl-divider);
  }
  li.gl-item:last-child { border-bottom: none; }
  li.gl-item.checked .gl-item-name {
    text-decoration: line-through;
    color: var(--gl-muted);
  }

  .gl-check {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    border: 2px solid var(--gl-muted);
    background: transparent;
    cursor: pointer;
    flex: 0 0 auto;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 0.8rem;
  }
  .gl-check.on {
    background: var(--gl-accent);
    border-color: var(--gl-accent);
  }

  .gl-item-main {
    flex: 1 1 auto;
    min-width: 0;
    display: flex;
    align-items: baseline;
    gap: 8px;
  }
  .gl-qty-swipe {
    cursor: ew-resize;
    touch-action: pan-y;
    user-select: none;
  }
  .gl-item-name {
    flex: 1 1 auto;
    min-width: 0;
    font-size: 1rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .gl-item-qty {
    flex: 0 0 auto;
    font-size: 1rem;
    color: var(--gl-muted);
    white-space: nowrap;
    border-radius: 999px;
    padding: 1px 5px;
    margin: -1px -5px;
  }
  .gl-item.gl-qty-pulse-0,
  .gl-item.gl-qty-pulse-1 {
    animation: gl-qty-pulse 420ms ease-out;
  }
  @keyframes gl-qty-pulse {
    0%, 100% { background-color: transparent; }
    45% { background-color: color-mix(in srgb, var(--gl-accent) 18%, transparent); }
  }
  .gl-edit { display: flex; flex-direction: column; gap: 6px; flex: 1 1 auto; }
  .gl-edit-row { display: flex; gap: var(--gl-gap); flex: 1 1 auto; }
  .gl-edit-row input {
    flex: 1 1 auto;
    min-width: 0;
    border: 1px solid var(--gl-accent);
    border-radius: var(--gl-radius);
    padding: 6px 10px;
    font-size: 1rem;
    background: var(--gl-card-bg);
    color: var(--gl-text);
  }

  .gl-empty {
    text-align: center;
    color: var(--gl-muted);
    padding: 24px 8px;
    font-size: 0.95rem;
  }

  .gl-footer {
    display: flex;
    justify-content: flex-start;
    margin-top: 4px;
  }
  .gl-clear-btn {
    background: transparent;
    border: 1px solid var(--gl-divider);
    color: var(--gl-muted);
    border-radius: var(--gl-radius);
    padding: 6px 12px;
    font-size: 0.85rem;
    cursor: pointer;
  }
  .gl-clear-btn:hover { color: var(--error-color, #f44336); }

  /* --- Category manager overlay --- */
  .gl-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.45);
    display: flex;
    align-items: flex-end;
    justify-content: center;
    z-index: 10;
  }
  @media (min-width: 600px) {
    .gl-overlay { align-items: center; }
  }
  .gl-sheet {
    background: var(--gl-card-bg);
    color: var(--gl-text);
    width: 100%;
    max-width: 480px;
    max-height: 80vh;
    overflow-y: auto;
    border-radius: var(--gl-radius) var(--gl-radius) 0 0;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: var(--gl-gap);
    box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.25);
  }
  @media (min-width: 600px) {
    .gl-sheet { border-radius: var(--gl-radius); }
  }
  .gl-sheet-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .gl-sheet-header h3 { margin: 0; font-size: 1.1rem; }

  .gl-catlist { list-style: none; margin: 0; padding: 0; }
  .gl-catrow {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 0;
    border-bottom: 1px solid var(--gl-divider);
  }
  .gl-catrow:last-child { border-bottom: none; }
  .gl-catrow input.gl-cat-label {
    flex: 1 1 auto;
    min-width: 0;
    border: 1px solid var(--gl-divider);
    border-radius: 8px;
    padding: 6px 8px;
    font-size: 0.95rem;
    background: var(--gl-card-bg);
    color: var(--gl-text);
  }
  .gl-settings-section {
    margin-bottom: 18px;
  }
  .gl-settings-section:last-child { margin-bottom: 0; }
  .gl-section-title {
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--gl-muted);
    margin: 4px 0 8px;
  }
  .gl-section-title-list {
    color: var(--gl-accent, var(--primary-color));
    text-transform: none;
  }
  .gl-cat-new {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 8px;
    border: 1px dashed var(--gl-divider);
    border-radius: var(--gl-radius);
  }
  .gl-cat-new input {
    border: 1px solid var(--gl-divider);
    border-radius: 8px;
    padding: 8px;
    font-size: 0.95rem;
    background: var(--gl-card-bg);
    color: var(--gl-text);
  }
  .gl-cat-new .gl-add-btn {
    background: var(--gl-accent);
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 8px 12px;
    font-weight: 600;
    cursor: pointer;
  }

  /* ----- Archive subview ----- */
  .gl-archive-list {
    list-style: none;
    margin: 0;
    padding: 0;
  }
  .gl-archive-row {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 10px;
    padding: 8px 4px;
    border-bottom: 1px solid var(--gl-divider);
  }
  .gl-archive-name {
    flex: 1;
    min-width: 0;
    color: var(--gl-muted);
    text-decoration: line-through;
  }
  .gl-archive-qty {
    font-size: 0.8rem;
    color: var(--gl-muted);
  }
  .gl-archive-ts {
    font-size: 0.72rem;
    color: var(--gl-muted);
    white-space: nowrap;
  }

  /* In-card dialog (prompt / confirm). Reuses .gl-overlay for the backdrop. */
  .gl-dialog {
    background: var(--gl-card-bg);
    color: var(--gl-text);
    width: 100%;
    max-width: 400px;
    margin: 0 16px;
    border-radius: var(--gl-radius);
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 14px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
  }
  .gl-dialog-title {
    margin: 0;
    font-size: 1.15rem;
    font-weight: 600;
  }
  .gl-dialog-msg {
    margin: 0;
    color: var(--gl-muted);
    font-size: 0.95rem;
    line-height: 1.4;
  }
  .gl-dialog-input {
    width: 100%;
    box-sizing: border-box;
    border: 1px solid var(--gl-divider);
    border-radius: 8px;
    padding: 10px 12px;
    background: var(--gl-card-bg);
    color: var(--gl-text);
    font-size: 1rem;
  }
  .gl-dialog-actions {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    margin-top: 4px;
  }
  .gl-dialog-actions .gl-btn {
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    background: var(--gl-accent);
    color: #fff;
    line-height: 1.4;
    min-width: 72px;
  }
  .gl-dialog-actions .gl-btn:hover {
    filter: brightness(1.05);
  }
  .gl-btn-text {
    background: transparent;
    color: var(--gl-text);
  }
  .gl-btn-primary {
    background: var(--gl-accent);
    color: #fff;
  }
  .gl-btn-danger {
    background: var(--error-color, #db4437);
    color: #fff;
  }
`,_e={add_placeholder:"Add an item…",add:"Add",qty:"Qty",unit:"Unit",category:"Category",uncategorized:"Uncategorized",clear_checked:"Clear checked",clear_checked_confirm:"Remove all checked items? They move to the archive and can be restored from there.",checked_section:"Checked",restore:"Restore",restore_confirm:"Restore this item to the list?",undo:"Undo",redo:"Redo",sync:"Sync",save:"Save",cancel:"Cancel",delete:"Delete",edit:"Edit",empty_list:"Nothing here yet. Add your first item above.",git_prefix:"Git",sync_synced:"Synced",sync_pending:"Pending",sync_syncing:"Syncing…",sync_offline:"Offline",sync_error:"Sync error",settings:"Settings",new_category:"New category",category_name:"Name",close:"Close",archive:"Archive",view_archive:"View archive",no_archive:"Nothing archived yet. Cleared items appear here.",archived_on:"Archived",needs_config:"Grocery List not configured",needs_config_hint:"Open the card editor and pick a Grocery List, or set 'entry_id' in YAML.",select_list_entry:"Grocery List instance",no_entries:"No Grocery List integration found. Add it under Settings → Devices & Services first.",title:"Title (optional)",manage_lists:"Manage lists",lists:"Lists",new_list:"New list",list_name:"List name",add_list:"Add list",no_lists:"No lists yet. Create one above.",rename_list:"Rename list",delete_list:"Delete list",delete_list_confirm:"Delete this list and all its items? This cannot be undone by others once synced.",delete_item_confirm:"Delete this item? This cannot be undone by others once synced.",list_name_prompt:"New list name:",rename_list_prompt:"Rename list to:",categories:"Categories",reorder_categories:"Reorder categories",move_up:"Move up",move_down:"Move down",no_categories:"No categories yet. Add an item with a category first.",rename_category:"Rename category",rename_category_prompt:"Rename category to:"},me={en:_e,de:{add_placeholder:"Artikel hinzufügen…",add:"Hinzufügen",qty:"Menge",unit:"Einheit",category:"Kategorie",uncategorized:"Ohne Kategorie",clear_checked:"Erledigte entfernen",clear_checked_confirm:"Alle erledigten Artikel entfernen? Sie wandern ins Archiv und können von dort wiederhergestellt werden.",checked_section:"Erledigt",restore:"Wiederherstellen",restore_confirm:"Diesen Artikel zurück auf die Liste setzen?",undo:"Rückgängig",redo:"Wiederholen",sync:"Sync",save:"Speichern",cancel:"Abbrechen",delete:"Löschen",edit:"Bearbeiten",empty_list:"Noch nichts hier. Füge oben deinen ersten Artikel hinzu.",sync_synced:"Synchronisiert",sync_pending:"Ausstehend",sync_syncing:"Synchronisiere…",sync_offline:"Offline",sync_error:"Sync-Fehler",settings:"Einstellungen",new_category:"Neue Kategorie",category_name:"Name",close:"Schließen",archive:"Archiv",view_archive:"Archiv anzeigen",no_archive:"Noch nichts archiviert. Entfernte Artikel erscheinen hier.",archived_on:"Archiviert",needs_config:"Einkaufsliste nicht konfiguriert",needs_config_hint:"Öffne den Karten-Editor und wähle eine Einkaufsliste, oder setze 'entry_id' im YAML.",select_list_entry:"Einkaufslisten-Instanz",no_entries:"Keine Einkaufslisten-Integration gefunden. Füge sie zuerst unter Einstellungen → Geräte & Dienste hinzu.",title:"Titel (optional)",manage_lists:"Listen verwalten",lists:"Listen",new_list:"Neue Liste",list_name:"Listenname",add_list:"Liste hinzufügen",no_lists:"Noch keine Listen. Erstelle oben eine.",rename_list:"Liste umbenennen",delete_list:"Liste löschen",delete_list_confirm:"Diese Liste und alle ihre Artikel löschen? Nach der Synchronisierung können andere dies nicht rückgängig machen.",delete_item_confirm:"Diesen Artikel löschen? Nach der Synchronisierung können andere dies nicht rückgängig machen.",list_name_prompt:"Name der neuen Liste:",rename_list_prompt:"Liste umbenennen in:",categories:"Kategorien",reorder_categories:"Kategorien neu ordnen",move_up:"Nach oben",move_down:"Nach unten",no_categories:"Noch keine Kategorien. Füge zuerst einen Artikel mit Kategorie hinzu.",rename_category:"Kategorie umbenennen",rename_category_prompt:"Kategorie umbenennen in:"},es:{add_placeholder:"Añadir un artículo…",add:"Añadir",qty:"Cant.",unit:"Unidad",category:"Categoría",uncategorized:"Sin categoría",clear_checked:"Quitar marcados",clear_checked_confirm:"¿Quitar todos los artículos marcados? Pasan al archivo y pueden restaurarse desde allí.",checked_section:"Marcados",restore:"Restaurar",restore_confirm:"¿Restaurar este artículo a la lista?",undo:"Deshacer",redo:"Rehacer",sync:"Sincronizar",save:"Guardar",cancel:"Cancelar",delete:"Eliminar",edit:"Editar",empty_list:"Aún no hay nada. Añade tu primer artículo arriba.",sync_synced:"Sincronizado",sync_pending:"Pendiente",sync_syncing:"Sincronizando…",sync_offline:"Sin conexión",sync_error:"Error de sincronización",settings:"Ajustes",new_category:"Nueva categoría",category_name:"Nombre",close:"Cerrar",archive:"Archivo",view_archive:"Ver archivo",no_archive:"Aún no hay nada archivado. Los artículos quitados aparecen aquí.",archived_on:"Archivado",needs_config:"Lista de la compra no configurada",needs_config_hint:"Abre el editor de la tarjeta y elige una lista de la compra, o define 'entry_id' en YAML.",select_list_entry:"Instancia de lista de la compra",no_entries:"No se encontró ninguna integración de lista de la compra. Añádela primero en Ajustes → Dispositivos y servicios.",title:"Título (opcional)",manage_lists:"Gestionar listas",lists:"Listas",new_list:"Nueva lista",list_name:"Nombre de la lista",add_list:"Añadir lista",no_lists:"Aún no hay listas. Crea una arriba.",rename_list:"Renombrar lista",delete_list:"Eliminar lista",delete_list_confirm:"¿Eliminar esta lista y todos sus artículos? Una vez sincronizado, otros no podrán deshacerlo.",delete_item_confirm:"¿Eliminar este artículo? Una vez sincronizado, otros no podrán deshacerlo.",list_name_prompt:"Nombre de la nueva lista:",rename_list_prompt:"Renombrar lista a:",categories:"Categorías",reorder_categories:"Reordenar categorías",move_up:"Subir",move_down:"Bajar",no_categories:"Aún no hay categorías. Añade primero un artículo con categoría.",rename_category:"Renombrar categoría",rename_category_prompt:"Renombrar categoría a:"},fr:{add_placeholder:"Ajouter un article…",add:"Ajouter",qty:"Qté",unit:"Unité",category:"Catégorie",uncategorized:"Sans catégorie",clear_checked:"Effacer les cochés",clear_checked_confirm:"Retirer tous les articles cochés ? Ils passent dans les archives et peuvent y être restaurés.",checked_section:"Cochés",restore:"Restaurer",restore_confirm:"Restaurer cet article dans la liste ?",undo:"Annuler",redo:"Rétablir",sync:"Synchroniser",save:"Enregistrer",cancel:"Annuler",delete:"Supprimer",edit:"Modifier",empty_list:"Rien ici pour l'instant. Ajoutez votre premier article ci-dessus.",sync_synced:"Synchronisé",sync_pending:"En attente",sync_syncing:"Synchronisation…",sync_offline:"Hors ligne",sync_error:"Erreur de synchronisation",settings:"Paramètres",new_category:"Nouvelle catégorie",category_name:"Nom",close:"Fermer",archive:"Archives",view_archive:"Voir les archives",no_archive:"Rien d'archivé pour l'instant. Les articles retirés apparaissent ici.",archived_on:"Archivé",needs_config:"Liste de courses non configurée",needs_config_hint:"Ouvrez l'éditeur de carte et choisissez une liste de courses, ou définissez 'entry_id' dans le YAML.",select_list_entry:"Instance de liste de courses",no_entries:"Aucune intégration de liste de courses trouvée. Ajoutez-la d'abord dans Paramètres → Appareils et services.",title:"Titre (optionnel)",manage_lists:"Gérer les listes",lists:"Listes",new_list:"Nouvelle liste",list_name:"Nom de la liste",add_list:"Ajouter une liste",no_lists:"Aucune liste pour l'instant. Créez-en une ci-dessus.",rename_list:"Renommer la liste",delete_list:"Supprimer la liste",delete_list_confirm:"Supprimer cette liste et tous ses articles ? Une fois synchronisé, les autres ne pourront pas l'annuler.",delete_item_confirm:"Supprimer cet article ? Une fois synchronisé, les autres ne pourront pas l'annuler.",list_name_prompt:"Nom de la nouvelle liste :",rename_list_prompt:"Renommer la liste en :",categories:"Catégories",reorder_categories:"Réorganiser les catégories",move_up:"Monter",move_down:"Descendre",no_categories:"Aucune catégorie pour l'instant. Ajoutez d'abord un article avec une catégorie.",rename_category:"Renommer la catégorie",rename_category_prompt:"Renommer la catégorie en :"},it:{add_placeholder:"Aggiungi un articolo…",add:"Aggiungi",qty:"Qtà",unit:"Unità",category:"Categoria",uncategorized:"Senza categoria",clear_checked:"Rimuovi selezionati",clear_checked_confirm:"Rimuovere tutti gli articoli selezionati? Vengono spostati nell'archivio e possono essere ripristinati da lì.",checked_section:"Selezionati",restore:"Ripristina",restore_confirm:"Ripristinare questo articolo nella lista?",undo:"Annulla",redo:"Ripeti",sync:"Sincronizza",save:"Salva",cancel:"Annulla",delete:"Elimina",edit:"Modifica",empty_list:"Ancora niente qui. Aggiungi il tuo primo articolo sopra.",sync_synced:"Sincronizzato",sync_pending:"In attesa",sync_syncing:"Sincronizzazione…",sync_offline:"Non in linea",sync_error:"Errore di sincronizzazione",settings:"Impostazioni",new_category:"Nuova categoria",category_name:"Nome",close:"Chiudi",archive:"Archivio",view_archive:"Visualizza archivio",no_archive:"Ancora niente in archivio. Gli articoli rimossi appaiono qui.",archived_on:"Archiviato",needs_config:"Lista della spesa non configurata",needs_config_hint:"Apri l'editor della scheda e scegli una lista della spesa, oppure imposta 'entry_id' nello YAML.",select_list_entry:"Istanza della lista della spesa",no_entries:"Nessuna integrazione della lista della spesa trovata. Aggiungila prima in Impostazioni → Dispositivi e servizi.",title:"Titolo (opzionale)",manage_lists:"Gestisci liste",lists:"Liste",new_list:"Nuova lista",list_name:"Nome della lista",add_list:"Aggiungi lista",no_lists:"Ancora nessuna lista. Creane una sopra.",rename_list:"Rinomina lista",delete_list:"Elimina lista",delete_list_confirm:"Eliminare questa lista e tutti i suoi articoli? Una volta sincronizzato, altri non potranno annullarlo.",delete_item_confirm:"Eliminare questo articolo? Una volta sincronizzato, altri non potranno annullarlo.",list_name_prompt:"Nome della nuova lista:",rename_list_prompt:"Rinomina lista in:",categories:"Categorie",reorder_categories:"Riordina categorie",move_up:"Sposta su",move_down:"Sposta giù",no_categories:"Ancora nessuna categoria. Aggiungi prima un articolo con categoria.",rename_category:"Rinomina categoria",rename_category_prompt:"Rinomina categoria in:"},pt:{add_placeholder:"Adicionar um artigo…",add:"Adicionar",qty:"Qtd.",unit:"Unidade",category:"Categoria",uncategorized:"Sem categoria",clear_checked:"Remover marcados",clear_checked_confirm:"Remover todos os artigos marcados? Passam para o arquivo e podem ser restaurados a partir daí.",checked_section:"Marcados",restore:"Restaurar",restore_confirm:"Restaurar este artigo para a lista?",undo:"Desfazer",redo:"Refazer",sync:"Sincronizar",save:"Guardar",cancel:"Cancelar",delete:"Eliminar",edit:"Editar",empty_list:"Ainda nada aqui. Adicione o seu primeiro artigo acima.",sync_synced:"Sincronizado",sync_pending:"Pendente",sync_syncing:"A sincronizar…",sync_offline:"Offline",sync_error:"Erro de sincronização",settings:"Definições",new_category:"Nova categoria",category_name:"Nome",close:"Fechar",archive:"Arquivo",view_archive:"Ver arquivo",no_archive:"Ainda nada arquivado. Os artigos removidos aparecem aqui.",archived_on:"Arquivado",needs_config:"Lista de compras não configurada",needs_config_hint:"Abra o editor do cartão e escolha uma lista de compras, ou defina 'entry_id' no YAML.",select_list_entry:"Instância da lista de compras",no_entries:"Nenhuma integração de lista de compras encontrada. Adicione-a primeiro em Definições → Dispositivos e serviços.",title:"Título (opcional)",manage_lists:"Gerir listas",lists:"Listas",new_list:"Nova lista",list_name:"Nome da lista",add_list:"Adicionar lista",no_lists:"Ainda sem listas. Crie uma acima.",rename_list:"Renomear lista",delete_list:"Eliminar lista",delete_list_confirm:"Eliminar esta lista e todos os seus artigos? Após a sincronização, outros não poderão desfazer.",delete_item_confirm:"Eliminar este artigo? Após a sincronização, outros não poderão desfazer.",list_name_prompt:"Nome da nova lista:",rename_list_prompt:"Renomear lista para:",categories:"Categorias",reorder_categories:"Reordenar categorias",move_up:"Mover para cima",move_down:"Mover para baixo",no_categories:"Ainda sem categorias. Adicione primeiro um artigo com categoria.",rename_category:"Renomear categoria",rename_category_prompt:"Renomear categoria para:"},nl:{add_placeholder:"Een item toevoegen…",add:"Toevoegen",qty:"Aantal",unit:"Eenheid",category:"Categorie",uncategorized:"Zonder categorie",clear_checked:"Afgevinkte wissen",clear_checked_confirm:"Alle afgevinkte items verwijderen? Ze gaan naar het archief en kunnen daar worden hersteld.",checked_section:"Afgevinkt",restore:"Herstellen",restore_confirm:"Dit item terugzetten op de lijst?",undo:"Ongedaan maken",redo:"Opnieuw",sync:"Synchroniseren",save:"Opslaan",cancel:"Annuleren",delete:"Verwijderen",edit:"Bewerken",empty_list:"Nog niets hier. Voeg hierboven je eerste item toe.",sync_synced:"Gesynchroniseerd",sync_pending:"In behandeling",sync_syncing:"Synchroniseren…",sync_offline:"Offline",sync_error:"Synchronisatiefout",settings:"Instellingen",new_category:"Nieuwe categorie",category_name:"Naam",close:"Sluiten",archive:"Archief",view_archive:"Archief bekijken",no_archive:"Nog niets gearchiveerd. Verwijderde items verschijnen hier.",archived_on:"Gearchiveerd",needs_config:"Boodschappenlijst niet geconfigureerd",needs_config_hint:"Open de kaarteditor en kies een boodschappenlijst, of stel 'entry_id' in de YAML in.",select_list_entry:"Boodschappenlijst-instantie",no_entries:"Geen boodschappenlijst-integratie gevonden. Voeg deze eerst toe via Instellingen → Apparaten en diensten.",title:"Titel (optioneel)",manage_lists:"Lijsten beheren",lists:"Lijsten",new_list:"Nieuwe lijst",list_name:"Lijstnaam",add_list:"Lijst toevoegen",no_lists:"Nog geen lijsten. Maak er hierboven een.",rename_list:"Lijst hernoemen",delete_list:"Lijst verwijderen",delete_list_confirm:"Deze lijst en al haar items verwijderen? Na synchronisatie kunnen anderen dit niet ongedaan maken.",delete_item_confirm:"Dit item verwijderen? Na synchronisatie kunnen anderen dit niet ongedaan maken.",list_name_prompt:"Naam van de nieuwe lijst:",rename_list_prompt:"Lijst hernoemen naar:",categories:"Categorieën",reorder_categories:"Categorieën herordenen",move_up:"Omhoog",move_down:"Omlaag",no_categories:"Nog geen categorieën. Voeg eerst een item met een categorie toe.",rename_category:"Categorie hernoemen",rename_category_prompt:"Categorie hernoemen naar:"},pl:{add_placeholder:"Dodaj artykuł…",add:"Dodaj",qty:"Il.",unit:"Jednostka",category:"Kategoria",uncategorized:"Bez kategorii",clear_checked:"Usuń zaznaczone",clear_checked_confirm:"Usunąć wszystkie zaznaczone artykuły? Trafiają do archiwum i można je stamtąd przywrócić.",checked_section:"Zaznaczone",restore:"Przywróć",restore_confirm:"Przywrócić ten artykuł na listę?",undo:"Cofnij",redo:"Ponów",sync:"Synchronizuj",save:"Zapisz",cancel:"Anuluj",delete:"Usuń",edit:"Edytuj",empty_list:"Jeszcze nic tu nie ma. Dodaj swój pierwszy artykuł powyżej.",sync_synced:"Zsynchronizowano",sync_pending:"Oczekuje",sync_syncing:"Synchronizacja…",sync_offline:"Offline",sync_error:"Błąd synchronizacji",settings:"Ustawienia",new_category:"Nowa kategoria",category_name:"Nazwa",close:"Zamknij",archive:"Archiwum",view_archive:"Pokaż archiwum",no_archive:"Nic jeszcze nie zarchiwizowano. Usunięte artykuły pojawiają się tutaj.",archived_on:"Zarchiwizowano",needs_config:"Lista zakupów nie skonfigurowana",needs_config_hint:"Otwórz edytor karty i wybierz listę zakupów lub ustaw 'entry_id' w YAML.",select_list_entry:"Instancja listy zakupów",no_entries:"Nie znaleziono integracji listy zakupów. Dodaj ją najpierw w Ustawienia → Urządzenia i usługi.",title:"Tytuł (opcjonalny)",manage_lists:"Zarządzaj listami",lists:"Listy",new_list:"Nowa lista",list_name:"Nazwa listy",add_list:"Dodaj listę",no_lists:"Brak list. Utwórz jedną powyżej.",rename_list:"Zmień nazwę listy",delete_list:"Usuń listę",delete_list_confirm:"Usunąć tę listę i wszystkie jej artykuły? Po synchronizacji inni nie będą mogli tego cofnąć.",delete_item_confirm:"Usunąć ten artykuł? Po synchronizacji inni nie będą mogli tego cofnąć.",list_name_prompt:"Nazwa nowej listy:",rename_list_prompt:"Zmień nazwę listy na:",categories:"Kategorie",reorder_categories:"Zmień kolejność kategorii",move_up:"W górę",move_down:"W dół",no_categories:"Brak kategorii. Najpierw dodaj artykuł z kategorią.",rename_category:"Zmień nazwę kategorii",rename_category_prompt:"Zmień nazwę kategorii na:"},sv:{add_placeholder:"Lägg till en vara…",add:"Lägg till",qty:"Antal",unit:"Enhet",category:"Kategori",uncategorized:"Utan kategori",clear_checked:"Rensa markerade",clear_checked_confirm:"Ta bort alla markerade varor? De flyttas till arkivet och kan återställas därifrån.",checked_section:"Markerade",restore:"Återställ",restore_confirm:"Återställ denna vara till listan?",undo:"Ångra",redo:"Gör om",sync:"Synkronisera",save:"Spara",cancel:"Avbryt",delete:"Ta bort",edit:"Redigera",empty_list:"Inget här ännu. Lägg till din första vara ovan.",sync_synced:"Synkroniserad",sync_pending:"Väntar",sync_syncing:"Synkroniserar…",sync_offline:"Offline",sync_error:"Synkroniseringsfel",settings:"Inställningar",new_category:"Ny kategori",category_name:"Namn",close:"Stäng",archive:"Arkiv",view_archive:"Visa arkiv",no_archive:"Inget arkiverat ännu. Borttagna varor visas här.",archived_on:"Arkiverad",needs_config:"Inköpslista inte konfigurerad",needs_config_hint:"Öppna kortredigeraren och välj en inköpslista, eller ange 'entry_id' i YAML.",select_list_entry:"Inköpslista-instans",no_entries:"Ingen inköpslista-integration hittades. Lägg till den först under Inställningar → Enheter och tjänster.",title:"Titel (valfritt)",manage_lists:"Hantera listor",lists:"Listor",new_list:"Ny lista",list_name:"Listnamn",add_list:"Lägg till lista",no_lists:"Inga listor ännu. Skapa en ovan.",rename_list:"Byt namn på lista",delete_list:"Ta bort lista",delete_list_confirm:"Ta bort denna lista och alla dess varor? När den synkroniserats kan andra inte ångra det.",delete_item_confirm:"Ta bort denna vara? När den synkroniserats kan andra inte ångra det.",list_name_prompt:"Namn på den nya listan:",rename_list_prompt:"Byt namn på listan till:",categories:"Kategorier",reorder_categories:"Ordna om kategorier",move_up:"Flytta upp",move_down:"Flytta ner",no_categories:"Inga kategorier ännu. Lägg först till en vara med kategori.",rename_category:"Byt namn på kategori",rename_category_prompt:"Byt namn på kategori till:"},nb:{add_placeholder:"Legg til en vare…",add:"Legg til",qty:"Ant.",unit:"Enhet",category:"Kategori",uncategorized:"Uten kategori",clear_checked:"Fjern avkryssede",clear_checked_confirm:"Fjerne alle avkryssede varer? De flyttes til arkivet og kan gjenopprettes derfra.",checked_section:"Avkrysset",restore:"Gjenopprett",restore_confirm:"Gjenopprette denne varen til listen?",undo:"Angre",redo:"Gjenta",sync:"Synkroniser",save:"Lagre",cancel:"Avbryt",delete:"Slett",edit:"Rediger",empty_list:"Ingenting her ennå. Legg til din første vare ovenfor.",sync_synced:"Synkronisert",sync_pending:"Venter",sync_syncing:"Synkroniserer…",sync_offline:"Frakoblet",sync_error:"Synkroniseringsfeil",settings:"Innstillinger",new_category:"Ny kategori",category_name:"Navn",close:"Lukk",archive:"Arkiv",view_archive:"Vis arkiv",no_archive:"Ingenting arkivert ennå. Fjernede varer vises her.",archived_on:"Arkivert",needs_config:"Handleliste ikke konfigurert",needs_config_hint:"Åpne kortredigereren og velg en handleliste, eller angi 'entry_id' i YAML.",select_list_entry:"Handleliste-instans",no_entries:"Fant ingen handleliste-integrasjon. Legg den til først under Innstillinger → Enheter og tjenester.",title:"Tittel (valgfritt)",manage_lists:"Administrer lister",lists:"Lister",new_list:"Ny liste",list_name:"Listenavn",add_list:"Legg til liste",no_lists:"Ingen lister ennå. Opprett en ovenfor.",rename_list:"Gi listen nytt navn",delete_list:"Slett liste",delete_list_confirm:"Slette denne listen og alle varene? Når den er synkronisert, kan andre ikke angre det.",delete_item_confirm:"Slette denne varen? Når den er synkronisert, kan andre ikke angre det.",list_name_prompt:"Navn på den nye listen:",rename_list_prompt:"Gi listen nytt navn:",categories:"Kategorier",reorder_categories:"Endre rekkefølge på kategorier",move_up:"Flytt opp",move_down:"Flytt ned",no_categories:"Ingen kategorier ennå. Legg først til en vare med kategori.",rename_category:"Gi kategorien nytt navn",rename_category_prompt:"Gi kategorien nytt navn:"}};function ye(e){const t=(e??"").toLowerCase();return t.startsWith("de")?"de":t.startsWith("es")?"es":t.startsWith("fr")?"fr":t.startsWith("it")?"it":t.startsWith("pt")?"pt":t.startsWith("nl")?"nl":t.startsWith("pl")?"pl":t.startsWith("sv")?"sv":t.startsWith("nb")||t.startsWith("nn")||t.startsWith("no")?"nb":"en"}function ve(e){const t=me[e]??_e;return e=>t[e]??_e[e]??e}var fe;!function(e){e.Pcs="pcs",e.G="g",e.Kg="kg",e.Ml="ml",e.L="l",e.Jar="jar",e.Pack="pack",e.Bottle="bottle",e.Can="can",e.Bunch="bunch"}(fe||(fe={}));const be=fe.Pcs,$e="__none__",we="__new__",ke={[fe.Pcs]:1,[fe.G]:50,[fe.Kg]:.5,[fe.Ml]:50,[fe.L]:.05,[fe.Jar]:1,[fe.Pack]:1,[fe.Bottle]:1,[fe.Can]:1,[fe.Bunch]:1};function xe(e){return`${e.category??""}|${e.name}`}let Ae=class extends ae{constructor(){super(...arguments),this._units=[],this._defaultUnit=be,this._editingId=null,this._editValue="",this._editQty=1,this._editUnit=be,this._editCategory=null,this._extraCategories=[],this._addOpen=!1,this._draftName="",this._draftQty=1,this._draftUnit=be,this._draftCategory=null,this._settingsOpen=!1,this._archiveOpen=!1,this._dialogValue="",this._newListName=""}setConfig(e){const t=e??{type:"custom:grocery-list-card",entry_id:""};this._config=t,t.slug&&(this._activeSlug=t.slug),this._subscribedEntry&&this._subscribedEntry!==t.entry_id&&this._teardown(),this._maybeSubscribe()}static getConfigElement(){return document.createElement("grocery-list-card-editor")}static async getStubConfig(e){let t="";try{const i=(await e.connection.sendMessagePromise({type:"config_entries/get",domain:"grocery_list"})).find(e=>"grocery_list"===e.domain);i&&(t=i.entry_id)}catch(e){}return{type:"custom:grocery-list-card",entry_id:t}}getCardSize(){const e=this._activeList()?.items.length??0;return 2+Math.ceil(e/3)}connectedCallback(){super.connectedCallback(),this._maybeSubscribe()}disconnectedCallback(){super.disconnectedCallback(),this._teardown()}updated(e){e.has("hass")&&this._maybeSubscribe()}get _lang(){return ye(this.hass?.locale?.language??this.hass?.language)}async _maybeSubscribe(){if(this.hass&&this._config&&this._config.entry_id&&this._subscribedEntry!==this._config.entry_id){this._teardown(),this._subscribedEntry=this._config.entry_id,this._api=new pe(this.hass,this._config.entry_id);try{const e=await this._api.getUnits();this._units=e.units,this._defaultUnit=e.default_unit,this._draftUnit===be&&(this._draftUnit=e.default_unit)}catch(e){this._units=[]}this._unsub=await this._api.subscribe(e=>{this._snapshot=e,!this._activeSlug&&e.lists.length&&(this._activeSlug=e.lists[0].slug)},this._lang)}}_teardown(){this._unsub&&(this._unsub(),this._unsub=void 0),this._subscribedEntry=void 0}_activeList(){const e=this._snapshot;if(e)return e.lists.find(e=>e.slug===this._activeSlug)??e.lists[0]}_targetSlug(){return this._activeList()?.slug??this._activeSlug??this._config?.slug??"default"}render(){const e=ve(this._lang);if(!this._config?.entry_id)return D`<ha-card>
        <div class="gl-empty">
          <p><strong>${e("needs_config")}</strong></p>
          <p>${e("needs_config_hint")}</p>
        </div>
      </ha-card>`;if(!this._snapshot)return D`<ha-card><div class="gl-empty">\u2026</div></ha-card>`;const t=ve(this._lang),i=this._activeList();return D`
      <ha-card>
        ${this._renderHeader(t)}
        ${this._snapshot.lists.length>1?this._renderSwitcher():H}
        ${this._renderAddBar(t)}
        ${i?D`<div class="gl-scroll">${this._renderGroups(i,t)}</div>`:H}
        ${this._renderFooter(t)}
      </ha-card>
      ${this._addOpen?this._renderAddSheet(t):H}
      ${this._settingsOpen?this._renderSettings(t):H}
      ${this._archiveOpen?this._renderArchive(t):H}
      ${this._dialog?this._renderDialog():H}
    `}_renderHeader(e){const t=this._snapshot,i=this._activeList(),n=this._config?.title??i?.title??"Grocery",r=t.sync_state,s="local"!==r;return D`
      <div class="gl-header">
        <h2 class="gl-title">${n}</h2>
        <div class="gl-toolbar">
          ${s?D`<span class="gl-badge ${r}"
                >${e("git_prefix")}: ${e("sync_"+r)}</span
              >`:H}
          <button
            class="gl-icon-btn"
            title=${e("undo")}
            ?disabled=${!t.can_undo}
            @click=${()=>this._api?.undo()}
          >\u21b6</button>
          <button
            class="gl-icon-btn"
            title=${e("redo")}
            ?disabled=${!t.can_redo}
            @click=${()=>this._api?.redo()}
          >\u21b7</button>
          ${s?D`<button
                class="gl-icon-btn"
                title=${e("sync")}
                @click=${()=>this._api?.sync()}
              >\u21bb</button>`:H}
          <button
            class="gl-icon-btn"
            title=${e("view_archive")}
            @click=${()=>this._archiveOpen=!0}
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
            title=${e("settings")}
            @click=${()=>this._settingsOpen=!0}
          >\u2699</button>
        </div>
      </div>
    `}_renderSwitcher(){const e=this._snapshot;return D`
      <div class="gl-switcher">
        ${e.lists.map(e=>D`
            <button
              class="gl-tab ${e.slug===this._activeSlug?"active":""}"
              @click=${()=>this._activeSlug=e.slug}
            >
              ${e.title}
            </button>
          `)}
      </div>
    `}_renderAddBar(e){return D`
      <button
        class="gl-add-fab"
        title=${e("add")}
        aria-label=${e("add")}
        @click=${()=>this._addOpen=!0}
      >
        +
      </button>
    `}_renderAddSheet(e){return D`
      <div
        class="gl-add-backdrop"
        @click=${e=>{e.target===e.currentTarget&&(this._addOpen=!1)}}
      >
        <div class="gl-add-dialog" @click=${e=>e.stopPropagation()}>
          <h3 class="gl-dialog-title">${e("add")}</h3>
          <div class="gl-add-form">
            <input
              class="gl-name"
              .value=${this._draftName}
              placeholder=${e("add_placeholder")}
              @input=${e=>this._draftName=e.target.value}
              @keydown=${e=>{"Enter"===e.key&&this._commitAdd()}}
            />
            <div class="gl-qtyrow">
              <div class="gl-stepper">
                <button @click=${()=>this._bumpQty(-1)}>\u2212</button>
                <input
                  type="number"
                  min="1"
                  .value=${String(this._draftQty)}
                  @input=${e=>this._draftQty=Math.max(1,parseFloat(e.target.value)||1)}
                />
                <button @click=${()=>this._bumpQty(1)}>+</button>
              </div>
              <select
                class="gl-unit"
                .value=${this._draftUnit}
                @change=${e=>this._draftUnit=this._asQuantityUnitId(e.target.value)??this._defaultUnit}
              >
                ${this._units.map(e=>D`<option value=${e.id} ?selected=${e.id===this._draftUnit}>
                    ${this._unitLabel(e.id)}
                  </option>`)}
              </select>
              <select
                class="gl-cat"
                @change=${async t=>{const i=t.target,n=i.value;if(n===we){i.value=this._draftCategory??$e;const t=await this._promptNewCategory(e);t&&(this._draftCategory=t)}else this._draftCategory=n===$e?null:n}}
              >
                <option value=${$e} ?selected=${null==this._draftCategory}>
                  ${e("uncategorized")}
                </option>
                ${this._categories().map(e=>D`<option value=${e} ?selected=${this._draftCategory===e}>
                    ${e}
                  </option>`)}
                <option value=${we}>${e("new_category")}…</option>
              </select>
            </div>
            <div class="gl-add-actions">
              <button class="gl-text-btn" @click=${()=>this._addOpen=!1}>
                ${e("cancel")}
              </button>
              <button class="gl-primary-btn" @click=${()=>this._commitAdd()}>
                ${e("add")}
              </button>
            </div>
          </div>
        </div>
      </div>
    `}_renderGroups(e,t){if(!e.items.length)return D`<div class="gl-empty">${t("empty_list")}</div>`;const i=e.items.filter(e=>!e.checked),n=e.items.filter(e=>e.checked);return D`
      ${this._renderCategoryGroups(i,e,t)}
      ${n.length?D`<div class="gl-checked-section">
              <div class="gl-checked-divider">${t("checked_section")}</div>
              ${this._renderCategoryGroups(n,e,t)}
            </div>`:H}
    `}_renderCategoryGroups(e,t,i){if(!e.length)return D``;const n=t.slug,r=new Map;for(const t of e){const e=t.category??$e,i=r.get(e);i?i.push(t):r.set(e,[t])}const s=t.category_order??[],a=new Map;s.forEach((e,t)=>a.set(e,t));const o=[...r.keys()].sort((e,t)=>{if(e===$e)return 1;if(t===$e)return-1;const i=a.has(e)?a.get(e):1/0,n=a.has(t)?a.get(t):1/0;return i!==n?i-n:e.localeCompare(t)});return D`
      ${o.map(e=>{const t=[...r.get(e)].sort((e,t)=>e.name.localeCompare(t.name)),s=e===$e?i("uncategorized"):e;return D`
          <div class="gl-group">
            <div class="gl-group-title">${s}</div>
            <ul class="gl-items">
              ${t.map(e=>this._renderItem(e,n,i))}
            </ul>
          </div>
        `})}
    `}_renderItem(e,t,i){if(this._editingId===xe(e))return D`<li class="gl-item">${this._renderEdit(e,t,i)}</li>`;const n=this._qtySwipe,r=n?.slug===t&&xe(n.item)===xe(e),s=r?n.previewValue:e.qty?.value,a=r?n.unit:e.qty?.unit,o=void 0!==s&&a?`${this._fmtNum(s)} ${this._unitLabel(a,s)}`:"",l=n?.slug===t&&xe(n.item)===xe(e)&&n.pulseKey?" gl-qty-pulse gl-qty-pulse-"+n.pulseKey%2:"",c=this._canQuickAdjustQty(e.qty?.unit??this._defaultUnit);return D`
      <li class="gl-item ${e.checked?"checked":""}${l}">
        <button
          class="gl-check ${e.checked?"on":""}"
          @click=${()=>this._api?.setChecked(t,e.category,e.name,!e.checked)}
        >
          ${e.checked?"✓":""}
        </button>
        <div
          class="gl-item-main ${c?"gl-qty-swipe":""}"
          title=${c?"Swipe right to increase quantity. Swipe left to decrease quantity.":H}
          @pointerdown=${i=>this._handleQtyPointerDown(i,t,e)}
        >
          <div class="gl-item-name">${e.name}</div>
          ${o?D`<div class="gl-item-qty">${o}</div>`:H}
        </div>
        <button
          class="gl-icon-btn"
          title=${i("edit")}
          @click=${()=>this._beginEdit(e)}
        >✎</button>
      </li>
    `}_renderEdit(e,t,i){return D`
      <div class="gl-edit">
        <div class="gl-edit-row">
          <input
            .value=${this._editValue}
            @input=${e=>this._editValue=e.target.value}
            @keydown=${i=>{"Enter"===i.key&&this._saveEdit(t,e),"Escape"===i.key&&this._cancelEdit()}}
          />
          <button
            class="gl-icon-btn"
            title=${i("save")}
            @click=${()=>this._saveEdit(t,e)}
          >\u2713</button>
          <button
            class="gl-icon-btn"
            title=${i("cancel")}
            @click=${()=>this._cancelEdit()}
          >\u2715</button>
          <button
            class="gl-icon-btn gl-danger"
            title=${i("delete")}
            @click=${()=>this._deleteItemConfirm(t,e,i)}
          >Del</button>
        </div>
        <div class="gl-qtyrow">
          <div class="gl-stepper">
            <button @click=${()=>this._bumpEditQty(-1)}>\u2212</button>
            <input
              type="number"
              min="1"
              .value=${String(this._editQty)}
              @input=${e=>this._editQty=Math.max(1,parseFloat(e.target.value)||1)}
            />
            <button @click=${()=>this._bumpEditQty(1)}>+</button>
          </div>
          <select
            class="gl-unit"
            .value=${this._editUnit}
            @change=${e=>this._editUnit=this._asQuantityUnitId(e.target.value)??this._defaultUnit}
          >
            ${this._units.map(e=>D`<option value=${e.id} ?selected=${e.id===this._editUnit}>
                ${this._unitLabel(e.id)}
              </option>`)}
          </select>
          <select
            class="gl-cat"
            @change=${async e=>{const t=e.target,n=t.value;if(n===we){t.value=this._editCategory??$e;const e=await this._promptNewCategory(i);e&&(this._editCategory=e)}else this._editCategory=n===$e?null:n}}
          >
            <option value=${$e} ?selected=${null==this._editCategory}>
              ${i("uncategorized")}
            </option>
            ${this._categories().map(e=>D`<option value=${e} ?selected=${this._editCategory===e}>
                ${e}
              </option>`)}
            <option value=${we}>${i("new_category")}…</option>
          </select>
        </div>
      </div>
    `}_renderFooter(e){const t=this._activeList(),i=!!t?.items.some(e=>e.checked);return D`
      <div class="gl-footer">
        <button
          class="gl-clear-btn"
          ?disabled=${!i}
          @click=${()=>this._clearCheckedConfirm(e)}
        >
          ${e("clear_checked")}
        </button>
      </div>
    `}async _clearCheckedConfirm(e){const t=this._activeList();if(!t)return;await this._showConfirm({title:e("clear_checked"),message:e("clear_checked_confirm"),confirmLabel:e("delete"),cancelLabel:e("cancel"),danger:!0})&&this._api?.clearChecked(t.slug)}_renderArchive(e){const t=this._activeSlug,i=t&&this._snapshot?.archives?.[t]||[];return D`
      <div
        class="gl-overlay"
        @click=${e=>{e.target===e.currentTarget&&(this._archiveOpen=!1)}}
      >
        <div class="gl-sheet">
          <div class="gl-sheet-header">
            <h3>${e("archive")}</h3>
            <button
              class="gl-icon-btn"
              title=${e("close")}
              @click=${()=>this._archiveOpen=!1}
            >\u2715</button>
          </div>

          ${i.length?D`<ul class="gl-archive-list">
                ${i.map(t=>this._renderArchiveRow(t,e))}
              </ul>`:D`<div class="gl-empty">${e("no_archive")}</div>`}
        </div>
      </div>
    `}_renderArchiveRow(e,t){const i=e.item.qty?`${this._fmtNum(e.item.qty.value)} ${this._unitLabel(e.item.qty.unit,e.item.qty.value)}`:"";return D`
      <li class="gl-archive-row">
        <span class="gl-archive-name">${e.item.name}</span>
        ${i?D`<span class="gl-archive-qty">${i}</span>`:H}
        <span class="gl-archive-ts"
          >${t("archived_on")} ${this._fmtArchiveTs(e.archived_ts)}</span
        >
        <button
          class="gl-icon-btn"
          title=${t("restore")}
          @click=${()=>this._restoreArchived(e)}
        >\u21a9</button>
      </li>
    `}_restoreArchived(e){const t=this._activeSlug;t&&this._api?.restoreArchived(t,e.item.category,e.item.name)}_fmtArchiveTs(e){const t=new Date(e);return isNaN(t.getTime())?e:t.toLocaleDateString(this._lang,{year:"numeric",month:"short",day:"numeric"})}_renderSettings(e){const t=this._snapshot?.lists??[],i=this._activeList(),n=i?.category_order??[];return D`
      <div
        class="gl-overlay"
        @click=${e=>{e.target===e.currentTarget&&this._closeSettings()}}
      >
        <div class="gl-sheet">
          <div class="gl-sheet-header">
            <h3>${e("settings")}</h3>
            <button
              class="gl-icon-btn"
              title=${e("close")}
              @click=${()=>this._closeSettings()}
            >\u2715</button>
          </div>

          <div class="gl-settings-section">
            <div class="gl-section-title">${e("lists")}</div>
            ${t.length?D`<ul class="gl-catlist">
                  ${t.map(i=>this._renderListRow(i,t.length,e))}
                </ul>`:D`<div class="gl-empty">${e("no_lists")}</div>`}
            <div class="gl-cat-new">
              <input
                .value=${this._newListName}
                placeholder=${e("list_name")}
                @input=${e=>this._newListName=e.target.value}
                @keydown=${e=>{"Enter"===e.key&&this._commitNewList()}}
              />
              <button class="gl-add-btn" @click=${()=>this._commitNewList()}>
                ${e("add_list")}
              </button>
            </div>
          </div>

          <div class="gl-settings-section">
            <div class="gl-section-title">
              ${e("categories")}${i?D` — <span class="gl-section-title-list"
                    >${i.title}</span
                  >`:""}
            </div>
            ${i&&n.length?D`<ul class="gl-catlist">
                  ${n.map((t,r)=>this._renderCategoryRow(i.slug,t,r,n.length,e))}
                </ul>`:D`<div class="gl-empty">${e("no_categories")}</div>`}
          </div>
        </div>
      </div>
    `}_renderCategoryRow(e,t,i,n,r){return D`
      <li class="gl-catrow">
        <span class="gl-cat-label" style="flex:1">${t}</span>
        <button
          class="gl-icon-btn"
          title=${r("move_up")}
          ?disabled=${i<=0}
          @click=${()=>this._moveCategory(e,i,-1)}
        >\u2191</button>
        <button
          class="gl-icon-btn"
          title=${r("move_down")}
          ?disabled=${i>=n-1}
          @click=${()=>this._moveCategory(e,i,1)}
        >\u2193</button>
        <button
          class="gl-icon-btn"
          title=${r("rename_category")}
          @click=${()=>this._renameCategoryPrompt(e,t,r)}
        >\u270e</button>
      </li>
    `}async _renameCategoryPrompt(e,t,i){const n=await this._showPrompt({title:i("rename_category"),message:i("rename_category_prompt"),initial:t,confirmLabel:i("save"),cancelLabel:i("cancel")});if(null===n)return;const r=n.trim();r&&r!==t&&this._api?.renameCategory(e,t,r)}_moveCategory(e,t,i){const n=[...this._activeList()?.category_order??[]],r=t+i;t<0||t>=n.length||r<0||r>=n.length||([n[t],n[r]]=[n[r],n[t]],this._api?.reorderCategories(e,n))}_renderListRow(e,t,i){return D`
      <li class="gl-catrow">
        <span class="gl-cat-label" style="flex:1">${e.title}</span>
        <button
          class="gl-icon-btn"
          title=${i("rename_list")}
          @click=${()=>this._renameListPrompt(e,i)}
        >\u270e</button>
        <button
          class="gl-icon-btn"
          title=${i("delete_list")}
          ?disabled=${t<=1}
          @click=${()=>this._deleteListConfirm(e,i)}
        >\u2715</button>
      </li>
    `}_categories(){const e=new Set(this._snapshot?.categories??[]);for(const t of this._extraCategories)e.add(t);return[...e].sort((e,t)=>e.localeCompare(t))}_registerCategory(e){this._extraCategories.includes(e)||(this._extraCategories=[...this._extraCategories,e])}async _promptNewCategory(e){const t=await this._showPrompt({title:e("new_category"),placeholder:e("category_name"),confirmLabel:e("save"),cancelLabel:e("cancel")});return t&&this._registerCategory(t),t}_showPrompt(e){return this._dialogValue=e.initial??"",new Promise(t=>{this._dialog={kind:"prompt",title:e.title,message:e.message,placeholder:e.placeholder,confirmLabel:e.confirmLabel,cancelLabel:e.cancelLabel,resolve:e=>t("string"==typeof e?e:null)}})}_showConfirm(e){return new Promise(t=>{this._dialog={kind:"confirm",title:e.title,message:e.message,confirmLabel:e.confirmLabel,cancelLabel:e.cancelLabel,danger:e.danger,resolve:e=>t(!0===e)}})}_dialogConfirm(){const e=this._dialog;if(e)if(this._dialog=void 0,"prompt"===e.kind){const t=this._dialogValue.trim();e.resolve(t||null)}else e.resolve(!0)}_dialogCancel(){const e=this._dialog;e&&(this._dialog=void 0,e.resolve("prompt"===e.kind&&null))}_renderDialog(){const e=this._dialog;return D`
      <div
        class="gl-overlay"
        @click=${e=>{e.target===e.currentTarget&&this._dialogCancel()}}
      >
        <div
          class="gl-dialog"
          role="dialog"
          aria-modal="true"
          @keydown=${t=>{"Escape"===t.key&&this._dialogCancel(),"Enter"===t.key&&"prompt"===e.kind&&this._dialogConfirm()}}
        >
          <h3 class="gl-dialog-title">${e.title}</h3>
          ${e.message?D`<p class="gl-dialog-msg">${e.message}</p>`:H}
          ${"prompt"===e.kind?D`<input
                class="gl-dialog-input"
                .value=${this._dialogValue}
                placeholder=${e.placeholder??""}
                @input=${e=>this._dialogValue=e.target.value}
                autofocus
              />`:H}
          <div class="gl-dialog-actions">
            <button
              class="gl-btn gl-btn-text"
              @click=${()=>this._dialogCancel()}
            >
              ${e.cancelLabel}
            </button>
            <button
              class="gl-btn ${e.danger?"gl-btn-danger":"gl-btn-primary"}"
              @click=${()=>this._dialogConfirm()}
            >
              ${e.confirmLabel}
            </button>
          </div>
        </div>
      </div>
    `}_unitLabel(e,t){const i=this._asQuantityUnitId(e),n=i?this._units.find(e=>e.id===i):void 0,r=n?.labels[this._lang]??n?.labels.en;return r?"string"==typeof r?r:void 0===t||1===t?r.one:r.other:e}_asQuantityUnitId(e){const t=e?.trim().toLowerCase();if(t)return Object.values(fe).includes(t)?t:void 0}_fmtNum(e){return Number.isInteger(e)?String(e):e.toFixed(2).replace(/0+$/,"")}_canQuickAdjustQty(e){return void 0!==this._quickQtyStep(e)}_quickQtyStep(e){const t=this._asQuantityUnitId(e);return t?ke[t]:void 0}_roundQuickQty(e){return Math.max(1,Math.round(100*e)/100)}_nextQuickQty(e,t,i){if(t<=0||0===i)return this._roundQuickQty(e);const n=e/t,r=i>0?Math.floor(n+1e-9)+i:Math.ceil(n-1e-9)+i;return this._roundQuickQty(r*t)}_handleQtyPointerDown(e,t,i){const n=this._asQuantityUnitId(i.qty?.unit)??this._defaultUnit,r=this._quickQtyStep(n);if(0!==e.button||void 0===r)return;this._cancelQtySwipe();const s=this.ownerDocument.defaultView,a=e=>this._handleQtyPointerMove(e),o=e=>this._handleQtyPointerEnd(e),l=e=>this._handleQtyPointerCancel(e);s?.addEventListener("pointermove",a,!0),s?.addEventListener("pointerup",o,!0),s?.addEventListener("pointercancel",l,!0),this._qtySwipe={slug:t,item:i,pointerId:e.pointerId,cleanup:()=>{s?.removeEventListener("pointermove",a,!0),s?.removeEventListener("pointerup",o,!0),s?.removeEventListener("pointercancel",l,!0)},startX:e.clientX,startY:e.clientY,startValue:i.qty?.value??1,previewValue:i.qty?.value??1,unit:n,pulseKey:0}}_handleQtyPointerMove(e){const t=this._qtySwipe;if(!t||t.pointerId!==e.pointerId)return;const i=e.clientX-t.startX,n=e.clientY-t.startY,r=this._quickQtyStep(t.unit),s=Math.abs(i)>=32&&Math.abs(i)>Math.abs(n),a=void 0!==r&&s?Math.trunc(i/32):0,o=this._nextQuickQty(t.startValue,r??0,a);if(o!==t.previewValue){const e=t.pulseKey+1;this._qtySwipe={...t,previewValue:o,pulseKey:e}}s&&e.preventDefault()}_handleQtyPointerEnd(e){const t=this._qtySwipe;if(!t||t.pointerId!==e.pointerId)return;const i=t.previewValue!==t.startValue;this._cancelQtySwipe(),i&&this._setQtyValue(t.slug,t.item,t.previewValue),i||this.requestUpdate()}_handleQtyPointerCancel(e){const t=this._qtySwipe;t&&t.pointerId===e.pointerId&&(this._cancelQtySwipe(),this.requestUpdate())}_cancelQtySwipe(){const e=this._qtySwipe;e&&(this._qtySwipe=void 0,e.cleanup())}_setQtyValue(e,t,i){this._api?.updateItem(e,t.category,t.name,{qty_value:Math.max(1,i),qty_unit:this._asQuantityUnitId(t.qty?.unit)??this._defaultUnit})}_bumpQty(e){this._draftQty=Math.max(1,Math.round(100*(this._draftQty+e))/100)}_beginEdit(e){this._editingId=xe(e),this._editValue=e.name,this._editQty=e.qty?.value??1,this._editUnit=this._asQuantityUnitId(e.qty?.unit)??this._defaultUnit,this._editCategory=e.category}_cancelEdit(){this._editingId=null,this._editValue="",this._editQty=1,this._editUnit=this._defaultUnit,this._editCategory=null}_bumpEditQty(e){this._editQty=Math.max(1,Math.round(100*(this._editQty+e))/100)}async _deleteItemConfirm(e,t,i){await this._showConfirm({title:i("delete"),message:i("delete_item_confirm"),confirmLabel:i("delete"),cancelLabel:i("cancel"),danger:!0})&&(this._cancelEdit(),this._api?.deleteItem(e,t.category,t.name))}_saveEdit(e,t){const i=this._editValue.trim();if(!i||!this._api)return void this._cancelEdit();const n={};i!==t.name&&(n.new_name=i),this._editCategory!==t.category&&(n.new_category=this._editCategory);const r=Math.max(1,this._editQty||1),s=t.qty?.value??null,a=this._editUnit||this._defaultUnit,o=t.qty?.unit??null;r===s&&a===o||(n.qty_value=r,n.qty_unit=a),Object.keys(n).length&&this._api.updateItem(e,t.category,t.name,n),this._cancelEdit()}_commitAdd(){const e=this._draftName.trim();if(!e||!this._api)return;const t=this._targetSlug();this._api.addItem(t,e,{category:this._draftCategory,qty_value:Math.max(1,this._draftQty||1),qty_unit:this._draftUnit||this._defaultUnit}),this._activeSlug=t,this._draftName="",this._addOpen=!1}_closeSettings(){this._settingsOpen=!1,this._newListName=""}async _commitNewList(){const e=this._newListName.trim();if(e&&this._api){this._newListName="";try{const t=await this._api.createList(e);t?.list?.slug&&(this._activeSlug=t.list.slug)}catch(e){}}}async _renameListPrompt(e,t){const i=await this._showPrompt({title:t("rename_list"),message:t("rename_list_prompt"),initial:e.title,confirmLabel:t("save"),cancelLabel:t("cancel")});if(null===i)return;const n=i.trim();n&&n!==e.title&&this._api?.renameList(e.slug,n)}async _deleteListConfirm(e,t){if(await this._showConfirm({title:t("delete_list"),message:t("delete_list_confirm"),confirmLabel:t("delete"),cancelLabel:t("cancel"),danger:!0})&&(this._api?.deleteList(e.slug),this._activeSlug===e.slug)){const t=(this._snapshot?.lists??[]).filter(t=>t.slug!==e.slug);this._activeSlug=t[0]?.slug}}};Ae.styles=ue,e([ge({attribute:!1})],Ae.prototype,"hass",void 0),e([he()],Ae.prototype,"_config",void 0),e([he()],Ae.prototype,"_snapshot",void 0),e([he()],Ae.prototype,"_units",void 0),e([he()],Ae.prototype,"_defaultUnit",void 0),e([he()],Ae.prototype,"_activeSlug",void 0),e([he()],Ae.prototype,"_editingId",void 0),e([he()],Ae.prototype,"_editValue",void 0),e([he()],Ae.prototype,"_editQty",void 0),e([he()],Ae.prototype,"_editUnit",void 0),e([he()],Ae.prototype,"_editCategory",void 0),e([he()],Ae.prototype,"_extraCategories",void 0),e([he()],Ae.prototype,"_addOpen",void 0),e([he()],Ae.prototype,"_draftName",void 0),e([he()],Ae.prototype,"_draftQty",void 0),e([he()],Ae.prototype,"_draftUnit",void 0),e([he()],Ae.prototype,"_draftCategory",void 0),e([he()],Ae.prototype,"_settingsOpen",void 0),e([he()],Ae.prototype,"_archiveOpen",void 0),e([he()],Ae.prototype,"_dialog",void 0),e([he()],Ae.prototype,"_dialogValue",void 0),e([he()],Ae.prototype,"_newListName",void 0),e([he()],Ae.prototype,"_qtySwipe",void 0),Ae=e([le("grocery-list-card")],Ae);let Se=class extends ae{constructor(){super(...arguments),this._config={type:"custom:grocery-list-card",entry_id:""},this._entries=[]}setConfig(e){this._config=e??{type:"custom:grocery-list-card",entry_id:""}}connectedCallback(){super.connectedCallback(),this._loadEntries()}async _loadEntries(){if(this.hass)try{const e=await this.hass.connection.sendMessagePromise({type:"config_entries/get",domain:"grocery_list"});this._entries=e.filter(e=>"grocery_list"===e.domain).map(e=>({entry_id:e.entry_id,title:e.title}))}catch(e){this._entries=[]}}get _lang(){return ye(this.hass?.locale?.language??this.hass?.language)}_emit(e){this._config=e,this.dispatchEvent(new CustomEvent("config-changed",{detail:{config:e},bubbles:!0,composed:!0}))}render(){const e=ve(this._lang);return D`
      <div class="gl-editor">
        <label>${e("select_list_entry")}</label>
        ${this._entries.length?D`<select
              .value=${this._config.entry_id}
              @change=${e=>this._emit({...this._config,entry_id:e.target.value})}
            >
              <option value="" ?selected=${!this._config.entry_id}></option>
              ${this._entries.map(e=>D`<option
                  value=${e.entry_id}
                  ?selected=${e.entry_id===this._config.entry_id}
                >
                  ${e.title||e.entry_id}
                </option>`)}
            </select>`:D`<p>${e("no_entries")}</p>`}
        <label>${e("title")}</label>
        <input
          .value=${this._config.title??""}
          @input=${e=>{const t=e.target.value;this._emit({...this._config,title:t||void 0})}}
        />
      </div>
    `}};e([ge({attribute:!1})],Se.prototype,"hass",void 0),e([he()],Se.prototype,"_config",void 0),e([he()],Se.prototype,"_entries",void 0),Se=e([le("grocery-list-card-editor")],Se);const ze={en:{name:"Grocery List Card",description:"A slick, mobile-first grocery list with categories and sync."},de:{name:"Einkaufslisten-Karte",description:"Eine schicke, mobil-optimierte Einkaufsliste mit Kategorien und Sync."}},Ce=ze[ye("undefined"!=typeof navigator?navigator.language:void 0)]??ze.en;window.customCards=window.customCards||[],window.customCards.push({type:"grocery-list-card",name:Ce.name,description:Ce.description,preview:!0,documentationURL:"https://codeberg.org/Apollo3zehn/ha-grocery-list"});export{Ae as GroceryListCard,Se as GroceryListCardEditor};
