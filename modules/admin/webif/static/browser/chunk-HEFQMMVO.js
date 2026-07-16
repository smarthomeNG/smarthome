import{a as me}from"./chunk-BS6CGNTB.js";import{a as Ge,b as je}from"./chunk-QLATPZVE.js";import{b as ze,d as Ke,i as qe,s as Qe,z as We}from"./chunk-TWKP3LGB.js";import{b as $e,k as He}from"./chunk-JKP3TXC4.js";import{Ma as Be,Q as ae,Ra as Fe,T as U,U as P,Ua as pe,V as H,Va as se,Wa as ce,Y as xe,Ya as de,ab as ue,bb as Re,cb as E,db as De,f as Me,gb as Ue,ib as Pe,jb as Ne,n as ne,o as Ae,p as ie,q as Le,r as oe,ta as re,ua as k,v as le}from"./chunk-XMFB5O6P.js";import{Eb as p,Fb as h,Fc as M,G as L,Gb as _,Hb as F,Kc as te,Lb as T,Mb as O,Nb as S,Ob as C,Oc as ye,Sa as Ie,Sb as v,T as be,U as K,Ub as r,Va as s,Vb as Ce,Wb as we,X as G,Xb as X,Xc as f,Yb as Te,Yc as D,Z as w,Zb as x,_b as b,cb as _e,cc as q,da as d,dc as Oe,ea as u,fa as B,fc as $,gc as m,hb as W,hc as R,ic as Q,jc as ge,ka as I,la as ve,lb as Z,mb as J,nb as c,nc as Se,o as A,oa as j,oc as Ee,pc as Ve,sc as Y,ta as N,tc as ke,u as z,uc as V,vb as y,vc as ee,wc as fe}from"./chunk-25ZXD53X.js";var Ze=class i{constructor(){this.http=w(Me);this.appConfig=w(Ue);this.log=w(Pe)}getItemList(){let l=this.appConfig.apiUrl+"items/list/";return this.http.get(l).pipe(L(e=>(this.log.error("ItemsApiService.getItemList(): Could not read item list - "+e.error?.error),A([]))))}getItemTree(){let l=this.appConfig.apiUrl+"items/tree";return this.http.get(l).pipe(L(e=>(this.log.error("ItemsApiService.getItemTree(): Could not read item tree - "+e.error?.error),A([]))))}getCoreItemAttributes(){let l=this.appConfig.apiUrl+"items/attributes";return this.http.get(l).pipe(z(e=>e),L(e=>(this.log.error("ItemsApiService.getCoreItemAttributes(): Could not read attribute catalog - "+e.error?.error),A({}))))}getItemDetails(l){let e=this.appConfig.apiUrl+"items/"+encodeURIComponent(l);return this.http.get(e).pipe(L(t=>(this.log.error("ItemsApiService.getItemDetails("+l+"): Could not read item details - "+t.error?.error),A([]))))}changeItemValue(l,e){let t=this.appConfig.apiUrl+"items/"+encodeURIComponent(l);return this.http.put(t,JSON.stringify({value:e})).pipe(L(n=>(this.log.error("ItemsApiService.changeItemValue("+l+"): Could not set value - "+n.error?.error),A({}))))}createItem(l,e,t=!0,n,o=!1){let a=this.appConfig.apiUrl+"items/"+encodeURIComponent(l),g={config:e,persist:t};return n&&(g.filename=n),o&&(g.create_missing_parents=!0),this.http.post(a,JSON.stringify(g))}editItem(l,e){let t=this.appConfig.apiUrl+"items/"+encodeURIComponent(l);return this.http.patch(t,JSON.stringify({config:e}))}renameItem(l,e,t){let n=this.appConfig.apiUrl+"items/"+encodeURIComponent(l)+"/rename",o={new_path:e};return t&&(o.filename=t),this.http.post(n,JSON.stringify(o)).pipe(z(a=>a))}copyItem(l,e,t,n=!0){let o=this.appConfig.apiUrl+"items/"+encodeURIComponent(l)+"/copy",a={new_path:e};return t&&(a.filename=t),n||(a.include_children=!1),this.http.post(o,JSON.stringify(a)).pipe(z(g=>g))}deleteItem(l,e=!0,t=!1){let n=this.appConfig.apiUrl+"items/"+encodeURIComponent(l)+"?persist="+e+"&recursive="+t;return this.http.delete(n)}removeReferences(l){let e=this.appConfig.apiUrl+"items/"+encodeURIComponent(l)+"/remove_references";return this.http.post(e,"").pipe(z(t=>t))}getItemReferences(l){let e=this.appConfig.apiUrl+"items/"+encodeURIComponent(l)+"/references";return this.http.get(e).pipe(z(t=>t),L(t=>(this.log.error("ItemsApiService.getItemReferences("+l+"): Could not read references - "+t.error?.error),A(null))))}static{this.\u0275fac=function(e){return new(e||i)}}static{this.\u0275prov=K({token:i,factory:i.\u0275fac,providedIn:"root"})}};var Xe=`
    .p-chip {
        display: inline-flex;
        align-items: center;
        background: dt('chip.background');
        color: dt('chip.color');
        border-radius: dt('chip.border.radius');
        padding-block: dt('chip.padding.y');
        padding-inline: dt('chip.padding.x');
        gap: dt('chip.gap');
    }

    .p-chip-icon {
        color: dt('chip.icon.color');
        font-size: dt('chip.icon.size');
        width: dt('chip.icon.size');
        height: dt('chip.icon.size');
    }

    .p-chip-image {
        border-radius: 50%;
        width: dt('chip.image.width');
        height: dt('chip.image.height');
        margin-inline-start: calc(-1 * dt('chip.padding.y'));
    }

    .p-chip:has(.p-chip-remove-icon) {
        padding-inline-end: dt('chip.padding.y');
    }

    .p-chip:has(.p-chip-image) {
        padding-block-start: calc(dt('chip.padding.y') / 2);
        padding-block-end: calc(dt('chip.padding.y') / 2);
    }

    .p-chip-remove-icon {
        cursor: pointer;
        font-size: dt('chip.remove.icon.size');
        width: dt('chip.remove.icon.size');
        height: dt('chip.remove.icon.size');
        color: dt('chip.remove.icon.color');
        border-radius: 50%;
        transition:
            outline-color dt('chip.transition.duration'),
            box-shadow dt('chip.transition.duration');
        outline-color: transparent;
    }

    .p-chip-remove-icon:focus-visible {
        box-shadow: dt('chip.remove.icon.focus.ring.shadow');
        outline: dt('chip.remove.icon.focus.ring.width') dt('chip.remove.icon.focus.ring.style') dt('chip.remove.icon.focus.ring.color');
        outline-offset: dt('chip.remove.icon.focus.ring.offset');
    }
`;var dt=["removeicon"],ut=["*"];function mt(i,l){if(i&1){let e=C();h(0,"img",4),v("error",function(n){d(e);let o=r();return u(o.imageError(n))}),_()}if(i&2){let e=r();m(e.cx("image")),p("pBind",e.ptm("image"))("src",e.image,Ie)("alt",e.alt)}}function ht(i,l){if(i&1&&F(0,"span",6),i&2){let e=r(2);m(e.icon),p("pBind",e.ptm("icon"))("ngClass",e.cx("icon"))}}function _t(i,l){if(i&1&&c(0,ht,1,4,"span",5),i&2){let e=r();p("ngIf",e.icon)}}function gt(i,l){if(i&1&&(h(0,"div",7),R(1),_()),i&2){let e=r();m(e.cx("label")),p("pBind",e.ptm("label")),s(),Q(e.label)}}function ft(i,l){if(i&1){let e=C();h(0,"span",11),v("click",function(n){d(e);let o=r(3);return u(o.close(n))})("keydown",function(n){d(e);let o=r(3);return u(o.onKeydown(n))}),_()}if(i&2){let e=r(3);m(e.removeIcon),p("pBind",e.ptm("removeIcon"))("ngClass",e.cx("removeIcon")),y("tabindex",e.disabled?-1:0)("aria-label",e.removeAriaLabel)}}function yt(i,l){if(i&1){let e=C();B(),h(0,"svg",12),v("click",function(n){d(e);let o=r(3);return u(o.close(n))})("keydown",function(n){d(e);let o=r(3);return u(o.onKeydown(n))}),_()}if(i&2){let e=r(3);m(e.cx("removeIcon")),p("pBind",e.ptm("removeIcon")),y("tabindex",e.disabled?-1:0)("aria-label",e.removeAriaLabel)}}function xt(i,l){if(i&1&&(T(0),c(1,ft,1,6,"span",9)(2,yt,1,5,"svg",10),O()),i&2){let e=r(2);s(),p("ngIf",e.removeIcon),s(),p("ngIf",!e.removeIcon)}}function bt(i,l){}function vt(i,l){i&1&&c(0,bt,0,0,"ng-template")}function It(i,l){if(i&1){let e=C();h(0,"span",13),v("click",function(n){d(e);let o=r(2);return u(o.close(n))})("keydown",function(n){d(e);let o=r(2);return u(o.onKeydown(n))}),c(1,vt,1,0,null,14),_()}if(i&2){let e=r(2);m(e.cx("removeIcon")),p("pBind",e.ptm("removeIcon")),y("tabindex",e.disabled?-1:0)("aria-label",e.removeAriaLabel),s(),p("ngTemplateOutlet",e.removeIconTemplate||e._removeIconTemplate)}}function Ct(i,l){if(i&1&&(T(0),c(1,xt,3,2,"ng-container",3)(2,It,2,6,"span",8),O()),i&2){let e=r();s(),p("ngIf",!e.removeIconTemplate&&!e._removeIconTemplate),s(),p("ngIf",e.removeIconTemplate||e._removeIconTemplate)}}var wt={root:({instance:i})=>({display:!i.visible&&"none"})},Tt={root:({instance:i})=>["p-chip p-component",{"p-disabled":i.disabled}],image:"p-chip-image",icon:"p-chip-icon",label:"p-chip-label",removeIcon:"p-chip-remove-icon"},Ye=(()=>{class i extends de{name="chip";style=Xe;classes=Tt;inlineStyles=wt;static \u0275fac=(()=>{let e;return function(n){return(e||(e=N(i)))(n||i)}})();static \u0275prov=K({token:i,factory:i.\u0275fac})}return i})();var et=new G("CHIP_INSTANCE"),tt=(()=>{class i extends Re{componentName="Chip";$pcChip=w(et,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=w(E,{self:!0});onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptms(["host","root"]))}label;icon;image;alt;styleClass;disabled=!1;removable=!1;removeIcon;onRemove=new I;onImageError=new I;visible=!0;get removeAriaLabel(){return this.config.getTranslation(ce.ARIA).removeLabel}get chipProps(){return this._chipProps}set chipProps(e){this._chipProps=e,e&&typeof e=="object"&&Object.entries(e).forEach(([t,n])=>this[`_${t}`]!==n&&(this[`_${t}`]=n))}_chipProps;_componentStyle=w(Ye);removeIconTemplate;templates;_removeIconTemplate;onAfterContentInit(){this.templates.forEach(e=>{e.getType()==="removeicon"?this._removeIconTemplate=e.template:this._removeIconTemplate=e.template})}onChanges(e){if(e.chipProps&&e.chipProps.currentValue){let{currentValue:t}=e.chipProps;t.label!==void 0&&(this.label=t.label),t.icon!==void 0&&(this.icon=t.icon),t.image!==void 0&&(this.image=t.image),t.alt!==void 0&&(this.alt=t.alt),t.styleClass!==void 0&&(this.styleClass=t.styleClass),t.removable!==void 0&&(this.removable=t.removable),t.removeIcon!==void 0&&(this.removeIcon=t.removeIcon)}}close(e){this.visible=!1,this.onRemove.emit(e)}onKeydown(e){(e.key==="Enter"||e.key==="Backspace")&&this.close(e)}imageError(e){this.onImageError.emit(e)}get dataP(){return this.cn({removable:this.removable})}static \u0275fac=(()=>{let e;return function(n){return(e||(e=N(i)))(n||i)}})();static \u0275cmp=W({type:i,selectors:[["p-chip"]],contentQueries:function(t,n,o){if(t&1&&X(o,dt,4)(o,pe,4),t&2){let a;x(a=b())&&(n.removeIconTemplate=a.first),x(a=b())&&(n.templates=a)}},hostVars:6,hostBindings:function(t,n){t&2&&(y("aria-label",n.label)("data-p",n.dataP),$(n.sx("root")),m(n.cn(n.cx("root"),n.styleClass)))},inputs:{label:"label",icon:"icon",image:"image",alt:"alt",styleClass:"styleClass",disabled:[2,"disabled","disabled",f],removable:[2,"removable","removable",f],removeIcon:"removeIcon",chipProps:"chipProps"},outputs:{onRemove:"onRemove",onImageError:"onImageError"},features:[Y([Ye,{provide:et,useExisting:i},{provide:ue,useExisting:i}]),Z([E]),J],ngContentSelectors:ut,decls:6,vars:4,consts:[["iconTemplate",""],[3,"pBind","class","src","alt","error",4,"ngIf","ngIfElse"],[3,"pBind","class",4,"ngIf"],[4,"ngIf"],[3,"error","pBind","src","alt"],[3,"pBind","class","ngClass",4,"ngIf"],[3,"pBind","ngClass"],[3,"pBind"],["role","button",3,"pBind","class","click","keydown",4,"ngIf"],["role","button",3,"pBind","class","ngClass","click","keydown",4,"ngIf"],["data-p-icon","times-circle","role","button",3,"pBind","class","click","keydown",4,"ngIf"],["role","button",3,"click","keydown","pBind","ngClass"],["data-p-icon","times-circle","role","button",3,"click","keydown","pBind"],["role","button",3,"click","keydown","pBind"],[4,"ngTemplateOutlet"]],template:function(t,n){if(t&1&&(Ce(),we(0),c(1,mt,1,5,"img",1)(2,_t,1,1,"ng-template",null,0,M)(4,gt,2,4,"div",2)(5,Ct,3,2,"ng-container",3)),t&2){let o=q(3);s(),p("ngIf",n.image)("ngIfElse",o),s(3),p("ngIf",n.label),s(),p("ngIf",n.removable)}},dependencies:[le,ne,ie,oe,me,se,E],encapsulation:2,changeDetection:0})}return i})();var nt=`
    .p-autocomplete {
        display: inline-flex;
    }

    .p-autocomplete-loader {
        position: absolute;
        top: 50%;
        margin-top: -0.5rem;
        inset-inline-end: dt('autocomplete.padding.x');
    }

    .p-autocomplete:has(.p-autocomplete-dropdown) .p-autocomplete-loader {
        inset-inline-end: calc(dt('autocomplete.dropdown.width') + dt('autocomplete.padding.x'));
    }

    .p-autocomplete:has(.p-autocomplete-dropdown) .p-autocomplete-input {
        flex: 1 1 auto;
        width: 1%;
    }

    .p-autocomplete:has(.p-autocomplete-dropdown) .p-autocomplete-input,
    .p-autocomplete:has(.p-autocomplete-dropdown) .p-autocomplete-input-multiple {
        border-start-end-radius: 0;
        border-end-end-radius: 0;
    }

    .p-autocomplete-dropdown {
        cursor: pointer;
        display: inline-flex;
        user-select: none;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        position: relative;
        width: dt('autocomplete.dropdown.width');
        border-start-end-radius: dt('autocomplete.dropdown.border.radius');
        border-end-end-radius: dt('autocomplete.dropdown.border.radius');
        background: dt('autocomplete.dropdown.background');
        border: 1px solid dt('autocomplete.dropdown.border.color');
        border-inline-start: 0 none;
        color: dt('autocomplete.dropdown.color');
        transition:
            background dt('autocomplete.transition.duration'),
            color dt('autocomplete.transition.duration'),
            border-color dt('autocomplete.transition.duration'),
            outline-color dt('autocomplete.transition.duration'),
            box-shadow dt('autocomplete.transition.duration');
        outline-color: transparent;
    }

    .p-autocomplete-dropdown:not(:disabled):hover {
        background: dt('autocomplete.dropdown.hover.background');
        border-color: dt('autocomplete.dropdown.hover.border.color');
        color: dt('autocomplete.dropdown.hover.color');
    }

    .p-autocomplete-dropdown:not(:disabled):active {
        background: dt('autocomplete.dropdown.active.background');
        border-color: dt('autocomplete.dropdown.active.border.color');
        color: dt('autocomplete.dropdown.active.color');
    }

    .p-autocomplete-dropdown:focus-visible {
        box-shadow: dt('autocomplete.dropdown.focus.ring.shadow');
        outline: dt('autocomplete.dropdown.focus.ring.width') dt('autocomplete.dropdown.focus.ring.style') dt('autocomplete.dropdown.focus.ring.color');
        outline-offset: dt('autocomplete.dropdown.focus.ring.offset');
    }

    .p-autocomplete-overlay {
        position: absolute;
        top: 0;
        left: 0;
        background: dt('autocomplete.overlay.background');
        color: dt('autocomplete.overlay.color');
        border: 1px solid dt('autocomplete.overlay.border.color');
        border-radius: dt('autocomplete.overlay.border.radius');
        box-shadow: dt('autocomplete.overlay.shadow');
        min-width: 100%;
    }

    .p-autocomplete-list-container {
        overflow: auto;
    }

    .p-autocomplete-list {
        margin: 0;
        list-style-type: none;
        display: flex;
        flex-direction: column;
        gap: dt('autocomplete.list.gap');
        padding: dt('autocomplete.list.padding');
    }

    .p-autocomplete-option {
        cursor: pointer;
        white-space: nowrap;
        position: relative;
        overflow: hidden;
        display: flex;
        align-items: center;
        padding: dt('autocomplete.option.padding');
        border: 0 none;
        color: dt('autocomplete.option.color');
        background: transparent;
        transition:
            background dt('autocomplete.transition.duration'),
            color dt('autocomplete.transition.duration'),
            border-color dt('autocomplete.transition.duration');
        border-radius: dt('autocomplete.option.border.radius');
    }

    .p-autocomplete-option:not(.p-autocomplete-option-selected):not(.p-disabled).p-focus {
        background: dt('autocomplete.option.focus.background');
        color: dt('autocomplete.option.focus.color');
    }

    .p-autocomplete-option:not(.p-autocomplete-option-selected):not(.p-disabled):hover {
        background: dt('autocomplete.option.focus.background');
        color: dt('autocomplete.option.focus.color');
    }

    .p-autocomplete-option-selected {
        background: dt('autocomplete.option.selected.background');
        color: dt('autocomplete.option.selected.color');
    }

    .p-autocomplete-option-selected.p-focus {
        background: dt('autocomplete.option.selected.focus.background');
        color: dt('autocomplete.option.selected.focus.color');
    }

    .p-autocomplete-option-group {
        margin: 0;
        padding: dt('autocomplete.option.group.padding');
        color: dt('autocomplete.option.group.color');
        background: dt('autocomplete.option.group.background');
        font-weight: dt('autocomplete.option.group.font.weight');
    }

    .p-autocomplete-input-multiple {
        margin: 0;
        list-style-type: none;
        cursor: text;
        overflow: hidden;
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        padding: calc(dt('autocomplete.padding.y') / 2) dt('autocomplete.padding.x');
        gap: calc(dt('autocomplete.padding.y') / 2);
        color: dt('autocomplete.color');
        background: dt('autocomplete.background');
        border: 1px solid dt('autocomplete.border.color');
        border-radius: dt('autocomplete.border.radius');
        width: 100%;
        transition:
            background dt('autocomplete.transition.duration'),
            color dt('autocomplete.transition.duration'),
            border-color dt('autocomplete.transition.duration'),
            outline-color dt('autocomplete.transition.duration'),
            box-shadow dt('autocomplete.transition.duration');
        outline-color: transparent;
        box-shadow: dt('autocomplete.shadow');
    }

    .p-autocomplete-input-multiple.p-disabled {
        opacity: 1;
        background: dt('autocomplete.disabled.background');
        color: dt('autocomplete.disabled.color');
    }

    .p-autocomplete-input-multiple:not(.p-disabled):hover {
        border-color: dt('autocomplete.hover.border.color');
    }

    .p-autocomplete.p-focus .p-autocomplete-input-multiple:not(.p-disabled) {
        border-color: dt('autocomplete.focus.border.color');
        box-shadow: dt('autocomplete.focus.ring.shadow');
        outline: dt('autocomplete.focus.ring.width') dt('autocomplete.focus.ring.style') dt('autocomplete.focus.ring.color');
        outline-offset: dt('autocomplete.focus.ring.offset');
    }

    .p-autocomplete.p-invalid .p-autocomplete-input-multiple {
        border-color: dt('autocomplete.invalid.border.color');
    }

    .p-variant-filled.p-autocomplete-input-multiple {
        background: dt('autocomplete.filled.background');
    }

    .p-autocomplete-input-multiple.p-variant-filled:not(.p-disabled):hover {
        background: dt('autocomplete.filled.hover.background');
    }

    .p-autocomplete.p-focus .p-autocomplete-input-multiple.p-variant-filled:not(.p-disabled) {
        background: dt('autocomplete.filled.focus.background');
    }

    .p-autocomplete-chip.p-chip {
        padding-block-start: calc(dt('autocomplete.padding.y') / 2);
        padding-block-end: calc(dt('autocomplete.padding.y') / 2);
        border-radius: dt('autocomplete.chip.border.radius');
    }

    .p-autocomplete-input-multiple:has(.p-autocomplete-chip) {
        padding-inline-start: calc(dt('autocomplete.padding.y') / 2);
        padding-inline-end: calc(dt('autocomplete.padding.y') / 2);
    }

    .p-autocomplete-chip-item.p-focus .p-autocomplete-chip {
        background: dt('autocomplete.chip.focus.background');
        color: dt('autocomplete.chip.focus.color');
    }

    .p-autocomplete-input-chip {
        flex: 1 1 auto;
        display: inline-flex;
        padding-block-start: calc(dt('autocomplete.padding.y') / 2);
        padding-block-end: calc(dt('autocomplete.padding.y') / 2);
    }

    .p-autocomplete-input-chip input {
        border: 0 none;
        outline: 0 none;
        background: transparent;
        margin: 0;
        padding: 0;
        box-shadow: none;
        border-radius: 0;
        width: 100%;
        font-family: inherit;
        font-feature-settings: inherit;
        font-size: 1rem;
        color: inherit;
    }

    .p-autocomplete-input-chip input::placeholder {
        color: dt('autocomplete.placeholder.color');
    }

    .p-autocomplete.p-invalid .p-autocomplete-input-chip input::placeholder {
        color: dt('autocomplete.invalid.placeholder.color');
    }

    .p-autocomplete-empty-message {
        padding: dt('autocomplete.empty.message.padding');
    }

    .p-autocomplete-fluid {
        display: flex;
    }

    .p-autocomplete-fluid:has(.p-autocomplete-dropdown) .p-autocomplete-input {
        width: 1%;
    }

    .p-autocomplete:has(.p-inputtext-sm) .p-autocomplete-dropdown {
        width: dt('autocomplete.dropdown.sm.width');
    }

    .p-autocomplete:has(.p-inputtext-sm) .p-autocomplete-dropdown .p-icon {
        font-size: dt('form.field.sm.font.size');
        width: dt('form.field.sm.font.size');
        height: dt('form.field.sm.font.size');
    }

    .p-autocomplete:has(.p-inputtext-lg) .p-autocomplete-dropdown {
        width: dt('autocomplete.dropdown.lg.width');
    }

    .p-autocomplete:has(.p-inputtext-lg) .p-autocomplete-dropdown .p-icon {
        font-size: dt('form.field.lg.font.size');
        width: dt('form.field.lg.font.size');
        height: dt('form.field.lg.font.size');
    }

    .p-autocomplete-clear-icon {
        position: absolute;
        top: 50%;
        margin-top: -0.5rem;
        cursor: pointer;
        color: dt('form.field.icon.color');
        inset-inline-end: dt('autocomplete.padding.x');
    }

    .p-autocomplete:has(.p-autocomplete-dropdown) .p-autocomplete-clear-icon {
        inset-inline-end: calc(dt('autocomplete.padding.x') + dt('autocomplete.dropdown.width'));
    }

    .p-autocomplete:has(.p-autocomplete-clear-icon) .p-autocomplete-input {
        padding-inline-end: calc((dt('form.field.padding.x') * 2) + dt('icon.size'));
    }

    .p-inputgroup .p-autocomplete-dropdown {
        border-radius: 0;
    }

    .p-inputgroup > .p-autocomplete:last-child:has(.p-autocomplete-dropdown) > .p-autocomplete-input {
        border-start-end-radius: 0;
        border-end-end-radius: 0;
    }

    .p-inputgroup > .p-autocomplete:last-child .p-autocomplete-dropdown {
        border-start-end-radius: dt('autocomplete.dropdown.border.radius');
        border-end-end-radius: dt('autocomplete.dropdown.border.radius');
    }
`;var Ot=["item"],St=["empty"],Et=["header"],Vt=["footer"],kt=["selecteditem"],Mt=["group"],At=["loader"],Lt=["removeicon"],Bt=["loadingicon"],Ft=["clearicon"],Rt=["dropdownicon"],Dt=["focusInput"],zt=["multiIn"],Kt=["multiContainer"],$t=["ddBtn"],Ut=["items"],Pt=["scroller"],Ht=["overlay"],Nt=i=>({i}),lt=i=>({$implicit:i}),qt=(i,l,e)=>({removeCallback:i,index:l,class:e}),he=i=>({height:i}),at=(i,l)=>({$implicit:i,options:l}),Qt=i=>({options:i}),Gt=()=>({}),jt=(i,l,e)=>({option:i,i:l,scrollerOptions:e}),Wt=(i,l)=>({$implicit:i,index:l});function Zt(i,l){if(i&1){let e=C();h(0,"input",18,2),v("input",function(n){d(e);let o=r();return u(o.onInput(n))})("keydown",function(n){d(e);let o=r();return u(o.onKeyDown(n))})("change",function(n){d(e);let o=r();return u(o.onInputChange(n))})("focus",function(n){d(e);let o=r();return u(o.onInputFocus(n))})("blur",function(n){d(e);let o=r();return u(o.onInputBlur(n))})("paste",function(n){d(e);let o=r();return u(o.onInputPaste(n))})("keyup",function(n){d(e);let o=r();return u(o.onInputKeyUp(n))}),_()}if(i&2){let e=r();m(e.cn(e.cx("pcInputText"),e.inputStyleClass)),p("pAutoFocus",e.autofocus)("pt",e.ptm("pcInputText"))("ngStyle",e.inputStyle)("variant",e.$variant())("invalid",e.invalid())("pSize",e.size())("fluid",e.hasFluid)("pInputTextUnstyled",e.unstyled()),y("type",e.type)("value",e.inputValue())("id",e.inputId)("autocomplete",e.autocomplete)("placeholder",e.placeholder)("name",e.name())("minlength",e.minlength())("min",e.min())("max",e.max())("pattern",e.pattern())("size",e.inputSize())("maxlength",e.maxlength())("tabindex",e.$disabled()?-1:e.tabindex)("required",e.required()?"":void 0)("readonly",e.readonly?"":void 0)("disabled",e.$disabled()?"":void 0)("aria-label",e.ariaLabel)("aria-labelledby",e.ariaLabelledBy)("aria-required",e.required())("aria-expanded",e.overlayVisible??!1)("aria-controls",e.overlayVisible?e.id+"_list":null)("aria-activedescendant",e.focused?e.focusedOptionId:void 0)}}function Jt(i,l){if(i&1){let e=C();B(),h(0,"svg",21),v("click",function(){d(e);let n=r(2);return u(n.clear())}),_()}if(i&2){let e=r(2);m(e.cx("clearIcon")),p("pBind",e.ptm("clearIcon")),y("aria-hidden",!0)}}function Xt(i,l){}function Yt(i,l){i&1&&c(0,Xt,0,0,"ng-template")}function en(i,l){if(i&1){let e=C();h(0,"span",22),v("click",function(){d(e);let n=r(2);return u(n.clear())}),c(1,Yt,1,0,null,23),_()}if(i&2){let e=r(2);m(e.cx("clearIcon")),p("pBind",e.ptm("clearIcon")),y("aria-hidden",!0),s(),p("ngTemplateOutlet",e.clearIconTemplate||e._clearIconTemplate)}}function tn(i,l){if(i&1&&(T(0),c(1,Jt,1,4,"svg",19)(2,en,2,5,"span",20),O()),i&2){let e=r();s(),p("ngIf",!e.clearIconTemplate&&!e._clearIconTemplate),s(),p("ngIf",e.clearIconTemplate||e._clearIconTemplate)}}function nn(i,l){i&1&&S(0)}function on(i,l){if(i&1){let e=C();h(0,"span",22),v("click",function(n){d(e);let o=r(2).index,a=r(2);return u(!a.readonly&&!a.$disabled()?a.removeOption(n,o):"")}),B(),F(1,"svg",31),_()}if(i&2){let e=r(4);m(e.cx("chipIcon")),p("pBind",e.ptm("chipIcon")),s(),m(e.cx("chipIcon")),y("aria-hidden",!0)}}function ln(i,l){}function an(i,l){i&1&&c(0,ln,0,0,"ng-template")}function rn(i,l){if(i&1&&(h(0,"span",32),c(1,an,1,0,null,29),_()),i&2){let e=r(2).index,t=r(2);p("pBind",t.ptm("chipIcon")),y("aria-hidden",!0),s(),p("ngTemplateOutlet",t.removeIconTemplate||t._removeIconTemplate)("ngTemplateOutletContext",fe(4,qt,t.removeOption.bind(t),e,t.cx("chipIcon")))}}function pn(i,l){if(i&1&&c(0,on,2,6,"span",20)(1,rn,2,8,"span",30),i&2){let e=r(3);p("ngIf",!e.removeIconTemplate&&!e._removeIconTemplate),s(),p("ngIf",e.removeIconTemplate||e._removeIconTemplate)}}function sn(i,l){if(i&1){let e=C();h(0,"li",26,5)(2,"p-chip",28),v("onRemove",function(n){let o=d(e).index,a=r(2);return u(a.readonly?"":a.removeOption(n,o))}),c(3,nn,1,0,"ng-container",29)(4,pn,2,2,"ng-template",null,6,M),_()()}if(i&2){let e=l.$implicit,t=l.index,n=r(2);m(n.cx("chipItem",V(17,Nt,t))),p("pBind",n.ptm("chipItem")),y("id",n.id+"_multiple_option_"+t)("aria-label",n.getOptionLabel(e))("aria-setsize",n.modelValue().length)("aria-posinset",t+1)("aria-selected",!0),s(2),m(n.cx("pcChip")),p("pt",n.ptm("pcChip"))("label",!n.selectedItemTemplate&&!n._selectedItemTemplate&&n.getOptionLabel(e))("disabled",n.$disabled())("removable",!0)("unstyled",n.unstyled()),s(),p("ngTemplateOutlet",n.selectedItemTemplate||n._selectedItemTemplate)("ngTemplateOutletContext",V(19,lt,e))}}function cn(i,l){if(i&1){let e=C();h(0,"ul",24,3),v("focus",function(n){d(e);let o=r();return u(o.onMultipleContainerFocus(n))})("blur",function(n){d(e);let o=r();return u(o.onMultipleContainerBlur(n))})("keydown",function(n){d(e);let o=r();return u(o.onMultipleContainerKeyDown(n))}),c(2,sn,6,21,"li",25),h(3,"li",26)(4,"input",27,4),v("input",function(n){d(e);let o=r();return u(o.onInput(n))})("keydown",function(n){d(e);let o=r();return u(o.onKeyDown(n))})("change",function(n){d(e);let o=r();return u(o.onInputChange(n))})("focus",function(n){d(e);let o=r();return u(o.onInputFocus(n))})("blur",function(n){d(e);let o=r();return u(o.onInputBlur(n))})("paste",function(n){d(e);let o=r();return u(o.onInputPaste(n))})("keyup",function(n){d(e);let o=r();return u(o.onInputKeyUp(n))}),_()()()}if(i&2){let e=r();m(e.cx("inputMultiple")),p("pBind",e.ptm("inputMultiple"))("tabindex",-1),y("data-p",e.inputMultipleDataP)("aria-orientation","horizontal")("aria-activedescendant",e.focused?e.focusedMultipleOptionId:void 0),s(2),p("ngForOf",e.modelValue()),s(),m(e.cx("inputChip")),p("pBind",e.ptm("inputChip")),s(),m(e.cx("pcInputText")),p("pAutoFocus",e.autofocus)("pBind",e.ptm("input"))("ngStyle",e.inputStyle),y("type",e.type)("id",e.inputId)("autocomplete",e.autocomplete)("name",e.name())("minlength",e.minlength())("maxlength",e.maxlength())("size",e.size())("min",e.min())("max",e.max())("pattern",e.pattern())("placeholder",e.$filled()?null:e.placeholder)("tabindex",e.$disabled()?-1:e.tabindex)("required",e.required()?"":void 0)("readonly",e.readonly?"":void 0)("disabled",e.$disabled()?"":void 0)("aria-label",e.ariaLabel)("aria-labelledby",e.ariaLabelledBy)("aria-required",e.required())("aria-expanded",e.overlayVisible??!1)("aria-controls",e.overlayVisible?e.id+"_list":null)("aria-activedescendant",e.focused?e.focusedOptionId:void 0)}}function dn(i,l){if(i&1&&(B(),F(0,"svg",35)),i&2){let e=r(2);m(e.cx("loader")),p("pBind",e.ptm("loader"))("spin",!0),y("aria-hidden",!0)}}function un(i,l){}function mn(i,l){i&1&&c(0,un,0,0,"ng-template")}function hn(i,l){if(i&1&&(h(0,"span",32),c(1,mn,1,0,null,23),_()),i&2){let e=r(2);m(e.cx("loader")),p("pBind",e.ptm("loader")),y("aria-hidden",!0),s(),p("ngTemplateOutlet",e.loadingIconTemplate||e._loadingIconTemplate)}}function _n(i,l){if(i&1&&(T(0),c(1,dn,1,5,"svg",33)(2,hn,2,5,"span",34),O()),i&2){let e=r();s(),p("ngIf",!e.loadingIconTemplate&&!e._loadingIconTemplate),s(),p("ngIf",e.loadingIconTemplate||e._loadingIconTemplate)}}function gn(i,l){if(i&1&&F(0,"span",38),i&2){let e=r(2);p("ngClass",e.dropdownIcon),y("aria-hidden",!0)}}function fn(i,l){if(i&1&&(B(),F(0,"svg",40)),i&2){let e=r(3);p("pBind",e.ptm("dropdown"))}}function yn(i,l){}function xn(i,l){i&1&&c(0,yn,0,0,"ng-template")}function bn(i,l){if(i&1&&(T(0),c(1,fn,1,1,"svg",39)(2,xn,1,0,null,23),O()),i&2){let e=r(2);s(),p("ngIf",!e.dropdownIconTemplate&&!e._dropdownIconTemplate),s(),p("ngTemplateOutlet",e.dropdownIconTemplate||e._dropdownIconTemplate)}}function vn(i,l){if(i&1){let e=C();h(0,"button",36,7),v("click",function(n){d(e);let o=r();return u(o.handleDropdownClick(n))}),c(2,gn,1,2,"span",37)(3,bn,3,2,"ng-container",14),_()}if(i&2){let e=r();m(e.cx("dropdown")),p("pBind",e.ptm("dropdown"))("disabled",e.$disabled()),y("aria-label",e.dropdownAriaLabel)("tabindex",e.tabindex),s(2),p("ngIf",e.dropdownIcon),s(),p("ngIf",!e.dropdownIcon)}}function In(i,l){i&1&&S(0)}function Cn(i,l){i&1&&S(0)}function wn(i,l){if(i&1&&c(0,Cn,1,0,"ng-container",29),i&2){let e=l.$implicit,t=l.options;r(2);let n=q(6);p("ngTemplateOutlet",n)("ngTemplateOutletContext",ee(2,at,e,t))}}function Tn(i,l){i&1&&S(0)}function On(i,l){if(i&1&&c(0,Tn,1,0,"ng-container",29),i&2){let e=l.options,t=r(4);p("ngTemplateOutlet",t.loaderTemplate||t._loaderTemplate)("ngTemplateOutletContext",V(2,Qt,e))}}function Sn(i,l){i&1&&(T(0),c(1,On,1,4,"ng-template",null,10,M),O())}function En(i,l){if(i&1){let e=C();h(0,"p-scroller",45,9),v("onLazyLoad",function(n){d(e);let o=r(2);return u(o.onLazyLoad.emit(n))}),c(2,wn,1,5,"ng-template",null,1,M)(4,Sn,3,0,"ng-container",14),_()}if(i&2){let e=r(2);$(V(10,he,e.scrollHeight)),p("tabindex",-1)("pt",e.ptm("virtualScroller"))("items",e.visibleOptions())("itemSize",e.virtualScrollItemSize)("autoSize",!0)("lazy",e.lazy)("options",e.virtualScrollOptions),s(4),p("ngIf",e.loaderTemplate||e._loaderTemplate)}}function Vn(i,l){i&1&&S(0)}function kn(i,l){if(i&1&&(T(0),c(1,Vn,1,0,"ng-container",29),O()),i&2){r();let e=q(6),t=r();s(),p("ngTemplateOutlet",e)("ngTemplateOutletContext",ee(3,at,t.visibleOptions(),ke(2,Gt)))}}function Mn(i,l){if(i&1&&(h(0,"span"),R(1),_()),i&2){let e=r(2).$implicit,t=r(3);s(),Q(t.getOptionGroupLabel(e.optionGroup))}}function An(i,l){i&1&&S(0)}function Ln(i,l){if(i&1&&(T(0),h(1,"li",49),c(2,Mn,2,1,"span",14)(3,An,1,0,"ng-container",29),_(),O()),i&2){let e=r(),t=e.$implicit,n=e.index,o=r().options,a=r(2);s(),m(a.cx("optionGroup")),p("pBind",a.ptm("optionGroup"))("ngStyle",V(8,he,o.itemSize+"px")),y("id",a.id+"_"+a.getOptionIndex(n,o)),s(),p("ngIf",!a.groupTemplate),s(),p("ngTemplateOutlet",a.groupTemplate)("ngTemplateOutletContext",V(10,lt,t.optionGroup))}}function Bn(i,l){if(i&1&&(h(0,"span"),R(1),_()),i&2){let e=r(2).$implicit,t=r(3);s(),Q(t.getOptionLabel(e))}}function Fn(i,l){i&1&&S(0)}function Rn(i,l){if(i&1){let e=C();T(0),h(1,"li",50),v("click",function(n){d(e);let o=r().$implicit,a=r(3);return u(a.onOptionSelect(n,o))})("mouseenter",function(n){d(e);let o=r().index,a=r().options,g=r(2);return u(g.onOptionMouseEnter(n,g.getOptionIndex(o,a)))}),c(2,Bn,2,1,"span",14)(3,Fn,1,0,"ng-container",29),_(),O()}if(i&2){let e=r(),t=e.$implicit,n=e.index,o=r().options,a=r(2);s(),m(a.cx("option",fe(15,jt,t,n,o))),p("pBind",a.getPTOptions(t,o,n,"option"))("ngStyle",V(19,he,o.itemSize+"px")),y("id",a.id+"_"+a.getOptionIndex(n,o))("aria-label",a.getOptionLabel(t))("aria-selected",a.isSelected(t))("data-p-selected",a.isSelected(t))("aria-disabled",a.isOptionDisabled(t))("data-p-focused",a.focusedOptionIndex()===a.getOptionIndex(n,o))("aria-setsize",a.ariaSetSize)("aria-posinset",a.getAriaPosInset(a.getOptionIndex(n,o))),s(),p("ngIf",!a.itemTemplate&&!a._itemTemplate),s(),p("ngTemplateOutlet",a.itemTemplate||a._itemTemplate)("ngTemplateOutletContext",ee(21,Wt,t,o.getOptions?o.getOptions(n):n))}}function Dn(i,l){if(i&1&&c(0,Ln,4,12,"ng-container",14)(1,Rn,4,24,"ng-container",14),i&2){let e=l.$implicit,t=r(3);p("ngIf",t.isOptionGroup(e)),s(),p("ngIf",!t.isOptionGroup(e))}}function zn(i,l){if(i&1&&(T(0),R(1),O()),i&2){let e=r(4);s(),ge(" ",e.searchResultMessageText," ")}}function Kn(i,l){i&1&&S(0,null,12)}function $n(i,l){if(i&1&&(h(0,"li",49),c(1,zn,2,1,"ng-container",51)(2,Kn,2,0,"ng-container",23),_()),i&2){let e=r().options,t=r(2);m(t.cx("emptyMessage")),p("pBind",t.ptm("emptyMessage"))("ngStyle",V(7,he,e.itemSize+"px")),s(),p("ngIf",!t.emptyTemplate&&!t._emptyTemplate)("ngIfElse",t.empty),s(),p("ngTemplateOutlet",t.emptyTemplate||t._emptyTemplate)}}function Un(i,l){if(i&1&&(h(0,"ul",46,11),c(2,Dn,2,2,"ng-template",47)(3,$n,3,9,"li",48),_()),i&2){let e=l.$implicit,t=l.options,n=r(2);$(t.contentStyle),m(n.cn(n.cx("list"),t.contentStyleClass)),p("pBind",n.ptm("list")),y("id",n.id+"_list")("aria-label",n.listLabel),s(2),p("ngForOf",e),s(),p("ngIf",!e||e&&e.length===0&&n.showEmptyMessage)}}function Pn(i,l){i&1&&S(0)}function Hn(i,l){if(i&1&&(h(0,"div",41),c(1,In,1,0,"ng-container",23),h(2,"div",42),c(3,En,5,12,"p-scroller",43)(4,kn,2,6,"ng-container",14),_(),c(5,Un,4,9,"ng-template",null,8,M)(7,Pn,1,0,"ng-container",23),_(),h(8,"span",44),R(9),_()),i&2){let e=r();m(e.cn(e.cx("overlay"),e.panelStyleClass)),p("pBind",e.ptm("overlay"))("ngStyle",e.panelStyle),s(),p("ngTemplateOutlet",e.headerTemplate||e._headerTemplate),s(),m(e.cx("listContainer")),Oe("max-height",e.virtualScroll?"auto":e.scrollHeight),p("pBind",e.ptm("listContainer"))("tabindex",-1),s(),p("ngIf",e.virtualScroll),s(),p("ngIf",!e.virtualScroll),s(3),p("ngTemplateOutlet",e.footerTemplate||e._footerTemplate),s(2),ge(" ",e.selectedMessageText," ")}}var Nn=`
${nt}

/* For PrimeNG */
p-autoComplete.ng-invalid.ng-dirty .p-autocomplete-input,
p-autoComplete.ng-invalid.ng-dirty .p-autocomplete-input-multiple,
p-auto-complete.ng-invalid.ng-dirty .p-autocomplete-input,
p-auto-complete.ng-invalid.ng-dirty .p-autocomplete-input-multiple p-autocomplete.ng-invalid.ng-dirty .p-autocomplete-input,
p-autocomplete.ng-invalid.ng-dirty .p-autocomplete-input-multiple {
    border-color: dt('autocomplete.invalid.border.color');
}

p-autoComplete.ng-invalid.ng-dirty .p-autocomplete-input:enabled:focus,
p-autoComplete.ng-invalid.ng-dirty:not(.p-disabled).p-focus .p-autocomplete-input-multiple,
p-auto-complete.ng-invalid.ng-dirty .p-autocomplete-input:enabled:focus,
p-auto-complete.ng-invalid.ng-dirty:not(.p-disabled).p-focus .p-autocomplete-input-multiple,
p-autocomplete.ng-invalid.ng-dirty .p-autocomplete-input:enabled:focus,
p-autocomplete.ng-invalid.ng-dirty:not(.p-disabled).p-focus .p-autocomplete-input-multiple {
    border-color: dt('autocomplete.focus.border.color');
}

p-autoComplete.ng-invalid.ng-dirty .p-autocomplete-input-chip input::placeholder,
p-auto-complete.ng-invalid.ng-dirty .p-autocomplete-input-chip input::placeholder,
p-autocomplete.ng-invalid.ng-dirty .p-autocomplete-input-chip input::placeholder {
    color: dt('autocomplete.invalid.placeholder.color');
}

p-autoComplete.ng-invalid.ng-dirty .p-autocomplete-input::placeholder,
p-auto-complete.ng-invalid.ng-dirty .p-autocomplete-input::placeholder,
p-autocomplete.ng-invalid.ng-dirty .p-autocomplete-input::placeholder {
    color: dt('autocomplete.invalid.placeholder.color');
}
`,qn={root:{position:"relative"}},Qn={root:({instance:i})=>["p-autocomplete p-component p-inputwrapper",{"p-invalid":i.invalid(),"p-focus":i.focused,"p-inputwrapper-filled":i.$filled(),"p-inputwrapper-focus":i.focused&&!i.$disabled()||i.autofocus||i.overlayVisible,"p-autocomplete-open":i.overlayVisible,"p-autocomplete-clearable":i.showClear&&!i.$disabled(),"p-autocomplete-fluid":i.hasFluid}],pcInputText:"p-autocomplete-input",inputMultiple:({instance:i})=>["p-autocomplete-input-multiple",{"p-disabled":i.$disabled(),"p-variant-filled":i.$variant()==="filled"}],chipItem:({instance:i,i:l})=>["p-autocomplete-chip-item",{"p-focus":i.focusedMultipleOptionIndex()===l}],pcChip:"p-autocomplete-chip",chipIcon:"p-autocomplete-chip-icon",inputChip:"p-autocomplete-input-chip",loader:"p-autocomplete-loader",dropdown:"p-autocomplete-dropdown",overlay:({instance:i})=>["p-autocomplete-overlay p-component-overlay p-component",{"p-input-filled":i.$variant()==="filled","p-ripple-disabled":i.config.ripple()===!1}],listContainer:"p-autocomplete-list-container",list:"p-autocomplete-list",optionGroup:"p-autocomplete-option-group",option:({instance:i,option:l,i:e,scrollerOptions:t})=>({"p-autocomplete-option":!0,"p-autocomplete-option-selected":i.isSelected(l),"p-focus":i.focusedOptionIndex()===i.getOptionIndex(e,t),"p-disabled":i.isOptionDisabled(l)}),emptyMessage:"p-autocomplete-empty-message",clearIcon:"p-autocomplete-clear-icon"},it=(()=>{class i extends de{name="autocomplete";style=Nn;classes=Qn;inlineStyles=qn;static \u0275fac=(()=>{let e;return function(n){return(e||(e=N(i)))(n||i)}})();static \u0275prov=K({token:i,factory:i.\u0275fac})}return i})();var ot=new G("AUTOCOMPLETE_INSTANCE"),Gn={provide:He,useExisting:be(()=>jn),multi:!0},jn=(()=>{class i extends Ge{overlayService;zone;componentName="AutoComplete";$pcAutoComplete=w(ot,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=w(E,{self:!0});minLength=1;minQueryLength;delay=300;panelStyle;styleClass;panelStyleClass;inputStyle;inputId;inputStyleClass;placeholder;readonly;scrollHeight="200px";lazy=!1;virtualScroll;virtualScrollItemSize;virtualScrollOptions;autoHighlight;forceSelection;type="text";autoZIndex=!0;baseZIndex=0;ariaLabel;dropdownAriaLabel;ariaLabelledBy;dropdownIcon;unique=!0;group;completeOnFocus=!1;showClear=!1;dropdown;showEmptyMessage=!0;dropdownMode="blank";multiple;addOnTab=!1;tabindex;dataKey;emptyMessage;showTransitionOptions=".12s cubic-bezier(0, 0, 0.2, 1)";hideTransitionOptions=".1s linear";autofocus;autocomplete="off";optionGroupChildren="items";optionGroupLabel="label";overlayOptions;get suggestions(){return this._suggestions()}set suggestions(e){this._suggestions.set(e),this.handleSuggestionsChange()}optionLabel;optionValue;id;searchMessage;emptySelectionMessage;selectionMessage;autoOptionFocus=!1;selectOnFocus;searchLocale;optionDisabled;focusOnHover=!0;typeahead=!0;addOnBlur=!1;separator;appendTo=ye(void 0);motionOptions=ye(void 0);completeMethod=new I;onSelect=new I;onUnselect=new I;onAdd=new I;onFocus=new I;onBlur=new I;onDropdownClick=new I;onClear=new I;onInputKeydown=new I;onKeyUp=new I;onShow=new I;onHide=new I;onLazyLoad=new I;inputEL;multiInputEl;multiContainerEL;dropdownButton;itemsViewChild;scroller;overlayViewChild;itemsWrapper;itemTemplate;emptyTemplate;headerTemplate;footerTemplate;selectedItemTemplate;groupTemplate;loaderTemplate;removeIconTemplate;loadingIconTemplate;clearIconTemplate;dropdownIconTemplate;onHostClick(e){this.onContainerClick(e)}value;_suggestions=j(null);timeout;overlayVisible;suggestionsUpdated;highlightOption;highlightOptionChanged;focused=!1;loading;scrollHandler;listId;searchTimeout;dirty=!1;_itemTemplate;_groupTemplate;_selectedItemTemplate;_headerTemplate;_emptyTemplate;_footerTemplate;_loaderTemplate;_removeIconTemplate;_loadingIconTemplate;_clearIconTemplate;_dropdownIconTemplate;focusedMultipleOptionIndex=j(-1);focusedOptionIndex=j(-1);_componentStyle=w(it);$appendTo=te(()=>this.appendTo()||this.config.overlayAppendTo());visibleOptions=te(()=>this.group?this.flatOptions(this._suggestions()):this._suggestions()||[]);inputValue=te(()=>{let e=this.modelValue(),t=this.optionValueSelected?(this.suggestions||[]).find(n=>H(n,e,this.equalityKey())):e;if(U(e))if(typeof e=="object"||this.optionValueSelected){let n=this.getOptionLabel(t);return n??e}else return e;else return""});get focusedMultipleOptionId(){return this.focusedMultipleOptionIndex()!==-1?`${this.id}_multiple_option_${this.focusedMultipleOptionIndex()}`:null}get focusedOptionId(){return this.focusedOptionIndex()!==-1?`${this.id}_${this.focusedOptionIndex()}`:null}get searchResultMessageText(){return U(this.visibleOptions())&&this.overlayVisible?this.searchMessageText.replaceAll("{0}",this.visibleOptions().length):this.emptySearchMessageText}get searchMessageText(){return this.searchMessage||this.config.translation.searchMessage||""}get emptySearchMessageText(){return this.emptyMessage||this.config.translation.emptySearchMessage||""}get selectionMessageText(){return this.selectionMessage||this.config.translation.selectionMessage||""}get emptySelectionMessageText(){return this.emptySelectionMessage||this.config.translation.emptySelectionMessage||""}get selectedMessageText(){return this.hasSelectedOption()?this.selectionMessageText.replaceAll("{0}",this.multiple?this.modelValue()?.length:"1"):this.emptySelectionMessageText}get ariaSetSize(){return this.visibleOptions().filter(e=>!this.isOptionGroup(e)).length}get listLabel(){return this.config.getTranslation(ce.ARIA).listLabel}get virtualScrollerDisabled(){return!this.virtualScroll}get optionValueSelected(){return typeof this.modelValue()=="string"&&this.optionValue}chipItemClass(e){return this._componentStyle.classes.chipItem({instance:this,i:e})}constructor(e,t){super(),this.overlayService=e,this.zone=t}onInit(){this.id=this.id||Be("pn_id_"),this.cd.detectChanges()}templates;onAfterContentInit(){this.templates.forEach(e=>{switch(e.getType()){case"item":this._itemTemplate=e.template;break;case"group":this._groupTemplate=e.template;break;case"selecteditem":this._selectedItemTemplate=e.template;break;case"selectedItem":this._selectedItemTemplate=e.template;break;case"header":this._headerTemplate=e.template;break;case"empty":this._emptyTemplate=e.template;break;case"footer":this._footerTemplate=e.template;break;case"loader":this._loaderTemplate=e.template;break;case"removetokenicon":this._removeIconTemplate=e.template;break;case"loadingicon":this._loadingIconTemplate=e.template;break;case"clearicon":this._clearIconTemplate=e.template;break;case"dropdownicon":this._dropdownIconTemplate=e.template;break;default:this._itemTemplate=e.template;break}})}onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptms(["host","root"])),this.suggestionsUpdated&&this.overlayViewChild&&this.zone.runOutsideAngular(()=>{setTimeout(()=>{this.overlayViewChild&&this.overlayViewChild.alignOverlay()},1),this.suggestionsUpdated=!1})}handleSuggestionsChange(){if(this.loading){this._suggestions()?.length>0||this.showEmptyMessage||this.emptyTemplate?this.show():this.hide();let e=this.overlayVisible&&this.autoOptionFocus?this.findFirstFocusedOptionIndex():-1;this.focusedOptionIndex.set(e),this.suggestionsUpdated=!0,this.loading=!1,this.cd.markForCheck()}}flatOptions(e){return(e||[]).reduce((t,n,o)=>{t.push({optionGroup:n,group:!0,index:o});let a=this.getOptionGroupChildren(n);return a&&a.forEach(g=>t.push(g)),t},[])}isOptionGroup(e){return this.optionGroupLabel&&e.optionGroup&&e.group}findFirstOptionIndex(){return this.visibleOptions().findIndex(e=>this.isValidOption(e))}findLastOptionIndex(){return xe(this.visibleOptions(),e=>this.isValidOption(e))}findFirstFocusedOptionIndex(){let e=this.findSelectedOptionIndex();return e<0?this.findFirstOptionIndex():e}findLastFocusedOptionIndex(){let e=this.findSelectedOptionIndex();return e<0?this.findLastOptionIndex():e}findSelectedOptionIndex(){return this.hasSelectedOption()?this.visibleOptions().findIndex(e=>this.isValidSelectedOption(e)):-1}findNextOptionIndex(e){let t=e<this.visibleOptions().length-1?this.visibleOptions().slice(e+1).findIndex(n=>this.isValidOption(n)):-1;return t>-1?t+e+1:e}findPrevOptionIndex(e){let t=e>0?xe(this.visibleOptions().slice(0,e),n=>this.isValidOption(n)):-1;return t>-1?t:e}isValidSelectedOption(e){return this.isValidOption(e)&&this.isSelected(e)}isValidOption(e){return e&&!(this.isOptionDisabled(e)||this.isOptionGroup(e))}isOptionDisabled(e){return this.optionDisabled?P(e,this.optionDisabled):!1}isSelected(e){return this.multiple?this.unique?this.modelValue()?.some(t=>H(t,e,this.equalityKey())):!1:H(this.modelValue(),e,this.equalityKey())}isOptionMatched(e,t){return this.isValidOption(e)&&this.getOptionLabel(e).toLocaleLowerCase(this.searchLocale)===t.toLocaleLowerCase(this.searchLocale)}isInputClicked(e){return e.target===this.inputEL?.nativeElement}isDropdownClicked(e){return this.dropdownButton?.nativeElement?e.target===this.dropdownButton.nativeElement||this.dropdownButton.nativeElement.contains(e.target):!1}equalityKey(){return this.optionValue?void 0:this.dataKey}onContainerClick(e){this.$disabled()||this.loading||this.isInputClicked(e)||this.isDropdownClicked(e)||(!this.overlayViewChild||!this.overlayViewChild.overlayViewChild?.nativeElement.contains(e.target))&&k(this.inputEL?.nativeElement)}handleDropdownClick(e){let t;this.overlayVisible?this.hide(!0):(k(this.inputEL?.nativeElement),t=this.inputEL?.nativeElement?.value,this.dropdownMode==="blank"?this.search(e,"","dropdown"):this.dropdownMode==="current"&&this.search(e,t,"dropdown")),this.onDropdownClick.emit({originalEvent:e,query:t})}onInput(e){if(this.typeahead){let t=this.minQueryLength||this.minLength;this.searchTimeout&&clearTimeout(this.searchTimeout);let n=e.target.value;this.maxlength()!==null&&(n=n.split("").slice(0,this.maxlength()).join("")),!this.multiple&&!this.forceSelection&&this.updateModel(n),n.length===0&&!this.multiple?(this.onClear.emit(),setTimeout(()=>{this.hide()},this.delay/2)):n.length>=t?(this.focusedOptionIndex.set(-1),this.searchTimeout=setTimeout(()=>{this.search(e,n,"input")},this.delay)):this.hide()}}onInputChange(e){this.updateInputWithForceSelection(e)}onInputFocus(e){if(this.$disabled())return;!this.dirty&&this.completeOnFocus&&this.search(e,e.target.value,"focus"),this.dirty=!0,this.focused=!0;let t=this.focusedOptionIndex()!==-1?this.focusedOptionIndex():this.overlayVisible&&this.autoOptionFocus?this.findFirstFocusedOptionIndex():-1;this.focusedOptionIndex.set(t),this.overlayVisible&&this.scrollInView(this.focusedOptionIndex()),this.onFocus.emit(e)}onMultipleContainerFocus(e){this.$disabled()||(this.focused=!0)}onMultipleContainerBlur(e){this.focusedMultipleOptionIndex.set(-1),this.focused=!1}onMultipleContainerKeyDown(e){if(this.$disabled()){e.preventDefault();return}switch(e.code){case"ArrowLeft":this.onArrowLeftKeyOnMultiple(e);break;case"ArrowRight":this.onArrowRightKeyOnMultiple(e);break;case"Backspace":this.onBackspaceKeyOnMultiple(e);break;default:break}}onInputBlur(e){if(this.dirty=!1,this.focused=!1,this.focusedOptionIndex.set(-1),this.addOnBlur&&this.multiple&&!this.typeahead){let t=(this.multiInputEl?.nativeElement?.value||e.target.value||"").trim();t&&!this.isSelected(t)&&(this.updateModel([...this.modelValue()||[],t]),this.onAdd.emit({originalEvent:e,value:t}),this.multiInputEl?.nativeElement?this.multiInputEl.nativeElement.value="":e.target.value="")}this.onModelTouched(),this.onBlur.emit(e)}onInputPaste(e){if(this.separator&&this.multiple&&!this.typeahead){let t=(e.clipboardData||window.clipboardData)?.getData("Text");if(t){let n=t.split(this.separator),o=[...this.modelValue()||[]];if(n.forEach(a=>{let g=a.trim();g&&!this.isSelected(g)&&o.push(g)}),o.length>(this.modelValue()||[]).length){let a=o.slice((this.modelValue()||[]).length);this.updateModel(o),a.forEach(g=>{this.onAdd.emit({originalEvent:e,value:g})}),this.multiInputEl?.nativeElement?this.multiInputEl.nativeElement.value="":e.target.value="",e.preventDefault()}}}else this.onKeyDown(e)}onInputKeyUp(e){this.onKeyUp.emit(e)}onKeyDown(e){if(this.$disabled()){e.preventDefault();return}switch(this.onInputKeydown.emit(e),e.code){case"ArrowDown":this.onArrowDownKey(e);break;case"ArrowUp":this.onArrowUpKey(e);break;case"ArrowLeft":this.onArrowLeftKey(e);break;case"ArrowRight":this.onArrowRightKey(e);break;case"Home":this.onHomeKey(e);break;case"End":this.onEndKey(e);break;case"PageDown":this.onPageDownKey(e);break;case"PageUp":this.onPageUpKey(e);break;case"Enter":case"NumpadEnter":this.onEnterKey(e);break;case"Escape":this.onEscapeKey(e);break;case"Tab":this.onTabKey(e);break;case"Backspace":this.onBackspaceKey(e);break;case"ShiftLeft":case"ShiftRight":break;default:this.handleSeparatorKey(e);break}}handleSeparatorKey(e){if(this.separator&&this.multiple&&!this.typeahead&&(this.separator===e.key||typeof this.separator=="string"&&e.key===this.separator||this.separator instanceof RegExp&&e.key.match(this.separator))){let t=(this.multiInputEl?.nativeElement?.value||e.target.value||"").trim();t&&!this.isSelected(t)&&(this.updateModel([...this.modelValue()||[],t]),this.onAdd.emit({originalEvent:e,value:t}),this.multiInputEl?.nativeElement?this.multiInputEl.nativeElement.value="":e.target.value="",e.preventDefault())}}onArrowDownKey(e){if(!this.overlayVisible)return;let t=this.focusedOptionIndex()!==-1?this.findNextOptionIndex(this.focusedOptionIndex()):this.findFirstFocusedOptionIndex();this.changeFocusedOptionIndex(e,t),e.preventDefault(),e.stopPropagation()}onArrowUpKey(e){if(this.overlayVisible)if(e.altKey)this.focusedOptionIndex()!==-1&&this.onOptionSelect(e,this.visibleOptions()[this.focusedOptionIndex()]),this.overlayVisible&&this.hide(),e.preventDefault();else{let t=this.focusedOptionIndex()!==-1?this.findPrevOptionIndex(this.focusedOptionIndex()):this.findLastFocusedOptionIndex();this.changeFocusedOptionIndex(e,t),e.preventDefault(),e.stopPropagation()}}onArrowLeftKey(e){let t=e.currentTarget;this.focusedOptionIndex.set(-1),this.multiple&&(ae(t.value)&&this.hasSelectedOption()?(k(this.multiContainerEL?.nativeElement),this.focusedMultipleOptionIndex.set(this.modelValue().length)):e.stopPropagation())}onArrowRightKey(e){this.focusedOptionIndex.set(-1),this.multiple&&e.stopPropagation()}onHomeKey(e){let{currentTarget:t}=e,n=t.value.length;t.setSelectionRange(0,e.shiftKey?n:0),this.focusedOptionIndex.set(-1),e.preventDefault()}onEndKey(e){let{currentTarget:t}=e,n=t.value.length;t.setSelectionRange(e.shiftKey?0:n,n),this.focusedOptionIndex.set(-1),e.preventDefault()}onPageDownKey(e){this.scrollInView(this.visibleOptions().length-1),e.preventDefault()}onPageUpKey(e){this.scrollInView(0),e.preventDefault()}onEnterKey(e){if(!this.typeahead&&!this.forceSelection&&this.multiple){let t=e.target.value?.trim();t&&!this.isSelected(t)&&(this.updateModel([...this.modelValue()||[],t]),this.onAdd.emit({originalEvent:e,value:t}),this.inputEL?.nativeElement&&(this.inputEL.nativeElement.value=""))}if(this.overlayVisible)this.focusedOptionIndex()!==-1&&this.onOptionSelect(e,this.visibleOptions()[this.focusedOptionIndex()]),this.hide();else return;e.preventDefault()}onEscapeKey(e){this.overlayVisible&&this.hide(!0),e.preventDefault()}onTabKey(e){if(this.focusedOptionIndex()!==-1){this.onOptionSelect(e,this.visibleOptions()[this.focusedOptionIndex()]);return}if(this.multiple&&!this.typeahead){let t=(this.multiInputEl?.nativeElement?.value||this.inputEL?.nativeElement?.value||"").trim();if(this.addOnTab&&t&&!this.isSelected(t)){this.updateModel([...this.modelValue()||[],t]),this.onAdd.emit({originalEvent:e,value:t}),this.multiInputEl?.nativeElement?this.multiInputEl.nativeElement.value="":this.inputEL?.nativeElement&&(this.inputEL.nativeElement.value=""),this.updateInputValue(),e.preventDefault(),this.overlayVisible&&this.hide();return}}this.overlayVisible&&this.hide()}onBackspaceKey(e){if(this.multiple){if(U(this.modelValue())&&!this.inputEL?.nativeElement?.value){let t=this.modelValue()[this.modelValue().length-1],n=this.modelValue().slice(0,-1);this.updateModel(n),this.onUnselect.emit({originalEvent:e,value:t})}e.stopPropagation()}}onArrowLeftKeyOnMultiple(e){let t=this.focusedMultipleOptionIndex()<1?0:this.focusedMultipleOptionIndex()-1;this.focusedMultipleOptionIndex.set(t)}onArrowRightKeyOnMultiple(e){let t=this.focusedMultipleOptionIndex();t++,this.focusedMultipleOptionIndex.set(t),t>this.modelValue().length-1&&(this.focusedMultipleOptionIndex.set(-1),k(this.inputEL?.nativeElement))}onBackspaceKeyOnMultiple(e){this.focusedMultipleOptionIndex()!==-1&&this.removeOption(e,this.focusedMultipleOptionIndex())}onOptionSelect(e,t,n=!0){this.multiple?(this.inputEL?.nativeElement&&(this.inputEL.nativeElement.value=""),this.isSelected(t)||this.updateModel([...this.modelValue()||[],t])):this.updateModel(t),this.onSelect.emit({originalEvent:e,value:t}),n&&this.hide(!0)}onOptionMouseEnter(e,t){this.focusOnHover&&this.changeFocusedOptionIndex(e,t)}search(e,t,n){t!=null&&(n==="input"&&t.trim().length===0||(this.loading=!0,this.completeMethod.emit({originalEvent:e,query:t})))}removeOption(e,t){e.stopPropagation();let n=this.modelValue()[t],o=this.modelValue().filter((a,g)=>g!==t);this.updateModel(o),this.onUnselect.emit({originalEvent:e,value:n}),k(this.inputEL?.nativeElement)}updateModel(e){let t=null;e&&(t=this.multiple?e.map(n=>this.getOptionValue(n)):this.getOptionValue(e)),this.value=t,this.writeModelValue(e),this.onModelChange(t),this.updateInputValue(),this.cd.markForCheck()}updateInputValue(){this.inputEL&&this.inputEL.nativeElement&&(this.multiple?this.inputEL.nativeElement.value="":this.inputEL.nativeElement.value=this.inputValue())}updateInputWithForceSelection(e){let t=this.inputEL?.nativeElement,n=!t?.value&&U(this.modelValue());if(!this.forceSelection||this.overlayVisible||!t?.value&&!n)return;let o=this.minQueryLength??this.minLength;if(!n&&t.value.length<o)return;let a=this.visibleOptions()?.find(g=>this.isOptionMatched(g,t.value));if(!a){t.value="",this.multiple||this.clear();return}a&&!this.isSelected(a)&&this.onOptionSelect(e,a)}autoUpdateModel(){if((this.selectOnFocus||this.autoHighlight)&&this.autoOptionFocus&&!this.hasSelectedOption()){let e=this.findFirstFocusedOptionIndex();this.focusedOptionIndex.set(e),this.onOptionSelect(null,this.visibleOptions()[this.focusedOptionIndex()],!1)}}scrollInView(e=-1){let t=e!==-1?`${this.id}_${e}`:this.focusedOptionId;if(this.itemsViewChild&&this.itemsViewChild.nativeElement){let n=re(this.itemsViewChild.nativeElement,`li[id="${t}"]`);n?n.scrollIntoView&&n.scrollIntoView({block:"nearest",inline:"nearest"}):this.virtualScrollerDisabled||setTimeout(()=>{this.virtualScroll&&this.scroller?.scrollToIndex(e!==-1?e:this.focusedOptionIndex())},0)}}changeFocusedOptionIndex(e,t){this.focusedOptionIndex()!==t&&(this.focusedOptionIndex.set(t),this.scrollInView(),this.selectOnFocus&&this.onOptionSelect(e,this.visibleOptions()[t],!1))}show(e=!1){this.dirty=!0,this.overlayVisible=!0;let t=this.focusedOptionIndex()!==-1?this.focusedOptionIndex():this.autoOptionFocus?this.findFirstFocusedOptionIndex():-1;this.focusedOptionIndex.set(t),e&&k(this.inputEL?.nativeElement),e&&k(this.inputEL?.nativeElement),this.onShow.emit(),this.cd.markForCheck()}hide(e=!1){let t=()=>{this.dirty=e,this.overlayVisible=!1,this.focusedOptionIndex.set(-1),e&&k(this.inputEL?.nativeElement),this.onHide.emit(),this.updateInputWithForceSelection(null),this.cd.markForCheck()};setTimeout(()=>{t()},0)}clear(){this.updateModel(null),this.inputEL?.nativeElement&&(this.inputEL.nativeElement.value=""),this.onClear.emit()}hasSelectedOption(){return U(this.modelValue())}getAriaPosInset(e){return(this.optionGroupLabel?e-this.visibleOptions().slice(0,e).filter(t=>this.isOptionGroup(t)).length:e)+1}getOptionLabel(e){return this.optionLabel?P(e,this.optionLabel):e&&e.label!=null?e.label:e}getOptionValue(e){return this.optionValue?P(e,this.optionValue):e&&e.value!=null?e.value:e}getOptionIndex(e,t){return this.virtualScrollerDisabled?e:t&&t.getItemOptions(e).index}getOptionGroupLabel(e){return this.optionGroupLabel?P(e,this.optionGroupLabel):e&&e.label!=null?e.label:e}getOptionGroupChildren(e){return this.optionGroupChildren?P(e,this.optionGroupChildren):e.items}getPTOptions(e,t,n,o){return this.ptm(o,{context:{option:e,index:this.getOptionIndex(n,t),selected:this.isSelected(e),focused:this.focusedOptionIndex()===this.getOptionIndex(n,t),disabled:this.isOptionDisabled(e)}})}onOverlayBeforeEnter(){if(this.itemsWrapper=re(this.overlayViewChild.overlayViewChild?.nativeElement,this.virtualScroll?'[data-pc-name="virtualscroller"]':'[data-pc-name="pcoverlay"]'),this.virtualScroll&&(this.scroller?.setContentEl(this.itemsViewChild?.nativeElement),this.scroller?.viewInit()),this.visibleOptions()&&this.visibleOptions().length)if(this.virtualScroll){let e=this.modelValue()?this.focusedOptionIndex():-1;e!==-1&&this.scroller?.scrollToIndex(e)}else{let e=re(this.itemsWrapper,'[data-pc-section="option"][data-p-selected="true"]');e&&e.scrollIntoView({block:"nearest",inline:"center"})}}get containerDataP(){return this.cn({fluid:this.hasFluid})}get overlayDataP(){return this.cn({[`overlay-${this.$appendTo()}`]:!0})}get inputMultipleDataP(){return this.cn({invalid:this.invalid(),disabled:this.$disabled(),focus:this.focused,fluid:this.hasFluid,filled:this.$variant()==="filled",empty:!this.$filled(),[this.size()]:this.size()})}writeControlValue(e,t){if(this.multiple){let n=(e||[]).map(o=>this.visibleOptions().find(g=>H(o,g,this.equalityKey()))??o);t(ae(e)?e:n)}else{let n=this.visibleOptions().find(o=>H(e,o,this.equalityKey()));t(ae(n)?e:n)}this.value=e,this.updateInputValue(),this.cd.markForCheck()}onDestroy(){this.scrollHandler&&(this.scrollHandler.destroy(),this.scrollHandler=null)}static \u0275fac=function(t){return new(t||i)(_e(Fe),_e(ve))};static \u0275cmp=W({type:i,selectors:[["p-autoComplete"],["p-autocomplete"],["p-auto-complete"]],contentQueries:function(t,n,o){if(t&1&&X(o,Ot,5)(o,St,5)(o,Et,5)(o,Vt,5)(o,kt,5)(o,Mt,5)(o,At,5)(o,Lt,5)(o,Bt,5)(o,Ft,5)(o,Rt,5)(o,pe,4),t&2){let a;x(a=b())&&(n.itemTemplate=a.first),x(a=b())&&(n.emptyTemplate=a.first),x(a=b())&&(n.headerTemplate=a.first),x(a=b())&&(n.footerTemplate=a.first),x(a=b())&&(n.selectedItemTemplate=a.first),x(a=b())&&(n.groupTemplate=a.first),x(a=b())&&(n.loaderTemplate=a.first),x(a=b())&&(n.removeIconTemplate=a.first),x(a=b())&&(n.loadingIconTemplate=a.first),x(a=b())&&(n.clearIconTemplate=a.first),x(a=b())&&(n.dropdownIconTemplate=a.first),x(a=b())&&(n.templates=a)}},viewQuery:function(t,n){if(t&1&&Te(Dt,5)(zt,5)(Kt,5)($t,5)(Ut,5)(Pt,5)(Ht,5),t&2){let o;x(o=b())&&(n.inputEL=o.first),x(o=b())&&(n.multiInputEl=o.first),x(o=b())&&(n.multiContainerEL=o.first),x(o=b())&&(n.dropdownButton=o.first),x(o=b())&&(n.itemsViewChild=o.first),x(o=b())&&(n.scroller=o.first),x(o=b())&&(n.overlayViewChild=o.first)}},hostVars:5,hostBindings:function(t,n){t&1&&v("click",function(a){return n.onHostClick(a)}),t&2&&(y("data-p",n.containerDataP),$(n.sx("root")),m(n.cn(n.cx("root"),n.styleClass)))},inputs:{minLength:[2,"minLength","minLength",D],minQueryLength:[2,"minQueryLength","minQueryLength",D],delay:[2,"delay","delay",D],panelStyle:"panelStyle",styleClass:"styleClass",panelStyleClass:"panelStyleClass",inputStyle:"inputStyle",inputId:"inputId",inputStyleClass:"inputStyleClass",placeholder:"placeholder",readonly:[2,"readonly","readonly",f],scrollHeight:"scrollHeight",lazy:[2,"lazy","lazy",f],virtualScroll:[2,"virtualScroll","virtualScroll",f],virtualScrollItemSize:[2,"virtualScrollItemSize","virtualScrollItemSize",D],virtualScrollOptions:"virtualScrollOptions",autoHighlight:[2,"autoHighlight","autoHighlight",f],forceSelection:[2,"forceSelection","forceSelection",f],type:"type",autoZIndex:[2,"autoZIndex","autoZIndex",f],baseZIndex:[2,"baseZIndex","baseZIndex",D],ariaLabel:"ariaLabel",dropdownAriaLabel:"dropdownAriaLabel",ariaLabelledBy:"ariaLabelledBy",dropdownIcon:"dropdownIcon",unique:[2,"unique","unique",f],group:[2,"group","group",f],completeOnFocus:[2,"completeOnFocus","completeOnFocus",f],showClear:[2,"showClear","showClear",f],dropdown:[2,"dropdown","dropdown",f],showEmptyMessage:[2,"showEmptyMessage","showEmptyMessage",f],dropdownMode:"dropdownMode",multiple:[2,"multiple","multiple",f],addOnTab:[2,"addOnTab","addOnTab",f],tabindex:[2,"tabindex","tabindex",D],dataKey:"dataKey",emptyMessage:"emptyMessage",showTransitionOptions:"showTransitionOptions",hideTransitionOptions:"hideTransitionOptions",autofocus:[2,"autofocus","autofocus",f],autocomplete:"autocomplete",optionGroupChildren:"optionGroupChildren",optionGroupLabel:"optionGroupLabel",overlayOptions:"overlayOptions",suggestions:"suggestions",optionLabel:"optionLabel",optionValue:"optionValue",id:"id",searchMessage:"searchMessage",emptySelectionMessage:"emptySelectionMessage",selectionMessage:"selectionMessage",autoOptionFocus:[2,"autoOptionFocus","autoOptionFocus",f],selectOnFocus:[2,"selectOnFocus","selectOnFocus",f],searchLocale:[2,"searchLocale","searchLocale",f],optionDisabled:"optionDisabled",focusOnHover:[2,"focusOnHover","focusOnHover",f],typeahead:[2,"typeahead","typeahead",f],addOnBlur:[2,"addOnBlur","addOnBlur",f],separator:"separator",appendTo:[1,"appendTo"],motionOptions:[1,"motionOptions"]},outputs:{completeMethod:"completeMethod",onSelect:"onSelect",onUnselect:"onUnselect",onAdd:"onAdd",onFocus:"onFocus",onBlur:"onBlur",onDropdownClick:"onDropdownClick",onClear:"onClear",onInputKeydown:"onInputKeydown",onKeyUp:"onKeyUp",onShow:"onShow",onHide:"onHide",onLazyLoad:"onLazyLoad"},features:[Y([Gn,it,{provide:ot,useExisting:i},{provide:ue,useExisting:i}]),Z([E]),J],decls:9,vars:14,consts:[["overlay",""],["content",""],["focusInput",""],["multiContainer",""],["focusInput","","multiIn",""],["token",""],["removeicon",""],["ddBtn",""],["buildInItems",""],["scroller",""],["loader",""],["items",""],["empty",""],["pInputText","","aria-autocomplete","list","role","combobox",3,"pAutoFocus","pt","class","ngStyle","variant","invalid","pSize","fluid","pInputTextUnstyled","input","keydown","change","focus","blur","paste","keyup",4,"ngIf"],[4,"ngIf"],["role","listbox",3,"pBind","class","tabindex","focus","blur","keydown",4,"ngIf"],["type","button","pRipple","",3,"pBind","class","disabled","click",4,"ngIf"],[3,"visibleChange","onBeforeEnter","onHide","hostAttrSelector","visible","options","target","appendTo","unstyled","pt","motionOptions"],["pInputText","","aria-autocomplete","list","role","combobox",3,"input","keydown","change","focus","blur","paste","keyup","pAutoFocus","pt","ngStyle","variant","invalid","pSize","fluid","pInputTextUnstyled"],["data-p-icon","times",3,"pBind","class","click",4,"ngIf"],[3,"pBind","class","click",4,"ngIf"],["data-p-icon","times",3,"click","pBind"],[3,"click","pBind"],[4,"ngTemplateOutlet"],["role","listbox",3,"focus","blur","keydown","pBind","tabindex"],["role","option",3,"pBind","class",4,"ngFor","ngForOf"],["role","option",3,"pBind"],["role","combobox","aria-autocomplete","list",3,"input","keydown","change","focus","blur","paste","keyup","pAutoFocus","pBind","ngStyle"],[3,"onRemove","pt","label","disabled","removable","unstyled"],[4,"ngTemplateOutlet","ngTemplateOutletContext"],[3,"pBind",4,"ngIf"],["data-p-icon","times-circle"],[3,"pBind"],["data-p-icon","spinner",3,"pBind","class","spin",4,"ngIf"],[3,"pBind","class",4,"ngIf"],["data-p-icon","spinner",3,"pBind","spin"],["type","button","pRipple","",3,"click","pBind","disabled"],[3,"ngClass",4,"ngIf"],[3,"ngClass"],["data-p-icon","chevron-down",3,"pBind",4,"ngIf"],["data-p-icon","chevron-down",3,"pBind"],[3,"pBind","ngStyle"],[3,"pBind","tabindex"],[3,"tabindex","pt","items","style","itemSize","autoSize","lazy","options","onLazyLoad",4,"ngIf"],["role","status","aria-live","polite",1,"p-hidden-accessible"],[3,"onLazyLoad","tabindex","pt","items","itemSize","autoSize","lazy","options"],["role","listbox",3,"pBind"],["ngFor","",3,"ngForOf"],["role","option",3,"pBind","class","ngStyle",4,"ngIf"],["role","option",3,"pBind","ngStyle"],["pRipple","","role","option",3,"click","mouseenter","pBind","ngStyle"],[4,"ngIf","ngIfElse"]],template:function(t,n){if(t&1){let o=C();c(0,Zt,2,32,"input",13)(1,tn,3,2,"ng-container",14)(2,cn,7,37,"ul",15)(3,_n,3,2,"ng-container",14)(4,vn,4,8,"button",16),h(5,"p-overlay",17,0),Ve("visibleChange",function(g){return d(o),Ee(n.overlayVisible,g)||(n.overlayVisible=g),u(g)}),v("onBeforeEnter",function(){return n.onOverlayBeforeEnter()})("onHide",function(){return n.hide()}),c(7,Hn,10,15,"ng-template",null,1,M),_()}t&2&&(p("ngIf",!n.multiple),s(),p("ngIf",n.$filled()&&!n.$disabled()&&n.showClear&&!n.loading),s(),p("ngIf",n.multiple),s(),p("ngIf",n.loading),s(),p("ngIf",n.dropdown),s(),p("hostAttrSelector",n.$attrSelector),Se("visible",n.overlayVisible),p("options",n.overlayOptions)("target","@parent")("appendTo",n.$appendTo())("unstyled",n.unstyled())("pt",n.ptm("pcOverlay"))("motionOptions",n.motionOptions()),y("data-p",n.overlayDataP))},dependencies:[le,ne,Ae,ie,oe,Le,je,Qe,Ne,We,qe,me,Ke,ze,tt,se,$e,De,E],encapsulation:2,changeDetection:0})}return i})();export{Ze as a,jn as b};
