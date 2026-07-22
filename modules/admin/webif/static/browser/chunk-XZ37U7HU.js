import{a as de}from"./chunk-6RJNNOA7.js";import{b as ce}from"./chunk-KN6SFELY.js";import{c as se,e as le,i as B}from"./chunk-JKP3TXC4.js";import{Ma as ie,Va as ae,Ya as re,ab as T,bb as O,cb as d,db as F,jb as pe,p as oe,r as te,ta as A,ua as L,v as P,va as M}from"./chunk-XMFB5O6P.js";import{Eb as r,Fb as z,Gb as J,Hb as N,Kc as c,Lb as V,Mb as j,Oc as H,Sb as R,Sc as $,T as m,U as Q,Ub as u,Va as p,Vb as x,Wb as w,X as _,Xb as X,Z as a,Zb as Y,_b as Z,a as y,dc as ee,fa as S,gc as s,hb as C,ka as K,lb as D,mb as E,nb as b,oa as q,sc as I,ta as v,uc as ne,vb as f,yb as G,zb as W}from"./chunk-25ZXD53X.js";var ue=`
    .p-accordionpanel {
        display: flex;
        flex-direction: column;
        border-style: solid;
        border-width: dt('accordion.panel.border.width');
        border-color: dt('accordion.panel.border.color');
    }

    .p-accordionheader {
        all: unset;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: dt('accordion.header.padding');
        color: dt('accordion.header.color');
        background: dt('accordion.header.background');
        border-style: solid;
        border-width: dt('accordion.header.border.width');
        border-color: dt('accordion.header.border.color');
        font-weight: dt('accordion.header.font.weight');
        border-radius: dt('accordion.header.border.radius');
        transition:
            background dt('accordion.transition.duration'),
            color dt('accordion.transition.duration'),
            outline-color dt('accordion.transition.duration'),
            box-shadow dt('accordion.transition.duration');
        outline-color: transparent;
    }

    .p-accordionpanel:first-child > .p-accordionheader {
        border-width: dt('accordion.header.first.border.width');
        border-start-start-radius: dt('accordion.header.first.top.border.radius');
        border-start-end-radius: dt('accordion.header.first.top.border.radius');
    }

    .p-accordionpanel:last-child > .p-accordionheader {
        border-end-start-radius: dt('accordion.header.last.bottom.border.radius');
        border-end-end-radius: dt('accordion.header.last.bottom.border.radius');
    }

    .p-accordionpanel:last-child.p-accordionpanel-active > .p-accordionheader {
        border-end-start-radius: dt('accordion.header.last.active.bottom.border.radius');
        border-end-end-radius: dt('accordion.header.last.active.bottom.border.radius');
    }

    .p-accordionheader-toggle-icon {
        color: dt('accordion.header.toggle.icon.color');
    }

    .p-accordionpanel:not(.p-disabled) .p-accordionheader:focus-visible {
        box-shadow: dt('accordion.header.focus.ring.shadow');
        outline: dt('accordion.header.focus.ring.width') dt('accordion.header.focus.ring.style') dt('accordion.header.focus.ring.color');
        outline-offset: dt('accordion.header.focus.ring.offset');
    }

    .p-accordionpanel:not(.p-accordionpanel-active):not(.p-disabled) > .p-accordionheader:hover {
        background: dt('accordion.header.hover.background');
        color: dt('accordion.header.hover.color');
    }

    .p-accordionpanel:not(.p-accordionpanel-active):not(.p-disabled) .p-accordionheader:hover .p-accordionheader-toggle-icon {
        color: dt('accordion.header.toggle.icon.hover.color');
    }

    .p-accordionpanel:not(.p-disabled).p-accordionpanel-active > .p-accordionheader {
        background: dt('accordion.header.active.background');
        color: dt('accordion.header.active.color');
    }

    .p-accordionpanel:not(.p-disabled).p-accordionpanel-active > .p-accordionheader .p-accordionheader-toggle-icon {
        color: dt('accordion.header.toggle.icon.active.color');
    }

    .p-accordionpanel:not(.p-disabled).p-accordionpanel-active > .p-accordionheader:hover {
        background: dt('accordion.header.active.hover.background');
        color: dt('accordion.header.active.hover.color');
    }

    .p-accordionpanel:not(.p-disabled).p-accordionpanel-active > .p-accordionheader:hover .p-accordionheader-toggle-icon {
        color: dt('accordion.header.toggle.icon.active.hover.color');
    }

    .p-accordioncontent {
        display: grid;
        grid-template-rows: 1fr;
    }

    .p-accordioncontent-wrapper {
        min-height: 0;
    }

    .p-accordioncontent-content {
        border-style: solid;
        border-width: dt('accordion.content.border.width');
        border-color: dt('accordion.content.border.color');
        background-color: dt('accordion.content.background');
        color: dt('accordion.content.color');
        padding: dt('accordion.content.padding');
    }
`;var k=["*"],be=["toggleicon"],Ae=o=>({active:o});function ye(o,l){}function _e(o,l){o&1&&b(0,ye,0,0,"ng-template")}function Ce(o,l){if(o&1&&b(0,_e,1,0,null,0),o&2){let e=u();r("ngTemplateOutlet",e.toggleicon)("ngTemplateOutletContext",ne(2,Ae,e.active()))}}function De(o,l){if(o&1&&N(0,"span",4),o&2){let e=u(3);s(e.cn(e.cx("toggleicon"),e.pcAccordion.collapseIcon)),r("pBind",e.ptm("toggleicon")),f("aria-hidden",!0)}}function Ee(o,l){if(o&1&&(S(),N(0,"svg",5)),o&2){let e=u(3);s(e.cx("toggleicon")),r("pBind",e.ptm("toggleicon")),f("aria-hidden",!0)}}function Ne(o,l){if(o&1&&(V(0),b(1,De,1,4,"span",2)(2,Ee,1,4,"svg",3),j()),o&2){let e=u(2);p(),r("ngIf",e.pcAccordion.collapseIcon),p(),r("ngIf",!e.pcAccordion.collapseIcon)}}function xe(o,l){if(o&1&&N(0,"span",4),o&2){let e=u(3);s(e.cn(e.cx("toggleicon"),e.pcAccordion.expandIcon)),r("pBind",e.ptm("toggleicon")),f("aria-hidden",!0)}}function we(o,l){if(o&1&&(S(),N(0,"svg",7)),o&2){let e=u(3);r("pBind",e.ptm("toggleicon")),f("aria-hidden",!0)}}function Ie(o,l){if(o&1&&(V(0),b(1,xe,1,4,"span",2)(2,we,1,2,"svg",6),j()),o&2){let e=u(2);p(),r("ngIf",e.pcAccordion.expandIcon),p(),r("ngIf",!e.pcAccordion.expandIcon)}}function He(o,l){if(o&1&&b(0,Ne,3,2,"ng-container",1)(1,Ie,3,2,"ng-container",1),o&2){let e=u();r("ngIf",e.active()),p(),r("ngIf",!e.active())}}var Pe=`
${ue}

/* For PrimeNG */
.p-accordionheader-toggle-icon.icon-start {
    order: -1;
}

.p-accordionheader:has(.p-accordionheader-toggle-icon.icon-start) {
    justify-content: flex-start;
    gap: dt('accordion.header.padding');
}

.p-accordionheader.p-ripple {
    overflow: hidden;
    position: relative;
}

.p-accordioncontent .p-motion {
    display: grid;
    grid-template-rows: 1fr;
}
`,Me={root:"p-accordion p-component",panel:({instance:o})=>["p-accordionpanel",{"p-accordionpanel-active":o.active(),"p-disabled":o.disabled()}],header:"p-accordionheader",toggleicon:"p-accordionheader-toggle-icon",contentContainer:"p-accordioncontent",contentWrapper:"p-accordioncontent-wrapper",content:"p-accordioncontent-content"},g=(()=>{class o extends re{name="accordion";style=Pe;classes=Me;static \u0275fac=(()=>{let e;return function(n){return(e||(e=v(o)))(n||o)}})();static \u0275prov=Q({token:o,factory:o.\u0275fac})}return o})();var he=new _("ACCORDION_PANEL_INSTANCE"),fe=new _("ACCORDION_HEADER_INSTANCE"),ge=new _("ACCORDION_CONTENT_INSTANCE"),me=new _("ACCORDION_INSTANCE"),ve=(()=>{class o extends O{$pcAccordionPanel=a(he,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=a(d,{self:!0});componentName="AccordionPanel";onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptm("root"))}pcAccordion=a(m(()=>U));value=$(void 0);disabled=H(!1,{transform:e=>B(e)});active=c(()=>this.pcAccordion.multiple()?this.valueEquals(this.pcAccordion.value(),this.value()):this.pcAccordion.value()===this.value());valueEquals(e,t){return Array.isArray(e)?e.includes(t):e===t}_componentStyle=a(g);static \u0275fac=(()=>{let e;return function(n){return(e||(e=v(o)))(n||o)}})();static \u0275cmp=C({type:o,selectors:[["p-accordion-panel"],["p-accordionpanel"]],hostVars:4,hostBindings:function(t,n){t&2&&(f("data-p-disabled",n.disabled())("data-p-active",n.active()),s(n.cx("panel")))},inputs:{value:[1,"value"],disabled:[1,"disabled"]},outputs:{value:"valueChange"},features:[I([g,{provide:he,useExisting:o},{provide:T,useExisting:o}]),D([d]),E],ngContentSelectors:k,decls:1,vars:0,template:function(t,n){t&1&&(x(),w(0))},dependencies:[P,F],encapsulation:2,changeDetection:0})}return o})(),cn=(()=>{class o extends O{$pcAccordionHeader=a(fe,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=a(d,{self:!0});componentName="AccordionHeader";onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptm("root"))}pcAccordion=a(m(()=>U));pcAccordionPanel=a(m(()=>ve));id=c(()=>`${this.pcAccordion.id()}_accordionheader_${this.pcAccordionPanel.value()}`);active=c(()=>this.pcAccordionPanel.active());disabled=c(()=>this.pcAccordionPanel.disabled());ariaControls=c(()=>`${this.pcAccordion.id()}_accordioncontent_${this.pcAccordionPanel.value()}`);toggleicon;onClick(e){if(this.disabled())return;let t=this.active();this.changeActiveValue();let n=this.active(),i=this.pcAccordionPanel.value();!t&&n?this.pcAccordion.onOpen.emit({originalEvent:e,index:i}):t&&!n&&this.pcAccordion.onClose.emit({originalEvent:e,index:i})}onFocus(){!this.disabled()&&this.pcAccordion.selectOnFocus()&&this.changeActiveValue()}onKeydown(e){switch(e.code){case"ArrowDown":this.arrowDownKey(e);break;case"ArrowUp":this.arrowUpKey(e);break;case"Home":this.onHomeKey(e);break;case"End":this.onEndKey(e);break;case"Enter":case"Space":case"NumpadEnter":this.onEnterKey(e);break;default:break}}_componentStyle=a(g);changeActiveValue(){this.pcAccordion.updateValue(this.pcAccordionPanel.value())}findPanel(e){return e?.closest('[data-pc-name="accordionpanel"]')}findHeader(e){return A(e,'[data-pc-name="accordionheader"]')}findNextPanel(e,t=!1){let n=t?e:e.nextElementSibling;return n?M(n,"data-p-disabled")?this.findNextPanel(n):this.findHeader(n):null}findPrevPanel(e,t=!1){let n=t?e:e.previousElementSibling;return n?M(n,"data-p-disabled")?this.findPrevPanel(n):this.findHeader(n):null}findFirstPanel(){return this.findNextPanel(this.pcAccordion.el.nativeElement.firstElementChild,!0)}findLastPanel(){return this.findPrevPanel(this.pcAccordion.el.nativeElement.lastElementChild,!0)}changeFocusedPanel(e,t){L(t)}arrowDownKey(e){let t=this.findNextPanel(this.findPanel(e.currentTarget));t?this.changeFocusedPanel(e,t):this.onHomeKey(e),e.preventDefault()}arrowUpKey(e){let t=this.findPrevPanel(this.findPanel(e.currentTarget));t?this.changeFocusedPanel(e,t):this.onEndKey(e),e.preventDefault()}onHomeKey(e){let t=this.findFirstPanel();this.changeFocusedPanel(e,t),e.preventDefault()}onEndKey(e){let t=this.findLastPanel();this.changeFocusedPanel(e,t),e.preventDefault()}onEnterKey(e){this.disabled()||this.changeActiveValue(),e.preventDefault()}get dataP(){return this.cn({active:this.active()})}static \u0275fac=(()=>{let e;return function(n){return(e||(e=v(o)))(n||o)}})();static \u0275cmp=C({type:o,selectors:[["p-accordion-header"],["p-accordionheader"]],contentQueries:function(t,n,i){if(t&1&&X(i,be,5),t&2){let h;Y(h=Z())&&(n.toggleicon=h.first)}},hostVars:13,hostBindings:function(t,n){t&1&&R("click",function(h){return n.onClick(h)})("focus",function(){return n.onFocus()})("keydown",function(h){return n.onKeydown(h)}),t&2&&(f("id",n.id())("aria-expanded",n.active())("aria-controls",n.ariaControls())("aria-disabled",n.disabled())("role","button")("tabindex",n.disabled()?"-1":"0")("data-p-active",n.active())("data-p-disabled",n.disabled())("data-p",n.dataP),s(n.cx("header")),ee("user-select","none"))},features:[I([g,{provide:fe,useExisting:o},{provide:T,useExisting:o}]),D([pe,d]),E],ngContentSelectors:k,decls:3,vars:1,consts:[[4,"ngTemplateOutlet","ngTemplateOutletContext"],[4,"ngIf"],[3,"class","pBind",4,"ngIf"],["data-p-icon","chevron-up",3,"class","pBind",4,"ngIf"],[3,"pBind"],["data-p-icon","chevron-up",3,"pBind"],["data-p-icon","chevron-down",3,"pBind",4,"ngIf"],["data-p-icon","chevron-down",3,"pBind"]],template:function(t,n){t&1&&(x(),w(0),G(1,Ce,1,4)(2,He,2,2)),t&2&&(p(),W(n.toggleicon?1:2))},dependencies:[P,oe,te,ce,de,F,d],encapsulation:2,changeDetection:0})}return o})(),dn=(()=>{class o extends O{$pcAccordionContent=a(ge,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=a(d,{self:!0});componentName="AccordionContent";onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptm("root"))}pcAccordion=a(m(()=>U));pcAccordionPanel=a(m(()=>ve));active=c(()=>this.pcAccordionPanel.active());ariaLabelledby=c(()=>`${this.pcAccordion.id()}_accordionheader_${this.pcAccordionPanel.value()}`);id=c(()=>`${this.pcAccordion.id()}_accordioncontent_${this.pcAccordionPanel.value()}`);_componentStyle=a(g);ptParams=c(()=>({context:this.active()}));computedMotionOptions=c(()=>y(y({},this.ptm("motion",this.ptParams())),this.pcAccordion.computedMotionOptions()));static \u0275fac=(()=>{let e;return function(n){return(e||(e=v(o)))(n||o)}})();static \u0275cmp=C({type:o,selectors:[["p-accordion-content"],["p-accordioncontent"]],hostVars:6,hostBindings:function(t,n){t&2&&(f("id",n.id())("role","region")("data-p-active",n.active())("aria-labelledby",n.ariaLabelledby()),s(n.cx("contentContainer")))},features:[I([g,{provide:ge,useExisting:o},{provide:T,useExisting:o}]),D([d]),E],ngContentSelectors:k,decls:4,vars:10,consts:[["name","p-collapsible","hideStrategy","visibility",3,"visible","mountOnEnter","unmountOnLeave","options"],[3,"pBind"]],template:function(t,n){t&1&&(x(),z(0,"p-motion",0)(1,"div",1)(2,"div",1),w(3),J()()()),t&2&&(r("visible",n.active())("mountOnEnter",!1)("unmountOnLeave",!1)("options",n.computedMotionOptions()),p(),s(n.cx("contentWrapper")),r("pBind",n.ptm("contentWrapper",n.ptParams())),p(),s(n.cx("content")),r("pBind",n.ptm("content",n.ptParams())))},dependencies:[P,F,d,le,se],encapsulation:2,changeDetection:0})}return o})(),U=(()=>{class o extends O{componentName="Accordion";$pcAccordion=a(me,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=a(d,{self:!0});onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptm("root"))}value=$(void 0);multiple=H(!1,{transform:e=>B(e)});styleClass;expandIcon;collapseIcon;selectOnFocus=H(!1,{transform:e=>B(e)});transitionOptions="400ms cubic-bezier(0.86, 0, 0.07, 1)";motionOptions=H(void 0);computedMotionOptions=c(()=>y(y({},this.ptm("motion")),this.motionOptions()));onClose=new K;onOpen=new K;id=q(ie("pn_id_"));_componentStyle=a(g);onKeydown(e){switch(e.code){case"ArrowDown":this.onTabArrowDownKey(e);break;case"ArrowUp":this.onTabArrowUpKey(e);break;case"Home":e.shiftKey||this.onTabHomeKey(e);break;case"End":e.shiftKey||this.onTabEndKey(e);break}}onTabArrowDownKey(e){let t=this.findNextHeaderAction(e.target.parentElement);t?this.changeFocusedTab(t):this.onTabHomeKey(e),e.preventDefault()}onTabArrowUpKey(e){let t=this.findPrevHeaderAction(e.target.parentElement);t?this.changeFocusedTab(t):this.onTabEndKey(e),e.preventDefault()}onTabHomeKey(e){let t=this.findFirstHeaderAction();this.changeFocusedTab(t),e.preventDefault()}changeFocusedTab(e){e&&L(e)}findNextHeaderAction(e,t=!1){let n=t?e:e.nextElementSibling,i=A(n,'[data-pc-section="accordionheader"]');return i?M(i,"data-p-disabled")?this.findNextHeaderAction(i.parentElement):A(i.parentElement,'[data-pc-section="accordionheader"]'):null}findPrevHeaderAction(e,t=!1){let n=t?e:e.previousElementSibling,i=A(n,'[data-pc-section="accordionheader"]');return i?M(i,"data-p-disabled")?this.findPrevHeaderAction(i.parentElement):A(i.parentElement,'[data-pc-section="accordionheader"]'):null}findFirstHeaderAction(){let e=this.el.nativeElement.firstElementChild;return this.findNextHeaderAction(e,!0)}findLastHeaderAction(){let e=this.el.nativeElement.lastElementChild;return this.findPrevHeaderAction(e,!0)}onTabEndKey(e){let t=this.findLastHeaderAction();this.changeFocusedTab(t),e.preventDefault()}getBlockableElement(){return this.el.nativeElement.children[0]}updateValue(e){let t=this.value();if(this.multiple()){let n=Array.isArray(t)?[...t]:[],i=n.indexOf(e);i!==-1?n.splice(i,1):n.push(e),this.value.set(n)}else t===e?this.value.set(void 0):this.value.set(e)}static \u0275fac=(()=>{let e;return function(n){return(e||(e=v(o)))(n||o)}})();static \u0275cmp=C({type:o,selectors:[["p-accordion"]],hostVars:2,hostBindings:function(t,n){t&1&&R("keydown",function(h){return n.onKeydown(h)}),t&2&&s(n.cn(n.cx("root"),n.styleClass))},inputs:{value:[1,"value"],multiple:[1,"multiple"],styleClass:"styleClass",expandIcon:"expandIcon",collapseIcon:"collapseIcon",selectOnFocus:[1,"selectOnFocus"],transitionOptions:"transitionOptions",motionOptions:[1,"motionOptions"]},outputs:{value:"valueChange",onClose:"onClose",onOpen:"onOpen"},features:[I([g,{provide:me,useExisting:o},{provide:T,useExisting:o}]),D([d]),E],ngContentSelectors:k,decls:1,vars:0,template:function(t,n){t&1&&(x(),w(0))},dependencies:[P,ae,F],encapsulation:2,changeDetection:0})}return o})();export{ve as a,cn as b,dn as c,U as d};
