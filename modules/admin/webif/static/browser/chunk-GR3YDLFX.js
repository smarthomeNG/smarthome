import{i as ee,u as te}from"./chunk-TWKP3LGB.js";import{k as Z}from"./chunk-JKP3TXC4.js";import{Ua as q,Va as x,Ya as J,ab as W,cb as h,db as K,f as Q,gb as X,ib as Y,r as $,v as G}from"./chunk-XMFB5O6P.js";import{Eb as u,Fb as k,G as a,Gb as y,Nb as M,Oc as j,Sb as P,T as A,U as w,Ub as V,Va as m,X as T,Xb as F,Xc as S,Yb as L,Yc as z,Z as d,Zb as b,_b as C,fc as N,gc as p,hb as E,ka as _,lb as I,mb as U,nb as R,o as s,sc as O,ta as v,u as g,uc as D,vb as c,yb as B,zb as H}from"./chunk-25ZXD53X.js";var ie=`
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
`;var se=["handle"],ae=["input"],de=n=>({checked:n});function ge(n,l){n&1&&M(0)}function ce(n,l){if(n&1&&R(0,ge,1,0,"ng-container",3),n&2){let t=V();u("ngTemplateOutlet",t.handleTemplate||t._handleTemplate)("ngTemplateOutletContext",D(2,de,t.checked()))}}var ue=`
    ${ie}

    p-toggleswitch.ng-invalid.ng-dirty > .p-toggleswitch-slider {
        border-color: dt('toggleswitch.invalid.border.color');
    }
`,pe={root:{position:"relative"}},he={root:({instance:n})=>["p-toggleswitch p-component",{"p-toggleswitch p-component":!0,"p-toggleswitch-checked":n.checked(),"p-disabled":n.$disabled(),"p-invalid":n.invalid()}],input:"p-toggleswitch-input",slider:"p-toggleswitch-slider",handle:"p-toggleswitch-handle"},ne=(()=>{class n extends J{name="toggleswitch";style=ue;classes=he;inlineStyles=pe;static \u0275fac=(()=>{let t;return function(e){return(t||(t=v(n)))(e||n)}})();static \u0275prov=w({token:n,factory:n.\u0275fac})}return n})();var oe=new T("TOGGLESWITCH_INSTANCE"),fe={provide:Z,useExisting:A(()=>we),multi:!0},we=(()=>{class n extends te{componentName="ToggleSwitch";$pcToggleSwitch=d(oe,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=d(h,{self:!0});onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptms(["host","root"]))}styleClass;tabindex;inputId;readonly;trueValue=!0;falseValue=!1;ariaLabel;size=j();ariaLabelledBy;autofocus;onChange=new _;input;handleTemplate;_handleTemplate;focused=!1;_componentStyle=d(ne);templates;onHostClick(t){this.onClick(t)}onAfterContentInit(){this.templates.forEach(t=>{t.getType()==="handle"?this._handleTemplate=t.template:this._handleTemplate=t.template})}onClick(t){!this.$disabled()&&!this.readonly&&(this.writeModelValue(this.checked()?this.falseValue:this.trueValue),this.onModelChange(this.modelValue()),this.onChange.emit({originalEvent:t,checked:this.modelValue()}),this.input.nativeElement.focus())}onFocus(){this.focused=!0}onBlur(){this.focused=!1,this.onModelTouched()}checked(){return this.modelValue()===this.trueValue}writeControlValue(t,i){i(t),this.cd.markForCheck()}get dataP(){return this.cn({checked:this.checked(),disabled:this.$disabled(),invalid:this.invalid()})}static \u0275fac=(()=>{let t;return function(e){return(t||(t=v(n)))(e||n)}})();static \u0275cmp=E({type:n,selectors:[["p-toggleswitch"],["p-toggleSwitch"],["p-toggle-switch"]],contentQueries:function(i,e,o){if(i&1&&F(o,se,4)(o,q,4),i&2){let r;b(r=C())&&(e.handleTemplate=r.first),b(r=C())&&(e.templates=r)}},viewQuery:function(i,e){if(i&1&&L(ae,5),i&2){let o;b(o=C())&&(e.input=o.first)}},hostVars:7,hostBindings:function(i,e){i&1&&P("click",function(r){return e.onHostClick(r)}),i&2&&(c("data-p-checked",e.checked())("data-p-disabled",e.$disabled())("data-p",e.dataP),N(e.sx("root")),p(e.cn(e.cx("root"),e.styleClass)))},inputs:{styleClass:"styleClass",tabindex:[2,"tabindex","tabindex",z],inputId:"inputId",readonly:[2,"readonly","readonly",S],trueValue:"trueValue",falseValue:"falseValue",ariaLabel:"ariaLabel",size:[1,"size"],ariaLabelledBy:"ariaLabelledBy",autofocus:[2,"autofocus","autofocus",S]},outputs:{onChange:"onChange"},features:[O([fe,ne,{provide:oe,useExisting:n},{provide:W,useExisting:n}]),I([h]),U],decls:5,vars:22,consts:[["input",""],["type","checkbox","role","switch",3,"focus","blur","checked","pAutoFocus","pBind"],[3,"pBind"],[4,"ngTemplateOutlet","ngTemplateOutletContext"]],template:function(i,e){i&1&&(k(0,"input",1,0),P("focus",function(){return e.onFocus()})("blur",function(){return e.onBlur()}),y(),k(2,"div",2)(3,"div",2),B(4,ce,1,4,"ng-container"),y()()),i&2&&(p(e.cx("input")),u("checked",e.checked())("pAutoFocus",e.autofocus)("pBind",e.ptm("input")),c("id",e.inputId)("required",e.required()?"":void 0)("disabled",e.$disabled()?"":void 0)("aria-checked",e.checked())("aria-labelledby",e.ariaLabelledBy)("aria-label",e.ariaLabel)("name",e.name())("tabindex",e.tabindex),m(2),p(e.cx("slider")),u("pBind",e.ptm("slider")),c("data-p",e.dataP),m(),p(e.cx("handle")),u("pBind",e.ptm("handle")),c("data-p",e.dataP),m(),H(e.handleTemplate||e._handleTemplate?4:-1))},dependencies:[G,$,ee,x,K,h],encapsulation:2,changeDetection:0})}return n})();var re=class n{constructor(){this.http=d(Q);this.appConfig=d(X);this.log=d(Y)}getInstalledPlugins(){let t=this.appConfig.apiUrl+"plugins/installed/";return this.http.get(t).pipe(a(i=>(this.log.error("PluginsApiService (getInstalledPlugins): Could not read plugins data - "+i.error.error),s({}))))}getPluginsConfig(){let t=this.appConfig.apiUrl+"plugins/config/";return this.http.get(t).pipe(a(i=>(this.log.error("PluginsApiService (getPluginsConfig): Could not read plugins data - "+i.error.error),s({}))))}getPluginsInfo(){let t=this.appConfig.apiUrl+"plugins/info/";return this.http.get(t).pipe(a(i=>(this.log.error("PluginsApiService (getPluginsInfo): Could not read plugins data - "+i.error.error),s({}))))}getPluginsLogicParameters(){let t=this.appConfig.apiUrl+"plugins/logicparams/";return this.http.get(t).pipe(a(i=>(this.log.error("PluginsApiService (getPluginsLogicParameters): Could not read plugins data - "+i.error.error),s({}))))}getPluginsAPI(){let t=this.appConfig.apiUrl+"plugins/api/";return this.http.get(t).pipe(a(i=>(this.log.error("PluginsApiService (getPluginsInfo): Could not read plugins data - "+i.error.error),s({}))))}setPluginConfig(l,t){let e=this.appConfig.apiUrl+"plugin/"+encodeURIComponent(l)+"/";return this.http.put(e,JSON.stringify(t)).pipe(g(o=>{let r=o;if(r)return r.result==="ok"?!0:(this.log.error("PluginsApiService.setPluginConfig failed:",r.result,r.description),!1);this.log.log("PluginsApiService.setPluginConfig","fail: undefined result")}),a(o=>(this.log.error("PluginsApiService (setPluginConfig): Could not set plugin config data - "+o.error.error),s({}))))}addPluginConfig(l,t){let e=this.appConfig.apiUrl+"plugin/"+encodeURIComponent(l)+"/";return this.http.post(e,JSON.stringify(t)).pipe(g(o=>{let r=o;if(r)return this.log.log("PluginsApiService.addPluginConfig","- config",t,`
result`,{result:r}),r.result==="ok"?!0:(this.log.error("PluginsApiService.addPluginConfig failed:",r.result,r.description),!1);this.log.log("PluginsApiService.addPluginConfig","fail: undefined result")}),a(o=>(this.log.error("PluginsApiService (addPluginConfig): Could not set plugin config data - "+o.error.error),s({}))))}deletePluginConfig(l){let i=this.appConfig.apiUrl+"plugin/"+encodeURIComponent(l)+"/";return this.http.delete(i).pipe(g(e=>{let o=e;if(o)return this.log.log("PluginsApiService.deletePluginConfig","- section",l,`
result`,{result:o}),o.result==="ok"?!0:(this.log.error("PluginsApiService.deletePluginConfig failed:",o.result,o.description),!1);this.log.log("PluginsApiService.deletePluginConfig","fail: undefined result")}),a(e=>(this.log.error("PluginsApiService (deletePluginConfig): Could not set plugin config data - "+e.error.error),s({}))))}setPluginState(l,t,i=""){t=t.toLowerCase(),this.log.warn("PluginsApiService.setPluginState",{pluginConfigName:l},{action:t});let o=this.appConfig.apiUrl+"plugin/"+encodeURIComponent(l)+"?action="+t;return i!==""&&(o+="&filename="+encodeURIComponent(i)),this.http.put(o,JSON.stringify("")).pipe(g(r=>{let f=r;if(f)return f.result==="ok"?!0:(this.log.error("PluginsApiService.setPluginState failed:",f.result,f.description),!1);this.log.log("PluginsApiService.setPluginState","fail: undefined result")}),a(r=>(this.log.error("PluginsApiService.setPluginState: Could not set logic state - "+r.error.error),s({}))))}static{this.\u0275fac=function(t){return new(t||n)}}static{this.\u0275prov=w({token:n,factory:n.\u0275fac,providedIn:"root"})}};export{we as a,re as b};
