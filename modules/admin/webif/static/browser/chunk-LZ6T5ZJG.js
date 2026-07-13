import{a as _t,b as xt}from"./chunk-6ETCCTDR.js";import{Ba as et,Ea as z,Ma as yt,Ua as Tt,V as Z,Va as nt,Ya as k,ab as E,bb as F,cb as l,db as A,ja as tt,jb as it,kb as Bt,ma as ht,r as W,ta as gt,ua as mt,v as V,va as R,w as U}from"./chunk-XMFB5O6P.js";import{$b as dt,Eb as u,Fb as P,Fc as pt,Gb as K,Hb as Q,Kc as r,Nb as $,Ob as Y,Oc as g,Pb as rt,Rc as ft,Sb as O,Sc as q,T as L,U as T,Ub as h,Va as v,Vb as C,Wb as I,X as _,Xb as lt,Xc as y,Yb as ct,Yc as vt,Z as o,Zb as p,_b as f,bc as bt,cc as ut,da as G,ea as J,fa as X,gc as c,hb as x,lb as B,mb as D,nb as S,oa as H,ra as ot,sc as M,ta as b,va as st,vb as m,yb as w,zb as N}from"./chunk-25ZXD53X.js";var Dt=`
    .p-tabs {
        display: flex;
        flex-direction: column;
    }

    .p-tablist {
        display: flex;
        position: relative;
        overflow: hidden;
        background: dt('tabs.tablist.background');
    }

    .p-tablist-viewport {
        overflow-x: auto;
        overflow-y: hidden;
        scroll-behavior: smooth;
        scrollbar-width: none;
        overscroll-behavior: contain auto;
    }

    .p-tablist-viewport::-webkit-scrollbar {
        display: none;
    }

    .p-tablist-tab-list {
        position: relative;
        display: flex;
        border-style: solid;
        border-color: dt('tabs.tablist.border.color');
        border-width: dt('tabs.tablist.border.width');
    }

    .p-tablist-content {
        flex-grow: 1;
    }

    .p-tablist-nav-button {
        all: unset;
        position: absolute !important;
        flex-shrink: 0;
        inset-block-start: 0;
        z-index: 2;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: dt('tabs.nav.button.background');
        color: dt('tabs.nav.button.color');
        width: dt('tabs.nav.button.width');
        transition:
            color dt('tabs.transition.duration'),
            outline-color dt('tabs.transition.duration'),
            box-shadow dt('tabs.transition.duration');
        box-shadow: dt('tabs.nav.button.shadow');
        outline-color: transparent;
        cursor: pointer;
    }

    .p-tablist-nav-button:focus-visible {
        z-index: 1;
        box-shadow: dt('tabs.nav.button.focus.ring.shadow');
        outline: dt('tabs.nav.button.focus.ring.width') dt('tabs.nav.button.focus.ring.style') dt('tabs.nav.button.focus.ring.color');
        outline-offset: dt('tabs.nav.button.focus.ring.offset');
    }

    .p-tablist-nav-button:hover {
        color: dt('tabs.nav.button.hover.color');
    }

    .p-tablist-prev-button {
        inset-inline-start: 0;
    }

    .p-tablist-next-button {
        inset-inline-end: 0;
    }

    .p-tablist-prev-button:dir(rtl),
    .p-tablist-next-button:dir(rtl) {
        transform: rotate(180deg);
    }

    .p-tab {
        flex-shrink: 0;
        cursor: pointer;
        user-select: none;
        position: relative;
        border-style: solid;
        white-space: nowrap;
        gap: dt('tabs.tab.gap');
        background: dt('tabs.tab.background');
        border-width: dt('tabs.tab.border.width');
        border-color: dt('tabs.tab.border.color');
        color: dt('tabs.tab.color');
        padding: dt('tabs.tab.padding');
        font-weight: dt('tabs.tab.font.weight');
        transition:
            background dt('tabs.transition.duration'),
            border-color dt('tabs.transition.duration'),
            color dt('tabs.transition.duration'),
            outline-color dt('tabs.transition.duration'),
            box-shadow dt('tabs.transition.duration');
        margin: dt('tabs.tab.margin');
        outline-color: transparent;
    }

    .p-tab:not(.p-disabled):focus-visible {
        z-index: 1;
        box-shadow: dt('tabs.tab.focus.ring.shadow');
        outline: dt('tabs.tab.focus.ring.width') dt('tabs.tab.focus.ring.style') dt('tabs.tab.focus.ring.color');
        outline-offset: dt('tabs.tab.focus.ring.offset');
    }

    .p-tab:not(.p-tab-active):not(.p-disabled):hover {
        background: dt('tabs.tab.hover.background');
        border-color: dt('tabs.tab.hover.border.color');
        color: dt('tabs.tab.hover.color');
    }

    .p-tab-active {
        background: dt('tabs.tab.active.background');
        border-color: dt('tabs.tab.active.border.color');
        color: dt('tabs.tab.active.color');
    }

    .p-tabpanels {
        background: dt('tabs.tabpanel.background');
        color: dt('tabs.tabpanel.color');
        padding: dt('tabs.tabpanel.padding');
        outline: 0 none;
    }

    .p-tabpanel:focus-visible {
        box-shadow: dt('tabs.tabpanel.focus.ring.shadow');
        outline: dt('tabs.tabpanel.focus.ring.width') dt('tabs.tabpanel.focus.ring.style') dt('tabs.tabpanel.focus.ring.color');
        outline-offset: dt('tabs.tabpanel.focus.ring.offset');
    }

    .p-tablist-active-bar {
        z-index: 1;
        display: block;
        position: absolute;
        inset-block-end: dt('tabs.active.bar.bottom');
        height: dt('tabs.active.bar.height');
        background: dt('tabs.active.bar.background');
        transition: 250ms cubic-bezier(0.35, 0, 0.25, 1);
    }
`;var j=["*"],Ot=["previcon"],Vt=["nexticon"],St=["content"],Rt=["prevButton"],zt=["nextButton"],jt=["inkbar"],Ht=["tabs"];function Kt(e,d){e&1&&$(0)}function Qt(e,d){if(e&1&&S(0,Kt,1,0,"ng-container",11),e&2){let t=h(2);u("ngTemplateOutlet",t.prevIconTemplate||t._prevIconTemplate)}}function $t(e,d){e&1&&(X(),Q(0,"svg",10))}function qt(e,d){if(e&1){let t=Y();P(0,"button",9,3),O("click",function(){G(t);let n=h();return J(n.onPrevButtonClick())}),w(2,Qt,1,1,"ng-container")(3,$t,1,0,":svg:svg",10),K()}if(e&2){let t=h();c(t.cx("prevButton")),u("pBind",t.ptm("prevButton")),m("aria-label",t.prevButtonAriaLabel)("tabindex",t.tabindex())("data-pc-group-section","navigator"),v(2),N(t.prevIconTemplate||t._prevIconTemplate?2:3)}}function Wt(e,d){e&1&&$(0)}function Ut(e,d){if(e&1&&S(0,Wt,1,0,"ng-container",11),e&2){let t=h(2);u("ngTemplateOutlet",t.nextIconTemplate||t._nextIconTemplate)}}function Gt(e,d){e&1&&(X(),Q(0,"svg",12))}function Jt(e,d){if(e&1){let t=Y();P(0,"button",9,4),O("click",function(){G(t);let n=h();return J(n.onNextButtonClick())}),w(2,Ut,1,1,"ng-container")(3,Gt,1,0,":svg:svg",12),K()}if(e&2){let t=h();c(t.cx("nextButton")),u("pBind",t.ptm("nextButton")),m("aria-label",t.nextButtonAriaLabel)("tabindex",t.tabindex())("data-pc-group-section","navigator"),v(2),N(t.nextIconTemplate||t._nextIconTemplate?2:3)}}function Xt(e,d){e&1&&I(0)}function Yt(e,d){e&1&&$(0)}function Zt(e,d){if(e&1&&S(0,Yt,1,0,"ng-container",1),e&2){let t=h(),i=ut(1);u("ngTemplateOutlet",t.content()?t.content():i)}}var te={root:({instance:e})=>["p-tabs p-component",{"p-tabs-scrollable":e.scrollable()}]},wt=(()=>{class e extends k{name="tabs";style=Dt;classes=te;static \u0275fac=(()=>{let t;return function(n){return(t||(t=b(e)))(n||e)}})();static \u0275prov=T({token:e,factory:e.\u0275fac})}return e})();var Nt=new _("TABS_INSTANCE"),at=(()=>{class e extends F{componentName="Tabs";$pcTabs=o(Nt,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=o(l,{self:!0});onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptms(["host","root"]))}value=q(void 0);scrollable=g(!1,{transform:y});lazy=g(!1,{transform:y});selectOnFocus=g(!1,{transform:y});showNavigators=g(!0,{transform:y});tabindex=g(0,{transform:vt});id=H(yt("pn_id_"));_componentStyle=o(wt);updateValue(t){this.value.update(()=>t)}static \u0275fac=(()=>{let t;return function(n){return(t||(t=b(e)))(n||e)}})();static \u0275cmp=x({type:e,selectors:[["p-tabs"]],hostVars:3,hostBindings:function(i,n){i&2&&(m("id",n.id()),c(n.cx("root")))},inputs:{value:[1,"value"],scrollable:[1,"scrollable"],lazy:[1,"lazy"],selectOnFocus:[1,"selectOnFocus"],showNavigators:[1,"showNavigators"],tabindex:[1,"tabindex"]},outputs:{value:"valueChange"},features:[M([wt,{provide:Nt,useExisting:e},{provide:E,useExisting:e}]),B([l]),D],ngContentSelectors:j,decls:1,vars:0,template:function(i,n){i&1&&(C(),I(0))},dependencies:[V,A],encapsulation:2,changeDetection:0})}return e})(),ee={root:({instance:e})=>["p-tab",{"p-tab-active":e.active(),"p-disabled":e.disabled()}]},Ct=(()=>{class e extends k{name="tab";classes=ee;static \u0275fac=(()=>{let t;return function(n){return(t||(t=b(e)))(n||e)}})();static \u0275prov=T({token:e,factory:e.\u0275fac})}return e})();var ne={root:"p-tablist",content:"p-tablist-content p-tablist-viewport",tabList:"p-tablist-tab-list",activeBar:"p-tablist-active-bar",prevButton:"p-tablist-prev-button p-tablist-nav-button",nextButton:"p-tablist-next-button p-tablist-nav-button"},It=(()=>{class e extends k{name="tablist";classes=ne;static \u0275fac=(()=>{let t;return function(n){return(t||(t=b(e)))(n||e)}})();static \u0275prov=T({token:e,factory:e.\u0275fac})}return e})();var Mt=new _("TABLIST_INSTANCE"),ie=(()=>{class e extends F{componentName="TabList";$pcTabList=o(Mt,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=o(l,{self:!0});onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptms(["host","root"]))}prevIconTemplate;nextIconTemplate;templates;content;prevButton;nextButton;inkbar;tabs;pcTabs=o(L(()=>at));isPrevButtonEnabled=H(!1);isNextButtonEnabled=H(!1);resizeObserver;showNavigators=r(()=>this.pcTabs.showNavigators());tabindex=r(()=>this.pcTabs.tabindex());scrollable=r(()=>this.pcTabs.scrollable());_componentStyle=o(It);constructor(){super(),ot(()=>{this.pcTabs.value(),U(this.platformId)&&setTimeout(()=>{this.updateInkBar()})})}get prevButtonAriaLabel(){return this.config?.translation?.aria?.previous}get nextButtonAriaLabel(){return this.config?.translation?.aria?.next}onAfterViewInit(){this.showNavigators()&&U(this.platformId)&&(this.updateButtonState(),this.bindResizeObserver())}_prevIconTemplate;_nextIconTemplate;onAfterContentInit(){this.templates?.forEach(t=>{switch(t.getType()){case"previcon":this._prevIconTemplate=t.template;break;case"nexticon":this._nextIconTemplate=t.template;break}})}onDestroy(){this.unbindResizeObserver()}onScroll(t){this.showNavigators()&&this.updateButtonState(),t.preventDefault()}onPrevButtonClick(){let t=this.content.nativeElement,i=z(t),n=Math.abs(t.scrollLeft)-i,a=n<=0?0:n;t.scrollLeft=tt(t)?-1*a:a}onNextButtonClick(){let t=this.content.nativeElement,i=z(t)-this.getVisibleButtonWidths(),n=t.scrollLeft+i,a=t.scrollWidth-i,s=n>=a?a:n;t.scrollLeft=tt(t)?-1*s:s}updateButtonState(){let t=this.content?.nativeElement,i=this.el?.nativeElement,{scrollWidth:n,offsetWidth:a}=t,s=Math.abs(t.scrollLeft),Pt=z(t);this.isPrevButtonEnabled.set(s!==0),this.isNextButtonEnabled.set(i.offsetWidth>=a&&Math.abs(s-n+Pt)>1)}updateInkBar(){let t=this.content?.nativeElement,i=this.inkbar?.nativeElement,n=this.tabs?.nativeElement,a=gt(t,'[data-pc-name="tab"][data-p-active="true"]');i&&(i.style.width=ht(a)+"px",i.style.left=et(a).left-et(n).left+"px")}getVisibleButtonWidths(){let t=this.prevButton?.nativeElement,i=this.nextButton?.nativeElement;return[t,i].reduce((n,a)=>a?n+z(a):n,0)}bindResizeObserver(){this.resizeObserver=new ResizeObserver(()=>this.updateButtonState()),this.resizeObserver.observe(this.el.nativeElement)}unbindResizeObserver(){this.resizeObserver&&(this.resizeObserver.unobserve(this.el.nativeElement),this.resizeObserver=null)}static \u0275fac=function(i){return new(i||e)};static \u0275cmp=x({type:e,selectors:[["p-tablist"]],contentQueries:function(i,n,a){if(i&1&&lt(a,Ot,4)(a,Vt,4)(a,Tt,4),i&2){let s;p(s=f())&&(n.prevIconTemplate=s.first),p(s=f())&&(n.nextIconTemplate=s.first),p(s=f())&&(n.templates=s)}},viewQuery:function(i,n){if(i&1&&ct(St,5)(Rt,5)(zt,5)(jt,5)(Ht,5),i&2){let a;p(a=f())&&(n.content=a.first),p(a=f())&&(n.prevButton=a.first),p(a=f())&&(n.nextButton=a.first),p(a=f())&&(n.inkbar=a.first),p(a=f())&&(n.tabs=a.first)}},hostVars:2,hostBindings:function(i,n){i&2&&c(n.cx("root"))},features:[M([It,{provide:Mt,useExisting:e},{provide:E,useExisting:e}]),B([l]),D],ngContentSelectors:j,decls:9,vars:11,consts:[["content",""],["tabs",""],["inkbar",""],["prevButton",""],["nextButton",""],["type","button","pRipple","",3,"pBind","class"],[3,"scroll","pBind"],["role","tablist",3,"pBind"],["role","presentation",3,"pBind"],["type","button","pRipple","",3,"click","pBind"],["data-p-icon","chevron-left"],[4,"ngTemplateOutlet"],["data-p-icon","chevron-right"]],template:function(i,n){i&1&&(C(),w(0,qt,4,7,"button",5),P(1,"div",6,0),O("scroll",function(s){return n.onScroll(s)}),P(3,"div",7,1),I(5),Q(6,"span",8,2),K()(),w(8,Jt,4,7,"button",5)),i&2&&(N(n.showNavigators()&&n.isPrevButtonEnabled()?0:-1),v(),c(n.cx("content")),u("pBind",n.ptm("content")),v(2),c(n.cx("tabList")),u("pBind",n.ptm("tabList")),v(3),c(n.cx("activeBar")),u("pBind",n.ptm("activeBar")),v(2),N(n.showNavigators()&&n.isNextButtonEnabled()?8:-1))},dependencies:[V,W,_t,xt,Bt,it,nt,A,l],encapsulation:2,changeDetection:0})}return e})(),kt=new _("TAB_INSTANCE"),Ae=(()=>{class e extends F{componentName="Tab";$pcTab=o(kt,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=o(l,{self:!0});onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptms(["host","root"]))}value=q();disabled=g(!1,{transform:y});pcTabs=o(L(()=>at));pcTabList=o(L(()=>ie));el=o(st);_componentStyle=o(Ct);ripple=r(()=>this.config.ripple());id=r(()=>`${this.pcTabs.id()}_tab_${this.value()}`);ariaControls=r(()=>`${this.pcTabs.id()}_tabpanel_${this.value()}`);active=r(()=>Z(this.pcTabs.value(),this.value()));tabindex=r(()=>this.disabled()?-1:this.active()?this.pcTabs.tabindex():-1);mutationObserver;onFocus(t){this.disabled()||this.pcTabs.selectOnFocus()&&this.changeActiveValue()}onClick(t){this.disabled()||this.changeActiveValue()}onKeyDown(t){switch(t.code){case"ArrowRight":this.onArrowRightKey(t);break;case"ArrowLeft":this.onArrowLeftKey(t);break;case"Home":this.onHomeKey(t);break;case"End":this.onEndKey(t);break;case"PageDown":this.onPageDownKey(t);break;case"PageUp":this.onPageUpKey(t);break;case"Enter":case"NumpadEnter":case"Space":this.onEnterKey(t);break;default:break}t.stopPropagation()}onAfterViewInit(){this.bindMutationObserver()}onArrowRightKey(t){let i=this.findNextTab(t.currentTarget);i?this.changeFocusedTab(t,i):this.onHomeKey(t),t.preventDefault()}onArrowLeftKey(t){let i=this.findPrevTab(t.currentTarget);i?this.changeFocusedTab(t,i):this.onEndKey(t),t.preventDefault()}onHomeKey(t){let i=this.findFirstTab();this.changeFocusedTab(t,i),t.preventDefault()}onEndKey(t){let i=this.findLastTab();this.changeFocusedTab(t,i),t.preventDefault()}onPageDownKey(t){this.scrollInView(this.findLastTab()),t.preventDefault()}onPageUpKey(t){this.scrollInView(this.findFirstTab()),t.preventDefault()}onEnterKey(t){this.disabled()||this.changeActiveValue(),t.preventDefault()}findNextTab(t,i=!1){let n=i?t:t.nextElementSibling;return n?R(n,"data-p-disabled")||R(n,"data-pc-section")==="activebar"?this.findNextTab(n):n:null}findPrevTab(t,i=!1){let n=i?t:t.previousElementSibling;return n?R(n,"data-p-disabled")||R(n,"data-pc-section")==="activebar"?this.findPrevTab(n):n:null}findFirstTab(){return this.findNextTab(this.pcTabList?.tabs?.nativeElement?.firstElementChild,!0)}findLastTab(){return this.findPrevTab(this.pcTabList?.tabs?.nativeElement?.lastElementChild,!0)}changeActiveValue(){this.pcTabs.updateValue(this.value())}changeFocusedTab(t,i){mt(i),this.scrollInView(i)}scrollInView(t){t?.scrollIntoView?.({block:"nearest"})}bindMutationObserver(){U(this.platformId)&&(this.mutationObserver=new MutationObserver(t=>{t.forEach(()=>{this.active()&&this.pcTabList?.updateInkBar()})}),this.mutationObserver.observe(this.el.nativeElement,{childList:!0,characterData:!0,subtree:!0}))}unbindMutationObserver(){this.mutationObserver?.disconnect()}onDestroy(){this.mutationObserver&&this.unbindMutationObserver()}static \u0275fac=(()=>{let t;return function(n){return(t||(t=b(e)))(n||e)}})();static \u0275cmp=x({type:e,selectors:[["p-tab"]],hostVars:10,hostBindings:function(i,n){i&1&&O("focus",function(s){return n.onFocus(s)})("click",function(s){return n.onClick(s)})("keydown",function(s){return n.onKeyDown(s)}),i&2&&(m("id",n.id())("aria-controls",n.ariaControls())("role","tab")("aria-selected",n.active())("aria-disabled",n.disabled())("data-p-disabled",n.disabled())("data-p-active",n.active())("tabindex",n.tabindex()),c(n.cx("root")))},inputs:{value:[1,"value"],disabled:[1,"disabled"]},outputs:{value:"valueChange"},features:[M([Ct,{provide:kt,useExisting:e},{provide:E,useExisting:e}]),B([it,l]),D],ngContentSelectors:j,decls:1,vars:0,template:function(i,n){i&1&&(C(),I(0))},dependencies:[V,nt,A],encapsulation:2,changeDetection:0})}return e})(),ae={root:({instance:e})=>["p-tabpanel",{"p-tabpanel-active":e.active()}]},Et=(()=>{class e extends k{name="tabpanel";classes=ae;static \u0275fac=(()=>{let t;return function(n){return(t||(t=b(e)))(n||e)}})();static \u0275prov=T({token:e,factory:e.\u0275fac})}return e})();var Ft=new _("TABPANEL_INSTANCE"),Le=(()=>{class e extends F{componentName="TabPanel";$pcTabPanel=o(Ft,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=o(l,{self:!0});pcTabs=o(L(()=>at));onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptms(["host","root"]))}lazy=g(!1,{transform:y});value=q(void 0);content=ft("content");id=r(()=>`${this.pcTabs.id()}_tabpanel_${this.value()}`);ariaLabelledby=r(()=>`${this.pcTabs.id()}_tab_${this.value()}`);active=r(()=>Z(this.pcTabs.value(),this.value()));isLazyEnabled=r(()=>this.pcTabs.lazy()||this.lazy());hasBeenRendered=!1;shouldRender=r(()=>!this.isLazyEnabled()||this.hasBeenRendered?!0:this.active()?(this.hasBeenRendered=!0,!0):!1);_componentStyle=o(Et);static \u0275fac=(()=>{let t;return function(n){return(t||(t=b(e)))(n||e)}})();static \u0275cmp=x({type:e,selectors:[["p-tabpanel"]],contentQueries:function(i,n,a){i&1&&dt(a,n.content,St,5),i&2&&bt()},hostVars:7,hostBindings:function(i,n){i&2&&(rt("hidden",!n.active()),m("id",n.id())("role","tabpanel")("aria-labelledby",n.ariaLabelledby())("data-p-active",n.active()),c(n.cx("root")))},inputs:{lazy:[1,"lazy"],value:[1,"value"]},outputs:{value:"valueChange"},features:[M([Et,{provide:Ft,useExisting:e},{provide:E,useExisting:e}]),B([l]),D],ngContentSelectors:j,decls:3,vars:1,consts:[["defaultContent",""],[4,"ngTemplateOutlet"]],template:function(i,n){i&1&&(C(),S(0,Xt,1,0,"ng-template",null,0,pt),w(2,Zt,1,1,"ng-container")),i&2&&(v(2),N(n.shouldRender()?2:-1))},dependencies:[W,A],encapsulation:2,changeDetection:0})}return e})(),oe={root:"p-tabpanels"},At=(()=>{class e extends k{name="tabpanels";classes=oe;static \u0275fac=(()=>{let t;return function(n){return(t||(t=b(e)))(n||e)}})();static \u0275prov=T({token:e,factory:e.\u0275fac})}return e})();var Lt=new _("TABPANELS_INSTANCE"),Se=(()=>{class e extends F{componentName="TabPanels";$pcTabPanels=o(Lt,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=o(l,{self:!0});_componentStyle=o(At);onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptms(["host","root"]))}static \u0275fac=(()=>{let t;return function(n){return(t||(t=b(e)))(n||e)}})();static \u0275cmp=x({type:e,selectors:[["p-tabpanels"]],hostVars:3,hostBindings:function(i,n){i&2&&(m("role","presentation"),c(n.cx("root")))},features:[M([At,{provide:Lt,useExisting:e},{provide:E,useExisting:e}]),B([l]),D],ngContentSelectors:j,decls:1,vars:0,template:function(i,n){i&1&&(C(),I(0))},dependencies:[V,A],encapsulation:2,changeDetection:0})}return e})();export{at as a,ie as b,Ae as c,Le as d,Se as e};
