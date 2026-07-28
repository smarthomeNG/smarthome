import{i as x,v as W}from"./chunk-XVJEVSJM.js";import{k as q}from"./chunk-4IPD53LF.js";import{V as G,X as P,Z as r,_ as R}from"./chunk-JGSTUQPT.js";import{ga as $,ha as j,r as z,v as Q}from"./chunk-XAETJXNU.js";import{$b as u,Ab as M,Fb as a,Gb as w,Hb as b,Ob as I,Pc as H,Tb as f,U as k,V as y,Vb as V,Wa as g,Y as v,Yb as F,Yc as m,Zb as A,Zc as O,_ as c,_b as h,gc as L,hc as s,ib as T,la as C,mb as _,nb as S,ob as E,tc as D,ua as p,vc as N,wb as d,zb as B}from"./chunk-BDB7QD2D.js";var U=`
    .p-toggleswitch {
        display: inline-block;
        width: dt('toggleswitch.width');
        height: dt('toggleswitch.height');
    }

    .p-toggleswitch-input {
        cursor: pointer;
        appearance: none;
        position: absolute;
        top: 0;
        inset-inline-start: 0;
        width: 100%;
        height: 100%;
        padding: 0;
        margin: 0;
        opacity: 0;
        z-index: 1;
        outline: 0 none;
        border-radius: dt('toggleswitch.border.radius');
    }

    .p-toggleswitch-slider {
        cursor: pointer;
        width: 100%;
        height: 100%;
        border-width: dt('toggleswitch.border.width');
        border-style: solid;
        border-color: dt('toggleswitch.border.color');
        background: dt('toggleswitch.background');
        transition:
            background dt('toggleswitch.transition.duration'),
            color dt('toggleswitch.transition.duration'),
            border-color dt('toggleswitch.transition.duration'),
            outline-color dt('toggleswitch.transition.duration'),
            box-shadow dt('toggleswitch.transition.duration');
        border-radius: dt('toggleswitch.border.radius');
        outline-color: transparent;
        box-shadow: dt('toggleswitch.shadow');
    }

    .p-toggleswitch-handle {
        position: absolute;
        top: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        background: dt('toggleswitch.handle.background');
        color: dt('toggleswitch.handle.color');
        width: dt('toggleswitch.handle.size');
        height: dt('toggleswitch.handle.size');
        inset-inline-start: dt('toggleswitch.gap');
        margin-block-start: calc(-1 * calc(dt('toggleswitch.handle.size') / 2));
        border-radius: dt('toggleswitch.handle.border.radius');
        transition:
            background dt('toggleswitch.transition.duration'),
            color dt('toggleswitch.transition.duration'),
            inset-inline-start dt('toggleswitch.slide.duration'),
            box-shadow dt('toggleswitch.slide.duration');
    }

    .p-toggleswitch.p-toggleswitch-checked .p-toggleswitch-slider {
        background: dt('toggleswitch.checked.background');
        border-color: dt('toggleswitch.checked.border.color');
    }

    .p-toggleswitch.p-toggleswitch-checked .p-toggleswitch-handle {
        background: dt('toggleswitch.handle.checked.background');
        color: dt('toggleswitch.handle.checked.color');
        inset-inline-start: calc(dt('toggleswitch.width') - calc(dt('toggleswitch.handle.size') + dt('toggleswitch.gap')));
    }

    .p-toggleswitch:not(.p-disabled):has(.p-toggleswitch-input:hover) .p-toggleswitch-slider {
        background: dt('toggleswitch.hover.background');
        border-color: dt('toggleswitch.hover.border.color');
    }

    .p-toggleswitch:not(.p-disabled):has(.p-toggleswitch-input:hover) .p-toggleswitch-handle {
        background: dt('toggleswitch.handle.hover.background');
        color: dt('toggleswitch.handle.hover.color');
    }

    .p-toggleswitch:not(.p-disabled):has(.p-toggleswitch-input:hover).p-toggleswitch-checked .p-toggleswitch-slider {
        background: dt('toggleswitch.checked.hover.background');
        border-color: dt('toggleswitch.checked.hover.border.color');
    }

    .p-toggleswitch:not(.p-disabled):has(.p-toggleswitch-input:hover).p-toggleswitch-checked .p-toggleswitch-handle {
        background: dt('toggleswitch.handle.checked.hover.background');
        color: dt('toggleswitch.handle.checked.hover.color');
    }

    .p-toggleswitch:not(.p-disabled):has(.p-toggleswitch-input:focus-visible) .p-toggleswitch-slider {
        box-shadow: dt('toggleswitch.focus.ring.shadow');
        outline: dt('toggleswitch.focus.ring.width') dt('toggleswitch.focus.ring.style') dt('toggleswitch.focus.ring.color');
        outline-offset: dt('toggleswitch.focus.ring.offset');
    }

    .p-toggleswitch.p-invalid > .p-toggleswitch-slider {
        border-color: dt('toggleswitch.invalid.border.color');
    }

    .p-toggleswitch.p-disabled {
        opacity: 1;
    }

    .p-toggleswitch.p-disabled .p-toggleswitch-slider {
        background: dt('toggleswitch.disabled.background');
    }

    .p-toggleswitch.p-disabled .p-toggleswitch-handle {
        background: dt('toggleswitch.handle.disabled.background');
    }
`;var Y=["handle"],Z=["input"],ee=t=>({checked:t});function te(t,X){t&1&&I(0)}function ie(t,X){if(t&1&&E(0,te,1,0,"ng-container",3),t&2){let i=V();a("ngTemplateOutlet",i.handleTemplate||i._handleTemplate)("ngTemplateOutletContext",N(2,ee,i.checked()))}}var ne=`
    ${U}

    p-toggleswitch.ng-invalid.ng-dirty > .p-toggleswitch-slider {
        border-color: dt('toggleswitch.invalid.border.color');
    }
`,oe={root:{position:"relative"}},le={root:({instance:t})=>["p-toggleswitch p-component",{"p-toggleswitch p-component":!0,"p-toggleswitch-checked":t.checked(),"p-disabled":t.$disabled(),"p-invalid":t.invalid()}],input:"p-toggleswitch-input",slider:"p-toggleswitch-slider",handle:"p-toggleswitch-handle"},J=(()=>{class t extends G{name="toggleswitch";style=ne;classes=le;inlineStyles=oe;static \u0275fac=(()=>{let i;return function(e){return(i||(i=p(t)))(e||t)}})();static \u0275prov=y({token:t,factory:t.\u0275fac})}return t})();var K=new v("TOGGLESWITCH_INSTANCE"),de={provide:q,useExisting:k(()=>ae),multi:!0},ae=(()=>{class t extends W{componentName="ToggleSwitch";$pcToggleSwitch=c(K,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=c(r,{self:!0});onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptms(["host","root"]))}styleClass;tabindex;inputId;readonly;trueValue=!0;falseValue=!1;ariaLabel;size=H();ariaLabelledBy;autofocus;onChange=new C;input;handleTemplate;_handleTemplate;focused=!1;_componentStyle=c(J);templates;onHostClick(i){this.onClick(i)}onAfterContentInit(){this.templates.forEach(i=>{i.getType()==="handle"?this._handleTemplate=i.template:this._handleTemplate=i.template})}onClick(i){!this.$disabled()&&!this.readonly&&(this.writeModelValue(this.checked()?this.falseValue:this.trueValue),this.onModelChange(this.modelValue()),this.onChange.emit({originalEvent:i,checked:this.modelValue()}),this.input.nativeElement.focus())}onFocus(){this.focused=!0}onBlur(){this.focused=!1,this.onModelTouched()}checked(){return this.modelValue()===this.trueValue}writeControlValue(i,n){n(i),this.cd.markForCheck()}get dataP(){return this.cn({checked:this.checked(),disabled:this.$disabled(),invalid:this.invalid()})}static \u0275fac=(()=>{let i;return function(e){return(i||(i=p(t)))(e||t)}})();static \u0275cmp=T({type:t,selectors:[["p-toggleswitch"],["p-toggleSwitch"],["p-toggle-switch"]],contentQueries:function(n,e,o){if(n&1&&F(o,Y,4)(o,$,4),n&2){let l;h(l=u())&&(e.handleTemplate=l.first),h(l=u())&&(e.templates=l)}},viewQuery:function(n,e){if(n&1&&A(Z,5),n&2){let o;h(o=u())&&(e.input=o.first)}},hostVars:7,hostBindings:function(n,e){n&1&&f("click",function(l){return e.onHostClick(l)}),n&2&&(d("data-p-checked",e.checked())("data-p-disabled",e.$disabled())("data-p",e.dataP),L(e.sx("root")),s(e.cn(e.cx("root"),e.styleClass)))},inputs:{styleClass:"styleClass",tabindex:[2,"tabindex","tabindex",O],inputId:"inputId",readonly:[2,"readonly","readonly",m],trueValue:"trueValue",falseValue:"falseValue",ariaLabel:"ariaLabel",size:[1,"size"],ariaLabelledBy:"ariaLabelledBy",autofocus:[2,"autofocus","autofocus",m]},outputs:{onChange:"onChange"},features:[D([de,J,{provide:K,useExisting:t},{provide:P,useExisting:t}]),_([r]),S],decls:5,vars:22,consts:[["input",""],["type","checkbox","role","switch",3,"focus","blur","checked","pAutoFocus","pBind"],[3,"pBind"],[4,"ngTemplateOutlet","ngTemplateOutletContext"]],template:function(n,e){n&1&&(w(0,"input",1,0),f("focus",function(){return e.onFocus()})("blur",function(){return e.onBlur()}),b(),w(2,"div",2)(3,"div",2),B(4,ie,1,4,"ng-container"),b()()),n&2&&(s(e.cx("input")),a("checked",e.checked())("pAutoFocus",e.autofocus)("pBind",e.ptm("input")),d("id",e.inputId)("required",e.required()?"":void 0)("disabled",e.$disabled()?"":void 0)("aria-checked",e.checked())("aria-labelledby",e.ariaLabelledBy)("aria-label",e.ariaLabel)("name",e.name())("tabindex",e.tabindex),g(2),s(e.cx("slider")),a("pBind",e.ptm("slider")),d("data-p",e.dataP),g(),s(e.cx("handle")),a("pBind",e.ptm("handle")),d("data-p",e.dataP),g(),M(e.handleTemplate||e._handleTemplate?4:-1))},dependencies:[Q,z,x,j,R,r],encapsulation:2,changeDetection:0})}return t})();export{ae as a};
