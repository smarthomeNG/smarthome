import{b as re,e as le}from"./chunk-4IPD53LF.js";import{V as ie,X as ae,Y as ce,Z as x,aa as de}from"./chunk-JGSTUQPT.js";import{ga as se,ha as oe,n as Z,p as ee,r as ne,v as te}from"./chunk-XAETJXNU.js";import{$b as v,Ab as p,Fb as o,Gb as f,Gc as U,Hb as b,Ib as h,Lc as X,Ob as w,Pb as R,Pc as Y,Sa as D,Tb as H,V as k,Vb as a,Wa as c,Wb as Q,Xb as V,Y as I,Yb as L,Yc as M,_ as y,_b as _,a as C,dc as q,ea as z,fa as B,fc as G,ga as E,hc as g,ib as N,ic as W,jc as $,la as O,mb as P,nb as A,ob as u,pa as S,tc as J,ua as T,vc as K,wb as r,xb as F,yb as j,zb as m}from"./chunk-BDB7QD2D.js";var me=`
    .p-message {
        display: grid;
        grid-template-rows: 1fr;
        border-radius: dt('message.border.radius');
        outline-width: dt('message.border.width');
        outline-style: solid;
    }

    .p-message-content-wrapper {
        min-height: 0;
    }

    .p-message-content {
        display: flex;
        align-items: center;
        padding: dt('message.content.padding');
        gap: dt('message.content.gap');
    }

    .p-message-icon {
        flex-shrink: 0;
    }

    .p-message-close-button {
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        margin-inline-start: auto;
        overflow: hidden;
        position: relative;
        width: dt('message.close.button.width');
        height: dt('message.close.button.height');
        border-radius: dt('message.close.button.border.radius');
        background: transparent;
        transition:
            background dt('message.transition.duration'),
            color dt('message.transition.duration'),
            outline-color dt('message.transition.duration'),
            box-shadow dt('message.transition.duration'),
            opacity 0.3s;
        outline-color: transparent;
        color: inherit;
        padding: 0;
        border: none;
        cursor: pointer;
        user-select: none;
    }

    .p-message-close-icon {
        font-size: dt('message.close.icon.size');
        width: dt('message.close.icon.size');
        height: dt('message.close.icon.size');
    }

    .p-message-close-button:focus-visible {
        outline-width: dt('message.close.button.focus.ring.width');
        outline-style: dt('message.close.button.focus.ring.style');
        outline-offset: dt('message.close.button.focus.ring.offset');
    }

    .p-message-info {
        background: dt('message.info.background');
        outline-color: dt('message.info.border.color');
        color: dt('message.info.color');
        box-shadow: dt('message.info.shadow');
    }

    .p-message-info .p-message-close-button:focus-visible {
        outline-color: dt('message.info.close.button.focus.ring.color');
        box-shadow: dt('message.info.close.button.focus.ring.shadow');
    }

    .p-message-info .p-message-close-button:hover {
        background: dt('message.info.close.button.hover.background');
    }

    .p-message-info.p-message-outlined {
        color: dt('message.info.outlined.color');
        outline-color: dt('message.info.outlined.border.color');
    }

    .p-message-info.p-message-simple {
        color: dt('message.info.simple.color');
    }

    .p-message-success {
        background: dt('message.success.background');
        outline-color: dt('message.success.border.color');
        color: dt('message.success.color');
        box-shadow: dt('message.success.shadow');
    }

    .p-message-success .p-message-close-button:focus-visible {
        outline-color: dt('message.success.close.button.focus.ring.color');
        box-shadow: dt('message.success.close.button.focus.ring.shadow');
    }

    .p-message-success .p-message-close-button:hover {
        background: dt('message.success.close.button.hover.background');
    }

    .p-message-success.p-message-outlined {
        color: dt('message.success.outlined.color');
        outline-color: dt('message.success.outlined.border.color');
    }

    .p-message-success.p-message-simple {
        color: dt('message.success.simple.color');
    }

    .p-message-warn {
        background: dt('message.warn.background');
        outline-color: dt('message.warn.border.color');
        color: dt('message.warn.color');
        box-shadow: dt('message.warn.shadow');
    }

    .p-message-warn .p-message-close-button:focus-visible {
        outline-color: dt('message.warn.close.button.focus.ring.color');
        box-shadow: dt('message.warn.close.button.focus.ring.shadow');
    }

    .p-message-warn .p-message-close-button:hover {
        background: dt('message.warn.close.button.hover.background');
    }

    .p-message-warn.p-message-outlined {
        color: dt('message.warn.outlined.color');
        outline-color: dt('message.warn.outlined.border.color');
    }

    .p-message-warn.p-message-simple {
        color: dt('message.warn.simple.color');
    }

    .p-message-error {
        background: dt('message.error.background');
        outline-color: dt('message.error.border.color');
        color: dt('message.error.color');
        box-shadow: dt('message.error.shadow');
    }

    .p-message-error .p-message-close-button:focus-visible {
        outline-color: dt('message.error.close.button.focus.ring.color');
        box-shadow: dt('message.error.close.button.focus.ring.shadow');
    }

    .p-message-error .p-message-close-button:hover {
        background: dt('message.error.close.button.hover.background');
    }

    .p-message-error.p-message-outlined {
        color: dt('message.error.outlined.color');
        outline-color: dt('message.error.outlined.border.color');
    }

    .p-message-error.p-message-simple {
        color: dt('message.error.simple.color');
    }

    .p-message-secondary {
        background: dt('message.secondary.background');
        outline-color: dt('message.secondary.border.color');
        color: dt('message.secondary.color');
        box-shadow: dt('message.secondary.shadow');
    }

    .p-message-secondary .p-message-close-button:focus-visible {
        outline-color: dt('message.secondary.close.button.focus.ring.color');
        box-shadow: dt('message.secondary.close.button.focus.ring.shadow');
    }

    .p-message-secondary .p-message-close-button:hover {
        background: dt('message.secondary.close.button.hover.background');
    }

    .p-message-secondary.p-message-outlined {
        color: dt('message.secondary.outlined.color');
        outline-color: dt('message.secondary.outlined.border.color');
    }

    .p-message-secondary.p-message-simple {
        color: dt('message.secondary.simple.color');
    }

    .p-message-contrast {
        background: dt('message.contrast.background');
        outline-color: dt('message.contrast.border.color');
        color: dt('message.contrast.color');
        box-shadow: dt('message.contrast.shadow');
    }

    .p-message-contrast .p-message-close-button:focus-visible {
        outline-color: dt('message.contrast.close.button.focus.ring.color');
        box-shadow: dt('message.contrast.close.button.focus.ring.shadow');
    }

    .p-message-contrast .p-message-close-button:hover {
        background: dt('message.contrast.close.button.hover.background');
    }

    .p-message-contrast.p-message-outlined {
        color: dt('message.contrast.outlined.color');
        outline-color: dt('message.contrast.outlined.border.color');
    }

    .p-message-contrast.p-message-simple {
        color: dt('message.contrast.simple.color');
    }

    .p-message-text {
        font-size: dt('message.text.font.size');
        font-weight: dt('message.text.font.weight');
    }

    .p-message-icon {
        font-size: dt('message.icon.size');
        width: dt('message.icon.size');
        height: dt('message.icon.size');
    }

    .p-message-sm .p-message-content {
        padding: dt('message.content.sm.padding');
    }

    .p-message-sm .p-message-text {
        font-size: dt('message.text.sm.font.size');
    }

    .p-message-sm .p-message-icon {
        font-size: dt('message.icon.sm.size');
        width: dt('message.icon.sm.size');
        height: dt('message.icon.sm.size');
    }

    .p-message-sm .p-message-close-icon {
        font-size: dt('message.close.icon.sm.size');
        width: dt('message.close.icon.sm.size');
        height: dt('message.close.icon.sm.size');
    }

    .p-message-lg .p-message-content {
        padding: dt('message.content.lg.padding');
    }

    .p-message-lg .p-message-text {
        font-size: dt('message.text.lg.font.size');
    }

    .p-message-lg .p-message-icon {
        font-size: dt('message.icon.lg.size');
        width: dt('message.icon.lg.size');
        height: dt('message.icon.lg.size');
    }

    .p-message-lg .p-message-close-icon {
        font-size: dt('message.close.icon.lg.size');
        width: dt('message.close.icon.lg.size');
        height: dt('message.close.icon.lg.size');
    }

    .p-message-outlined {
        background: transparent;
        outline-width: dt('message.outlined.border.width');
    }

    .p-message-simple {
        background: transparent;
        outline-color: transparent;
        box-shadow: none;
    }

    .p-message-simple .p-message-content {
        padding: dt('message.simple.content.padding');
    }

    .p-message-outlined .p-message-close-button:hover,
    .p-message-simple .p-message-close-button:hover {
        background: transparent;
    }

    .p-message-enter-active {
        animation: p-animate-message-enter 0.3s ease-out forwards;
        overflow: hidden;
    }

    .p-message-leave-active {
        animation: p-animate-message-leave 0.15s ease-in forwards;
        overflow: hidden;
    }

    @keyframes p-animate-message-enter {
        from {
            opacity: 0;
            grid-template-rows: 0fr;
        }
        to {
            opacity: 1;
            grid-template-rows: 1fr;
        }
    }

    @keyframes p-animate-message-leave {
        from {
            opacity: 1;
            grid-template-rows: 1fr;
        }
        to {
            opacity: 0;
            margin: 0;
            grid-template-rows: 0fr;
        }
    }
`;var ue=["container"],fe=["icon"],be=["closeicon"],he=["*"],_e=n=>({closeCallback:n});function ve(n,i){n&1&&w(0)}function xe(n,i){if(n&1&&u(0,ve,1,0,"ng-container",4),n&2){let e=a();o("ngTemplateOutlet",e.iconTemplate||e._iconTemplate)}}function ye(n,i){if(n&1&&h(0,"i",1),n&2){let e=a();g(e.cn(e.cx("icon"),e.icon)),o("pBind",e.ptm("icon")),r("data-p",e.dataP)}}function we(n,i){n&1&&w(0)}function Ce(n,i){if(n&1&&u(0,we,1,0,"ng-container",5),n&2){let e=a();o("ngTemplateOutlet",e.containerTemplate||e._containerTemplate)("ngTemplateOutletContext",K(2,_e,e.closeCallback))}}function Te(n,i){if(n&1&&h(0,"span",9),n&2){let e=a(3);o("pBind",e.ptm("text"))("ngClass",e.cx("text"))("innerHTML",e.text,D),r("data-p",e.dataP)}}function Me(n,i){if(n&1&&(f(0,"div"),u(1,Te,1,4,"span",8),b()),n&2){let e=a(2);c(),o("ngIf",!e.escape)}}function ke(n,i){if(n&1&&(f(0,"span",7),W(1),b()),n&2){let e=a(3);o("pBind",e.ptm("text"))("ngClass",e.cx("text")),r("data-p",e.dataP),c(),$(e.text)}}function Ie(n,i){if(n&1&&u(0,ke,2,4,"span",10),n&2){let e=a(2);o("ngIf",e.escape&&e.text)}}function ze(n,i){if(n&1&&(u(0,Me,2,1,"div",6)(1,Ie,1,1,"ng-template",null,0,U),f(3,"span",7),V(4),b()),n&2){let e=q(2),s=a();o("ngIf",!s.escape)("ngIfElse",e),c(3),o("pBind",s.ptm("text"))("ngClass",s.cx("text")),r("data-p",s.dataP)}}function Be(n,i){if(n&1&&h(0,"i",7),n&2){let e=a(2);g(e.cn(e.cx("closeIcon"),e.closeIcon)),o("pBind",e.ptm("closeIcon"))("ngClass",e.closeIcon),r("data-p",e.dataP)}}function Ee(n,i){n&1&&w(0)}function Oe(n,i){if(n&1&&u(0,Ee,1,0,"ng-container",4),n&2){let e=a(2);o("ngTemplateOutlet",e.closeIconTemplate||e._closeIconTemplate)}}function Se(n,i){if(n&1&&(E(),h(0,"svg",14)),n&2){let e=a(2);g(e.cx("closeIcon")),o("pBind",e.ptm("closeIcon")),r("data-p",e.dataP)}}function De(n,i){if(n&1){let e=R();f(0,"button",11),H("click",function(t){z(e);let l=a();return B(l.close(t))}),m(1,Be,1,5,"i",12),m(2,Oe,1,1,"ng-container"),m(3,Se,1,4,":svg:svg",13),b()}if(n&2){let e=a();g(e.cx("closeButton")),o("pBind",e.ptm("closeButton")),r("aria-label",e.closeAriaLabel)("data-p",e.dataP),c(),p(e.closeIcon?1:-1),c(),p(e.closeIconTemplate||e._closeIconTemplate?2:-1),c(),p(!e.closeIconTemplate&&!e._closeIconTemplate&&!e.closeIcon?3:-1)}}var Ne={root:({instance:n})=>["p-message p-component p-message-"+n.severity,n.variant&&"p-message-"+n.variant,{"p-message-sm":n.size==="small","p-message-lg":n.size==="large"}],contentWrapper:"p-message-content-wrapper",content:"p-message-content",icon:"p-message-icon",text:"p-message-text",closeButton:"p-message-close-button",closeIcon:"p-message-close-icon"},pe=(()=>{class n extends ie{name="message";style=me;classes=Ne;static \u0275fac=(()=>{let e;return function(t){return(e||(e=T(n)))(t||n)}})();static \u0275prov=k({token:n,factory:n.\u0275fac})}return n})();var ge=new I("MESSAGE_INSTANCE"),cn=(()=>{class n extends ce{componentName="Message";_componentStyle=y(pe);bindDirectiveInstance=y(x,{self:!0});$pcMessage=y(ge,{optional:!0,skipSelf:!0})??void 0;onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptms(["host","root"]))}severity="info";text;escape=!0;style;styleClass;closable=!1;icon;closeIcon;life;showTransitionOptions="300ms ease-out";hideTransitionOptions="200ms cubic-bezier(0.86, 0, 0.07, 1)";size;variant;motionOptions=Y(void 0);computedMotionOptions=X(()=>C(C({},this.ptm("motion")),this.motionOptions()));onClose=new O;get closeAriaLabel(){return this.config.translation.aria?this.config.translation.aria.close:void 0}visible=S(!0);containerTemplate;iconTemplate;closeIconTemplate;templates;_containerTemplate;_iconTemplate;_closeIconTemplate;closeCallback=e=>{this.close(e)};onInit(){this.life&&setTimeout(()=>{this.visible.set(!1)},this.life)}onAfterContentInit(){this.templates?.forEach(e=>{switch(e.getType()){case"container":this._containerTemplate=e.template;break;case"icon":this._iconTemplate=e.template;break;case"closeicon":this._closeIconTemplate=e.template;break}})}close(e){this.visible.set(!1),this.onClose.emit({originalEvent:e})}get dataP(){return this.cn({outlined:this.variant==="outlined",simple:this.variant==="simple",[this.severity]:this.severity,[this.size]:this.size})}static \u0275fac=(()=>{let e;return function(t){return(e||(e=T(n)))(t||n)}})();static \u0275cmp=N({type:n,selectors:[["p-message"]],contentQueries:function(s,t,l){if(s&1&&L(l,ue,4)(l,fe,4)(l,be,4)(l,se,4),s&2){let d;_(d=v())&&(t.containerTemplate=d.first),_(d=v())&&(t.iconTemplate=d.first),_(d=v())&&(t.closeIconTemplate=d.first),_(d=v())&&(t.templates=d)}},hostAttrs:["role","alert","aria-live","polite"],hostVars:5,hostBindings:function(s,t){s&1&&(F(function(){return"p-message-enter-active"}),j(function(){return"p-message-leave-active"})),s&2&&(r("data-p",t.dataP),g(t.cn(t.cx("root"),t.styleClass)),G("p-message-leave-active",!t.visible()))},inputs:{severity:"severity",text:"text",escape:[2,"escape","escape",M],style:"style",styleClass:"styleClass",closable:[2,"closable","closable",M],icon:"icon",closeIcon:"closeIcon",life:"life",showTransitionOptions:"showTransitionOptions",hideTransitionOptions:"hideTransitionOptions",size:"size",variant:"variant",motionOptions:[1,"motionOptions"]},outputs:{onClose:"onClose"},features:[J([pe,{provide:ge,useExisting:n},{provide:ae,useExisting:n}]),P([x]),A],ngContentSelectors:he,decls:7,vars:12,consts:[["escapeOut",""],[3,"pBind"],[3,"pBind","class"],["pRipple","","type","button",3,"pBind","class"],[4,"ngTemplateOutlet"],[4,"ngTemplateOutlet","ngTemplateOutletContext"],[4,"ngIf","ngIfElse"],[3,"pBind","ngClass"],[3,"pBind","ngClass","innerHTML",4,"ngIf"],[3,"pBind","ngClass","innerHTML"],[3,"pBind","ngClass",4,"ngIf"],["pRipple","","type","button",3,"click","pBind"],[3,"pBind","class","ngClass"],["data-p-icon","times",3,"pBind","class"],["data-p-icon","times",3,"pBind"]],template:function(s,t){s&1&&(Q(),f(0,"div",1)(1,"div",1),m(2,xe,1,1,"ng-container"),m(3,ye,1,4,"i",2),m(4,Ce,1,4,"ng-container")(5,ze,5,5),m(6,De,4,8,"button",3),b()()),s&2&&(g(t.cx("contentWrapper")),o("pBind",t.ptm("contentWrapper")),r("data-p",t.dataP),c(),g(t.cx("content")),o("pBind",t.ptm("content")),r("data-p",t.dataP),c(),p(t.iconTemplate||t._iconTemplate?2:-1),c(),p(t.icon?3:-1),c(),p(t.containerTemplate||t._containerTemplate?4:5),c(2),p(t.closable?6:-1))},dependencies:[te,Z,ee,ne,re,de,oe,x,le],encapsulation:2,changeDetection:0})}return n})();export{cn as a};
