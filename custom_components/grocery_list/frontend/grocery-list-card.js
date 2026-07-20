function t(t,e,i,s){var r,n=arguments.length,o=n<3?e:null===s?s=Object.getOwnPropertyDescriptor(e,i):s;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)o=Reflect.decorate(t,e,i,s);else for(var a=t.length-1;a>=0;a--)(r=t[a])&&(o=(n<3?r(o):n>3?r(e,i,o):r(e,i))||o);return n>3&&o&&Object.defineProperty(e,i,o),o}"function"==typeof SuppressedError&&SuppressedError;const e=globalThis,i=e.ShadowRoot&&(void 0===e.ShadyCSS||e.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,s=Symbol(),r=new WeakMap;let n=class{constructor(t,e,i){if(this._$cssResult$=!0,i!==s)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const e=this.t;if(i&&void 0===t){const i=void 0!==e&&1===e.length;i&&(t=r.get(e)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),i&&r.set(e,t))}return t}toString(){return this.cssText}};const o=i?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const i of t.cssRules)e+=i.cssText;return(t=>new n("string"==typeof t?t:t+"",void 0,s))(e)})(t):t,{is:a,defineProperty:l,getOwnPropertyDescriptor:c,getOwnPropertyNames:d,getOwnPropertySymbols:h,getPrototypeOf:g}=Object,u=globalThis,p=u.trustedTypes,_=p?p.emptyScript:"",m=u.reactiveElementPolyfillSupport,v=(t,e)=>t,y={toAttribute(t,e){switch(e){case Boolean:t=t?_:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let i=t;switch(e){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t)}catch(t){i=null}}return i}},f=(t,e)=>!a(t,e),b={attribute:!0,type:String,converter:y,reflect:!1,useDefault:!1,hasChanged:f};Symbol.metadata??=Symbol("metadata"),u.litPropertyMetadata??=new WeakMap;let $=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=b){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){const i=Symbol(),s=this.getPropertyDescriptor(t,i,e);void 0!==s&&l(this.prototype,t,s)}}static getPropertyDescriptor(t,e,i){const{get:s,set:r}=c(this.prototype,t)??{get(){return this[e]},set(t){this[e]=t}};return{get:s,set(e){const n=s?.call(this);r?.call(this,e),this.requestUpdate(t,n,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??b}static _$Ei(){if(this.hasOwnProperty(v("elementProperties")))return;const t=g(this);t.finalize(),void 0!==t.l&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(v("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(v("properties"))){const t=this.properties,e=[...d(t),...h(t)];for(const i of e)this.createProperty(i,t[i])}const t=this[Symbol.metadata];if(null!==t){const e=litPropertyMetadata.get(t);if(void 0!==e)for(const[t,i]of e)this.elementProperties.set(t,i)}this._$Eh=new Map;for(const[t,e]of this.elementProperties){const i=this._$Eu(t,e);void 0!==i&&this._$Eh.set(i,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const i=new Set(t.flat(1/0).reverse());for(const t of i)e.unshift(o(t))}else void 0!==t&&e.push(o(t));return e}static _$Eu(t,e){const i=e.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),void 0!==this.renderRoot&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){const t=new Map,e=this.constructor.elementProperties;for(const i of e.keys())this.hasOwnProperty(i)&&(t.set(i,this[i]),delete this[i]);t.size>0&&(this._$Ep=t)}createRenderRoot(){const t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return((t,s)=>{if(i)t.adoptedStyleSheets=s.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(const i of s){const s=document.createElement("style"),r=e.litNonce;void 0!==r&&s.setAttribute("nonce",r),s.textContent=i.cssText,t.appendChild(s)}})(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$ET(t,e){const i=this.constructor.elementProperties.get(t),s=this.constructor._$Eu(t,i);if(void 0!==s&&!0===i.reflect){const r=(void 0!==i.converter?.toAttribute?i.converter:y).toAttribute(e,i.type);this._$Em=t,null==r?this.removeAttribute(s):this.setAttribute(s,r),this._$Em=null}}_$AK(t,e){const i=this.constructor,s=i._$Eh.get(t);if(void 0!==s&&this._$Em!==s){const t=i.getPropertyOptions(s),r="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==t.converter?.fromAttribute?t.converter:y;this._$Em=s;const n=r.fromAttribute(e,t.type);this[s]=n??this._$Ej?.get(s)??n,this._$Em=null}}requestUpdate(t,e,i,s=!1,r){if(void 0!==t){const n=this.constructor;if(!1===s&&(r=this[t]),i??=n.getPropertyOptions(t),!((i.hasChanged??f)(r,e)||i.useDefault&&i.reflect&&r===this._$Ej?.get(t)&&!this.hasAttribute(n._$Eu(t,i))))return;this.C(t,e,i)}!1===this.isUpdatePending&&(this._$ES=this._$EP())}C(t,e,{useDefault:i,reflect:s,wrapped:r},n){i&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,n??e??this[t]),!0!==r||void 0!==n)||(this._$AL.has(t)||(this.hasUpdated||i||(e=void 0),this._$AL.set(t,e)),!0===s&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[t,e]of this._$Ep)this[t]=e;this._$Ep=void 0}const t=this.constructor.elementProperties;if(t.size>0)for(const[e,i]of t){const{wrapped:t}=i,s=this[e];!0!==t||this._$AL.has(e)||void 0===s||this.C(e,void 0,i,s)}}let t=!1;const e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(t=>t.hostUpdate?.()),this.update(e)):this._$EM()}catch(e){throw t=!1,this._$EM(),e}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(t){}firstUpdated(t){}};$.elementStyles=[],$.shadowRootOptions={mode:"open"},$[v("elementProperties")]=new Map,$[v("finalized")]=new Map,m?.({ReactiveElement:$}),(u.reactiveElementVersions??=[]).push("2.1.2");const w=globalThis,x=t=>t,A=w.trustedTypes,k=A?A.createPolicy("lit-html",{createHTML:t=>t}):void 0,E="$lit$",C=`lit$${Math.random().toFixed(9).slice(2)}$`,S="?"+C,N=`<${S}>`,L=document,U=()=>L.createComment(""),P=t=>null===t||"object"!=typeof t&&"function"!=typeof t,z=Array.isArray,O="[ \t\n\f\r]",M=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,R=/-->/g,T=/>/g,H=RegExp(`>|${O}(?:([^\\s"'>=/]+)(${O}*=${O}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),I=/'/g,q=/"/g,j=/^(?:script|style|textarea|title)$/i,D=(t=>(e,...i)=>({_$litType$:t,strings:e,values:i}))(1),Q=Symbol.for("lit-noChange"),B=Symbol.for("lit-nothing"),K=new WeakMap,V=L.createTreeWalker(L,129);function G(t,e){if(!z(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==k?k.createHTML(e):e}const W=(t,e)=>{const i=t.length-1,s=[];let r,n=2===e?"<svg>":3===e?"<math>":"",o=M;for(let e=0;e<i;e++){const i=t[e];let a,l,c=-1,d=0;for(;d<i.length&&(o.lastIndex=d,l=o.exec(i),null!==l);)d=o.lastIndex,o===M?"!--"===l[1]?o=R:void 0!==l[1]?o=T:void 0!==l[2]?(j.test(l[2])&&(r=RegExp("</"+l[2],"g")),o=H):void 0!==l[3]&&(o=H):o===H?">"===l[0]?(o=r??M,c=-1):void 0===l[1]?c=-2:(c=o.lastIndex-l[2].length,a=l[1],o=void 0===l[3]?H:'"'===l[3]?q:I):o===q||o===I?o=H:o===R||o===T?o=M:(o=H,r=void 0);const h=o===H&&t[e+1].startsWith("/>")?" ":"";n+=o===M?i+N:c>=0?(s.push(a),i.slice(0,c)+E+i.slice(c)+C+h):i+C+(-2===c?e:h)}return[G(t,n+(t[i]||"<?>")+(2===e?"</svg>":3===e?"</math>":"")),s]};class F{constructor({strings:t,_$litType$:e},i){let s;this.parts=[];let r=0,n=0;const o=t.length-1,a=this.parts,[l,c]=W(t,e);if(this.el=F.createElement(l,i),V.currentNode=this.el.content,2===e||3===e){const t=this.el.content.firstChild;t.replaceWith(...t.childNodes)}for(;null!==(s=V.nextNode())&&a.length<o;){if(1===s.nodeType){if(s.hasAttributes())for(const t of s.getAttributeNames())if(t.endsWith(E)){const e=c[n++],i=s.getAttribute(t).split(C),o=/([.?@])?(.*)/.exec(e);a.push({type:1,index:r,name:o[2],strings:i,ctor:"."===o[1]?tt:"?"===o[1]?et:"@"===o[1]?it:X}),s.removeAttribute(t)}else t.startsWith(C)&&(a.push({type:6,index:r}),s.removeAttribute(t));if(j.test(s.tagName)){const t=s.textContent.split(C),e=t.length-1;if(e>0){s.textContent=A?A.emptyScript:"";for(let i=0;i<e;i++)s.append(t[i],U()),V.nextNode(),a.push({type:2,index:++r});s.append(t[e],U())}}}else if(8===s.nodeType)if(s.data===S)a.push({type:2,index:r});else{let t=-1;for(;-1!==(t=s.data.indexOf(C,t+1));)a.push({type:7,index:r}),t+=C.length-1}r++}}static createElement(t,e){const i=L.createElement("template");return i.innerHTML=t,i}}function J(t,e,i=t,s){if(e===Q)return e;let r=void 0!==s?i._$Co?.[s]:i._$Cl;const n=P(e)?void 0:e._$litDirective$;return r?.constructor!==n&&(r?._$AO?.(!1),void 0===n?r=void 0:(r=new n(t),r._$AT(t,i,s)),void 0!==s?(i._$Co??=[])[s]=r:i._$Cl=r),void 0!==r&&(e=J(t,r._$AS(t,e.values),r,s)),e}class Y{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){const{el:{content:e},parts:i}=this._$AD,s=(t?.creationScope??L).importNode(e,!0);V.currentNode=s;let r=V.nextNode(),n=0,o=0,a=i[0];for(;void 0!==a;){if(n===a.index){let e;2===a.type?e=new Z(r,r.nextSibling,this,t):1===a.type?e=new a.ctor(r,a.name,a.strings,this,t):6===a.type&&(e=new st(r,this,t)),this._$AV.push(e),a=i[++o]}n!==a?.index&&(r=V.nextNode(),n++)}return V.currentNode=L,s}p(t){let e=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}}class Z{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,i,s){this.type=2,this._$AH=B,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=s,this._$Cv=s?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t?.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=J(this,t,e),P(t)?t===B||null==t||""===t?(this._$AH!==B&&this._$AR(),this._$AH=B):t!==this._$AH&&t!==Q&&this._(t):void 0!==t._$litType$?this.$(t):void 0!==t.nodeType?this.T(t):(t=>z(t)||"function"==typeof t?.[Symbol.iterator])(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==B&&P(this._$AH)?this._$AA.nextSibling.data=t:this.T(L.createTextNode(t)),this._$AH=t}$(t){const{values:e,_$litType$:i}=t,s="number"==typeof i?this._$AC(t):(void 0===i.el&&(i.el=F.createElement(G(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===s)this._$AH.p(e);else{const t=new Y(s,this),i=t.u(this.options);t.p(e),this.T(i),this._$AH=t}}_$AC(t){let e=K.get(t.strings);return void 0===e&&K.set(t.strings,e=new F(t)),e}k(t){z(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let i,s=0;for(const r of t)s===e.length?e.push(i=new Z(this.O(U()),this.O(U()),this,this.options)):i=e[s],i._$AI(r),s++;s<e.length&&(this._$AR(i&&i._$AB.nextSibling,s),e.length=s)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){const e=x(t).nextSibling;x(t).remove(),t=e}}setConnected(t){void 0===this._$AM&&(this._$Cv=t,this._$AP?.(t))}}class X{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,i,s,r){this.type=1,this._$AH=B,this._$AN=void 0,this.element=t,this.name=e,this._$AM=s,this.options=r,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=B}_$AI(t,e=this,i,s){const r=this.strings;let n=!1;if(void 0===r)t=J(this,t,e,0),n=!P(t)||t!==this._$AH&&t!==Q,n&&(this._$AH=t);else{const s=t;let o,a;for(t=r[0],o=0;o<r.length-1;o++)a=J(this,s[i+o],e,o),a===Q&&(a=this._$AH[o]),n||=!P(a)||a!==this._$AH[o],a===B?t=B:t!==B&&(t+=(a??"")+r[o+1]),this._$AH[o]=a}n&&!s&&this.j(t)}j(t){t===B?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}}class tt extends X{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===B?void 0:t}}class et extends X{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==B)}}class it extends X{constructor(t,e,i,s,r){super(t,e,i,s,r),this.type=5}_$AI(t,e=this){if((t=J(this,t,e,0)??B)===Q)return;const i=this._$AH,s=t===B&&i!==B||t.capture!==i.capture||t.once!==i.once||t.passive!==i.passive,r=t!==B&&(i===B||s);s&&this.element.removeEventListener(this.name,this,i),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}}class st{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){J(this,t)}}const rt=w.litHtmlPolyfillSupport;rt?.(F,Z),(w.litHtmlVersions??=[]).push("3.3.3");const nt=globalThis;class ot extends ${constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,i)=>{const s=i?.renderBefore??e;let r=s._$litPart$;if(void 0===r){const t=i?.renderBefore??null;s._$litPart$=r=new Z(e.insertBefore(U(),t),t,void 0,i??{})}return r._$AI(t),r})(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return Q}}ot._$litElement$=!0,ot.finalized=!0,nt.litElementHydrateSupport?.({LitElement:ot});const at=nt.litElementPolyfillSupport;at?.({LitElement:ot}),(nt.litElementVersions??=[]).push("4.2.2");const lt=t=>(e,i)=>{void 0!==i?i.addInitializer(()=>{customElements.define(t,e)}):customElements.define(t,e)},ct={attribute:!0,type:String,converter:y,reflect:!1,hasChanged:f},dt=(t=ct,e,i)=>{const{kind:s,metadata:r}=i;let n=globalThis.litPropertyMetadata.get(r);if(void 0===n&&globalThis.litPropertyMetadata.set(r,n=new Map),"setter"===s&&((t=Object.create(t)).wrapped=!0),n.set(i.name,t),"accessor"===s){const{name:s}=i;return{set(i){const r=e.get.call(this);e.set.call(this,i),this.requestUpdate(s,r,t,!0,i)},init(e){return void 0!==e&&this.C(s,void 0,t,e),e}}}if("setter"===s){const{name:s}=i;return function(i){const r=this[s];e.call(this,i),this.requestUpdate(s,r,t,!0,i)}}throw Error("Unsupported decorator location: "+s)};function ht(t){return(e,i)=>"object"==typeof i?dt(t,e,i):((t,e,i)=>{const s=e.hasOwnProperty(i);return e.constructor.createProperty(i,t),s?Object.getOwnPropertyDescriptor(e,i):void 0})(t,e,i)}function gt(t){return ht({...t,state:!0,attribute:!1})}class ut{constructor(t,e){this.hass=t,this.entryId=e}async subscribe(t,e="en"){return this.hass.connection.subscribeMessage(e=>t(e),{type:"grocery_list/subscribe",entry_id:this.entryId,locale:e})}send(t,e={}){return this.hass.connection.sendMessagePromise({type:`grocery_list/${t}`,entry_id:this.entryId,...e})}addItem(t,e,i={}){return this.send("add_item",{slug:t,name:e,...i})}updateItem(t,e,i){return this.send("update_item",{slug:t,item_id:e,...i})}setChecked(t,e,i){return this.send("set_checked",{slug:t,item_id:e,checked:i})}deleteItem(t,e){return this.send("delete_item",{slug:t,item_id:e})}clearChecked(t){return this.send("clear_checked",{slug:t})}restoreArchived(t,e,i){return this.send("restore_archived",{slug:t,item_id:e,archived_ts:i??null})}createList(t,e){return this.send("create_list",{title:t,slug:e??null})}renameList(t,e){return this.send("rename_list",{slug:t,title:e})}deleteList(t){return this.send("delete_list",{slug:t})}createCategory(t,e){return this.send("create_category",{name:t,icon:e})}updateCategory(t,e){return this.send("update_category",{cat_id:t,...e})}deleteCategory(t){return this.send("delete_category",{cat_id:t})}reorderCategories(t){return this.send("reorder_categories",{ordered_ids:t})}undo(){return this.send("undo")}redo(){return this.send("redo")}sync(){return this.send("sync")}getUnits(){return this.hass.connection.sendMessagePromise({type:"grocery_list/get_units"})}}const pt=((t,...e)=>{const i=1===t.length?t[0]:e.reduce((e,i,s)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+t[s+1],t[0]);return new n(i,t,s)})`
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
`,_t={add_placeholder:"Add an item…",add:"Add",qty:"Qty",unit:"Unit",category:"Category",uncategorized:"Uncategorized",clear_checked:"Clear checked",clear_checked_confirm:"Remove all checked items? They move to the archive and can be restored from there.",checked_section:"Checked",restore:"Restore",restore_confirm:"Restore this item to the list?",undo:"Undo",redo:"Redo",sync:"Sync",save:"Save",cancel:"Cancel",delete:"Delete",edit:"Edit",empty_list:"Nothing here yet. Add your first item above.",sync_synced:"Synced",sync_pending:"Pending",sync_syncing:"Syncing…",sync_offline:"Offline",sync_error:"Sync error",settings:"Settings",manage_categories:"Manage categories",categories:"Categories",new_category:"New category",category_name:"Name",add_category:"Add category",no_categories:"No categories yet. Create one above.",move_up:"Move up",move_down:"Move down",close:"Close",delete_category_confirm:"Delete this category? Its items become uncategorized.",archive:"Archive",view_archive:"View archive",no_archive:"Nothing archived yet. Cleared items appear here.",archived_on:"Archived",needs_config:"Grocery List not configured",needs_config_hint:"Open the card editor and pick a Grocery List, or set 'entry_id' in YAML.",select_list_entry:"Grocery List instance",no_entries:"No Grocery List integration found. Add it under Settings → Devices & Services first.",title:"Title (optional)",manage_lists:"Manage lists",lists:"Lists",new_list:"New list",list_name:"List name",add_list:"Add list",no_lists:"No lists yet. Create one above.",rename_list:"Rename list",delete_list:"Delete list",delete_list_confirm:"Delete this list and all its items? This cannot be undone by others once synced.",list_name_prompt:"New list name:",rename_list_prompt:"Rename list to:"},mt={en:_t,de:{add_placeholder:"Artikel hinzufügen…",add:"Hinzufügen",qty:"Menge",unit:"Einheit",category:"Kategorie",uncategorized:"Ohne Kategorie",clear_checked:"Erledigte entfernen",clear_checked_confirm:"Alle erledigten Artikel entfernen? Sie wandern ins Archiv und können von dort wiederhergestellt werden.",checked_section:"Erledigt",restore:"Wiederherstellen",restore_confirm:"Diesen Artikel zurück auf die Liste setzen?",undo:"Rückgängig",redo:"Wiederholen",sync:"Sync",save:"Speichern",cancel:"Abbrechen",delete:"Löschen",edit:"Bearbeiten",empty_list:"Noch nichts hier. Füge oben deinen ersten Artikel hinzu.",sync_synced:"Synchronisiert",sync_pending:"Ausstehend",sync_syncing:"Synchronisiere…",sync_offline:"Offline",sync_error:"Sync-Fehler",settings:"Einstellungen",manage_categories:"Kategorien verwalten",categories:"Kategorien",new_category:"Neue Kategorie",category_name:"Name",add_category:"Kategorie hinzufügen",no_categories:"Noch keine Kategorien. Erstelle oben eine.",move_up:"Nach oben",move_down:"Nach unten",close:"Schließen",delete_category_confirm:"Diese Kategorie löschen? Ihre Artikel werden dann ohne Kategorie angezeigt.",archive:"Archiv",view_archive:"Archiv anzeigen",no_archive:"Noch nichts archiviert. Entfernte Artikel erscheinen hier.",archived_on:"Archiviert",needs_config:"Einkaufsliste nicht konfiguriert",needs_config_hint:"Öffne den Karten-Editor und wähle eine Einkaufsliste, oder setze 'entry_id' im YAML.",select_list_entry:"Einkaufslisten-Instanz",no_entries:"Keine Einkaufslisten-Integration gefunden. Füge sie zuerst unter Einstellungen → Geräte & Dienste hinzu.",title:"Titel (optional)",manage_lists:"Listen verwalten",lists:"Listen",new_list:"Neue Liste",list_name:"Listenname",add_list:"Liste hinzufügen",no_lists:"Noch keine Listen. Erstelle oben eine.",rename_list:"Liste umbenennen",delete_list:"Liste löschen",delete_list_confirm:"Diese Liste und alle ihre Artikel löschen? Nach der Synchronisierung können andere dies nicht rückgängig machen.",list_name_prompt:"Name der neuen Liste:",rename_list_prompt:"Liste umbenennen in:"}};function vt(t){return t&&t.toLowerCase().startsWith("de")?"de":"en"}function yt(t){const e=mt[t]??_t;return t=>e[t]??_t[t]??t}const ft="__none__";let bt=class extends ot{constructor(){super(...arguments),this._units=[],this._defaultUnit="pcs",this._editingId=null,this._editValue="",this._editQty=0,this._editUnit="",this._editCategory=null,this._draftName="",this._draftQty=1,this._draftUnit="",this._draftCategory=null,this._settingsOpen=!1,this._archiveOpen=!1,this._newCatName="",this._newListName=""}setConfig(t){const e=t??{type:"custom:grocery-list-card",entry_id:""};this._config=e,e.slug&&(this._activeSlug=e.slug),this._subscribedEntry&&this._subscribedEntry!==e.entry_id&&this._teardown(),this._maybeSubscribe()}static getConfigElement(){return document.createElement("grocery-list-card-editor")}static async getStubConfig(t){let e="";try{const i=(await t.connection.sendMessagePromise({type:"config_entries/get",domain:"grocery_list"})).find(t=>"grocery_list"===t.domain);i&&(e=i.entry_id)}catch(t){}return{type:"custom:grocery-list-card",entry_id:e}}getCardSize(){const t=this._activeList()?.items.length??0;return 2+Math.ceil(t/3)}connectedCallback(){super.connectedCallback(),this._maybeSubscribe()}disconnectedCallback(){super.disconnectedCallback(),this._teardown()}updated(t){t.has("hass")&&this._maybeSubscribe()}get _lang(){return vt(this.hass?.locale?.language??this.hass?.language)}async _maybeSubscribe(){if(this.hass&&this._config&&this._config.entry_id&&this._subscribedEntry!==this._config.entry_id){this._teardown(),this._subscribedEntry=this._config.entry_id,this._api=new ut(this.hass,this._config.entry_id);try{const t=await this._api.getUnits();this._units=t.units,this._defaultUnit=t.default_unit,this._draftUnit||(this._draftUnit=t.default_unit)}catch(t){this._units=[]}this._unsub=await this._api.subscribe(t=>{this._snapshot=t,!this._activeSlug&&t.lists.length&&(this._activeSlug=t.lists[0].slug)},this._lang)}}_teardown(){this._unsub&&(this._unsub(),this._unsub=void 0),this._subscribedEntry=void 0}_activeList(){const t=this._snapshot;if(t)return t.lists.find(t=>t.slug===this._activeSlug)??t.lists[0]}_targetSlug(){return this._activeList()?.slug??this._activeSlug??this._config?.slug??"default"}render(){const t=yt(this._lang);if(!this._config?.entry_id)return D`<ha-card>
        <div class="gl-empty">
          <p><strong>${t("needs_config")}</strong></p>
          <p>${t("needs_config_hint")}</p>
        </div>
      </ha-card>`;if(!this._snapshot)return D`<ha-card><div class="gl-empty">\u2026</div></ha-card>`;const e=yt(this._lang),i=this._activeList();return D`
      <ha-card>
        ${this._renderHeader(e)}
        ${this._snapshot.lists.length>1?this._renderSwitcher():B}
        ${this._renderAddBar(e)}
        ${i?this._renderGroups(i,e):B}
        ${this._renderFooter(e)}
      </ha-card>
      ${this._settingsOpen?this._renderSettings(e):B}
      ${this._archiveOpen?this._renderArchive(e):B}
    `}_renderHeader(t){const e=this._snapshot,i=this._activeList(),s=this._config?.title??i?.title??"Grocery",r=e.sync_state;return D`
      <div class="gl-header">
        <h2 class="gl-title">${s}</h2>
        <div class="gl-toolbar">
          <span class="gl-badge ${r}">${t("sync_"+r)}</span>
          <button
            class="gl-icon-btn"
            title=${t("undo")}
            ?disabled=${!e.can_undo}
            @click=${()=>this._api?.undo()}
          >\u21b6</button>
          <button
            class="gl-icon-btn"
            title=${t("redo")}
            ?disabled=${!e.can_redo}
            @click=${()=>this._api?.redo()}
          >\u21b7</button>
          <button
            class="gl-icon-btn"
            title=${t("sync")}
            @click=${()=>this._api?.sync()}
          >\u21bb</button>
          <button
            class="gl-icon-btn"
            title=${t("view_archive")}
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
            title=${t("settings")}
            @click=${()=>this._settingsOpen=!0}
          >\u2699</button>
        </div>
      </div>
    `}_renderSwitcher(){const t=this._snapshot;return D`
      <div class="gl-switcher">
        ${t.lists.map(t=>D`
            <button
              class="gl-tab ${t.slug===this._activeSlug?"active":""}"
              @click=${()=>this._activeSlug=t.slug}
            >
              ${t.title}
            </button>
          `)}
      </div>
    `}_renderAddBar(t){return D`
      <div class="gl-add">
        <input
          class="gl-name"
          .value=${this._draftName}
          placeholder=${t("add_placeholder")}
          @input=${t=>this._draftName=t.target.value}
          @keydown=${t=>{"Enter"===t.key&&this._commitAdd()}}
        />
        <button class="gl-add-btn" @click=${()=>this._commitAdd()}>
          ${t("add")}
        </button>
      </div>
      <div class="gl-qtyrow">
        <div class="gl-stepper">
          <button @click=${()=>this._bumpQty(-1)}>\u2212</button>
          <input
            type="number"
            .value=${String(this._draftQty)}
            @input=${t=>this._draftQty=parseFloat(t.target.value)||0}
          />
          <button @click=${()=>this._bumpQty(1)}>+</button>
        </div>
        <select
          class="gl-unit"
          .value=${this._draftUnit}
          @change=${t=>this._draftUnit=t.target.value}
        >
          ${this._units.map(t=>D`<option value=${t.id}>
              ${t.labels[this._lang]??t.labels.en??t.id}
            </option>`)}
        </select>
        <select
          class="gl-cat"
          .value=${this._draftCategory??ft}
          @change=${t=>{const e=t.target.value;this._draftCategory=e===ft?null:e}}
        >
          <option value=${ft}>${t("uncategorized")}</option>
          ${this._categories().map(t=>D`<option value=${t.id}>${this._catLabel(t)}</option>`)}
        </select>
      </div>
    `}_renderGroups(t,e){if(!t.items.length)return D`<div class="gl-empty">${e("empty_list")}</div>`;const i=t.items.filter(t=>!t.checked),s=t.items.filter(t=>t.checked);return D`
      ${this._renderCategoryGroups(i,t.slug,e)}
      ${s.length?D`<div class="gl-checked-section">
              <div class="gl-checked-divider">${e("checked_section")}</div>
              ${this._renderCategoryGroups(s,t.slug,e)}
            </div>`:B}
    `}_renderCategoryGroups(t,e,i){if(!t.length)return D``;const s=this._categories(),r=new Map;s.forEach((t,e)=>r.set(t.id,e));const n=new Map;for(const e of t){const t=e.category??ft,i=n.get(t);i?i.push(e):n.set(t,[e])}const o=[...n.keys()].sort((t,e)=>t===ft?1:e===ft?-1:(r.get(t)??999)-(r.get(e)??999));return D`
      ${o.map(t=>{const s=[...n.get(t)].sort((t,e)=>t.created_ts.localeCompare(e.created_ts)),r=t===ft?i("uncategorized"):this._snapshot.category_labels[t]??t;return D`
          <div class="gl-group">
            <div class="gl-group-title">${r}</div>
            <ul class="gl-items">
              ${s.map(t=>this._renderItem(t,e,i))}
            </ul>
          </div>
        `})}
    `}_renderItem(t,e,i){if(this._editingId===t.id)return D`<li class="gl-item">${this._renderEdit(t,e,i)}</li>`;const s=t.qty?`${this._fmtNum(t.qty.value)} ${this._unitLabel(t.qty.unit)}`:"";return D`
      <li class="gl-item ${t.checked?"checked":""}">
        <button
          class="gl-check ${t.checked?"on":""}"
          @click=${()=>this._api?.setChecked(e,t.id,!t.checked)}
        >
          ${t.checked?"✓":""}
        </button>
        <div
          class="gl-item-main"
          @click=${()=>this._beginEdit(t)}
        >
          <div class="gl-item-name">${t.name}</div>
          ${s?D`<div class="gl-item-qty">${s}</div>`:B}
        </div>
        <button
          class="gl-icon-btn"
          title=${i("delete")}
          @click=${()=>this._api?.deleteItem(e,t.id)}
        >\u2715</button>
      </li>
    `}_renderEdit(t,e,i){return D`
      <div class="gl-edit">
        <div class="gl-edit-row">
          <input
            .value=${this._editValue}
            @input=${t=>this._editValue=t.target.value}
            @keydown=${i=>{"Enter"===i.key&&this._saveEdit(e,t),"Escape"===i.key&&this._cancelEdit()}}
          />
          <button
            class="gl-icon-btn"
            title=${i("save")}
            @click=${()=>this._saveEdit(e,t)}
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
              @input=${t=>this._editQty=parseFloat(t.target.value)||0}
            />
            <button @click=${()=>this._bumpEditQty(1)}>+</button>
          </div>
          <select
            class="gl-unit"
            .value=${this._editUnit}
            @change=${t=>this._editUnit=t.target.value}
          >
            ${this._units.map(t=>D`<option value=${t.id}>
                ${t.labels[this._lang]??t.labels.en??t.id}
              </option>`)}
          </select>
          <select
            class="gl-cat"
            .value=${this._editCategory??ft}
            @change=${t=>{const e=t.target.value;this._editCategory=e===ft?null:e}}
          >
            <option value=${ft}>${i("uncategorized")}</option>
            ${this._categories().map(t=>D`<option value=${t.id}>${this._catLabel(t)}</option>`)}
          </select>
        </div>
      </div>
    `}_renderFooter(t){const e=this._activeList(),i=!!e?.items.some(t=>t.checked);return D`
      <div class="gl-footer">
        <button
          class="gl-clear-btn"
          ?disabled=${!i}
          @click=${()=>this._clearCheckedConfirm(t)}
        >
          ${t("clear_checked")}
        </button>
      </div>
    `}_clearCheckedConfirm(t){const e=this._activeList();e&&window.confirm(t("clear_checked_confirm"))&&this._api?.clearChecked(e.slug)}_renderArchive(t){const e=this._activeSlug,i=e&&this._snapshot?.archives?.[e]||[];return D`
      <div
        class="gl-overlay"
        @click=${t=>{t.target===t.currentTarget&&(this._archiveOpen=!1)}}
      >
        <div class="gl-sheet">
          <div class="gl-sheet-header">
            <h3>${t("archive")}</h3>
            <button
              class="gl-icon-btn"
              title=${t("close")}
              @click=${()=>this._archiveOpen=!1}
            >\u2715</button>
          </div>

          ${i.length?D`<ul class="gl-archive-list">
                ${i.map(e=>this._renderArchiveRow(e,t))}
              </ul>`:D`<div class="gl-empty">${t("no_archive")}</div>`}
        </div>
      </div>
    `}_renderArchiveRow(t,e){const i=t.item.qty?`${this._fmtNum(t.item.qty.value)} ${this._unitLabel(t.item.qty.unit)}`:"";return D`
      <li class="gl-archive-row">
        <span class="gl-archive-name">${t.item.name}</span>
        ${i?D`<span class="gl-archive-qty">${i}</span>`:B}
        <span class="gl-archive-ts"
          >${e("archived_on")} ${this._fmtArchiveTs(t.archived_ts)}</span
        >
        <button
          class="gl-icon-btn"
          title=${e("restore")}
          @click=${()=>this._restoreArchived(t)}
        >\u21a9</button>
      </li>
    `}_restoreArchived(t){const e=this._activeSlug;e&&this._api?.restoreArchived(e,t.item.id,t.archived_ts)}_fmtArchiveTs(t){const e=new Date(t);return isNaN(e.getTime())?t:e.toLocaleDateString(this._lang,{year:"numeric",month:"short",day:"numeric"})}_renderSettings(t){const e=this._snapshot?.lists??[],i=this._categories();return D`
      <div
        class="gl-overlay"
        @click=${t=>{t.target===t.currentTarget&&this._closeSettings()}}
      >
        <div class="gl-sheet">
          <div class="gl-sheet-header">
            <h3>${t("settings")}</h3>
            <button
              class="gl-icon-btn"
              title=${t("close")}
              @click=${()=>this._closeSettings()}
            >\u2715</button>
          </div>

          <div class="gl-settings-section">
            <div class="gl-section-title">${t("lists")}</div>
            ${e.length?D`<ul class="gl-catlist">
                  ${e.map(i=>this._renderListRow(i,e.length,t))}
                </ul>`:D`<div class="gl-empty">${t("no_lists")}</div>`}
            <div class="gl-cat-new">
              <input
                .value=${this._newListName}
                placeholder=${t("list_name")}
                @input=${t=>this._newListName=t.target.value}
                @keydown=${t=>{"Enter"===t.key&&this._commitNewList()}}
              />
              <button class="gl-add-btn" @click=${()=>this._commitNewList()}>
                ${t("add_list")}
              </button>
            </div>
          </div>

          <div class="gl-settings-section">
            <div class="gl-section-title">${t("categories")}</div>
            ${i.length?D`<ul class="gl-catlist">
                  ${i.map((e,s)=>this._renderCatRow(e,s,i.length,t))}
                </ul>`:D`<div class="gl-empty">${t("no_categories")}</div>`}
            <div class="gl-cat-new">
              <input
                .value=${this._newCatName}
                placeholder=${t("category_name")}
                @input=${t=>this._newCatName=t.target.value}
                @keydown=${t=>{"Enter"===t.key&&this._commitNewCategory()}}
              />
              <button class="gl-add-btn" @click=${()=>this._commitNewCategory()}>
                ${t("add_category")}
              </button>
            </div>
          </div>
        </div>
      </div>
    `}_renderListRow(t,e,i){return D`
      <li class="gl-catrow">
        <span class="gl-cat-label" style="flex:1">${t.title}</span>
        <button
          class="gl-icon-btn"
          title=${i("rename_list")}
          @click=${()=>this._renameListPrompt(t,i)}
        >\u270e</button>
        <button
          class="gl-icon-btn"
          title=${i("delete_list")}
          ?disabled=${e<=1}
          @click=${()=>this._deleteListConfirm(t,i)}
        >\u2715</button>
      </li>
    `}_renderCatRow(t,e,i,s){return D`
      <li class="gl-catrow">
        <input
          class="gl-cat-label"
          .value=${t.name??""}
          @change=${e=>this._renameCategory(t,e.target.value)}
        />
        <button
          class="gl-icon-btn"
          title=${s("move_up")}
          ?disabled=${0===e}
          @click=${()=>this._moveCategory(e,-1)}
        >\u2191</button>
        <button
          class="gl-icon-btn"
          title=${s("move_down")}
          ?disabled=${e===i-1}
          @click=${()=>this._moveCategory(e,1)}
        >\u2193</button>
        <button
          class="gl-icon-btn"
          title=${s("delete")}
          @click=${()=>this._deleteCategory(t,s)}
        >\u2715</button>
      </li>
    `}_categories(){return this._snapshot?.categories??[]}_catLabel(t){return t.name||t.id}_unitLabel(t){const e=this._units.find(e=>e.id===t);return e?e.labels[this._lang]??e.labels.en??t:t}_fmtNum(t){return Number.isInteger(t)?String(t):t.toFixed(2).replace(/0+$/,"")}_bumpQty(t){this._draftQty=Math.max(0,Math.round(100*(this._draftQty+t))/100)}_beginEdit(t){this._editingId=t.id,this._editValue=t.name,this._editQty=t.qty?.value??0,this._editUnit=t.qty?.unit??this._defaultUnit,this._editCategory=t.category}_cancelEdit(){this._editingId=null,this._editValue="",this._editQty=0,this._editUnit="",this._editCategory=null}_bumpEditQty(t){this._editQty=Math.max(0,Math.round(100*(this._editQty+t))/100)}_saveEdit(t,e){const i=this._editValue.trim();if(!i||!this._api)return void this._cancelEdit();const s={};i!==e.name&&(s.name=i),this._editCategory!==e.category&&(s.category=this._editCategory);const r=this._editQty||null,n=e.qty?.value??null,o=r?this._editUnit||this._defaultUnit:null,a=e.qty?.unit??null;r===n&&o===a||(s.qty_value=r,s.qty_unit=o),Object.keys(s).length&&this._api.updateItem(t,e.id,s),this._cancelEdit()}_commitAdd(){const t=this._draftName.trim();if(!t||!this._api)return;const e=this._targetSlug();this._api.addItem(e,t,{category:this._draftCategory,qty_value:this._draftQty||null,qty_unit:this._draftQty?this._draftUnit||this._defaultUnit:null}),this._activeSlug=e,this._draftName=""}_commitNewCategory(){const t=this._newCatName.trim();t&&(this._api?.createCategory(t),this._newCatName="")}_renameCategory(t,e){const i=e.trim();i&&i!==(t.name??"")&&this._api?.updateCategory(t.id,{name:i})}_moveCategory(t,e){const i=this._categories().map(t=>t.id),s=t+e;s<0||s>=i.length||([i[t],i[s]]=[i[s],i[t]],this._api?.reorderCategories(i))}_deleteCategory(t,e){window.confirm(e("delete_category_confirm"))&&this._api?.deleteCategory(t.id)}_closeSettings(){this._settingsOpen=!1,this._newListName="",this._newCatName=""}async _commitNewList(){const t=this._newListName.trim();if(t&&this._api){this._newListName="";try{const e=await this._api.createList(t);e?.list?.slug&&(this._activeSlug=e.list.slug)}catch(t){}}}_renameListPrompt(t,e){const i=window.prompt(e("rename_list_prompt"),t.title);if(null===i)return;const s=i.trim();s&&s!==t.title&&this._api?.renameList(t.slug,s)}_deleteListConfirm(t,e){if(window.confirm(e("delete_list_confirm"))&&(this._api?.deleteList(t.slug),this._activeSlug===t.slug)){const e=(this._snapshot?.lists??[]).filter(e=>e.slug!==t.slug);this._activeSlug=e[0]?.slug}}};bt.styles=pt,t([ht({attribute:!1})],bt.prototype,"hass",void 0),t([gt()],bt.prototype,"_config",void 0),t([gt()],bt.prototype,"_snapshot",void 0),t([gt()],bt.prototype,"_units",void 0),t([gt()],bt.prototype,"_defaultUnit",void 0),t([gt()],bt.prototype,"_activeSlug",void 0),t([gt()],bt.prototype,"_editingId",void 0),t([gt()],bt.prototype,"_editValue",void 0),t([gt()],bt.prototype,"_editQty",void 0),t([gt()],bt.prototype,"_editUnit",void 0),t([gt()],bt.prototype,"_editCategory",void 0),t([gt()],bt.prototype,"_draftName",void 0),t([gt()],bt.prototype,"_draftQty",void 0),t([gt()],bt.prototype,"_draftUnit",void 0),t([gt()],bt.prototype,"_draftCategory",void 0),t([gt()],bt.prototype,"_settingsOpen",void 0),t([gt()],bt.prototype,"_archiveOpen",void 0),t([gt()],bt.prototype,"_newCatName",void 0),t([gt()],bt.prototype,"_newListName",void 0),bt=t([lt("grocery-list-card")],bt);let $t=class extends ot{constructor(){super(...arguments),this._config={type:"custom:grocery-list-card",entry_id:""},this._entries=[]}setConfig(t){this._config=t??{type:"custom:grocery-list-card",entry_id:""}}connectedCallback(){super.connectedCallback(),this._loadEntries()}async _loadEntries(){if(this.hass)try{const t=await this.hass.connection.sendMessagePromise({type:"config_entries/get",domain:"grocery_list"});this._entries=t.filter(t=>"grocery_list"===t.domain).map(t=>({entry_id:t.entry_id,title:t.title}))}catch(t){this._entries=[]}}get _lang(){return vt(this.hass?.locale?.language??this.hass?.language)}_emit(t){this._config=t,this.dispatchEvent(new CustomEvent("config-changed",{detail:{config:t},bubbles:!0,composed:!0}))}render(){const t=yt(this._lang);return D`
      <div class="gl-editor">
        <label>${t("select_list_entry")}</label>
        ${this._entries.length?D`<select
              .value=${this._config.entry_id}
              @change=${t=>this._emit({...this._config,entry_id:t.target.value})}
            >
              <option value="" ?selected=${!this._config.entry_id}></option>
              ${this._entries.map(t=>D`<option
                  value=${t.entry_id}
                  ?selected=${t.entry_id===this._config.entry_id}
                >
                  ${t.title||t.entry_id}
                </option>`)}
            </select>`:D`<p>${t("no_entries")}</p>`}
        <label>${t("title")}</label>
        <input
          .value=${this._config.title??""}
          @input=${t=>{const e=t.target.value;this._emit({...this._config,title:e||void 0})}}
        />
      </div>
    `}};t([ht({attribute:!1})],$t.prototype,"hass",void 0),t([gt()],$t.prototype,"_config",void 0),t([gt()],$t.prototype,"_entries",void 0),$t=t([lt("grocery-list-card-editor")],$t);const wt={en:{name:"Grocery List Card",description:"A slick, mobile-first grocery list with categories and sync."},de:{name:"Einkaufslisten-Karte",description:"Eine schicke, mobil-optimierte Einkaufsliste mit Kategorien und Sync."}},xt=wt[vt("undefined"!=typeof navigator?navigator.language:void 0)]??wt.en;window.customCards=window.customCards||[],window.customCards.push({type:"grocery-list-card",name:xt.name,description:xt.description,preview:!0,documentationURL:"https://codeberg.org/Apollo3zehn/ha-grocery-list"});export{bt as GroceryListCard,$t as GroceryListCardEditor};
