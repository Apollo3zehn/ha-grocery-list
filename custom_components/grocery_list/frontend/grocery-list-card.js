function t(t,e,i,s){var r,n=arguments.length,a=n<3?e:null===s?s=Object.getOwnPropertyDescriptor(e,i):s;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)a=Reflect.decorate(t,e,i,s);else for(var o=t.length-1;o>=0;o--)(r=t[o])&&(a=(n<3?r(a):n>3?r(e,i,a):r(e,i))||a);return n>3&&a&&Object.defineProperty(e,i,a),a}"function"==typeof SuppressedError&&SuppressedError;const e=globalThis,i=e.ShadowRoot&&(void 0===e.ShadyCSS||e.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,s=Symbol(),r=new WeakMap;let n=class{constructor(t,e,i){if(this._$cssResult$=!0,i!==s)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const e=this.t;if(i&&void 0===t){const i=void 0!==e&&1===e.length;i&&(t=r.get(e)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),i&&r.set(e,t))}return t}toString(){return this.cssText}};const a=i?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const i of t.cssRules)e+=i.cssText;return(t=>new n("string"==typeof t?t:t+"",void 0,s))(e)})(t):t,{is:o,defineProperty:l,getOwnPropertyDescriptor:c,getOwnPropertyNames:d,getOwnPropertySymbols:h,getPrototypeOf:g}=Object,p=globalThis,u=p.trustedTypes,_=u?u.emptyScript:"",v=p.reactiveElementPolyfillSupport,m=(t,e)=>t,y={toAttribute(t,e){switch(e){case Boolean:t=t?_:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let i=t;switch(e){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t)}catch(t){i=null}}return i}},f=(t,e)=>!o(t,e),b={attribute:!0,type:String,converter:y,reflect:!1,useDefault:!1,hasChanged:f};Symbol.metadata??=Symbol("metadata"),p.litPropertyMetadata??=new WeakMap;let $=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=b){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){const i=Symbol(),s=this.getPropertyDescriptor(t,i,e);void 0!==s&&l(this.prototype,t,s)}}static getPropertyDescriptor(t,e,i){const{get:s,set:r}=c(this.prototype,t)??{get(){return this[e]},set(t){this[e]=t}};return{get:s,set(e){const n=s?.call(this);r?.call(this,e),this.requestUpdate(t,n,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??b}static _$Ei(){if(this.hasOwnProperty(m("elementProperties")))return;const t=g(this);t.finalize(),void 0!==t.l&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(m("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(m("properties"))){const t=this.properties,e=[...d(t),...h(t)];for(const i of e)this.createProperty(i,t[i])}const t=this[Symbol.metadata];if(null!==t){const e=litPropertyMetadata.get(t);if(void 0!==e)for(const[t,i]of e)this.elementProperties.set(t,i)}this._$Eh=new Map;for(const[t,e]of this.elementProperties){const i=this._$Eu(t,e);void 0!==i&&this._$Eh.set(i,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const i=new Set(t.flat(1/0).reverse());for(const t of i)e.unshift(a(t))}else void 0!==t&&e.push(a(t));return e}static _$Eu(t,e){const i=e.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),void 0!==this.renderRoot&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){const t=new Map,e=this.constructor.elementProperties;for(const i of e.keys())this.hasOwnProperty(i)&&(t.set(i,this[i]),delete this[i]);t.size>0&&(this._$Ep=t)}createRenderRoot(){const t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return((t,s)=>{if(i)t.adoptedStyleSheets=s.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(const i of s){const s=document.createElement("style"),r=e.litNonce;void 0!==r&&s.setAttribute("nonce",r),s.textContent=i.cssText,t.appendChild(s)}})(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$ET(t,e){const i=this.constructor.elementProperties.get(t),s=this.constructor._$Eu(t,i);if(void 0!==s&&!0===i.reflect){const r=(void 0!==i.converter?.toAttribute?i.converter:y).toAttribute(e,i.type);this._$Em=t,null==r?this.removeAttribute(s):this.setAttribute(s,r),this._$Em=null}}_$AK(t,e){const i=this.constructor,s=i._$Eh.get(t);if(void 0!==s&&this._$Em!==s){const t=i.getPropertyOptions(s),r="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==t.converter?.fromAttribute?t.converter:y;this._$Em=s;const n=r.fromAttribute(e,t.type);this[s]=n??this._$Ej?.get(s)??n,this._$Em=null}}requestUpdate(t,e,i,s=!1,r){if(void 0!==t){const n=this.constructor;if(!1===s&&(r=this[t]),i??=n.getPropertyOptions(t),!((i.hasChanged??f)(r,e)||i.useDefault&&i.reflect&&r===this._$Ej?.get(t)&&!this.hasAttribute(n._$Eu(t,i))))return;this.C(t,e,i)}!1===this.isUpdatePending&&(this._$ES=this._$EP())}C(t,e,{useDefault:i,reflect:s,wrapped:r},n){i&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,n??e??this[t]),!0!==r||void 0!==n)||(this._$AL.has(t)||(this.hasUpdated||i||(e=void 0),this._$AL.set(t,e)),!0===s&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[t,e]of this._$Ep)this[t]=e;this._$Ep=void 0}const t=this.constructor.elementProperties;if(t.size>0)for(const[e,i]of t){const{wrapped:t}=i,s=this[e];!0!==t||this._$AL.has(e)||void 0===s||this.C(e,void 0,i,s)}}let t=!1;const e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(t=>t.hostUpdate?.()),this.update(e)):this._$EM()}catch(e){throw t=!1,this._$EM(),e}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(t){}firstUpdated(t){}};$.elementStyles=[],$.shadowRootOptions={mode:"open"},$[m("elementProperties")]=new Map,$[m("finalized")]=new Map,v?.({ReactiveElement:$}),(p.reactiveElementVersions??=[]).push("2.1.2");const w=globalThis,x=t=>t,A=w.trustedTypes,E=A?A.createPolicy("lit-html",{createHTML:t=>t}):void 0,C="$lit$",k=`lit$${Math.random().toFixed(9).slice(2)}$`,S="?"+k,U=`<${S}>`,N=document,P=()=>N.createComment(""),M=t=>null===t||"object"!=typeof t&&"function"!=typeof t,O=Array.isArray,z="[ \t\n\f\r]",T=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,R=/-->/g,H=/>/g,D=RegExp(`>|${z}(?:([^\\s"'>=/]+)(${z}*=${z}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),I=/'/g,L=/"/g,j=/^(?:script|style|textarea|title)$/i,q=(t=>(e,...i)=>({_$litType$:t,strings:e,values:i}))(1),B=Symbol.for("lit-noChange"),V=Symbol.for("lit-nothing"),Q=new WeakMap,K=N.createTreeWalker(N,129);function W(t,e){if(!O(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==E?E.createHTML(e):e}const F=(t,e)=>{const i=t.length-1,s=[];let r,n=2===e?"<svg>":3===e?"<math>":"",a=T;for(let e=0;e<i;e++){const i=t[e];let o,l,c=-1,d=0;for(;d<i.length&&(a.lastIndex=d,l=a.exec(i),null!==l);)d=a.lastIndex,a===T?"!--"===l[1]?a=R:void 0!==l[1]?a=H:void 0!==l[2]?(j.test(l[2])&&(r=RegExp("</"+l[2],"g")),a=D):void 0!==l[3]&&(a=D):a===D?">"===l[0]?(a=r??T,c=-1):void 0===l[1]?c=-2:(c=a.lastIndex-l[2].length,o=l[1],a=void 0===l[3]?D:'"'===l[3]?L:I):a===L||a===I?a=D:a===R||a===H?a=T:(a=D,r=void 0);const h=a===D&&t[e+1].startsWith("/>")?" ":"";n+=a===T?i+U:c>=0?(s.push(o),i.slice(0,c)+C+i.slice(c)+k+h):i+k+(-2===c?e:h)}return[W(t,n+(t[i]||"<?>")+(2===e?"</svg>":3===e?"</math>":"")),s]};class G{constructor({strings:t,_$litType$:e},i){let s;this.parts=[];let r=0,n=0;const a=t.length-1,o=this.parts,[l,c]=F(t,e);if(this.el=G.createElement(l,i),K.currentNode=this.el.content,2===e||3===e){const t=this.el.content.firstChild;t.replaceWith(...t.childNodes)}for(;null!==(s=K.nextNode())&&o.length<a;){if(1===s.nodeType){if(s.hasAttributes())for(const t of s.getAttributeNames())if(t.endsWith(C)){const e=c[n++],i=s.getAttribute(t).split(k),a=/([.?@])?(.*)/.exec(e);o.push({type:1,index:r,name:a[2],strings:i,ctor:"."===a[1]?tt:"?"===a[1]?et:"@"===a[1]?it:Y}),s.removeAttribute(t)}else t.startsWith(k)&&(o.push({type:6,index:r}),s.removeAttribute(t));if(j.test(s.tagName)){const t=s.textContent.split(k),e=t.length-1;if(e>0){s.textContent=A?A.emptyScript:"";for(let i=0;i<e;i++)s.append(t[i],P()),K.nextNode(),o.push({type:2,index:++r});s.append(t[e],P())}}}else if(8===s.nodeType)if(s.data===S)o.push({type:2,index:r});else{let t=-1;for(;-1!==(t=s.data.indexOf(k,t+1));)o.push({type:7,index:r}),t+=k.length-1}r++}}static createElement(t,e){const i=N.createElement("template");return i.innerHTML=t,i}}function J(t,e,i=t,s){if(e===B)return e;let r=void 0!==s?i._$Co?.[s]:i._$Cl;const n=M(e)?void 0:e._$litDirective$;return r?.constructor!==n&&(r?._$AO?.(!1),void 0===n?r=void 0:(r=new n(t),r._$AT(t,i,s)),void 0!==s?(i._$Co??=[])[s]=r:i._$Cl=r),void 0!==r&&(e=J(t,r._$AS(t,e.values),r,s)),e}class Z{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){const{el:{content:e},parts:i}=this._$AD,s=(t?.creationScope??N).importNode(e,!0);K.currentNode=s;let r=K.nextNode(),n=0,a=0,o=i[0];for(;void 0!==o;){if(n===o.index){let e;2===o.type?e=new X(r,r.nextSibling,this,t):1===o.type?e=new o.ctor(r,o.name,o.strings,this,t):6===o.type&&(e=new st(r,this,t)),this._$AV.push(e),o=i[++a]}n!==o?.index&&(r=K.nextNode(),n++)}return K.currentNode=N,s}p(t){let e=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}}class X{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,i,s){this.type=2,this._$AH=V,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=s,this._$Cv=s?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t?.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=J(this,t,e),M(t)?t===V||null==t||""===t?(this._$AH!==V&&this._$AR(),this._$AH=V):t!==this._$AH&&t!==B&&this._(t):void 0!==t._$litType$?this.$(t):void 0!==t.nodeType?this.T(t):(t=>O(t)||"function"==typeof t?.[Symbol.iterator])(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==V&&M(this._$AH)?this._$AA.nextSibling.data=t:this.T(N.createTextNode(t)),this._$AH=t}$(t){const{values:e,_$litType$:i}=t,s="number"==typeof i?this._$AC(t):(void 0===i.el&&(i.el=G.createElement(W(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===s)this._$AH.p(e);else{const t=new Z(s,this),i=t.u(this.options);t.p(e),this.T(i),this._$AH=t}}_$AC(t){let e=Q.get(t.strings);return void 0===e&&Q.set(t.strings,e=new G(t)),e}k(t){O(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let i,s=0;for(const r of t)s===e.length?e.push(i=new X(this.O(P()),this.O(P()),this,this.options)):i=e[s],i._$AI(r),s++;s<e.length&&(this._$AR(i&&i._$AB.nextSibling,s),e.length=s)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){const e=x(t).nextSibling;x(t).remove(),t=e}}setConnected(t){void 0===this._$AM&&(this._$Cv=t,this._$AP?.(t))}}class Y{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,i,s,r){this.type=1,this._$AH=V,this._$AN=void 0,this.element=t,this.name=e,this._$AM=s,this.options=r,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=V}_$AI(t,e=this,i,s){const r=this.strings;let n=!1;if(void 0===r)t=J(this,t,e,0),n=!M(t)||t!==this._$AH&&t!==B,n&&(this._$AH=t);else{const s=t;let a,o;for(t=r[0],a=0;a<r.length-1;a++)o=J(this,s[i+a],e,a),o===B&&(o=this._$AH[a]),n||=!M(o)||o!==this._$AH[a],o===V?t=V:t!==V&&(t+=(o??"")+r[a+1]),this._$AH[a]=o}n&&!s&&this.j(t)}j(t){t===V?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}}class tt extends Y{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===V?void 0:t}}class et extends Y{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==V)}}class it extends Y{constructor(t,e,i,s,r){super(t,e,i,s,r),this.type=5}_$AI(t,e=this){if((t=J(this,t,e,0)??V)===B)return;const i=this._$AH,s=t===V&&i!==V||t.capture!==i.capture||t.once!==i.once||t.passive!==i.passive,r=t!==V&&(i===V||s);s&&this.element.removeEventListener(this.name,this,i),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}}class st{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){J(this,t)}}const rt=w.litHtmlPolyfillSupport;rt?.(G,X),(w.litHtmlVersions??=[]).push("3.3.3");const nt=globalThis;class at extends ${constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,i)=>{const s=i?.renderBefore??e;let r=s._$litPart$;if(void 0===r){const t=i?.renderBefore??null;s._$litPart$=r=new X(e.insertBefore(P(),t),t,void 0,i??{})}return r._$AI(t),r})(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return B}}at._$litElement$=!0,at.finalized=!0,nt.litElementHydrateSupport?.({LitElement:at});const ot=nt.litElementPolyfillSupport;ot?.({LitElement:at}),(nt.litElementVersions??=[]).push("4.2.2");const lt={attribute:!0,type:String,converter:y,reflect:!1,hasChanged:f},ct=(t=lt,e,i)=>{const{kind:s,metadata:r}=i;let n=globalThis.litPropertyMetadata.get(r);if(void 0===n&&globalThis.litPropertyMetadata.set(r,n=new Map),"setter"===s&&((t=Object.create(t)).wrapped=!0),n.set(i.name,t),"accessor"===s){const{name:s}=i;return{set(i){const r=e.get.call(this);e.set.call(this,i),this.requestUpdate(s,r,t,!0,i)},init(e){return void 0!==e&&this.C(s,void 0,t,e),e}}}if("setter"===s){const{name:s}=i;return function(i){const r=this[s];e.call(this,i),this.requestUpdate(s,r,t,!0,i)}}throw Error("Unsupported decorator location: "+s)};function dt(t){return(e,i)=>"object"==typeof i?ct(t,e,i):((t,e,i)=>{const s=e.hasOwnProperty(i);return e.constructor.createProperty(i,t),s?Object.getOwnPropertyDescriptor(e,i):void 0})(t,e,i)}function ht(t){return dt({...t,state:!0,attribute:!1})}class gt{constructor(t,e){this.hass=t,this.entryId=e}async subscribe(t,e="en"){return this.hass.connection.subscribeMessage(e=>t(e),{type:"grocery_list/subscribe",entry_id:this.entryId,locale:e})}send(t,e={}){return this.hass.connection.sendMessagePromise({type:`grocery_list/${t}`,entry_id:this.entryId,...e})}addItem(t,e,i={}){return this.send("add_item",{slug:t,name:e,...i})}updateItem(t,e,i){return this.send("update_item",{slug:t,item_id:e,...i})}setChecked(t,e,i){return this.send("set_checked",{slug:t,item_id:e,checked:i})}deleteItem(t,e){return this.send("delete_item",{slug:t,item_id:e})}clearChecked(t){return this.send("clear_checked",{slug:t})}createCategory(t,e){return this.send("create_category",{labels:t,icon:e})}updateCategory(t,e){return this.send("update_category",{cat_id:t,...e})}deleteCategory(t){return this.send("delete_category",{cat_id:t})}reorderCategories(t){return this.send("reorder_categories",{ordered_ids:t})}undo(){return this.send("undo")}redo(){return this.send("redo")}sync(){return this.send("sync")}getUnits(){return this.hass.connection.sendMessagePromise({type:"grocery_list/get_units"})}}const pt=((t,...e)=>{const i=1===t.length?t[0]:e.reduce((e,i,s)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+t[s+1],t[0]);return new n(i,t,s)})`
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
  .gl-catrow .gl-lang-tag {
    font-size: 0.7rem;
    font-weight: 700;
    color: var(--gl-muted);
    width: 20px;
    text-transform: uppercase;
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
`,ut={add_placeholder:"Add an item…",add:"Add",qty:"Qty",unit:"Unit",category:"Category",uncategorized:"Uncategorized",clear_checked:"Clear checked",undo:"Undo",redo:"Redo",sync:"Sync",save:"Save",cancel:"Cancel",delete:"Delete",edit:"Edit",empty_list:"Nothing here yet. Add your first item above.",sync_synced:"Synced",sync_pending:"Pending",sync_syncing:"Syncing…",sync_offline:"Offline",sync_error:"Sync error",manage_categories:"Manage categories",categories:"Categories",new_category:"New category",category_name_en:"Name (English)",category_name_de:"Name (German)",add_category:"Add category",no_categories:"No categories yet. Create one above.",move_up:"Move up",move_down:"Move down",close:"Close",delete_category_confirm:"Delete this category? Its items become uncategorized.",archive:"Archive",view_archive:"View archive",no_archive:"Nothing archived yet. Cleared items appear here.",archived_on:"Archived"},_t={en:ut,de:{add_placeholder:"Artikel hinzufügen…",add:"Hinzufügen",qty:"Menge",unit:"Einheit",category:"Kategorie",uncategorized:"Ohne Kategorie",clear_checked:"Erledigte entfernen",undo:"Rückgängig",redo:"Wiederholen",sync:"Sync",save:"Speichern",cancel:"Abbrechen",delete:"Löschen",edit:"Bearbeiten",empty_list:"Noch nichts hier. Füge oben deinen ersten Artikel hinzu.",sync_synced:"Synchronisiert",sync_pending:"Ausstehend",sync_syncing:"Synchronisiere…",sync_offline:"Offline",sync_error:"Sync-Fehler",manage_categories:"Kategorien verwalten",categories:"Kategorien",new_category:"Neue Kategorie",category_name_en:"Name (Englisch)",category_name_de:"Name (Deutsch)",add_category:"Kategorie hinzufügen",no_categories:"Noch keine Kategorien. Erstelle oben eine.",move_up:"Nach oben",move_down:"Nach unten",close:"Schließen",delete_category_confirm:"Diese Kategorie löschen? Ihre Artikel werden dann ohne Kategorie angezeigt."}};const vt="__none__";let mt=class extends at{constructor(){super(...arguments),this._units=[],this._defaultUnit="pcs",this._editingId=null,this._editValue="",this._draftName="",this._draftQty=1,this._draftUnit="",this._draftCategory=null,this._catManagerOpen=!1,this._archiveOpen=!1,this._newCatEn="",this._newCatDe=""}setConfig(t){if(!t||!t.entry_id)throw new Error("grocery-list-card: 'entry_id' is required");this._config=t,t.slug&&(this._activeSlug=t.slug),this._subscribedEntry&&this._subscribedEntry!==t.entry_id&&this._teardown(),this._maybeSubscribe()}getCardSize(){const t=this._activeList()?.items.length??0;return 2+Math.ceil(t/3)}connectedCallback(){super.connectedCallback(),this._maybeSubscribe()}disconnectedCallback(){super.disconnectedCallback(),this._teardown()}updated(t){t.has("hass")&&this._maybeSubscribe()}get _lang(){return(t=this.hass?.locale?.language??this.hass?.language)&&t.toLowerCase().startsWith("de")?"de":"en";var t}async _maybeSubscribe(){if(this.hass&&this._config&&this._subscribedEntry!==this._config.entry_id){this._teardown(),this._subscribedEntry=this._config.entry_id,this._api=new gt(this.hass,this._config.entry_id);try{const t=await this._api.getUnits();this._units=t.units,this._defaultUnit=t.default_unit,this._draftUnit||(this._draftUnit=t.default_unit)}catch(t){this._units=[]}this._unsub=await this._api.subscribe(t=>{this._snapshot=t,!this._activeSlug&&t.lists.length&&(this._activeSlug=t.lists[0].slug)},this._lang)}}_teardown(){this._unsub&&(this._unsub(),this._unsub=void 0),this._subscribedEntry=void 0}_activeList(){const t=this._snapshot;if(t)return t.lists.find(t=>t.slug===this._activeSlug)??t.lists[0]}render(){if(!this._snapshot)return q`<ha-card><div class="gl-empty">\u2026</div></ha-card>`;const t=function(t){const e=_t[t]??ut;return t=>e[t]??ut[t]??t}(this._lang),e=this._activeList();return q`
      <ha-card>
        ${this._renderHeader(t)}
        ${this._snapshot.lists.length>1?this._renderSwitcher():V}
        ${this._renderAddBar(t)}
        ${e?this._renderGroups(e,t):V}
        ${this._renderFooter(t)}
      </ha-card>
      ${this._catManagerOpen?this._renderCategoryManager(t):V}
      ${this._archiveOpen?this._renderArchive(t):V}
    `}_renderHeader(t){const e=this._snapshot,i=this._activeList(),s=this._config?.title??i?.title??"Grocery",r=e.sync_state;return q`
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
          >\u{1F5C4}</button>
          <button
            class="gl-icon-btn"
            title=${t("manage_categories")}
            @click=${()=>this._catManagerOpen=!0}
          >\u2699</button>
        </div>
      </div>
    `}_renderSwitcher(){const t=this._snapshot;return q`
      <div class="gl-switcher">
        ${t.lists.map(t=>q`
            <button
              class="gl-tab ${t.slug===this._activeSlug?"active":""}"
              @click=${()=>this._activeSlug=t.slug}
            >
              ${t.title}
            </button>
          `)}
      </div>
    `}_renderAddBar(t){return q`
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
          ${this._units.map(t=>q`<option value=${t.id}>
              ${t.labels[this._lang]??t.labels.en??t.id}
            </option>`)}
        </select>
        <select
          class="gl-cat"
          .value=${this._draftCategory??vt}
          @change=${t=>{const e=t.target.value;this._draftCategory=e===vt?null:e}}
        >
          <option value=${vt}>${t("uncategorized")}</option>
          ${this._categories().map(t=>q`<option value=${t.id}>${this._catLabel(t)}</option>`)}
        </select>
      </div>
    `}_renderGroups(t,e){if(!t.items.length)return q`<div class="gl-empty">${e("empty_list")}</div>`;const i=this._categories(),s=new Map;i.forEach((t,e)=>s.set(t.id,e));const r=new Map;for(const e of t.items){const t=e.category??vt,i=r.get(t);i?i.push(e):r.set(t,[e])}const n=[...r.keys()].sort((t,e)=>t===vt?1:e===vt?-1:(s.get(t)??999)-(s.get(e)??999));return q`
      ${n.map(i=>{const s=this._sortSunk(r.get(i)),n=i===vt?e("uncategorized"):this._snapshot.category_labels[i]??i;return q`
          <div class="gl-group">
            <div class="gl-group-title">${n}</div>
            <ul class="gl-items">
              ${s.map(i=>this._renderItem(i,t.slug,e))}
            </ul>
          </div>
        `})}
    `}_sortSunk(t){return[...t].sort((t,e)=>t.checked!==e.checked?t.checked?1:-1:t.created_ts.localeCompare(e.created_ts))}_renderItem(t,e,i){if(this._editingId===t.id)return q`<li class="gl-item">${this._renderEdit(t,e,i)}</li>`;const s=t.qty?`${this._fmtNum(t.qty.value)} ${this._unitLabel(t.qty.unit)}`:"";return q`
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
          ${s?q`<div class="gl-item-qty">${s}</div>`:V}
        </div>
        <button
          class="gl-icon-btn"
          title=${i("delete")}
          @click=${()=>this._api?.deleteItem(e,t.id)}
        >\u2715</button>
      </li>
    `}_renderEdit(t,e,i){return q`
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
    `}_renderFooter(t){const e=this._activeList(),i=!!e?.items.some(t=>t.checked);return q`
      <div class="gl-footer">
        <button
          class="gl-clear-btn"
          ?disabled=${!i}
          @click=${()=>e&&this._api?.clearChecked(e.slug)}
        >
          ${t("clear_checked")}
        </button>
      </div>
    `}_renderArchive(t){const e=this._activeSlug,i=e&&this._snapshot?.archives?.[e]||[];return q`
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

          ${i.length?q`<ul class="gl-archive-list">
                ${i.map(e=>this._renderArchiveRow(e,t))}
              </ul>`:q`<div class="gl-empty">${t("no_archive")}</div>`}
        </div>
      </div>
    `}_renderArchiveRow(t,e){const i=t.item.qty?`${this._fmtNum(t.item.qty.value)} ${this._unitLabel(t.item.qty.unit)}`:"";return q`
      <li class="gl-archive-row">
        <span class="gl-archive-name">${t.item.name}</span>
        ${i?q`<span class="gl-archive-qty">${i}</span>`:V}
        <span class="gl-archive-ts"
          >${e("archived_on")} ${this._fmtArchiveTs(t.archived_ts)}</span
        >
      </li>
    `}_fmtArchiveTs(t){const e=new Date(t);return isNaN(e.getTime())?t:e.toLocaleDateString(this._lang,{year:"numeric",month:"short",day:"numeric"})}_renderCategoryManager(t){const e=this._categories();return q`
      <div
        class="gl-overlay"
        @click=${t=>{t.target===t.currentTarget&&this._closeCatManager()}}
      >
        <div class="gl-sheet">
          <div class="gl-sheet-header">
            <h3>${t("categories")}</h3>
            <button
              class="gl-icon-btn"
              title=${t("close")}
              @click=${()=>this._closeCatManager()}
            >\u2715</button>
          </div>

          ${e.length?q`<ul class="gl-catlist">
                ${e.map((i,s)=>this._renderCatRow(i,s,e.length,t))}
              </ul>`:q`<div class="gl-empty">${t("no_categories")}</div>`}

          <div class="gl-cat-new">
            <input
              .value=${this._newCatEn}
              placeholder=${t("category_name_en")}
              @input=${t=>this._newCatEn=t.target.value}
            />
            <input
              .value=${this._newCatDe}
              placeholder=${t("category_name_de")}
              @input=${t=>this._newCatDe=t.target.value}
            />
            <button class="gl-add-btn" @click=${()=>this._commitNewCategory()}>
              ${t("add_category")}
            </button>
          </div>
        </div>
      </div>
    `}_renderCatRow(t,e,i,s){return q`
      <li class="gl-catrow">
        <span class="gl-lang-tag">EN</span>
        <input
          class="gl-cat-label"
          .value=${t.labels.en??""}
          @change=${e=>this._renameCategory(t,"en",e.target.value)}
        />
        <span class="gl-lang-tag">DE</span>
        <input
          class="gl-cat-label"
          .value=${t.labels.de??""}
          @change=${e=>this._renameCategory(t,"de",e.target.value)}
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
    `}_categories(){return this._snapshot?.categories??[]}_catLabel(t){return t.labels[this._lang]??t.labels.en??t.id}_unitLabel(t){const e=this._units.find(e=>e.id===t);return e?e.labels[this._lang]??e.labels.en??t:t}_fmtNum(t){return Number.isInteger(t)?String(t):t.toFixed(2).replace(/0+$/,"")}_bumpQty(t){this._draftQty=Math.max(0,Math.round(100*(this._draftQty+t))/100)}_beginEdit(t){this._editingId=t.id,this._editValue=t.name}_cancelEdit(){this._editingId=null,this._editValue=""}_saveEdit(t,e){const i=this._editValue.trim();i&&i!==e.name&&this._api?.updateItem(t,e.id,{name:i}),this._cancelEdit()}_commitAdd(){const t=this._draftName.trim(),e=this._activeList();t&&e&&this._api&&(this._api.addItem(e.slug,t,{category:this._draftCategory,qty_value:this._draftQty||null,qty_unit:this._draftQty?this._draftUnit||this._defaultUnit:null}),this._draftName="")}_closeCatManager(){this._catManagerOpen=!1,this._newCatEn="",this._newCatDe=""}_commitNewCategory(){const t=this._newCatEn.trim(),e=this._newCatDe.trim();if(!t&&!e)return;const i={};t&&(i.en=t),e&&(i.de=e),i.en||(i.en=e),this._api?.createCategory(i),this._newCatEn="",this._newCatDe=""}_renameCategory(t,e,i){const s=i.trim();if(s===(t.labels[e]??""))return;const r={...t.labels};s?r[e]=s:delete r[e],r.en||(r.en=s||r.de||t.id),this._api?.updateCategory(t.id,{labels:r})}_moveCategory(t,e){const i=this._categories().map(t=>t.id),s=t+e;s<0||s>=i.length||([i[t],i[s]]=[i[s],i[t]],this._api?.reorderCategories(i))}_deleteCategory(t,e){window.confirm(e("delete_category_confirm"))&&this._api?.deleteCategory(t.id)}};mt.styles=pt,t([dt({attribute:!1})],mt.prototype,"hass",void 0),t([ht()],mt.prototype,"_config",void 0),t([ht()],mt.prototype,"_snapshot",void 0),t([ht()],mt.prototype,"_units",void 0),t([ht()],mt.prototype,"_defaultUnit",void 0),t([ht()],mt.prototype,"_activeSlug",void 0),t([ht()],mt.prototype,"_editingId",void 0),t([ht()],mt.prototype,"_editValue",void 0),t([ht()],mt.prototype,"_draftName",void 0),t([ht()],mt.prototype,"_draftQty",void 0),t([ht()],mt.prototype,"_draftUnit",void 0),t([ht()],mt.prototype,"_draftCategory",void 0),t([ht()],mt.prototype,"_catManagerOpen",void 0),t([ht()],mt.prototype,"_archiveOpen",void 0),t([ht()],mt.prototype,"_newCatEn",void 0),t([ht()],mt.prototype,"_newCatDe",void 0),mt=t([(t=>(e,i)=>{void 0!==i?i.addInitializer(()=>{customElements.define(t,e)}):customElements.define(t,e)})("grocery-list-card")],mt),window.customCards=window.customCards||[],window.customCards.push({type:"grocery-list-card",name:"Grocery List Card",description:"A slick, mobile-first grocery list with categories and sync."});export{mt as GroceryListCard};
