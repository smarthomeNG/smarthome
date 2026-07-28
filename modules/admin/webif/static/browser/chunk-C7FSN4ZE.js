import{a as ce}from"./chunk-XF65IFLA.js";import{a as Pe,b as Ne}from"./chunk-SUEDW7CP.js";import{A as qe,b as Be,d as Fe,i as Re,t as $e}from"./chunk-XVJEVSJM.js";import{b as De,k as ze}from"./chunk-4IPD53LF.js";import{B as oe,C as E,U as ke,V as re,X as se,Y as Ae,Z as S,_ as Le,aa as Ke}from"./chunk-JGSTUQPT.js";import{J as ie,M as z,N as K,O as R,R as ge,da as Me,ga as le,ha as ae,ia as pe,n as Y,o as Ve,p as ee,q as Ee,r as te,v as ne}from"./chunk-XAETJXNU.js";import{$b as x,Fb as p,Gb as h,Gc as M,Hb as _,Ib as L,Lc as X,Mb as w,Nb as T,Ob as O,Pb as C,Pc as _e,Ta as xe,Tb as v,U as fe,V as q,Vb as l,Wa as s,Wb as be,Xb as ve,Y as H,Yb as W,Yc as g,Zb as Ie,Zc as F,_ as k,_b as y,db as ue,dc as P,ea as d,ec as Ce,fa as u,ga as A,gc as D,hc as m,ib as G,ic as B,jc as N,kc as me,la as I,ma as ye,mb as U,nb as j,ob as c,oc as we,pa as Q,pc as Te,qc as Oe,tc as Z,ua as $,uc as Se,vc as V,wb as f,wc as J,xc as he}from"./chunk-BDB7QD2D.js";var He=`
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
`;var ot=["removeicon"],lt=["*"];function at(n,r){if(n&1){let e=C();h(0,"img",4),v("error",function(i){d(e);let o=l();return u(o.imageError(i))}),_()}if(n&2){let e=l();m(e.cx("image")),p("pBind",e.ptm("image"))("src",e.image,xe)("alt",e.alt)}}function pt(n,r){if(n&1&&L(0,"span",6),n&2){let e=l(2);m(e.icon),p("pBind",e.ptm("icon"))("ngClass",e.cx("icon"))}}function rt(n,r){if(n&1&&c(0,pt,1,4,"span",5),n&2){let e=l();p("ngIf",e.icon)}}function st(n,r){if(n&1&&(h(0,"div",7),B(1),_()),n&2){let e=l();m(e.cx("label")),p("pBind",e.ptm("label")),s(),N(e.label)}}function ct(n,r){if(n&1){let e=C();h(0,"span",11),v("click",function(i){d(e);let o=l(3);return u(o.close(i))})("keydown",function(i){d(e);let o=l(3);return u(o.onKeydown(i))}),_()}if(n&2){let e=l(3);m(e.removeIcon),p("pBind",e.ptm("removeIcon"))("ngClass",e.cx("removeIcon")),f("tabindex",e.disabled?-1:0)("aria-label",e.removeAriaLabel)}}function dt(n,r){if(n&1){let e=C();A(),h(0,"svg",12),v("click",function(i){d(e);let o=l(3);return u(o.close(i))})("keydown",function(i){d(e);let o=l(3);return u(o.onKeydown(i))}),_()}if(n&2){let e=l(3);m(e.cx("removeIcon")),p("pBind",e.ptm("removeIcon")),f("tabindex",e.disabled?-1:0)("aria-label",e.removeAriaLabel)}}function ut(n,r){if(n&1&&(w(0),c(1,ct,1,6,"span",9)(2,dt,1,5,"svg",10),T()),n&2){let e=l(2);s(),p("ngIf",e.removeIcon),s(),p("ngIf",!e.removeIcon)}}function mt(n,r){}function ht(n,r){n&1&&c(0,mt,0,0,"ng-template")}function _t(n,r){if(n&1){let e=C();h(0,"span",13),v("click",function(i){d(e);let o=l(2);return u(o.close(i))})("keydown",function(i){d(e);let o=l(2);return u(o.onKeydown(i))}),c(1,ht,1,0,null,14),_()}if(n&2){let e=l(2);m(e.cx("removeIcon")),p("pBind",e.ptm("removeIcon")),f("tabindex",e.disabled?-1:0)("aria-label",e.removeAriaLabel),s(),p("ngTemplateOutlet",e.removeIconTemplate||e._removeIconTemplate)}}function gt(n,r){if(n&1&&(w(0),c(1,ut,3,2,"ng-container",3)(2,_t,2,6,"span",8),T()),n&2){let e=l();s(),p("ngIf",!e.removeIconTemplate&&!e._removeIconTemplate),s(),p("ngIf",e.removeIconTemplate||e._removeIconTemplate)}}var ft={root:({instance:n})=>({display:!n.visible&&"none"})},yt={root:({instance:n})=>["p-chip p-component",{"p-disabled":n.disabled}],image:"p-chip-image",icon:"p-chip-icon",label:"p-chip-label",removeIcon:"p-chip-remove-icon"},Qe=(()=>{class n extends re{name="chip";style=He;classes=yt;inlineStyles=ft;static \u0275fac=(()=>{let e;return function(i){return(e||(e=$(n)))(i||n)}})();static \u0275prov=q({token:n,factory:n.\u0275fac})}return n})();var Ge=new H("CHIP_INSTANCE"),Ue=(()=>{class n extends Ae{componentName="Chip";$pcChip=k(Ge,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=k(S,{self:!0});onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptms(["host","root"]))}label;icon;image;alt;styleClass;disabled=!1;removable=!1;removeIcon;onRemove=new I;onImageError=new I;visible=!0;get removeAriaLabel(){return this.config.getTranslation(pe.ARIA).removeLabel}get chipProps(){return this._chipProps}set chipProps(e){this._chipProps=e,e&&typeof e=="object"&&Object.entries(e).forEach(([t,i])=>this[`_${t}`]!==i&&(this[`_${t}`]=i))}_chipProps;_componentStyle=k(Qe);removeIconTemplate;templates;_removeIconTemplate;onAfterContentInit(){this.templates.forEach(e=>{e.getType()==="removeicon"?this._removeIconTemplate=e.template:this._removeIconTemplate=e.template})}onChanges(e){if(e.chipProps&&e.chipProps.currentValue){let{currentValue:t}=e.chipProps;t.label!==void 0&&(this.label=t.label),t.icon!==void 0&&(this.icon=t.icon),t.image!==void 0&&(this.image=t.image),t.alt!==void 0&&(this.alt=t.alt),t.styleClass!==void 0&&(this.styleClass=t.styleClass),t.removable!==void 0&&(this.removable=t.removable),t.removeIcon!==void 0&&(this.removeIcon=t.removeIcon)}}close(e){this.visible=!1,this.onRemove.emit(e)}onKeydown(e){(e.key==="Enter"||e.key==="Backspace")&&this.close(e)}imageError(e){this.onImageError.emit(e)}get dataP(){return this.cn({removable:this.removable})}static \u0275fac=(()=>{let e;return function(i){return(e||(e=$(n)))(i||n)}})();static \u0275cmp=G({type:n,selectors:[["p-chip"]],contentQueries:function(t,i,o){if(t&1&&W(o,ot,4)(o,le,4),t&2){let a;y(a=x())&&(i.removeIconTemplate=a.first),y(a=x())&&(i.templates=a)}},hostVars:6,hostBindings:function(t,i){t&2&&(f("aria-label",i.label)("data-p",i.dataP),D(i.sx("root")),m(i.cn(i.cx("root"),i.styleClass)))},inputs:{label:"label",icon:"icon",image:"image",alt:"alt",styleClass:"styleClass",disabled:[2,"disabled","disabled",g],removable:[2,"removable","removable",g],removeIcon:"removeIcon",chipProps:"chipProps"},outputs:{onRemove:"onRemove",onImageError:"onImageError"},features:[Z([Qe,{provide:Ge,useExisting:n},{provide:se,useExisting:n}]),U([S]),j],ngContentSelectors:lt,decls:6,vars:4,consts:[["iconTemplate",""],[3,"pBind","class","src","alt","error",4,"ngIf","ngIfElse"],[3,"pBind","class",4,"ngIf"],[4,"ngIf"],[3,"error","pBind","src","alt"],[3,"pBind","class","ngClass",4,"ngIf"],[3,"pBind","ngClass"],[3,"pBind"],["role","button",3,"pBind","class","click","keydown",4,"ngIf"],["role","button",3,"pBind","class","ngClass","click","keydown",4,"ngIf"],["data-p-icon","times-circle","role","button",3,"pBind","class","click","keydown",4,"ngIf"],["role","button",3,"click","keydown","pBind","ngClass"],["data-p-icon","times-circle","role","button",3,"click","keydown","pBind"],["role","button",3,"click","keydown","pBind"],[4,"ngTemplateOutlet"]],template:function(t,i){if(t&1&&(be(),ve(0),c(1,at,1,5,"img",1)(2,rt,1,1,"ng-template",null,0,M)(4,st,2,4,"div",2)(5,gt,3,2,"ng-container",3)),t&2){let o=P(3);s(),p("ngIf",i.image)("ngIfElse",o),s(3),p("ngIf",i.label),s(),p("ngIf",i.removable)}},dependencies:[ne,Y,ee,te,ce,ae,S],encapsulation:2,changeDetection:0})}return n})();var je=`
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
`;var xt=["item"],bt=["empty"],vt=["header"],It=["footer"],Ct=["selecteditem"],wt=["group"],Tt=["loader"],Ot=["removeicon"],St=["loadingicon"],Vt=["clearicon"],Et=["dropdownicon"],kt=["focusInput"],Mt=["multiIn"],At=["multiContainer"],Lt=["ddBtn"],Bt=["items"],Ft=["scroller"],Dt=["overlay"],zt=n=>({i:n}),Je=n=>({$implicit:n}),Kt=(n,r,e)=>({removeCallback:n,index:r,class:e}),de=n=>({height:n}),Xe=(n,r)=>({$implicit:n,options:r}),Rt=n=>({options:n}),$t=()=>({}),Pt=(n,r,e)=>({option:n,i:r,scrollerOptions:e}),Nt=(n,r)=>({$implicit:n,index:r});function qt(n,r){if(n&1){let e=C();h(0,"input",18,2),v("input",function(i){d(e);let o=l();return u(o.onInput(i))})("keydown",function(i){d(e);let o=l();return u(o.onKeyDown(i))})("change",function(i){d(e);let o=l();return u(o.onInputChange(i))})("focus",function(i){d(e);let o=l();return u(o.onInputFocus(i))})("blur",function(i){d(e);let o=l();return u(o.onInputBlur(i))})("paste",function(i){d(e);let o=l();return u(o.onInputPaste(i))})("keyup",function(i){d(e);let o=l();return u(o.onInputKeyUp(i))}),_()}if(n&2){let e=l();m(e.cn(e.cx("pcInputText"),e.inputStyleClass)),p("pAutoFocus",e.autofocus)("pt",e.ptm("pcInputText"))("ngStyle",e.inputStyle)("variant",e.$variant())("invalid",e.invalid())("pSize",e.size())("fluid",e.hasFluid)("pInputTextUnstyled",e.unstyled()),f("type",e.type)("value",e.inputValue())("id",e.inputId)("autocomplete",e.autocomplete)("placeholder",e.placeholder)("name",e.name())("minlength",e.minlength())("min",e.min())("max",e.max())("pattern",e.pattern())("size",e.inputSize())("maxlength",e.maxlength())("tabindex",e.$disabled()?-1:e.tabindex)("required",e.required()?"":void 0)("readonly",e.readonly?"":void 0)("disabled",e.$disabled()?"":void 0)("aria-label",e.ariaLabel)("aria-labelledby",e.ariaLabelledBy)("aria-required",e.required())("aria-expanded",e.overlayVisible??!1)("aria-controls",e.overlayVisible?e.id+"_list":null)("aria-activedescendant",e.focused?e.focusedOptionId:void 0)}}function Ht(n,r){if(n&1){let e=C();A(),h(0,"svg",21),v("click",function(){d(e);let i=l(2);return u(i.clear())}),_()}if(n&2){let e=l(2);m(e.cx("clearIcon")),p("pBind",e.ptm("clearIcon")),f("aria-hidden",!0)}}function Qt(n,r){}function Gt(n,r){n&1&&c(0,Qt,0,0,"ng-template")}function Ut(n,r){if(n&1){let e=C();h(0,"span",22),v("click",function(){d(e);let i=l(2);return u(i.clear())}),c(1,Gt,1,0,null,23),_()}if(n&2){let e=l(2);m(e.cx("clearIcon")),p("pBind",e.ptm("clearIcon")),f("aria-hidden",!0),s(),p("ngTemplateOutlet",e.clearIconTemplate||e._clearIconTemplate)}}function jt(n,r){if(n&1&&(w(0),c(1,Ht,1,4,"svg",19)(2,Ut,2,5,"span",20),T()),n&2){let e=l();s(),p("ngIf",!e.clearIconTemplate&&!e._clearIconTemplate),s(),p("ngIf",e.clearIconTemplate||e._clearIconTemplate)}}function Wt(n,r){n&1&&O(0)}function Zt(n,r){if(n&1){let e=C();h(0,"span",22),v("click",function(i){d(e);let o=l(2).index,a=l(2);return u(!a.readonly&&!a.$disabled()?a.removeOption(i,o):"")}),A(),L(1,"svg",31),_()}if(n&2){let e=l(4);m(e.cx("chipIcon")),p("pBind",e.ptm("chipIcon")),s(),m(e.cx("chipIcon")),f("aria-hidden",!0)}}function Jt(n,r){}function Xt(n,r){n&1&&c(0,Jt,0,0,"ng-template")}function Yt(n,r){if(n&1&&(h(0,"span",32),c(1,Xt,1,0,null,29),_()),n&2){let e=l(2).index,t=l(2);p("pBind",t.ptm("chipIcon")),f("aria-hidden",!0),s(),p("ngTemplateOutlet",t.removeIconTemplate||t._removeIconTemplate)("ngTemplateOutletContext",he(4,Kt,t.removeOption.bind(t),e,t.cx("chipIcon")))}}function en(n,r){if(n&1&&c(0,Zt,2,6,"span",20)(1,Yt,2,8,"span",30),n&2){let e=l(3);p("ngIf",!e.removeIconTemplate&&!e._removeIconTemplate),s(),p("ngIf",e.removeIconTemplate||e._removeIconTemplate)}}function tn(n,r){if(n&1){let e=C();h(0,"li",26,5)(2,"p-chip",28),v("onRemove",function(i){let o=d(e).index,a=l(2);return u(a.readonly?"":a.removeOption(i,o))}),c(3,Wt,1,0,"ng-container",29)(4,en,2,2,"ng-template",null,6,M),_()()}if(n&2){let e=r.$implicit,t=r.index,i=l(2);m(i.cx("chipItem",V(17,zt,t))),p("pBind",i.ptm("chipItem")),f("id",i.id+"_multiple_option_"+t)("aria-label",i.getOptionLabel(e))("aria-setsize",i.modelValue().length)("aria-posinset",t+1)("aria-selected",!0),s(2),m(i.cx("pcChip")),p("pt",i.ptm("pcChip"))("label",!i.selectedItemTemplate&&!i._selectedItemTemplate&&i.getOptionLabel(e))("disabled",i.$disabled())("removable",!0)("unstyled",i.unstyled()),s(),p("ngTemplateOutlet",i.selectedItemTemplate||i._selectedItemTemplate)("ngTemplateOutletContext",V(19,Je,e))}}function nn(n,r){if(n&1){let e=C();h(0,"ul",24,3),v("focus",function(i){d(e);let o=l();return u(o.onMultipleContainerFocus(i))})("blur",function(i){d(e);let o=l();return u(o.onMultipleContainerBlur(i))})("keydown",function(i){d(e);let o=l();return u(o.onMultipleContainerKeyDown(i))}),c(2,tn,6,21,"li",25),h(3,"li",26)(4,"input",27,4),v("input",function(i){d(e);let o=l();return u(o.onInput(i))})("keydown",function(i){d(e);let o=l();return u(o.onKeyDown(i))})("change",function(i){d(e);let o=l();return u(o.onInputChange(i))})("focus",function(i){d(e);let o=l();return u(o.onInputFocus(i))})("blur",function(i){d(e);let o=l();return u(o.onInputBlur(i))})("paste",function(i){d(e);let o=l();return u(o.onInputPaste(i))})("keyup",function(i){d(e);let o=l();return u(o.onInputKeyUp(i))}),_()()()}if(n&2){let e=l();m(e.cx("inputMultiple")),p("pBind",e.ptm("inputMultiple"))("tabindex",-1),f("data-p",e.inputMultipleDataP)("aria-orientation","horizontal")("aria-activedescendant",e.focused?e.focusedMultipleOptionId:void 0),s(2),p("ngForOf",e.modelValue()),s(),m(e.cx("inputChip")),p("pBind",e.ptm("inputChip")),s(),m(e.cx("pcInputText")),p("pAutoFocus",e.autofocus)("pBind",e.ptm("input"))("ngStyle",e.inputStyle),f("type",e.type)("id",e.inputId)("autocomplete",e.autocomplete)("name",e.name())("minlength",e.minlength())("maxlength",e.maxlength())("size",e.size())("min",e.min())("max",e.max())("pattern",e.pattern())("placeholder",e.$filled()?null:e.placeholder)("tabindex",e.$disabled()?-1:e.tabindex)("required",e.required()?"":void 0)("readonly",e.readonly?"":void 0)("disabled",e.$disabled()?"":void 0)("aria-label",e.ariaLabel)("aria-labelledby",e.ariaLabelledBy)("aria-required",e.required())("aria-expanded",e.overlayVisible??!1)("aria-controls",e.overlayVisible?e.id+"_list":null)("aria-activedescendant",e.focused?e.focusedOptionId:void 0)}}function on(n,r){if(n&1&&(A(),L(0,"svg",35)),n&2){let e=l(2);m(e.cx("loader")),p("pBind",e.ptm("loader"))("spin",!0),f("aria-hidden",!0)}}function ln(n,r){}function an(n,r){n&1&&c(0,ln,0,0,"ng-template")}function pn(n,r){if(n&1&&(h(0,"span",32),c(1,an,1,0,null,23),_()),n&2){let e=l(2);m(e.cx("loader")),p("pBind",e.ptm("loader")),f("aria-hidden",!0),s(),p("ngTemplateOutlet",e.loadingIconTemplate||e._loadingIconTemplate)}}function rn(n,r){if(n&1&&(w(0),c(1,on,1,5,"svg",33)(2,pn,2,5,"span",34),T()),n&2){let e=l();s(),p("ngIf",!e.loadingIconTemplate&&!e._loadingIconTemplate),s(),p("ngIf",e.loadingIconTemplate||e._loadingIconTemplate)}}function sn(n,r){if(n&1&&L(0,"span",38),n&2){let e=l(2);p("ngClass",e.dropdownIcon),f("aria-hidden",!0)}}function cn(n,r){if(n&1&&(A(),L(0,"svg",40)),n&2){let e=l(3);p("pBind",e.ptm("dropdown"))}}function dn(n,r){}function un(n,r){n&1&&c(0,dn,0,0,"ng-template")}function mn(n,r){if(n&1&&(w(0),c(1,cn,1,1,"svg",39)(2,un,1,0,null,23),T()),n&2){let e=l(2);s(),p("ngIf",!e.dropdownIconTemplate&&!e._dropdownIconTemplate),s(),p("ngTemplateOutlet",e.dropdownIconTemplate||e._dropdownIconTemplate)}}function hn(n,r){if(n&1){let e=C();h(0,"button",36,7),v("click",function(i){d(e);let o=l();return u(o.handleDropdownClick(i))}),c(2,sn,1,2,"span",37)(3,mn,3,2,"ng-container",14),_()}if(n&2){let e=l();m(e.cx("dropdown")),p("pBind",e.ptm("dropdown"))("disabled",e.$disabled()),f("aria-label",e.dropdownAriaLabel)("tabindex",e.tabindex),s(2),p("ngIf",e.dropdownIcon),s(),p("ngIf",!e.dropdownIcon)}}function _n(n,r){n&1&&O(0)}function gn(n,r){n&1&&O(0)}function fn(n,r){if(n&1&&c(0,gn,1,0,"ng-container",29),n&2){let e=r.$implicit,t=r.options;l(2);let i=P(6);p("ngTemplateOutlet",i)("ngTemplateOutletContext",J(2,Xe,e,t))}}function yn(n,r){n&1&&O(0)}function xn(n,r){if(n&1&&c(0,yn,1,0,"ng-container",29),n&2){let e=r.options,t=l(4);p("ngTemplateOutlet",t.loaderTemplate||t._loaderTemplate)("ngTemplateOutletContext",V(2,Rt,e))}}function bn(n,r){n&1&&(w(0),c(1,xn,1,4,"ng-template",null,10,M),T())}function vn(n,r){if(n&1){let e=C();h(0,"p-scroller",45,9),v("onLazyLoad",function(i){d(e);let o=l(2);return u(o.onLazyLoad.emit(i))}),c(2,fn,1,5,"ng-template",null,1,M)(4,bn,3,0,"ng-container",14),_()}if(n&2){let e=l(2);D(V(10,de,e.scrollHeight)),p("tabindex",-1)("pt",e.ptm("virtualScroller"))("items",e.visibleOptions())("itemSize",e.virtualScrollItemSize)("autoSize",!0)("lazy",e.lazy)("options",e.virtualScrollOptions),s(4),p("ngIf",e.loaderTemplate||e._loaderTemplate)}}function In(n,r){n&1&&O(0)}function Cn(n,r){if(n&1&&(w(0),c(1,In,1,0,"ng-container",29),T()),n&2){l();let e=P(6),t=l();s(),p("ngTemplateOutlet",e)("ngTemplateOutletContext",J(3,Xe,t.visibleOptions(),Se(2,$t)))}}function wn(n,r){if(n&1&&(h(0,"span"),B(1),_()),n&2){let e=l(2).$implicit,t=l(3);s(),N(t.getOptionGroupLabel(e.optionGroup))}}function Tn(n,r){n&1&&O(0)}function On(n,r){if(n&1&&(w(0),h(1,"li",49),c(2,wn,2,1,"span",14)(3,Tn,1,0,"ng-container",29),_(),T()),n&2){let e=l(),t=e.$implicit,i=e.index,o=l().options,a=l(2);s(),m(a.cx("optionGroup")),p("pBind",a.ptm("optionGroup"))("ngStyle",V(8,de,o.itemSize+"px")),f("id",a.id+"_"+a.getOptionIndex(i,o)),s(),p("ngIf",!a.groupTemplate),s(),p("ngTemplateOutlet",a.groupTemplate)("ngTemplateOutletContext",V(10,Je,t.optionGroup))}}function Sn(n,r){if(n&1&&(h(0,"span"),B(1),_()),n&2){let e=l(2).$implicit,t=l(3);s(),N(t.getOptionLabel(e))}}function Vn(n,r){n&1&&O(0)}function En(n,r){if(n&1){let e=C();w(0),h(1,"li",50),v("click",function(i){d(e);let o=l().$implicit,a=l(3);return u(a.onOptionSelect(i,o))})("mouseenter",function(i){d(e);let o=l().index,a=l().options,b=l(2);return u(b.onOptionMouseEnter(i,b.getOptionIndex(o,a)))}),c(2,Sn,2,1,"span",14)(3,Vn,1,0,"ng-container",29),_(),T()}if(n&2){let e=l(),t=e.$implicit,i=e.index,o=l().options,a=l(2);s(),m(a.cx("option",he(15,Pt,t,i,o))),p("pBind",a.getPTOptions(t,o,i,"option"))("ngStyle",V(19,de,o.itemSize+"px")),f("id",a.id+"_"+a.getOptionIndex(i,o))("aria-label",a.getOptionLabel(t))("aria-selected",a.isSelected(t))("data-p-selected",a.isSelected(t))("aria-disabled",a.isOptionDisabled(t))("data-p-focused",a.focusedOptionIndex()===a.getOptionIndex(i,o))("aria-setsize",a.ariaSetSize)("aria-posinset",a.getAriaPosInset(a.getOptionIndex(i,o))),s(),p("ngIf",!a.itemTemplate&&!a._itemTemplate),s(),p("ngTemplateOutlet",a.itemTemplate||a._itemTemplate)("ngTemplateOutletContext",J(21,Nt,t,o.getOptions?o.getOptions(i):i))}}function kn(n,r){if(n&1&&c(0,On,4,12,"ng-container",14)(1,En,4,24,"ng-container",14),n&2){let e=r.$implicit,t=l(3);p("ngIf",t.isOptionGroup(e)),s(),p("ngIf",!t.isOptionGroup(e))}}function Mn(n,r){if(n&1&&(w(0),B(1),T()),n&2){let e=l(4);s(),me(" ",e.searchResultMessageText," ")}}function An(n,r){n&1&&O(0,null,12)}function Ln(n,r){if(n&1&&(h(0,"li",49),c(1,Mn,2,1,"ng-container",51)(2,An,2,0,"ng-container",23),_()),n&2){let e=l().options,t=l(2);m(t.cx("emptyMessage")),p("pBind",t.ptm("emptyMessage"))("ngStyle",V(7,de,e.itemSize+"px")),s(),p("ngIf",!t.emptyTemplate&&!t._emptyTemplate)("ngIfElse",t.empty),s(),p("ngTemplateOutlet",t.emptyTemplate||t._emptyTemplate)}}function Bn(n,r){if(n&1&&(h(0,"ul",46,11),c(2,kn,2,2,"ng-template",47)(3,Ln,3,9,"li",48),_()),n&2){let e=r.$implicit,t=r.options,i=l(2);D(t.contentStyle),m(i.cn(i.cx("list"),t.contentStyleClass)),p("pBind",i.ptm("list")),f("id",i.id+"_list")("aria-label",i.listLabel),s(2),p("ngForOf",e),s(),p("ngIf",!e||e&&e.length===0&&i.showEmptyMessage)}}function Fn(n,r){n&1&&O(0)}function Dn(n,r){if(n&1&&(h(0,"div",41),c(1,_n,1,0,"ng-container",23),h(2,"div",42),c(3,vn,5,12,"p-scroller",43)(4,Cn,2,6,"ng-container",14),_(),c(5,Bn,4,9,"ng-template",null,8,M)(7,Fn,1,0,"ng-container",23),_(),h(8,"span",44),B(9),_()),n&2){let e=l();m(e.cn(e.cx("overlay"),e.panelStyleClass)),p("pBind",e.ptm("overlay"))("ngStyle",e.panelStyle),s(),p("ngTemplateOutlet",e.headerTemplate||e._headerTemplate),s(),m(e.cx("listContainer")),Ce("max-height",e.virtualScroll?"auto":e.scrollHeight),p("pBind",e.ptm("listContainer"))("tabindex",-1),s(),p("ngIf",e.virtualScroll),s(),p("ngIf",!e.virtualScroll),s(3),p("ngTemplateOutlet",e.footerTemplate||e._footerTemplate),s(2),me(" ",e.selectedMessageText," ")}}var zn=`
${je}

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
`,Kn={root:{position:"relative"}},Rn={root:({instance:n})=>["p-autocomplete p-component p-inputwrapper",{"p-invalid":n.invalid(),"p-focus":n.focused,"p-inputwrapper-filled":n.$filled(),"p-inputwrapper-focus":n.focused&&!n.$disabled()||n.autofocus||n.overlayVisible,"p-autocomplete-open":n.overlayVisible,"p-autocomplete-clearable":n.showClear&&!n.$disabled(),"p-autocomplete-fluid":n.hasFluid}],pcInputText:"p-autocomplete-input",inputMultiple:({instance:n})=>["p-autocomplete-input-multiple",{"p-disabled":n.$disabled(),"p-variant-filled":n.$variant()==="filled"}],chipItem:({instance:n,i:r})=>["p-autocomplete-chip-item",{"p-focus":n.focusedMultipleOptionIndex()===r}],pcChip:"p-autocomplete-chip",chipIcon:"p-autocomplete-chip-icon",inputChip:"p-autocomplete-input-chip",loader:"p-autocomplete-loader",dropdown:"p-autocomplete-dropdown",overlay:({instance:n})=>["p-autocomplete-overlay p-component-overlay p-component",{"p-input-filled":n.$variant()==="filled","p-ripple-disabled":n.config.ripple()===!1}],listContainer:"p-autocomplete-list-container",list:"p-autocomplete-list",optionGroup:"p-autocomplete-option-group",option:({instance:n,option:r,i:e,scrollerOptions:t})=>({"p-autocomplete-option":!0,"p-autocomplete-option-selected":n.isSelected(r),"p-focus":n.focusedOptionIndex()===n.getOptionIndex(e,t),"p-disabled":n.isOptionDisabled(r)}),emptyMessage:"p-autocomplete-empty-message",clearIcon:"p-autocomplete-clear-icon"},We=(()=>{class n extends re{name="autocomplete";style=zn;classes=Rn;inlineStyles=Kn;static \u0275fac=(()=>{let e;return function(i){return(e||(e=$(n)))(i||n)}})();static \u0275prov=q({token:n,factory:n.\u0275fac})}return n})();var Ze=new H("AUTOCOMPLETE_INSTANCE"),$n={provide:ze,useExisting:fe(()=>Pn),multi:!0},Pn=(()=>{class n extends Pe{overlayService;zone;componentName="AutoComplete";$pcAutoComplete=k(Ze,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=k(S,{self:!0});minLength=1;minQueryLength;delay=300;panelStyle;styleClass;panelStyleClass;inputStyle;inputId;inputStyleClass;placeholder;readonly;scrollHeight="200px";lazy=!1;virtualScroll;virtualScrollItemSize;virtualScrollOptions;autoHighlight;forceSelection;type="text";autoZIndex=!0;baseZIndex=0;ariaLabel;dropdownAriaLabel;ariaLabelledBy;dropdownIcon;unique=!0;group;completeOnFocus=!1;showClear=!1;dropdown;showEmptyMessage=!0;dropdownMode="blank";multiple;addOnTab=!1;tabindex;dataKey;emptyMessage;showTransitionOptions=".12s cubic-bezier(0, 0, 0.2, 1)";hideTransitionOptions=".1s linear";autofocus;autocomplete="off";optionGroupChildren="items";optionGroupLabel="label";overlayOptions;get suggestions(){return this._suggestions()}set suggestions(e){this._suggestions.set(e),this.handleSuggestionsChange()}optionLabel;optionValue;id;searchMessage;emptySelectionMessage;selectionMessage;autoOptionFocus=!1;selectOnFocus;searchLocale;optionDisabled;focusOnHover=!0;typeahead=!0;addOnBlur=!1;separator;appendTo=_e(void 0);motionOptions=_e(void 0);completeMethod=new I;onSelect=new I;onUnselect=new I;onAdd=new I;onFocus=new I;onBlur=new I;onDropdownClick=new I;onClear=new I;onInputKeydown=new I;onKeyUp=new I;onShow=new I;onHide=new I;onLazyLoad=new I;inputEL;multiInputEl;multiContainerEL;dropdownButton;itemsViewChild;scroller;overlayViewChild;itemsWrapper;itemTemplate;emptyTemplate;headerTemplate;footerTemplate;selectedItemTemplate;groupTemplate;loaderTemplate;removeIconTemplate;loadingIconTemplate;clearIconTemplate;dropdownIconTemplate;onHostClick(e){this.onContainerClick(e)}value;_suggestions=Q(null);timeout;overlayVisible;suggestionsUpdated;highlightOption;highlightOptionChanged;focused=!1;loading;scrollHandler;listId;searchTimeout;dirty=!1;_itemTemplate;_groupTemplate;_selectedItemTemplate;_headerTemplate;_emptyTemplate;_footerTemplate;_loaderTemplate;_removeIconTemplate;_loadingIconTemplate;_clearIconTemplate;_dropdownIconTemplate;focusedMultipleOptionIndex=Q(-1);focusedOptionIndex=Q(-1);_componentStyle=k(We);$appendTo=X(()=>this.appendTo()||this.config.overlayAppendTo());visibleOptions=X(()=>this.group?this.flatOptions(this._suggestions()):this._suggestions()||[]);inputValue=X(()=>{let e=this.modelValue(),t=this.optionValueSelected?(this.suggestions||[]).find(i=>R(i,e,this.equalityKey())):e;if(z(e))if(typeof e=="object"||this.optionValueSelected){let i=this.getOptionLabel(t);return i??e}else return e;else return""});get focusedMultipleOptionId(){return this.focusedMultipleOptionIndex()!==-1?`${this.id}_multiple_option_${this.focusedMultipleOptionIndex()}`:null}get focusedOptionId(){return this.focusedOptionIndex()!==-1?`${this.id}_${this.focusedOptionIndex()}`:null}get searchResultMessageText(){return z(this.visibleOptions())&&this.overlayVisible?this.searchMessageText.replaceAll("{0}",this.visibleOptions().length):this.emptySearchMessageText}get searchMessageText(){return this.searchMessage||this.config.translation.searchMessage||""}get emptySearchMessageText(){return this.emptyMessage||this.config.translation.emptySearchMessage||""}get selectionMessageText(){return this.selectionMessage||this.config.translation.selectionMessage||""}get emptySelectionMessageText(){return this.emptySelectionMessage||this.config.translation.emptySelectionMessage||""}get selectedMessageText(){return this.hasSelectedOption()?this.selectionMessageText.replaceAll("{0}",this.multiple?this.modelValue()?.length:"1"):this.emptySelectionMessageText}get ariaSetSize(){return this.visibleOptions().filter(e=>!this.isOptionGroup(e)).length}get listLabel(){return this.config.getTranslation(pe.ARIA).listLabel}get virtualScrollerDisabled(){return!this.virtualScroll}get optionValueSelected(){return typeof this.modelValue()=="string"&&this.optionValue}chipItemClass(e){return this._componentStyle.classes.chipItem({instance:this,i:e})}constructor(e,t){super(),this.overlayService=e,this.zone=t}onInit(){this.id=this.id||ke("pn_id_"),this.cd.detectChanges()}templates;onAfterContentInit(){this.templates.forEach(e=>{switch(e.getType()){case"item":this._itemTemplate=e.template;break;case"group":this._groupTemplate=e.template;break;case"selecteditem":this._selectedItemTemplate=e.template;break;case"selectedItem":this._selectedItemTemplate=e.template;break;case"header":this._headerTemplate=e.template;break;case"empty":this._emptyTemplate=e.template;break;case"footer":this._footerTemplate=e.template;break;case"loader":this._loaderTemplate=e.template;break;case"removetokenicon":this._removeIconTemplate=e.template;break;case"loadingicon":this._loadingIconTemplate=e.template;break;case"clearicon":this._clearIconTemplate=e.template;break;case"dropdownicon":this._dropdownIconTemplate=e.template;break;default:this._itemTemplate=e.template;break}})}onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptms(["host","root"])),this.suggestionsUpdated&&this.overlayViewChild&&this.zone.runOutsideAngular(()=>{setTimeout(()=>{this.overlayViewChild&&this.overlayViewChild.alignOverlay()},1),this.suggestionsUpdated=!1})}handleSuggestionsChange(){if(this.loading){this._suggestions()?.length>0||this.showEmptyMessage||this.emptyTemplate?this.show():this.hide();let e=this.overlayVisible&&this.autoOptionFocus?this.findFirstFocusedOptionIndex():-1;this.focusedOptionIndex.set(e),this.suggestionsUpdated=!0,this.loading=!1,this.cd.markForCheck()}}flatOptions(e){return(e||[]).reduce((t,i,o)=>{t.push({optionGroup:i,group:!0,index:o});let a=this.getOptionGroupChildren(i);return a&&a.forEach(b=>t.push(b)),t},[])}isOptionGroup(e){return this.optionGroupLabel&&e.optionGroup&&e.group}findFirstOptionIndex(){return this.visibleOptions().findIndex(e=>this.isValidOption(e))}findLastOptionIndex(){return ge(this.visibleOptions(),e=>this.isValidOption(e))}findFirstFocusedOptionIndex(){let e=this.findSelectedOptionIndex();return e<0?this.findFirstOptionIndex():e}findLastFocusedOptionIndex(){let e=this.findSelectedOptionIndex();return e<0?this.findLastOptionIndex():e}findSelectedOptionIndex(){return this.hasSelectedOption()?this.visibleOptions().findIndex(e=>this.isValidSelectedOption(e)):-1}findNextOptionIndex(e){let t=e<this.visibleOptions().length-1?this.visibleOptions().slice(e+1).findIndex(i=>this.isValidOption(i)):-1;return t>-1?t+e+1:e}findPrevOptionIndex(e){let t=e>0?ge(this.visibleOptions().slice(0,e),i=>this.isValidOption(i)):-1;return t>-1?t:e}isValidSelectedOption(e){return this.isValidOption(e)&&this.isSelected(e)}isValidOption(e){return e&&!(this.isOptionDisabled(e)||this.isOptionGroup(e))}isOptionDisabled(e){return this.optionDisabled?K(e,this.optionDisabled):!1}isSelected(e){return this.multiple?this.unique?this.modelValue()?.some(t=>R(t,e,this.equalityKey())):!1:R(this.modelValue(),e,this.equalityKey())}isOptionMatched(e,t){return this.isValidOption(e)&&this.getOptionLabel(e).toLocaleLowerCase(this.searchLocale)===t.toLocaleLowerCase(this.searchLocale)}isInputClicked(e){return e.target===this.inputEL?.nativeElement}isDropdownClicked(e){return this.dropdownButton?.nativeElement?e.target===this.dropdownButton.nativeElement||this.dropdownButton.nativeElement.contains(e.target):!1}equalityKey(){return this.optionValue?void 0:this.dataKey}onContainerClick(e){this.$disabled()||this.loading||this.isInputClicked(e)||this.isDropdownClicked(e)||(!this.overlayViewChild||!this.overlayViewChild.overlayViewChild?.nativeElement.contains(e.target))&&E(this.inputEL?.nativeElement)}handleDropdownClick(e){let t;this.overlayVisible?this.hide(!0):(E(this.inputEL?.nativeElement),t=this.inputEL?.nativeElement?.value,this.dropdownMode==="blank"?this.search(e,"","dropdown"):this.dropdownMode==="current"&&this.search(e,t,"dropdown")),this.onDropdownClick.emit({originalEvent:e,query:t})}onInput(e){if(this.typeahead){let t=this.minQueryLength||this.minLength;this.searchTimeout&&clearTimeout(this.searchTimeout);let i=e.target.value;this.maxlength()!==null&&(i=i.split("").slice(0,this.maxlength()).join("")),!this.multiple&&!this.forceSelection&&this.updateModel(i),i.length===0&&!this.multiple?(this.onClear.emit(),setTimeout(()=>{this.hide()},this.delay/2)):i.length>=t?(this.focusedOptionIndex.set(-1),this.searchTimeout=setTimeout(()=>{this.search(e,i,"input")},this.delay)):this.hide()}}onInputChange(e){this.updateInputWithForceSelection(e)}onInputFocus(e){if(this.$disabled())return;!this.dirty&&this.completeOnFocus&&this.search(e,e.target.value,"focus"),this.dirty=!0,this.focused=!0;let t=this.focusedOptionIndex()!==-1?this.focusedOptionIndex():this.overlayVisible&&this.autoOptionFocus?this.findFirstFocusedOptionIndex():-1;this.focusedOptionIndex.set(t),this.overlayVisible&&this.scrollInView(this.focusedOptionIndex()),this.onFocus.emit(e)}onMultipleContainerFocus(e){this.$disabled()||(this.focused=!0)}onMultipleContainerBlur(e){this.focusedMultipleOptionIndex.set(-1),this.focused=!1}onMultipleContainerKeyDown(e){if(this.$disabled()){e.preventDefault();return}switch(e.code){case"ArrowLeft":this.onArrowLeftKeyOnMultiple(e);break;case"ArrowRight":this.onArrowRightKeyOnMultiple(e);break;case"Backspace":this.onBackspaceKeyOnMultiple(e);break;default:break}}onInputBlur(e){if(this.dirty=!1,this.focused=!1,this.focusedOptionIndex.set(-1),this.addOnBlur&&this.multiple&&!this.typeahead){let t=(this.multiInputEl?.nativeElement?.value||e.target.value||"").trim();t&&!this.isSelected(t)&&(this.updateModel([...this.modelValue()||[],t]),this.onAdd.emit({originalEvent:e,value:t}),this.multiInputEl?.nativeElement?this.multiInputEl.nativeElement.value="":e.target.value="")}this.onModelTouched(),this.onBlur.emit(e)}onInputPaste(e){if(this.separator&&this.multiple&&!this.typeahead){let t=(e.clipboardData||window.clipboardData)?.getData("Text");if(t){let i=t.split(this.separator),o=[...this.modelValue()||[]];if(i.forEach(a=>{let b=a.trim();b&&!this.isSelected(b)&&o.push(b)}),o.length>(this.modelValue()||[]).length){let a=o.slice((this.modelValue()||[]).length);this.updateModel(o),a.forEach(b=>{this.onAdd.emit({originalEvent:e,value:b})}),this.multiInputEl?.nativeElement?this.multiInputEl.nativeElement.value="":e.target.value="",e.preventDefault()}}}else this.onKeyDown(e)}onInputKeyUp(e){this.onKeyUp.emit(e)}onKeyDown(e){if(this.$disabled()){e.preventDefault();return}switch(this.onInputKeydown.emit(e),e.code){case"ArrowDown":this.onArrowDownKey(e);break;case"ArrowUp":this.onArrowUpKey(e);break;case"ArrowLeft":this.onArrowLeftKey(e);break;case"ArrowRight":this.onArrowRightKey(e);break;case"Home":this.onHomeKey(e);break;case"End":this.onEndKey(e);break;case"PageDown":this.onPageDownKey(e);break;case"PageUp":this.onPageUpKey(e);break;case"Enter":case"NumpadEnter":this.onEnterKey(e);break;case"Escape":this.onEscapeKey(e);break;case"Tab":this.onTabKey(e);break;case"Backspace":this.onBackspaceKey(e);break;case"ShiftLeft":case"ShiftRight":break;default:this.handleSeparatorKey(e);break}}handleSeparatorKey(e){if(this.separator&&this.multiple&&!this.typeahead&&(this.separator===e.key||typeof this.separator=="string"&&e.key===this.separator||this.separator instanceof RegExp&&e.key.match(this.separator))){let t=(this.multiInputEl?.nativeElement?.value||e.target.value||"").trim();t&&!this.isSelected(t)&&(this.updateModel([...this.modelValue()||[],t]),this.onAdd.emit({originalEvent:e,value:t}),this.multiInputEl?.nativeElement?this.multiInputEl.nativeElement.value="":e.target.value="",e.preventDefault())}}onArrowDownKey(e){if(!this.overlayVisible)return;let t=this.focusedOptionIndex()!==-1?this.findNextOptionIndex(this.focusedOptionIndex()):this.findFirstFocusedOptionIndex();this.changeFocusedOptionIndex(e,t),e.preventDefault(),e.stopPropagation()}onArrowUpKey(e){if(this.overlayVisible)if(e.altKey)this.focusedOptionIndex()!==-1&&this.onOptionSelect(e,this.visibleOptions()[this.focusedOptionIndex()]),this.overlayVisible&&this.hide(),e.preventDefault();else{let t=this.focusedOptionIndex()!==-1?this.findPrevOptionIndex(this.focusedOptionIndex()):this.findLastFocusedOptionIndex();this.changeFocusedOptionIndex(e,t),e.preventDefault(),e.stopPropagation()}}onArrowLeftKey(e){let t=e.currentTarget;this.focusedOptionIndex.set(-1),this.multiple&&(ie(t.value)&&this.hasSelectedOption()?(E(this.multiContainerEL?.nativeElement),this.focusedMultipleOptionIndex.set(this.modelValue().length)):e.stopPropagation())}onArrowRightKey(e){this.focusedOptionIndex.set(-1),this.multiple&&e.stopPropagation()}onHomeKey(e){let{currentTarget:t}=e,i=t.value.length;t.setSelectionRange(0,e.shiftKey?i:0),this.focusedOptionIndex.set(-1),e.preventDefault()}onEndKey(e){let{currentTarget:t}=e,i=t.value.length;t.setSelectionRange(e.shiftKey?0:i,i),this.focusedOptionIndex.set(-1),e.preventDefault()}onPageDownKey(e){this.scrollInView(this.visibleOptions().length-1),e.preventDefault()}onPageUpKey(e){this.scrollInView(0),e.preventDefault()}onEnterKey(e){if(!this.typeahead&&!this.forceSelection&&this.multiple){let t=e.target.value?.trim();t&&!this.isSelected(t)&&(this.updateModel([...this.modelValue()||[],t]),this.onAdd.emit({originalEvent:e,value:t}),this.inputEL?.nativeElement&&(this.inputEL.nativeElement.value=""))}if(this.overlayVisible)this.focusedOptionIndex()!==-1&&this.onOptionSelect(e,this.visibleOptions()[this.focusedOptionIndex()]),this.hide();else return;e.preventDefault()}onEscapeKey(e){this.overlayVisible&&this.hide(!0),e.preventDefault()}onTabKey(e){if(this.focusedOptionIndex()!==-1){this.onOptionSelect(e,this.visibleOptions()[this.focusedOptionIndex()]);return}if(this.multiple&&!this.typeahead){let t=(this.multiInputEl?.nativeElement?.value||this.inputEL?.nativeElement?.value||"").trim();if(this.addOnTab&&t&&!this.isSelected(t)){this.updateModel([...this.modelValue()||[],t]),this.onAdd.emit({originalEvent:e,value:t}),this.multiInputEl?.nativeElement?this.multiInputEl.nativeElement.value="":this.inputEL?.nativeElement&&(this.inputEL.nativeElement.value=""),this.updateInputValue(),e.preventDefault(),this.overlayVisible&&this.hide();return}}this.overlayVisible&&this.hide()}onBackspaceKey(e){if(this.multiple){if(z(this.modelValue())&&!this.inputEL?.nativeElement?.value){let t=this.modelValue()[this.modelValue().length-1],i=this.modelValue().slice(0,-1);this.updateModel(i),this.onUnselect.emit({originalEvent:e,value:t})}e.stopPropagation()}}onArrowLeftKeyOnMultiple(e){let t=this.focusedMultipleOptionIndex()<1?0:this.focusedMultipleOptionIndex()-1;this.focusedMultipleOptionIndex.set(t)}onArrowRightKeyOnMultiple(e){let t=this.focusedMultipleOptionIndex();t++,this.focusedMultipleOptionIndex.set(t),t>this.modelValue().length-1&&(this.focusedMultipleOptionIndex.set(-1),E(this.inputEL?.nativeElement))}onBackspaceKeyOnMultiple(e){this.focusedMultipleOptionIndex()!==-1&&this.removeOption(e,this.focusedMultipleOptionIndex())}onOptionSelect(e,t,i=!0){this.multiple?(this.inputEL?.nativeElement&&(this.inputEL.nativeElement.value=""),this.isSelected(t)||this.updateModel([...this.modelValue()||[],t])):this.updateModel(t),this.onSelect.emit({originalEvent:e,value:t}),i&&this.hide(!0)}onOptionMouseEnter(e,t){this.focusOnHover&&this.changeFocusedOptionIndex(e,t)}search(e,t,i){t!=null&&(i==="input"&&t.trim().length===0||(this.loading=!0,this.completeMethod.emit({originalEvent:e,query:t})))}removeOption(e,t){e.stopPropagation();let i=this.modelValue()[t],o=this.modelValue().filter((a,b)=>b!==t);this.updateModel(o),this.onUnselect.emit({originalEvent:e,value:i}),E(this.inputEL?.nativeElement)}updateModel(e){let t=null;e&&(t=this.multiple?e.map(i=>this.getOptionValue(i)):this.getOptionValue(e)),this.value=t,this.writeModelValue(e),this.onModelChange(t),this.updateInputValue(),this.cd.markForCheck()}updateInputValue(){this.inputEL&&this.inputEL.nativeElement&&(this.multiple?this.inputEL.nativeElement.value="":this.inputEL.nativeElement.value=this.inputValue())}updateInputWithForceSelection(e){let t=this.inputEL?.nativeElement,i=!t?.value&&z(this.modelValue());if(!this.forceSelection||this.overlayVisible||!t?.value&&!i)return;let o=this.minQueryLength??this.minLength;if(!i&&t.value.length<o)return;let a=this.visibleOptions()?.find(b=>this.isOptionMatched(b,t.value));if(!a){t.value="",this.multiple||this.clear();return}a&&!this.isSelected(a)&&this.onOptionSelect(e,a)}autoUpdateModel(){if((this.selectOnFocus||this.autoHighlight)&&this.autoOptionFocus&&!this.hasSelectedOption()){let e=this.findFirstFocusedOptionIndex();this.focusedOptionIndex.set(e),this.onOptionSelect(null,this.visibleOptions()[this.focusedOptionIndex()],!1)}}scrollInView(e=-1){let t=e!==-1?`${this.id}_${e}`:this.focusedOptionId;if(this.itemsViewChild&&this.itemsViewChild.nativeElement){let i=oe(this.itemsViewChild.nativeElement,`li[id="${t}"]`);i?i.scrollIntoView&&i.scrollIntoView({block:"nearest",inline:"nearest"}):this.virtualScrollerDisabled||setTimeout(()=>{this.virtualScroll&&this.scroller?.scrollToIndex(e!==-1?e:this.focusedOptionIndex())},0)}}changeFocusedOptionIndex(e,t){this.focusedOptionIndex()!==t&&(this.focusedOptionIndex.set(t),this.scrollInView(),this.selectOnFocus&&this.onOptionSelect(e,this.visibleOptions()[t],!1))}show(e=!1){this.dirty=!0,this.overlayVisible=!0;let t=this.focusedOptionIndex()!==-1?this.focusedOptionIndex():this.autoOptionFocus?this.findFirstFocusedOptionIndex():-1;this.focusedOptionIndex.set(t),e&&E(this.inputEL?.nativeElement),e&&E(this.inputEL?.nativeElement),this.onShow.emit(),this.cd.markForCheck()}hide(e=!1){let t=()=>{this.dirty=e,this.overlayVisible=!1,this.focusedOptionIndex.set(-1),e&&E(this.inputEL?.nativeElement),this.onHide.emit(),this.updateInputWithForceSelection(null),this.cd.markForCheck()};setTimeout(()=>{t()},0)}clear(){this.updateModel(null),this.inputEL?.nativeElement&&(this.inputEL.nativeElement.value=""),this.onClear.emit()}hasSelectedOption(){return z(this.modelValue())}getAriaPosInset(e){return(this.optionGroupLabel?e-this.visibleOptions().slice(0,e).filter(t=>this.isOptionGroup(t)).length:e)+1}getOptionLabel(e){return this.optionLabel?K(e,this.optionLabel):e&&e.label!=null?e.label:e}getOptionValue(e){return this.optionValue?K(e,this.optionValue):e&&e.value!=null?e.value:e}getOptionIndex(e,t){return this.virtualScrollerDisabled?e:t&&t.getItemOptions(e).index}getOptionGroupLabel(e){return this.optionGroupLabel?K(e,this.optionGroupLabel):e&&e.label!=null?e.label:e}getOptionGroupChildren(e){return this.optionGroupChildren?K(e,this.optionGroupChildren):e.items}getPTOptions(e,t,i,o){return this.ptm(o,{context:{option:e,index:this.getOptionIndex(i,t),selected:this.isSelected(e),focused:this.focusedOptionIndex()===this.getOptionIndex(i,t),disabled:this.isOptionDisabled(e)}})}onOverlayBeforeEnter(){if(this.itemsWrapper=oe(this.overlayViewChild.overlayViewChild?.nativeElement,this.virtualScroll?'[data-pc-name="virtualscroller"]':'[data-pc-name="pcoverlay"]'),this.virtualScroll&&(this.scroller?.setContentEl(this.itemsViewChild?.nativeElement),this.scroller?.viewInit()),this.visibleOptions()&&this.visibleOptions().length)if(this.virtualScroll){let e=this.modelValue()?this.focusedOptionIndex():-1;e!==-1&&this.scroller?.scrollToIndex(e)}else{let e=oe(this.itemsWrapper,'[data-pc-section="option"][data-p-selected="true"]');e&&e.scrollIntoView({block:"nearest",inline:"center"})}}get containerDataP(){return this.cn({fluid:this.hasFluid})}get overlayDataP(){return this.cn({[`overlay-${this.$appendTo()}`]:!0})}get inputMultipleDataP(){return this.cn({invalid:this.invalid(),disabled:this.$disabled(),focus:this.focused,fluid:this.hasFluid,filled:this.$variant()==="filled",empty:!this.$filled(),[this.size()]:this.size()})}writeControlValue(e,t){if(this.multiple){let i=(e||[]).map(o=>this.visibleOptions().find(b=>R(o,b,this.equalityKey()))??o);t(ie(e)?e:i)}else{let i=this.visibleOptions().find(o=>R(e,o,this.equalityKey()));t(ie(i)?e:i)}this.value=e,this.updateInputValue(),this.cd.markForCheck()}onDestroy(){this.scrollHandler&&(this.scrollHandler.destroy(),this.scrollHandler=null)}static \u0275fac=function(t){return new(t||n)(ue(Me),ue(ye))};static \u0275cmp=G({type:n,selectors:[["p-autoComplete"],["p-autocomplete"],["p-auto-complete"]],contentQueries:function(t,i,o){if(t&1&&W(o,xt,5)(o,bt,5)(o,vt,5)(o,It,5)(o,Ct,5)(o,wt,5)(o,Tt,5)(o,Ot,5)(o,St,5)(o,Vt,5)(o,Et,5)(o,le,4),t&2){let a;y(a=x())&&(i.itemTemplate=a.first),y(a=x())&&(i.emptyTemplate=a.first),y(a=x())&&(i.headerTemplate=a.first),y(a=x())&&(i.footerTemplate=a.first),y(a=x())&&(i.selectedItemTemplate=a.first),y(a=x())&&(i.groupTemplate=a.first),y(a=x())&&(i.loaderTemplate=a.first),y(a=x())&&(i.removeIconTemplate=a.first),y(a=x())&&(i.loadingIconTemplate=a.first),y(a=x())&&(i.clearIconTemplate=a.first),y(a=x())&&(i.dropdownIconTemplate=a.first),y(a=x())&&(i.templates=a)}},viewQuery:function(t,i){if(t&1&&Ie(kt,5)(Mt,5)(At,5)(Lt,5)(Bt,5)(Ft,5)(Dt,5),t&2){let o;y(o=x())&&(i.inputEL=o.first),y(o=x())&&(i.multiInputEl=o.first),y(o=x())&&(i.multiContainerEL=o.first),y(o=x())&&(i.dropdownButton=o.first),y(o=x())&&(i.itemsViewChild=o.first),y(o=x())&&(i.scroller=o.first),y(o=x())&&(i.overlayViewChild=o.first)}},hostVars:5,hostBindings:function(t,i){t&1&&v("click",function(a){return i.onHostClick(a)}),t&2&&(f("data-p",i.containerDataP),D(i.sx("root")),m(i.cn(i.cx("root"),i.styleClass)))},inputs:{minLength:[2,"minLength","minLength",F],minQueryLength:[2,"minQueryLength","minQueryLength",F],delay:[2,"delay","delay",F],panelStyle:"panelStyle",styleClass:"styleClass",panelStyleClass:"panelStyleClass",inputStyle:"inputStyle",inputId:"inputId",inputStyleClass:"inputStyleClass",placeholder:"placeholder",readonly:[2,"readonly","readonly",g],scrollHeight:"scrollHeight",lazy:[2,"lazy","lazy",g],virtualScroll:[2,"virtualScroll","virtualScroll",g],virtualScrollItemSize:[2,"virtualScrollItemSize","virtualScrollItemSize",F],virtualScrollOptions:"virtualScrollOptions",autoHighlight:[2,"autoHighlight","autoHighlight",g],forceSelection:[2,"forceSelection","forceSelection",g],type:"type",autoZIndex:[2,"autoZIndex","autoZIndex",g],baseZIndex:[2,"baseZIndex","baseZIndex",F],ariaLabel:"ariaLabel",dropdownAriaLabel:"dropdownAriaLabel",ariaLabelledBy:"ariaLabelledBy",dropdownIcon:"dropdownIcon",unique:[2,"unique","unique",g],group:[2,"group","group",g],completeOnFocus:[2,"completeOnFocus","completeOnFocus",g],showClear:[2,"showClear","showClear",g],dropdown:[2,"dropdown","dropdown",g],showEmptyMessage:[2,"showEmptyMessage","showEmptyMessage",g],dropdownMode:"dropdownMode",multiple:[2,"multiple","multiple",g],addOnTab:[2,"addOnTab","addOnTab",g],tabindex:[2,"tabindex","tabindex",F],dataKey:"dataKey",emptyMessage:"emptyMessage",showTransitionOptions:"showTransitionOptions",hideTransitionOptions:"hideTransitionOptions",autofocus:[2,"autofocus","autofocus",g],autocomplete:"autocomplete",optionGroupChildren:"optionGroupChildren",optionGroupLabel:"optionGroupLabel",overlayOptions:"overlayOptions",suggestions:"suggestions",optionLabel:"optionLabel",optionValue:"optionValue",id:"id",searchMessage:"searchMessage",emptySelectionMessage:"emptySelectionMessage",selectionMessage:"selectionMessage",autoOptionFocus:[2,"autoOptionFocus","autoOptionFocus",g],selectOnFocus:[2,"selectOnFocus","selectOnFocus",g],searchLocale:[2,"searchLocale","searchLocale",g],optionDisabled:"optionDisabled",focusOnHover:[2,"focusOnHover","focusOnHover",g],typeahead:[2,"typeahead","typeahead",g],addOnBlur:[2,"addOnBlur","addOnBlur",g],separator:"separator",appendTo:[1,"appendTo"],motionOptions:[1,"motionOptions"]},outputs:{completeMethod:"completeMethod",onSelect:"onSelect",onUnselect:"onUnselect",onAdd:"onAdd",onFocus:"onFocus",onBlur:"onBlur",onDropdownClick:"onDropdownClick",onClear:"onClear",onInputKeydown:"onInputKeydown",onKeyUp:"onKeyUp",onShow:"onShow",onHide:"onHide",onLazyLoad:"onLazyLoad"},features:[Z([$n,We,{provide:Ze,useExisting:n},{provide:se,useExisting:n}]),U([S]),j],decls:9,vars:14,consts:[["overlay",""],["content",""],["focusInput",""],["multiContainer",""],["focusInput","","multiIn",""],["token",""],["removeicon",""],["ddBtn",""],["buildInItems",""],["scroller",""],["loader",""],["items",""],["empty",""],["pInputText","","aria-autocomplete","list","role","combobox",3,"pAutoFocus","pt","class","ngStyle","variant","invalid","pSize","fluid","pInputTextUnstyled","input","keydown","change","focus","blur","paste","keyup",4,"ngIf"],[4,"ngIf"],["role","listbox",3,"pBind","class","tabindex","focus","blur","keydown",4,"ngIf"],["type","button","pRipple","",3,"pBind","class","disabled","click",4,"ngIf"],[3,"visibleChange","onBeforeEnter","onHide","hostAttrSelector","visible","options","target","appendTo","unstyled","pt","motionOptions"],["pInputText","","aria-autocomplete","list","role","combobox",3,"input","keydown","change","focus","blur","paste","keyup","pAutoFocus","pt","ngStyle","variant","invalid","pSize","fluid","pInputTextUnstyled"],["data-p-icon","times",3,"pBind","class","click",4,"ngIf"],[3,"pBind","class","click",4,"ngIf"],["data-p-icon","times",3,"click","pBind"],[3,"click","pBind"],[4,"ngTemplateOutlet"],["role","listbox",3,"focus","blur","keydown","pBind","tabindex"],["role","option",3,"pBind","class",4,"ngFor","ngForOf"],["role","option",3,"pBind"],["role","combobox","aria-autocomplete","list",3,"input","keydown","change","focus","blur","paste","keyup","pAutoFocus","pBind","ngStyle"],[3,"onRemove","pt","label","disabled","removable","unstyled"],[4,"ngTemplateOutlet","ngTemplateOutletContext"],[3,"pBind",4,"ngIf"],["data-p-icon","times-circle"],[3,"pBind"],["data-p-icon","spinner",3,"pBind","class","spin",4,"ngIf"],[3,"pBind","class",4,"ngIf"],["data-p-icon","spinner",3,"pBind","spin"],["type","button","pRipple","",3,"click","pBind","disabled"],[3,"ngClass",4,"ngIf"],[3,"ngClass"],["data-p-icon","chevron-down",3,"pBind",4,"ngIf"],["data-p-icon","chevron-down",3,"pBind"],[3,"pBind","ngStyle"],[3,"pBind","tabindex"],[3,"tabindex","pt","items","style","itemSize","autoSize","lazy","options","onLazyLoad",4,"ngIf"],["role","status","aria-live","polite",1,"p-hidden-accessible"],[3,"onLazyLoad","tabindex","pt","items","itemSize","autoSize","lazy","options"],["role","listbox",3,"pBind"],["ngFor","",3,"ngForOf"],["role","option",3,"pBind","class","ngStyle",4,"ngIf"],["role","option",3,"pBind","ngStyle"],["pRipple","","role","option",3,"click","mouseenter","pBind","ngStyle"],[4,"ngIf","ngIfElse"]],template:function(t,i){if(t&1){let o=C();c(0,qt,2,32,"input",13)(1,jt,3,2,"ng-container",14)(2,nn,7,37,"ul",15)(3,rn,3,2,"ng-container",14)(4,hn,4,8,"button",16),h(5,"p-overlay",17,0),Oe("visibleChange",function(b){return d(o),Te(i.overlayVisible,b)||(i.overlayVisible=b),u(b)}),v("onBeforeEnter",function(){return i.onOverlayBeforeEnter()})("onHide",function(){return i.hide()}),c(7,Dn,10,15,"ng-template",null,1,M),_()}t&2&&(p("ngIf",!i.multiple),s(),p("ngIf",i.$filled()&&!i.$disabled()&&i.showClear&&!i.loading),s(),p("ngIf",i.multiple),s(),p("ngIf",i.loading),s(),p("ngIf",i.dropdown),s(),p("hostAttrSelector",i.$attrSelector),we("visible",i.overlayVisible),p("options",i.overlayOptions)("target","@parent")("appendTo",i.$appendTo())("unstyled",i.unstyled())("pt",i.ptm("pcOverlay"))("motionOptions",i.motionOptions()),f("data-p",i.overlayDataP))},dependencies:[ne,Y,Ve,ee,te,Ee,Ne,$e,Ke,qe,Re,ce,Fe,Be,Ue,ae,De,Le,S],encapsulation:2,changeDetection:0})}return n})();export{Pn as a};
