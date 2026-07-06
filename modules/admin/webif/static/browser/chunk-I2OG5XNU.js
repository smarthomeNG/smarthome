import{a as _e}from"./chunk-PSTFOCVG.js";import{a as je,b as Ze}from"./chunk-BLMNQ5ZN.js";import{b as ze,d as Qe,i as Ue,s as Ge,z as We}from"./chunk-XJPGZAJH.js";import{b as $e,g as Pe}from"./chunk-FQUEGOUU.js";import{E as ve,Fa as De,H as j,I as N,Ia as ce,J as P,Ja as ue,Ka as de,M as be,Ma as me,Pa as he,Qa as Re,Ra as k,Sa as Ke,Va as He,Xa as Ne,Ya as qe,c as Ae,ha as se,ia as A,k as le,l as Le,m as ae,n as Be,o as re,s as pe,ya as Fe}from"./chunk-PN5D6VAD.js";import{$b as y,Fb as p,Fc as B,Gb as h,Hb as _,I as D,Ib as K,Jc as oe,Mb as S,Nb as V,Nc as Me,Ob as E,Pb as C,Sa as Ce,Tb as b,Ua as s,Uc as g,Vb as a,Vc as Q,Wb as Te,Xb as Oe,Y as Ie,Yb as w,Z as H,Za as I,Zb as L,_a as we,_b as f,aa as Z,ca as O,cc as U,db as fe,dc as ee,fc as te,gc as m,hc as z,ia as c,ib as J,ic as G,ja as u,jc as ye,ka as R,mb as X,nb as Y,nc as Se,ob as d,oc as Ve,pc as Ee,q as F,qa as W,sc as ne,tc as ke,uc as M,va as q,vc as ie,w as T,wb as x,wc as xe}from"./chunk-HJNL6B4D.js";var Je=`
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
        font-size: dt('chip.icon.font.size');
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
`;var dt=["removeicon"],mt=["*"];function ht(i,l){if(i&1){let e=C();h(0,"img",4),b("error",function(n){c(e);let o=a();return u(o.imageError(n))}),_()}if(i&2){let e=a();m(e.cx("image")),p("pBind",e.ptm("image"))("src",e.image,Ce)("alt",e.alt)}}function _t(i,l){if(i&1&&K(0,"span",6),i&2){let e=a(2);m(e.icon),p("pBind",e.ptm("icon"))("ngClass",e.cx("icon"))}}function gt(i,l){if(i&1&&d(0,_t,1,4,"span",5),i&2){let e=a();p("ngIf",e.icon)}}function ft(i,l){if(i&1&&(h(0,"div",7),z(1),_()),i&2){let e=a();m(e.cx("label")),p("pBind",e.ptm("label")),s(),G(e.label)}}function yt(i,l){if(i&1){let e=C();h(0,"span",11),b("click",function(n){c(e);let o=a(3);return u(o.close(n))})("keydown",function(n){c(e);let o=a(3);return u(o.onKeydown(n))}),_()}if(i&2){let e=a(3);m(e.removeIcon),p("pBind",e.ptm("removeIcon"))("ngClass",e.cx("removeIcon")),x("tabindex",e.disabled?-1:0)("aria-label",e.removeAriaLabel)}}function xt(i,l){if(i&1){let e=C();R(),h(0,"svg",12),b("click",function(n){c(e);let o=a(3);return u(o.close(n))})("keydown",function(n){c(e);let o=a(3);return u(o.onKeydown(n))}),_()}if(i&2){let e=a(3);m(e.cx("removeIcon")),p("pBind",e.ptm("removeIcon")),x("tabindex",e.disabled?-1:0)("aria-label",e.removeAriaLabel)}}function vt(i,l){if(i&1&&(S(0),d(1,yt,1,6,"span",9)(2,xt,1,5,"svg",10),V()),i&2){let e=a(2);s(),p("ngIf",e.removeIcon),s(),p("ngIf",!e.removeIcon)}}function bt(i,l){}function It(i,l){i&1&&d(0,bt,0,0,"ng-template")}function Ct(i,l){if(i&1){let e=C();h(0,"span",13),b("click",function(n){c(e);let o=a(2);return u(o.close(n))})("keydown",function(n){c(e);let o=a(2);return u(o.onKeydown(n))}),d(1,It,1,0,null,14),_()}if(i&2){let e=a(2);m(e.cx("removeIcon")),p("pBind",e.ptm("removeIcon")),x("tabindex",e.disabled?-1:0)("aria-label",e.removeAriaLabel),s(),p("ngTemplateOutlet",e.removeIconTemplate||e._removeIconTemplate)}}function wt(i,l){if(i&1&&(S(0),d(1,vt,3,2,"ng-container",3)(2,Ct,2,6,"span",8),V()),i&2){let e=a();s(),p("ngIf",!e.removeIconTemplate&&!e._removeIconTemplate),s(),p("ngIf",e.removeIconTemplate||e._removeIconTemplate)}}var Tt={root:({instance:i})=>["p-chip p-component",{"p-disabled":i.disabled}],image:"p-chip-image",icon:"p-chip-icon",label:"p-chip-label",removeIcon:"p-chip-remove-icon"},Xe=(()=>{class i extends me{name="chip";style=Je;classes=Tt;static \u0275fac=(()=>{let e;return function(n){return(e||(e=q(i)))(n||i)}})();static \u0275prov=H({token:i,factory:i.\u0275fac})}return i})();var Ye=new Z("CHIP_INSTANCE"),tt=(()=>{class i extends Re{$pcChip=O(Ye,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=O(k,{self:!0});onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptms(["host","root"]))}label;icon;image;alt;styleClass;disabled=!1;removable=!1;removeIcon;onRemove=new I;onImageError=new I;visible=!0;get removeAriaLabel(){return this.config.getTranslation(de.ARIA).removeLabel}get chipProps(){return this._chipProps}set chipProps(e){this._chipProps=e,e&&typeof e=="object"&&Object.entries(e).forEach(([t,n])=>this[`_${t}`]!==n&&(this[`_${t}`]=n))}_chipProps;_componentStyle=O(Xe);removeIconTemplate;templates;_removeIconTemplate;onAfterContentInit(){this.templates.forEach(e=>{e.getType()==="removeicon"?this._removeIconTemplate=e.template:this._removeIconTemplate=e.template})}onChanges(e){if(e.chipProps&&e.chipProps.currentValue){let{currentValue:t}=e.chipProps;t.label!==void 0&&(this.label=t.label),t.icon!==void 0&&(this.icon=t.icon),t.image!==void 0&&(this.image=t.image),t.alt!==void 0&&(this.alt=t.alt),t.styleClass!==void 0&&(this.styleClass=t.styleClass),t.removable!==void 0&&(this.removable=t.removable),t.removeIcon!==void 0&&(this.removeIcon=t.removeIcon)}}close(e){this.visible=!1,this.onRemove.emit(e)}onKeydown(e){(e.key==="Enter"||e.key==="Backspace")&&this.close(e)}imageError(e){this.onImageError.emit(e)}static \u0275fac=(()=>{let e;return function(n){return(e||(e=q(i)))(n||i)}})();static \u0275cmp=J({type:i,selectors:[["p-chip"]],contentQueries:function(t,n,o){if(t&1&&(w(o,dt,4),w(o,ce,4)),t&2){let r;f(r=y())&&(n.removeIconTemplate=r.first),f(r=y())&&(n.templates=r)}},hostVars:5,hostBindings:function(t,n){t&2&&(x("aria-label",n.label),m(n.cn(n.cx("root"),n.styleClass)),ee("display",!n.visible&&"none"))},inputs:{label:"label",icon:"icon",image:"image",alt:"alt",styleClass:"styleClass",disabled:[2,"disabled","disabled",g],removable:[2,"removable","removable",g],removeIcon:"removeIcon",chipProps:"chipProps"},outputs:{onRemove:"onRemove",onImageError:"onImageError"},features:[ne([Xe,{provide:Ye,useExisting:i},{provide:he,useExisting:i}]),Y([k]),X],ngContentSelectors:mt,decls:6,vars:4,consts:[["iconTemplate",""],[3,"pBind","class","src","alt","error",4,"ngIf","ngIfElse"],[3,"pBind","class",4,"ngIf"],[4,"ngIf"],[3,"error","pBind","src","alt"],[3,"pBind","class","ngClass",4,"ngIf"],[3,"pBind","ngClass"],[3,"pBind"],["role","button",3,"pBind","class","click","keydown",4,"ngIf"],["role","button",3,"pBind","class","ngClass","click","keydown",4,"ngIf"],["data-p-icon","times-circle","role","button",3,"pBind","class","click","keydown",4,"ngIf"],["role","button",3,"click","keydown","pBind","ngClass"],["data-p-icon","times-circle","role","button",3,"click","keydown","pBind"],["role","button",3,"click","keydown","pBind"],[4,"ngTemplateOutlet"]],template:function(t,n){if(t&1&&(Te(),Oe(0),d(1,ht,1,5,"img",1)(2,gt,1,1,"ng-template",null,0,B)(4,ft,2,4,"div",2)(5,wt,3,2,"ng-container",3)),t&2){let o=U(3);s(),p("ngIf",n.image)("ngIfElse",o),s(3),p("ngIf",n.label),s(),p("ngIf",n.removable)}},dependencies:[pe,le,ae,re,_e,ue,k],encapsulation:2,changeDetection:0})}return i})();var nt=`
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
        background: dt('inputtext.disabled.background');
        color: dt('inputtext.disabled.color');
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
`;var Ot=["item"],St=["empty"],Vt=["header"],Et=["footer"],kt=["selecteditem"],Mt=["group"],At=["loader"],Lt=["removeicon"],Bt=["loadingicon"],Ft=["clearicon"],Dt=["dropdownicon"],Rt=["focusInput"],Kt=["multiIn"],zt=["multiContainer"],Qt=["ddBtn"],$t=["items"],Ht=["scroller"],Nt=["overlay"],Pt=i=>({i}),lt=i=>({$implicit:i}),qt=(i,l,e)=>({removeCallback:i,index:l,class:e}),ge=i=>({height:i}),at=(i,l)=>({$implicit:i,options:l}),Ut=i=>({options:i}),Gt=()=>({}),jt=(i,l,e)=>({option:i,i:l,scrollerOptions:e}),Zt=(i,l)=>({$implicit:i,index:l});function Wt(i,l){if(i&1){let e=C();h(0,"input",18,2),b("input",function(n){c(e);let o=a();return u(o.onInput(n))})("keydown",function(n){c(e);let o=a();return u(o.onKeyDown(n))})("change",function(n){c(e);let o=a();return u(o.onInputChange(n))})("focus",function(n){c(e);let o=a();return u(o.onInputFocus(n))})("blur",function(n){c(e);let o=a();return u(o.onInputBlur(n))})("paste",function(n){c(e);let o=a();return u(o.onInputPaste(n))})("keyup",function(n){c(e);let o=a();return u(o.onInputKeyUp(n))}),_()}if(i&2){let e=a();m(e.cn(e.cx("pcInputText"),e.inputStyleClass)),p("pAutoFocus",e.autofocus)("pt",e.ptm("pcInputText"))("ngStyle",e.inputStyle)("variant",e.$variant())("invalid",e.invalid())("pSize",e.size())("fluid",e.hasFluid),x("type",e.type)("value",e.inputValue())("id",e.inputId)("autocomplete",e.autocomplete)("placeholder",e.placeholder)("name",e.name())("minlength",e.minlength())("min",e.min())("max",e.max())("pattern",e.pattern())("size",e.inputSize())("maxlength",e.maxlength())("tabindex",e.$disabled()?-1:e.tabindex)("required",e.required()?"":void 0)("readonly",e.readonly?"":void 0)("disabled",e.$disabled()?"":void 0)("aria-label",e.ariaLabel)("aria-labelledby",e.ariaLabelledBy)("aria-required",e.required())("aria-expanded",e.overlayVisible??!1)("aria-controls",e.overlayVisible?e.id+"_list":null)("aria-activedescendant",e.focused?e.focusedOptionId:void 0)}}function Jt(i,l){if(i&1){let e=C();R(),h(0,"svg",21),b("click",function(){c(e);let n=a(2);return u(n.clear())}),_()}if(i&2){let e=a(2);m(e.cx("clearIcon")),p("pBind",e.ptm("clearIcon")),x("aria-hidden",!0)}}function Xt(i,l){}function Yt(i,l){i&1&&d(0,Xt,0,0,"ng-template")}function en(i,l){if(i&1){let e=C();h(0,"span",22),b("click",function(){c(e);let n=a(2);return u(n.clear())}),d(1,Yt,1,0,null,23),_()}if(i&2){let e=a(2);m(e.cx("clearIcon")),p("pBind",e.ptm("clearIcon")),x("aria-hidden",!0),s(),p("ngTemplateOutlet",e.clearIconTemplate||e._clearIconTemplate)}}function tn(i,l){if(i&1&&(S(0),d(1,Jt,1,4,"svg",19)(2,en,2,5,"span",20),V()),i&2){let e=a();s(),p("ngIf",!e.clearIconTemplate&&!e._clearIconTemplate),s(),p("ngIf",e.clearIconTemplate||e._clearIconTemplate)}}function nn(i,l){i&1&&E(0)}function on(i,l){if(i&1){let e=C();h(0,"span",22),b("click",function(n){c(e);let o=a(2).index,r=a(2);return u(!r.readonly&&!r.$disabled()?r.removeOption(n,o):"")}),R(),K(1,"svg",31),_()}if(i&2){let e=a(4);m(e.cx("chipIcon")),p("pBind",e.ptm("chipIcon")),s(),m(e.cx("chipIcon")),x("aria-hidden",!0)}}function ln(i,l){}function an(i,l){i&1&&d(0,ln,0,0,"ng-template")}function rn(i,l){if(i&1&&(h(0,"span",32),d(1,an,1,0,null,29),_()),i&2){let e=a(2).index,t=a(2);p("pBind",t.ptm("chipIcon")),x("aria-hidden",!0),s(),p("ngTemplateOutlet",t.removeIconTemplate||t._removeIconTemplate)("ngTemplateOutletContext",xe(4,qt,t.removeOption.bind(t),e,t.cx("chipIcon")))}}function pn(i,l){if(i&1&&d(0,on,2,6,"span",20)(1,rn,2,8,"span",30),i&2){let e=a(3);p("ngIf",!e.removeIconTemplate&&!e._removeIconTemplate),s(),p("ngIf",e.removeIconTemplate||e._removeIconTemplate)}}function sn(i,l){if(i&1){let e=C();h(0,"li",26,5)(2,"p-chip",28),b("onRemove",function(n){let o=c(e).index,r=a(2);return u(r.readonly?"":r.removeOption(n,o))}),d(3,nn,1,0,"ng-container",29)(4,pn,2,2,"ng-template",null,6,B),_()()}if(i&2){let e=l.$implicit,t=l.index,n=a(2);m(n.cx("chipItem",M(16,Pt,t))),p("pBind",n.ptm("chipItem")),x("id",n.id+"_multiple_option_"+t)("aria-label",n.getOptionLabel(e))("aria-setsize",n.modelValue().length)("aria-posinset",t+1)("aria-selected",!0),s(2),m(n.cx("pcChip")),p("pt",n.ptm("pcChip"))("label",!n.selectedItemTemplate&&!n._selectedItemTemplate&&n.getOptionLabel(e))("disabled",n.$disabled())("removable",!0),s(),p("ngTemplateOutlet",n.selectedItemTemplate||n._selectedItemTemplate)("ngTemplateOutletContext",M(18,lt,e))}}function cn(i,l){if(i&1){let e=C();h(0,"ul",24,3),b("focus",function(n){c(e);let o=a();return u(o.onMultipleContainerFocus(n))})("blur",function(n){c(e);let o=a();return u(o.onMultipleContainerBlur(n))})("keydown",function(n){c(e);let o=a();return u(o.onMultipleContainerKeyDown(n))}),d(2,sn,6,20,"li",25),h(3,"li",26)(4,"input",27,4),b("input",function(n){c(e);let o=a();return u(o.onInput(n))})("keydown",function(n){c(e);let o=a();return u(o.onKeyDown(n))})("change",function(n){c(e);let o=a();return u(o.onInputChange(n))})("focus",function(n){c(e);let o=a();return u(o.onInputFocus(n))})("blur",function(n){c(e);let o=a();return u(o.onInputBlur(n))})("paste",function(n){c(e);let o=a();return u(o.onInputPaste(n))})("keyup",function(n){c(e);let o=a();return u(o.onInputKeyUp(n))}),_()()()}if(i&2){let e=a();m(e.cx("inputMultiple")),p("pBind",e.ptm("inputMultiple"))("tabindex",-1),x("aria-orientation","horizontal")("aria-activedescendant",e.focused?e.focusedMultipleOptionId:void 0),s(2),p("ngForOf",e.modelValue()),s(),m(e.cx("inputChip")),p("pBind",e.ptm("inputChip")),s(),m(e.cx("pcInputText")),p("pAutoFocus",e.autofocus)("pBind",e.ptm("input"))("ngStyle",e.inputStyle),x("type",e.type)("id",e.inputId)("autocomplete",e.autocomplete)("name",e.name())("minlength",e.minlength())("maxlength",e.maxlength())("size",e.size())("min",e.min())("max",e.max())("pattern",e.pattern())("placeholder",e.$filled()?null:e.placeholder)("tabindex",e.$disabled()?-1:e.tabindex)("required",e.required()?"":void 0)("readonly",e.readonly?"":void 0)("disabled",e.$disabled()?"":void 0)("aria-label",e.ariaLabel)("aria-labelledby",e.ariaLabelledBy)("aria-required",e.required())("aria-expanded",e.overlayVisible??!1)("aria-controls",e.overlayVisible?e.id+"_list":null)("aria-activedescendant",e.focused?e.focusedOptionId:void 0)}}function un(i,l){if(i&1&&(R(),K(0,"svg",35)),i&2){let e=a(2);m(e.cx("loader")),p("pBind",e.ptm("loader"))("spin",!0),x("aria-hidden",!0)}}function dn(i,l){}function mn(i,l){i&1&&d(0,dn,0,0,"ng-template")}function hn(i,l){if(i&1&&(h(0,"span",32),d(1,mn,1,0,null,23),_()),i&2){let e=a(2);m(e.cx("loader")),p("pBind",e.ptm("loader")),x("aria-hidden",!0),s(),p("ngTemplateOutlet",e.loadingIconTemplate||e._loadingIconTemplate)}}function _n(i,l){if(i&1&&(S(0),d(1,un,1,5,"svg",33)(2,hn,2,5,"span",34),V()),i&2){let e=a();s(),p("ngIf",!e.loadingIconTemplate&&!e._loadingIconTemplate),s(),p("ngIf",e.loadingIconTemplate||e._loadingIconTemplate)}}function gn(i,l){if(i&1&&K(0,"span",38),i&2){let e=a(2);p("ngClass",e.dropdownIcon),x("aria-hidden",!0)}}function fn(i,l){if(i&1&&(R(),K(0,"svg",40)),i&2){let e=a(3);p("pBind",e.ptm("dropdown"))}}function yn(i,l){}function xn(i,l){i&1&&d(0,yn,0,0,"ng-template")}function vn(i,l){if(i&1&&(S(0),d(1,fn,1,1,"svg",39)(2,xn,1,0,null,23),V()),i&2){let e=a(2);s(),p("ngIf",!e.dropdownIconTemplate&&!e._dropdownIconTemplate),s(),p("ngTemplateOutlet",e.dropdownIconTemplate||e._dropdownIconTemplate)}}function bn(i,l){if(i&1){let e=C();h(0,"button",36,7),b("click",function(n){c(e);let o=a();return u(o.handleDropdownClick(n))}),d(2,gn,1,2,"span",37)(3,vn,3,2,"ng-container",14),_()}if(i&2){let e=a();m(e.cx("dropdown")),p("pBind",e.ptm("dropdown"))("disabled",e.$disabled()),x("aria-label",e.dropdownAriaLabel)("tabindex",e.tabindex),s(2),p("ngIf",e.dropdownIcon),s(),p("ngIf",!e.dropdownIcon)}}function In(i,l){i&1&&E(0)}function Cn(i,l){i&1&&E(0)}function wn(i,l){if(i&1&&d(0,Cn,1,0,"ng-container",29),i&2){let e=l.$implicit,t=l.options;a(2);let n=U(6);p("ngTemplateOutlet",n)("ngTemplateOutletContext",ie(2,at,e,t))}}function Tn(i,l){i&1&&E(0)}function On(i,l){if(i&1&&d(0,Tn,1,0,"ng-container",29),i&2){let e=l.options,t=a(4);p("ngTemplateOutlet",t.loaderTemplate||t._loaderTemplate)("ngTemplateOutletContext",M(2,Ut,e))}}function Sn(i,l){i&1&&(S(0),d(1,On,1,4,"ng-template",null,10,B),V())}function Vn(i,l){if(i&1){let e=C();h(0,"p-scroller",45,9),b("onLazyLoad",function(n){c(e);let o=a(2);return u(o.onLazyLoad.emit(n))}),d(2,wn,1,5,"ng-template",null,1,B)(4,Sn,3,0,"ng-container",14),_()}if(i&2){let e=a(2);te(M(9,ge,e.scrollHeight)),p("pt",e.ptm("virtualScroller"))("items",e.visibleOptions())("itemSize",e.virtualScrollItemSize)("autoSize",!0)("lazy",e.lazy)("options",e.virtualScrollOptions),s(4),p("ngIf",e.loaderTemplate||e._loaderTemplate)}}function En(i,l){i&1&&E(0)}function kn(i,l){if(i&1&&(S(0),d(1,En,1,0,"ng-container",29),V()),i&2){a();let e=U(6),t=a();s(),p("ngTemplateOutlet",e)("ngTemplateOutletContext",ie(3,at,t.visibleOptions(),ke(2,Gt)))}}function Mn(i,l){if(i&1&&(h(0,"span"),z(1),_()),i&2){let e=a(2).$implicit,t=a(3);s(),G(t.getOptionGroupLabel(e.optionGroup))}}function An(i,l){i&1&&E(0)}function Ln(i,l){if(i&1&&(S(0),h(1,"li",49),d(2,Mn,2,1,"span",14)(3,An,1,0,"ng-container",29),_(),V()),i&2){let e=a(),t=e.$implicit,n=e.index,o=a().options,r=a(2);s(),m(r.cx("optionGroup")),p("pBind",r.ptm("optionGroup"))("ngStyle",M(8,ge,o.itemSize+"px")),x("id",r.id+"_"+r.getOptionIndex(n,o)),s(),p("ngIf",!r.groupTemplate),s(),p("ngTemplateOutlet",r.groupTemplate)("ngTemplateOutletContext",M(10,lt,t.optionGroup))}}function Bn(i,l){if(i&1&&(h(0,"span"),z(1),_()),i&2){let e=a(2).$implicit,t=a(3);s(),G(t.getOptionLabel(e))}}function Fn(i,l){i&1&&E(0)}function Dn(i,l){if(i&1){let e=C();S(0),h(1,"li",50),b("click",function(n){c(e);let o=a().$implicit,r=a(3);return u(r.onOptionSelect(n,o))})("mouseenter",function(n){c(e);let o=a().index,r=a().options,v=a(2);return u(v.onOptionMouseEnter(n,v.getOptionIndex(o,r)))}),d(2,Bn,2,1,"span",14)(3,Fn,1,0,"ng-container",29),_(),V()}if(i&2){let e=a(),t=e.$implicit,n=e.index,o=a().options,r=a(2);s(),m(r.cx("option",xe(14,jt,t,n,o))),p("pBind",r.getPTOptions(t,o,n,"option"))("ngStyle",M(18,ge,o.itemSize+"px")),x("id",r.id+"_"+r.getOptionIndex(n,o))("aria-label",r.getOptionLabel(t))("aria-selected",r.isSelected(t))("aria-disabled",r.isOptionDisabled(t))("data-p-focused",r.focusedOptionIndex()===r.getOptionIndex(n,o))("aria-setsize",r.ariaSetSize)("aria-posinset",r.getAriaPosInset(r.getOptionIndex(n,o))),s(),p("ngIf",!r.itemTemplate&&!r._itemTemplate),s(),p("ngTemplateOutlet",r.itemTemplate||r._itemTemplate)("ngTemplateOutletContext",ie(20,Zt,t,o.getOptions?o.getOptions(n):n))}}function Rn(i,l){if(i&1&&d(0,Ln,4,12,"ng-container",14)(1,Dn,4,23,"ng-container",14),i&2){let e=l.$implicit,t=a(3);p("ngIf",t.isOptionGroup(e)),s(),p("ngIf",!t.isOptionGroup(e))}}function Kn(i,l){if(i&1&&(S(0),z(1),V()),i&2){let e=a(4);s(),ye(" ",e.searchResultMessageText," ")}}function zn(i,l){i&1&&E(0,null,12)}function Qn(i,l){if(i&1&&(h(0,"li",49),d(1,Kn,2,1,"ng-container",51)(2,zn,2,0,"ng-container",23),_()),i&2){let e=a().options,t=a(2);m(t.cx("emptyMessage")),p("pBind",t.ptm("emptyMessage"))("ngStyle",M(7,ge,e.itemSize+"px")),s(),p("ngIf",!t.emptyTemplate&&!t._emptyTemplate)("ngIfElse",t.empty),s(),p("ngTemplateOutlet",t.emptyTemplate||t._emptyTemplate)}}function $n(i,l){if(i&1&&(h(0,"ul",46,11),d(2,Rn,2,2,"ng-template",47)(3,Qn,3,9,"li",48),_()),i&2){let e=l.$implicit,t=l.options,n=a(2);te(t.contentStyle),m(n.cn(n.cx("list"),t.contentStyleClass)),p("pBind",n.ptm("list")),x("id",n.id+"_list")("aria-label",n.listLabel),s(2),p("ngForOf",e),s(),p("ngIf",!e||e&&e.length===0&&n.showEmptyMessage)}}function Hn(i,l){i&1&&E(0)}function Nn(i,l){if(i&1&&(h(0,"div",41),d(1,In,1,0,"ng-container",23),h(2,"div",42),d(3,Vn,5,11,"p-scroller",43)(4,kn,2,6,"ng-container",14),_(),d(5,$n,4,9,"ng-template",null,8,B)(7,Hn,1,0,"ng-container",23),_(),h(8,"span",44),z(9),_()),i&2){let e=a();m(e.cn(e.cx("overlay"),e.panelStyleClass)),p("pBind",e.ptm("overlay"))("ngStyle",e.panelStyle),s(),p("ngTemplateOutlet",e.headerTemplate||e._headerTemplate),s(),m(e.cx("listContainer")),ee("max-height",e.virtualScroll?"auto":e.scrollHeight),p("pBind",e.ptm("listContainer"))("tabindex",-1),s(),p("ngIf",e.virtualScroll),s(),p("ngIf",!e.virtualScroll),s(3),p("ngTemplateOutlet",e.footerTemplate||e._footerTemplate),s(2),ye(" ",e.selectedMessageText," ")}}var Pn=`
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
`,qn={root:{position:"relative"}},Un={root:({instance:i})=>["p-autocomplete p-component p-inputwrapper",{"p-invalid":i.invalid(),"p-focus":i.focused,"p-inputwrapper-filled":i.$filled(),"p-inputwrapper-focus":i.focused&&!i.$disabled()||i.autofocus||i.overlayVisible,"p-autocomplete-open":i.overlayVisible,"p-autocomplete-clearable":i.showClear&&!i.$disabled(),"p-autocomplete-fluid":i.hasFluid}],pcInputText:"p-autocomplete-input",inputMultiple:({instance:i})=>["p-autocomplete-input-multiple",{"p-disabled":i.$disabled(),"p-variant-filled":i.$variant()==="filled"}],chipItem:({instance:i,i:l})=>["p-autocomplete-chip-item",{"p-focus":i.focusedMultipleOptionIndex()===l}],pcChip:"p-autocomplete-chip",chipIcon:"p-autocomplete-chip-icon",inputChip:"p-autocomplete-input-chip",loader:"p-autocomplete-loader",dropdown:"p-autocomplete-dropdown",overlay:({instance:i})=>["p-autocomplete-overlay p-component-overlay p-component",{"p-input-filled":i.$variant()==="filled","p-ripple-disabled":i.config.ripple()===!1}],listContainer:"p-autocomplete-list-container",list:"p-autocomplete-list",optionGroup:"p-autocomplete-option-group",option:({instance:i,option:l,i:e,scrollerOptions:t})=>({"p-autocomplete-option":!0,"p-autocomplete-option-selected":i.isSelected(l),"p-focus":i.focusedOptionIndex()===i.getOptionIndex(e,t),"p-disabled":i.isOptionDisabled(l)}),emptyMessage:"p-autocomplete-empty-message",clearIcon:"p-autocomplete-clear-icon"},it=(()=>{class i extends me{name="autocomplete";style=Pn;classes=Un;inlineStyles=qn;static \u0275fac=(()=>{let e;return function(n){return(e||(e=q(i)))(n||i)}})();static \u0275prov=H({token:i,factory:i.\u0275fac})}return i})();var ot=new Z("AUTOCOMPLETE_INSTANCE"),Gn={provide:Pe,useExisting:Ie(()=>jn),multi:!0},jn=(()=>{class i extends je{overlayService;zone;$pcAutoComplete=O(ot,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=O(k,{self:!0});minLength=1;minQueryLength;delay=300;panelStyle;styleClass;panelStyleClass;inputStyle;inputId;inputStyleClass;placeholder;readonly;scrollHeight="200px";lazy=!1;virtualScroll;virtualScrollItemSize;virtualScrollOptions;autoHighlight;forceSelection;type="text";autoZIndex=!0;baseZIndex=0;ariaLabel;dropdownAriaLabel;ariaLabelledBy;dropdownIcon;unique=!0;group;completeOnFocus=!1;showClear=!1;dropdown;showEmptyMessage=!0;dropdownMode="blank";multiple;addOnTab=!1;tabindex;dataKey;emptyMessage;showTransitionOptions=".12s cubic-bezier(0, 0, 0.2, 1)";hideTransitionOptions=".1s linear";autofocus;autocomplete="off";optionGroupChildren="items";optionGroupLabel="label";overlayOptions;get suggestions(){return this._suggestions()}set suggestions(e){this._suggestions.set(e),this.handleSuggestionsChange()}optionLabel;optionValue;id;searchMessage;emptySelectionMessage;selectionMessage;autoOptionFocus=!1;selectOnFocus;searchLocale;optionDisabled;focusOnHover=!0;typeahead=!0;addOnBlur=!1;separator;appendTo=Me(void 0);completeMethod=new I;onSelect=new I;onUnselect=new I;onAdd=new I;onFocus=new I;onBlur=new I;onDropdownClick=new I;onClear=new I;onInputKeydown=new I;onKeyUp=new I;onShow=new I;onHide=new I;onLazyLoad=new I;inputEL;multiInputEl;multiContainerEL;dropdownButton;itemsViewChild;scroller;overlayViewChild;itemsWrapper;itemTemplate;emptyTemplate;headerTemplate;footerTemplate;selectedItemTemplate;groupTemplate;loaderTemplate;removeIconTemplate;loadingIconTemplate;clearIconTemplate;dropdownIconTemplate;onHostClick(e){this.onContainerClick(e)}value;_suggestions=W(null);timeout;overlayVisible;suggestionsUpdated;highlightOption;highlightOptionChanged;focused=!1;loading;scrollHandler;listId;searchTimeout;dirty=!1;_itemTemplate;_groupTemplate;_selectedItemTemplate;_headerTemplate;_emptyTemplate;_footerTemplate;_loaderTemplate;_removeIconTemplate;_loadingIconTemplate;_clearIconTemplate;_dropdownIconTemplate;focusedMultipleOptionIndex=W(-1);focusedOptionIndex=W(-1);_componentStyle=O(it);$appendTo=oe(()=>this.appendTo()||this.config.overlayAppendTo());visibleOptions=oe(()=>this.group?this.flatOptions(this._suggestions()):this._suggestions()||[]);inputValue=oe(()=>{let e=this.modelValue(),t=this.optionValueSelected?(this.suggestions||[]).find(n=>P(n,e,this.equalityKey())):e;if(j(e))if(typeof e=="object"||this.optionValueSelected){let n=this.getOptionLabel(t);return n??e}else return e;else return""});get focusedMultipleOptionId(){return this.focusedMultipleOptionIndex()!==-1?`${this.id}_multiple_option_${this.focusedMultipleOptionIndex()}`:null}get focusedOptionId(){return this.focusedOptionIndex()!==-1?`${this.id}_${this.focusedOptionIndex()}`:null}get searchResultMessageText(){return j(this.visibleOptions())&&this.overlayVisible?this.searchMessageText.replaceAll("{0}",this.visibleOptions().length):this.emptySearchMessageText}get searchMessageText(){return this.searchMessage||this.config.translation.searchMessage||""}get emptySearchMessageText(){return this.emptyMessage||this.config.translation.emptySearchMessage||""}get selectionMessageText(){return this.selectionMessage||this.config.translation.selectionMessage||""}get emptySelectionMessageText(){return this.emptySelectionMessage||this.config.translation.emptySelectionMessage||""}get selectedMessageText(){return this.hasSelectedOption()?this.selectionMessageText.replaceAll("{0}",this.multiple?this.modelValue()?.length:"1"):this.emptySelectionMessageText}get ariaSetSize(){return this.visibleOptions().filter(e=>!this.isOptionGroup(e)).length}get listLabel(){return this.config.getTranslation(de.ARIA).listLabel}get virtualScrollerDisabled(){return!this.virtualScroll}get optionValueSelected(){return typeof this.modelValue()=="string"&&this.optionValue}chipItemClass(e){return this._componentStyle.classes.chipItem({instance:this,i:e})}constructor(e,t){super(),this.overlayService=e,this.zone=t}onInit(){this.id=this.id||Fe("pn_id_"),this.cd.detectChanges()}templates;onAfterContentInit(){this.templates.forEach(e=>{switch(e.getType()){case"item":this._itemTemplate=e.template;break;case"group":this._groupTemplate=e.template;break;case"selecteditem":this._selectedItemTemplate=e.template;break;case"selectedItem":this._selectedItemTemplate=e.template;break;case"header":this._headerTemplate=e.template;break;case"empty":this._emptyTemplate=e.template;break;case"footer":this._footerTemplate=e.template;break;case"loader":this._loaderTemplate=e.template;break;case"removetokenicon":this._removeIconTemplate=e.template;break;case"loadingicon":this._loadingIconTemplate=e.template;break;case"clearicon":this._clearIconTemplate=e.template;break;case"dropdownicon":this._dropdownIconTemplate=e.template;break;default:this._itemTemplate=e.template;break}})}onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptms(["host","root"])),this.suggestionsUpdated&&this.overlayViewChild&&this.zone.runOutsideAngular(()=>{setTimeout(()=>{this.overlayViewChild&&this.overlayViewChild.alignOverlay()},1),this.suggestionsUpdated=!1})}handleSuggestionsChange(){if(this.loading){this._suggestions()?.length>0||this.showEmptyMessage||this.emptyTemplate?this.show():this.hide();let e=this.overlayVisible&&this.autoOptionFocus?this.findFirstFocusedOptionIndex():-1;this.focusedOptionIndex.set(e),this.suggestionsUpdated=!0,this.loading=!1,this.cd.markForCheck()}}flatOptions(e){return(e||[]).reduce((t,n,o)=>{t.push({optionGroup:n,group:!0,index:o});let r=this.getOptionGroupChildren(n);return r&&r.forEach(v=>t.push(v)),t},[])}isOptionGroup(e){return this.optionGroupLabel&&e.optionGroup&&e.group}findFirstOptionIndex(){return this.visibleOptions().findIndex(e=>this.isValidOption(e))}findLastOptionIndex(){return be(this.visibleOptions(),e=>this.isValidOption(e))}findFirstFocusedOptionIndex(){let e=this.findSelectedOptionIndex();return e<0?this.findFirstOptionIndex():e}findLastFocusedOptionIndex(){let e=this.findSelectedOptionIndex();return e<0?this.findLastOptionIndex():e}findSelectedOptionIndex(){return this.hasSelectedOption()?this.visibleOptions().findIndex(e=>this.isValidSelectedOption(e)):-1}findNextOptionIndex(e){let t=e<this.visibleOptions().length-1?this.visibleOptions().slice(e+1).findIndex(n=>this.isValidOption(n)):-1;return t>-1?t+e+1:e}findPrevOptionIndex(e){let t=e>0?be(this.visibleOptions().slice(0,e),n=>this.isValidOption(n)):-1;return t>-1?t:e}isValidSelectedOption(e){return this.isValidOption(e)&&this.isSelected(e)}isValidOption(e){return e&&!(this.isOptionDisabled(e)||this.isOptionGroup(e))}isOptionDisabled(e){return this.optionDisabled?N(e,this.optionDisabled):!1}isSelected(e){return this.multiple?this.unique?this.modelValue()?.some(t=>P(t,e,this.equalityKey())):!1:P(this.modelValue(),e,this.equalityKey())}isOptionMatched(e,t){return this.isValidOption(e)&&this.getOptionLabel(e).toLocaleLowerCase(this.searchLocale)===t.toLocaleLowerCase(this.searchLocale)}isInputClicked(e){return e.target===this.inputEL?.nativeElement}isDropdownClicked(e){return this.dropdownButton?.nativeElement?e.target===this.dropdownButton.nativeElement||this.dropdownButton.nativeElement.contains(e.target):!1}equalityKey(){return this.optionValue?void 0:this.dataKey}onContainerClick(e){this.$disabled()||this.loading||this.isInputClicked(e)||this.isDropdownClicked(e)||(!this.overlayViewChild||!this.overlayViewChild.overlayViewChild?.nativeElement.contains(e.target))&&A(this.inputEL?.nativeElement)}handleDropdownClick(e){let t;this.overlayVisible?this.hide(!0):(A(this.inputEL?.nativeElement),t=this.inputEL?.nativeElement?.value,this.dropdownMode==="blank"?this.search(e,"","dropdown"):this.dropdownMode==="current"&&this.search(e,t,"dropdown")),this.onDropdownClick.emit({originalEvent:e,query:t})}onInput(e){if(this.typeahead){let t=this.minQueryLength||this.minLength;this.searchTimeout&&clearTimeout(this.searchTimeout);let n=e.target.value;this.maxlength()!==null&&(n=n.split("").slice(0,this.maxlength()).join("")),!this.multiple&&!this.forceSelection&&this.updateModel(n),n.length===0&&!this.multiple?(this.onClear.emit(),setTimeout(()=>{this.hide()},this.delay/2)):n.length>=t?(this.focusedOptionIndex.set(-1),this.searchTimeout=setTimeout(()=>{this.search(e,n,"input")},this.delay)):this.hide()}}onInputChange(e){if(this.forceSelection){let t=!1;if(this.visibleOptions()){let n=this.visibleOptions().find(o=>this.isOptionMatched(o,this.inputEL?.nativeElement?.value||""));n!==void 0&&(t=!0,!this.isSelected(n)&&this.onOptionSelect(e,n))}t||(this.inputEL?.nativeElement&&(this.inputEL.nativeElement.value=""),!this.multiple&&this.updateModel(null))}}onInputFocus(e){if(this.$disabled())return;!this.dirty&&this.completeOnFocus&&this.search(e,e.target.value,"focus"),this.dirty=!0,this.focused=!0;let t=this.focusedOptionIndex()!==-1?this.focusedOptionIndex():this.overlayVisible&&this.autoOptionFocus?this.findFirstFocusedOptionIndex():-1;this.focusedOptionIndex.set(t),this.overlayVisible&&this.scrollInView(this.focusedOptionIndex()),this.onFocus.emit(e)}onMultipleContainerFocus(e){this.$disabled()||(this.focused=!0)}onMultipleContainerBlur(e){this.focusedMultipleOptionIndex.set(-1),this.focused=!1}onMultipleContainerKeyDown(e){if(this.$disabled()){e.preventDefault();return}switch(e.code){case"ArrowLeft":this.onArrowLeftKeyOnMultiple(e);break;case"ArrowRight":this.onArrowRightKeyOnMultiple(e);break;case"Backspace":this.onBackspaceKeyOnMultiple(e);break;default:break}}onInputBlur(e){if(this.dirty=!1,this.focused=!1,this.focusedOptionIndex.set(-1),this.addOnBlur&&this.multiple&&!this.typeahead){let t=(this.multiInputEl?.nativeElement?.value||e.target.value||"").trim();t&&!this.isSelected(t)&&(this.updateModel([...this.modelValue()||[],t]),this.onAdd.emit({originalEvent:e,value:t}),this.multiInputEl?.nativeElement?this.multiInputEl.nativeElement.value="":e.target.value="")}this.onModelTouched(),this.onBlur.emit(e)}onInputPaste(e){if(this.separator&&this.multiple&&!this.typeahead){let t=(e.clipboardData||window.clipboardData)?.getData("Text");if(t){let n=t.split(this.separator),o=[...this.modelValue()||[]];if(n.forEach(r=>{let v=r.trim();v&&!this.isSelected(v)&&o.push(v)}),o.length>(this.modelValue()||[]).length){let r=o.slice((this.modelValue()||[]).length);this.updateModel(o),r.forEach(v=>{this.onAdd.emit({originalEvent:e,value:v})}),this.multiInputEl?.nativeElement?this.multiInputEl.nativeElement.value="":e.target.value="",e.preventDefault()}}}else this.onKeyDown(e)}onInputKeyUp(e){this.onKeyUp.emit(e)}onKeyDown(e){if(this.$disabled()){e.preventDefault();return}switch(this.onInputKeydown.emit(e),e.code){case"ArrowDown":this.onArrowDownKey(e);break;case"ArrowUp":this.onArrowUpKey(e);break;case"ArrowLeft":this.onArrowLeftKey(e);break;case"ArrowRight":this.onArrowRightKey(e);break;case"Home":this.onHomeKey(e);break;case"End":this.onEndKey(e);break;case"PageDown":this.onPageDownKey(e);break;case"PageUp":this.onPageUpKey(e);break;case"Enter":case"NumpadEnter":this.onEnterKey(e);break;case"Escape":this.onEscapeKey(e);break;case"Tab":this.onTabKey(e);break;case"Backspace":this.onBackspaceKey(e);break;case"ShiftLeft":case"ShiftRight":break;default:this.handleSeparatorKey(e);break}}handleSeparatorKey(e){if(this.separator&&this.multiple&&!this.typeahead&&(this.separator===e.key||typeof this.separator=="string"&&e.key===this.separator||this.separator instanceof RegExp&&e.key.match(this.separator))){let t=(this.multiInputEl?.nativeElement?.value||e.target.value||"").trim();t&&!this.isSelected(t)&&(this.updateModel([...this.modelValue()||[],t]),this.onAdd.emit({originalEvent:e,value:t}),this.multiInputEl?.nativeElement?this.multiInputEl.nativeElement.value="":e.target.value="",e.preventDefault())}}onArrowDownKey(e){if(!this.overlayVisible)return;let t=this.focusedOptionIndex()!==-1?this.findNextOptionIndex(this.focusedOptionIndex()):this.findFirstFocusedOptionIndex();this.changeFocusedOptionIndex(e,t),e.preventDefault(),e.stopPropagation()}onArrowUpKey(e){if(this.overlayVisible)if(e.altKey)this.focusedOptionIndex()!==-1&&this.onOptionSelect(e,this.visibleOptions()[this.focusedOptionIndex()]),this.overlayVisible&&this.hide(),e.preventDefault();else{let t=this.focusedOptionIndex()!==-1?this.findPrevOptionIndex(this.focusedOptionIndex()):this.findLastFocusedOptionIndex();this.changeFocusedOptionIndex(e,t),e.preventDefault(),e.stopPropagation()}}onArrowLeftKey(e){let t=e.currentTarget;this.focusedOptionIndex.set(-1),this.multiple&&(ve(t.value)&&this.hasSelectedOption()?(A(this.multiContainerEL?.nativeElement),this.focusedMultipleOptionIndex.set(this.modelValue().length)):e.stopPropagation())}onArrowRightKey(e){this.focusedOptionIndex.set(-1),this.multiple&&e.stopPropagation()}onHomeKey(e){let{currentTarget:t}=e,n=t.value.length;t.setSelectionRange(0,e.shiftKey?n:0),this.focusedOptionIndex.set(-1),e.preventDefault()}onEndKey(e){let{currentTarget:t}=e,n=t.value.length;t.setSelectionRange(e.shiftKey?0:n,n),this.focusedOptionIndex.set(-1),e.preventDefault()}onPageDownKey(e){this.scrollInView(this.visibleOptions().length-1),e.preventDefault()}onPageUpKey(e){this.scrollInView(0),e.preventDefault()}onEnterKey(e){if(!this.typeahead&&!this.forceSelection&&this.multiple){let t=e.target.value?.trim();t&&!this.isSelected(t)&&(this.updateModel([...this.modelValue()||[],t]),this.inputEL?.nativeElement&&(this.inputEL.nativeElement.value=""))}if(this.overlayVisible)this.focusedOptionIndex()!==-1&&this.onOptionSelect(e,this.visibleOptions()[this.focusedOptionIndex()]),this.hide();else return;e.preventDefault()}onEscapeKey(e){this.overlayVisible&&this.hide(!0),e.preventDefault()}onTabKey(e){if(this.focusedOptionIndex()!==-1){this.onOptionSelect(e,this.visibleOptions()[this.focusedOptionIndex()]);return}if(this.multiple&&!this.typeahead){let t=(this.multiInputEl?.nativeElement?.value||this.inputEL?.nativeElement?.value||"").trim();if(this.addOnTab&&t&&!this.isSelected(t)){this.updateModel([...this.modelValue()||[],t]),this.onAdd.emit({originalEvent:e,value:t}),this.multiInputEl?.nativeElement?this.multiInputEl.nativeElement.value="":this.inputEL?.nativeElement&&(this.inputEL.nativeElement.value=""),this.updateInputValue(),e.preventDefault(),this.overlayVisible&&this.hide();return}}this.overlayVisible&&this.hide()}onBackspaceKey(e){if(this.multiple){if(j(this.modelValue())&&!this.inputEL?.nativeElement?.value){let t=this.modelValue()[this.modelValue().length-1],n=this.modelValue().slice(0,-1);this.updateModel(n),this.onUnselect.emit({originalEvent:e,value:t})}e.stopPropagation()}}onArrowLeftKeyOnMultiple(e){let t=this.focusedMultipleOptionIndex()<1?0:this.focusedMultipleOptionIndex()-1;this.focusedMultipleOptionIndex.set(t)}onArrowRightKeyOnMultiple(e){let t=this.focusedMultipleOptionIndex();t++,this.focusedMultipleOptionIndex.set(t),t>this.modelValue().length-1&&(this.focusedMultipleOptionIndex.set(-1),A(this.inputEL?.nativeElement))}onBackspaceKeyOnMultiple(e){this.focusedMultipleOptionIndex()!==-1&&this.removeOption(e,this.focusedMultipleOptionIndex())}onOptionSelect(e,t,n=!0){this.multiple?(this.inputEL?.nativeElement&&(this.inputEL.nativeElement.value=""),this.isSelected(t)||this.updateModel([...this.modelValue()||[],t])):this.updateModel(t),this.onSelect.emit({originalEvent:e,value:t}),n&&this.hide(!0)}onOptionMouseEnter(e,t){this.focusOnHover&&this.changeFocusedOptionIndex(e,t)}search(e,t,n){t!=null&&(n==="input"&&t.trim().length===0||(this.loading=!0,this.completeMethod.emit({originalEvent:e,query:t})))}removeOption(e,t){e.stopPropagation();let n=this.modelValue()[t],o=this.modelValue().filter((r,v)=>v!==t);this.updateModel(o),this.onUnselect.emit({originalEvent:e,value:n}),A(this.inputEL?.nativeElement)}updateModel(e){let t=null;e&&(t=this.multiple?e.map(n=>this.getOptionValue(n)):this.getOptionValue(e)),this.value=t,this.writeModelValue(e),this.onModelChange(t),this.updateInputValue(),this.cd.markForCheck()}updateInputValue(){this.inputEL&&this.inputEL.nativeElement&&(this.multiple?this.inputEL.nativeElement.value="":this.inputEL.nativeElement.value=this.inputValue())}autoUpdateModel(){if((this.selectOnFocus||this.autoHighlight)&&this.autoOptionFocus&&!this.hasSelectedOption()){let e=this.findFirstFocusedOptionIndex();this.focusedOptionIndex.set(e),this.onOptionSelect(null,this.visibleOptions()[this.focusedOptionIndex()],!1)}}scrollInView(e=-1){let t=e!==-1?`${this.id}_${e}`:this.focusedOptionId;if(this.itemsViewChild&&this.itemsViewChild.nativeElement){let n=se(this.itemsViewChild.nativeElement,`li[id="${t}"]`);n?n.scrollIntoView&&n.scrollIntoView({block:"nearest",inline:"nearest"}):this.virtualScrollerDisabled||setTimeout(()=>{this.virtualScroll&&this.scroller?.scrollToIndex(e!==-1?e:this.focusedOptionIndex())},0)}}changeFocusedOptionIndex(e,t){this.focusedOptionIndex()!==t&&(this.focusedOptionIndex.set(t),this.scrollInView(),this.selectOnFocus&&this.onOptionSelect(e,this.visibleOptions()[t],!1))}show(e=!1){this.dirty=!0,this.overlayVisible=!0;let t=this.focusedOptionIndex()!==-1?this.focusedOptionIndex():this.autoOptionFocus?this.findFirstFocusedOptionIndex():-1;this.focusedOptionIndex.set(t),e&&A(this.inputEL?.nativeElement),e&&A(this.inputEL?.nativeElement),this.onShow.emit(),this.cd.markForCheck()}hide(e=!1){let t=()=>{this.dirty=e,this.overlayVisible=!1,this.focusedOptionIndex.set(-1),e&&A(this.inputEL?.nativeElement),this.onHide.emit(),this.cd.markForCheck()};setTimeout(()=>{t()},0)}clear(){this.updateModel(null),this.inputEL?.nativeElement&&(this.inputEL.nativeElement.value=""),this.onClear.emit()}hasSelectedOption(){return j(this.modelValue())}getAriaPosInset(e){return(this.optionGroupLabel?e-this.visibleOptions().slice(0,e).filter(t=>this.isOptionGroup(t)).length:e)+1}getOptionLabel(e){return this.optionLabel?N(e,this.optionLabel):e&&e.label!=null?e.label:e}getOptionValue(e){return this.optionValue?N(e,this.optionValue):e&&e.value!=null?e.value:e}getOptionIndex(e,t){return this.virtualScrollerDisabled?e:t&&t.getItemOptions(e).index}getOptionGroupLabel(e){return this.optionGroupLabel?N(e,this.optionGroupLabel):e&&e.label!=null?e.label:e}getOptionGroupChildren(e){return this.optionGroupChildren?N(e,this.optionGroupChildren):e.items}getPTOptions(e,t,n,o){return this.ptm(o,{context:{option:e,index:this.getOptionIndex(n,t),selected:this.isSelected(e),focused:this.focusedOptionIndex()===this.getOptionIndex(n,t),disabled:this.isOptionDisabled(e)}})}onOverlayAnimationStart(e){if(e.toState==="visible"&&(this.itemsWrapper=se(this.overlayViewChild.overlayViewChild?.nativeElement,this.virtualScroll?".p-scroller":".p-autocomplete-panel"),this.virtualScroll&&(this.scroller?.setContentEl(this.itemsViewChild?.nativeElement),this.scroller?.viewInit()),this.visibleOptions()&&this.visibleOptions().length))if(this.virtualScroll){let t=this.modelValue()?this.focusedOptionIndex():-1;t!==-1&&this.scroller?.scrollToIndex(t)}else{let t=se(this.itemsWrapper,".p-autocomplete-item.p-highlight");t&&t.scrollIntoView({block:"nearest",inline:"center"})}}writeControlValue(e,t){let n=this.multiple?this.visibleOptions().filter(o=>e?.some(r=>P(r,o,this.equalityKey()))):this.visibleOptions().find(o=>P(e,o,this.equalityKey()));this.value=e,t(ve(n)?e:n),this.updateInputValue(),this.cd.markForCheck()}onDestroy(){this.scrollHandler&&(this.scrollHandler.destroy(),this.scrollHandler=null)}static \u0275fac=function(t){return new(t||i)(fe(De),fe(we))};static \u0275cmp=J({type:i,selectors:[["p-autoComplete"],["p-autocomplete"],["p-auto-complete"]],contentQueries:function(t,n,o){if(t&1&&(w(o,Ot,5),w(o,St,5),w(o,Vt,5),w(o,Et,5),w(o,kt,5),w(o,Mt,5),w(o,At,5),w(o,Lt,5),w(o,Bt,5),w(o,Ft,5),w(o,Dt,5),w(o,ce,4)),t&2){let r;f(r=y())&&(n.itemTemplate=r.first),f(r=y())&&(n.emptyTemplate=r.first),f(r=y())&&(n.headerTemplate=r.first),f(r=y())&&(n.footerTemplate=r.first),f(r=y())&&(n.selectedItemTemplate=r.first),f(r=y())&&(n.groupTemplate=r.first),f(r=y())&&(n.loaderTemplate=r.first),f(r=y())&&(n.removeIconTemplate=r.first),f(r=y())&&(n.loadingIconTemplate=r.first),f(r=y())&&(n.clearIconTemplate=r.first),f(r=y())&&(n.dropdownIconTemplate=r.first),f(r=y())&&(n.templates=r)}},viewQuery:function(t,n){if(t&1&&(L(Rt,5),L(Kt,5),L(zt,5),L(Qt,5),L($t,5),L(Ht,5),L(Nt,5)),t&2){let o;f(o=y())&&(n.inputEL=o.first),f(o=y())&&(n.multiInputEl=o.first),f(o=y())&&(n.multiContainerEL=o.first),f(o=y())&&(n.dropdownButton=o.first),f(o=y())&&(n.itemsViewChild=o.first),f(o=y())&&(n.scroller=o.first),f(o=y())&&(n.overlayViewChild=o.first)}},hostVars:4,hostBindings:function(t,n){t&1&&b("click",function(r){return n.onHostClick(r)}),t&2&&(te(n.sx("root")),m(n.cn(n.cx("root"),n.styleClass)))},inputs:{minLength:[2,"minLength","minLength",Q],minQueryLength:[2,"minQueryLength","minQueryLength",Q],delay:[2,"delay","delay",Q],panelStyle:"panelStyle",styleClass:"styleClass",panelStyleClass:"panelStyleClass",inputStyle:"inputStyle",inputId:"inputId",inputStyleClass:"inputStyleClass",placeholder:"placeholder",readonly:[2,"readonly","readonly",g],scrollHeight:"scrollHeight",lazy:[2,"lazy","lazy",g],virtualScroll:[2,"virtualScroll","virtualScroll",g],virtualScrollItemSize:[2,"virtualScrollItemSize","virtualScrollItemSize",Q],virtualScrollOptions:"virtualScrollOptions",autoHighlight:[2,"autoHighlight","autoHighlight",g],forceSelection:[2,"forceSelection","forceSelection",g],type:"type",autoZIndex:[2,"autoZIndex","autoZIndex",g],baseZIndex:[2,"baseZIndex","baseZIndex",Q],ariaLabel:"ariaLabel",dropdownAriaLabel:"dropdownAriaLabel",ariaLabelledBy:"ariaLabelledBy",dropdownIcon:"dropdownIcon",unique:[2,"unique","unique",g],group:[2,"group","group",g],completeOnFocus:[2,"completeOnFocus","completeOnFocus",g],showClear:[2,"showClear","showClear",g],dropdown:[2,"dropdown","dropdown",g],showEmptyMessage:[2,"showEmptyMessage","showEmptyMessage",g],dropdownMode:"dropdownMode",multiple:[2,"multiple","multiple",g],addOnTab:[2,"addOnTab","addOnTab",g],tabindex:[2,"tabindex","tabindex",Q],dataKey:"dataKey",emptyMessage:"emptyMessage",showTransitionOptions:"showTransitionOptions",hideTransitionOptions:"hideTransitionOptions",autofocus:[2,"autofocus","autofocus",g],autocomplete:"autocomplete",optionGroupChildren:"optionGroupChildren",optionGroupLabel:"optionGroupLabel",overlayOptions:"overlayOptions",suggestions:"suggestions",optionLabel:"optionLabel",optionValue:"optionValue",id:"id",searchMessage:"searchMessage",emptySelectionMessage:"emptySelectionMessage",selectionMessage:"selectionMessage",autoOptionFocus:[2,"autoOptionFocus","autoOptionFocus",g],selectOnFocus:[2,"selectOnFocus","selectOnFocus",g],searchLocale:[2,"searchLocale","searchLocale",g],optionDisabled:"optionDisabled",focusOnHover:[2,"focusOnHover","focusOnHover",g],typeahead:[2,"typeahead","typeahead",g],addOnBlur:[2,"addOnBlur","addOnBlur",g],separator:"separator",appendTo:[1,"appendTo"]},outputs:{completeMethod:"completeMethod",onSelect:"onSelect",onUnselect:"onUnselect",onAdd:"onAdd",onFocus:"onFocus",onBlur:"onBlur",onDropdownClick:"onDropdownClick",onClear:"onClear",onInputKeydown:"onInputKeydown",onKeyUp:"onKeyUp",onShow:"onShow",onHide:"onHide",onLazyLoad:"onLazyLoad"},features:[ne([Gn,it,{provide:ot,useExisting:i},{provide:he,useExisting:i}]),Y([k]),X],decls:9,vars:13,consts:[["overlay",""],["content",""],["focusInput",""],["multiContainer",""],["focusInput","","multiIn",""],["token",""],["removeicon",""],["ddBtn",""],["buildInItems",""],["scroller",""],["loader",""],["items",""],["empty",""],["pInputText","","aria-autocomplete","list","role","combobox",3,"pAutoFocus","pt","class","ngStyle","variant","invalid","pSize","fluid","input","keydown","change","focus","blur","paste","keyup",4,"ngIf"],[4,"ngIf"],["role","listbox",3,"pBind","class","tabindex","focus","blur","keydown",4,"ngIf"],["type","button","pRipple","",3,"pBind","class","disabled","click",4,"ngIf"],[3,"visibleChange","onAnimationStart","onHide","pt","hostAttrSelector","visible","options","target","appendTo","showTransitionOptions","hideTransitionOptions"],["pInputText","","aria-autocomplete","list","role","combobox",3,"input","keydown","change","focus","blur","paste","keyup","pAutoFocus","pt","ngStyle","variant","invalid","pSize","fluid"],["data-p-icon","times",3,"pBind","class","click",4,"ngIf"],[3,"pBind","class","click",4,"ngIf"],["data-p-icon","times",3,"click","pBind"],[3,"click","pBind"],[4,"ngTemplateOutlet"],["role","listbox",3,"focus","blur","keydown","pBind","tabindex"],["role","option",3,"pBind","class",4,"ngFor","ngForOf"],["role","option",3,"pBind"],["role","combobox","aria-autocomplete","list",3,"input","keydown","change","focus","blur","paste","keyup","pAutoFocus","pBind","ngStyle"],[3,"onRemove","pt","label","disabled","removable"],[4,"ngTemplateOutlet","ngTemplateOutletContext"],[3,"pBind",4,"ngIf"],["data-p-icon","times-circle"],[3,"pBind"],["data-p-icon","spinner",3,"pBind","class","spin",4,"ngIf"],[3,"pBind","class",4,"ngIf"],["data-p-icon","spinner",3,"pBind","spin"],["type","button","pRipple","",3,"click","pBind","disabled"],[3,"ngClass",4,"ngIf"],[3,"ngClass"],["data-p-icon","chevron-down",3,"pBind",4,"ngIf"],["data-p-icon","chevron-down",3,"pBind"],[3,"pBind","ngStyle"],[3,"pBind","tabindex"],[3,"pt","items","style","itemSize","autoSize","lazy","options","onLazyLoad",4,"ngIf"],["role","status","aria-live","polite",1,"p-hidden-accessible"],[3,"onLazyLoad","pt","items","itemSize","autoSize","lazy","options"],["role","listbox",3,"pBind"],["ngFor","",3,"ngForOf"],["role","option",3,"pBind","class","ngStyle",4,"ngIf"],["role","option",3,"pBind","ngStyle"],["pRipple","","role","option",3,"click","mouseenter","pBind","ngStyle"],[4,"ngIf","ngIfElse"]],template:function(t,n){if(t&1){let o=C();d(0,Wt,2,31,"input",13)(1,tn,3,2,"ng-container",14)(2,cn,7,36,"ul",15)(3,_n,3,2,"ng-container",14)(4,bn,4,8,"button",16),h(5,"p-overlay",17,0),Ee("visibleChange",function(v){return c(o),Ve(n.overlayVisible,v)||(n.overlayVisible=v),u(v)}),b("onAnimationStart",function(v){return c(o),u(n.onOverlayAnimationStart(v))})("onHide",function(){return c(o),u(n.hide())}),d(7,Nn,10,15,"ng-template",null,1,B),_()}t&2&&(p("ngIf",!n.multiple),s(),p("ngIf",n.$filled()&&!n.$disabled()&&n.showClear&&!n.loading),s(),p("ngIf",n.multiple),s(),p("ngIf",n.loading),s(),p("ngIf",n.dropdown),s(),p("pt",n.ptm("pcOverlay"))("hostAttrSelector",n.$attrSelector),Se("visible",n.overlayVisible),p("options",n.overlayOptions)("target","@parent")("appendTo",n.$appendTo())("showTransitionOptions",n.showTransitionOptions)("hideTransitionOptions",n.hideTransitionOptions))},dependencies:[pe,le,Le,ae,re,Be,Ze,Ge,qe,We,Ue,_e,Qe,ze,tt,ue,$e,Ke,k],encapsulation:2,changeDetection:0})}return i})();var $=class ${constructor(){this.http=O(Ae);this.appConfig=O(He);this.log=O(Ne)}getItemList(){let l=this.appConfig.apiUrl+"items/list/";return this.http.get(l).pipe(T(e=>e),D(e=>(this.log.error("ItemsApiService.getItemList(): Could not read item list - "+e.error?.error),F([]))))}getItemTree(){let l=this.appConfig.apiUrl+"items/tree";return this.http.get(l).pipe(T(e=>e),D(e=>(this.log.error("ItemsApiService.getItemTree(): Could not read item tree - "+e.error?.error),F([]))))}getCoreItemAttributes(){let l=this.appConfig.apiUrl+"items/attributes";return this.http.get(l).pipe(T(e=>e),D(e=>(this.log.error("ItemsApiService.getCoreItemAttributes(): Could not read attribute catalog - "+e.error?.error),F({}))))}getItemDetails(l){let e=this.appConfig.apiUrl+"items/"+l;return this.http.get(e).pipe(T(t=>t),D(t=>(this.log.error("ItemsApiService.getItemDetails("+l+"): Could not read item details - "+t.error?.error),F([]))))}changeItemValue(l,e){let t=this.appConfig.apiUrl+"items/"+l;return this.http.put(t,JSON.stringify({value:e})).pipe(T(n=>n),D(n=>(this.log.error("ItemsApiService.changeItemValue("+l+"): Could not set value - "+n.error?.error),F({}))))}createItem(l,e,t=!0,n){let o=this.appConfig.apiUrl+"items/"+l,r={config:e,persist:t};return n&&(r.filename=n),this.http.post(o,JSON.stringify(r)).pipe(T(v=>v))}editItem(l,e){let t=this.appConfig.apiUrl+"items/"+l;return this.http.patch(t,JSON.stringify({config:e})).pipe(T(n=>n))}renameItem(l,e,t){let n=this.appConfig.apiUrl+"items/"+l+"/rename",o={new_path:e};return t&&(o.filename=t),this.http.post(n,JSON.stringify(o)).pipe(T(r=>r))}deleteItem(l,e=!0){let t=this.appConfig.apiUrl+"items/"+l+"?persist="+e;return this.http.delete(t).pipe(T(n=>n))}removeReferences(l){let e=this.appConfig.apiUrl+"items/"+l+"/remove_references";return this.http.post(e,"").pipe(T(t=>t))}getItemReferences(l){let e=this.appConfig.apiUrl+"items/"+l+"/references";return this.http.get(e).pipe(T(t=>t),D(t=>(this.log.error("ItemsApiService.getItemReferences("+l+"): Could not read references - "+t.error?.error),F(null))))}};$.\u0275fac=function(e){return new(e||$)},$.\u0275prov=H({token:$,factory:$.\u0275fac,providedIn:"root"});var rt=$;export{jn as a,rt as b};
