function e(e,t,i,s){var n,r=arguments.length,a=r<3?t:null===s?s=Object.getOwnPropertyDescriptor(t,i):s;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)a=Reflect.decorate(e,t,i,s);else for(var o=e.length-1;o>=0;o--)(n=e[o])&&(a=(r<3?n(a):r>3?n(t,i,a):n(t,i))||a);return r>3&&a&&Object.defineProperty(t,i,a),a}"function"==typeof SuppressedError&&SuppressedError;const t=globalThis,i=t.ShadowRoot&&(void 0===t.ShadyCSS||t.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,s=Symbol(),n=new WeakMap;let r=class{constructor(e,t,i){if(this._$cssResult$=!0,i!==s)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o;const t=this.t;if(i&&void 0===e){const i=void 0!==t&&1===t.length;i&&(e=n.get(t)),void 0===e&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),i&&n.set(t,e))}return e}toString(){return this.cssText}};const a=i?e=>e:e=>e instanceof CSSStyleSheet?(e=>{let t="";for(const i of e.cssRules)t+=i.cssText;return(e=>new r("string"==typeof e?e:e+"",void 0,s))(t)})(e):e,{is:o,defineProperty:l,getOwnPropertyDescriptor:c,getOwnPropertyNames:d,getOwnPropertySymbols:h,getPrototypeOf:g}=Object,u=globalThis,_=u.trustedTypes,p=_?_.emptyScript:"",m=u.reactiveElementPolyfillSupport,y=(e,t)=>e,v={toAttribute(e,t){switch(t){case Boolean:e=e?p:null;break;case Object:case Array:e=null==e?e:JSON.stringify(e)}return e},fromAttribute(e,t){let i=e;switch(t){case Boolean:i=null!==e;break;case Number:i=null===e?null:Number(e);break;case Object:case Array:try{i=JSON.parse(e)}catch(e){i=null}}return i}},f=(e,t)=>!o(e,t),b={attribute:!0,type:String,converter:v,reflect:!1,useDefault:!1,hasChanged:f};Symbol.metadata??=Symbol("metadata"),u.litPropertyMetadata??=new WeakMap;let $=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=b){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){const i=Symbol(),s=this.getPropertyDescriptor(e,i,t);void 0!==s&&l(this.prototype,e,s)}}static getPropertyDescriptor(e,t,i){const{get:s,set:n}=c(this.prototype,e)??{get(){return this[t]},set(e){this[t]=e}};return{get:s,set(t){const r=s?.call(this);n?.call(this,t),this.requestUpdate(e,r,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??b}static _$Ei(){if(this.hasOwnProperty(y("elementProperties")))return;const e=g(this);e.finalize(),void 0!==e.l&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(y("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(y("properties"))){const e=this.properties,t=[...d(e),...h(e)];for(const i of t)this.createProperty(i,e[i])}const e=this[Symbol.metadata];if(null!==e){const t=litPropertyMetadata.get(e);if(void 0!==t)for(const[e,i]of t)this.elementProperties.set(e,i)}this._$Eh=new Map;for(const[e,t]of this.elementProperties){const i=this._$Eu(e,t);void 0!==i&&this._$Eh.set(i,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){const t=[];if(Array.isArray(e)){const i=new Set(e.flat(1/0).reverse());for(const e of i)t.unshift(a(e))}else void 0!==e&&t.push(a(e));return t}static _$Eu(e,t){const i=t.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof e?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),void 0!==this.renderRoot&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){const e=new Map,t=this.constructor.elementProperties;for(const i of t.keys())this.hasOwnProperty(i)&&(e.set(i,this[i]),delete this[i]);e.size>0&&(this._$Ep=e)}createRenderRoot(){const e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return((e,s)=>{if(i)e.adoptedStyleSheets=s.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(const i of s){const s=document.createElement("style"),n=t.litNonce;void 0!==n&&s.setAttribute("nonce",n),s.textContent=i.cssText,e.appendChild(s)}})(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,i){this._$AK(e,i)}_$ET(e,t){const i=this.constructor.elementProperties.get(e),s=this.constructor._$Eu(e,i);if(void 0!==s&&!0===i.reflect){const n=(void 0!==i.converter?.toAttribute?i.converter:v).toAttribute(t,i.type);this._$Em=e,null==n?this.removeAttribute(s):this.setAttribute(s,n),this._$Em=null}}_$AK(e,t){const i=this.constructor,s=i._$Eh.get(e);if(void 0!==s&&this._$Em!==s){const e=i.getPropertyOptions(s),n="function"==typeof e.converter?{fromAttribute:e.converter}:void 0!==e.converter?.fromAttribute?e.converter:v;this._$Em=s;const r=n.fromAttribute(t,e.type);this[s]=r??this._$Ej?.get(s)??r,this._$Em=null}}requestUpdate(e,t,i,s=!1,n){if(void 0!==e){const r=this.constructor;if(!1===s&&(n=this[e]),i??=r.getPropertyOptions(e),!((i.hasChanged??f)(n,t)||i.useDefault&&i.reflect&&n===this._$Ej?.get(e)&&!this.hasAttribute(r._$Eu(e,i))))return;this.C(e,t,i)}!1===this.isUpdatePending&&(this._$ES=this._$EP())}C(e,t,{useDefault:i,reflect:s,wrapped:n},r){i&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,r??t??this[e]),!0!==n||void 0!==r)||(this._$AL.has(e)||(this.hasUpdated||i||(t=void 0),this._$AL.set(e,t)),!0===s&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}const e=this.scheduleUpdate();return null!=e&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[e,t]of this._$Ep)this[e]=t;this._$Ep=void 0}const e=this.constructor.elementProperties;if(e.size>0)for(const[t,i]of e){const{wrapped:e}=i,s=this[t];!0!==e||this._$AL.has(t)||void 0===s||this.C(t,void 0,i,s)}}let e=!1;const t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(e=>e.hostUpdate?.()),this.update(t)):this._$EM()}catch(t){throw e=!1,this._$EM(),t}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(e){}firstUpdated(e){}};$.elementStyles=[],$.shadowRootOptions={mode:"open"},$[y("elementProperties")]=new Map,$[y("finalized")]=new Map,m?.({ReactiveElement:$}),(u.reactiveElementVersions??=[]).push("2.1.2");const w=globalThis,k=e=>e,A=w.trustedTypes,x=A?A.createPolicy("lit-html",{createHTML:e=>e}):void 0,S="$lit$",E=`lit$${Math.random().toFixed(9).slice(2)}$`,z="?"+E,C=`<${z}>`,N=document,L=()=>N.createComment(""),j=e=>null===e||"object"!=typeof e&&"function"!=typeof e,U=Array.isArray,R="[ \t\n\f\r]",P=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,O=/-->/g,M=/>/g,I=RegExp(`>|${R}(?:([^\\s"'>=/]+)(${R}*=${R}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),T=/'/g,q=/"/g,H=/^(?:script|style|textarea|title)$/i,D=(e=>(t,...i)=>({_$litType$:e,strings:t,values:i}))(1),Q=Symbol.for("lit-noChange"),G=Symbol.for("lit-nothing"),V=new WeakMap,B=N.createTreeWalker(N,129);function W(e,t){if(!U(e)||!e.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==x?x.createHTML(t):t}const F=(e,t)=>{const i=e.length-1,s=[];let n,r=2===t?"<svg>":3===t?"<math>":"",a=P;for(let t=0;t<i;t++){const i=e[t];let o,l,c=-1,d=0;for(;d<i.length&&(a.lastIndex=d,l=a.exec(i),null!==l);)d=a.lastIndex,a===P?"!--"===l[1]?a=O:void 0!==l[1]?a=M:void 0!==l[2]?(H.test(l[2])&&(n=RegExp("</"+l[2],"g")),a=I):void 0!==l[3]&&(a=I):a===I?">"===l[0]?(a=n??P,c=-1):void 0===l[1]?c=-2:(c=a.lastIndex-l[2].length,o=l[1],a=void 0===l[3]?I:'"'===l[3]?q:T):a===q||a===T?a=I:a===O||a===M?a=P:(a=I,n=void 0);const h=a===I&&e[t+1].startsWith("/>")?" ":"";r+=a===P?i+C:c>=0?(s.push(o),i.slice(0,c)+S+i.slice(c)+E+h):i+E+(-2===c?t:h)}return[W(e,r+(e[i]||"<?>")+(2===t?"</svg>":3===t?"</math>":"")),s]};class K{constructor({strings:e,_$litType$:t},i){let s;this.parts=[];let n=0,r=0;const a=e.length-1,o=this.parts,[l,c]=F(e,t);if(this.el=K.createElement(l,i),B.currentNode=this.el.content,2===t||3===t){const e=this.el.content.firstChild;e.replaceWith(...e.childNodes)}for(;null!==(s=B.nextNode())&&o.length<a;){if(1===s.nodeType){if(s.hasAttributes())for(const e of s.getAttributeNames())if(e.endsWith(S)){const t=c[r++],i=s.getAttribute(e).split(E),a=/([.?@])?(.*)/.exec(t);o.push({type:1,index:n,name:a[2],strings:i,ctor:"."===a[1]?ee:"?"===a[1]?te:"@"===a[1]?ie:X}),s.removeAttribute(e)}else e.startsWith(E)&&(o.push({type:6,index:n}),s.removeAttribute(e));if(H.test(s.tagName)){const e=s.textContent.split(E),t=e.length-1;if(t>0){s.textContent=A?A.emptyScript:"";for(let i=0;i<t;i++)s.append(e[i],L()),B.nextNode(),o.push({type:2,index:++n});s.append(e[t],L())}}}else if(8===s.nodeType)if(s.data===z)o.push({type:2,index:n});else{let e=-1;for(;-1!==(e=s.data.indexOf(E,e+1));)o.push({type:7,index:n}),e+=E.length-1}n++}}static createElement(e,t){const i=N.createElement("template");return i.innerHTML=e,i}}function Z(e,t,i=e,s){if(t===Q)return t;let n=void 0!==s?i._$Co?.[s]:i._$Cl;const r=j(t)?void 0:t._$litDirective$;return n?.constructor!==r&&(n?._$AO?.(!1),void 0===r?n=void 0:(n=new r(e),n._$AT(e,i,s)),void 0!==s?(i._$Co??=[])[s]=n:i._$Cl=n),void 0!==n&&(t=Z(e,n._$AS(e,t.values),n,s)),t}class Y{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){const{el:{content:t},parts:i}=this._$AD,s=(e?.creationScope??N).importNode(t,!0);B.currentNode=s;let n=B.nextNode(),r=0,a=0,o=i[0];for(;void 0!==o;){if(r===o.index){let t;2===o.type?t=new J(n,n.nextSibling,this,e):1===o.type?t=new o.ctor(n,o.name,o.strings,this,e):6===o.type&&(t=new se(n,this,e)),this._$AV.push(t),o=i[++a]}r!==o?.index&&(n=B.nextNode(),r++)}return B.currentNode=N,s}p(e){let t=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(e,i,t),t+=i.strings.length-2):i._$AI(e[t])),t++}}class J{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,i,s){this.type=2,this._$AH=G,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=i,this.options=s,this._$Cv=s?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode;const t=this._$AM;return void 0!==t&&11===e?.nodeType&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=Z(this,e,t),j(e)?e===G||null==e||""===e?(this._$AH!==G&&this._$AR(),this._$AH=G):e!==this._$AH&&e!==Q&&this._(e):void 0!==e._$litType$?this.$(e):void 0!==e.nodeType?this.T(e):(e=>U(e)||"function"==typeof e?.[Symbol.iterator])(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==G&&j(this._$AH)?this._$AA.nextSibling.data=e:this.T(N.createTextNode(e)),this._$AH=e}$(e){const{values:t,_$litType$:i}=e,s="number"==typeof i?this._$AC(e):(void 0===i.el&&(i.el=K.createElement(W(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===s)this._$AH.p(t);else{const e=new Y(s,this),i=e.u(this.options);e.p(t),this.T(i),this._$AH=e}}_$AC(e){let t=V.get(e.strings);return void 0===t&&V.set(e.strings,t=new K(e)),t}k(e){U(this._$AH)||(this._$AH=[],this._$AR());const t=this._$AH;let i,s=0;for(const n of e)s===t.length?t.push(i=new J(this.O(L()),this.O(L()),this,this.options)):i=t[s],i._$AI(n),s++;s<t.length&&(this._$AR(i&&i._$AB.nextSibling,s),t.length=s)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){const t=k(e).nextSibling;k(e).remove(),e=t}}setConnected(e){void 0===this._$AM&&(this._$Cv=e,this._$AP?.(e))}}class X{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,i,s,n){this.type=1,this._$AH=G,this._$AN=void 0,this.element=e,this.name=t,this._$AM=s,this.options=n,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=G}_$AI(e,t=this,i,s){const n=this.strings;let r=!1;if(void 0===n)e=Z(this,e,t,0),r=!j(e)||e!==this._$AH&&e!==Q,r&&(this._$AH=e);else{const s=e;let a,o;for(e=n[0],a=0;a<n.length-1;a++)o=Z(this,s[i+a],t,a),o===Q&&(o=this._$AH[a]),r||=!j(o)||o!==this._$AH[a],o===G?e=G:e!==G&&(e+=(o??"")+n[a+1]),this._$AH[a]=o}r&&!s&&this.j(e)}j(e){e===G?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}}class ee extends X{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===G?void 0:e}}class te extends X{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==G)}}class ie extends X{constructor(e,t,i,s,n){super(e,t,i,s,n),this.type=5}_$AI(e,t=this){if((e=Z(this,e,t,0)??G)===Q)return;const i=this._$AH,s=e===G&&i!==G||e.capture!==i.capture||e.once!==i.once||e.passive!==i.passive,n=e!==G&&(i===G||s);s&&this.element.removeEventListener(this.name,this,i),n&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}}class se{constructor(e,t,i){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(e){Z(this,e)}}const ne=w.litHtmlPolyfillSupport;ne?.(K,J),(w.litHtmlVersions??=[]).push("3.3.3");const re=globalThis;class ae extends ${constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){const t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=((e,t,i)=>{const s=i?.renderBefore??t;let n=s._$litPart$;if(void 0===n){const e=i?.renderBefore??null;s._$litPart$=n=new J(t.insertBefore(L(),e),e,void 0,i??{})}return n._$AI(e),n})(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return Q}}ae._$litElement$=!0,ae.finalized=!0,re.litElementHydrateSupport?.({LitElement:ae});const oe=re.litElementPolyfillSupport;oe?.({LitElement:ae}),(re.litElementVersions??=[]).push("4.2.2");const le=e=>(t,i)=>{void 0!==i?i.addInitializer(()=>{customElements.define(e,t)}):customElements.define(e,t)},ce={attribute:!0,type:String,converter:v,reflect:!1,hasChanged:f},de=(e=ce,t,i)=>{const{kind:s,metadata:n}=i;let r=globalThis.litPropertyMetadata.get(n);if(void 0===r&&globalThis.litPropertyMetadata.set(n,r=new Map),"setter"===s&&((e=Object.create(e)).wrapped=!0),r.set(i.name,e),"accessor"===s){const{name:s}=i;return{set(i){const n=t.get.call(this);t.set.call(this,i),this.requestUpdate(s,n,e,!0,i)},init(t){return void 0!==t&&this.C(s,void 0,e,t),t}}}if("setter"===s){const{name:s}=i;return function(i){const n=this[s];t.call(this,i),this.requestUpdate(s,n,e,!0,i)}}throw Error("Unsupported decorator location: "+s)};function he(e){return(t,i)=>"object"==typeof i?de(e,t,i):((e,t,i)=>{const s=t.hasOwnProperty(i);return t.constructor.createProperty(i,e),s?Object.getOwnPropertyDescriptor(t,i):void 0})(e,t,i)}function ge(e){return he({...e,state:!0,attribute:!1})}class ue{constructor(e,t){this.hass=e,this.entryId=t}async subscribe(e,t="en"){return this.hass.connection.subscribeMessage(t=>e(t),{type:"grocery_list/subscribe",entry_id:this.entryId,locale:t})}send(e,t={}){return this.hass.connection.sendMessagePromise({type:`grocery_list/${e}`,entry_id:this.entryId,...t})}addItem(e,t,i={}){return this.send("add_item",{slug:e,name:t,...i})}updateItem(e,t,i){return this.send("update_item",{slug:e,item_id:t,...i})}setChecked(e,t,i){return this.send("set_checked",{slug:e,item_id:t,checked:i})}deleteItem(e,t){return this.send("delete_item",{slug:e,item_id:t})}clearChecked(e){return this.send("clear_checked",{slug:e})}restoreArchived(e,t,i){return this.send("restore_archived",{slug:e,item_id:t,archived_ts:i??null})}createList(e,t){return this.send("create_list",{title:e,slug:t??null})}renameList(e,t){return this.send("rename_list",{slug:e,title:t})}deleteList(e){return this.send("delete_list",{slug:e})}undo(){return this.send("undo")}redo(){return this.send("redo")}sync(){return this.send("sync")}getUnits(){return this.hass.connection.sendMessagePromise({type:"grocery_list/get_units"})}}const _e=((e,...t)=>{const i=1===e.length?e[0]:t.reduce((t,i,s)=>t+(e=>{if(!0===e._$cssResult$)return e.cssText;if("number"==typeof e)return e;throw Error("Value passed to 'css' function must be a 'css' function result: "+e+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+e[s+1],e[0]);return new r(i,e,s)})`
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

  .gl-add {
    display: flex;
    gap: var(--gl-gap);
    align-items: center;
  }
  .gl-add input.gl-name {
    flex: 1 1 auto;
    min-width: 0;
    border: 1px solid var(--gl-divider);
    border-radius: var(--gl-radius);
    padding: 10px 12px;
    font-size: 1rem;
    background: var(--gl-card-bg);
    color: var(--gl-text);
  }
  .gl-add .gl-add-btn {
    background: var(--gl-accent);
    color: #fff;
    border: none;
    border-radius: var(--gl-radius);
    padding: 10px 16px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
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
  .gl-checked-divider {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--gl-muted);
    margin: 6px 4px 2px;
  }

  .gl-group { margin-top: 4px; }
  .gl-group-title {
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--gl-muted);
    margin: 8px 4px 2px;
    display: flex;
    align-items: center;
    gap: 6px;
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

  .gl-item-main { flex: 1 1 auto; min-width: 0; }
  .gl-item-name {
    font-size: 1rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .gl-item-qty {
    font-size: 0.8rem;
    color: var(--gl-muted);
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
    justify-content: flex-end;
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
`,pe={add_placeholder:"Add an item…",add:"Add",qty:"Qty",unit:"Unit",category:"Category",uncategorized:"Uncategorized",clear_checked:"Clear checked",clear_checked_confirm:"Remove all checked items? They move to the archive and can be restored from there.",checked_section:"Checked",restore:"Restore",restore_confirm:"Restore this item to the list?",undo:"Undo",redo:"Redo",sync:"Sync",save:"Save",cancel:"Cancel",delete:"Delete",edit:"Edit",empty_list:"Nothing here yet. Add your first item above.",sync_synced:"Synced",sync_pending:"Pending",sync_syncing:"Syncing…",sync_offline:"Offline",sync_error:"Sync error",settings:"Settings",new_category:"New category",category_name:"Name",close:"Close",archive:"Archive",view_archive:"View archive",no_archive:"Nothing archived yet. Cleared items appear here.",archived_on:"Archived",needs_config:"Grocery List not configured",needs_config_hint:"Open the card editor and pick a Grocery List, or set 'entry_id' in YAML.",select_list_entry:"Grocery List instance",no_entries:"No Grocery List integration found. Add it under Settings → Devices & Services first.",title:"Title (optional)",manage_lists:"Manage lists",lists:"Lists",new_list:"New list",list_name:"List name",add_list:"Add list",no_lists:"No lists yet. Create one above.",rename_list:"Rename list",delete_list:"Delete list",delete_list_confirm:"Delete this list and all its items? This cannot be undone by others once synced.",list_name_prompt:"New list name:",rename_list_prompt:"Rename list to:"},me={en:pe,de:{add_placeholder:"Artikel hinzufügen…",add:"Hinzufügen",qty:"Menge",unit:"Einheit",category:"Kategorie",uncategorized:"Ohne Kategorie",clear_checked:"Erledigte entfernen",clear_checked_confirm:"Alle erledigten Artikel entfernen? Sie wandern ins Archiv und können von dort wiederhergestellt werden.",checked_section:"Erledigt",restore:"Wiederherstellen",restore_confirm:"Diesen Artikel zurück auf die Liste setzen?",undo:"Rückgängig",redo:"Wiederholen",sync:"Sync",save:"Speichern",cancel:"Abbrechen",delete:"Löschen",edit:"Bearbeiten",empty_list:"Noch nichts hier. Füge oben deinen ersten Artikel hinzu.",sync_synced:"Synchronisiert",sync_pending:"Ausstehend",sync_syncing:"Synchronisiere…",sync_offline:"Offline",sync_error:"Sync-Fehler",settings:"Einstellungen",new_category:"Neue Kategorie",category_name:"Name",close:"Schließen",archive:"Archiv",view_archive:"Archiv anzeigen",no_archive:"Noch nichts archiviert. Entfernte Artikel erscheinen hier.",archived_on:"Archiviert",needs_config:"Einkaufsliste nicht konfiguriert",needs_config_hint:"Öffne den Karten-Editor und wähle eine Einkaufsliste, oder setze 'entry_id' im YAML.",select_list_entry:"Einkaufslisten-Instanz",no_entries:"Keine Einkaufslisten-Integration gefunden. Füge sie zuerst unter Einstellungen → Geräte & Dienste hinzu.",title:"Titel (optional)",manage_lists:"Listen verwalten",lists:"Listen",new_list:"Neue Liste",list_name:"Listenname",add_list:"Liste hinzufügen",no_lists:"Noch keine Listen. Erstelle oben eine.",rename_list:"Liste umbenennen",delete_list:"Liste löschen",delete_list_confirm:"Diese Liste und alle ihre Artikel löschen? Nach der Synchronisierung können andere dies nicht rückgängig machen.",list_name_prompt:"Name der neuen Liste:",rename_list_prompt:"Liste umbenennen in:"},es:{add_placeholder:"Añadir un artículo…",add:"Añadir",qty:"Cant.",unit:"Unidad",category:"Categoría",uncategorized:"Sin categoría",clear_checked:"Quitar marcados",clear_checked_confirm:"¿Quitar todos los artículos marcados? Pasan al archivo y pueden restaurarse desde allí.",checked_section:"Marcados",restore:"Restaurar",restore_confirm:"¿Restaurar este artículo a la lista?",undo:"Deshacer",redo:"Rehacer",sync:"Sincronizar",save:"Guardar",cancel:"Cancelar",delete:"Eliminar",edit:"Editar",empty_list:"Aún no hay nada. Añade tu primer artículo arriba.",sync_synced:"Sincronizado",sync_pending:"Pendiente",sync_syncing:"Sincronizando…",sync_offline:"Sin conexión",sync_error:"Error de sincronización",settings:"Ajustes",new_category:"Nueva categoría",category_name:"Nombre",close:"Cerrar",archive:"Archivo",view_archive:"Ver archivo",no_archive:"Aún no hay nada archivado. Los artículos quitados aparecen aquí.",archived_on:"Archivado",needs_config:"Lista de la compra no configurada",needs_config_hint:"Abre el editor de la tarjeta y elige una lista de la compra, o define 'entry_id' en YAML.",select_list_entry:"Instancia de lista de la compra",no_entries:"No se encontró ninguna integración de lista de la compra. Añádela primero en Ajustes → Dispositivos y servicios.",title:"Título (opcional)",manage_lists:"Gestionar listas",lists:"Listas",new_list:"Nueva lista",list_name:"Nombre de la lista",add_list:"Añadir lista",no_lists:"Aún no hay listas. Crea una arriba.",rename_list:"Renombrar lista",delete_list:"Eliminar lista",delete_list_confirm:"¿Eliminar esta lista y todos sus artículos? Una vez sincronizado, otros no podrán deshacerlo.",list_name_prompt:"Nombre de la nueva lista:",rename_list_prompt:"Renombrar lista a:"},fr:{add_placeholder:"Ajouter un article…",add:"Ajouter",qty:"Qté",unit:"Unité",category:"Catégorie",uncategorized:"Sans catégorie",clear_checked:"Effacer les cochés",clear_checked_confirm:"Retirer tous les articles cochés ? Ils passent dans les archives et peuvent y être restaurés.",checked_section:"Cochés",restore:"Restaurer",restore_confirm:"Restaurer cet article dans la liste ?",undo:"Annuler",redo:"Rétablir",sync:"Synchroniser",save:"Enregistrer",cancel:"Annuler",delete:"Supprimer",edit:"Modifier",empty_list:"Rien ici pour l'instant. Ajoutez votre premier article ci-dessus.",sync_synced:"Synchronisé",sync_pending:"En attente",sync_syncing:"Synchronisation…",sync_offline:"Hors ligne",sync_error:"Erreur de synchronisation",settings:"Paramètres",new_category:"Nouvelle catégorie",category_name:"Nom",close:"Fermer",archive:"Archives",view_archive:"Voir les archives",no_archive:"Rien d'archivé pour l'instant. Les articles retirés apparaissent ici.",archived_on:"Archivé",needs_config:"Liste de courses non configurée",needs_config_hint:"Ouvrez l'éditeur de carte et choisissez une liste de courses, ou définissez 'entry_id' dans le YAML.",select_list_entry:"Instance de liste de courses",no_entries:"Aucune intégration de liste de courses trouvée. Ajoutez-la d'abord dans Paramètres → Appareils et services.",title:"Titre (optionnel)",manage_lists:"Gérer les listes",lists:"Listes",new_list:"Nouvelle liste",list_name:"Nom de la liste",add_list:"Ajouter une liste",no_lists:"Aucune liste pour l'instant. Créez-en une ci-dessus.",rename_list:"Renommer la liste",delete_list:"Supprimer la liste",delete_list_confirm:"Supprimer cette liste et tous ses articles ? Une fois synchronisé, les autres ne pourront pas l'annuler.",list_name_prompt:"Nom de la nouvelle liste :",rename_list_prompt:"Renommer la liste en :"},it:{add_placeholder:"Aggiungi un articolo…",add:"Aggiungi",qty:"Qtà",unit:"Unità",category:"Categoria",uncategorized:"Senza categoria",clear_checked:"Rimuovi selezionati",clear_checked_confirm:"Rimuovere tutti gli articoli selezionati? Vengono spostati nell'archivio e possono essere ripristinati da lì.",checked_section:"Selezionati",restore:"Ripristina",restore_confirm:"Ripristinare questo articolo nella lista?",undo:"Annulla",redo:"Ripeti",sync:"Sincronizza",save:"Salva",cancel:"Annulla",delete:"Elimina",edit:"Modifica",empty_list:"Ancora niente qui. Aggiungi il tuo primo articolo sopra.",sync_synced:"Sincronizzato",sync_pending:"In attesa",sync_syncing:"Sincronizzazione…",sync_offline:"Non in linea",sync_error:"Errore di sincronizzazione",settings:"Impostazioni",new_category:"Nuova categoria",category_name:"Nome",close:"Chiudi",archive:"Archivio",view_archive:"Visualizza archivio",no_archive:"Ancora niente in archivio. Gli articoli rimossi appaiono qui.",archived_on:"Archiviato",needs_config:"Lista della spesa non configurata",needs_config_hint:"Apri l'editor della scheda e scegli una lista della spesa, oppure imposta 'entry_id' nello YAML.",select_list_entry:"Istanza della lista della spesa",no_entries:"Nessuna integrazione della lista della spesa trovata. Aggiungila prima in Impostazioni → Dispositivi e servizi.",title:"Titolo (opzionale)",manage_lists:"Gestisci liste",lists:"Liste",new_list:"Nuova lista",list_name:"Nome della lista",add_list:"Aggiungi lista",no_lists:"Ancora nessuna lista. Creane una sopra.",rename_list:"Rinomina lista",delete_list:"Elimina lista",delete_list_confirm:"Eliminare questa lista e tutti i suoi articoli? Una volta sincronizzato, altri non potranno annullarlo.",list_name_prompt:"Nome della nuova lista:",rename_list_prompt:"Rinomina lista in:"},pt:{add_placeholder:"Adicionar um artigo…",add:"Adicionar",qty:"Qtd.",unit:"Unidade",category:"Categoria",uncategorized:"Sem categoria",clear_checked:"Remover marcados",clear_checked_confirm:"Remover todos os artigos marcados? Passam para o arquivo e podem ser restaurados a partir daí.",checked_section:"Marcados",restore:"Restaurar",restore_confirm:"Restaurar este artigo para a lista?",undo:"Desfazer",redo:"Refazer",sync:"Sincronizar",save:"Guardar",cancel:"Cancelar",delete:"Eliminar",edit:"Editar",empty_list:"Ainda nada aqui. Adicione o seu primeiro artigo acima.",sync_synced:"Sincronizado",sync_pending:"Pendente",sync_syncing:"A sincronizar…",sync_offline:"Offline",sync_error:"Erro de sincronização",settings:"Definições",new_category:"Nova categoria",category_name:"Nome",close:"Fechar",archive:"Arquivo",view_archive:"Ver arquivo",no_archive:"Ainda nada arquivado. Os artigos removidos aparecem aqui.",archived_on:"Arquivado",needs_config:"Lista de compras não configurada",needs_config_hint:"Abra o editor do cartão e escolha uma lista de compras, ou defina 'entry_id' no YAML.",select_list_entry:"Instância da lista de compras",no_entries:"Nenhuma integração de lista de compras encontrada. Adicione-a primeiro em Definições → Dispositivos e serviços.",title:"Título (opcional)",manage_lists:"Gerir listas",lists:"Listas",new_list:"Nova lista",list_name:"Nome da lista",add_list:"Adicionar lista",no_lists:"Ainda sem listas. Crie uma acima.",rename_list:"Renomear lista",delete_list:"Eliminar lista",delete_list_confirm:"Eliminar esta lista e todos os seus artigos? Após a sincronização, outros não poderão desfazer.",list_name_prompt:"Nome da nova lista:",rename_list_prompt:"Renomear lista para:"},nl:{add_placeholder:"Een item toevoegen…",add:"Toevoegen",qty:"Aantal",unit:"Eenheid",category:"Categorie",uncategorized:"Zonder categorie",clear_checked:"Afgevinkte wissen",clear_checked_confirm:"Alle afgevinkte items verwijderen? Ze gaan naar het archief en kunnen daar worden hersteld.",checked_section:"Afgevinkt",restore:"Herstellen",restore_confirm:"Dit item terugzetten op de lijst?",undo:"Ongedaan maken",redo:"Opnieuw",sync:"Synchroniseren",save:"Opslaan",cancel:"Annuleren",delete:"Verwijderen",edit:"Bewerken",empty_list:"Nog niets hier. Voeg hierboven je eerste item toe.",sync_synced:"Gesynchroniseerd",sync_pending:"In behandeling",sync_syncing:"Synchroniseren…",sync_offline:"Offline",sync_error:"Synchronisatiefout",settings:"Instellingen",new_category:"Nieuwe categorie",category_name:"Naam",close:"Sluiten",archive:"Archief",view_archive:"Archief bekijken",no_archive:"Nog niets gearchiveerd. Verwijderde items verschijnen hier.",archived_on:"Gearchiveerd",needs_config:"Boodschappenlijst niet geconfigureerd",needs_config_hint:"Open de kaarteditor en kies een boodschappenlijst, of stel 'entry_id' in de YAML in.",select_list_entry:"Boodschappenlijst-instantie",no_entries:"Geen boodschappenlijst-integratie gevonden. Voeg deze eerst toe via Instellingen → Apparaten en diensten.",title:"Titel (optioneel)",manage_lists:"Lijsten beheren",lists:"Lijsten",new_list:"Nieuwe lijst",list_name:"Lijstnaam",add_list:"Lijst toevoegen",no_lists:"Nog geen lijsten. Maak er hierboven een.",rename_list:"Lijst hernoemen",delete_list:"Lijst verwijderen",delete_list_confirm:"Deze lijst en al haar items verwijderen? Na synchronisatie kunnen anderen dit niet ongedaan maken.",list_name_prompt:"Naam van de nieuwe lijst:",rename_list_prompt:"Lijst hernoemen naar:"},pl:{add_placeholder:"Dodaj artykuł…",add:"Dodaj",qty:"Il.",unit:"Jednostka",category:"Kategoria",uncategorized:"Bez kategorii",clear_checked:"Usuń zaznaczone",clear_checked_confirm:"Usunąć wszystkie zaznaczone artykuły? Trafiają do archiwum i można je stamtąd przywrócić.",checked_section:"Zaznaczone",restore:"Przywróć",restore_confirm:"Przywrócić ten artykuł na listę?",undo:"Cofnij",redo:"Ponów",sync:"Synchronizuj",save:"Zapisz",cancel:"Anuluj",delete:"Usuń",edit:"Edytuj",empty_list:"Jeszcze nic tu nie ma. Dodaj swój pierwszy artykuł powyżej.",sync_synced:"Zsynchronizowano",sync_pending:"Oczekuje",sync_syncing:"Synchronizacja…",sync_offline:"Offline",sync_error:"Błąd synchronizacji",settings:"Ustawienia",new_category:"Nowa kategoria",category_name:"Nazwa",close:"Zamknij",archive:"Archiwum",view_archive:"Pokaż archiwum",no_archive:"Nic jeszcze nie zarchiwizowano. Usunięte artykuły pojawiają się tutaj.",archived_on:"Zarchiwizowano",needs_config:"Lista zakupów nie skonfigurowana",needs_config_hint:"Otwórz edytor karty i wybierz listę zakupów lub ustaw 'entry_id' w YAML.",select_list_entry:"Instancja listy zakupów",no_entries:"Nie znaleziono integracji listy zakupów. Dodaj ją najpierw w Ustawienia → Urządzenia i usługi.",title:"Tytuł (opcjonalny)",manage_lists:"Zarządzaj listami",lists:"Listy",new_list:"Nowa lista",list_name:"Nazwa listy",add_list:"Dodaj listę",no_lists:"Brak list. Utwórz jedną powyżej.",rename_list:"Zmień nazwę listy",delete_list:"Usuń listę",delete_list_confirm:"Usunąć tę listę i wszystkie jej artykuły? Po synchronizacji inni nie będą mogli tego cofnąć.",list_name_prompt:"Nazwa nowej listy:",rename_list_prompt:"Zmień nazwę listy na:"},sv:{add_placeholder:"Lägg till en vara…",add:"Lägg till",qty:"Antal",unit:"Enhet",category:"Kategori",uncategorized:"Utan kategori",clear_checked:"Rensa markerade",clear_checked_confirm:"Ta bort alla markerade varor? De flyttas till arkivet och kan återställas därifrån.",checked_section:"Markerade",restore:"Återställ",restore_confirm:"Återställ denna vara till listan?",undo:"Ångra",redo:"Gör om",sync:"Synkronisera",save:"Spara",cancel:"Avbryt",delete:"Ta bort",edit:"Redigera",empty_list:"Inget här ännu. Lägg till din första vara ovan.",sync_synced:"Synkroniserad",sync_pending:"Väntar",sync_syncing:"Synkroniserar…",sync_offline:"Offline",sync_error:"Synkroniseringsfel",settings:"Inställningar",new_category:"Ny kategori",category_name:"Namn",close:"Stäng",archive:"Arkiv",view_archive:"Visa arkiv",no_archive:"Inget arkiverat ännu. Borttagna varor visas här.",archived_on:"Arkiverad",needs_config:"Inköpslista inte konfigurerad",needs_config_hint:"Öppna kortredigeraren och välj en inköpslista, eller ange 'entry_id' i YAML.",select_list_entry:"Inköpslista-instans",no_entries:"Ingen inköpslista-integration hittades. Lägg till den först under Inställningar → Enheter och tjänster.",title:"Titel (valfritt)",manage_lists:"Hantera listor",lists:"Listor",new_list:"Ny lista",list_name:"Listnamn",add_list:"Lägg till lista",no_lists:"Inga listor ännu. Skapa en ovan.",rename_list:"Byt namn på lista",delete_list:"Ta bort lista",delete_list_confirm:"Ta bort denna lista och alla dess varor? När den synkroniserats kan andra inte ångra det.",list_name_prompt:"Namn på den nya listan:",rename_list_prompt:"Byt namn på listan till:"},nb:{add_placeholder:"Legg til en vare…",add:"Legg til",qty:"Ant.",unit:"Enhet",category:"Kategori",uncategorized:"Uten kategori",clear_checked:"Fjern avkryssede",clear_checked_confirm:"Fjerne alle avkryssede varer? De flyttes til arkivet og kan gjenopprettes derfra.",checked_section:"Avkrysset",restore:"Gjenopprett",restore_confirm:"Gjenopprette denne varen til listen?",undo:"Angre",redo:"Gjenta",sync:"Synkroniser",save:"Lagre",cancel:"Avbryt",delete:"Slett",edit:"Rediger",empty_list:"Ingenting her ennå. Legg til din første vare ovenfor.",sync_synced:"Synkronisert",sync_pending:"Venter",sync_syncing:"Synkroniserer…",sync_offline:"Frakoblet",sync_error:"Synkroniseringsfeil",settings:"Innstillinger",new_category:"Ny kategori",category_name:"Navn",close:"Lukk",archive:"Arkiv",view_archive:"Vis arkiv",no_archive:"Ingenting arkivert ennå. Fjernede varer vises her.",archived_on:"Arkivert",needs_config:"Handleliste ikke konfigurert",needs_config_hint:"Åpne kortredigereren og velg en handleliste, eller angi 'entry_id' i YAML.",select_list_entry:"Handleliste-instans",no_entries:"Fant ingen handleliste-integrasjon. Legg den til først under Innstillinger → Enheter og tjenester.",title:"Tittel (valgfritt)",manage_lists:"Administrer lister",lists:"Lister",new_list:"Ny liste",list_name:"Listenavn",add_list:"Legg til liste",no_lists:"Ingen lister ennå. Opprett en ovenfor.",rename_list:"Gi listen nytt navn",delete_list:"Slett liste",delete_list_confirm:"Slette denne listen og alle varene? Når den er synkronisert, kan andre ikke angre det.",list_name_prompt:"Navn på den nye listen:",rename_list_prompt:"Gi listen nytt navn:"}};function ye(e){const t=(e??"").toLowerCase();return t.startsWith("de")?"de":t.startsWith("es")?"es":t.startsWith("fr")?"fr":t.startsWith("it")?"it":t.startsWith("pt")?"pt":t.startsWith("nl")?"nl":t.startsWith("pl")?"pl":t.startsWith("sv")?"sv":t.startsWith("nb")||t.startsWith("nn")||t.startsWith("no")?"nb":"en"}function ve(e){const t=me[e]??pe;return e=>t[e]??pe[e]??e}const fe="__none__",be="__new__";let $e=class extends ae{constructor(){super(...arguments),this._units=[],this._defaultUnit="pcs",this._editingId=null,this._editValue="",this._editQty=0,this._editUnit="",this._editCategory=null,this._draftName="",this._draftQty=1,this._draftUnit="",this._draftCategory=null,this._settingsOpen=!1,this._archiveOpen=!1,this._newListName=""}setConfig(e){const t=e??{type:"custom:grocery-list-card",entry_id:""};this._config=t,t.slug&&(this._activeSlug=t.slug),this._subscribedEntry&&this._subscribedEntry!==t.entry_id&&this._teardown(),this._maybeSubscribe()}static getConfigElement(){return document.createElement("grocery-list-card-editor")}static async getStubConfig(e){let t="";try{const i=(await e.connection.sendMessagePromise({type:"config_entries/get",domain:"grocery_list"})).find(e=>"grocery_list"===e.domain);i&&(t=i.entry_id)}catch(e){}return{type:"custom:grocery-list-card",entry_id:t}}getCardSize(){const e=this._activeList()?.items.length??0;return 2+Math.ceil(e/3)}connectedCallback(){super.connectedCallback(),this._maybeSubscribe()}disconnectedCallback(){super.disconnectedCallback(),this._teardown()}updated(e){e.has("hass")&&this._maybeSubscribe()}get _lang(){return ye(this.hass?.locale?.language??this.hass?.language)}async _maybeSubscribe(){if(this.hass&&this._config&&this._config.entry_id&&this._subscribedEntry!==this._config.entry_id){this._teardown(),this._subscribedEntry=this._config.entry_id,this._api=new ue(this.hass,this._config.entry_id);try{const e=await this._api.getUnits();this._units=e.units,this._defaultUnit=e.default_unit,this._draftUnit||(this._draftUnit=e.default_unit)}catch(e){this._units=[]}this._unsub=await this._api.subscribe(e=>{this._snapshot=e,!this._activeSlug&&e.lists.length&&(this._activeSlug=e.lists[0].slug)},this._lang)}}_teardown(){this._unsub&&(this._unsub(),this._unsub=void 0),this._subscribedEntry=void 0}_activeList(){const e=this._snapshot;if(e)return e.lists.find(e=>e.slug===this._activeSlug)??e.lists[0]}_targetSlug(){return this._activeList()?.slug??this._activeSlug??this._config?.slug??"default"}render(){const e=ve(this._lang);if(!this._config?.entry_id)return D`<ha-card>
        <div class="gl-empty">
          <p><strong>${e("needs_config")}</strong></p>
          <p>${e("needs_config_hint")}</p>
        </div>
      </ha-card>`;if(!this._snapshot)return D`<ha-card><div class="gl-empty">\u2026</div></ha-card>`;const t=ve(this._lang),i=this._activeList();return D`
      <ha-card>
        ${this._renderHeader(t)}
        ${this._snapshot.lists.length>1?this._renderSwitcher():G}
        ${this._renderAddBar(t)}
        ${i?this._renderGroups(i,t):G}
        ${this._renderFooter(t)}
      </ha-card>
      ${this._settingsOpen?this._renderSettings(t):G}
      ${this._archiveOpen?this._renderArchive(t):G}
    `}_renderHeader(e){const t=this._snapshot,i=this._activeList(),s=this._config?.title??i?.title??"Grocery",n=t.sync_state;return D`
      <div class="gl-header">
        <h2 class="gl-title">${s}</h2>
        <div class="gl-toolbar">
          <span class="gl-badge ${n}">${e("sync_"+n)}</span>
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
          <button
            class="gl-icon-btn"
            title=${e("sync")}
            @click=${()=>this._api?.sync()}
          >\u21bb</button>
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
      <div class="gl-add">
        <input
          class="gl-name"
          .value=${this._draftName}
          placeholder=${e("add_placeholder")}
          @input=${e=>this._draftName=e.target.value}
          @keydown=${e=>{"Enter"===e.key&&this._commitAdd()}}
        />
        <button class="gl-add-btn" @click=${()=>this._commitAdd()}>
          ${e("add")}
        </button>
      </div>
      <div class="gl-qtyrow">
        <div class="gl-stepper">
          <button @click=${()=>this._bumpQty(-1)}>\u2212</button>
          <input
            type="number"
            .value=${String(this._draftQty)}
            @input=${e=>this._draftQty=parseFloat(e.target.value)||0}
          />
          <button @click=${()=>this._bumpQty(1)}>+</button>
        </div>
        <select
          class="gl-unit"
          .value=${this._draftUnit}
          @change=${e=>this._draftUnit=e.target.value}
        >
          ${this._units.map(e=>D`<option value=${e.id}>
              ${e.labels[this._lang]??e.labels.en??e.id}
            </option>`)}
        </select>
        <select
          class="gl-cat"
          .value=${this._draftCategory??fe}
          @change=${t=>{const i=t.target,s=i.value;if(s===be){const t=this._promptNewCategory(e);this._draftCategory=t,i.value=t??fe}else this._draftCategory=s===fe?null:s}}
        >
          <option value=${fe}>${e("uncategorized")}</option>
          ${this._categories().map(e=>D`<option value=${e}>${e}</option>`)}
          <option value=${be}>${e("new_category")}…</option>
        </select>
      </div>
    `}_renderGroups(e,t){if(!e.items.length)return D`<div class="gl-empty">${t("empty_list")}</div>`;const i=e.items.filter(e=>!e.checked),s=e.items.filter(e=>e.checked);return D`
      ${this._renderCategoryGroups(i,e.slug,t)}
      ${s.length?D`<div class="gl-checked-section">
              <div class="gl-checked-divider">${t("checked_section")}</div>
              ${this._renderCategoryGroups(s,e.slug,t)}
            </div>`:G}
    `}_renderCategoryGroups(e,t,i){if(!e.length)return D``;const s=new Map;for(const t of e){const e=t.category??fe,i=s.get(e);i?i.push(t):s.set(e,[t])}const n=[...s.keys()].sort((e,t)=>e===fe?1:t===fe?-1:e.localeCompare(t));return D`
      ${n.map(e=>{const n=[...s.get(e)].sort((e,t)=>e.created_ts.localeCompare(t.created_ts)),r=e===fe?i("uncategorized"):e;return D`
          <div class="gl-group">
            <div class="gl-group-title">${r}</div>
            <ul class="gl-items">
              ${n.map(e=>this._renderItem(e,t,i))}
            </ul>
          </div>
        `})}
    `}_renderItem(e,t,i){if(this._editingId===e.id)return D`<li class="gl-item">${this._renderEdit(e,t,i)}</li>`;const s=e.qty?`${this._fmtNum(e.qty.value)} ${this._unitLabel(e.qty.unit)}`:"";return D`
      <li class="gl-item ${e.checked?"checked":""}">
        <button
          class="gl-check ${e.checked?"on":""}"
          @click=${()=>this._api?.setChecked(t,e.id,!e.checked)}
        >
          ${e.checked?"✓":""}
        </button>
        <div
          class="gl-item-main"
          @click=${()=>this._beginEdit(e)}
        >
          <div class="gl-item-name">${e.name}</div>
          ${s?D`<div class="gl-item-qty">${s}</div>`:G}
        </div>
        <button
          class="gl-icon-btn"
          title=${i("delete")}
          @click=${()=>this._api?.deleteItem(t,e.id)}
        >\u2715</button>
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
        </div>
        <div class="gl-qtyrow">
          <div class="gl-stepper">
            <button @click=${()=>this._bumpEditQty(-1)}>\u2212</button>
            <input
              type="number"
              .value=${String(this._editQty)}
              @input=${e=>this._editQty=parseFloat(e.target.value)||0}
            />
            <button @click=${()=>this._bumpEditQty(1)}>+</button>
          </div>
          <select
            class="gl-unit"
            .value=${this._editUnit}
            @change=${e=>this._editUnit=e.target.value}
          >
            ${this._units.map(e=>D`<option value=${e.id}>
                ${e.labels[this._lang]??e.labels.en??e.id}
              </option>`)}
          </select>
          <select
            class="gl-cat"
            .value=${this._editCategory??fe}
            @change=${e=>{const t=e.target,s=t.value;if(s===be){const e=this._promptNewCategory(i);this._editCategory=e,t.value=e??fe}else this._editCategory=s===fe?null:s}}
          >
            <option value=${fe}>${i("uncategorized")}</option>
            ${this._categories().map(e=>D`<option value=${e}>${e}</option>`)}
            <option value=${be}>${i("new_category")}…</option>
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
    `}_clearCheckedConfirm(e){const t=this._activeList();t&&window.confirm(e("clear_checked_confirm"))&&this._api?.clearChecked(t.slug)}_renderArchive(e){const t=this._activeSlug,i=t&&this._snapshot?.archives?.[t]||[];return D`
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
    `}_renderArchiveRow(e,t){const i=e.item.qty?`${this._fmtNum(e.item.qty.value)} ${this._unitLabel(e.item.qty.unit)}`:"";return D`
      <li class="gl-archive-row">
        <span class="gl-archive-name">${e.item.name}</span>
        ${i?D`<span class="gl-archive-qty">${i}</span>`:G}
        <span class="gl-archive-ts"
          >${t("archived_on")} ${this._fmtArchiveTs(e.archived_ts)}</span
        >
        <button
          class="gl-icon-btn"
          title=${t("restore")}
          @click=${()=>this._restoreArchived(e)}
        >\u21a9</button>
      </li>
    `}_restoreArchived(e){const t=this._activeSlug;t&&this._api?.restoreArchived(t,e.item.id,e.archived_ts)}_fmtArchiveTs(e){const t=new Date(e);return isNaN(t.getTime())?e:t.toLocaleDateString(this._lang,{year:"numeric",month:"short",day:"numeric"})}_renderSettings(e){const t=this._snapshot?.lists??[];return D`
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
        </div>
      </div>
    `}_renderListRow(e,t,i){return D`
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
    `}_categories(){return this._snapshot?.categories??[]}_promptNewCategory(e){const t=window.prompt(e("category_name"));if(null===t)return null;return t.trim()||null}_unitLabel(e){const t=this._units.find(t=>t.id===e);return t?t.labels[this._lang]??t.labels.en??e:e}_fmtNum(e){return Number.isInteger(e)?String(e):e.toFixed(2).replace(/0+$/,"")}_bumpQty(e){this._draftQty=Math.max(0,Math.round(100*(this._draftQty+e))/100)}_beginEdit(e){this._editingId=e.id,this._editValue=e.name,this._editQty=e.qty?.value??0,this._editUnit=e.qty?.unit??this._defaultUnit,this._editCategory=e.category}_cancelEdit(){this._editingId=null,this._editValue="",this._editQty=0,this._editUnit="",this._editCategory=null}_bumpEditQty(e){this._editQty=Math.max(0,Math.round(100*(this._editQty+e))/100)}_saveEdit(e,t){const i=this._editValue.trim();if(!i||!this._api)return void this._cancelEdit();const s={};i!==t.name&&(s.name=i),this._editCategory!==t.category&&(s.category=this._editCategory);const n=this._editQty||null,r=t.qty?.value??null,a=n?this._editUnit||this._defaultUnit:null,o=t.qty?.unit??null;n===r&&a===o||(s.qty_value=n,s.qty_unit=a),Object.keys(s).length&&this._api.updateItem(e,t.id,s),this._cancelEdit()}_commitAdd(){const e=this._draftName.trim();if(!e||!this._api)return;const t=this._targetSlug();this._api.addItem(t,e,{category:this._draftCategory,qty_value:this._draftQty||null,qty_unit:this._draftQty?this._draftUnit||this._defaultUnit:null}),this._activeSlug=t,this._draftName=""}_closeSettings(){this._settingsOpen=!1,this._newListName=""}async _commitNewList(){const e=this._newListName.trim();if(e&&this._api){this._newListName="";try{const t=await this._api.createList(e);t?.list?.slug&&(this._activeSlug=t.list.slug)}catch(e){}}}_renameListPrompt(e,t){const i=window.prompt(t("rename_list_prompt"),e.title);if(null===i)return;const s=i.trim();s&&s!==e.title&&this._api?.renameList(e.slug,s)}_deleteListConfirm(e,t){if(window.confirm(t("delete_list_confirm"))&&(this._api?.deleteList(e.slug),this._activeSlug===e.slug)){const t=(this._snapshot?.lists??[]).filter(t=>t.slug!==e.slug);this._activeSlug=t[0]?.slug}}};$e.styles=_e,e([he({attribute:!1})],$e.prototype,"hass",void 0),e([ge()],$e.prototype,"_config",void 0),e([ge()],$e.prototype,"_snapshot",void 0),e([ge()],$e.prototype,"_units",void 0),e([ge()],$e.prototype,"_defaultUnit",void 0),e([ge()],$e.prototype,"_activeSlug",void 0),e([ge()],$e.prototype,"_editingId",void 0),e([ge()],$e.prototype,"_editValue",void 0),e([ge()],$e.prototype,"_editQty",void 0),e([ge()],$e.prototype,"_editUnit",void 0),e([ge()],$e.prototype,"_editCategory",void 0),e([ge()],$e.prototype,"_draftName",void 0),e([ge()],$e.prototype,"_draftQty",void 0),e([ge()],$e.prototype,"_draftUnit",void 0),e([ge()],$e.prototype,"_draftCategory",void 0),e([ge()],$e.prototype,"_settingsOpen",void 0),e([ge()],$e.prototype,"_archiveOpen",void 0),e([ge()],$e.prototype,"_newListName",void 0),$e=e([le("grocery-list-card")],$e);let we=class extends ae{constructor(){super(...arguments),this._config={type:"custom:grocery-list-card",entry_id:""},this._entries=[]}setConfig(e){this._config=e??{type:"custom:grocery-list-card",entry_id:""}}connectedCallback(){super.connectedCallback(),this._loadEntries()}async _loadEntries(){if(this.hass)try{const e=await this.hass.connection.sendMessagePromise({type:"config_entries/get",domain:"grocery_list"});this._entries=e.filter(e=>"grocery_list"===e.domain).map(e=>({entry_id:e.entry_id,title:e.title}))}catch(e){this._entries=[]}}get _lang(){return ye(this.hass?.locale?.language??this.hass?.language)}_emit(e){this._config=e,this.dispatchEvent(new CustomEvent("config-changed",{detail:{config:e},bubbles:!0,composed:!0}))}render(){const e=ve(this._lang);return D`
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
    `}};e([he({attribute:!1})],we.prototype,"hass",void 0),e([ge()],we.prototype,"_config",void 0),e([ge()],we.prototype,"_entries",void 0),we=e([le("grocery-list-card-editor")],we);const ke={en:{name:"Grocery List Card",description:"A slick, mobile-first grocery list with categories and sync."},de:{name:"Einkaufslisten-Karte",description:"Eine schicke, mobil-optimierte Einkaufsliste mit Kategorien und Sync."}},Ae=ke[ye("undefined"!=typeof navigator?navigator.language:void 0)]??ke.en;window.customCards=window.customCards||[],window.customCards.push({type:"grocery-list-card",name:Ae.name,description:Ae.description,preview:!0,documentationURL:"https://codeberg.org/Apollo3zehn/ha-grocery-list"});export{$e as GroceryListCard,we as GroceryListCardEditor};
