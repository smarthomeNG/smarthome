import{a as ie,c as oe,f as St}from"./chunk-2HIXAOWN.js";import{a as ne,j as se}from"./chunk-MSJFQPAD.js";import{Ca as ee,J as Xt,Ka as kt,L as Kt,La as R,M as Jt,Oa as j,Qa as $,Ra as J,Sa as b,Ta as ut,Ua as Y,j as Ut,ja as Yt,k as Gt,l as It,m as Zt,n as wt,oa as st,r as K,ua as rt,v as Ft,wa as Bt,xa as te}from"./chunk-JYMX7FOM.js";import{$b as V,Fb as a,Gb as it,Gc as gt,Hb as nt,Ib as ot,Jb as Vt,Kb as Dt,Lb as q,Lc as X,Mb as B,Nb as N,Ob as ct,Pb as Rt,Pc as k,Qb as jt,Tb as dt,U as Pt,V as L,Vb as x,W as U,Wa as u,Wb as ht,Xb as pt,Y as O,Yb as xt,Yc as D,Zb as yt,Zc as qt,_ as g,_b as M,a as bt,b as Et,db as Ht,dc as mt,ea as Lt,ec as $t,fa as Ot,ga as T,gc as vt,hc as v,ib as w,jb as Z,kb as at,la as G,ma as At,mb as A,nb as _,ob as C,pa as lt,sa as Mt,tc as H,ua as p,uc as Wt,vc as Ct,wb as z,wc as ft,xc as Qt}from"./chunk-BDB7QD2D.js";var Tt=(()=>{class e extends J{modelValue=lt(void 0);$filled=X(()=>Xt(this.modelValue()));writeModelValue(t){this.modelValue.set(t)}static \u0275fac=(()=>{let t;return function(n){return(t||(t=p(e)))(n||e)}})();static \u0275dir=at({type:e,features:[_]})}return e})();var re=`
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
`;var we=`
    ${re}

    /* For PrimeNG */
   .p-inputtext.ng-invalid.ng-dirty {
        border-color: dt('inputtext.invalid.border.color');
    }

    .p-inputtext.ng-invalid.ng-dirty::placeholder {
        color: dt('inputtext.invalid.placeholder.color');
    }
`,ke={root:({instance:e})=>["p-inputtext p-component",{"p-filled":e.$filled(),"p-inputtext-sm":e.pSize==="small","p-inputtext-lg":e.pSize==="large","p-invalid":e.invalid(),"p-variant-filled":e.$variant()==="filled","p-inputtext-fluid":e.hasFluid}]},le=(()=>{class e extends j{name="inputtext";style=we;classes=ke;static \u0275fac=(()=>{let t;return function(n){return(t||(t=p(e)))(n||e)}})();static \u0275prov=L({token:e,factory:e.\u0275fac})}return e})();var ae=new O("INPUTTEXT_INSTANCE"),ji=(()=>{class e extends Tt{componentName="InputText";hostName="";ptInputText=k();pInputTextPT=k();pInputTextUnstyled=k();bindDirectiveInstance=g(b,{self:!0});$pcInputText=g(ae,{optional:!0,skipSelf:!0})??void 0;ngControl=g(St,{optional:!0,self:!0});pcFluid=g(se,{optional:!0,host:!0,skipSelf:!0});pSize;variant=k();fluid=k(void 0,{transform:D});invalid=k(void 0,{transform:D});$variant=X(()=>this.variant()||this.config.inputStyle()||this.config.inputVariant());_componentStyle=g(le);constructor(){super(),Mt(()=>{let t=this.ptInputText()||this.pInputTextPT();t&&this.directivePT.set(t)}),Mt(()=>{this.pInputTextUnstyled()&&this.directiveUnstyled.set(this.pInputTextUnstyled())})}onAfterViewInit(){this.writeModelValue(this.ngControl?.value??this.el.nativeElement.value),this.cd.detectChanges()}onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptm("root"))}onDoCheck(){this.writeModelValue(this.ngControl?.value??this.el.nativeElement.value)}onInput(){this.writeModelValue(this.ngControl?.value??this.el.nativeElement.value)}get hasFluid(){return this.fluid()??!!this.pcFluid}get dataP(){return this.cn({invalid:this.invalid(),fluid:this.hasFluid,filled:this.$variant()==="filled",[this.pSize]:this.pSize})}static \u0275fac=function(i){return new(i||e)};static \u0275dir=at({type:e,selectors:[["","pInputText",""]],hostVars:3,hostBindings:function(i,n){i&1&&dt("input",function(){return n.onInput()}),i&2&&(z("data-p",n.dataP),v(n.cx("root")))},inputs:{hostName:"hostName",ptInputText:[1,"ptInputText"],pInputTextPT:[1,"pInputTextPT"],pInputTextUnstyled:[1,"pInputTextUnstyled"],pSize:"pSize",variant:[1,"variant"],fluid:[1,"fluid"],invalid:[1,"invalid"]},features:[H([le,{provide:ae,useExisting:e},{provide:$,useExisting:e}]),A([b]),_]})}return e})(),$i=(()=>{class e{static \u0275fac=function(i){return new(i||e)};static \u0275mod=Z({type:e});static \u0275inj=U({})}return e})();var Se=["data-p-icon","blank"],qi=(()=>{class e extends Y{static \u0275fac=(()=>{let t;return function(n){return(t||(t=p(e)))(n||e)}})();static \u0275cmp=w({type:e,selectors:[["","data-p-icon","blank"]],features:[_],attrs:Se,decls:1,vars:0,consts:[["width","1","height","1","fill","currentColor","fill-opacity","0"]],template:function(i,n){i&1&&(T(),q(0,"rect",0))},encapsulation:2})}return e})();var Te=["data-p-icon","chevron-down"],Zi=(()=>{class e extends Y{static \u0275fac=(()=>{let t;return function(n){return(t||(t=p(e)))(n||e)}})();static \u0275cmp=w({type:e,selectors:[["","data-p-icon","chevron-down"]],features:[_],attrs:Te,decls:1,vars:0,consts:[["d","M7.01744 10.398C6.91269 10.3985 6.8089 10.378 6.71215 10.3379C6.61541 10.2977 6.52766 10.2386 6.45405 10.1641L1.13907 4.84913C1.03306 4.69404 0.985221 4.5065 1.00399 4.31958C1.02276 4.13266 1.10693 3.95838 1.24166 3.82747C1.37639 3.69655 1.55301 3.61742 1.74039 3.60402C1.92777 3.59062 2.11386 3.64382 2.26584 3.75424L7.01744 8.47394L11.769 3.75424C11.9189 3.65709 12.097 3.61306 12.2748 3.62921C12.4527 3.64535 12.6199 3.72073 12.7498 3.84328C12.8797 3.96582 12.9647 4.12842 12.9912 4.30502C13.0177 4.48162 12.9841 4.662 12.8958 4.81724L7.58083 10.1322C7.50996 10.2125 7.42344 10.2775 7.32656 10.3232C7.22968 10.3689 7.12449 10.3944 7.01744 10.398Z","fill","currentColor"]],template:function(i,n){i&1&&(T(),q(0,"path",0))},encapsulation:2})}return e})();var ze=["data-p-icon","search"],Yi=(()=>{class e extends Y{pathId;onInit(){this.pathId="url(#"+ee()+")"}static \u0275fac=(()=>{let t;return function(n){return(t||(t=p(e)))(n||e)}})();static \u0275cmp=w({type:e,selectors:[["","data-p-icon","search"]],features:[_],attrs:ze,decls:5,vars:2,consts:[["fill-rule","evenodd","clip-rule","evenodd","d","M2.67602 11.0265C3.6661 11.688 4.83011 12.0411 6.02086 12.0411C6.81149 12.0411 7.59438 11.8854 8.32483 11.5828C8.87005 11.357 9.37808 11.0526 9.83317 10.6803L12.9769 13.8241C13.0323 13.8801 13.0983 13.9245 13.171 13.9548C13.2438 13.985 13.3219 14.0003 13.4007 14C13.4795 14.0003 13.5575 13.985 13.6303 13.9548C13.7031 13.9245 13.7691 13.8801 13.8244 13.8241C13.9367 13.7116 13.9998 13.5592 13.9998 13.4003C13.9998 13.2414 13.9367 13.089 13.8244 12.9765L10.6807 9.8328C11.053 9.37773 11.3573 8.86972 11.5831 8.32452C11.8857 7.59408 12.0414 6.81119 12.0414 6.02056C12.0414 4.8298 11.6883 3.66579 11.0268 2.67572C10.3652 1.68564 9.42494 0.913972 8.32483 0.45829C7.22472 0.00260857 6.01418 -0.116618 4.84631 0.115686C3.67844 0.34799 2.60568 0.921393 1.76369 1.76338C0.921698 2.60537 0.348296 3.67813 0.115991 4.84601C-0.116313 6.01388 0.00291375 7.22441 0.458595 8.32452C0.914277 9.42464 1.68595 10.3649 2.67602 11.0265ZM3.35565 2.0158C4.14456 1.48867 5.07206 1.20731 6.02086 1.20731C7.29317 1.20731 8.51338 1.71274 9.41304 2.6124C10.3127 3.51206 10.8181 4.73226 10.8181 6.00457C10.8181 6.95337 10.5368 7.88088 10.0096 8.66978C9.48251 9.45868 8.73328 10.0736 7.85669 10.4367C6.98011 10.7997 6.01554 10.8947 5.08496 10.7096C4.15439 10.5245 3.2996 10.0676 2.62869 9.39674C1.95778 8.72583 1.50089 7.87104 1.31579 6.94046C1.13068 6.00989 1.22568 5.04532 1.58878 4.16874C1.95187 3.29215 2.56675 2.54292 3.35565 2.0158Z","fill","currentColor"],[3,"id"],["width","14","height","14","fill","white"]],template:function(i,n){i&1&&(T(),Vt(0,"g"),q(1,"path",0),Dt(),Vt(2,"defs")(3,"clipPath",1),q(4,"rect",2),Dt()()),i&2&&(z("clip-path",n.pathId),u(3),jt("id",n.pathId))},encapsulation:2})}return e})();var ce=(()=>{class e extends Tt{required=k(void 0,{transform:D});invalid=k(void 0,{transform:D});disabled=k(void 0,{transform:D});name=k();_disabled=lt(!1);$disabled=X(()=>this.disabled()||this._disabled());onModelChange=()=>{};onModelTouched=()=>{};writeDisabledState(t){this._disabled.set(t)}writeControlValue(t,i){}writeValue(t){this.writeControlValue(t,this.writeModelValue.bind(this))}registerOnChange(t){this.onModelChange=t}registerOnTouched(t){this.onModelTouched=t}setDisabledState(t){this.writeDisabledState(t),this.cd.markForCheck()}static \u0275fac=(()=>{let t;return function(n){return(t||(t=p(e)))(n||e)}})();static \u0275dir=at({type:e,inputs:{required:[1,"required"],invalid:[1,"invalid"],disabled:[1,"disabled"],name:[1,"name"]},features:[_]})}return e})();var Ee=["data-p-icon","minus"],de=(()=>{class e extends Y{static \u0275fac=(()=>{let t;return function(n){return(t||(t=p(e)))(n||e)}})();static \u0275cmp=w({type:e,selectors:[["","data-p-icon","minus"]],features:[_],attrs:Ee,decls:1,vars:0,consts:[["d","M13.2222 7.77778H0.777778C0.571498 7.77778 0.373667 7.69584 0.227806 7.54998C0.0819442 7.40412 0 7.20629 0 7.00001C0 6.79373 0.0819442 6.5959 0.227806 6.45003C0.373667 6.30417 0.571498 6.22223 0.777778 6.22223H13.2222C13.4285 6.22223 13.6263 6.30417 13.7722 6.45003C13.9181 6.5959 14 6.79373 14 7.00001C14 7.20629 13.9181 7.40412 13.7722 7.54998C13.6263 7.69584 13.4285 7.77778 13.2222 7.77778Z","fill","currentColor"]],template:function(i,n){i&1&&(T(),q(0,"path",0))},encapsulation:2})}return e})();var he=`
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
`;var Ve=["icon"],De=["input"],Fe=(e,l,t)=>({checked:e,class:l,dataP:t});function Be(e,l){if(e&1&&ot(0,"span",8),e&2){let t=x(3);v(t.cx("icon")),a("ngClass",t.checkboxIcon)("pBind",t.ptm("icon")),z("data-p",t.dataP)}}function Ne(e,l){if(e&1&&(T(),ot(0,"svg",9)),e&2){let t=x(3);v(t.cx("icon")),a("pBind",t.ptm("icon")),z("data-p",t.dataP)}}function Pe(e,l){if(e&1&&(B(0),C(1,Be,1,5,"span",6)(2,Ne,1,4,"svg",7),N()),e&2){let t=x(2);u(),a("ngIf",t.checkboxIcon),u(),a("ngIf",!t.checkboxIcon)}}function Le(e,l){if(e&1&&(T(),ot(0,"svg",10)),e&2){let t=x(2);v(t.cx("icon")),a("pBind",t.ptm("icon")),z("data-p",t.dataP)}}function Oe(e,l){if(e&1&&(B(0),C(1,Pe,3,2,"ng-container",3)(2,Le,1,4,"svg",5),N()),e&2){let t=x();u(),a("ngIf",t.checked),u(),a("ngIf",t._indeterminate())}}function Ae(e,l){}function He(e,l){e&1&&C(0,Ae,0,0,"ng-template")}var Re=`
    ${he}

    /* For PrimeNG */
    p-checkBox.ng-invalid.ng-dirty .p-checkbox-box,
    p-check-box.ng-invalid.ng-dirty .p-checkbox-box,
    p-checkbox.ng-invalid.ng-dirty .p-checkbox-box {
        border-color: dt('checkbox.invalid.border.color');
    }
`,je={root:({instance:e})=>["p-checkbox p-component",{"p-checkbox-checked p-highlight":e.checked,"p-disabled":e.$disabled(),"p-invalid":e.invalid(),"p-variant-filled":e.$variant()==="filled","p-checkbox-sm p-inputfield-sm":e.size()==="small","p-checkbox-lg p-inputfield-lg":e.size()==="large"}],box:"p-checkbox-box",input:"p-checkbox-input",icon:"p-checkbox-icon"},pe=(()=>{class e extends j{name="checkbox";style=Re;classes=je;static \u0275fac=(()=>{let t;return function(n){return(t||(t=p(e)))(n||e)}})();static \u0275prov=L({token:e,factory:e.\u0275fac})}return e})();var ue=new O("CHECKBOX_INSTANCE"),$e={provide:oe,useExisting:Pt(()=>me),multi:!0},me=(()=>{class e extends ce{componentName="Checkbox";hostName="";value;binary;ariaLabelledBy;ariaLabel;tabindex;inputId;inputStyle;styleClass;inputClass;indeterminate=!1;formControl;checkboxIcon;readonly;autofocus;trueValue=!0;falseValue=!1;variant=k();size=k();onChange=new G;onFocus=new G;onBlur=new G;inputViewChild;get checked(){return this._indeterminate()?!1:this.binary?this.modelValue()===this.trueValue:Jt(this.value,this.modelValue())}_indeterminate=lt(void 0);checkboxIconTemplate;templates;_checkboxIconTemplate;focused=!1;_componentStyle=g(pe);bindDirectiveInstance=g(b,{self:!0});$pcCheckbox=g(ue,{optional:!0,skipSelf:!0})??void 0;$variant=X(()=>this.variant()||this.config.inputStyle()||this.config.inputVariant());onAfterContentInit(){this.templates?.forEach(t=>{switch(t.getType()){case"icon":this._checkboxIconTemplate=t.template;break;case"checkboxicon":this._checkboxIconTemplate=t.template;break}})}onChanges(t){t.indeterminate&&this._indeterminate.set(t.indeterminate.currentValue)}onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptms(["host","root"]))}updateModel(t){let i,n=this.injector.get(St,null,{optional:!0,self:!0}),o=n&&!this.formControl?n.value:this.modelValue();this.binary?(i=this._indeterminate()?this.trueValue:this.checked?this.falseValue:this.trueValue,this.writeModelValue(i),this.onModelChange(i)):(this.checked||this._indeterminate()?i=o.filter(s=>!Kt(s,this.value)):i=o?[...o,this.value]:[this.value],this.onModelChange(i),this.writeModelValue(i),this.formControl&&this.formControl.setValue(i)),this._indeterminate()&&this._indeterminate.set(!1),this.onChange.emit({checked:i,originalEvent:t})}handleChange(t){this.readonly||this.updateModel(t)}onInputFocus(t){this.focused=!0,this.onFocus.emit(t)}onInputBlur(t){this.focused=!1,this.onBlur.emit(t),this.onModelTouched()}focus(){this.inputViewChild?.nativeElement.focus()}writeControlValue(t,i){i(t),this.cd.markForCheck()}get dataP(){return this.cn({invalid:this.invalid(),checked:this.checked,disabled:this.$disabled(),filled:this.$variant()==="filled",[this.size()]:this.size()})}static \u0275fac=(()=>{let t;return function(n){return(t||(t=p(e)))(n||e)}})();static \u0275cmp=w({type:e,selectors:[["p-checkbox"],["p-checkBox"],["p-check-box"]],contentQueries:function(i,n,o){if(i&1&&xt(o,Ve,4)(o,kt,4),i&2){let s;M(s=V())&&(n.checkboxIconTemplate=s.first),M(s=V())&&(n.templates=s)}},viewQuery:function(i,n){if(i&1&&yt(De,5),i&2){let o;M(o=V())&&(n.inputViewChild=o.first)}},hostVars:6,hostBindings:function(i,n){i&2&&(z("data-p-highlight",n.checked)("data-p-checked",n.checked)("data-p-disabled",n.$disabled())("data-p",n.dataP),v(n.cn(n.cx("root"),n.styleClass)))},inputs:{hostName:"hostName",value:"value",binary:[2,"binary","binary",D],ariaLabelledBy:"ariaLabelledBy",ariaLabel:"ariaLabel",tabindex:[2,"tabindex","tabindex",qt],inputId:"inputId",inputStyle:"inputStyle",styleClass:"styleClass",inputClass:"inputClass",indeterminate:[2,"indeterminate","indeterminate",D],formControl:"formControl",checkboxIcon:"checkboxIcon",readonly:[2,"readonly","readonly",D],autofocus:[2,"autofocus","autofocus",D],trueValue:"trueValue",falseValue:"falseValue",variant:[1,"variant"],size:[1,"size"]},outputs:{onChange:"onChange",onFocus:"onFocus",onBlur:"onBlur"},features:[H([$e,pe,{provide:ue,useExisting:e},{provide:$,useExisting:e}]),A([b]),_],decls:5,vars:26,consts:[["input",""],["type","checkbox",3,"focus","blur","change","checked","pBind"],[3,"pBind"],[4,"ngIf"],[4,"ngTemplateOutlet","ngTemplateOutletContext"],["data-p-icon","minus",3,"class","pBind",4,"ngIf"],[3,"class","ngClass","pBind",4,"ngIf"],["data-p-icon","check",3,"class","pBind",4,"ngIf"],[3,"ngClass","pBind"],["data-p-icon","check",3,"pBind"],["data-p-icon","minus",3,"pBind"]],template:function(i,n){i&1&&(it(0,"input",1,0),dt("focus",function(s){return n.onInputFocus(s)})("blur",function(s){return n.onInputBlur(s)})("change",function(s){return n.handleChange(s)}),nt(),it(2,"div",2),C(3,Oe,3,2,"ng-container",3)(4,He,1,0,null,4),nt()),i&2&&(vt(n.inputStyle),v(n.cn(n.cx("input"),n.inputClass)),a("checked",n.checked)("pBind",n.ptm("input")),z("id",n.inputId)("value",n.value)("name",n.name())("tabindex",n.tabindex)("required",n.required()?"":void 0)("readonly",n.readonly?"":void 0)("disabled",n.$disabled()?"":void 0)("aria-labelledby",n.ariaLabelledBy)("aria-label",n.ariaLabel),u(2),v(n.cx("box")),a("pBind",n.ptm("box")),z("data-p",n.dataP),u(),a("ngIf",!n.checkboxIconTemplate&&!n._checkboxIconTemplate),u(),a("ngTemplateOutlet",n.checkboxIconTemplate||n._checkboxIconTemplate)("ngTemplateOutletContext",Qt(22,Fe,n.checked,n.cx("icon"),n.dataP)))},dependencies:[K,Ut,It,wt,R,ie,de,ut,b],encapsulation:2,changeDetection:0})}return e})(),Vn=(()=>{class e{static \u0275fac=function(i){return new(i||e)};static \u0275mod=Z({type:e});static \u0275inj=U({imports:[me,R,R]})}return e})();var fe=`
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
`;var We=["*"],Qe={root:({instance:e})=>["p-iconfield",{"p-iconfield-left":e.iconPosition=="left","p-iconfield-right":e.iconPosition=="right"}]},ge=(()=>{class e extends j{name="iconfield";style=fe;classes=Qe;static \u0275fac=(()=>{let t;return function(n){return(t||(t=p(e)))(n||e)}})();static \u0275prov=L({token:e,factory:e.\u0275fac})}return e})();var _e=new O("ICONFIELD_INSTANCE"),Un=(()=>{class e extends J{componentName="IconField";hostName="";_componentStyle=g(ge);$pcIconField=g(_e,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=g(b,{self:!0});onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptms(["host","root"]))}iconPosition="left";styleClass;static \u0275fac=(()=>{let t;return function(n){return(t||(t=p(e)))(n||e)}})();static \u0275cmp=w({type:e,selectors:[["p-iconfield"],["p-iconField"],["p-icon-field"]],hostVars:2,hostBindings:function(i,n){i&2&&v(n.cn(n.cx("root"),n.styleClass))},inputs:{hostName:"hostName",iconPosition:"iconPosition",styleClass:"styleClass"},features:[H([ge,{provide:_e,useExisting:e},{provide:$,useExisting:e}]),A([b]),_],ngContentSelectors:We,decls:1,vars:0,template:function(i,n){i&1&&(ht(),pt(0))},dependencies:[K,ut],encapsulation:2,changeDetection:0})}return e})();var qe=["*"],Ue={root:"p-inputicon"},be=(()=>{class e extends j{name="inputicon";classes=Ue;static \u0275fac=(()=>{let t;return function(n){return(t||(t=p(e)))(n||e)}})();static \u0275prov=L({token:e,factory:e.\u0275fac})}return e})(),xe=new O("INPUTICON_INSTANCE"),lo=(()=>{class e extends J{componentName="InputIcon";hostName="";styleClass;_componentStyle=g(be);$pcInputIcon=g(xe,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=g(b,{self:!0});onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptms(["host","root"]))}static \u0275fac=(()=>{let t;return function(n){return(t||(t=p(e)))(n||e)}})();static \u0275cmp=w({type:e,selectors:[["p-inputicon"],["p-inputIcon"]],hostVars:2,hostBindings:function(i,n){i&2&&v(n.cn(n.cx("root"),n.styleClass))},inputs:{hostName:"hostName",styleClass:"styleClass"},features:[H([be,{provide:xe,useExisting:e},{provide:$,useExisting:e}]),A([b]),_],ngContentSelectors:qe,decls:1,vars:0,template:function(i,n){i&1&&(ht(),pt(0))},dependencies:[K,R,ut],encapsulation:2,changeDetection:0})}return e})();var ye=["content"],Ge=["item"],Ze=["loader"],Xe=["loadericon"],Ke=["element"],Je=["*"],Nt=(e,l)=>({$implicit:e,options:l}),Ye=e=>({numCols:e}),Ie=e=>({options:e}),ti=()=>({styleClass:"p-virtualscroller-loading-icon"}),ei=(e,l)=>({rows:e,columns:l});function ii(e,l){e&1&&ct(0)}function ni(e,l){if(e&1&&(B(0),C(1,ii,1,0,"ng-container",10),N()),e&2){let t=x(2);u(),a("ngTemplateOutlet",t.contentTemplate||t._contentTemplate)("ngTemplateOutletContext",ft(2,Nt,t.loadedItems,t.getContentOptions()))}}function oi(e,l){e&1&&ct(0)}function si(e,l){if(e&1&&(B(0),C(1,oi,1,0,"ng-container",10),N()),e&2){let t=l.$implicit,i=l.index,n=x(3);u(),a("ngTemplateOutlet",n.itemTemplate||n._itemTemplate)("ngTemplateOutletContext",ft(2,Nt,t,n.getOptions(i)))}}function ri(e,l){if(e&1&&(it(0,"div",11,3),C(2,si,2,5,"ng-container",12),nt()),e&2){let t=x(2);vt(t.contentStyle),v(t.cn(t.cx("content"),t.contentStyleClass)),a("pBind",t.ptm("content")),u(2),a("ngForOf",t.loadedItems)("ngForTrackBy",t._trackBy)}}function li(e,l){if(e&1&&ot(0,"div",13),e&2){let t=x(2);v(t.cx("spacer")),a("ngStyle",t.spacerStyle)("pBind",t.ptm("spacer"))}}function ai(e,l){e&1&&ct(0)}function ci(e,l){if(e&1&&(B(0),C(1,ai,1,0,"ng-container",10),N()),e&2){let t=l.index,i=x(4);u(),a("ngTemplateOutlet",i.loaderTemplate||i._loaderTemplate)("ngTemplateOutletContext",Ct(4,Ie,i.getLoaderOptions(t,i.both&&Ct(2,Ye,i.numItemsInViewport.cols))))}}function di(e,l){if(e&1&&(B(0),C(1,ci,2,6,"ng-container",14),N()),e&2){let t=x(3);u(),a("ngForOf",t.loaderArr)}}function hi(e,l){e&1&&ct(0)}function pi(e,l){if(e&1&&(B(0),C(1,hi,1,0,"ng-container",10),N()),e&2){let t=x(4);u(),a("ngTemplateOutlet",t.loaderIconTemplate||t._loaderIconTemplate)("ngTemplateOutletContext",Ct(3,Ie,Wt(2,ti)))}}function ui(e,l){if(e&1&&(T(),ot(0,"svg",15)),e&2){let t=x(4);v(t.cx("loadingIcon")),a("spin",!0)("pBind",t.ptm("loadingIcon"))}}function mi(e,l){if(e&1&&C(0,pi,2,5,"ng-container",6)(1,ui,1,4,"ng-template",null,5,gt),e&2){let t=mt(2),i=x(3);a("ngIf",i.loaderIconTemplate||i._loaderIconTemplate)("ngIfElse",t)}}function fi(e,l){if(e&1&&(it(0,"div",11),C(1,di,2,1,"ng-container",6)(2,mi,3,2,"ng-template",null,4,gt),nt()),e&2){let t=mt(3),i=x(2);v(i.cx("loader")),a("pBind",i.ptm("loader")),u(),a("ngIf",i.loaderTemplate||i._loaderTemplate)("ngIfElse",t)}}function gi(e,l){if(e&1){let t=Rt();B(0),it(1,"div",7,1),dt("scroll",function(n){Lt(t);let o=x();return Ot(o.onContainerScroll(n))}),C(3,ni,2,5,"ng-container",6)(4,ri,3,7,"ng-template",null,2,gt)(6,li,1,4,"div",8)(7,fi,4,5,"div",9),nt(),N()}if(e&2){let t=mt(5),i=x();u(),v(i.cn(i.cx("root"),i.styleClass)),a("ngStyle",i._style)("pBind",i.ptm("root")),z("id",i._id)("tabindex",i.tabindex),u(2),a("ngIf",i.contentTemplate||i._contentTemplate)("ngIfElse",t),u(3),a("ngIf",i._showSpacer),u(),a("ngIf",!i.loaderDisabled&&i._showLoader&&i.d_loading)}}function _i(e,l){e&1&&ct(0)}function bi(e,l){if(e&1&&(B(0),C(1,_i,1,0,"ng-container",10),N()),e&2){let t=x(2);u(),a("ngTemplateOutlet",t.contentTemplate||t._contentTemplate)("ngTemplateOutletContext",ft(5,Nt,t.items,ft(2,ei,t._items,t.loadedColumns)))}}function xi(e,l){if(e&1&&(pt(0),C(1,bi,2,8,"ng-container",16)),e&2){let t=x();u(),a("ngIf",t.contentTemplate||t._contentTemplate)}}var yi=`
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
`,vi={root:({instance:e})=>["p-virtualscroller",{"p-virtualscroller-inline":e.inline,"p-virtualscroller-both p-both-scroll":e.both,"p-virtualscroller-horizontal p-horizontal-scroll":e.horizontal}],content:"p-virtualscroller-content",spacer:"p-virtualscroller-spacer",loader:({instance:e})=>["p-virtualscroller-loader",{"p-virtualscroller-loader-mask":!e.loaderTemplate}],loadingIcon:"p-virtualscroller-loading-icon"},ve=(()=>{class e extends j{name="virtualscroller";css=yi;classes=vi;static \u0275fac=(()=>{let t;return function(n){return(t||(t=p(e)))(n||e)}})();static \u0275prov=L({token:e,factory:e.\u0275fac})}return e})();var Ce=new O("SCROLLER_INSTANCE"),Ci=(()=>{class e extends J{zone;componentName="VirtualScroller";bindDirectiveInstance=g(b,{self:!0});$pcScroller=g(Ce,{optional:!0,skipSelf:!0})??void 0;hostName="";get id(){return this._id}set id(t){this._id=t}get style(){return this._style}set style(t){this._style=t}get styleClass(){return this._styleClass}set styleClass(t){this._styleClass=t}get tabindex(){return this._tabindex}set tabindex(t){this._tabindex=t}get items(){return this._items}set items(t){this._items=t}get itemSize(){return this._itemSize}set itemSize(t){this._itemSize=t}get scrollHeight(){return this._scrollHeight}set scrollHeight(t){this._scrollHeight=t}get scrollWidth(){return this._scrollWidth}set scrollWidth(t){this._scrollWidth=t}get orientation(){return this._orientation}set orientation(t){this._orientation=t}get step(){return this._step}set step(t){this._step=t}get delay(){return this._delay}set delay(t){this._delay=t}get resizeDelay(){return this._resizeDelay}set resizeDelay(t){this._resizeDelay=t}get appendOnly(){return this._appendOnly}set appendOnly(t){this._appendOnly=t}get inline(){return this._inline}set inline(t){this._inline=t}get lazy(){return this._lazy}set lazy(t){this._lazy=t}get disabled(){return this._disabled}set disabled(t){this._disabled=t}get loaderDisabled(){return this._loaderDisabled}set loaderDisabled(t){this._loaderDisabled=t}get columns(){return this._columns}set columns(t){this._columns=t}get showSpacer(){return this._showSpacer}set showSpacer(t){this._showSpacer=t}get showLoader(){return this._showLoader}set showLoader(t){this._showLoader=t}get numToleratedItems(){return this._numToleratedItems}set numToleratedItems(t){this._numToleratedItems=t}get loading(){return this._loading}set loading(t){this._loading=t}get autoSize(){return this._autoSize}set autoSize(t){this._autoSize=t}get trackBy(){return this._trackBy}set trackBy(t){this._trackBy=t}get options(){return this._options}set options(t){this._options=t,t&&typeof t=="object"&&(Object.entries(t).forEach(([i,n])=>this[`_${i}`]!==n&&(this[`_${i}`]=n)),Object.entries(t).forEach(([i,n])=>this[`${i}`]!==n&&(this[`${i}`]=n)))}onLazyLoad=new G;onScroll=new G;onScrollIndexChange=new G;elementViewChild;contentViewChild;height;_id;_style;_styleClass;_tabindex=0;_items;_itemSize=0;_scrollHeight;_scrollWidth;_orientation="vertical";_step=0;_delay=0;_resizeDelay=10;_appendOnly=!1;_inline=!1;_lazy=!1;_disabled=!1;_loaderDisabled=!1;_columns;_showSpacer=!0;_showLoader=!1;_numToleratedItems;_loading;_autoSize=!1;_trackBy;_options;d_loading=!1;d_numToleratedItems;contentEl;contentTemplate;itemTemplate;loaderTemplate;loaderIconTemplate;templates;_contentTemplate;_itemTemplate;_loaderTemplate;_loaderIconTemplate;first=0;last=0;page=0;isRangeChanged=!1;numItemsInViewport=0;lastScrollPos=0;lazyLoadState={};loaderArr=[];spacerStyle={};contentStyle={};scrollTimeout;resizeTimeout;initialized=!1;windowResizeListener;defaultWidth;defaultHeight;defaultContentWidth;defaultContentHeight;_contentStyleClass;get contentStyleClass(){return this._contentStyleClass}set contentStyleClass(t){this._contentStyleClass=t}get vertical(){return this._orientation==="vertical"}get horizontal(){return this._orientation==="horizontal"}get both(){return this._orientation==="both"}get loadedItems(){return this._items&&!this.d_loading?this.both?this._items.slice(this._appendOnly?0:this.first.rows,this.last.rows).map(t=>this._columns?t:Array.isArray(t)?t.slice(this._appendOnly?0:this.first.cols,this.last.cols):t):this.horizontal&&this._columns?this._items:this._items.slice(this._appendOnly?0:this.first,this.last):[]}get loadedRows(){return this.d_loading?this._loaderDisabled?this.loaderArr:[]:this.loadedItems}get loadedColumns(){return this._columns&&(this.both||this.horizontal)?this.d_loading&&this._loaderDisabled?this.both?this.loaderArr[0]:this.loaderArr:this._columns.slice(this.both?this.first.cols:this.first,this.both?this.last.cols:this.last):this._columns}_componentStyle=g(ve);constructor(t){super(),this.zone=t}onInit(){this.setInitialState()}onChanges(t){let i=!1;if(this.scrollHeight=="100%"&&(this.height="100%"),t.loading){let{previousValue:n,currentValue:o}=t.loading;this.lazy&&n!==o&&o!==this.d_loading&&(this.d_loading=o,i=!0)}if(t.orientation&&(this.lastScrollPos=this.both?{top:0,left:0}:0),t.numToleratedItems){let{previousValue:n,currentValue:o}=t.numToleratedItems;n!==o&&o!==this.d_numToleratedItems&&(this.d_numToleratedItems=o)}if(t.options){let{previousValue:n,currentValue:o}=t.options;this.lazy&&n?.loading!==o?.loading&&o?.loading!==this.d_loading&&(this.d_loading=o.loading,i=!0),n?.numToleratedItems!==o?.numToleratedItems&&o?.numToleratedItems!==this.d_numToleratedItems&&(this.d_numToleratedItems=o.numToleratedItems)}this.initialized&&!i&&(t.items?.previousValue?.length!==t.items?.currentValue?.length||t.itemSize||t.scrollHeight||t.scrollWidth)&&this.init()}onAfterContentInit(){this.templates.forEach(t=>{switch(t.getType()){case"content":this._contentTemplate=t.template;break;case"item":this._itemTemplate=t.template;break;case"loader":this._loaderTemplate=t.template;break;case"loadericon":this._loaderIconTemplate=t.template;break;default:this._itemTemplate=t.template;break}})}onAfterViewInit(){Promise.resolve().then(()=>{this.viewInit()})}onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptm("host")),this.initialized||this.viewInit()}onDestroy(){this.unbindResizeListener(),this.contentEl=null,this.initialized=!1}viewInit(){Ft(this.platformId)&&!this.initialized&&Bt(this.elementViewChild?.nativeElement)&&(this.setInitialState(),this.setContentEl(this.contentEl),this.init(),this.defaultWidth=rt(this.elementViewChild?.nativeElement),this.defaultHeight=st(this.elementViewChild?.nativeElement),this.defaultContentWidth=rt(this.contentEl),this.defaultContentHeight=st(this.contentEl),this.initialized=!0)}init(){this._disabled||(this.bindResizeListener(),setTimeout(()=>{this.setSpacerSize(),this.setSize(),this.calculateOptions(),this.calculateAutoSize(),this.cd.detectChanges()},1))}setContentEl(t){this.contentEl=t||this.contentViewChild?.nativeElement||Yt(this.elementViewChild?.nativeElement,".p-virtualscroller-content")}setInitialState(){this.first=this.both?{rows:0,cols:0}:0,this.last=this.both?{rows:0,cols:0}:0,this.numItemsInViewport=this.both?{rows:0,cols:0}:0,this.lastScrollPos=this.both?{top:0,left:0}:0,(this.d_loading===void 0||this.d_loading===!1)&&(this.d_loading=this._loading||!1),this.d_numToleratedItems=this._numToleratedItems,this.loaderArr=this.loaderArr.length>0?this.loaderArr:[]}getElementRef(){return this.elementViewChild}getPageByFirst(t){return Math.floor(((t??this.first)+this.d_numToleratedItems*4)/(this._step||1))}isPageChanged(t){return this._step?this.page!==this.getPageByFirst(t??this.first):!0}scrollTo(t){this.elementViewChild?.nativeElement?.scrollTo(t)}scrollToIndex(t,i="auto"){if(this.both?t.every(o=>o>-1):t>-1){let o=this.first,{scrollTop:s=0,scrollLeft:r=0}=this.elementViewChild?.nativeElement,{numToleratedItems:y}=this.calculateNumItems(),m=this.getContentPosition(),h=this.itemSize,E=(d=0,f)=>d<=f?0:d,I=(d,f,F)=>d*f+F,P=(d=0,f=0)=>this.scrollTo({left:d,top:f,behavior:i}),S=this.both?{rows:0,cols:0}:0,tt=!1,c=!1;this.both?(S={rows:E(t[0],y[0]),cols:E(t[1],y[1])},P(I(S.cols,h[1],m.left),I(S.rows,h[0],m.top)),c=this.lastScrollPos.top!==s||this.lastScrollPos.left!==r,tt=S.rows!==o.rows||S.cols!==o.cols):(S=E(t,y),this.horizontal?P(I(S,h,m.left),s):P(r,I(S,h,m.top)),c=this.lastScrollPos!==(this.horizontal?r:s),tt=S!==o),this.isRangeChanged=tt,c&&(this.first=S)}}scrollInView(t,i,n="auto"){if(i){let{first:o,viewport:s}=this.getRenderedRange(),r=(h=0,E=0)=>this.scrollTo({left:h,top:E,behavior:n}),y=i==="to-start",m=i==="to-end";if(y){if(this.both)s.first.rows-o.rows>t[0]?r(s.first.cols*this._itemSize[1],(s.first.rows-1)*this._itemSize[0]):s.first.cols-o.cols>t[1]&&r((s.first.cols-1)*this._itemSize[1],s.first.rows*this._itemSize[0]);else if(s.first-o>t){let h=(s.first-1)*this._itemSize;this.horizontal?r(h,0):r(0,h)}}else if(m){if(this.both)s.last.rows-o.rows<=t[0]+1?r(s.first.cols*this._itemSize[1],(s.first.rows+1)*this._itemSize[0]):s.last.cols-o.cols<=t[1]+1&&r((s.first.cols+1)*this._itemSize[1],s.first.rows*this._itemSize[0]);else if(s.last-o<=t+1){let h=(s.first+1)*this._itemSize;this.horizontal?r(h,0):r(0,h)}}}else this.scrollToIndex(t,n)}getRenderedRange(){let t=(o,s)=>s||o?Math.floor(o/(s||o)):0,i=this.first,n=0;if(this.elementViewChild?.nativeElement){let{scrollTop:o,scrollLeft:s}=this.elementViewChild.nativeElement;if(this.both)i={rows:t(o,this._itemSize[0]),cols:t(s,this._itemSize[1])},n={rows:i.rows+this.numItemsInViewport.rows,cols:i.cols+this.numItemsInViewport.cols};else{let r=this.horizontal?s:o;i=t(r,this._itemSize),n=i+this.numItemsInViewport}}return{first:this.first,last:this.last,viewport:{first:i,last:n}}}calculateNumItems(){let t=this.getContentPosition(),i=(this.elementViewChild?.nativeElement?this.elementViewChild.nativeElement.offsetWidth-t.left:0)||0,n=(this.elementViewChild?.nativeElement?this.elementViewChild.nativeElement.offsetHeight-t.top:0)||0,o=(m,h)=>h||m?Math.ceil(m/(h||m)):0,s=m=>Math.ceil(m/2),r=this.both?{rows:o(n,this._itemSize[0]),cols:o(i,this._itemSize[1])}:o(this.horizontal?i:n,this._itemSize),y=this.d_numToleratedItems||(this.both?[s(r.rows),s(r.cols)]:s(r));return{numItemsInViewport:r,numToleratedItems:y}}calculateOptions(){let{numItemsInViewport:t,numToleratedItems:i}=this.calculateNumItems(),n=(r,y,m,h=!1)=>this.getLast(r+y+(r<m?2:3)*m,h),o=this.first,s=this.both?{rows:n(this.first.rows,t.rows,i[0]),cols:n(this.first.cols,t.cols,i[1],!0)}:n(this.first,t,i);this.last=s,this.numItemsInViewport=t,this.d_numToleratedItems=i,this._showLoader&&(this.loaderArr=this.both?Array.from({length:t.rows}).map(()=>Array.from({length:t.cols})):Array.from({length:t})),this._lazy&&Promise.resolve().then(()=>{this.lazyLoadState={first:this._step?this.both?{rows:0,cols:o.cols}:0:o,last:Math.min(this._step?this._step:this.last,this._items.length)},this.handleEvents("onLazyLoad",this.lazyLoadState)})}calculateAutoSize(){this._autoSize&&!this.d_loading&&Promise.resolve().then(()=>{if(this.contentEl){this.contentEl.style.minHeight=this.contentEl.style.minWidth="auto",this.contentEl.style.position="relative",this.elementViewChild.nativeElement.style.contain="none";let[t,i]=[rt(this.contentEl),st(this.contentEl)];t!==this.defaultContentWidth&&(this.elementViewChild.nativeElement.style.width=""),i!==this.defaultContentHeight&&(this.elementViewChild.nativeElement.style.height="");let[n,o]=[rt(this.elementViewChild.nativeElement),st(this.elementViewChild.nativeElement)];(this.both||this.horizontal)&&(this.elementViewChild.nativeElement.style.width=n<this.defaultWidth?n+"px":this._scrollWidth||this.defaultWidth+"px"),(this.both||this.vertical)&&(this.elementViewChild.nativeElement.style.height=o<this.defaultHeight?o+"px":this._scrollHeight||this.defaultHeight+"px"),this.contentEl.style.minHeight=this.contentEl.style.minWidth="",this.contentEl.style.position="",this.elementViewChild.nativeElement.style.contain=""}})}getLast(t=0,i=!1){return this._items?Math.min(i?(this._columns||this._items[0]).length:this._items.length,t):0}getContentPosition(){if(this.contentEl){let t=getComputedStyle(this.contentEl),i=parseFloat(t.paddingLeft)+Math.max(parseFloat(t.left)||0,0),n=parseFloat(t.paddingRight)+Math.max(parseFloat(t.right)||0,0),o=parseFloat(t.paddingTop)+Math.max(parseFloat(t.top)||0,0),s=parseFloat(t.paddingBottom)+Math.max(parseFloat(t.bottom)||0,0);return{left:i,right:n,top:o,bottom:s,x:i+n,y:o+s}}return{left:0,right:0,top:0,bottom:0,x:0,y:0}}setSize(){if(this.elementViewChild?.nativeElement){let t=this.elementViewChild.nativeElement,i=t.parentElement?.parentElement,n=t.offsetWidth,o=i?.offsetWidth||0,s=this._scrollWidth||`${n||o}px`,r=t.offsetHeight,y=i?.offsetHeight||0,m=this._scrollHeight||`${r||y}px`,h=(E,I)=>t.style[E]=I;this.both||this.horizontal?(h("height",m),h("width",s)):h("height",m)}}setSpacerSize(){if(this._items){let t=this.getContentPosition(),i=(n,o,s,r=0)=>this.spacerStyle=Et(bt({},this.spacerStyle),{[`${n}`]:(o||[]).length*s+r+"px"});this.both?(i("height",this._items,this._itemSize[0],t.y),i("width",this._columns||this._items[1],this._itemSize[1],t.x)):this.horizontal?i("width",this._columns||this._items,this._itemSize,t.x):i("height",this._items,this._itemSize,t.y)}}setContentPosition(t){if(this.contentEl&&!this._appendOnly){let i=t?t.first:this.first,n=(s,r)=>s*r,o=(s=0,r=0)=>this.contentStyle=Et(bt({},this.contentStyle),{transform:`translate3d(${s}px, ${r}px, 0)`});if(this.both)o(n(i.cols,this._itemSize[1]),n(i.rows,this._itemSize[0]));else{let s=n(i,this._itemSize);this.horizontal?o(s,0):o(0,s)}}}onScrollPositionChange(t){let i=t.target;if(!i)throw new Error("Event target is null");let n=this.getContentPosition(),o=(c,d)=>c?c>d?c-d:c:0,s=(c,d)=>d||c?Math.floor(c/(d||c)):0,r=(c,d,f,F,Q,et)=>c<=Q?Q:et?f-F-Q:d+Q-1,y=(c,d,f,F,Q,et,_t)=>c<=et?0:Math.max(0,_t?c<d?f:c-et:c>d?f:c-2*et),m=(c,d,f,F,Q,et=!1)=>{let _t=d+F+2*Q;return c>=Q&&(_t+=Q+1),this.getLast(_t,et)},h=o(i.scrollTop,n.top),E=o(i.scrollLeft,n.left),I=this.both?{rows:0,cols:0}:0,P=this.last,S=!1,tt=this.lastScrollPos;if(this.both){let c=this.lastScrollPos.top<=h,d=this.lastScrollPos.left<=E;if(!this._appendOnly||this._appendOnly&&(c||d)){let f={rows:s(h,this._itemSize[0]),cols:s(E,this._itemSize[1])},F={rows:r(f.rows,this.first.rows,this.last.rows,this.numItemsInViewport.rows,this.d_numToleratedItems[0],c),cols:r(f.cols,this.first.cols,this.last.cols,this.numItemsInViewport.cols,this.d_numToleratedItems[1],d)};I={rows:y(f.rows,F.rows,this.first.rows,this.last.rows,this.numItemsInViewport.rows,this.d_numToleratedItems[0],c),cols:y(f.cols,F.cols,this.first.cols,this.last.cols,this.numItemsInViewport.cols,this.d_numToleratedItems[1],d)},P={rows:m(f.rows,I.rows,this.last.rows,this.numItemsInViewport.rows,this.d_numToleratedItems[0]),cols:m(f.cols,I.cols,this.last.cols,this.numItemsInViewport.cols,this.d_numToleratedItems[1],!0)},S=I.rows!==this.first.rows||P.rows!==this.last.rows||I.cols!==this.first.cols||P.cols!==this.last.cols||this.isRangeChanged,tt={top:h,left:E}}}else{let c=this.horizontal?E:h,d=this.lastScrollPos<=c;if(!this._appendOnly||this._appendOnly&&d){let f=s(c,this._itemSize),F=r(f,this.first,this.last,this.numItemsInViewport,this.d_numToleratedItems,d);I=y(f,F,this.first,this.last,this.numItemsInViewport,this.d_numToleratedItems,d),P=m(f,I,this.last,this.numItemsInViewport,this.d_numToleratedItems),S=I!==this.first||P!==this.last||this.isRangeChanged,tt=c}}return{first:I,last:P,isRangeChanged:S,scrollPos:tt}}onScrollChange(t){let{first:i,last:n,isRangeChanged:o,scrollPos:s}=this.onScrollPositionChange(t);if(o){let r={first:i,last:n};if(this.setContentPosition(r),this.first=i,this.last=n,this.lastScrollPos=s,this.handleEvents("onScrollIndexChange",r),this._lazy&&this.isPageChanged(i)){let y={first:this._step?Math.min(this.getPageByFirst(i)*this._step,this._items.length-this._step):i,last:Math.min(this._step?(this.getPageByFirst(i)+1)*this._step:n,this._items.length)};(this.lazyLoadState.first!==y.first||this.lazyLoadState.last!==y.last)&&this.handleEvents("onLazyLoad",y),this.lazyLoadState=y}}}onContainerScroll(t){if(this.handleEvents("onScroll",{originalEvent:t}),this._delay){if(this.scrollTimeout&&clearTimeout(this.scrollTimeout),!this.d_loading&&this._showLoader){let{isRangeChanged:i}=this.onScrollPositionChange(t);(i||this._step&&this.isPageChanged())&&(this.d_loading=!0,this.cd.detectChanges())}this.scrollTimeout=setTimeout(()=>{this.onScrollChange(t),this.d_loading&&this._showLoader&&(!this._lazy||this._loading===void 0)&&(this.d_loading=!1,this.page=this.getPageByFirst()),this.cd.detectChanges()},this._delay)}else!this.d_loading&&this.onScrollChange(t)}bindResizeListener(){Ft(this.platformId)&&(this.windowResizeListener||this.zone.runOutsideAngular(()=>{let t=this.document.defaultView,i=te()?"orientationchange":"resize";this.windowResizeListener=this.renderer.listen(t,i,this.onWindowResize.bind(this))}))}unbindResizeListener(){this.windowResizeListener&&(this.windowResizeListener(),this.windowResizeListener=null)}onWindowResize(){this.resizeTimeout&&clearTimeout(this.resizeTimeout),this.resizeTimeout=setTimeout(()=>{if(Bt(this.elementViewChild?.nativeElement)){let[t,i]=[rt(this.elementViewChild?.nativeElement),st(this.elementViewChild?.nativeElement)],[n,o]=[t!==this.defaultWidth,i!==this.defaultHeight];(this.both?n||o:this.horizontal?n:this.vertical&&o)&&this.zone.run(()=>{this.d_numToleratedItems=this._numToleratedItems,this.defaultWidth=t,this.defaultHeight=i,this.defaultContentWidth=rt(this.contentEl),this.defaultContentHeight=st(this.contentEl),this.init()})}},this._resizeDelay)}handleEvents(t,i){return this.options&&this.options[t]?this.options[t](i):this[t].emit(i)}getContentOptions(){return{contentStyleClass:`p-virtualscroller-content ${this.d_loading?"p-virtualscroller-loading":""}`,items:this.loadedItems,getItemOptions:t=>this.getOptions(t),loading:this.d_loading,getLoaderOptions:(t,i)=>this.getLoaderOptions(t,i),itemSize:this._itemSize,rows:this.loadedRows,columns:this.loadedColumns,spacerStyle:this.spacerStyle,contentStyle:this.contentStyle,vertical:this.vertical,horizontal:this.horizontal,both:this.both,scrollTo:this.scrollTo.bind(this),scrollToIndex:this.scrollToIndex.bind(this),orientation:this._orientation,scrollableElement:this.elementViewChild?.nativeElement}}getOptions(t){let i=(this._items||[]).length,n=this.both?this.first.rows+t:this.first+t;return{index:n,count:i,first:n===0,last:n===i-1,even:n%2===0,odd:n%2!==0}}getLoaderOptions(t,i){let n=this.loaderArr.length;return bt({index:t,count:n,first:t===0,last:t===n-1,even:t%2===0,odd:t%2!==0,loading:this.d_loading},i)}static \u0275fac=function(i){return new(i||e)(Ht(At))};static \u0275cmp=w({type:e,selectors:[["p-scroller"],["p-virtualscroller"],["p-virtual-scroller"],["p-virtualScroller"]],contentQueries:function(i,n,o){if(i&1&&xt(o,ye,4)(o,Ge,4)(o,Ze,4)(o,Xe,4)(o,kt,4),i&2){let s;M(s=V())&&(n.contentTemplate=s.first),M(s=V())&&(n.itemTemplate=s.first),M(s=V())&&(n.loaderTemplate=s.first),M(s=V())&&(n.loaderIconTemplate=s.first),M(s=V())&&(n.templates=s)}},viewQuery:function(i,n){if(i&1&&yt(Ke,5)(ye,5),i&2){let o;M(o=V())&&(n.elementViewChild=o.first),M(o=V())&&(n.contentViewChild=o.first)}},hostVars:2,hostBindings:function(i,n){i&2&&$t("height",n.height)},inputs:{hostName:"hostName",id:"id",style:"style",styleClass:"styleClass",tabindex:"tabindex",items:"items",itemSize:"itemSize",scrollHeight:"scrollHeight",scrollWidth:"scrollWidth",orientation:"orientation",step:"step",delay:"delay",resizeDelay:"resizeDelay",appendOnly:"appendOnly",inline:"inline",lazy:"lazy",disabled:"disabled",loaderDisabled:"loaderDisabled",columns:"columns",showSpacer:"showSpacer",showLoader:"showLoader",numToleratedItems:"numToleratedItems",loading:"loading",autoSize:"autoSize",trackBy:"trackBy",options:"options"},outputs:{onLazyLoad:"onLazyLoad",onScroll:"onScroll",onScrollIndexChange:"onScrollIndexChange"},features:[H([ve,{provide:Ce,useExisting:e},{provide:$,useExisting:e}]),A([b]),_],ngContentSelectors:Je,decls:3,vars:2,consts:[["disabledContainer",""],["element",""],["buildInContent",""],["content",""],["buildInLoader",""],["buildInLoaderIcon",""],[4,"ngIf","ngIfElse"],[3,"scroll","ngStyle","pBind"],[3,"class","ngStyle","pBind",4,"ngIf"],[3,"class","pBind",4,"ngIf"],[4,"ngTemplateOutlet","ngTemplateOutletContext"],[3,"pBind"],[4,"ngFor","ngForOf","ngForTrackBy"],[3,"ngStyle","pBind"],[4,"ngFor","ngForOf"],["data-p-icon","spinner",3,"spin","pBind"],[4,"ngIf"]],template:function(i,n){if(i&1&&(ht(),C(0,gi,8,10,"ng-container",6)(1,xi,2,1,"ng-template",null,0,gt)),i&2){let o=mt(2);a("ngIf",!n._disabled)("ngIfElse",o)}},dependencies:[K,Gt,It,wt,Zt,ne,R,b],encapsulation:2})}return e})(),Eo=(()=>{class e{static \u0275fac=function(i){return new(i||e)};static \u0275mod=Z({type:e});static \u0275inj=U({imports:[Ci,R,R]})}return e})();export{qi as a,Zi as b,Yi as c,Tt as d,ji as e,$i as f,ce as g,me as h,Vn as i,Un as j,lo as k,Ci as l,Eo as m};
