import{a as ue}from"./chunk-JTSAB4XJ.js";import{b as pe}from"./chunk-XJPGZAJH.js";import{f as M}from"./chunk-FQUEGOUU.js";import{c as ce,d as L,f as U,g as Q,h as q}from"./chunk-4O3FVBGX.js";import{Ja as se,Ma as le,Pa as T,Qa as F,Ra as c,Sa as B,Ya as he,ha as _,ia as G,ja as P,m as ae,o as re,s as N,ya as de}from"./chunk-PN5D6VAD.js";import{$b as te,Ab as Y,Fb as r,Gb as Z,Hb as ee,Ib as x,Jc as s,Mb as V,Nb as j,Nc as k,Pc as $,Tb as R,Ua as g,Vb as p,Wb as w,Xb as I,Y as m,Yb as ne,Z as z,Za as K,_b as oe,aa as y,ca as a,dc as ie,gc as u,ib as C,ka as S,mb as D,nb as E,ob as b,qa as J,sc as H,uc as A,va as v,wb as h,zb as X}from"./chunk-HJNL6B4D.js";var fe=`
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

    .p-accordioncontent-content {
        border-style: solid;
        border-width: dt('accordion.content.border.width');
        border-color: dt('accordion.content.border.color');
        background-color: dt('accordion.content.background');
        color: dt('accordion.content.color');
        padding: dt('accordion.content.padding');
    }
`;var O=["*"],ye=["toggleicon"],Ce=n=>({active:n});function De(n,l){}function Ee(n,l){n&1&&b(0,De,0,0,"ng-template")}function xe(n,l){if(n&1&&b(0,Ee,1,0,null,0),n&2){let e=p();r("ngTemplateOutlet",e.toggleicon)("ngTemplateOutletContext",A(2,Ce,e.active()))}}function we(n,l){if(n&1&&x(0,"span",4),n&2){let e=p(3);u(e.cn(e.cx("toggleicon"),e.pcAccordion.collapseIcon)),r("pBind",e.ptm("toggleicon")),h("aria-hidden",!0)}}function Ie(n,l){if(n&1&&(S(),x(0,"svg",5)),n&2){let e=p(3);u(e.cx("toggleicon")),r("pBind",e.ptm("toggleicon")),h("aria-hidden",!0)}}function He(n,l){if(n&1&&(V(0),b(1,we,1,4,"span",2)(2,Ie,1,4,"svg",3),j()),n&2){let e=p(2);g(),r("ngIf",e.pcAccordion.collapseIcon),g(),r("ngIf",!e.pcAccordion.collapseIcon)}}function Ne(n,l){if(n&1&&x(0,"span",4),n&2){let e=p(3);u(e.cn(e.cx("toggleicon"),e.pcAccordion.expandIcon)),r("pBind",e.ptm("toggleicon")),h("aria-hidden",!0)}}function Pe(n,l){if(n&1&&(S(),x(0,"svg",7)),n&2){let e=p(3);r("pBind",e.ptm("toggleicon")),h("aria-hidden",!0)}}function Te(n,l){if(n&1&&(V(0),b(1,Ne,1,4,"span",2)(2,Pe,1,2,"svg",6),j()),n&2){let e=p(2);g(),r("ngIf",e.pcAccordion.expandIcon),g(),r("ngIf",!e.pcAccordion.expandIcon)}}function Fe(n,l){if(n&1&&b(0,He,3,2,"ng-container",1)(1,Te,3,2,"ng-container",1),n&2){let e=p();r("ngIf",e.active()),g(),r("ngIf",!e.active())}}var ge=n=>({transitionParams:n}),Be=n=>({value:"visible",params:n}),ke=n=>({value:"hidden",params:n}),Me=`
    ${fe}

    /*For PrimeNG*/
    .p-accordionpanel:not(.p-accordionpanel-active) > .p-accordioncontent,
    .p-accordioncontent-content.ng-animating {
        overflow: hidden;
    }

    .p-accordionheader-toggle-icon.icon-start {
        order: -1;
    }

    .p-accordionheader:has(.p-accordionheader-toggle-icon.icon-start) {
        justify-content: flex-start;
        gap: dt('accordion.header.padding');
    }

    .p-accordioncontent.ng-animating {
        overflow: hidden;
    }

    .p-accordionheader.p-ripple {
        overflow: hidden;
        position: relative;
    }
`,Oe={root:"p-accordion p-component",panel:({instance:n})=>["p-accordionpanel",{"p-accordionpanel-active":n.active(),"p-disabled":n.disabled()}],header:"p-accordionheader",toggleicon:"p-accordionheader-toggle-icon",contentContainer:"p-accordioncontent",content:"p-accordioncontent-content"},f=(()=>{class n extends le{name="accordion";style=Me;classes=Oe;static \u0275fac=(()=>{let e;return function(o){return(e||(e=v(n)))(o||n)}})();static \u0275prov=z({token:n,factory:n.\u0275fac})}return n})();var me=new y("ACCORDION_PANEL_INSTANCE"),ve=new y("ACCORDION_HEADER_INSTANCE"),be=new y("ACCORDION_CONTENT_INSTANCE"),Ae=new y("ACCORDION_INSTANCE"),_e=(()=>{class n extends F{$pcAccordionPanel=a(me,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=a(c,{self:!0});onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptm("root"))}pcAccordion=a(m(()=>W));value=$(void 0);disabled=k(!1,{transform:e=>M(e)});active=s(()=>this.pcAccordion.multiple()?this.valueEquals(this.pcAccordion.value(),this.value()):this.pcAccordion.value()===this.value());valueEquals(e,t){return Array.isArray(e)?e.includes(t):e===t}_componentStyle=a(f);static \u0275fac=(()=>{let e;return function(o){return(e||(e=v(n)))(o||n)}})();static \u0275cmp=C({type:n,selectors:[["p-accordion-panel"],["p-accordionpanel"]],hostVars:4,hostBindings:function(t,o){t&2&&(h("data-p-disabled",o.disabled())("data-p-active",o.active()),u(o.cx("panel")))},inputs:{value:[1,"value"],disabled:[1,"disabled"]},outputs:{value:"valueChange"},features:[H([f,{provide:me,useExisting:n},{provide:T,useExisting:n}]),E([c]),D],ngContentSelectors:O,decls:1,vars:0,template:function(t,o){t&1&&(w(),I(0))},dependencies:[N,B],encapsulation:2,changeDetection:0})}return n})(),pn=(()=>{class n extends F{$pcAccordionHeader=a(ve,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=a(c,{self:!0});onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptm("root"))}pcAccordion=a(m(()=>W));pcAccordionPanel=a(m(()=>_e));id=s(()=>`${this.pcAccordion.id()}_accordionheader_${this.pcAccordionPanel.value()}`);active=s(()=>this.pcAccordionPanel.active());disabled=s(()=>this.pcAccordionPanel.disabled());ariaControls=s(()=>`${this.pcAccordion.id()}_accordioncontent_${this.pcAccordionPanel.value()}`);toggleicon;onClick(e){if(this.disabled())return;let t=this.active();this.changeActiveValue();let o=this.active(),i=this.pcAccordionPanel.value();!t&&o?this.pcAccordion.onOpen.emit({originalEvent:e,index:i}):t&&!o&&this.pcAccordion.onClose.emit({originalEvent:e,index:i})}onFocus(){!this.disabled()&&this.pcAccordion.selectOnFocus()&&this.changeActiveValue()}onKeydown(e){switch(e.code){case"ArrowDown":this.arrowDownKey(e);break;case"ArrowUp":this.arrowUpKey(e);break;case"Home":this.onHomeKey(e);break;case"End":this.onEndKey(e);break;case"Enter":case"Space":case"NumpadEnter":this.onEnterKey(e);break;default:break}}_componentStyle=a(f);changeActiveValue(){this.pcAccordion.updateValue(this.pcAccordionPanel.value())}findPanel(e){return e?.closest('[data-pc-name="accordionpanel"]')}findHeader(e){return _(e,'[data-pc-name="accordionheader"]')}findNextPanel(e,t=!1){let o=t?e:e.nextElementSibling;return o?P(o,"data-p-disabled")?this.findNextPanel(o):this.findHeader(o):null}findPrevPanel(e,t=!1){let o=t?e:e.previousElementSibling;return o?P(o,"data-p-disabled")?this.findPrevPanel(o):this.findHeader(o):null}findFirstPanel(){return this.findNextPanel(this.pcAccordion.el.nativeElement.firstElementChild,!0)}findLastPanel(){return this.findPrevPanel(this.pcAccordion.el.nativeElement.lastElementChild,!0)}changeFocusedPanel(e,t){G(t)}arrowDownKey(e){let t=this.findNextPanel(this.findPanel(e.currentTarget));t?this.changeFocusedPanel(e,t):this.onHomeKey(e),e.preventDefault()}arrowUpKey(e){let t=this.findPrevPanel(this.findPanel(e.currentTarget));t?this.changeFocusedPanel(e,t):this.onEndKey(e),e.preventDefault()}onHomeKey(e){let t=this.findFirstPanel();this.changeFocusedPanel(e,t),e.preventDefault()}onEndKey(e){let t=this.findLastPanel();this.changeFocusedPanel(e,t),e.preventDefault()}onEnterKey(e){this.disabled()||this.changeActiveValue(),e.preventDefault()}static \u0275fac=(()=>{let e;return function(o){return(e||(e=v(n)))(o||n)}})();static \u0275cmp=C({type:n,selectors:[["p-accordion-header"],["p-accordionheader"]],contentQueries:function(t,o,i){if(t&1&&ne(i,ye,5),t&2){let d;oe(d=te())&&(o.toggleicon=d.first)}},hostVars:12,hostBindings:function(t,o){t&1&&R("click",function(d){return o.onClick(d)})("focus",function(d){return o.onFocus(d)})("keydown",function(d){return o.onKeydown(d)}),t&2&&(h("id",o.id())("aria-expanded",o.active())("aria-controls",o.ariaControls())("aria-disabled",o.disabled())("role","button")("tabindex",o.disabled()?"-1":"0")("data-p-active",o.active())("data-p-disabled",o.disabled()),u(o.cx("header")),ie("user-select","none"))},features:[H([f,{provide:ve,useExisting:n},{provide:T,useExisting:n}]),E([he,c]),D],ngContentSelectors:O,decls:3,vars:1,consts:[[4,"ngTemplateOutlet","ngTemplateOutletContext"],[4,"ngIf"],[3,"class","pBind",4,"ngIf"],["data-p-icon","chevron-up",3,"class","pBind",4,"ngIf"],[3,"pBind"],["data-p-icon","chevron-up",3,"pBind"],["data-p-icon","chevron-down",3,"pBind",4,"ngIf"],["data-p-icon","chevron-down",3,"pBind"]],template:function(t,o){t&1&&(w(),I(0),X(1,xe,1,4)(2,Fe,2,2)),t&2&&(g(),Y(o.toggleicon?1:2))},dependencies:[N,ae,re,pe,ue,B,c],encapsulation:2,changeDetection:0})}return n})(),un=(()=>{class n extends F{$pcAccordionContent=a(be,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=a(c,{self:!0});onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptm("root"))}pcAccordion=a(m(()=>W));pcAccordionPanel=a(m(()=>_e));active=s(()=>this.pcAccordionPanel.active());ariaLabelledby=s(()=>`${this.pcAccordion.id()}_accordionheader_${this.pcAccordionPanel.value()}`);id=s(()=>`${this.pcAccordion.id()}_accordioncontent_${this.pcAccordionPanel.value()}`);_componentStyle=a(f);ptParams=s(()=>({context:this.active()}));static \u0275fac=(()=>{let e;return function(o){return(e||(e=v(n)))(o||n)}})();static \u0275cmp=C({type:n,selectors:[["p-accordion-content"],["p-accordioncontent"]],hostVars:6,hostBindings:function(t,o){t&2&&(h("id",o.id())("role","region")("data-p-active",o.active())("aria-labelledby",o.ariaLabelledby()),u(o.cx("contentContainer")))},features:[H([f,{provide:be,useExisting:n},{provide:T,useExisting:n}]),E([c]),D],ngContentSelectors:O,decls:2,vars:12,consts:[[3,"pBind"]],template:function(t,o){t&1&&(w(),Z(0,"div",0),I(1),ee()),t&2&&(u(o.cx("content")),r("@content",o.active()?A(6,Be,A(4,ge,o.pcAccordion.transitionOptions)):A(10,ke,A(8,ge,o.pcAccordion.transitionOptions)))("pBind",o.ptm("content",o.ptParams())))},dependencies:[N,B,c],encapsulation:2,data:{animation:[ce("content",[Q("hidden",U({height:"0",paddingBlockStart:"0",paddingBlockEnd:"0",borderBlockStartWidth:"0",borderBlockEndWidth:"0",visibility:"hidden"})),Q("visible",U({height:"*"})),q("visible <=> hidden",[L("{{transitionParams}}")]),q("void => *",L(0))])]},changeDetection:0})}return n})(),W=(()=>{class n extends F{$pcAccordion=a(Ae,{optional:!0,skipSelf:!0})??void 0;bindDirectiveInstance=a(c,{self:!0});onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptm("root"))}value=$(void 0);multiple=k(!1,{transform:e=>M(e)});styleClass;expandIcon;collapseIcon;selectOnFocus=k(!1,{transform:e=>M(e)});transitionOptions="400ms cubic-bezier(0.86, 0, 0.07, 1)";onClose=new K;onOpen=new K;id=J(de("pn_id_"));_componentStyle=a(f);onKeydown(e){switch(e.code){case"ArrowDown":this.onTabArrowDownKey(e);break;case"ArrowUp":this.onTabArrowUpKey(e);break;case"Home":e.shiftKey||this.onTabHomeKey(e);break;case"End":e.shiftKey||this.onTabEndKey(e);break}}onTabArrowDownKey(e){let t=this.findNextHeaderAction(e.target.parentElement);t?this.changeFocusedTab(t):this.onTabHomeKey(e),e.preventDefault()}onTabArrowUpKey(e){let t=this.findPrevHeaderAction(e.target.parentElement);t?this.changeFocusedTab(t):this.onTabEndKey(e),e.preventDefault()}onTabHomeKey(e){let t=this.findFirstHeaderAction();this.changeFocusedTab(t),e.preventDefault()}changeFocusedTab(e){e&&G(e)}findNextHeaderAction(e,t=!1){let o=t?e:e.nextElementSibling,i=_(o,'[data-pc-section="accordionheader"]');return i?P(i,"data-p-disabled")?this.findNextHeaderAction(i.parentElement):_(i.parentElement,'[data-pc-section="accordionheader"]'):null}findPrevHeaderAction(e,t=!1){let o=t?e:e.previousElementSibling,i=_(o,'[data-pc-section="accordionheader"]');return i?P(i,"data-p-disabled")?this.findPrevHeaderAction(i.parentElement):_(i.parentElement,'[data-pc-section="accordionheader"]'):null}findFirstHeaderAction(){let e=this.el.nativeElement.firstElementChild;return this.findNextHeaderAction(e,!0)}findLastHeaderAction(){let e=this.el.nativeElement.lastElementChild;return this.findPrevHeaderAction(e,!0)}onTabEndKey(e){let t=this.findLastHeaderAction();this.changeFocusedTab(t),e.preventDefault()}getBlockableElement(){return this.el.nativeElement.children[0]}updateValue(e){let t=this.value();if(this.multiple()){let o=Array.isArray(t)?[...t]:[],i=o.indexOf(e);i!==-1?o.splice(i,1):o.push(e),this.value.set(o)}else t===e?this.value.set(void 0):this.value.set(e)}static \u0275fac=(()=>{let e;return function(o){return(e||(e=v(n)))(o||n)}})();static \u0275cmp=C({type:n,selectors:[["p-accordion"]],hostVars:2,hostBindings:function(t,o){t&1&&R("keydown",function(d){return o.onKeydown(d)}),t&2&&u(o.cn(o.cx("root"),o.styleClass))},inputs:{value:[1,"value"],multiple:[1,"multiple"],styleClass:"styleClass",expandIcon:"expandIcon",collapseIcon:"collapseIcon",selectOnFocus:[1,"selectOnFocus"],transitionOptions:"transitionOptions"},outputs:{value:"valueChange",onClose:"onClose",onOpen:"onOpen"},features:[H([f,{provide:Ae,useExisting:n},{provide:T,useExisting:n}]),E([c]),D],ngContentSelectors:O,decls:1,vars:0,template:function(t,o){t&1&&(w(),I(0))},dependencies:[N,se,B],encapsulation:2,changeDetection:0})}return n})();export{_e as a,pn as b,un as c,W as d};
