import{a as re,c as de,f as Et}from"./chunk-2HIXAOWN.js";import{a as le,j as he}from"./chunk-MSJFQPAD.js";import{e as Jt,u as ae,w as ce}from"./chunk-EI3ITX33.js";import{Ca as se,J as te,Ka as zt,L as ee,La as j,M as ie,Oa as $,Qa as W,Ra as et,Sa as b,Ta as gt,Ua as it,j as Zt,ja as ne,k as Xt,l as St,m as Kt,n as Tt,oa as at,r as tt,ua as ct,v as Pt,wa as Lt,xa as oe}from"./chunk-JYMX7FOM.js";import{$b as V,Fb as a,G as q,Gb as st,Gc as vt,Hb as rt,Ib as lt,Jb as Bt,Kb as Nt,Lb as G,Lc as J,Mb as N,Nb as P,Ob as pt,Pb as Wt,Pc as w,Qb as Ut,Tb as ut,U as Rt,V as M,Vb as v,W as Z,Wa as m,Wb as mt,Xb as ft,Y as R,Yb as Ct,Yc as F,Zb as It,Zc as Yt,_ as p,_b as D,a as yt,b as Vt,db as $t,dc as _t,ea as At,ec as Qt,fa as Ht,ga as T,gc as kt,hc as y,ib as k,jb as K,kb as ht,la as X,ma as jt,mb as A,nb as _,o as Q,ob as C,pa as dt,sa as Ft,tc as H,u as Y,ua as u,uc as qt,vc as wt,wb as z,wc as bt,xc as Gt}from"./chunk-BDB7QD2D.js";var pe=class e{constructor(){this.http=p(Jt);this.appConfig=p(ae);this.log=p(ce)}CheckEvalData(r){let i=this.appConfig.apiUrl+"services/evalcheck/";return this.http.put(i,r).pipe(Y(n=>{let o=n;if(o)return o;this.log.log("ServicesApiService.CheckEvalData","fail: undefined result")}),q(n=>(this.log.error("ServicesApiService.CheckEvalData: Could not set plugin config data - "+n.error.error),Q({}))))}CheckYamlText(r){let i=this.appConfig.apiUrl+"services/yamlcheck/";return this.http.put(i,r,{responseType:"text"}).pipe(Y(n=>{let o=n;return o||(this.log.log("ServicesApiService.CheckYamlText","fail: undefined result"),"")}),q(n=>(this.log.error("ServicesApiService.CheckYamlText: Could not set plugin config data - "+n.error.error),Q({}))))}ConvertToYamlText(r){let i=this.appConfig.apiUrl+"services/yamlconvert/";return this.http.put(i,r,{responseType:"text"}).pipe(Y(n=>{let o=n;if(o)return o;this.log.log("ServicesApiService.ConvertToYamlText","fail: undefined result")}),q(n=>(this.log.error("ServicesApiService.ConvertToYamlText: Could not set plugin config data - "+n.error.error),Q({}))))}getCacheOrphans(){let t=this.appConfig.apiUrl+"services/cachecheck/";return this.http.get(t).pipe(q(i=>(this.log.error("ServicesApiService (getCacheOrphans): Could not read cache orphans data - "+i.error.error),Q({}))))}deleteCacheFile(r){let i=this.appConfig.apiUrl+"services/cachefile_delete?filename="+encodeURIComponent(r);return this.http.put(i,"xxx").pipe(Y(n=>{let o=n;if(o)return o;this.log.log("ServicesApiService.deleteCacheFile","fail: undefined result")}),q(n=>(this.log.error("ServicesApiService.deleteCacheFile: Could not set plugin config data - "+n.error.error),Q({}))))}hashPassword(r){let t=this.appConfig.apiUrl+"services/hashpassword/";return this.http.put(t,r).pipe(Y(i=>i?.hash??null),q(i=>(this.log.error("ServicesApiService.hashPassword: Could not create password hash - "+i.message),Q(null))))}checkPassword(r,t){let i=this.appConfig.apiUrl+"services/checkpassword/";return this.http.put(i,{password:r,hash:t}).pipe(Y(n=>n?.match===!0),q(n=>(this.log.error("ServicesApiService.checkPassword: Could not check password - "+n.message),Q(!1))))}generateSecret(){let r=this.appConfig.apiUrl+"services/generatesecret/";return this.http.put(r,null).pipe(Y(t=>t?.secret??null),q(t=>(this.log.error("ServicesApiService.generateSecret: Could not create secret - "+t.message),Q(null))))}static{this.\u0275fac=function(t){return new(t||e)}}static{this.\u0275prov=M({token:e,factory:e.\u0275fac,providedIn:"root"})}};var Mt=(()=>{class e extends et{modelValue=dt(void 0);$filled=J(()=>te(this.modelValue()));writeModelValue(t){this.modelValue.set(t)}static \u0275fac=(()=>{let t;return function(n){return(t||(t=u(e)))(n||e)}})();static \u0275dir=ht({type:e,features:[_]})}return e})();var ue=`
    .p-inputtext {
        font-family: inherit;
        font-feature-settings: inherit;
        font-size: 1rem;
        color: dt('inputtext.color');
        background: dt('inputtext.background');
        padding-block: dt('inputtext.padding.y');
        padding-inline: dt('inputtext.padding.x');
        border: 1px solid dt('inputtext.border.color');
        transition:
            background dt('inputtext.transition.duration'),
            color dt('inputtext.transition.duration'),
            border-color dt('inputtext.transition.duration'),
            outline-color dt('inputtext.transition.duration'),
            box-shadow dt('inputtext.transition.duration');
        appearance: none;
        border-radius: dt('inputtext.border.radius');
        outline-color: transparent;
        box-shadow: dt('inputtext.shadow');
    }

    .p-inputtext:enabled:hover {
        border-color: dt('inputtext.hover.border.color');
    }

    .p-inputtext:enabled:focus {
        border-color: dt('inputtext.focus.border.color');
        box-shadow: dt('inputtext.focus.ring.shadow');
        outline: dt('inputtext.focus.ring.width') dt('inputtext.focus.ring.style') dt('inputtext.focus.ring.color');
        outline-offset: dt('inputtext.focus.ring.offset');
    }

    .p-inputtext.p-invalid {
        border-color: dt('inputtext.invalid.border.color');
    }

    .p-inputtext.p-variant-filled {
        background: dt('inputtext.filled.background');
    }

    .p-inputtext.p-variant-filled:enabled:hover {
        background: dt('inputtext.filled.hover.background');
    }

    .p-inputtext.p-variant-filled:enabled:focus {
        background: dt('inputtext.filled.focus.background');
    }

    .p-inputtext:disabled {
        opacity: 1;
        background: dt('inputtext.disabled.background');
        color: dt('inputtext.disabled.color');
    }

    .p-inputtext::placeholder {
        color: dt('inputtext.placeholder.color');
    }

    .p-inputtext.p-invalid::placeholder {
        color: dt('inputtext.invalid.placeholder.color');
    }

    .p-inputtext-sm {
        font-size: dt('inputtext.sm.font.size');
        padding-block: dt('inputtext.sm.padding.y');
        padding-inline: dt('inputtext.sm.padding.x');
    }

    .p-inputtext-lg {
        font-size: dt('inputtext.lg.font.size');
        padding-block: dt('inputtext.lg.padding.y');
        padding-inline: dt('inputtext.lg.padding.x');
    }

    .p-inputtext-fluid {
        width: 100%;
    }
`;var De=`
    ${ue}

    /* For PrimeNG */
   .p-inputtext.ng-invalid.ng-dirty {
        border-color: dt('inputtext.invalid.border.color');
    }

    .p-inputtext.ng-invalid.ng-dirty::placeholder {
        color: dt('inputtext.invalid.placeholder.color');
    }
`,Ve={root:({instance:e})=>["p-inputtext p-component",{"p-filled":e.$filled(),"p-inputtext-sm":e.pSize==="small","p-inputtext-lg":e.pSize==="large","p-invalid":e.invalid(),"p-variant-filled":e.$variant()==="filled","p-inputtext-fluid":e.hasFluid}]},me=(()=>{class e extends ${name="inputtext";style=De;classes=Ve;static \u0275fac=(()=>{let t;return function(n){return(t||(t=u(e)))(n||e)}})();static \u0275prov=M({token:e,factory:e.\u0275fac})}return e})();var fe=new R("INPUTTEXT_INSTANCE"),rn=(()=>{class e extends Mt{componentName="InputText";hostName="";ptInputText=w();pInputTextPT=w();pInputTextUnstyled=w();bindDirectiveInstance=p(b,{self:!0});$pcInputText=p(fe,{optional:!0,skipSelf:!0})??void 0;ngControl=p(Et,{optional:!0,self:!0});pcFluid=p(he,{optional:!0,host:!0,skipSelf:!0});pSize;variant=w();fluid=w(void 0,{transform:F});invalid=w(void 0,{transform:F});$variant=J(()=>this.variant()||this.config.inputStyle()||this.config.inputVariant());_componentStyle=p(me);constructor(){super(),Ft(()=>{let t=this.ptInputText()||this.pInputTextPT();t&&this.directivePT.set(t)}),Ft(()=>{this.pInputTextUnstyled()&&this.directiveUnstyled.set(this.pInputTextUnstyled())})}onAfterViewInit(){this.writeModelValue(this.ngControl?.value??this.el.nativeElement.value),this.cd.detectChanges()}onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptm("root"))}onDoCheck(){this.writeModelValue(this.ngControl?.value??this.el.nativeElement.value)}onInput(){this.writeModelValue(this.ngControl?.value??this.el.nativeElement.value)}get hasFluid(){return this.fluid()??!!this.pcFluid}get dataP(){return this.cn({invalid:this.invalid(),fluid:this.hasFluid,filled:this.$variant()==="filled",[this.pSize]:this.pSize})}static \u0275fac=function(i){return new(i||e)};static \u0275dir=ht({type:e,selectors:[["","pInputText",""]],hostVars:3,hostBindings:function(i,n){i&1&&ut("input",function(){return n.onInput()}),i&2&&(z("data-p",n.dataP),y(n.cx("root")))},inputs:{hostName:"hostName",ptInputText:[1,"ptInputText"],pInputTextPT:[1,"pInputTextPT"],pInputTextUnstyled:[1,"pInputTextUnstyled"],pSize:"pSize",variant:[1,"variant"],fluid:[1,"fluid"],invalid:[1,"invalid"]},features:[H([me,{provide:fe,useExisting:e},{provide:W,useExisting:e}]),A([b]),_]})}return e})(),ln=(()=>{class e{static \u0275fac=function(i){return new(i||e)};static \u0275mod=K({type:e});static \u0275inj=Z({})}return e})();var Fe=["data-p-icon","blank"],dn=(()=>{class e extends it{static \u0275fac=(()=>{let t;return function(n){return(t||(t=u(e)))(n||e)}})();static \u0275cmp=k({type:e,selectors:[["","data-p-icon","blank"]],features:[_],attrs:Fe,decls:1,vars:0,consts:[["width","1","height","1","fill","currentColor","fill-opacity","0"]],template:function(i,n){i&1&&(T(),G(0,"rect",0))},encapsulation:2})}return e})();var Be=["data-p-icon","chevron-down"],un=(()=>{class e extends it{static \u0275fac=(()=>{let t;return function(n){return(t||(t=u(e)))(n||e)}})();static \u0275cmp=k({type:e,selectors:[["","data-p-icon","chevron-down"]],features:[_],attrs:Be,decls:1,vars:0,consts:[["d","M7.01744 10.398C6.91269 10.3985 6.8089 10.378 6.71215 10.3379C6.61541 10.2977 6.52766 10.2386 6.45405 10.1641L1.13907 4.84913C1.03306 4.69404 0.985221 4.5065 1.00399 4.31958C1.02276 4.13266 1.10693 3.95838 1.24166 3.82747C1.37639 3.69655 1.55301 3.61742 1.74039 3.60402C1.92777 3.59062 2.11386 3.64382 2.26584 3.75424L7.01744 8.47394L11.769 3.75424C11.9189 3.65709 12.097 3.61306 12.2748 3.62921C12.4527 3.64535 12.6199 3.72073 12.7498 3.84328C12.8797 3.96582 12.9647 4.12842 12.9912 4.30502C13.0177 4.48162 12.9841 4.662 12.8958 4.81724L7.58083 10.1322C7.50996 10.2125 7.42344 10.2775 7.32656 10.3232C7.22968 10.3689 7.12449 10.3944 7.01744 10.398Z","fill","currentColor"]],template:function(i,n){i&1&&(T(),G(0,"path",0))},encapsulation:2})}return e})();var Ne=["data-p-icon","search"],_n=(()=>{class e extends it{pathId;onInit(){this.pathId="url(#"+se()+")"}static \u0275fac=(()=>{let t;return function(n){return(t||(t=u(e)))(n||e)}})();static \u0275cmp=k({type:e,selectors:[["","data-p-icon","search"]],features:[_],attrs:Ne,decls:5,vars:2,consts:[["fill-rule","evenodd","clip-rule","evenodd","d","M2.67602 11.0265C3.6661 11.688 4.83011 12.0411 6.02086 12.0411C6.81149 12.0411 7.59438 11.8854 8.32483 11.5828C8.87005 11.357 9.37808 11.0526 9.83317 10.6803L12.9769 13.8241C13.0323 13.8801 13.0983 13.9245 13.171 13.9548C13.2438 13.985 13.3219 14.0003 13.4007 14C13.4795 14.0003 13.5575 13.985 13.6303 13.9548C13.7031 13.9245 13.7691 13.8801 13.8244 13.8241C13.9367 13.7116 13.9998 13.5592 13.9998 13.4003C13.9998 13.2414 13.9367 13.089 13.8244 12.9765L10.6807 9.8328C11.053 9.37773 11.3573 8.86972 11.5831 8.32452C11.8857 7.59408 12.0414 6.81119 12.0414 6.02056C12.0414 4.8298 11.6883 3.66579 11.0268 2.67572C10.3652 1.68564 9.42494 0.913972 8.32483 0.45829C7.22472 0.00260857 6.01418 -0.116618 4.84631 0.115686C3.67844 0.34799 2.60568 0.921393 1.76369 1.76338C0.921698 2.60537 0.348296 3.67813 0.115991 4.84601C-0.116313 6.01388 0.00291375 7.22441 0.458595 8.32452C0.914277 9.42464 1.68595 10.3649 2.67602 11.0265ZM3.35565 2.0158C4.14456 1.48867 5.07206 1.20731 6.02086 1.20731C7.29317 1.20731 8.51338 1.71274 9.41304 2.6124C10.3127 3.51206 10.8181 4.73226 10.8181 6.00457C10.8181 6.95337 10.5368 7.88088 10.0096 8.66978C9.48251 9.45868 8.73328 10.0736 7.85669 10.4367C6.98011 10.7997 6.01554 10.8947 5.08496 10.7096C4.15439 10.5245 3.2996 10.0676 2.62869 9.39674C1.95778 8.72583 1.50089 7.87104 1.31579 6.94046C1.13068 6.00989 1.22568 5.04532 1.58878 4.16874C1.95187 3.29215 2.56675 2.54292 3.35565 2.0158Z","fill","currentColor"],[3,"id"],["width","14","height","14","fill","white"]],template:function(i,n){i&1&&(T(),Bt(0,"g"),G(1,"path",0),Nt(),Bt(2,"defs")(3,"clipPath",1),G(4,"rect",2),Nt()()),i&2&&(z("clip-path",n.pathId),m(3),Ut("id",n.pathId))},encapsulation:2})}return e})();var ge=(()=>{class e extends Mt{required=w(void 0,{transform:F});invalid=w(void 0,{transform:F});disabled=w(void 0,{transform:F});name=w();_disabled=dt(!1);$disabled=J(()=>this.disabled()||this._disabled());onModelChange=()=>{};onModelTouched=()=>{};writeDisabledState(t){this._disabled.set(t)}writeControlValue(t,i){}writeValue(t){this.writeControlValue(t,this.writeModelValue.bind(this))}registerOnChange(t){this.onModelChange=t}registerOnTouched(t){this.onModelTouched=t}setDisabledState(t){this.writeDisabledState(t),this.cd.markForCheck()}static \u0275fac=(()=>{let t;return function(n){return(t||(t=u(e)))(n||e)}})();static \u0275dir=ht({type:e,inputs:{required:[1,"required"],invalid:[1,"invalid"],disabled:[1,"disabled"],name:[1,"name"]},features:[_]})}return e})();var Pe=["data-p-icon","minus"],_e=(()=>{class e extends it{static \u0275fac=(()=>{let t;return function(n){return(t||(t=u(e)))(n||e)}})();static \u0275cmp=k({type:e,selectors:[["","data-p-icon","minus"]],features:[_],attrs:Pe,decls:1,vars:0,consts:[["d","M13.2222 7.77778H0.777778C0.571498 7.77778 0.373667 7.69584 0.227806 7.54998C0.0819442 7.40412 0 7.20629 0 7.00001C0 6.79373 0.0819442 6.5959 0.227806 6.45003C0.373667 6.30417 0.571498 6.22223 0.777778 6.22223H13.2222C13.4285 6.22223 13.6263 6.30417 13.7722 6.45003C13.9181 6.5959 14 6.79373 14 7.00001C14 7.20629 13.9181 7.40412 13.7722 7.54998C13.6263 7.69584 13.4285 7.77778 13.2222 7.77778Z","fill","currentColor"]],template:function(i,n){i&1&&(T(),G(0,"path",0))},encapsulation:2})}return e})();var be=`
    .p-checkbox {
        position: relative;
        display: inline-flex;
        user-select: none;
        vertical-align: bottom;
        width: dt('checkbox.width');
        height: dt('checkbox.height');
    }

    .p-checkbox-input {
        cursor: pointer;
        appearance: none;
        position: absolute;
        inset-block-start: 0;
        inset-inline-start: 0;
        width: 100%;
        height: 100%;
        padding: 0;
        margin: 0;
        opacity: 0;
        z-index: 1;
        outline: 0 none;
        border: 1px solid transparent;
        border-radius: dt('checkbox.border.radius');
    }

    .p-checkbox-box {
        display: flex;
        justify-content: center;
        align-items: center;
        border-radius: dt('checkbox.border.radius');
        border: 1px solid dt('checkbox.border.color');
        background: dt('checkbox.background');
        width: dt('checkbox.width');
        height: dt('checkbox.height');
        transition:
            background dt('checkbox.transition.duration'),
            color dt('checkbox.transition.duration'),
            border-color dt('checkbox.transition.duration'),
            box-shadow dt('checkbox.transition.duration'),
            outline-color dt('checkbox.transition.duration');
        outline-color: transparent;
        box-shadow: dt('checkbox.shadow');
    }

    .p-checkbox-icon {
        transition-duration: dt('checkbox.transition.duration');
        color: dt('checkbox.icon.color');
        font-size: dt('checkbox.icon.size');
        width: dt('checkbox.icon.size');
        height: dt('checkbox.icon.size');
    }

    .p-checkbox:not(.p-disabled):has(.p-checkbox-input:hover) .p-checkbox-box {
        border-color: dt('checkbox.hover.border.color');
    }

    .p-checkbox-checked .p-checkbox-box {
        border-color: dt('checkbox.checked.border.color');
        background: dt('checkbox.checked.background');
    }

    .p-checkbox-checked .p-checkbox-icon {
        color: dt('checkbox.icon.checked.color');
    }

    .p-checkbox-checked:not(.p-disabled):has(.p-checkbox-input:hover) .p-checkbox-box {
        background: dt('checkbox.checked.hover.background');
        border-color: dt('checkbox.checked.hover.border.color');
    }

    .p-checkbox-checked:not(.p-disabled):has(.p-checkbox-input:hover) .p-checkbox-icon {
        color: dt('checkbox.icon.checked.hover.color');
    }

    .p-checkbox:not(.p-disabled):has(.p-checkbox-input:focus-visible) .p-checkbox-box {
        border-color: dt('checkbox.focus.border.color');
        box-shadow: dt('checkbox.focus.ring.shadow');
        outline: dt('checkbox.focus.ring.width') dt('checkbox.focus.ring.style') dt('checkbox.focus.ring.color');
        outline-offset: dt('checkbox.focus.ring.offset');
    }

    .p-checkbox-checked:not(.p-disabled):has(.p-checkbox-input:focus-visible) .p-checkbox-box {
        border-color: dt('checkbox.checked.focus.border.color');
    }

    .p-checkbox.p-invalid > .p-checkbox-box {
        border-color: dt('checkbox.invalid.border.color');
    }

    .p-checkbox.p-variant-filled .p-checkbox-box {
        background: dt('checkbox.filled.background');
    }

    .p-checkbox-checked.p-variant-filled .p-checkbox-box {
        background: dt('checkbox.checked.background');
    }

    .p-checkbox-checked.p-variant-filled:not(.p-disabled):has(.p-checkbox-input:hover) .p-checkbox-box {
        background: dt('checkbox.checked.hover.background');
    }

    .p-checkbox.p-disabled {
        opacity: 1;
    }

    .p-checkbox.p-disabled .p-checkbox-box {
        background: dt('checkbox.disabled.background');
        border-color: dt('checkbox.checked.disabled.border.color');
    }

    .p-checkbox.p-disabled .p-checkbox-box .p-checkbox-icon {
        color: dt('checkbox.icon.disabled.color');
    }

    .p-checkbox-sm,
    .p-checkbox-sm .p-checkbox-box {
        width: dt('checkbox.sm.width');
        height: dt('checkbox.sm.height');
    }

    .p-checkbox-sm .p-checkbox-icon {
        font-size: dt('checkbox.icon.sm.size');
        width: dt('checkbox.icon.sm.size');
        height: dt('checkbox.icon.sm.size');
    }

    .p-checkbox-lg,
    .p-checkbox-lg .p-checkbox-box {
        width: dt('checkbox.lg.width');
        height: dt('checkbox.lg.height');
    }

    .p-checkbox-lg .p-checkbox-icon {
        font-size: dt('checkbox.icon.lg.size');
        width: dt('checkbox.icon.lg.size');
        height: dt('checkbox.icon.lg.size');
    }
`;var Oe=["icon"],Re=["input"],Ae=(e,r,t)=>({checked:e,class:r,dataP:t});function He(e,r){if(e&1&&lt(0,"span",8),e&2){let t=v(3);y(t.cx("icon")),a("ngClass",t.checkboxIcon)("pBind",t.ptm("icon")),z("data-p",t.dataP)}}function je(e,r){if(e&1&&(T(),lt(0,"svg",9)),e&2){let t=v(3);y(t.cx("icon")),a("pBind",t.ptm("icon")),z("data-p",t.dataP)}}function $e(e,r){if(e&1&&(N(0),C(1,He,1,5,"span",6)(2,je,1,4,"svg",7),P()),e&2){let t=v(2);m(),a("ngIf",t.checkboxIcon),m(),a("ngIf",!t.checkboxIcon)}}function We(e,r){if(e&1&&(T(),lt(0,"svg",10)),e&2){let t=v(2);y(t.cx("icon")),a("pBind",t.ptm("icon")),z("data-p",t.dataP)}}function Ue(e,r){if(e&1&&(N(0),C(1,$e,3,2,"ng-container",3)(2,We,1,4,"svg",5),P()),e&2){let t=v();m(),a("ngIf",t.checked),m(),a("ngIf",t._indeterminate())}}function Qe(e,r){}function qe(e,r){e&1&&C(0,Qe,0,0,"ng-template")}var Ge=`
    ${be}

    /* For PrimeNG */
    p-checkBox.ng-invalid.ng-dirty .p-checkbox-box,
    p-check-box.ng-invalid.ng-dirty .p-checkbox-box,
    p-checkbox.ng-invalid.ng-dirty .p-checkbox-box {
        border-color: dt('checkbox.invalid.border.color');
    }
`,Ye={root:({instance:e})=>["p-checkbox p-component",{"p-checkbox-checked p-highlight":e.checked,"p-disabled":e.$disabled(),"p-invalid":e.invalid(),"p-variant-filled":e.$variant()==="filled","p-checkbox-sm p-inputfield-sm":e.size()==="small","p-checkbox-lg p-inputfield-lg":e.size()==="large"}],box:"p-checkbox-box",input:"p-checkbox-input",icon:"p-checkbox-icon"},ve=(()=>{class e extends ${name="checkbox";style=Ge;classes=Ye;static \u0275fac=(()=>{let t;return function(n){return(t||(t=u(e)))(n||e)}})();static \u0275prov=M({token:e,factory:e.\u0275fac})}return e})();var xe=new R("CHECKBOX_INSTANCE"),Ze={provide:de,useExisting:Rt(()=>ye),multi:!0},ye=(()=>{class e extends ge{componentName="Checkbox";hostName="";value;binary;ariaLabelledBy;ariaLabel;tabindex;inputId;inputStyle;styleClass;inputClass;indeterminate=!1;formControl;checkboxIcon;readonly;autofocus;trueValue=!0;falseValue=!1;variant=w();size=w();onChange=new X;onFocus=new X;onBlur=new X;inputViewChild;get checked(){return this._indeterminate()?!1:this.binary?this.modelValue()===this.trueValue:ie(this.value,this.modelValue())}_indeterminate=dt(void 0);checkboxIconTemplate;templates;_checkboxIconTemplate;focused=!1;_componentStyle=p(ve);bindDirectiveInstance=p(b,{self:!0});$pcCheckbox=p(xe,{optional:!0,skipSelf:!0})??void 0;$variant=J(()=>this.variant()||this.config.inputStyle()||this.config.inputVariant());onAfterContentInit(){this.templates?.forEach(t=>{switch(t.getType()){case"icon":this._checkboxIconTemplate=t.template;break;case"checkboxicon":this._checkboxIconTemplate=t.template;break}})}onChanges(t){t.indeterminate&&this._indeterminate.set(t.indeterminate.currentValue)}onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptms(["host","root"]))}updateModel(t){let i,n=this.injector.get(Et,null,{optional:!0,self:!0}),o=n&&!this.formControl?n.value:this.modelValue();this.binary?(i=this._indeterminate()?this.trueValue:this.checked?this.falseValue:this.trueValue,this.writeModelValue(i),this.onModelChange(i)):(this.checked||this._indeterminate()?i=o.filter(s=>!ee(s,this.value)):i=o?[...o,this.value]:[this.value],this.onModelChange(i),this.writeModelValue(i),this.formControl&&this.formControl.setValue(i)),this._indeterminate()&&this._indeterminate.set(!1),this.onChange.emit({checked:i,originalEvent:t})}handleChange(t){this.readonly||this.updateModel(t)}onInputFocus(t){this.focused=!0,this.onFocus.emit(t)}onInputBlur(t){this.focused=!1,this.onBlur.emit(t),this.onModelTouched()}focus(){this.inputViewChild?.nativeElement.focus()}writeControlValue(t,i){i(t),this.cd.markForCheck()}get dataP(){return this.cn({invalid:this.invalid(),checked:this.checked,disabled:this.$disabled(),filled:this.$variant()==="filled",[this.size()]:this.size()})}static \u0275fac=(()=>{let t;return function(n){return(t||(t=u(e)))(n||e)}})();static \u0275cmp=k({type:e,selectors:[["p-checkbox"],["p-checkBox"],["p-check-box"]],contentQueries:function(i,n,o){if(i&1&&Ct(o,Oe,4)(o,zt,4),i&2){let s;D(s=V())&&(n.checkboxIconTemplate=s.first),D(s=V())&&(n.templates=s)}},viewQuery:function(i,n){if(i&1&&It(Re,5),i&2){let o;D(o=V())&&(n.inputViewChild=o.first)}},hostVars:6,hostBindings:function(i,n){i&2&&(z("data-p-highlight",n.checked)("data-p-checked",n.checked)("data-p-disabled",n.$disabled())("data-p",n.dataP),y(n.cn(n.cx("root"),n.styleClass)))},inputs:{hostName:"hostName",value:"value",binary:[2,"binary","binary",F],ariaLabelledBy:"ariaLabelledBy",ariaLabel:"ariaLabel",tabindex:[2,"tabindex","tabindex",Yt],inputId:"inputId",inputStyle:"inputStyle",styleClass:"styleClass",inputClass:"inputClass",indeterminate:[2,"indeterminate","indeterminate",F],formControl:"formControl",checkboxIcon:"checkboxIcon",readonly:[2,"readonly","readonly",F],autofocus:[2,"autofocus","autofocus",F],trueValue:"trueValue",falseValue:"falseValue",variant:[1,"variant"],size:[1,"size"]},outputs:{onChange:"onChange",onFocus:"onFocus",onBlur:"onBlur"},features:[H([Ze,ve,{provide:xe,useExisting:e},{provide:W,useExisting:e}]),A([b]),_],decls:5,vars:26,consts:[["input",""],["type","checkbox",3,"focus","blur","change","checked","pBind"],[3,"pBind"],[4,"ngIf"],[4,"ngTemplateOutlet","ngTemplateOutletContext"],["data-p-icon","minus",3,"class","pBind",4,"ngIf"],[3,"class","ngClass","pBind",4,"ngIf"],["data-p-icon","check",3,"class","pBind",4,"ngIf"],[3,"ngClass","pBind"],["data-p-icon","check",3,"pBind"],["data-p-icon","minus",3,"pBind"]],template:function(i,n){i&1&&(st(0,"input",1,0),ut("focus",function(s){return n.onInputFocus(s)})("blur",function(s){return n.onInputBlur(s)})("change",function(s){return n.handleChange(s)}),rt(),st(2,"div",2),C(3,Ue,3,2,"ng-container",3)(4,qe,1,0,null,4),rt()),i&2&&(kt(n.inputStyle),y(n.cn(n.cx("input"),n.inputClass)),a("checked",n.checked)("pBind",n.ptm("input")),z("id",n.inputId)("value",n.value)("name",n.name())("tabindex",n.tabindex)("required",n.required()?"":void 0)("readonly",n.readonly?"":void 0)("disabled",n.$disabled()?"":void 0)("aria-labelledby",n.ariaLabelledBy)("aria-label",n.ariaLabel),m(2),y(n.cx("box")),a("pBind",n.ptm("box")),z("data-p",n.dataP),m(),a("ngIf",!n.checkboxIconTemplate&&!n._checkboxIconTemplate),m(),a("ngTemplateOutlet",n.checkboxIconTemplate||n._checkboxIconTemplate)("ngTemplateOutletContext",Gt(22,Ae,n.checked,n.cx("icon"),n.dataP)))},dependencies:[tt,Zt,St,Tt,j,re,_e,gt,b],encapsulation:2,changeDetection:0})}return e})(),Gn=(()=>{class e{static \u0275fac=function(i){return new(i||e)};static \u0275mod=K({type:e});static \u0275inj=Z({imports:[ye,j,j]})}return e})();var Ce=`
    .p-iconfield {
        position: relative;
        display: block;
    }

    .p-inputicon {
        position: absolute;
        top: 50%;
        margin-top: calc(-1 * (dt('icon.size') / 2));
        color: dt('iconfield.icon.color');
        line-height: 1;
        z-index: 1;
    }

    .p-iconfield .p-inputicon:first-child {
        inset-inline-start: dt('form.field.padding.x');
    }

    .p-iconfield .p-inputicon:last-child {
        inset-inline-end: dt('form.field.padding.x');
    }

    .p-iconfield .p-inputtext:not(:first-child),
    .p-iconfield .p-inputwrapper:not(:first-child) .p-inputtext {
        padding-inline-start: calc((dt('form.field.padding.x') * 2) + dt('icon.size'));
    }

    .p-iconfield .p-inputtext:not(:last-child) {
        padding-inline-end: calc((dt('form.field.padding.x') * 2) + dt('icon.size'));
    }

    .p-iconfield:has(.p-inputfield-sm) .p-inputicon {
        font-size: dt('form.field.sm.font.size');
        width: dt('form.field.sm.font.size');
        height: dt('form.field.sm.font.size');
        margin-top: calc(-1 * (dt('form.field.sm.font.size') / 2));
    }

    .p-iconfield:has(.p-inputfield-lg) .p-inputicon {
        font-size: dt('form.field.lg.font.size');
        width: dt('form.field.lg.font.size');
        height: dt('form.field.lg.font.size');
        margin-top: calc(-1 * (dt('form.field.lg.font.size') / 2));
    }
`;var Xe=["*"],Ke={root:({instance:e})=>["p-iconfield",{"p-iconfield-left":e.iconPosition=="left","p-iconfield-right":e.iconPosition=="right"}]},Ie=(()=>{class e extends ${name="iconfield";style=Ce;classes=Ke;static \u0275fac=(()=>{let t;return function(n){return(t||(t=u(e)))(n||e)}})();static \u0275prov=M({token:e,factory:e.\u0275fac})}return e})();var ke=new R("ICONFIELD_INSTANCE"),ho=(()=>{class e extends et{componentName="IconField";hostName="";_componentStyle=p(Ie);$pcIconField=p(ke,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=p(b,{self:!0});onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptms(["host","root"]))}iconPosition="left";styleClass;static \u0275fac=(()=>{let t;return function(n){return(t||(t=u(e)))(n||e)}})();static \u0275cmp=k({type:e,selectors:[["p-iconfield"],["p-iconField"],["p-icon-field"]],hostVars:2,hostBindings:function(i,n){i&2&&y(n.cn(n.cx("root"),n.styleClass))},inputs:{hostName:"hostName",iconPosition:"iconPosition",styleClass:"styleClass"},features:[H([Ie,{provide:ke,useExisting:e},{provide:W,useExisting:e}]),A([b]),_],ngContentSelectors:Xe,decls:1,vars:0,template:function(i,n){i&1&&(mt(),ft(0))},dependencies:[tt,gt],encapsulation:2,changeDetection:0})}return e})();var Je=["*"],ti={root:"p-inputicon"},we=(()=>{class e extends ${name="inputicon";classes=ti;static \u0275fac=(()=>{let t;return function(n){return(t||(t=u(e)))(n||e)}})();static \u0275prov=M({token:e,factory:e.\u0275fac})}return e})(),Se=new R("INPUTICON_INSTANCE"),wo=(()=>{class e extends et{componentName="InputIcon";hostName="";styleClass;_componentStyle=p(we);$pcInputIcon=p(Se,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=p(b,{self:!0});onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptms(["host","root"]))}static \u0275fac=(()=>{let t;return function(n){return(t||(t=u(e)))(n||e)}})();static \u0275cmp=k({type:e,selectors:[["p-inputicon"],["p-inputIcon"]],hostVars:2,hostBindings:function(i,n){i&2&&y(n.cn(n.cx("root"),n.styleClass))},inputs:{hostName:"hostName",styleClass:"styleClass"},features:[H([we,{provide:Se,useExisting:e},{provide:W,useExisting:e}]),A([b]),_],ngContentSelectors:Je,decls:1,vars:0,template:function(i,n){i&1&&(mt(),ft(0))},dependencies:[tt,j,gt],encapsulation:2,changeDetection:0})}return e})();var Te=["content"],ei=["item"],ii=["loader"],ni=["loadericon"],oi=["element"],si=["*"],Ot=(e,r)=>({$implicit:e,options:r}),ri=e=>({numCols:e}),Me=e=>({options:e}),li=()=>({styleClass:"p-virtualscroller-loading-icon"}),ai=(e,r)=>({rows:e,columns:r});function ci(e,r){e&1&&pt(0)}function di(e,r){if(e&1&&(N(0),C(1,ci,1,0,"ng-container",10),P()),e&2){let t=v(2);m(),a("ngTemplateOutlet",t.contentTemplate||t._contentTemplate)("ngTemplateOutletContext",bt(2,Ot,t.loadedItems,t.getContentOptions()))}}function hi(e,r){e&1&&pt(0)}function pi(e,r){if(e&1&&(N(0),C(1,hi,1,0,"ng-container",10),P()),e&2){let t=r.$implicit,i=r.index,n=v(3);m(),a("ngTemplateOutlet",n.itemTemplate||n._itemTemplate)("ngTemplateOutletContext",bt(2,Ot,t,n.getOptions(i)))}}function ui(e,r){if(e&1&&(st(0,"div",11,3),C(2,pi,2,5,"ng-container",12),rt()),e&2){let t=v(2);kt(t.contentStyle),y(t.cn(t.cx("content"),t.contentStyleClass)),a("pBind",t.ptm("content")),m(2),a("ngForOf",t.loadedItems)("ngForTrackBy",t._trackBy)}}function mi(e,r){if(e&1&&lt(0,"div",13),e&2){let t=v(2);y(t.cx("spacer")),a("ngStyle",t.spacerStyle)("pBind",t.ptm("spacer"))}}function fi(e,r){e&1&&pt(0)}function gi(e,r){if(e&1&&(N(0),C(1,fi,1,0,"ng-container",10),P()),e&2){let t=r.index,i=v(4);m(),a("ngTemplateOutlet",i.loaderTemplate||i._loaderTemplate)("ngTemplateOutletContext",wt(4,Me,i.getLoaderOptions(t,i.both&&wt(2,ri,i.numItemsInViewport.cols))))}}function _i(e,r){if(e&1&&(N(0),C(1,gi,2,6,"ng-container",14),P()),e&2){let t=v(3);m(),a("ngForOf",t.loaderArr)}}function bi(e,r){e&1&&pt(0)}function vi(e,r){if(e&1&&(N(0),C(1,bi,1,0,"ng-container",10),P()),e&2){let t=v(4);m(),a("ngTemplateOutlet",t.loaderIconTemplate||t._loaderIconTemplate)("ngTemplateOutletContext",wt(3,Me,qt(2,li)))}}function xi(e,r){if(e&1&&(T(),lt(0,"svg",15)),e&2){let t=v(4);y(t.cx("loadingIcon")),a("spin",!0)("pBind",t.ptm("loadingIcon"))}}function yi(e,r){if(e&1&&C(0,vi,2,5,"ng-container",6)(1,xi,1,4,"ng-template",null,5,vt),e&2){let t=_t(2),i=v(3);a("ngIf",i.loaderIconTemplate||i._loaderIconTemplate)("ngIfElse",t)}}function Ci(e,r){if(e&1&&(st(0,"div",11),C(1,_i,2,1,"ng-container",6)(2,yi,3,2,"ng-template",null,4,vt),rt()),e&2){let t=_t(3),i=v(2);y(i.cx("loader")),a("pBind",i.ptm("loader")),m(),a("ngIf",i.loaderTemplate||i._loaderTemplate)("ngIfElse",t)}}function Ii(e,r){if(e&1){let t=Wt();N(0),st(1,"div",7,1),ut("scroll",function(n){At(t);let o=v();return Ht(o.onContainerScroll(n))}),C(3,di,2,5,"ng-container",6)(4,ui,3,7,"ng-template",null,2,vt)(6,mi,1,4,"div",8)(7,Ci,4,5,"div",9),rt(),P()}if(e&2){let t=_t(5),i=v();m(),y(i.cn(i.cx("root"),i.styleClass)),a("ngStyle",i._style)("pBind",i.ptm("root")),z("id",i._id)("tabindex",i.tabindex),m(2),a("ngIf",i.contentTemplate||i._contentTemplate)("ngIfElse",t),m(3),a("ngIf",i._showSpacer),m(),a("ngIf",!i.loaderDisabled&&i._showLoader&&i.d_loading)}}function ki(e,r){e&1&&pt(0)}function wi(e,r){if(e&1&&(N(0),C(1,ki,1,0,"ng-container",10),P()),e&2){let t=v(2);m(),a("ngTemplateOutlet",t.contentTemplate||t._contentTemplate)("ngTemplateOutletContext",bt(5,Ot,t.items,bt(2,ai,t._items,t.loadedColumns)))}}function Si(e,r){if(e&1&&(ft(0),C(1,wi,2,8,"ng-container",16)),e&2){let t=v();m(),a("ngIf",t.contentTemplate||t._contentTemplate)}}var Ti=`
.p-virtualscroller {
    position: relative;
    overflow: auto;
    contain: strict;
    transform: translateZ(0);
    will-change: scroll-position;
    outline: 0 none;
}

.p-virtualscroller-content {
    position: absolute;
    top: 0;
    left: 0;
    min-height: 100%;
    min-width: 100%;
    will-change: transform;
}

.p-virtualscroller-spacer {
    position: absolute;
    top: 0;
    left: 0;
    height: 1px;
    width: 1px;
    transform-origin: 0 0;
    pointer-events: none;
}

.p-virtualscroller-loader {
    position: sticky;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: dt('virtualscroller.loader.mask.background');
    color: dt('virtualscroller.loader.mask.color');
}

.p-virtualscroller-loader-mask {
    display: flex;
    align-items: center;
    justify-content: center;
}

.p-virtualscroller-loading-icon {
    font-size: dt('virtualscroller.loader.icon.size');
    width: dt('virtualscroller.loader.icon.size');
    height: dt('virtualscroller.loader.icon.size');
}

.p-virtualscroller-horizontal > .p-virtualscroller-content {
    display: flex;
}

.p-virtualscroller-inline .p-virtualscroller-content {
    position: static;
}
`,zi={root:({instance:e})=>["p-virtualscroller",{"p-virtualscroller-inline":e.inline,"p-virtualscroller-both p-both-scroll":e.both,"p-virtualscroller-horizontal p-horizontal-scroll":e.horizontal}],content:"p-virtualscroller-content",spacer:"p-virtualscroller-spacer",loader:({instance:e})=>["p-virtualscroller-loader",{"p-virtualscroller-loader-mask":!e.loaderTemplate}],loadingIcon:"p-virtualscroller-loading-icon"},ze=(()=>{class e extends ${name="virtualscroller";css=Ti;classes=zi;static \u0275fac=(()=>{let t;return function(n){return(t||(t=u(e)))(n||e)}})();static \u0275prov=M({token:e,factory:e.\u0275fac})}return e})();var Ee=new R("SCROLLER_INSTANCE"),Ei=(()=>{class e extends et{zone;componentName="VirtualScroller";bindDirectiveInstance=p(b,{self:!0});$pcScroller=p(Ee,{optional:!0,skipSelf:!0})??void 0;hostName="";get id(){return this._id}set id(t){this._id=t}get style(){return this._style}set style(t){this._style=t}get styleClass(){return this._styleClass}set styleClass(t){this._styleClass=t}get tabindex(){return this._tabindex}set tabindex(t){this._tabindex=t}get items(){return this._items}set items(t){this._items=t}get itemSize(){return this._itemSize}set itemSize(t){this._itemSize=t}get scrollHeight(){return this._scrollHeight}set scrollHeight(t){this._scrollHeight=t}get scrollWidth(){return this._scrollWidth}set scrollWidth(t){this._scrollWidth=t}get orientation(){return this._orientation}set orientation(t){this._orientation=t}get step(){return this._step}set step(t){this._step=t}get delay(){return this._delay}set delay(t){this._delay=t}get resizeDelay(){return this._resizeDelay}set resizeDelay(t){this._resizeDelay=t}get appendOnly(){return this._appendOnly}set appendOnly(t){this._appendOnly=t}get inline(){return this._inline}set inline(t){this._inline=t}get lazy(){return this._lazy}set lazy(t){this._lazy=t}get disabled(){return this._disabled}set disabled(t){this._disabled=t}get loaderDisabled(){return this._loaderDisabled}set loaderDisabled(t){this._loaderDisabled=t}get columns(){return this._columns}set columns(t){this._columns=t}get showSpacer(){return this._showSpacer}set showSpacer(t){this._showSpacer=t}get showLoader(){return this._showLoader}set showLoader(t){this._showLoader=t}get numToleratedItems(){return this._numToleratedItems}set numToleratedItems(t){this._numToleratedItems=t}get loading(){return this._loading}set loading(t){this._loading=t}get autoSize(){return this._autoSize}set autoSize(t){this._autoSize=t}get trackBy(){return this._trackBy}set trackBy(t){this._trackBy=t}get options(){return this._options}set options(t){this._options=t,t&&typeof t=="object"&&(Object.entries(t).forEach(([i,n])=>this[`_${i}`]!==n&&(this[`_${i}`]=n)),Object.entries(t).forEach(([i,n])=>this[`${i}`]!==n&&(this[`${i}`]=n)))}onLazyLoad=new X;onScroll=new X;onScrollIndexChange=new X;elementViewChild;contentViewChild;height;_id;_style;_styleClass;_tabindex=0;_items;_itemSize=0;_scrollHeight;_scrollWidth;_orientation="vertical";_step=0;_delay=0;_resizeDelay=10;_appendOnly=!1;_inline=!1;_lazy=!1;_disabled=!1;_loaderDisabled=!1;_columns;_showSpacer=!0;_showLoader=!1;_numToleratedItems;_loading;_autoSize=!1;_trackBy;_options;d_loading=!1;d_numToleratedItems;contentEl;contentTemplate;itemTemplate;loaderTemplate;loaderIconTemplate;templates;_contentTemplate;_itemTemplate;_loaderTemplate;_loaderIconTemplate;first=0;last=0;page=0;isRangeChanged=!1;numItemsInViewport=0;lastScrollPos=0;lazyLoadState={};loaderArr=[];spacerStyle={};contentStyle={};scrollTimeout;resizeTimeout;initialized=!1;windowResizeListener;defaultWidth;defaultHeight;defaultContentWidth;defaultContentHeight;_contentStyleClass;get contentStyleClass(){return this._contentStyleClass}set contentStyleClass(t){this._contentStyleClass=t}get vertical(){return this._orientation==="vertical"}get horizontal(){return this._orientation==="horizontal"}get both(){return this._orientation==="both"}get loadedItems(){return this._items&&!this.d_loading?this.both?this._items.slice(this._appendOnly?0:this.first.rows,this.last.rows).map(t=>this._columns?t:Array.isArray(t)?t.slice(this._appendOnly?0:this.first.cols,this.last.cols):t):this.horizontal&&this._columns?this._items:this._items.slice(this._appendOnly?0:this.first,this.last):[]}get loadedRows(){return this.d_loading?this._loaderDisabled?this.loaderArr:[]:this.loadedItems}get loadedColumns(){return this._columns&&(this.both||this.horizontal)?this.d_loading&&this._loaderDisabled?this.both?this.loaderArr[0]:this.loaderArr:this._columns.slice(this.both?this.first.cols:this.first,this.both?this.last.cols:this.last):this._columns}_componentStyle=p(ze);constructor(t){super(),this.zone=t}onInit(){this.setInitialState()}onChanges(t){let i=!1;if(this.scrollHeight=="100%"&&(this.height="100%"),t.loading){let{previousValue:n,currentValue:o}=t.loading;this.lazy&&n!==o&&o!==this.d_loading&&(this.d_loading=o,i=!0)}if(t.orientation&&(this.lastScrollPos=this.both?{top:0,left:0}:0),t.numToleratedItems){let{previousValue:n,currentValue:o}=t.numToleratedItems;n!==o&&o!==this.d_numToleratedItems&&(this.d_numToleratedItems=o)}if(t.options){let{previousValue:n,currentValue:o}=t.options;this.lazy&&n?.loading!==o?.loading&&o?.loading!==this.d_loading&&(this.d_loading=o.loading,i=!0),n?.numToleratedItems!==o?.numToleratedItems&&o?.numToleratedItems!==this.d_numToleratedItems&&(this.d_numToleratedItems=o.numToleratedItems)}this.initialized&&!i&&(t.items?.previousValue?.length!==t.items?.currentValue?.length||t.itemSize||t.scrollHeight||t.scrollWidth)&&this.init()}onAfterContentInit(){this.templates.forEach(t=>{switch(t.getType()){case"content":this._contentTemplate=t.template;break;case"item":this._itemTemplate=t.template;break;case"loader":this._loaderTemplate=t.template;break;case"loadericon":this._loaderIconTemplate=t.template;break;default:this._itemTemplate=t.template;break}})}onAfterViewInit(){Promise.resolve().then(()=>{this.viewInit()})}onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptm("host")),this.initialized||this.viewInit()}onDestroy(){this.unbindResizeListener(),this.contentEl=null,this.initialized=!1}viewInit(){Pt(this.platformId)&&!this.initialized&&Lt(this.elementViewChild?.nativeElement)&&(this.setInitialState(),this.setContentEl(this.contentEl),this.init(),this.defaultWidth=ct(this.elementViewChild?.nativeElement),this.defaultHeight=at(this.elementViewChild?.nativeElement),this.defaultContentWidth=ct(this.contentEl),this.defaultContentHeight=at(this.contentEl),this.initialized=!0)}init(){this._disabled||(this.bindResizeListener(),setTimeout(()=>{this.setSpacerSize(),this.setSize(),this.calculateOptions(),this.calculateAutoSize(),this.cd.detectChanges()},1))}setContentEl(t){this.contentEl=t||this.contentViewChild?.nativeElement||ne(this.elementViewChild?.nativeElement,".p-virtualscroller-content")}setInitialState(){this.first=this.both?{rows:0,cols:0}:0,this.last=this.both?{rows:0,cols:0}:0,this.numItemsInViewport=this.both?{rows:0,cols:0}:0,this.lastScrollPos=this.both?{top:0,left:0}:0,(this.d_loading===void 0||this.d_loading===!1)&&(this.d_loading=this._loading||!1),this.d_numToleratedItems=this._numToleratedItems,this.loaderArr=this.loaderArr.length>0?this.loaderArr:[]}getElementRef(){return this.elementViewChild}getPageByFirst(t){return Math.floor(((t??this.first)+this.d_numToleratedItems*4)/(this._step||1))}isPageChanged(t){return this._step?this.page!==this.getPageByFirst(t??this.first):!0}scrollTo(t){this.elementViewChild?.nativeElement?.scrollTo(t)}scrollToIndex(t,i="auto"){if(this.both?t.every(o=>o>-1):t>-1){let o=this.first,{scrollTop:s=0,scrollLeft:l=0}=this.elementViewChild?.nativeElement,{numToleratedItems:x}=this.calculateNumItems(),f=this.getContentPosition(),h=this.itemSize,E=(d=0,g)=>d<=g?0:d,I=(d,g,B)=>d*g+B,O=(d=0,g=0)=>this.scrollTo({left:d,top:g,behavior:i}),S=this.both?{rows:0,cols:0}:0,nt=!1,c=!1;this.both?(S={rows:E(t[0],x[0]),cols:E(t[1],x[1])},O(I(S.cols,h[1],f.left),I(S.rows,h[0],f.top)),c=this.lastScrollPos.top!==s||this.lastScrollPos.left!==l,nt=S.rows!==o.rows||S.cols!==o.cols):(S=E(t,x),this.horizontal?O(I(S,h,f.left),s):O(l,I(S,h,f.top)),c=this.lastScrollPos!==(this.horizontal?l:s),nt=S!==o),this.isRangeChanged=nt,c&&(this.first=S)}}scrollInView(t,i,n="auto"){if(i){let{first:o,viewport:s}=this.getRenderedRange(),l=(h=0,E=0)=>this.scrollTo({left:h,top:E,behavior:n}),x=i==="to-start",f=i==="to-end";if(x){if(this.both)s.first.rows-o.rows>t[0]?l(s.first.cols*this._itemSize[1],(s.first.rows-1)*this._itemSize[0]):s.first.cols-o.cols>t[1]&&l((s.first.cols-1)*this._itemSize[1],s.first.rows*this._itemSize[0]);else if(s.first-o>t){let h=(s.first-1)*this._itemSize;this.horizontal?l(h,0):l(0,h)}}else if(f){if(this.both)s.last.rows-o.rows<=t[0]+1?l(s.first.cols*this._itemSize[1],(s.first.rows+1)*this._itemSize[0]):s.last.cols-o.cols<=t[1]+1&&l((s.first.cols+1)*this._itemSize[1],s.first.rows*this._itemSize[0]);else if(s.last-o<=t+1){let h=(s.first+1)*this._itemSize;this.horizontal?l(h,0):l(0,h)}}}else this.scrollToIndex(t,n)}getRenderedRange(){let t=(o,s)=>s||o?Math.floor(o/(s||o)):0,i=this.first,n=0;if(this.elementViewChild?.nativeElement){let{scrollTop:o,scrollLeft:s}=this.elementViewChild.nativeElement;if(this.both)i={rows:t(o,this._itemSize[0]),cols:t(s,this._itemSize[1])},n={rows:i.rows+this.numItemsInViewport.rows,cols:i.cols+this.numItemsInViewport.cols};else{let l=this.horizontal?s:o;i=t(l,this._itemSize),n=i+this.numItemsInViewport}}return{first:this.first,last:this.last,viewport:{first:i,last:n}}}calculateNumItems(){let t=this.getContentPosition(),i=(this.elementViewChild?.nativeElement?this.elementViewChild.nativeElement.offsetWidth-t.left:0)||0,n=(this.elementViewChild?.nativeElement?this.elementViewChild.nativeElement.offsetHeight-t.top:0)||0,o=(f,h)=>h||f?Math.ceil(f/(h||f)):0,s=f=>Math.ceil(f/2),l=this.both?{rows:o(n,this._itemSize[0]),cols:o(i,this._itemSize[1])}:o(this.horizontal?i:n,this._itemSize),x=this.d_numToleratedItems||(this.both?[s(l.rows),s(l.cols)]:s(l));return{numItemsInViewport:l,numToleratedItems:x}}calculateOptions(){let{numItemsInViewport:t,numToleratedItems:i}=this.calculateNumItems(),n=(l,x,f,h=!1)=>this.getLast(l+x+(l<f?2:3)*f,h),o=this.first,s=this.both?{rows:n(this.first.rows,t.rows,i[0]),cols:n(this.first.cols,t.cols,i[1],!0)}:n(this.first,t,i);this.last=s,this.numItemsInViewport=t,this.d_numToleratedItems=i,this._showLoader&&(this.loaderArr=this.both?Array.from({length:t.rows}).map(()=>Array.from({length:t.cols})):Array.from({length:t})),this._lazy&&Promise.resolve().then(()=>{this.lazyLoadState={first:this._step?this.both?{rows:0,cols:o.cols}:0:o,last:Math.min(this._step?this._step:this.last,this._items.length)},this.handleEvents("onLazyLoad",this.lazyLoadState)})}calculateAutoSize(){this._autoSize&&!this.d_loading&&Promise.resolve().then(()=>{if(this.contentEl){this.contentEl.style.minHeight=this.contentEl.style.minWidth="auto",this.contentEl.style.position="relative",this.elementViewChild.nativeElement.style.contain="none";let[t,i]=[ct(this.contentEl),at(this.contentEl)];t!==this.defaultContentWidth&&(this.elementViewChild.nativeElement.style.width=""),i!==this.defaultContentHeight&&(this.elementViewChild.nativeElement.style.height="");let[n,o]=[ct(this.elementViewChild.nativeElement),at(this.elementViewChild.nativeElement)];(this.both||this.horizontal)&&(this.elementViewChild.nativeElement.style.width=n<this.defaultWidth?n+"px":this._scrollWidth||this.defaultWidth+"px"),(this.both||this.vertical)&&(this.elementViewChild.nativeElement.style.height=o<this.defaultHeight?o+"px":this._scrollHeight||this.defaultHeight+"px"),this.contentEl.style.minHeight=this.contentEl.style.minWidth="",this.contentEl.style.position="",this.elementViewChild.nativeElement.style.contain=""}})}getLast(t=0,i=!1){return this._items?Math.min(i?(this._columns||this._items[0]).length:this._items.length,t):0}getContentPosition(){if(this.contentEl){let t=getComputedStyle(this.contentEl),i=parseFloat(t.paddingLeft)+Math.max(parseFloat(t.left)||0,0),n=parseFloat(t.paddingRight)+Math.max(parseFloat(t.right)||0,0),o=parseFloat(t.paddingTop)+Math.max(parseFloat(t.top)||0,0),s=parseFloat(t.paddingBottom)+Math.max(parseFloat(t.bottom)||0,0);return{left:i,right:n,top:o,bottom:s,x:i+n,y:o+s}}return{left:0,right:0,top:0,bottom:0,x:0,y:0}}setSize(){if(this.elementViewChild?.nativeElement){let t=this.elementViewChild.nativeElement,i=t.parentElement?.parentElement,n=t.offsetWidth,o=i?.offsetWidth||0,s=this._scrollWidth||`${n||o}px`,l=t.offsetHeight,x=i?.offsetHeight||0,f=this._scrollHeight||`${l||x}px`,h=(E,I)=>t.style[E]=I;this.both||this.horizontal?(h("height",f),h("width",s)):h("height",f)}}setSpacerSize(){if(this._items){let t=this.getContentPosition(),i=(n,o,s,l=0)=>this.spacerStyle=Vt(yt({},this.spacerStyle),{[`${n}`]:(o||[]).length*s+l+"px"});this.both?(i("height",this._items,this._itemSize[0],t.y),i("width",this._columns||this._items[1],this._itemSize[1],t.x)):this.horizontal?i("width",this._columns||this._items,this._itemSize,t.x):i("height",this._items,this._itemSize,t.y)}}setContentPosition(t){if(this.contentEl&&!this._appendOnly){let i=t?t.first:this.first,n=(s,l)=>s*l,o=(s=0,l=0)=>this.contentStyle=Vt(yt({},this.contentStyle),{transform:`translate3d(${s}px, ${l}px, 0)`});if(this.both)o(n(i.cols,this._itemSize[1]),n(i.rows,this._itemSize[0]));else{let s=n(i,this._itemSize);this.horizontal?o(s,0):o(0,s)}}}onScrollPositionChange(t){let i=t.target;if(!i)throw new Error("Event target is null");let n=this.getContentPosition(),o=(c,d)=>c?c>d?c-d:c:0,s=(c,d)=>d||c?Math.floor(c/(d||c)):0,l=(c,d,g,B,U,ot)=>c<=U?U:ot?g-B-U:d+U-1,x=(c,d,g,B,U,ot,xt)=>c<=ot?0:Math.max(0,xt?c<d?g:c-ot:c>d?g:c-2*ot),f=(c,d,g,B,U,ot=!1)=>{let xt=d+B+2*U;return c>=U&&(xt+=U+1),this.getLast(xt,ot)},h=o(i.scrollTop,n.top),E=o(i.scrollLeft,n.left),I=this.both?{rows:0,cols:0}:0,O=this.last,S=!1,nt=this.lastScrollPos;if(this.both){let c=this.lastScrollPos.top<=h,d=this.lastScrollPos.left<=E;if(!this._appendOnly||this._appendOnly&&(c||d)){let g={rows:s(h,this._itemSize[0]),cols:s(E,this._itemSize[1])},B={rows:l(g.rows,this.first.rows,this.last.rows,this.numItemsInViewport.rows,this.d_numToleratedItems[0],c),cols:l(g.cols,this.first.cols,this.last.cols,this.numItemsInViewport.cols,this.d_numToleratedItems[1],d)};I={rows:x(g.rows,B.rows,this.first.rows,this.last.rows,this.numItemsInViewport.rows,this.d_numToleratedItems[0],c),cols:x(g.cols,B.cols,this.first.cols,this.last.cols,this.numItemsInViewport.cols,this.d_numToleratedItems[1],d)},O={rows:f(g.rows,I.rows,this.last.rows,this.numItemsInViewport.rows,this.d_numToleratedItems[0]),cols:f(g.cols,I.cols,this.last.cols,this.numItemsInViewport.cols,this.d_numToleratedItems[1],!0)},S=I.rows!==this.first.rows||O.rows!==this.last.rows||I.cols!==this.first.cols||O.cols!==this.last.cols||this.isRangeChanged,nt={top:h,left:E}}}else{let c=this.horizontal?E:h,d=this.lastScrollPos<=c;if(!this._appendOnly||this._appendOnly&&d){let g=s(c,this._itemSize),B=l(g,this.first,this.last,this.numItemsInViewport,this.d_numToleratedItems,d);I=x(g,B,this.first,this.last,this.numItemsInViewport,this.d_numToleratedItems,d),O=f(g,I,this.last,this.numItemsInViewport,this.d_numToleratedItems),S=I!==this.first||O!==this.last||this.isRangeChanged,nt=c}}return{first:I,last:O,isRangeChanged:S,scrollPos:nt}}onScrollChange(t){let{first:i,last:n,isRangeChanged:o,scrollPos:s}=this.onScrollPositionChange(t);if(o){let l={first:i,last:n};if(this.setContentPosition(l),this.first=i,this.last=n,this.lastScrollPos=s,this.handleEvents("onScrollIndexChange",l),this._lazy&&this.isPageChanged(i)){let x={first:this._step?Math.min(this.getPageByFirst(i)*this._step,this._items.length-this._step):i,last:Math.min(this._step?(this.getPageByFirst(i)+1)*this._step:n,this._items.length)};(this.lazyLoadState.first!==x.first||this.lazyLoadState.last!==x.last)&&this.handleEvents("onLazyLoad",x),this.lazyLoadState=x}}}onContainerScroll(t){if(this.handleEvents("onScroll",{originalEvent:t}),this._delay){if(this.scrollTimeout&&clearTimeout(this.scrollTimeout),!this.d_loading&&this._showLoader){let{isRangeChanged:i}=this.onScrollPositionChange(t);(i||this._step&&this.isPageChanged())&&(this.d_loading=!0,this.cd.detectChanges())}this.scrollTimeout=setTimeout(()=>{this.onScrollChange(t),this.d_loading&&this._showLoader&&(!this._lazy||this._loading===void 0)&&(this.d_loading=!1,this.page=this.getPageByFirst()),this.cd.detectChanges()},this._delay)}else!this.d_loading&&this.onScrollChange(t)}bindResizeListener(){Pt(this.platformId)&&(this.windowResizeListener||this.zone.runOutsideAngular(()=>{let t=this.document.defaultView,i=oe()?"orientationchange":"resize";this.windowResizeListener=this.renderer.listen(t,i,this.onWindowResize.bind(this))}))}unbindResizeListener(){this.windowResizeListener&&(this.windowResizeListener(),this.windowResizeListener=null)}onWindowResize(){this.resizeTimeout&&clearTimeout(this.resizeTimeout),this.resizeTimeout=setTimeout(()=>{if(Lt(this.elementViewChild?.nativeElement)){let[t,i]=[ct(this.elementViewChild?.nativeElement),at(this.elementViewChild?.nativeElement)],[n,o]=[t!==this.defaultWidth,i!==this.defaultHeight];(this.both?n||o:this.horizontal?n:this.vertical&&o)&&this.zone.run(()=>{this.d_numToleratedItems=this._numToleratedItems,this.defaultWidth=t,this.defaultHeight=i,this.defaultContentWidth=ct(this.contentEl),this.defaultContentHeight=at(this.contentEl),this.init()})}},this._resizeDelay)}handleEvents(t,i){return this.options&&this.options[t]?this.options[t](i):this[t].emit(i)}getContentOptions(){return{contentStyleClass:`p-virtualscroller-content ${this.d_loading?"p-virtualscroller-loading":""}`,items:this.loadedItems,getItemOptions:t=>this.getOptions(t),loading:this.d_loading,getLoaderOptions:(t,i)=>this.getLoaderOptions(t,i),itemSize:this._itemSize,rows:this.loadedRows,columns:this.loadedColumns,spacerStyle:this.spacerStyle,contentStyle:this.contentStyle,vertical:this.vertical,horizontal:this.horizontal,both:this.both,scrollTo:this.scrollTo.bind(this),scrollToIndex:this.scrollToIndex.bind(this),orientation:this._orientation,scrollableElement:this.elementViewChild?.nativeElement}}getOptions(t){let i=(this._items||[]).length,n=this.both?this.first.rows+t:this.first+t;return{index:n,count:i,first:n===0,last:n===i-1,even:n%2===0,odd:n%2!==0}}getLoaderOptions(t,i){let n=this.loaderArr.length;return yt({index:t,count:n,first:t===0,last:t===n-1,even:t%2===0,odd:t%2!==0,loading:this.d_loading},i)}static \u0275fac=function(i){return new(i||e)($t(jt))};static \u0275cmp=k({type:e,selectors:[["p-scroller"],["p-virtualscroller"],["p-virtual-scroller"],["p-virtualScroller"]],contentQueries:function(i,n,o){if(i&1&&Ct(o,Te,4)(o,ei,4)(o,ii,4)(o,ni,4)(o,zt,4),i&2){let s;D(s=V())&&(n.contentTemplate=s.first),D(s=V())&&(n.itemTemplate=s.first),D(s=V())&&(n.loaderTemplate=s.first),D(s=V())&&(n.loaderIconTemplate=s.first),D(s=V())&&(n.templates=s)}},viewQuery:function(i,n){if(i&1&&It(oi,5)(Te,5),i&2){let o;D(o=V())&&(n.elementViewChild=o.first),D(o=V())&&(n.contentViewChild=o.first)}},hostVars:2,hostBindings:function(i,n){i&2&&Qt("height",n.height)},inputs:{hostName:"hostName",id:"id",style:"style",styleClass:"styleClass",tabindex:"tabindex",items:"items",itemSize:"itemSize",scrollHeight:"scrollHeight",scrollWidth:"scrollWidth",orientation:"orientation",step:"step",delay:"delay",resizeDelay:"resizeDelay",appendOnly:"appendOnly",inline:"inline",lazy:"lazy",disabled:"disabled",loaderDisabled:"loaderDisabled",columns:"columns",showSpacer:"showSpacer",showLoader:"showLoader",numToleratedItems:"numToleratedItems",loading:"loading",autoSize:"autoSize",trackBy:"trackBy",options:"options"},outputs:{onLazyLoad:"onLazyLoad",onScroll:"onScroll",onScrollIndexChange:"onScrollIndexChange"},features:[H([ze,{provide:Ee,useExisting:e},{provide:W,useExisting:e}]),A([b]),_],ngContentSelectors:si,decls:3,vars:2,consts:[["disabledContainer",""],["element",""],["buildInContent",""],["content",""],["buildInLoader",""],["buildInLoaderIcon",""],[4,"ngIf","ngIfElse"],[3,"scroll","ngStyle","pBind"],[3,"class","ngStyle","pBind",4,"ngIf"],[3,"class","pBind",4,"ngIf"],[4,"ngTemplateOutlet","ngTemplateOutletContext"],[3,"pBind"],[4,"ngFor","ngForOf","ngForTrackBy"],[3,"ngStyle","pBind"],[4,"ngFor","ngForOf"],["data-p-icon","spinner",3,"spin","pBind"],[4,"ngIf"]],template:function(i,n){if(i&1&&(mt(),C(0,Ii,8,10,"ng-container",6)(1,Si,2,1,"ng-template",null,0,vt)),i&2){let o=_t(2);a("ngIf",!n._disabled)("ngIfElse",o)}},dependencies:[tt,Xt,St,Tt,Kt,le,j,b],encapsulation:2})}return e})(),Qo=(()=>{class e{static \u0275fac=function(i){return new(i||e)};static \u0275mod=K({type:e});static \u0275inj=Z({imports:[Ei,j,j]})}return e})();export{dn as a,un as b,_n as c,pe as d,Mt as e,rn as f,ln as g,ge as h,ye as i,Gn as j,ho as k,wo as l,Ei as m,Qo as n};
