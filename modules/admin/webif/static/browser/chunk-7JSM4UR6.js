import{i as oe,u as re}from"./chunk-XJPGZAJH.js";import{g as ne}from"./chunk-FQUEGOUU.js";import{Ia as K,Ja as X,Ma as Y,Pa as Z,Ra as h,Sa as ee,Va as te,Xa as ie,c as q,o as J,s as W}from"./chunk-PN5D6VAD.js";import{$b as C,Ab as L,Fb as u,Gb as P,Hb as A,I as g,Nc as G,Ob as N,Pb as O,Tb as T,Ua as m,Uc as E,Vb as D,Vc as $,Y as I,Yb as _,Z as w,Za as V,Zb as j,_b as b,aa as U,ca as d,fc as Q,gc as p,ia as v,ib as B,ja as k,mb as H,nb as R,ob as M,q as s,sc as x,uc as z,va as y,w as a,wb as S,zb as F}from"./chunk-HJNL6B4D.js";var le=`
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
`;var ce=["handle"],ue=["input"],pe=o=>({checked:o});function he(o,l){o&1&&N(0)}function fe(o,l){if(o&1&&M(0,he,1,0,"ng-container",3),o&2){let t=D();u("ngTemplateOutlet",t.handleTemplate||t._handleTemplate)("ngTemplateOutletContext",z(2,pe,t.checked()))}}var we=`
    ${le}

    p-toggleswitch.ng-invalid.ng-dirty > .p-toggleswitch-slider {
        border-color: dt('toggleswitch.invalid.border.color');
    }
`,me={root:{position:"relative"}},be={root:({instance:o})=>["p-toggleswitch p-component",{"p-toggleswitch p-component":!0,"p-toggleswitch-checked":o.checked(),"p-disabled":o.$disabled(),"p-invalid":o.invalid()}],input:"p-toggleswitch-input",slider:"p-toggleswitch-slider",handle:"p-toggleswitch-handle"},se=(()=>{class o extends Y{name="toggleswitch";style=we;classes=be;inlineStyles=me;static \u0275fac=(()=>{let t;return function(e){return(t||(t=y(o)))(e||o)}})();static \u0275prov=w({token:o,factory:o.\u0275fac})}return o})();var ae=new U("TOGGLESWITCH_INSTANCE"),Ce={provide:ne,useExisting:I(()=>ve),multi:!0},ve=(()=>{class o extends re{$pcToggleSwitch=d(ae,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=d(h,{self:!0});onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptms(["host","root"]))}styleClass;tabindex;inputId;readonly;trueValue=!0;falseValue=!1;ariaLabel;size=G();ariaLabelledBy;autofocus;onChange=new V;input;handleTemplate;_handleTemplate;focused=!1;_componentStyle=d(se);templates;onHostClick(t){this.onClick(t)}onAfterContentInit(){this.templates.forEach(t=>{t.getType()==="handle"?this._handleTemplate=t.template:this._handleTemplate=t.template})}onClick(t){!this.$disabled()&&!this.readonly&&(this.writeModelValue(this.checked()?this.falseValue:this.trueValue),this.onModelChange(this.modelValue()),this.onChange.emit({originalEvent:t,checked:this.modelValue()}),this.input.nativeElement.focus())}onFocus(){this.focused=!0}onBlur(){this.focused=!1,this.onModelTouched()}checked(){return this.modelValue()===this.trueValue}writeControlValue(t,i){i(t),this.cd.markForCheck()}static \u0275fac=(()=>{let t;return function(e){return(t||(t=y(o)))(e||o)}})();static \u0275cmp=B({type:o,selectors:[["p-toggleswitch"],["p-toggleSwitch"],["p-toggle-switch"]],contentQueries:function(i,e,n){if(i&1&&(_(n,ce,4),_(n,K,4)),i&2){let r;b(r=C())&&(e.handleTemplate=r.first),b(r=C())&&(e.templates=r)}},viewQuery:function(i,e){if(i&1&&j(ue,5),i&2){let n;b(n=C())&&(e.input=n.first)}},hostVars:5,hostBindings:function(i,e){i&1&&T("click",function(r){return e.onHostClick(r)}),i&2&&(S("data-pc-name","toggleswitch"),Q(e.sx("root")),p(e.cn(e.cx("root"),e.styleClass)))},inputs:{styleClass:"styleClass",tabindex:[2,"tabindex","tabindex",$],inputId:"inputId",readonly:[2,"readonly","readonly",E],trueValue:"trueValue",falseValue:"falseValue",ariaLabel:"ariaLabel",size:[1,"size"],ariaLabelledBy:"ariaLabelledBy",autofocus:[2,"autofocus","autofocus",E]},outputs:{onChange:"onChange"},features:[x([Ce,se,{provide:ae,useExisting:o},{provide:Z,useExisting:o}]),R([h]),H],decls:5,vars:20,consts:[["input",""],["type","checkbox","role","switch",3,"focus","blur","checked","pAutoFocus","pBind"],[3,"pBind"],[4,"ngTemplateOutlet","ngTemplateOutletContext"]],template:function(i,e){if(i&1){let n=O();P(0,"input",1,0),T("focus",function(){return v(n),k(e.onFocus())})("blur",function(){return v(n),k(e.onBlur())}),A(),P(2,"div",2)(3,"div",2),F(4,fe,1,4,"ng-container"),A()()}i&2&&(p(e.cx("input")),u("checked",e.checked())("pAutoFocus",e.autofocus)("pBind",e.ptm("input")),S("id",e.inputId)("required",e.required()?"":void 0)("disabled",e.$disabled()?"":void 0)("aria-checked",e.checked())("aria-labelledby",e.ariaLabelledBy)("aria-label",e.ariaLabel)("name",e.name())("tabindex",e.tabindex),m(2),p(e.cx("slider")),u("pBind",e.ptm("slider")),m(),p(e.cx("handle")),u("pBind",e.ptm("handle")),m(),L(e.handleTemplate||e._handleTemplate?4:-1))},dependencies:[W,J,oe,X,ee,h],encapsulation:2,changeDetection:0})}return o})();var c=class c{constructor(){this.http=d(q);this.appConfig=d(te);this.log=d(ie)}getInstalledPlugins(){let t=this.appConfig.apiUrl+"plugins/installed/";return this.http.get(t).pipe(a(i=>i),g(i=>(this.log.error("PluginsApiService (getInstalledPlugins): Could not read plugins data - "+i.error.error),s({}))))}getPluginsConfig(){let t=this.appConfig.apiUrl+"plugins/config/";return this.http.get(t).pipe(a(i=>i),g(i=>(this.log.error("PluginsApiService (getPluginsConfig): Could not read plugins data - "+i.error.error),s({}))))}getPluginsInfo(){let t=this.appConfig.apiUrl+"plugins/info/";return this.http.get(t).pipe(a(i=>i),g(i=>(this.log.error("PluginsApiService (getPluginsInfo): Could not read plugins data - "+i.error.error),s({}))))}getPluginsLogicParameters(){let t=this.appConfig.apiUrl+"plugins/logicparams/";return this.http.get(t).pipe(a(i=>i),g(i=>(this.log.error("PluginsApiService (getPluginsLogicParameters): Could not read plugins data - "+i.error.error),s({}))))}getPluginsAPI(){let t=this.appConfig.apiUrl+"plugins/api/";return this.http.get(t).pipe(a(i=>i),g(i=>(this.log.error("PluginsApiService (getPluginsInfo): Could not read plugins data - "+i.error.error),s({}))))}setPluginConfig(l,t){let e=this.appConfig.apiUrl+"plugin/"+l+"/";return this.http.put(e,JSON.stringify(t)).pipe(a(n=>{let r=n;if(r)return r.result==="ok"?!0:(this.log.error("PluginsApiService.setPluginConfig failed:",r.result,r.description),!1);this.log.log("PluginsApiService.setPluginConfig","fail: undefined result")}),g(n=>(this.log.error("PluginsApiService (setPluginConfig): Could not set plugin config data - "+n.error.error),s({}))))}addPluginConfig(l,t){let e=this.appConfig.apiUrl+"plugin/"+l+"/";return this.http.post(e,JSON.stringify(t)).pipe(a(n=>{let r=n;if(r)return this.log.log("PluginsApiService.addPluginConfig","- config",t,`
result`,{result:r}),r.result==="ok"?!0:(this.log.error("PluginsApiService.addPluginConfig failed:",r.result,r.description),!1);this.log.log("PluginsApiService.addPluginConfig","fail: undefined result")}),g(n=>(this.log.error("PluginsApiService (addPluginConfig): Could not set plugin config data - "+n.error.error),s({}))))}deletePluginConfig(l){let i=this.appConfig.apiUrl+"plugin/"+l+"/";return this.http.delete(i).pipe(a(e=>{let n=e;if(n)return this.log.log("PluginsApiService.deletePluginConfig","- section",l,`
result`,{result:n}),n.result==="ok"?!0:(this.log.error("PluginsApiService.deletePluginConfig failed:",n.result,n.description),!1);this.log.log("PluginsApiService.deletePluginConfig","fail: undefined result")}),g(e=>(this.log.error("PluginsApiService (deletePluginConfig): Could not set plugin config data - "+e.error.error),s({}))))}setPluginState(l,t,i=""){t=t.toLowerCase(),this.log.warn("PluginsApiService.setPluginState",{pluginConfigName:l},{action:t});let n=this.appConfig.apiUrl+"plugin/"+l+"?action="+t;return i!==""&&(n+="&filename="+i),this.http.put(n,JSON.stringify("")).pipe(a(r=>{let f=r;if(f)return f.result==="ok"?!0:(this.log.error("PluginsApiService.setPluginState failed:",f.result,f.description),!1);this.log.log("PluginsApiService.setPluginState","fail: undefined result")}),g(r=>(this.log.error("PluginsApiService.setPluginState: Could not set logic state - "+r.error.error),s({}))))}};c.\u0275fac=function(t){return new(t||c)},c.\u0275prov=w({token:c,factory:c.\u0275fac,providedIn:"root"});var ge=c;export{ve as a,ge as b};
