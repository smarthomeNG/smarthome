import{a as xt,b as Bt}from"./chunk-ET44F6JB.js";import{Ia as _t,J as nt,Ja as ot,Ma as E,Pa as A,Qa as F,Ra as l,Sa as L,Ya as st,Z as it,Za as wt,aa as gt,ha as mt,ia as yt,ja as z,o as Y,pa as at,s as R,sa as Q,t as Z,ya as Tt}from"./chunk-PN5D6VAD.js";import{$b as f,Ab as C,Fb as b,Fc as pt,Gb as V,Hb as q,Ib as W,Jc as r,Kc as ft,Nc as g,Ob as U,Oc as vt,Pb as G,Pc as X,Qb as ct,Tb as O,Ua as v,Uc as y,Vb as h,Vc as ht,Wb as N,Xb as I,Y as S,Yb as J,Z as T,Zb as M,_b as p,aa as _,ac as dt,bc as ut,ca as o,cc as bt,gc as c,ia as H,ib as x,ja as K,ka as et,mb as B,nb as w,ob as P,qa as $,sc as k,va as u,wb as m,xa as lt,zb as D}from"./chunk-HJNL6B4D.js";var Dt=`
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
`;var Vt=["previcon"],Ot=["nexticon"],Pt=["content"],Rt=["prevButton"],zt=["nextButton"],Qt=["inkbar"],jt=["tabs"],j=["*"];function Ht(e,d){e&1&&U(0)}function Kt(e,d){if(e&1&&P(0,Ht,1,0,"ng-container",11),e&2){let t=h(2);b("ngTemplateOutlet",t.prevIconTemplate||t._prevIconTemplate)}}function $t(e,d){e&1&&(et(),W(0,"svg",10))}function qt(e,d){if(e&1){let t=G();V(0,"button",9,3),O("click",function(){H(t);let n=h();return K(n.onPrevButtonClick())}),D(2,Kt,1,1,"ng-container")(3,$t,1,0,":svg:svg",10),q()}if(e&2){let t=h();c(t.cx("prevButton")),b("pBind",t.ptm("prevButton")),m("aria-label",t.prevButtonAriaLabel)("tabindex",t.tabindex())("data-pc-group-section","navigator"),v(2),C(t.prevIconTemplate||t._prevIconTemplate?2:3)}}function Wt(e,d){e&1&&U(0)}function Ut(e,d){if(e&1&&P(0,Wt,1,0,"ng-container",11),e&2){let t=h(2);b("ngTemplateOutlet",t.nextIconTemplate||t._nextIconTemplate)}}function Gt(e,d){e&1&&(et(),W(0,"svg",12))}function Jt(e,d){if(e&1){let t=G();V(0,"button",9,4),O("click",function(){H(t);let n=h();return K(n.onNextButtonClick())}),D(2,Ut,1,1,"ng-container")(3,Gt,1,0,":svg:svg",12),q()}if(e&2){let t=h();c(t.cx("nextButton")),b("pBind",t.ptm("nextButton")),m("aria-label",t.nextButtonAriaLabel)("tabindex",t.tabindex())("data-pc-group-section","navigator"),v(2),C(t.nextIconTemplate||t._nextIconTemplate?2:3)}}function Xt(e,d){e&1&&I(0)}function Yt(e,d){e&1&&U(0)}function Zt(e,d){if(e&1&&P(0,Yt,1,0,"ng-container",1),e&2){let t=h(),i=bt(1);b("ngTemplateOutlet",t.content()?t.content():i)}}var te={root:({instance:e})=>["p-tabs p-component",{"p-tabs-scrollable":e.scrollable()}]},Ct=(()=>{class e extends E{name="tabs";style=Dt;classes=te;static \u0275fac=(()=>{let t;return function(n){return(t||(t=u(e)))(n||e)}})();static \u0275prov=T({token:e,factory:e.\u0275fac})}return e})();var ee={root:({instance:e})=>["p-tab",{"p-tab-active":e.active(),"p-disabled":e.disabled()}]},Nt=(()=>{class e extends E{name="tab";classes=ee;static \u0275fac=(()=>{let t;return function(n){return(t||(t=u(e)))(n||e)}})();static \u0275prov=T({token:e,factory:e.\u0275fac})}return e})();var ne={root:"p-tablist",content:"p-tablist-content p-tablist-viewport",tabList:"p-tablist-tab-list",activeBar:"p-tablist-active-bar",prevButton:"p-tablist-prev-button p-tablist-nav-button",nextButton:"p-tablist-next-button p-tablist-nav-button"},It=(()=>{class e extends E{name="tablist";classes=ne;static \u0275fac=(()=>{let t;return function(n){return(t||(t=u(e)))(n||e)}})();static \u0275prov=T({token:e,factory:e.\u0275fac})}return e})();var Mt=new _("TABLIST_INSTANCE"),ie=(()=>{class e extends F{$pcTabList=o(Mt,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=o(l,{self:!0});onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptms(["host","root"]))}prevIconTemplate;nextIconTemplate;templates;content;prevButton;nextButton;inkbar;tabs;pcTabs=o(S(()=>rt));isPrevButtonEnabled=$(!1);isNextButtonEnabled=$(!1);resizeObserver;showNavigators=r(()=>this.pcTabs.showNavigators());tabindex=r(()=>this.pcTabs.tabindex());scrollable=r(()=>this.pcTabs.scrollable());_componentStyle=o(It);constructor(){super(),ft(()=>{this.pcTabs.value(),Z(this.platformId)&&setTimeout(()=>{this.updateInkBar()})})}get prevButtonAriaLabel(){return this.config?.translation?.aria?.previous}get nextButtonAriaLabel(){return this.config?.translation?.aria?.next}onAfterViewInit(){this.showNavigators()&&Z(this.platformId)&&(this.updateButtonState(),this.bindResizeObserver())}_prevIconTemplate;_nextIconTemplate;onAfterContentInit(){this.templates?.forEach(t=>{switch(t.getType()){case"previcon":this._prevIconTemplate=t.template;break;case"nexticon":this._nextIconTemplate=t.template;break}})}onDestroy(){this.unbindResizeObserver()}onScroll(t){this.showNavigators()&&this.updateButtonState(),t.preventDefault()}onPrevButtonClick(){let t=this.content.nativeElement,i=Q(t),n=Math.abs(t.scrollLeft)-i,a=n<=0?0:n;t.scrollLeft=it(t)?-1*a:a}onNextButtonClick(){let t=this.content.nativeElement,i=Q(t)-this.getVisibleButtonWidths(),n=t.scrollLeft+i,a=t.scrollWidth-i,s=n>=a?a:n;t.scrollLeft=it(t)?-1*s:s}updateButtonState(){let t=this.content?.nativeElement,i=this.el?.nativeElement,{scrollWidth:n,offsetWidth:a}=t,s=Math.abs(t.scrollLeft),tt=Q(t);this.isPrevButtonEnabled.set(s!==0),this.isNextButtonEnabled.set(i.offsetWidth>=a&&Math.abs(s-n+tt)>1)}updateInkBar(){let t=this.content?.nativeElement,i=this.inkbar?.nativeElement,n=this.tabs?.nativeElement,a=mt(t,'[data-pc-name="tab"][data-p-active="true"]');i&&(i.style.width=gt(a)+"px",i.style.left=at(a).left-at(n).left+"px")}getVisibleButtonWidths(){let t=this.prevButton?.nativeElement,i=this.nextButton?.nativeElement;return[t,i].reduce((n,a)=>a?n+Q(a):n,0)}bindResizeObserver(){this.resizeObserver=new ResizeObserver(()=>this.updateButtonState()),this.resizeObserver.observe(this.el.nativeElement)}unbindResizeObserver(){this.resizeObserver&&(this.resizeObserver.unobserve(this.el.nativeElement),this.resizeObserver=null)}static \u0275fac=function(i){return new(i||e)};static \u0275cmp=x({type:e,selectors:[["p-tablist"]],contentQueries:function(i,n,a){if(i&1&&(J(a,Vt,4),J(a,Ot,4),J(a,_t,4)),i&2){let s;p(s=f())&&(n.prevIconTemplate=s.first),p(s=f())&&(n.nextIconTemplate=s.first),p(s=f())&&(n.templates=s)}},viewQuery:function(i,n){if(i&1&&(M(Pt,5),M(Rt,5),M(zt,5),M(Qt,5),M(jt,5)),i&2){let a;p(a=f())&&(n.content=a.first),p(a=f())&&(n.prevButton=a.first),p(a=f())&&(n.nextButton=a.first),p(a=f())&&(n.inkbar=a.first),p(a=f())&&(n.tabs=a.first)}},hostVars:2,hostBindings:function(i,n){i&2&&c(n.cx("root"))},features:[k([It,{provide:Mt,useExisting:e},{provide:A,useExisting:e}]),w([l]),B],ngContentSelectors:j,decls:9,vars:11,consts:[["content",""],["tabs",""],["inkbar",""],["prevButton",""],["nextButton",""],["type","button","pRipple","",3,"pBind","class"],[3,"scroll","pBind"],["role","tablist",3,"pBind"],["role","presentation",3,"pBind"],["type","button","pRipple","",3,"click","pBind"],["data-p-icon","chevron-left"],[4,"ngTemplateOutlet"],["data-p-icon","chevron-right"]],template:function(i,n){if(i&1){let a=G();N(),D(0,qt,4,7,"button",5),V(1,"div",6,0),O("scroll",function(tt){return H(a),K(n.onScroll(tt))}),V(3,"div",7,1),I(5),W(6,"span",8,2),q()(),D(8,Jt,4,7,"button",5)}i&2&&(C(n.showNavigators()&&n.isPrevButtonEnabled()?0:-1),v(),c(n.cx("content")),b("pBind",n.ptm("content")),v(2),c(n.cx("tabList")),b("pBind",n.ptm("tabList")),v(3),c(n.cx("activeBar")),b("pBind",n.ptm("activeBar")),v(2),C(n.showNavigators()&&n.isNextButtonEnabled()?8:-1))},dependencies:[R,Y,xt,Bt,wt,st,ot,L,l],encapsulation:2,changeDetection:0})}return e})(),kt=new _("TAB_INSTANCE"),Fe=(()=>{class e extends F{$pcTab=o(kt,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=o(l,{self:!0});onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptms(["host","root"]))}value=X();disabled=g(!1,{transform:y});pcTabs=o(S(()=>rt));pcTabList=o(S(()=>ie));el=o(lt);_componentStyle=o(Nt);ripple=r(()=>this.config.ripple());id=r(()=>`${this.pcTabs.id()}_tab_${this.value()}`);ariaControls=r(()=>`${this.pcTabs.id()}_tabpanel_${this.value()}`);active=r(()=>nt(this.pcTabs.value(),this.value()));tabindex=r(()=>this.disabled()?-1:this.active()?this.pcTabs.tabindex():-1);mutationObserver;onFocus(t){this.disabled()||this.pcTabs.selectOnFocus()&&this.changeActiveValue()}onClick(t){this.disabled()||this.changeActiveValue()}onKeyDown(t){switch(t.code){case"ArrowRight":this.onArrowRightKey(t);break;case"ArrowLeft":this.onArrowLeftKey(t);break;case"Home":this.onHomeKey(t);break;case"End":this.onEndKey(t);break;case"PageDown":this.onPageDownKey(t);break;case"PageUp":this.onPageUpKey(t);break;case"Enter":case"NumpadEnter":case"Space":this.onEnterKey(t);break;default:break}t.stopPropagation()}onAfterViewInit(){this.bindMutationObserver()}onArrowRightKey(t){let i=this.findNextTab(t.currentTarget);i?this.changeFocusedTab(t,i):this.onHomeKey(t),t.preventDefault()}onArrowLeftKey(t){let i=this.findPrevTab(t.currentTarget);i?this.changeFocusedTab(t,i):this.onEndKey(t),t.preventDefault()}onHomeKey(t){let i=this.findFirstTab();this.changeFocusedTab(t,i),t.preventDefault()}onEndKey(t){let i=this.findLastTab();this.changeFocusedTab(t,i),t.preventDefault()}onPageDownKey(t){this.scrollInView(this.findLastTab()),t.preventDefault()}onPageUpKey(t){this.scrollInView(this.findFirstTab()),t.preventDefault()}onEnterKey(t){this.disabled()||this.changeActiveValue(),t.preventDefault()}findNextTab(t,i=!1){let n=i?t:t.nextElementSibling;return n?z(n,"data-p-disabled")||z(n,"data-pc-section")==="activebar"?this.findNextTab(n):n:null}findPrevTab(t,i=!1){let n=i?t:t.previousElementSibling;return n?z(n,"data-p-disabled")||z(n,"data-pc-section")==="activebar"?this.findPrevTab(n):n:null}findFirstTab(){return this.findNextTab(this.pcTabList?.tabs?.nativeElement?.firstElementChild,!0)}findLastTab(){return this.findPrevTab(this.pcTabList?.tabs?.nativeElement?.lastElementChild,!0)}changeActiveValue(){this.pcTabs.updateValue(this.value())}changeFocusedTab(t,i){yt(i),this.scrollInView(i)}scrollInView(t){t?.scrollIntoView?.({block:"nearest"})}bindMutationObserver(){Z(this.platformId)&&(this.mutationObserver=new MutationObserver(t=>{t.forEach(()=>{this.active()&&this.pcTabList?.updateInkBar()})}),this.mutationObserver.observe(this.el.nativeElement,{childList:!0,characterData:!0,subtree:!0}))}unbindMutationObserver(){this.mutationObserver?.disconnect()}onDestroy(){this.mutationObserver&&this.unbindMutationObserver()}static \u0275fac=(()=>{let t;return function(n){return(t||(t=u(e)))(n||e)}})();static \u0275cmp=x({type:e,selectors:[["p-tab"]],hostVars:10,hostBindings:function(i,n){i&1&&O("focus",function(s){return n.onFocus(s)})("click",function(s){return n.onClick(s)})("keydown",function(s){return n.onKeyDown(s)}),i&2&&(m("id",n.id())("aria-controls",n.ariaControls())("role","tab")("aria-selected",n.active())("aria-disabled",n.disabled())("data-p-disabled",n.disabled())("data-p-active",n.active())("tabindex",n.tabindex()),c(n.cx("root")))},inputs:{value:[1,"value"],disabled:[1,"disabled"]},outputs:{value:"valueChange"},features:[k([Nt,{provide:kt,useExisting:e},{provide:A,useExisting:e}]),w([st,l]),B],ngContentSelectors:j,decls:1,vars:0,template:function(i,n){i&1&&(N(),I(0))},dependencies:[R,ot,L],encapsulation:2,changeDetection:0})}return e})(),ae={root:({instance:e})=>["p-tabpanel",{"p-tabpanel-active":e.active()}]},Et=(()=>{class e extends E{name="tabpanel";classes=ae;static \u0275fac=(()=>{let t;return function(n){return(t||(t=u(e)))(n||e)}})();static \u0275prov=T({token:e,factory:e.\u0275fac})}return e})();var At=new _("TABPANEL_INSTANCE"),Le=(()=>{class e extends F{$pcTabPanel=o(At,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=o(l,{self:!0});pcTabs=o(S(()=>rt));onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptms(["host","root"]))}lazy=g(!1,{transform:y});value=X(void 0);content=vt("content");id=r(()=>`${this.pcTabs.id()}_tabpanel_${this.value()}`);ariaLabelledby=r(()=>`${this.pcTabs.id()}_tab_${this.value()}`);active=r(()=>nt(this.pcTabs.value(),this.value()));isLazyEnabled=r(()=>this.pcTabs.lazy()||this.lazy());hasBeenRendered=!1;shouldRender=r(()=>!this.isLazyEnabled()||this.hasBeenRendered?!0:this.active()?(this.hasBeenRendered=!0,!0):!1);_componentStyle=o(Et);static \u0275fac=(()=>{let t;return function(n){return(t||(t=u(e)))(n||e)}})();static \u0275cmp=x({type:e,selectors:[["p-tabpanel"]],contentQueries:function(i,n,a){i&1&&dt(a,n.content,Pt,5),i&2&&ut()},hostVars:7,hostBindings:function(i,n){i&2&&(ct("hidden",!n.active()),m("id",n.id())("role","tabpanel")("aria-labelledby",n.ariaLabelledby())("data-p-active",n.active()),c(n.cx("root")))},inputs:{lazy:[1,"lazy"],value:[1,"value"]},outputs:{value:"valueChange"},features:[k([Et,{provide:At,useExisting:e},{provide:A,useExisting:e}]),w([l]),B],ngContentSelectors:j,decls:3,vars:1,consts:[["defaultContent",""],[4,"ngTemplateOutlet"]],template:function(i,n){i&1&&(N(),P(0,Xt,1,0,"ng-template",null,0,pt),D(2,Zt,1,1,"ng-container")),i&2&&(v(2),C(n.shouldRender()?2:-1))},dependencies:[Y,L],encapsulation:2,changeDetection:0})}return e})(),oe={root:"p-tabpanels"},Ft=(()=>{class e extends E{name="tabpanels";classes=oe;static \u0275fac=(()=>{let t;return function(n){return(t||(t=u(e)))(n||e)}})();static \u0275prov=T({token:e,factory:e.\u0275fac})}return e})();var Lt=new _("TABPANELS_INSTANCE"),Se=(()=>{class e extends F{$pcTabPanels=o(Lt,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=o(l,{self:!0});_componentStyle=o(Ft);onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptms(["host","root"]))}static \u0275fac=(()=>{let t;return function(n){return(t||(t=u(e)))(n||e)}})();static \u0275cmp=x({type:e,selectors:[["p-tabpanels"]],hostVars:3,hostBindings:function(i,n){i&2&&(m("role","presentation"),c(n.cx("root")))},features:[k([Ft,{provide:Lt,useExisting:e},{provide:A,useExisting:e}]),w([l]),B],ngContentSelectors:j,decls:1,vars:0,template:function(i,n){i&1&&(N(),I(0))},dependencies:[R,L],encapsulation:2,changeDetection:0})}return e})(),St=new _("TABS_INSTANCE"),rt=(()=>{class e extends F{$pcTabs=o(St,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=o(l,{self:!0});onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptms(["host","root"]))}value=X(void 0);scrollable=g(!1,{transform:y});lazy=g(!1,{transform:y});selectOnFocus=g(!1,{transform:y});showNavigators=g(!0,{transform:y});tabindex=g(0,{transform:ht});id=$(Tt("pn_id_"));_componentStyle=o(Ct);updateValue(t){this.value.update(()=>t)}static \u0275fac=(()=>{let t;return function(n){return(t||(t=u(e)))(n||e)}})();static \u0275cmp=x({type:e,selectors:[["p-tabs"]],hostVars:3,hostBindings:function(i,n){i&2&&(m("id",n.id()),c(n.cx("root")))},inputs:{value:[1,"value"],scrollable:[1,"scrollable"],lazy:[1,"lazy"],selectOnFocus:[1,"selectOnFocus"],showNavigators:[1,"showNavigators"],tabindex:[1,"tabindex"]},outputs:{value:"valueChange"},features:[k([Ct,{provide:St,useExisting:e},{provide:A,useExisting:e}]),w([l]),B],ngContentSelectors:j,decls:1,vars:0,template:function(i,n){i&1&&(N(),I(0))},dependencies:[R,L],encapsulation:2,changeDetection:0})}return e})();export{ie as a,Fe as b,Le as c,Se as d,rt as e};
