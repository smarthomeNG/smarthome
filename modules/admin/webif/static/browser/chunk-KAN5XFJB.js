import{a as we}from"./chunk-7HEZD7Q7.js";import{f as Ce}from"./chunk-I6AFGF2Y.js";import{b as Ie,k as Y,n as ye}from"./chunk-TKLL4RYZ.js";import{f as ve}from"./chunk-MSJFQPAD.js";import{Ka as _e,La as Q,Oa as be,Qa as ge,Sa as G,Ta as xe,Ua as W,j as pe,l as ce,m as de,n as me,r as he,ta as fe}from"./chunk-JYMX7FOM.js";import{$b as P,Fb as l,Gb as V,Hb as S,Ib as B,Lb as j,Mb as R,Nb as L,Pb as U,Tb as y,U as K,V as J,Vb as s,W as ee,Wa as m,Y as te,Yb as se,Yc as T,Zb as le,Zc as H,_ as N,_b as $,a as O,b as z,db as re,ea as h,fa as f,ga as I,ha as ne,hc as v,ib as F,jb as oe,kb as ae,la as k,mb as ue,nb as A,ob as b,tc as q,ua as M,wa as ie,wb as E}from"./chunk-BDB7QD2D.js";function Me(i,a){let e=[],n=i.value;if(n!==null&&n!==""){let t=String(i.type).toLowerCase(),r=n;t==="knx_ga"&&!a.isKnxGroupaddress(r)&&e.push({code:"invalid_knx_address",value:r}),t==="mac"&&!a.isMac(r)&&e.push({code:"invalid_mac_address",value:r}),t==="ipv4"&&!a.isIpv4(r)&&e.push({code:"invalid_ip_address",value:r,version:"v4"}),t==="ipv6"&&!a.isIpv6(r)&&e.push({code:"invalid_ip_address",value:r,version:"v6"}),t==="ip"&&!a.isIpv4(r)&&!a.isIpv6(r)&&!a.isHostname(r)&&e.push({code:"invalid_hostname",value:r})}return n!==null&&n<i.valid_min&&e.push({code:"below_min",value:n,min:i.valid_min}),n!==null&&n>i.valid_max&&e.push({code:"above_max",value:n,max:i.valid_max}),(n==null||n==="")&&i.mandatory&&e.push({code:"mandatory_value"}),e}function It(i,a){switch(i.code){case"invalid_knx_address":return`'${i.value}' ${a("PLUGIN.INVALID_KNX_ADDRESS")}`;case"invalid_mac_address":return`'${i.value}' ${a("PLUGIN.INVALID_MAC_ADDRESS")}`;case"invalid_ip_address":return`'${i.value}' ${a("PLUGIN.INVALID_IP_ADDRESS")} (${i.version})`;case"invalid_hostname":return`'${i.value}' ${a("PLUGIN.INVALID_HOSTNAME")}`;case"below_min":return`${a("PLUGIN.DEFINED_MIN")} '${i.min}', ${a("PLUGIN.ACTUAL_VALUE")} '${i.value}'`;case"above_max":return`${a("PLUGIN.DEFINED_MAX")} '${i.max}', ${a("PLUGIN.ACTUAL_VALUE")} '${i.value}'`;case"mandatory_value":return a("PLUGIN.MANDATORY_VALUE")}}function yt(i,a,e){for(let n of i){let t=n.key.trim();if(t==="")continue;let r=Me(z(O({},a(t)),{value:n.value}),e);if(r.length>0)return{key:t,error:r[r.length-1]}}return null}var Fe=["data-p-icon","angle-down"],Be=(()=>{class i extends W{static \u0275fac=(()=>{let e;return function(t){return(e||(e=M(i)))(t||i)}})();static \u0275cmp=F({type:i,selectors:[["","data-p-icon","angle-down"]],features:[A],attrs:Fe,decls:1,vars:0,consts:[["d","M3.58659 4.5007C3.68513 4.50023 3.78277 4.51945 3.87379 4.55723C3.9648 4.59501 4.04735 4.65058 4.11659 4.7207L7.11659 7.7207L10.1166 4.7207C10.2619 4.65055 10.4259 4.62911 10.5843 4.65956C10.7427 4.69002 10.8871 4.77074 10.996 4.88976C11.1049 5.00877 11.1726 5.15973 11.1889 5.32022C11.2052 5.48072 11.1693 5.6422 11.0866 5.7807L7.58659 9.2807C7.44597 9.42115 7.25534 9.50004 7.05659 9.50004C6.85784 9.50004 6.66722 9.42115 6.52659 9.2807L3.02659 5.7807C2.88614 5.64007 2.80725 5.44945 2.80725 5.2507C2.80725 5.05195 2.88614 4.86132 3.02659 4.7207C3.09932 4.64685 3.18675 4.58911 3.28322 4.55121C3.37969 4.51331 3.48305 4.4961 3.58659 4.5007Z","fill","currentColor"]],template:function(n,t){n&1&&(I(),j(0,"path",0))},encapsulation:2})}return i})();var Ae=["data-p-icon","angle-up"],Te=(()=>{class i extends W{static \u0275fac=(()=>{let e;return function(t){return(e||(e=M(i)))(t||i)}})();static \u0275cmp=F({type:i,selectors:[["","data-p-icon","angle-up"]],features:[A],attrs:Ae,decls:1,vars:0,consts:[["d","M10.4134 9.49931C10.3148 9.49977 10.2172 9.48055 10.1262 9.44278C10.0352 9.405 9.95263 9.34942 9.88338 9.27931L6.88338 6.27931L3.88338 9.27931C3.73811 9.34946 3.57409 9.3709 3.41567 9.34044C3.25724 9.30999 3.11286 9.22926 3.00395 9.11025C2.89504 8.99124 2.82741 8.84028 2.8111 8.67978C2.79478 8.51928 2.83065 8.35781 2.91338 8.21931L6.41338 4.71931C6.55401 4.57886 6.74463 4.49997 6.94338 4.49997C7.14213 4.49997 7.33276 4.57886 7.47338 4.71931L10.9734 8.21931C11.1138 8.35994 11.1927 8.55056 11.1927 8.74931C11.1927 8.94806 11.1138 9.13868 10.9734 9.27931C10.9007 9.35315 10.8132 9.41089 10.7168 9.44879C10.6203 9.48669 10.5169 9.5039 10.4134 9.49931Z","fill","currentColor"]],template:function(n,t){n&1&&(I(),j(0,"path",0))},encapsulation:2})}return i})();var De=`
    .p-inputnumber {
        display: inline-flex;
        position: relative;
    }

    .p-inputnumber-button {
        display: flex;
        align-items: center;
        justify-content: center;
        flex: 0 0 auto;
        cursor: pointer;
        background: dt('inputnumber.button.background');
        color: dt('inputnumber.button.color');
        width: dt('inputnumber.button.width');
        transition:
            background dt('inputnumber.transition.duration'),
            color dt('inputnumber.transition.duration'),
            border-color dt('inputnumber.transition.duration'),
            outline-color dt('inputnumber.transition.duration');
    }

    .p-inputnumber-button:disabled {
        cursor: auto;
    }

    .p-inputnumber-button:not(:disabled):hover {
        background: dt('inputnumber.button.hover.background');
        color: dt('inputnumber.button.hover.color');
    }

    .p-inputnumber-button:not(:disabled):active {
        background: dt('inputnumber.button.active.background');
        color: dt('inputnumber.button.active.color');
    }

    .p-inputnumber-stacked .p-inputnumber-button {
        position: relative;
        flex: 1 1 auto;
        border: 0 none;
    }

    .p-inputnumber-stacked .p-inputnumber-button-group {
        display: flex;
        flex-direction: column;
        position: absolute;
        inset-block-start: 1px;
        inset-inline-end: 1px;
        height: calc(100% - 2px);
        z-index: 1;
    }

    .p-inputnumber-stacked .p-inputnumber-increment-button {
        padding: 0;
        border-start-end-radius: calc(dt('inputnumber.button.border.radius') - 1px);
    }

    .p-inputnumber-stacked .p-inputnumber-decrement-button {
        padding: 0;
        border-end-end-radius: calc(dt('inputnumber.button.border.radius') - 1px);
    }

    .p-inputnumber-stacked .p-inputnumber-input {
        padding-inline-end: calc(dt('inputnumber.button.width') + dt('form.field.padding.x'));
    }

    .p-inputnumber-horizontal .p-inputnumber-button {
        border: 1px solid dt('inputnumber.button.border.color');
    }

    .p-inputnumber-horizontal .p-inputnumber-button:hover {
        border-color: dt('inputnumber.button.hover.border.color');
    }

    .p-inputnumber-horizontal .p-inputnumber-button:active {
        border-color: dt('inputnumber.button.active.border.color');
    }

    .p-inputnumber-horizontal .p-inputnumber-increment-button {
        order: 3;
        border-start-end-radius: dt('inputnumber.button.border.radius');
        border-end-end-radius: dt('inputnumber.button.border.radius');
        border-inline-start: 0 none;
    }

    .p-inputnumber-horizontal .p-inputnumber-input {
        order: 2;
        border-radius: 0;
    }

    .p-inputnumber-horizontal .p-inputnumber-decrement-button {
        order: 1;
        border-start-start-radius: dt('inputnumber.button.border.radius');
        border-end-start-radius: dt('inputnumber.button.border.radius');
        border-inline-end: 0 none;
    }

    .p-floatlabel:has(.p-inputnumber-horizontal) label {
        margin-inline-start: dt('inputnumber.button.width');
    }

    .p-inputnumber-vertical {
        flex-direction: column;
    }

    .p-inputnumber-vertical .p-inputnumber-button {
        border: 1px solid dt('inputnumber.button.border.color');
        padding: dt('inputnumber.button.vertical.padding');
    }

    .p-inputnumber-vertical .p-inputnumber-button:hover {
        border-color: dt('inputnumber.button.hover.border.color');
    }

    .p-inputnumber-vertical .p-inputnumber-button:active {
        border-color: dt('inputnumber.button.active.border.color');
    }

    .p-inputnumber-vertical .p-inputnumber-increment-button {
        order: 1;
        border-start-start-radius: dt('inputnumber.button.border.radius');
        border-start-end-radius: dt('inputnumber.button.border.radius');
        width: 100%;
        border-block-end: 0 none;
    }

    .p-inputnumber-vertical .p-inputnumber-input {
        order: 2;
        border-radius: 0;
        text-align: center;
    }

    .p-inputnumber-vertical .p-inputnumber-decrement-button {
        order: 3;
        border-end-start-radius: dt('inputnumber.button.border.radius');
        border-end-end-radius: dt('inputnumber.button.border.radius');
        width: 100%;
        border-block-start: 0 none;
    }

    .p-inputnumber-input {
        flex: 1 1 auto;
    }

    .p-inputnumber-fluid {
        width: 100%;
    }

    .p-inputnumber-fluid .p-inputnumber-input {
        width: 1%;
    }

    .p-inputnumber-fluid.p-inputnumber-vertical .p-inputnumber-input {
        width: 100%;
    }

    .p-inputnumber:has(.p-inputtext-sm) .p-inputnumber-button .p-icon {
        font-size: dt('form.field.sm.font.size');
        width: dt('form.field.sm.font.size');
        height: dt('form.field.sm.font.size');
    }

    .p-inputnumber:has(.p-inputtext-lg) .p-inputnumber-button .p-icon {
        font-size: dt('form.field.lg.font.size');
        width: dt('form.field.lg.font.size');
        height: dt('form.field.lg.font.size');
    }

    .p-inputnumber-clear-icon {
        position: absolute;
        top: 50%;
        margin-top: -0.5rem;
        cursor: pointer;
        inset-inline-end: dt('form.field.padding.x');
        color: dt('form.field.icon.color');
    }

    .p-inputnumber:has(.p-inputnumber-clear-icon) .p-inputnumber-input {
        padding-inline-end: calc((dt('form.field.padding.x') * 2) + dt('icon.size'));
    }

    .p-inputnumber-stacked .p-inputnumber-clear-icon {
        inset-inline-end: calc(dt('inputnumber.button.width') + dt('form.field.padding.x'));
    }

    .p-inputnumber-stacked:has(.p-inputnumber-clear-icon) .p-inputnumber-input {
        padding-inline-end: calc(dt('inputnumber.button.width') + (dt('form.field.padding.x') * 2) + dt('icon.size'));
    }

    .p-inputnumber-horizontal .p-inputnumber-clear-icon {
        inset-inline-end: calc(dt('inputnumber.button.width') + dt('form.field.padding.x'));
    }
`;var Re=["clearicon"],Le=["incrementbuttonicon"],Ue=["decrementbuttonicon"],$e=["input"];function Pe(i,a){if(i&1){let e=U();I(),V(0,"svg",7),y("click",function(){h(e);let t=s(2);return f(t.clear())}),S()}if(i&2){let e=s(2);v(e.cx("clearIcon")),l("pBind",e.ptm("clearIcon"))}}function Ge(i,a){}function Oe(i,a){i&1&&b(0,Ge,0,0,"ng-template")}function ze(i,a){if(i&1){let e=U();V(0,"span",8),y("click",function(){h(e);let t=s(2);return f(t.clear())}),b(1,Oe,1,0,null,9),S()}if(i&2){let e=s(2);v(e.cx("clearIcon")),l("pBind",e.ptm("clearIcon")),m(),l("ngTemplateOutlet",e.clearIconTemplate||e._clearIconTemplate)}}function Ke(i,a){if(i&1&&(R(0),b(1,Pe,1,3,"svg",5)(2,ze,2,4,"span",6),L()),i&2){let e=s();m(),l("ngIf",!e.clearIconTemplate&&!e._clearIconTemplate),m(),l("ngIf",e.clearIconTemplate||e._clearIconTemplate)}}function je(i,a){if(i&1&&B(0,"span",13),i&2){let e=s(2);l("pBind",e.ptm("incrementButtonIcon"))("ngClass",e.incrementButtonIcon)}}function qe(i,a){if(i&1&&(I(),B(0,"svg",15)),i&2){let e=s(3);l("pBind",e.ptm("incrementButtonIcon"))}}function He(i,a){}function Qe(i,a){i&1&&b(0,He,0,0,"ng-template")}function We(i,a){if(i&1&&(R(0),b(1,qe,1,1,"svg",14)(2,Qe,1,0,null,9),L()),i&2){let e=s(2);m(),l("ngIf",!e.incrementButtonIconTemplate&&!e._incrementButtonIconTemplate),m(),l("ngTemplateOutlet",e.incrementButtonIconTemplate||e._incrementButtonIconTemplate)}}function Ye(i,a){if(i&1&&B(0,"span",13),i&2){let e=s(2);l("pBind",e.ptm("decrementButtonIcon"))("ngClass",e.decrementButtonIcon)}}function Xe(i,a){if(i&1&&(I(),B(0,"svg",17)),i&2){let e=s(3);l("pBind",e.ptm("decrementButtonIcon"))}}function Ze(i,a){}function Je(i,a){i&1&&b(0,Ze,0,0,"ng-template")}function et(i,a){if(i&1&&(R(0),b(1,Xe,1,1,"svg",16)(2,Je,1,0,null,9),L()),i&2){let e=s(2);m(),l("ngIf",!e.decrementButtonIconTemplate&&!e._decrementButtonIconTemplate),m(),l("ngTemplateOutlet",e.decrementButtonIconTemplate||e._decrementButtonIconTemplate)}}function tt(i,a){if(i&1){let e=U();V(0,"span",10)(1,"button",11),y("mousedown",function(t){h(e);let r=s();return f(r.onUpButtonMouseDown(t))})("mouseup",function(){h(e);let t=s();return f(t.onUpButtonMouseUp())})("mouseleave",function(){h(e);let t=s();return f(t.onUpButtonMouseLeave())})("keydown",function(t){h(e);let r=s();return f(r.onUpButtonKeyDown(t))})("keyup",function(){h(e);let t=s();return f(t.onUpButtonKeyUp())}),b(2,je,1,2,"span",12)(3,We,3,2,"ng-container",2),S(),V(4,"button",11),y("mousedown",function(t){h(e);let r=s();return f(r.onDownButtonMouseDown(t))})("mouseup",function(){h(e);let t=s();return f(t.onDownButtonMouseUp())})("mouseleave",function(){h(e);let t=s();return f(t.onDownButtonMouseLeave())})("keydown",function(t){h(e);let r=s();return f(r.onDownButtonKeyDown(t))})("keyup",function(){h(e);let t=s();return f(t.onDownButtonKeyUp())}),b(5,Ye,1,2,"span",12)(6,et,3,2,"ng-container",2),S()()}if(i&2){let e=s();v(e.cx("buttonGroup")),l("pBind",e.ptm("buttonGroup")),E("data-p",e.dataP),m(),v(e.cn(e.cx("incrementButton"),e.incrementButtonClass)),l("pBind",e.ptm("incrementButton")),E("disabled",e.$disabled()?"":void 0)("aria-hidden",!0)("data-p",e.dataP),m(),l("ngIf",e.incrementButtonIcon),m(),l("ngIf",!e.incrementButtonIcon),m(),v(e.cn(e.cx("decrementButton"),e.decrementButtonClass)),l("pBind",e.ptm("decrementButton")),E("disabled",e.$disabled()?"":void 0)("aria-hidden",!0)("data-p",e.dataP),m(),l("ngIf",e.decrementButtonIcon),m(),l("ngIf",!e.decrementButtonIcon)}}function nt(i,a){if(i&1&&B(0,"span",13),i&2){let e=s(2);l("pBind",e.ptm("incrementButtonIcon"))("ngClass",e.incrementButtonIcon)}}function it(i,a){if(i&1&&(I(),B(0,"svg",15)),i&2){let e=s(3);l("pBind",e.ptm("incrementButtonIcon"))}}function rt(i,a){}function ot(i,a){i&1&&b(0,rt,0,0,"ng-template")}function at(i,a){if(i&1&&(R(0),b(1,it,1,1,"svg",14)(2,ot,1,0,null,9),L()),i&2){let e=s(2);m(),l("ngIf",!e.incrementButtonIconTemplate&&!e._incrementButtonIconTemplate),m(),l("ngTemplateOutlet",e.incrementButtonIconTemplate||e._incrementButtonIconTemplate)}}function ut(i,a){if(i&1){let e=U();V(0,"button",11),y("mousedown",function(t){h(e);let r=s();return f(r.onUpButtonMouseDown(t))})("mouseup",function(){h(e);let t=s();return f(t.onUpButtonMouseUp())})("mouseleave",function(){h(e);let t=s();return f(t.onUpButtonMouseLeave())})("keydown",function(t){h(e);let r=s();return f(r.onUpButtonKeyDown(t))})("keyup",function(){h(e);let t=s();return f(t.onUpButtonKeyUp())}),b(1,nt,1,2,"span",12)(2,at,3,2,"ng-container",2),S()}if(i&2){let e=s();v(e.cn(e.cx("incrementButton"),e.incrementButtonClass)),l("pBind",e.ptm("incrementButton")),E("disabled",e.$disabled()?"":void 0)("aria-hidden",!0)("data-p",e.dataP),m(),l("ngIf",e.incrementButtonIcon),m(),l("ngIf",!e.incrementButtonIcon)}}function st(i,a){if(i&1&&B(0,"span",13),i&2){let e=s(2);l("pBind",e.ptm("decrementButtonIcon"))("ngClass",e.decrementButtonIcon)}}function lt(i,a){if(i&1&&(I(),B(0,"svg",17)),i&2){let e=s(3);l("pBind",e.ptm("decrementButtonIcon"))}}function pt(i,a){}function ct(i,a){i&1&&b(0,pt,0,0,"ng-template")}function dt(i,a){if(i&1&&(R(0),b(1,lt,1,1,"svg",16)(2,ct,1,0,null,9),L()),i&2){let e=s(2);m(),l("ngIf",!e.decrementButtonIconTemplate&&!e._decrementButtonIconTemplate),m(),l("ngTemplateOutlet",e.decrementButtonIconTemplate||e._decrementButtonIconTemplate)}}function mt(i,a){if(i&1){let e=U();V(0,"button",11),y("mousedown",function(t){h(e);let r=s();return f(r.onDownButtonMouseDown(t))})("mouseup",function(){h(e);let t=s();return f(t.onDownButtonMouseUp())})("mouseleave",function(){h(e);let t=s();return f(t.onDownButtonMouseLeave())})("keydown",function(t){h(e);let r=s();return f(r.onDownButtonKeyDown(t))})("keyup",function(){h(e);let t=s();return f(t.onDownButtonKeyUp())}),b(1,st,1,2,"span",12)(2,dt,3,2,"ng-container",2),S()}if(i&2){let e=s();v(e.cn(e.cx("decrementButton"),e.decrementButtonClass)),l("pBind",e.ptm("decrementButton")),E("disabled",e.$disabled()?"":void 0)("aria-hidden",!0)("data-p",e.dataP),m(),l("ngIf",e.decrementButtonIcon),m(),l("ngIf",!e.decrementButtonIcon)}}var ht=`
    ${De}

    /* For PrimeNG */
    p-inputNumber.ng-invalid.ng-dirty > .p-inputtext,
    p-input-number.ng-invalid.ng-dirty > .p-inputtext,
    p-inputnumber.ng-invalid.ng-dirty > .p-inputtext {
        border-color: dt('inputtext.invalid.border.color');
    }

    p-inputNumber.ng-invalid.ng-dirty > .p-inputtext:enabled:focus,
    p-input-number.ng-invalid.ng-dirty > .p-inputtext:enabled:focus,
    p-inputnumber.ng-invalid.ng-dirty > .p-inputtext:enabled:focus {
        border-color: dt('inputtext.focus.border.color');
    }

    p-inputNumber.ng-invalid.ng-dirty > .p-inputtext::placeholder,
    p-input-number.ng-invalid.ng-dirty > .p-inputtext::placeholder,
    p-inputnumber.ng-invalid.ng-dirty > .p-inputtext::placeholder {
        color: dt('inputtext.invalid.placeholder.color');
    }
`,ft={root:({instance:i})=>["p-inputnumber p-component p-inputwrapper",{"p-inputwrapper-filled":i.$filled()||i.allowEmpty===!1,"p-inputwrapper-focus":i.focused,"p-inputnumber-stacked":i.showButtons&&i.buttonLayout==="stacked","p-inputnumber-horizontal":i.showButtons&&i.buttonLayout==="horizontal","p-inputnumber-vertical":i.showButtons&&i.buttonLayout==="vertical","p-inputnumber-fluid":i.hasFluid,"p-invalid":i.invalid()}],pcInputText:"p-inputnumber-input",buttonGroup:"p-inputnumber-button-group",incrementButton:({instance:i})=>["p-inputnumber-button p-inputnumber-increment-button",{"p-disabled":i.showButtons&&i.max()!=null&&i.maxlength()}],decrementButton:({instance:i})=>["p-inputnumber-button p-inputnumber-decrement-button",{"p-disabled":i.showButtons&&i.min()!=null&&i.minlength()}],clearIcon:"p-inputnumber-clear-icon"},Ee=(()=>{class i extends be{name="inputnumber";style=ht;classes=ft;static \u0275fac=(()=>{let e;return function(t){return(e||(e=M(i)))(t||i)}})();static \u0275prov=J({token:i,factory:i.\u0275fac})}return i})();var Ve=new te("INPUTNUMBER_INSTANCE"),_t={provide:Y,useExisting:K(()=>Se),multi:!0},Se=(()=>{class i extends we{injector;componentName="InputNumber";$pcInputNumber=N(Ve,{optional:!0,skipSelf:!0})??void 0;_componentStyle=N(Ee);bindDirectiveInstance=N(G,{self:!0});onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptms(["host","root"]))}showButtons=!1;format=!0;buttonLayout="stacked";inputId;styleClass;placeholder;tabindex;title;ariaLabelledBy;ariaDescribedBy;ariaLabel;ariaRequired;autocomplete;incrementButtonClass;decrementButtonClass;incrementButtonIcon;decrementButtonIcon;readonly;allowEmpty=!0;locale;localeMatcher;mode="decimal";currency;currencyDisplay;useGrouping=!0;minFractionDigits;maxFractionDigits;prefix;suffix;inputStyle;inputStyleClass;showClear=!1;autofocus;onInput=new k;onFocus=new k;onBlur=new k;onKeyDown=new k;onClear=new k;clearIconTemplate;incrementButtonIconTemplate;decrementButtonIconTemplate;templates;input;_clearIconTemplate;_incrementButtonIconTemplate;_decrementButtonIconTemplate;value;focused;initialized;groupChar="";prefixChar="";suffixChar="";isSpecialChar;timer;lastValue;_numeral;numberFormat;_decimal;_decimalChar="";_group;_minusSign;_currency;_prefix;_suffix;_index;ngControl=null;constructor(e){super(),this.injector=e}onChanges(e){["locale","localeMatcher","mode","currency","currencyDisplay","useGrouping","minFractionDigits","maxFractionDigits","prefix","suffix"].some(t=>!!e[t])&&this.updateConstructParser()}onInit(){this.ngControl=this.injector.get(ye,null,{optional:!0}),this.constructParser(),this.initialized=!0}onAfterContentInit(){this.templates.forEach(e=>{switch(e.getType()){case"clearicon":this._clearIconTemplate=e.template;break;case"incrementbuttonicon":this._incrementButtonIconTemplate=e.template;break;case"decrementbuttonicon":this._decrementButtonIconTemplate=e.template;break}})}getOptions(){let e=(o,u,p)=>{if(!(o==null||isNaN(o)||!isFinite(o)))return Math.max(u,Math.min(p,Math.floor(o)))},n=e(this.minFractionDigits,0,20),t=e(this.maxFractionDigits,0,100),r=n!=null&&t!=null&&n>t?t:n;return{localeMatcher:this.localeMatcher,style:this.mode,currency:this.currency,currencyDisplay:this.currencyDisplay,useGrouping:this.useGrouping,minimumFractionDigits:r,maximumFractionDigits:t}}constructParser(){let e=this.getOptions(),n=Object.fromEntries(Object.entries(e).filter(([o,u])=>u!==void 0));this.numberFormat=new Intl.NumberFormat(this.locale,n);let t=[...new Intl.NumberFormat(this.locale,{useGrouping:!1}).format(9876543210)].reverse(),r=new Map(t.map((o,u)=>[o,u]));this._numeral=new RegExp(`[${t.join("")}]`,"g"),this._group=this.getGroupingExpression(),this._minusSign=this.getMinusSignExpression(),this._currency=this.getCurrencyExpression(),this._decimal=this.getDecimalExpression(),this._decimalChar=this.getDecimalChar(),this._suffix=this.getSuffixExpression(),this._prefix=this.getPrefixExpression(),this._index=o=>r.get(o)}updateConstructParser(){this.initialized&&this.constructParser()}escapeRegExp(e){return e.replace(/[-[\]{}()*+?.,\\^$|#\s]/g,"\\$&")}getDecimalExpression(){let e=this.getDecimalChar();return new RegExp(`[${e}]`,"g")}getDecimalChar(){return new Intl.NumberFormat(this.locale,z(O({},this.getOptions()),{useGrouping:!1})).format(1.1).replace(this._currency,"").trim().replace(this._numeral,"")}getGroupingExpression(){let e=new Intl.NumberFormat(this.locale,{useGrouping:!0});return this.groupChar=e.format(1e6).trim().replace(this._numeral,"").charAt(0),new RegExp(`[${this.groupChar}]`,"g")}getMinusSignExpression(){let e=new Intl.NumberFormat(this.locale,{useGrouping:!1});return new RegExp(`[${e.format(-1).trim().replace(this._numeral,"")}]`,"g")}getCurrencyExpression(){if(this.currency){let e=new Intl.NumberFormat(this.locale,{style:"currency",currency:this.currency,currencyDisplay:this.currencyDisplay,minimumFractionDigits:0,maximumFractionDigits:0});return new RegExp(`[${e.format(1).replace(/\s/g,"").replace(this._numeral,"").replace(this._group,"")}]`,"g")}return new RegExp("[]","g")}getPrefixExpression(){if(this.prefix)this.prefixChar=this.prefix;else{let e=new Intl.NumberFormat(this.locale,{style:this.mode,currency:this.currency,currencyDisplay:this.currencyDisplay});this.prefixChar=e.format(1).split("1")[0]}return new RegExp(`${this.escapeRegExp(this.prefixChar||"")}`,"g")}getSuffixExpression(){if(this.suffix)this.suffixChar=this.suffix;else{let e=new Intl.NumberFormat(this.locale,{style:this.mode,currency:this.currency,currencyDisplay:this.currencyDisplay,minimumFractionDigits:0,maximumFractionDigits:0});this.suffixChar=e.format(1).split("1")[1]}return new RegExp(`${this.escapeRegExp(this.suffixChar||"")}`,"g")}formatValue(e){if(e!=null){if(e==="-")return e;if(this.format){let t=new Intl.NumberFormat(this.locale,this.getOptions()).format(e);return this.prefix&&e!=this.prefix&&(t=this.prefix+t),this.suffix&&e!=this.suffix&&(t=t+this.suffix),t}return e.toString()}return""}parseValue(e){let n=this._suffix?new RegExp(this._suffix,""):/(?:)/,t=this._prefix?new RegExp(this._prefix,""):/(?:)/,r=this._currency?new RegExp(this._currency,""):/(?:)/,o=e.replace(n,"").replace(t,"").trim().replace(/\s/g,"").replace(r,"").replace(this._group,"").replace(this._minusSign,"-").replace(this._decimal,".").replace(this._numeral,this._index);if(o){if(o==="-")return o;let u=+o;return isNaN(u)?null:u}return null}repeat(e,n,t){if(this.readonly)return;let r=n||500;this.clearTimer(),this.timer=setTimeout(()=>{this.repeat(e,40,t)},r),this.spin(e,t)}spin(e,n){let t=(this.step()??1)*n,r=this.parseValue(this.input?.nativeElement.value)||0,o=this.validateValue(r+t),u=this.maxlength();u&&u<this.formatValue(o).length||(this.updateInput(o,null,"spin",null),this.updateModel(e,o),this.handleOnInput(e,r,o))}clear(){this.value=null,this.onModelChange(this.value),this.onClear.emit()}onUpButtonMouseDown(e){if(e.button===2){this.clearTimer();return}this.$disabled()||(this.input?.nativeElement.focus(),this.repeat(e,null,1),e.preventDefault())}onUpButtonMouseUp(){this.$disabled()||this.clearTimer()}onUpButtonMouseLeave(){this.$disabled()||this.clearTimer()}onUpButtonKeyDown(e){(e.keyCode===32||e.keyCode===13)&&this.repeat(e,null,1)}onUpButtonKeyUp(){this.$disabled()||this.clearTimer()}onDownButtonMouseDown(e){if(e.button===2){this.clearTimer();return}this.$disabled()||(this.input?.nativeElement.focus(),this.repeat(e,null,-1),e.preventDefault())}onDownButtonMouseUp(){this.$disabled()||this.clearTimer()}onDownButtonMouseLeave(){this.$disabled()||this.clearTimer()}onDownButtonKeyUp(){this.$disabled()||this.clearTimer()}onDownButtonKeyDown(e){(e.keyCode===32||e.keyCode===13)&&this.repeat(e,null,-1)}onUserInput(e){this.readonly||(this.isSpecialChar&&(e.target.value=this.lastValue),this.isSpecialChar=!1)}onInputKeyDown(e){if(this.readonly)return;if(this.lastValue=e.target.value,e.shiftKey||e.altKey){this.isSpecialChar=!0;return}let n=e.target.selectionStart,t=e.target.selectionEnd,r=e.target.value,o=null;switch(e.altKey&&e.preventDefault(),e.key){case"ArrowUp":this.spin(e,1),e.preventDefault();break;case"ArrowDown":this.spin(e,-1),e.preventDefault();break;case"ArrowLeft":for(let u=n;u<=r.length;u++){let p=u===0?0:u-1;if(this.isNumeralChar(r.charAt(p))){this.input.nativeElement.setSelectionRange(u,u);break}}break;case"ArrowRight":for(let u=t;u>=0;u--)if(this.isNumeralChar(r.charAt(u))){this.input.nativeElement.setSelectionRange(u,u);break}break;case"Tab":case"Enter":o=this.validateValue(this.parseValue(this.input.nativeElement.value)),this.input.nativeElement.value=this.formatValue(o),this.input.nativeElement.setAttribute("aria-valuenow",o),this.updateModel(e,o);break;case"Backspace":{if(e.preventDefault(),n===t){if(n==1&&this.prefix||n==r.length&&this.suffix)break;let u=r.charAt(n-1),{decimalCharIndex:p,decimalCharIndexWithoutPrefix:d}=this.getDecimalCharIndexes(r);if(this.isNumeralChar(u)){let c=this.getDecimalLength(r);if(this._group.test(u))this._group.lastIndex=0,o=r.slice(0,n-2)+r.slice(n-1);else if(this._decimal.test(u))this._decimal.lastIndex=0,c?this.input?.nativeElement.setSelectionRange(n-1,n-1):o=r.slice(0,n-1)+r.slice(n);else if(p>0&&n>p){let g=this.isDecimalMode()&&(this.minFractionDigits||0)<c?"":"0";o=r.slice(0,n-1)+g+r.slice(n)}else d===1?(o=r.slice(0,n-1)+"0"+r.slice(n),o=this.parseValue(o)>0?o:""):o=r.slice(0,n-1)+r.slice(n)}else this.mode==="currency"&&this._currency&&u.search(this._currency)!=-1&&(o=r.slice(1));this.updateValue(e,o,null,"delete-single")}else o=this.deleteRange(r,n,t),this.updateValue(e,o,null,"delete-range");break}case"Delete":if(e.preventDefault(),n===t){if(n==0&&this.prefix||n==r.length-1&&this.suffix)break;let u=r.charAt(n),{decimalCharIndex:p,decimalCharIndexWithoutPrefix:d}=this.getDecimalCharIndexes(r);if(this.isNumeralChar(u)){let c=this.getDecimalLength(r);if(this._group.test(u))this._group.lastIndex=0,o=r.slice(0,n)+r.slice(n+2);else if(this._decimal.test(u))this._decimal.lastIndex=0,c?this.input?.nativeElement.setSelectionRange(n+1,n+1):o=r.slice(0,n)+r.slice(n+1);else if(p>0&&n>p){let g=this.isDecimalMode()&&(this.minFractionDigits||0)<c?"":"0";o=r.slice(0,n)+g+r.slice(n+1)}else d===1?(o=r.slice(0,n)+"0"+r.slice(n+1),o=this.parseValue(o)>0?o:""):o=r.slice(0,n)+r.slice(n+1)}this.updateValue(e,o,null,"delete-back-single")}else o=this.deleteRange(r,n,t),this.updateValue(e,o,null,"delete-range");break;case"Home":this.min()&&(this.updateModel(e,this.min()),e.preventDefault());break;case"End":this.max()&&(this.updateModel(e,this.max()),e.preventDefault());break;default:break}this.onKeyDown.emit(e)}onInputKeyPress(e){if(this.readonly)return;let n=e.which||e.keyCode,t=String.fromCharCode(n),r=this.isDecimalSign(t),o=this.isMinusSign(t);n!=13&&e.preventDefault(),!r&&e.code==="NumpadDecimal"&&(r=!0,t=this._decimalChar,n=t.charCodeAt(0));let{value:u,selectionStart:p,selectionEnd:d}=this.input.nativeElement,c=this.parseValue(u+t),g=c!=null?c.toString():"",D=u.substring(p,d),_=this.parseValue(D),C=_!=null?_.toString():"";if(p!==d&&C.length>0){this.insert(e,t,{isDecimalSign:r,isMinusSign:o});return}let x=this.maxlength();x&&g.length>x||(48<=n&&n<=57||o||r)&&this.insert(e,t,{isDecimalSign:r,isMinusSign:o})}onPaste(e){if(!this.$disabled()&&!this.readonly){e.preventDefault();let n=(e.clipboardData||this.document.defaultView.clipboardData).getData("Text");if(this.inputId==="integeronly"&&/[^\d-]/.test(n))return;if(n){this.maxlength()&&(n=n.toString().substring(0,this.maxlength()));let t=this.parseValue(n);t!=null&&this.insert(e,t.toString())}}}allowMinusSign(){let e=this.min();return e==null||e<0}isMinusSign(e){return this._minusSign.test(e)||e==="-"?(this._minusSign.lastIndex=0,!0):!1}isDecimalSign(e){return this._decimal.test(e)?(this._decimal.lastIndex=0,!0):!1}isDecimalMode(){return this.mode==="decimal"}getDecimalCharIndexes(e){let n=e.search(this._decimal);this._decimal.lastIndex=0;let r=e.replace(this._prefix,"").trim().replace(/\s/g,"").replace(this._currency,"").search(this._decimal);return this._decimal.lastIndex=0,{decimalCharIndex:n,decimalCharIndexWithoutPrefix:r}}getCharIndexes(e){let n=e.search(this._decimal);this._decimal.lastIndex=0;let t=e.search(this._minusSign);this._minusSign.lastIndex=0;let r=e.search(this._suffix);this._suffix.lastIndex=0;let o=e.search(this._currency);return this._currency.lastIndex=0,{decimalCharIndex:n,minusCharIndex:t,suffixCharIndex:r,currencyCharIndex:o}}insert(e,n,t={isDecimalSign:!1,isMinusSign:!1}){let r=n.search(this._minusSign);if(this._minusSign.lastIndex=0,!this.allowMinusSign()&&r!==-1)return;let o=this.input?.nativeElement.selectionStart,u=this.input?.nativeElement.selectionEnd,p=this.input?.nativeElement.value.trim(),{decimalCharIndex:d,minusCharIndex:c,suffixCharIndex:g,currencyCharIndex:D}=this.getCharIndexes(p),_;if(t.isMinusSign)o===0&&(_=p,(c===-1||u!==0)&&(_=this.insertText(p,n,0,u)),this.updateValue(e,_,n,"insert"));else if(t.isDecimalSign)d>0&&o===d?this.updateValue(e,p,n,"insert"):d>o&&d<u?(_=this.insertText(p,n,o,u),this.updateValue(e,_,n,"insert")):d===-1&&this.maxFractionDigits&&(_=this.insertText(p,n,o,u),this.updateValue(e,_,n,"insert"));else{let C=this.numberFormat.resolvedOptions().maximumFractionDigits,x=o!==u?"range-insert":"insert";if(d>0&&o>d){if(o+n.length-(d+1)<=C){let w=D>=o?D-1:g>=o?g:p.length;_=p.slice(0,o)+n+p.slice(o+n.length,w)+p.slice(w),this.updateValue(e,_,n,x)}}else _=this.insertText(p,n,o,u),this.updateValue(e,_,n,x)}}insertText(e,n,t,r){if((n==="."?n:n.split(".")).length===2){let u=e.slice(t,r).search(this._decimal);return this._decimal.lastIndex=0,u>0?e.slice(0,t)+this.formatValue(n)+e.slice(r):e||this.formatValue(n)}else return r-t===e.length?this.formatValue(n):t===0?n+e.slice(r):r===e.length?e.slice(0,t)+n:e.slice(0,t)+n+e.slice(r)}deleteRange(e,n,t){let r;return t-n===e.length?r="":n===0?r=e.slice(t):t===e.length?r=e.slice(0,n):r=e.slice(0,n)+e.slice(t),r}initCursor(){let e=this.input?.nativeElement.selectionStart,n=this.input?.nativeElement.selectionEnd,t=this.input?.nativeElement.value,r=t.length,o=null,u=(this.prefixChar||"").length;t=t.replace(this._prefix,""),(e===n||e!==0||n<u)&&(e-=u);let p=t.charAt(e);if(this.isNumeralChar(p))return e+u;let d=e-1;for(;d>=0;)if(p=t.charAt(d),this.isNumeralChar(p)){o=d+u;break}else d--;if(o!==null)this.input?.nativeElement.setSelectionRange(o+1,o+1);else{for(d=e;d<r;)if(p=t.charAt(d),this.isNumeralChar(p)){o=d+u;break}else d++;o!==null&&this.input?.nativeElement.setSelectionRange(o,o)}return o||0}onInputClick(){let e=this.input?.nativeElement.value;!this.readonly&&e!==fe()&&this.initCursor()}isNumeralChar(e){return e.length===1&&(this._numeral.test(e)||this._decimal.test(e)||this._group.test(e)||this._minusSign.test(e))?(this.resetRegex(),!0):!1}resetRegex(){this._numeral.lastIndex=0,this._decimal.lastIndex=0,this._group.lastIndex=0,this._minusSign.lastIndex=0}updateValue(e,n,t,r){let o=this.input?.nativeElement.value,u=null;n!=null&&(u=this.parseValue(n),u=!u&&!this.allowEmpty?0:u,this.updateInput(u,t,r,n),this.handleOnInput(e,o,u))}handleOnInput(e,n,t){this.isValueChanged(n,t)&&(this.input.nativeElement.value=this.formatValue(t),this.input?.nativeElement.setAttribute("aria-valuenow",t),this.updateModel(e,t),this.onInput.emit({originalEvent:e,value:t,formattedValue:n}))}isValueChanged(e,n){if(n===null&&e!==null)return!0;if(n!=null){let t=typeof e=="string"?this.parseValue(e):e;return n!==t}return!1}validateValue(e){if(e==="-"||e==null)return null;let n=this.min(),t=this.max();return n!=null&&e<n?this.min():t!=null&&e>t?t:e}updateInput(e,n,t,r){n=n||"";let o=this.input?.nativeElement.value,u=this.formatValue(e),p=o.length;if(u!==r&&(u=this.concatValues(u,r)),p===0){this.input.nativeElement.value=u,this.input.nativeElement.setSelectionRange(0,0);let c=this.initCursor()+n.length;this.input.nativeElement.setSelectionRange(c,c)}else{let d=this.input.nativeElement.selectionStart,c=this.input.nativeElement.selectionEnd,g=this.maxlength();if(g&&u.length>g&&(u=u.slice(0,g),d=Math.min(d,g),c=Math.min(c,g)),g&&g<u.length)return;this.input.nativeElement.value=u;let D=u.length;if(t==="range-insert"){let _=this.parseValue((o||"").slice(0,d)),x=(_!==null?_.toString():"").split("").join(`(${this.groupChar})?`),w=new RegExp(x,"g");w.test(u);let ke=n.split("").join(`(${this.groupChar})?`),Z=new RegExp(ke,"g");Z.test(u.slice(w.lastIndex)),c=w.lastIndex+Z.lastIndex,this.input.nativeElement.setSelectionRange(c,c)}else if(D===p)t==="insert"||t==="delete-back-single"?this.input.nativeElement.setSelectionRange(c+1,c+1):t==="delete-single"?this.input.nativeElement.setSelectionRange(c-1,c-1):(t==="delete-range"||t==="spin")&&this.input.nativeElement.setSelectionRange(c,c);else if(t==="delete-back-single"){let _=o.charAt(c-1),C=o.charAt(c),x=p-D,w=this._group.test(C);w&&x===1?c+=1:!w&&this.isNumeralChar(_)&&(c+=-1*x+1),this._group.lastIndex=0,this.input.nativeElement.setSelectionRange(c,c)}else if(o==="-"&&t==="insert"){this.input.nativeElement.setSelectionRange(0,0);let C=this.initCursor()+n.length+1;this.input.nativeElement.setSelectionRange(C,C)}else c=c+(D-p),this.input.nativeElement.setSelectionRange(c,c)}this.input.nativeElement.setAttribute("aria-valuenow",e)}concatValues(e,n){if(e&&n){let t=n.search(this._decimal);return this._decimal.lastIndex=0,this.suffixChar?t!==-1?e.replace(this.suffixChar,"").split(this._decimal)[0]+n.replace(this.suffixChar,"").slice(t)+this.suffixChar:e:t!==-1?e.split(this._decimal)[0]+n.slice(t):e}return e}getDecimalLength(e){if(e){let n=e.split(this._decimal);if(n.length===2)return n[1].replace(this._suffix,"").trim().replace(/\s/g,"").replace(this._currency,"").length}return 0}onInputFocus(e){this.focused=!0,this.onFocus.emit(e)}onInputBlur(e){this.focused=!1;let n=this.validateValue(this.parseValue(this.input.nativeElement.value)),t=n?.toString();this.input.nativeElement.value=this.formatValue(t),this.input.nativeElement.setAttribute("aria-valuenow",t),this.updateModel(e,n),this.onModelTouched(),this.onBlur.emit(e)}formattedValue(){let e=!this.value&&!this.allowEmpty?0:this.value;return this.formatValue(e)}updateModel(e,n){let t=this.ngControl?.control?.updateOn==="blur";this.value!==n?(this.value=n,t&&this.focused||this.onModelChange(n)):t&&this.onModelChange(n)}writeControlValue(e,n){this.value=e&&Number(e),n(e),this.cd.markForCheck()}clearTimer(){this.timer&&clearInterval(this.timer)}get dataP(){return this.cn({invalid:this.invalid(),disabled:this.$disabled(),focus:this.focused,fluid:this.hasFluid,filled:this.$variant()==="filled",empty:!this.$filled(),[this.size()]:this.size(),[this.buttonLayout]:this.showButtons&&this.buttonLayout})}static \u0275fac=function(n){return new(n||i)(re(ne))};static \u0275cmp=F({type:i,selectors:[["p-inputNumber"],["p-inputnumber"],["p-input-number"]],contentQueries:function(n,t,r){if(n&1&&se(r,Re,4)(r,Le,4)(r,Ue,4)(r,_e,4),n&2){let o;$(o=P())&&(t.clearIconTemplate=o.first),$(o=P())&&(t.incrementButtonIconTemplate=o.first),$(o=P())&&(t.decrementButtonIconTemplate=o.first),$(o=P())&&(t.templates=o)}},viewQuery:function(n,t){if(n&1&&le($e,5),n&2){let r;$(r=P())&&(t.input=r.first)}},hostVars:3,hostBindings:function(n,t){n&2&&(E("data-p",t.dataP),v(t.cn(t.cx("root"),t.styleClass)))},inputs:{showButtons:[2,"showButtons","showButtons",T],format:[2,"format","format",T],buttonLayout:"buttonLayout",inputId:"inputId",styleClass:"styleClass",placeholder:"placeholder",tabindex:[2,"tabindex","tabindex",H],title:"title",ariaLabelledBy:"ariaLabelledBy",ariaDescribedBy:"ariaDescribedBy",ariaLabel:"ariaLabel",ariaRequired:[2,"ariaRequired","ariaRequired",T],autocomplete:"autocomplete",incrementButtonClass:"incrementButtonClass",decrementButtonClass:"decrementButtonClass",incrementButtonIcon:"incrementButtonIcon",decrementButtonIcon:"decrementButtonIcon",readonly:[2,"readonly","readonly",T],allowEmpty:[2,"allowEmpty","allowEmpty",T],locale:"locale",localeMatcher:"localeMatcher",mode:"mode",currency:"currency",currencyDisplay:"currencyDisplay",useGrouping:[2,"useGrouping","useGrouping",T],minFractionDigits:[2,"minFractionDigits","minFractionDigits",e=>H(e,void 0)],maxFractionDigits:[2,"maxFractionDigits","maxFractionDigits",e=>H(e,void 0)],prefix:"prefix",suffix:"suffix",inputStyle:"inputStyle",inputStyleClass:"inputStyleClass",showClear:[2,"showClear","showClear",T],autofocus:[2,"autofocus","autofocus",T]},outputs:{onInput:"onInput",onFocus:"onFocus",onBlur:"onBlur",onKeyDown:"onKeyDown",onClear:"onClear"},features:[q([_t,Ee,{provide:Ve,useExisting:i},{provide:ge,useExisting:i}]),ue([G]),A],decls:6,vars:38,consts:[["input",""],["pInputText","","role","spinbutton","inputmode","decimal",3,"input","keydown","keypress","paste","click","focus","blur","value","ngStyle","variant","invalid","pSize","pt","unstyled","pAutoFocus","fluid"],[4,"ngIf"],[3,"pBind","class",4,"ngIf"],["type","button","tabindex","-1",3,"pBind","class","mousedown","mouseup","mouseleave","keydown","keyup",4,"ngIf"],["data-p-icon","times",3,"pBind","class","click",4,"ngIf"],[3,"pBind","class","click",4,"ngIf"],["data-p-icon","times",3,"click","pBind"],[3,"click","pBind"],[4,"ngTemplateOutlet"],[3,"pBind"],["type","button","tabindex","-1",3,"mousedown","mouseup","mouseleave","keydown","keyup","pBind"],[3,"pBind","ngClass",4,"ngIf"],[3,"pBind","ngClass"],["data-p-icon","angle-up",3,"pBind",4,"ngIf"],["data-p-icon","angle-up",3,"pBind"],["data-p-icon","angle-down",3,"pBind",4,"ngIf"],["data-p-icon","angle-down",3,"pBind"]],template:function(n,t){n&1&&(V(0,"input",1,0),y("input",function(o){return t.onUserInput(o)})("keydown",function(o){return t.onInputKeyDown(o)})("keypress",function(o){return t.onInputKeyPress(o)})("paste",function(o){return t.onPaste(o)})("click",function(){return t.onInputClick()})("focus",function(o){return t.onInputFocus(o)})("blur",function(o){return t.onInputBlur(o)}),S(),b(2,Ke,3,2,"ng-container",2)(3,tt,7,20,"span",3)(4,ut,3,8,"button",4)(5,mt,3,8,"button",4)),n&2&&(v(t.cn(t.cx("pcInputText"),t.inputStyleClass)),l("value",t.formattedValue())("ngStyle",t.inputStyle)("variant",t.$variant())("invalid",t.invalid())("pSize",t.size())("pt",t.ptm("pcInputText"))("unstyled",t.unstyled())("pAutoFocus",t.autofocus)("fluid",t.hasFluid),E("id",t.inputId)("aria-valuemin",t.min())("aria-valuemax",t.max())("aria-valuenow",t.value)("placeholder",t.placeholder)("aria-label",t.ariaLabel)("aria-labelledby",t.ariaLabelledBy)("aria-describedby",t.ariaDescribedBy)("title",t.title)("size",t.inputSize())("name",t.name())("autocomplete",t.autocomplete)("maxlength",t.maxlength())("minlength",t.minlength())("tabindex",t.tabindex)("aria-required",t.ariaRequired)("min",t.min())("max",t.max())("step",t.step()??1)("required",t.required()?"":void 0)("readonly",t.readonly?"":void 0)("disabled",t.$disabled()?"":void 0)("data-p",t.dataP),m(2),l("ngIf",t.buttonLayout!="vertical"&&t.showClear&&t.value),m(),l("ngIf",t.showButtons&&t.buttonLayout==="stacked"),m(),l("ngIf",t.showButtons&&t.buttonLayout!=="stacked"),m(),l("ngIf",t.showButtons&&t.buttonLayout!=="stacked"))},dependencies:[he,pe,ce,me,de,Ce,ve,Ie,Te,Be,Q,xe,G],encapsulation:2,changeDetection:0})}return i})(),en=(()=>{class i{static \u0275fac=function(n){return new(n||i)};static \u0275mod=oe({type:i});static \u0275inj=ee({imports:[Se,Q,Q]})}return i})();var bt=/^-?\d*\.?\d*$/,Ne=class i{constructor(){this.el=N(ie).nativeElement;this.lastText="";this.onChange=()=>{};this.onTouched=()=>{}}writeValue(a){this.setText(a==null?"":String(a))}registerOnChange(a){this.onChange=a}registerOnTouched(a){this.onTouched=a}setDisabledState(a){this.el.disabled=a}onInput(){let a=this.el.value.replace(",",".");if(!bt.test(a)){this.setText(this.lastText);return}this.setText(a),this.onChange(this.parsed())}onBlur(){let a=this.parsed();this.setText(a===null?"":String(a)),this.onTouched()}parsed(){let a=Number.parseFloat(this.lastText);return Number.isFinite(a)?a:null}setText(a){this.lastText=a,this.el.value=a}static{this.\u0275fac=function(e){return new(e||i)}}static{this.\u0275dir=ae({type:i,selectors:[["input","appDecimalInput",""]],hostAttrs:["inputmode","decimal"],hostBindings:function(e,n){e&1&&y("input",function(){return n.onInput()})("blur",function(){return n.onBlur()})},features:[q([{provide:Y,useExisting:K(()=>i),multi:!0}])]})}};var gt=new Set(["int","scene"]),xt=new Set(["float","num"]);function pn(i,a,e){if(a)return"select";let n=(i??"").split("(")[0];return n==="bool"?e==="toggle"?"toggle":"select":n==="list"?"list":n==="dict"?"dict":n==="password"?"password":gt.has(n)?"number":xt.has(n)?"decimal":"text"}function cn(i,a){if(a&&a.length>0)return a.map(e=>({label:String(e),value:e}));if((i??"").split("(")[0]==="bool")return[{label:"true",value:!0},{label:"false",value:!1}]}export{Be as a,Te as b,Me as c,It as d,yt as e,Se as f,en as g,Ne as h,pn as i,cn as j};
