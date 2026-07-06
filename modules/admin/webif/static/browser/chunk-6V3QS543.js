import{b as ce}from"./chunk-FQUEGOUU.js";import{c as ne,d as z,f as M,h as B}from"./chunk-4O3FVBGX.js";import{Ia as te,Ja as oe,Ma as se,Pa as ie,Qa as ae,Ra as C,Ya as re,k as W,m as X,o as Z,s as ee}from"./chunk-PN5D6VAD.js";import{$b as x,Ab as l,Fb as o,Fc as U,Gb as u,Hb as f,Ib as _,Ob as y,Pb as L,Ra as N,Tb as V,Ua as c,Uc as k,Vb as s,Wb as H,Xb as q,Yb as b,Z as E,Za as Q,_b as h,aa as O,ca as v,cc as G,gc as g,hc as $,ia as S,ib as R,ic as Y,ja as A,ka as D,mb as j,nb as P,ob as d,qa as F,sc as J,uc as I,va as T,vc as K,wb as w,zb as r}from"./chunk-HJNL6B4D.js";var le=`
    .p-message {
        border-radius: dt('message.border.radius');
        outline-width: dt('message.border.width');
        outline-style: solid;
    }

    .p-message-content {
        display: flex;
        align-items: center;
        padding: dt('message.content.padding');
        gap: dt('message.content.gap');
        height: 100%;
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

    .p-message-enter-from {
        opacity: 0;
    }

    .p-message-enter-active {
        transition: opacity 0.3s;
    }

    .p-message.p-message-leave-from {
        max-height: 1000px;
    }

    .p-message.p-message-leave-to {
        max-height: 0;
        opacity: 0;
        margin: 0;
    }

    .p-message-leave-active {
        overflow: hidden;
        transition:
            max-height 0.45s cubic-bezier(0, 1, 0, 1),
            opacity 0.3s,
            margin 0.3s;
    }

    .p-message-leave-active .p-message-close-button {
        opacity: 0;
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
`;var ge=["container"],pe=["icon"],ue=["closeicon"],fe=["*"],_e=(n,t)=>({showTransitionParams:n,hideTransitionParams:t}),be=n=>({value:"visible()",params:n}),he=n=>({closeCallback:n});function xe(n,t){n&1&&y(0)}function Ce(n,t){if(n&1&&d(0,xe,1,0,"ng-container",4),n&2){let e=s(2);o("ngTemplateOutlet",e.iconTemplate||e._iconTemplate)}}function ve(n,t){if(n&1&&_(0,"i",2),n&2){let e=s(2);g(e.cn(e.cx("icon"),e.icon)),o("pBind",e.ptm("icon"))}}function ye(n,t){n&1&&y(0)}function Te(n,t){if(n&1&&d(0,ye,1,0,"ng-container",5),n&2){let e=s(2);o("ngTemplateOutlet",e.containerTemplate||e._containerTemplate)("ngTemplateOutletContext",I(2,he,e.closeCallback))}}function we(n,t){if(n&1&&_(0,"span",9),n&2){let e=s(4);o("pBind",e.ptm("text"))("ngClass",e.cx("text"))("innerHTML",e.text,N)}}function Ie(n,t){if(n&1&&(u(0,"div"),d(1,we,1,3,"span",8),f()),n&2){let e=s(3);c(),o("ngIf",!e.escape)}}function ke(n,t){if(n&1&&(u(0,"span",7),$(1),f()),n&2){let e=s(4);o("pBind",e.ptm("text"))("ngClass",e.cx("text")),c(),Y(e.text)}}function ze(n,t){if(n&1&&d(0,ke,2,3,"span",10),n&2){let e=s(3);o("ngIf",e.escape&&e.text)}}function Me(n,t){if(n&1&&(d(0,Ie,2,1,"div",6)(1,ze,1,1,"ng-template",null,0,U),u(3,"span",7),q(4),f()),n&2){let e=G(2),i=s(2);o("ngIf",!i.escape)("ngIfElse",e),c(3),o("pBind",i.ptm("text"))("ngClass",i.cx("text"))}}function Be(n,t){if(n&1&&_(0,"i",7),n&2){let e=s(3);g(e.cn(e.cx("closeIcon"),e.closeIcon)),o("pBind",e.ptm("closeIcon"))("ngClass",e.closeIcon)}}function Ee(n,t){n&1&&y(0)}function Oe(n,t){if(n&1&&d(0,Ee,1,0,"ng-container",4),n&2){let e=s(3);o("ngTemplateOutlet",e.closeIconTemplate||e._closeIconTemplate)}}function Se(n,t){if(n&1&&(D(),_(0,"svg",14)),n&2){let e=s(3);g(e.cx("closeIcon")),o("pBind",e.ptm("closeIcon"))}}function Ae(n,t){if(n&1){let e=L();u(0,"button",11),V("click",function(a){S(e);let p=s(2);return A(p.close(a))}),r(1,Be,1,4,"i",12),r(2,Oe,1,1,"ng-container"),r(3,Se,1,3,":svg:svg",13),f()}if(n&2){let e=s(2);g(e.cx("closeButton")),o("pBind",e.ptm("closeButton")),w("aria-label",e.closeAriaLabel),c(),l(e.closeIcon?1:-1),c(),l(e.closeIconTemplate||e._closeIconTemplate?2:-1),c(),l(!e.closeIconTemplate&&!e._closeIconTemplate&&!e.closeIcon?3:-1)}}function De(n,t){if(n&1&&(u(0,"div",2)(1,"div",2),r(2,Ce,1,1,"ng-container"),r(3,ve,1,3,"i",1),r(4,Te,1,4,"ng-container")(5,Me,5,4),r(6,Ae,4,7,"button",3),f()()),n&2){let e=s();g(e.cn(e.cx("root"),e.styleClass)),o("pBind",e.ptm("root"))("@messageAnimation",I(16,be,K(13,_e,e.showTransitionOptions,e.hideTransitionOptions))),w("aria-live","polite")("role","alert"),c(),g(e.cx("content")),o("pBind",e.ptm("content")),c(),l(e.iconTemplate||e._iconTemplate?2:-1),c(),l(e.icon?3:-1),c(),l(e.containerTemplate||e._containerTemplate?4:5),c(2),l(e.closable?6:-1)}}var Fe={root:({instance:n})=>["p-message p-component p-message-"+n.severity,"p-message-"+n.variant,{"p-message-sm":n.size==="small","p-message-lg":n.size==="large"}],content:"p-message-content",icon:"p-message-icon",text:"p-message-text",closeButton:"p-message-close-button",closeIcon:"p-message-close-icon"},me=(()=>{class n extends se{name="message";style=le;classes=Fe;static \u0275fac=(()=>{let e;return function(a){return(e||(e=T(n)))(a||n)}})();static \u0275prov=E({token:n,factory:n.\u0275fac})}return n})();var de=new O("MESSAGE_INSTANCE"),rn=(()=>{class n extends ae{_componentStyle=v(me);bindDirectiveInstance=v(C,{self:!0});$pcMessage=v(de,{optional:!0,skipSelf:!0})??void 0;onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptm("host"))}severity="info";text;escape=!0;style;styleClass;closable=!1;icon;closeIcon;life;showTransitionOptions="300ms ease-out";hideTransitionOptions="200ms cubic-bezier(0.86, 0, 0.07, 1)";size;variant;onClose=new Q;get closeAriaLabel(){return this.config.translation.aria?this.config.translation.aria.close:void 0}visible=F(!0);containerTemplate;iconTemplate;closeIconTemplate;templates;_containerTemplate;_iconTemplate;_closeIconTemplate;closeCallback=e=>{this.close(e)};onInit(){this.life&&setTimeout(()=>{this.visible.set(!1)},this.life)}onAfterContentInit(){this.templates?.forEach(e=>{switch(e.getType()){case"container":this._containerTemplate=e.template;break;case"icon":this._iconTemplate=e.template;break;case"closeicon":this._closeIconTemplate=e.template;break}})}close(e){this.visible.set(!1),this.onClose.emit({originalEvent:e})}static \u0275fac=(()=>{let e;return function(a){return(e||(e=T(n)))(a||n)}})();static \u0275cmp=R({type:n,selectors:[["p-message"]],contentQueries:function(i,a,p){if(i&1&&(b(p,ge,4),b(p,pe,4),b(p,ue,4),b(p,te,4)),i&2){let m;h(m=x())&&(a.containerTemplate=m.first),h(m=x())&&(a.iconTemplate=m.first),h(m=x())&&(a.closeIconTemplate=m.first),h(m=x())&&(a.templates=m)}},inputs:{severity:"severity",text:"text",escape:[2,"escape","escape",k],style:"style",styleClass:"styleClass",closable:[2,"closable","closable",k],icon:"icon",closeIcon:"closeIcon",life:"life",showTransitionOptions:"showTransitionOptions",hideTransitionOptions:"hideTransitionOptions",size:"size",variant:"variant"},outputs:{onClose:"onClose"},features:[J([me,{provide:de,useExisting:n},{provide:ie,useExisting:n}]),P([C]),j],ngContentSelectors:fe,decls:1,vars:1,consts:[["escapeOut",""],[3,"pBind","class"],[3,"pBind"],["pRipple","","type","button",3,"pBind","class"],[4,"ngTemplateOutlet"],[4,"ngTemplateOutlet","ngTemplateOutletContext"],[4,"ngIf","ngIfElse"],[3,"pBind","ngClass"],[3,"pBind","ngClass","innerHTML",4,"ngIf"],[3,"pBind","ngClass","innerHTML"],[3,"pBind","ngClass",4,"ngIf"],["pRipple","","type","button",3,"click","pBind"],[3,"pBind","class","ngClass"],["data-p-icon","times",3,"pBind","class"],["data-p-icon","times",3,"pBind"]],template:function(i,a){i&1&&(H(),r(0,De,7,18,"div",1)),i&2&&l(a.visible()?0:-1)},dependencies:[ee,W,X,Z,ce,re,oe,C],encapsulation:2,data:{animation:[ne("messageAnimation",[B(":enter",[M({opacity:0,transform:"translateY(-25%)"}),z("{{showTransitionParams}}")]),B(":leave",[z("{{hideTransitionParams}}",M({height:0,marginTop:0,marginBottom:0,marginLeft:0,marginRight:0,opacity:0}))])])]},changeDetection:0})}return n})();export{rn as a};
