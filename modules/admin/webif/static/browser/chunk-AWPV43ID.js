import{C as de}from"./chunk-XMFB5O6P.js";import{Kc as wn,Oc as nn,Pb as fe,Ra as re,Sc as k,U as yn,Vb as le,Wb as ue,Z as _,a as ee,b as te,gc as ce,ha as ae,hb as xn,jb as oe,ra as ie,vb as se}from"./chunk-25ZXD53X.js";function Cn(n,t){(t==null||t>n.length)&&(t=n.length);for(var e=0,a=Array(t);e<t;e++)a[e]=n[e];return a}function oa(n){if(Array.isArray(n))return n}function sa(n){if(Array.isArray(n))return Cn(n)}function fa(n,t){if(!(n instanceof t))throw new TypeError("Cannot call a class as a function")}function me(n,t){for(var e=0;e<t.length;e++){var a=t[e];a.enumerable=a.enumerable||!1,a.configurable=!0,"value"in a&&(a.writable=!0),Object.defineProperty(n,Xe(a.key),a)}}function la(n,t,e){return t&&me(n.prototype,t),e&&me(n,e),Object.defineProperty(n,"prototype",{writable:!1}),n}function on(n,t){var e=typeof Symbol<"u"&&n[Symbol.iterator]||n["@@iterator"];if(!e){if(Array.isArray(n)||(e=Hn(n))||t&&n&&typeof n.length=="number"){e&&(n=e);var a=0,i=function(){};return{s:i,n:function(){return a>=n.length?{done:!0}:{done:!1,value:n[a++]}},e:function(f){throw f},f:i}}throw new TypeError(`Invalid attempt to iterate non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}var r,o=!0,s=!1;return{s:function(){e=e.call(n)},n:function(){var f=e.next();return o=f.done,f},e:function(f){s=!0,r=f},f:function(){try{o||e.return==null||e.return()}finally{if(s)throw r}}}}function g(n,t,e){return(t=Xe(t))in n?Object.defineProperty(n,t,{value:e,enumerable:!0,configurable:!0,writable:!0}):n[t]=e,n}function ua(n){if(typeof Symbol<"u"&&n[Symbol.iterator]!=null||n["@@iterator"]!=null)return Array.from(n)}function ca(n,t){var e=n==null?null:typeof Symbol<"u"&&n[Symbol.iterator]||n["@@iterator"];if(e!=null){var a,i,r,o,s=[],f=!0,u=!1;try{if(r=(e=e.call(n)).next,t===0){if(Object(e)!==e)return;f=!1}else for(;!(f=(a=r.call(e)).done)&&(s.push(a.value),s.length!==t);f=!0);}catch(d){u=!0,i=d}finally{try{if(!f&&e.return!=null&&(o=e.return(),Object(o)!==o))return}finally{if(u)throw i}}return s}}function da(){throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}function ma(){throw new TypeError(`Invalid attempt to spread non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}function ge(n,t){var e=Object.keys(n);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(n);t&&(a=a.filter(function(i){return Object.getOwnPropertyDescriptor(n,i).enumerable})),e.push.apply(e,a)}return e}function l(n){for(var t=1;t<arguments.length;t++){var e=arguments[t]!=null?arguments[t]:{};t%2?ge(Object(e),!0).forEach(function(a){g(n,a,e[a])}):Object.getOwnPropertyDescriptors?Object.defineProperties(n,Object.getOwnPropertyDescriptors(e)):ge(Object(e)).forEach(function(a){Object.defineProperty(n,a,Object.getOwnPropertyDescriptor(e,a))})}return n}function dn(n,t){return oa(n)||ca(n,t)||Hn(n,t)||da()}function P(n){return sa(n)||ua(n)||Hn(n)||ma()}function ga(n,t){if(typeof n!="object"||!n)return n;var e=n[Symbol.toPrimitive];if(e!==void 0){var a=e.call(n,t||"default");if(typeof a!="object")return a;throw new TypeError("@@toPrimitive must return a primitive value.")}return(t==="string"?String:Number)(n)}function Xe(n){var t=ga(n,"string");return typeof t=="symbol"?t:t+""}function ln(n){"@babel/helpers - typeof";return ln=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(t){return typeof t}:function(t){return t&&typeof Symbol=="function"&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},ln(n)}function Hn(n,t){if(n){if(typeof n=="string")return Cn(n,t);var e={}.toString.call(n).slice(8,-1);return e==="Object"&&n.constructor&&(e=n.constructor.name),e==="Map"||e==="Set"?Array.from(n):e==="Arguments"||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(e)?Cn(n,t):void 0}}var pe=function(){},Un={},Ve={},Be=null,Ge={mark:pe,measure:pe};try{typeof window<"u"&&(Un=window),typeof document<"u"&&(Ve=document),typeof MutationObserver<"u"&&(Be=MutationObserver),typeof performance<"u"&&(Ge=performance)}catch(n){}var pa=Un.navigator||{},ve=pa.userAgent,he=ve===void 0?"":ve,j=Un,h=Ve,be=Be,en=Ge,Jo=!!j.document,M=!!h.documentElement&&!!h.head&&typeof h.addEventListener=="function"&&typeof h.createElement=="function",qe=~he.indexOf("MSIE")||~he.indexOf("Trident/"),tn,va=/fa(k|kd|s|r|l|t|d|dr|dl|dt|b|slr|slpr|wsb|tl|ns|nds|es|gt|jr|jfr|jdr|usb|ufsb|udsb|cr|ss|sr|sl|st|sds|sdr|sdl|sdt|sldr|slpdr|pr|ms|vs)?[\-\ ]/,ha=/Font ?Awesome ?([567 ]*)(Solid|Regular|Light|Thin|Duotone|Brands|Free|Pro|Sharp Duotone|Sharp|Kit|Notdog Duo|Notdog|Chisel|Etch|Graphite|Thumbprint|Jelly Fill|Jelly Duo|Jelly|Utility|Utility Fill|Utility Duo|Slab Press|Slab|Slab Duo|Slab Press Duo|Pixel|Mosaic|Vellum|Whiteboard)?.*/i,Ke={classic:{fa:"solid",fas:"solid","fa-solid":"solid",far:"regular","fa-regular":"regular",fal:"light","fa-light":"light",fat:"thin","fa-thin":"thin",fab:"brands","fa-brands":"brands"},duotone:{fa:"solid",fad:"solid","fa-solid":"solid","fa-duotone":"solid",fadr:"regular","fa-regular":"regular",fadl:"light","fa-light":"light",fadt:"thin","fa-thin":"thin"},sharp:{fa:"solid",fass:"solid","fa-solid":"solid",fasr:"regular","fa-regular":"regular",fasl:"light","fa-light":"light",fast:"thin","fa-thin":"thin"},"sharp-duotone":{fa:"solid",fasds:"solid","fa-solid":"solid",fasdr:"regular","fa-regular":"regular",fasdl:"light","fa-light":"light",fasdt:"thin","fa-thin":"thin"},slab:{"fa-regular":"regular",faslr:"regular"},"slab-press":{"fa-regular":"regular",faslpr:"regular"},"slab-duo":{"fa-regular":"regular",fasldr:"regular"},"slab-press-duo":{"fa-regular":"regular",faslpdr:"regular"},thumbprint:{"fa-light":"light",fatl:"light"},vellum:{"fa-solid":"solid",favs:"solid"},pixel:{"fa-regular":"regular",fapr:"regular"},mosaic:{"fa-solid":"solid",fams:"solid"},whiteboard:{"fa-semibold":"semibold",fawsb:"semibold"},notdog:{"fa-solid":"solid",fans:"solid"},"notdog-duo":{"fa-solid":"solid",fands:"solid"},etch:{"fa-solid":"solid",faes:"solid"},graphite:{"fa-thin":"thin",fagt:"thin"},jelly:{"fa-regular":"regular",fajr:"regular"},"jelly-fill":{"fa-regular":"regular",fajfr:"regular"},"jelly-duo":{"fa-regular":"regular",fajdr:"regular"},chisel:{"fa-regular":"regular",facr:"regular"},utility:{"fa-semibold":"semibold",fausb:"semibold"},"utility-duo":{"fa-semibold":"semibold",faudsb:"semibold"},"utility-fill":{"fa-semibold":"semibold",faufsb:"semibold"}},ba={GROUP:"duotone-group",SWAP_OPACITY:"swap-opacity",PRIMARY:"primary",SECONDARY:"secondary"},Je=["fa-classic","fa-duotone","fa-sharp","fa-sharp-duotone","fa-thumbprint","fa-whiteboard","fa-notdog","fa-notdog-duo","fa-chisel","fa-etch","fa-graphite","fa-jelly","fa-jelly-fill","fa-jelly-duo","fa-slab","fa-slab-press","fa-slab-press-duo","fa-slab-duo","fa-mosaic","fa-pixel","fa-vellum","fa-utility","fa-utility-duo","fa-utility-fill"],w="classic",J="duotone",Qe="sharp",Ze="sharp-duotone",nt="chisel",et="etch",tt="graphite",at="jelly",it="jelly-duo",rt="jelly-fill",ot="mosaic",st="notdog",ft="notdog-duo",lt="pixel",ut="slab",ct="slab-duo",dt="slab-press",mt="slab-press-duo",gt="thumbprint",pt="utility",vt="utility-duo",ht="utility-fill",bt="vellum",yt="whiteboard",ya="Classic",xa="Duotone",wa="Sharp",Sa="Sharp Duotone",ka="Chisel",Aa="Etch",Ia="Graphite",za="Jelly",Ca="Jelly Duo",Pa="Jelly Fill",Fa="Mosaic",Na="Notdog",Ea="Notdog Duo",Da="Pixel",Ma="Slab",Oa="Slab Duo",ja="Slab Press",Ta="Slab Press Duo",$a="Thumbprint",_a="Utility",La="Utility Duo",Ra="Utility Fill",Wa="Vellum",Ha="Whiteboard",xt=[w,J,Qe,Ze,nt,et,tt,at,it,rt,ot,st,ft,lt,ut,ct,dt,mt,gt,pt,vt,ht,bt,yt],Qo=(tn={},g(g(g(g(g(g(g(g(g(g(tn,w,ya),J,xa),Qe,wa),Ze,Sa),nt,ka),et,Aa),tt,Ia),at,za),it,Ca),rt,Pa),g(g(g(g(g(g(g(g(g(g(tn,ot,Fa),st,Na),ft,Ea),lt,Da),ut,Ma),ct,Oa),dt,ja),mt,Ta),gt,$a),pt,_a),g(g(g(g(tn,vt,La),ht,Ra),bt,Wa),yt,Ha)),Ua={classic:{900:"fas",400:"far",normal:"far",300:"fal",100:"fat"},duotone:{900:"fad",400:"fadr",300:"fadl",100:"fadt"},sharp:{900:"fass",400:"fasr",300:"fasl",100:"fast"},"sharp-duotone":{900:"fasds",400:"fasdr",300:"fasdl",100:"fasdt"},slab:{400:"faslr"},"slab-press":{400:"faslpr"},"slab-duo":{400:"fasldr"},"slab-press-duo":{400:"faslpdr"},vellum:{900:"favs"},mosaic:{900:"fams"},pixel:{400:"fapr"},whiteboard:{600:"fawsb"},thumbprint:{300:"fatl"},notdog:{900:"fans"},"notdog-duo":{900:"fands"},etch:{900:"faes"},graphite:{100:"fagt"},chisel:{400:"facr"},jelly:{400:"fajr"},"jelly-fill":{400:"fajfr"},"jelly-duo":{400:"fajdr"},utility:{600:"fausb"},"utility-duo":{600:"faudsb"},"utility-fill":{600:"faufsb"}},Ya={"Font Awesome 7 Free":{900:"fas",400:"far"},"Font Awesome 7 Pro":{900:"fas",400:"far",normal:"far",300:"fal",100:"fat"},"Font Awesome 7 Brands":{400:"fab",normal:"fab"},"Font Awesome 7 Duotone":{900:"fad",400:"fadr",normal:"fadr",300:"fadl",100:"fadt"},"Font Awesome 7 Sharp":{900:"fass",400:"fasr",normal:"fasr",300:"fasl",100:"fast"},"Font Awesome 7 Sharp Duotone":{900:"fasds",400:"fasdr",normal:"fasdr",300:"fasdl",100:"fasdt"},"Font Awesome 7 Jelly":{400:"fajr",normal:"fajr"},"Font Awesome 7 Jelly Fill":{400:"fajfr",normal:"fajfr"},"Font Awesome 7 Jelly Duo":{400:"fajdr",normal:"fajdr"},"Font Awesome 7 Slab":{400:"faslr",normal:"faslr"},"Font Awesome 7 Slab Press":{400:"faslpr",normal:"faslpr"},"Font Awesome 7 Slab Duo":{400:"fasldr",normal:"fasldr"},"Font Awesome 7 Slab Press Duo":{400:"faslpdr",normal:"faslpdr"},"Font Awesome 7 Pixel":{400:"fapr",normal:"fapr"},"Font Awesome 7 Mosaic":{900:"fams",normal:"fams"},"Font Awesome 7 Vellum":{900:"favs",normal:"favs"},"Font Awesome 7 Thumbprint":{300:"fatl",normal:"fatl"},"Font Awesome 7 Notdog":{900:"fans",normal:"fans"},"Font Awesome 7 Notdog Duo":{900:"fands",normal:"fands"},"Font Awesome 7 Etch":{900:"faes",normal:"faes"},"Font Awesome 7 Graphite":{100:"fagt",normal:"fagt"},"Font Awesome 7 Chisel":{400:"facr",normal:"facr"},"Font Awesome 7 Whiteboard":{600:"fawsb",normal:"fawsb"},"Font Awesome 7 Utility":{600:"fausb",normal:"fausb"},"Font Awesome 7 Utility Duo":{600:"faudsb",normal:"faudsb"},"Font Awesome 7 Utility Fill":{600:"faufsb",normal:"faufsb"}},Xa=new Map([["classic",{defaultShortPrefixId:"fas",defaultStyleId:"solid",styleIds:["solid","regular","light","thin","brands"],futureStyleIds:[],defaultFontWeight:900}],["duotone",{defaultShortPrefixId:"fad",defaultStyleId:"solid",styleIds:["solid","regular","light","thin"],futureStyleIds:[],defaultFontWeight:900}],["sharp",{defaultShortPrefixId:"fass",defaultStyleId:"solid",styleIds:["solid","regular","light","thin"],futureStyleIds:[],defaultFontWeight:900}],["sharp-duotone",{defaultShortPrefixId:"fasds",defaultStyleId:"solid",styleIds:["solid","regular","light","thin"],futureStyleIds:[],defaultFontWeight:900}],["chisel",{defaultShortPrefixId:"facr",defaultStyleId:"regular",styleIds:["regular"],futureStyleIds:[],defaultFontWeight:400}],["etch",{defaultShortPrefixId:"faes",defaultStyleId:"solid",styleIds:["solid"],futureStyleIds:[],defaultFontWeight:900}],["graphite",{defaultShortPrefixId:"fagt",defaultStyleId:"thin",styleIds:["thin"],futureStyleIds:[],defaultFontWeight:100}],["jelly",{defaultShortPrefixId:"fajr",defaultStyleId:"regular",styleIds:["regular"],futureStyleIds:[],defaultFontWeight:400}],["jelly-duo",{defaultShortPrefixId:"fajdr",defaultStyleId:"regular",styleIds:["regular"],futureStyleIds:[],defaultFontWeight:400}],["jelly-fill",{defaultShortPrefixId:"fajfr",defaultStyleId:"regular",styleIds:["regular"],futureStyleIds:[],defaultFontWeight:400}],["mosaic",{defaultShortPrefixId:"fams",defaultStyleId:"solid",styleIds:["solid"],futureStyleIds:[],defaultFontWeight:900}],["notdog",{defaultShortPrefixId:"fans",defaultStyleId:"solid",styleIds:["solid"],futureStyleIds:[],defaultFontWeight:900}],["notdog-duo",{defaultShortPrefixId:"fands",defaultStyleId:"solid",styleIds:["solid"],futureStyleIds:[],defaultFontWeight:900}],["pixel",{defaultShortPrefixId:"fapr",defaultStyleId:"regular",styleIds:["regular"],futureStyleIds:[],defaultFontWeight:400}],["slab",{defaultShortPrefixId:"faslr",defaultStyleId:"regular",styleIds:["regular"],futureStyleIds:[],defaultFontWeight:400}],["slab-duo",{defaultShortPrefixId:"fasldr",defaultStyleId:"regular",styleIds:["regular"],futureStyleIds:[],defaultFontWeight:400}],["slab-press",{defaultShortPrefixId:"faslpr",defaultStyleId:"regular",styleIds:["regular"],futureStyleIds:[],defaultFontWeight:400}],["slab-press-duo",{defaultShortPrefixId:"faslpdr",defaultStyleId:"regular",styleIds:["regular"],futureStyleIds:[],defaultFontWeight:400}],["thumbprint",{defaultShortPrefixId:"fatl",defaultStyleId:"light",styleIds:["light"],futureStyleIds:[],defaultFontWeight:300}],["utility",{defaultShortPrefixId:"fausb",defaultStyleId:"semibold",styleIds:["semibold"],futureStyleIds:[],defaultFontWeight:600}],["utility-duo",{defaultShortPrefixId:"faudsb",defaultStyleId:"semibold",styleIds:["semibold"],futureStyleIds:[],defaultFontWeight:600}],["utility-fill",{defaultShortPrefixId:"faufsb",defaultStyleId:"semibold",styleIds:["semibold"],futureStyleIds:[],defaultFontWeight:600}],["vellum",{defaultShortPrefixId:"favs",defaultStyleId:"solid",styleIds:["solid"],futureStyleIds:[],defaultFontWeight:900}],["whiteboard",{defaultShortPrefixId:"fawsb",defaultStyleId:"semibold",styleIds:["semibold"],futureStyleIds:[],defaultFontWeight:600}]]),Va={chisel:{regular:"facr"},classic:{brands:"fab",light:"fal",regular:"far",solid:"fas",thin:"fat"},duotone:{light:"fadl",regular:"fadr",solid:"fad",thin:"fadt"},etch:{solid:"faes"},graphite:{thin:"fagt"},jelly:{regular:"fajr"},"jelly-duo":{regular:"fajdr"},"jelly-fill":{regular:"fajfr"},mosaic:{solid:"fams"},notdog:{solid:"fans"},"notdog-duo":{solid:"fands"},pixel:{regular:"fapr"},sharp:{light:"fasl",regular:"fasr",solid:"fass",thin:"fast"},"sharp-duotone":{light:"fasdl",regular:"fasdr",solid:"fasds",thin:"fasdt"},slab:{regular:"faslr"},"slab-duo":{regular:"fasldr"},"slab-press":{regular:"faslpr"},"slab-press-duo":{regular:"faslpdr"},thumbprint:{light:"fatl"},utility:{semibold:"fausb"},"utility-duo":{semibold:"faudsb"},"utility-fill":{semibold:"faufsb"},vellum:{solid:"favs"},whiteboard:{semibold:"fawsb"}},wt=["fak","fa-kit","fakd","fa-kit-duotone"],ye={kit:{fak:"kit","fa-kit":"kit"},"kit-duotone":{fakd:"kit-duotone","fa-kit-duotone":"kit-duotone"}},Ba=["kit"],Ga="kit",qa="kit-duotone",Ka="Kit",Ja="Kit Duotone",Zo=g(g({},Ga,Ka),qa,Ja),Qa={kit:{"fa-kit":"fak"},"kit-duotone":{"fa-kit-duotone":"fakd"}},Za={"Font Awesome Kit":{400:"fak",normal:"fak"},"Font Awesome Kit Duotone":{400:"fakd",normal:"fakd"}},ni={kit:{fak:"fa-kit"},"kit-duotone":{fakd:"fa-kit-duotone"}},xe={kit:{kit:"fak"},"kit-duotone":{"kit-duotone":"fakd"}},an,rn={GROUP:"duotone-group",SWAP_OPACITY:"swap-opacity",PRIMARY:"primary",SECONDARY:"secondary"},ei=["fa-classic","fa-duotone","fa-sharp","fa-sharp-duotone","fa-thumbprint","fa-whiteboard","fa-notdog","fa-notdog-duo","fa-chisel","fa-etch","fa-graphite","fa-jelly","fa-jelly-fill","fa-jelly-duo","fa-slab","fa-slab-press","fa-slab-press-duo","fa-slab-duo","fa-mosaic","fa-pixel","fa-vellum","fa-utility","fa-utility-duo","fa-utility-fill"],ti="classic",ai="duotone",ii="sharp",ri="sharp-duotone",oi="chisel",si="etch",fi="graphite",li="jelly",ui="jelly-duo",ci="jelly-fill",di="mosaic",mi="notdog",gi="notdog-duo",pi="pixel",vi="slab",hi="slab-duo",bi="slab-press",yi="slab-press-duo",xi="thumbprint",wi="utility",Si="utility-duo",ki="utility-fill",Ai="vellum",Ii="whiteboard",zi="Classic",Ci="Duotone",Pi="Sharp",Fi="Sharp Duotone",Ni="Chisel",Ei="Etch",Di="Graphite",Mi="Jelly",Oi="Jelly Duo",ji="Jelly Fill",Ti="Mosaic",$i="Notdog",_i="Notdog Duo",Li="Pixel",Ri="Slab",Wi="Slab Duo",Hi="Slab Press",Ui="Slab Press Duo",Yi="Thumbprint",Xi="Utility",Vi="Utility Duo",Bi="Utility Fill",Gi="Vellum",qi="Whiteboard",ns=(an={},g(g(g(g(g(g(g(g(g(g(an,ti,zi),ai,Ci),ii,Pi),ri,Fi),oi,Ni),si,Ei),fi,Di),li,Mi),ui,Oi),ci,ji),g(g(g(g(g(g(g(g(g(g(an,di,Ti),mi,$i),gi,_i),pi,Li),vi,Ri),hi,Wi),bi,Hi),yi,Ui),xi,Yi),wi,Xi),g(g(g(g(an,Si,Vi),ki,Bi),Ai,Gi),Ii,qi)),Ki="kit",Ji="kit-duotone",Qi="Kit",Zi="Kit Duotone",es=g(g({},Ki,Qi),Ji,Zi),nr={classic:{"fa-brands":"fab","fa-duotone":"fad","fa-light":"fal","fa-regular":"far","fa-solid":"fas","fa-thin":"fat"},duotone:{"fa-regular":"fadr","fa-light":"fadl","fa-thin":"fadt"},sharp:{"fa-solid":"fass","fa-regular":"fasr","fa-light":"fasl","fa-thin":"fast"},"sharp-duotone":{"fa-solid":"fasds","fa-regular":"fasdr","fa-light":"fasdl","fa-thin":"fasdt"},slab:{"fa-regular":"faslr"},"slab-press":{"fa-regular":"faslpr"},"slab-duo":{"fa-regular":"fasldr"},"slab-press-duo":{"fa-regular":"faslpdr"},pixel:{"fa-regular":"fapr"},mosaic:{"fa-solid":"fams"},vellum:{"fa-solid":"favs"},whiteboard:{"fa-semibold":"fawsb"},thumbprint:{"fa-light":"fatl"},notdog:{"fa-solid":"fans"},"notdog-duo":{"fa-solid":"fands"},etch:{"fa-solid":"faes"},graphite:{"fa-thin":"fagt"},jelly:{"fa-regular":"fajr"},"jelly-fill":{"fa-regular":"fajfr"},"jelly-duo":{"fa-regular":"fajdr"},chisel:{"fa-regular":"facr"},utility:{"fa-semibold":"fausb"},"utility-duo":{"fa-semibold":"faudsb"},"utility-fill":{"fa-semibold":"faufsb"}},er={classic:["fas","far","fal","fat","fad"],duotone:["fadr","fadl","fadt"],sharp:["fass","fasr","fasl","fast"],"sharp-duotone":["fasds","fasdr","fasdl","fasdt"],slab:["faslr"],"slab-press":["faslpr"],"slab-duo":["fasldr"],"slab-press-duo":["faslpdr"],pixel:["fapr"],mosaic:["fams"],vellum:["favs"],whiteboard:["fawsb"],thumbprint:["fatl"],notdog:["fans"],"notdog-duo":["fands"],etch:["faes"],graphite:["fagt"],jelly:["fajr"],"jelly-fill":["fajfr"],"jelly-duo":["fajdr"],chisel:["facr"],utility:["fausb"],"utility-duo":["faudsb"],"utility-fill":["faufsb"]},Pn={classic:{fab:"fa-brands",fad:"fa-duotone",fal:"fa-light",far:"fa-regular",fas:"fa-solid",fat:"fa-thin"},duotone:{fadr:"fa-regular",fadl:"fa-light",fadt:"fa-thin"},sharp:{fass:"fa-solid",fasr:"fa-regular",fasl:"fa-light",fast:"fa-thin"},"sharp-duotone":{fasds:"fa-solid",fasdr:"fa-regular",fasdl:"fa-light",fasdt:"fa-thin"},slab:{faslr:"fa-regular"},"slab-press":{faslpr:"fa-regular"},"slab-duo":{fasldr:"fa-regular"},"slab-press-duo":{faslpdr:"fa-regular"},pixel:{fapr:"fa-regular"},mosaic:{fams:"fa-solid"},vellum:{favs:"fa-solid"},whiteboard:{fawsb:"fa-semibold"},thumbprint:{fatl:"fa-light"},notdog:{fans:"fa-solid"},"notdog-duo":{fands:"fa-solid"},etch:{faes:"fa-solid"},graphite:{fagt:"fa-thin"},jelly:{fajr:"fa-regular"},"jelly-fill":{fajfr:"fa-regular"},"jelly-duo":{fajdr:"fa-regular"},chisel:{facr:"fa-regular"},utility:{fausb:"fa-semibold"},"utility-duo":{faudsb:"fa-semibold"},"utility-fill":{faufsb:"fa-semibold"}},tr=["fa-solid","fa-regular","fa-light","fa-thin","fa-duotone","fa-brands","fa-semibold"],St=["fa","fas","far","fal","fat","fad","fadr","fadl","fadt","fab","fass","fasr","fasl","fast","fasds","fasdr","fasdl","fasdt","faslr","faslpr","fasldr","faslpdr","fapr","fams","favs","fawsb","fatl","fans","fands","faes","fagt","fajr","fajfr","fajdr","facr","fausb","faudsb","faufsb"].concat(ei,tr),ar=["solid","regular","light","thin","duotone","brands","semibold"],kt=[1,2,3,4,5,6,7,8,9,10],ir=kt.concat([11,12,13,14,15,16,17,18,19,20]),rr=["aw","fw","pull-left","pull-right"],or=[].concat(P(Object.keys(er)),ar,rr,["2xs","xs","sm","lg","xl","2xl","beat","beat-fade","border","bounce","buzz","canvas-square","canvas-roomy","fade","flip-360","flip-both","flip-horizontal","flip-vertical","flip","float","inverse","jello","layers","layers-bottom-left","layers-bottom-right","layers-counter","layers-text","layers-top-left","layers-top-right","li","pull-end","pull-start","pulse","rotate-180","rotate-270","rotate-90","rotate-by","shake","spin-pulse","spin-reverse","spin","spin-snap","spin-snap-4","spin-snap-8","stack-1x","stack-2x","stack","swing","ul","wag","width-auto","width-fixed",rn.GROUP,rn.SWAP_OPACITY,rn.PRIMARY,rn.SECONDARY]).concat(kt.map(function(n){return"".concat(n,"x")})).concat(ir.map(function(n){return"w-".concat(n)})),sr={"Font Awesome 5 Free":{900:"fas",400:"far"},"Font Awesome 5 Pro":{900:"fas",400:"far",normal:"far",300:"fal"},"Font Awesome 5 Brands":{400:"fab",normal:"fab"},"Font Awesome 5 Duotone":{900:"fad"}},E="___FONT_AWESOME___",Fn=16,At="fa",It="svg-inline--fa",R="data-fa-i2svg",Nn="data-fa-pseudo-element",fr="data-fa-pseudo-element-pending",Yn="data-prefix",Xn="data-icon",we="fontawesome-i2svg",lr="async",ur=["HTML","HEAD","STYLE","SCRIPT"],zt=["::before","::after",":before",":after"],Ct=(function(){try{return!0}catch(n){return!1}})();function Q(n){return new Proxy(n,{get:function(e,a){return a in e?e[a]:e[w]}})}var Pt=l({},Ke);Pt[w]=l(l(l(l({},{"fa-duotone":"duotone"}),Ke[w]),ye.kit),ye["kit-duotone"]);var cr=Q(Pt),En=l({},Va);En[w]=l(l(l(l({},{duotone:"fad"}),En[w]),xe.kit),xe["kit-duotone"]);var Se=Q(En),Dn=l({},Pn);Dn[w]=l(l({},Dn[w]),ni.kit);var Vn=Q(Dn),Mn=l({},nr);Mn[w]=l(l({},Mn[w]),Qa.kit);var ts=Q(Mn),dr=va,Ft="fa-layers-text",mr=ha,gr=l({},Ua),as=Q(gr),pr=["class","data-prefix","data-icon","data-fa-transform","data-fa-mask"],Sn=ba,vr=[].concat(P(Ba),P(or)),G=j.FontAwesomeConfig||{};function hr(n){var t=h.querySelector("script["+n+"]");if(t)return t.getAttribute(n)}function br(n){return n===""?!0:n==="false"?!1:n==="true"?!0:n}h&&typeof h.querySelector=="function"&&(ke=[["data-family-prefix","familyPrefix"],["data-css-prefix","cssPrefix"],["data-family-default","familyDefault"],["data-style-default","styleDefault"],["data-replacement-class","replacementClass"],["data-auto-replace-svg","autoReplaceSvg"],["data-auto-add-css","autoAddCss"],["data-search-pseudo-elements","searchPseudoElements"],["data-search-pseudo-elements-warnings","searchPseudoElementsWarnings"],["data-search-pseudo-elements-full-scan","searchPseudoElementsFullScan"],["data-observe-mutations","observeMutations"],["data-mutate-approach","mutateApproach"],["data-keep-original-source","keepOriginalSource"],["data-measure-performance","measurePerformance"],["data-show-missing-icons","showMissingIcons"]],ke.forEach(function(n){var t=dn(n,2),e=t[0],a=t[1],i=br(hr(e));i!=null&&(G[a]=i)}));var ke,Nt={styleDefault:"solid",familyDefault:w,cssPrefix:At,replacementClass:It,autoReplaceSvg:!0,autoAddCss:!0,searchPseudoElements:!1,searchPseudoElementsWarnings:!0,searchPseudoElementsFullScan:!1,observeMutations:!0,mutateApproach:"async",keepOriginalSource:!0,measurePerformance:!1,showMissingIcons:!0};G.familyPrefix&&(G.cssPrefix=G.familyPrefix);var X=l(l({},Nt),G);X.autoReplaceSvg||(X.observeMutations=!1);var m={};Object.keys(Nt).forEach(function(n){Object.defineProperty(m,n,{enumerable:!0,set:function(e){X[n]=e,q.forEach(function(a){return a(m)})},get:function(){return X[n]}})});Object.defineProperty(m,"familyPrefix",{enumerable:!0,set:function(t){X.cssPrefix=t,q.forEach(function(e){return e(m)})},get:function(){return X.cssPrefix}});j.FontAwesomeConfig=m;var q=[];function yr(n){return q.push(n),function(){q.splice(q.indexOf(n),1)}}var O=Fn,F={size:16,x:0,y:0,rotate:0,flipX:!1,flipY:!1};function xr(n){if(!(!n||!M)){var t=h.createElement("style");t.setAttribute("type","text/css"),t.innerHTML=n;for(var e=h.head.childNodes,a=null,i=e.length-1;i>-1;i--){var r=e[i],o=(r.tagName||"").toUpperCase();["STYLE","LINK"].indexOf(o)>-1&&(a=r)}return h.head.insertBefore(t,a),n}}var wr="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";function Ae(){for(var n=12,t="";n-- >0;)t+=wr[Math.random()*62|0];return t}function V(n){for(var t=[],e=(n||[]).length>>>0;e--;)t[e]=n[e];return t}function Bn(n){return n.classList?V(n.classList):(n.getAttribute("class")||"").split(" ").filter(function(t){return t})}function Et(n){return"".concat(n).replace(/&/g,"&amp;").replace(/"/g,"&quot;").replace(/'/g,"&#39;").replace(/</g,"&lt;").replace(/>/g,"&gt;")}function Sr(n){return Object.keys(n||{}).reduce(function(t,e){return t+"".concat(e,'="').concat(Et(n[e]),'" ')},"").trim()}function mn(n){return Object.keys(n||{}).reduce(function(t,e){return t+"".concat(e,": ").concat(n[e].trim(),";")},"")}function Gn(n){return n.size!==F.size||n.x!==F.x||n.y!==F.y||n.rotate!==F.rotate||n.flipX||n.flipY}function kr(n){var t=n.transform,e=n.containerWidth,a=n.iconWidth,i={transform:"translate(".concat(e/2," 256)")},r="translate(".concat(t.x*32,", ").concat(t.y*32,") "),o="scale(".concat(t.size/16*(t.flipX?-1:1),", ").concat(t.size/16*(t.flipY?-1:1),") "),s="rotate(".concat(t.rotate," 0 0)"),f={transform:"".concat(r," ").concat(o," ").concat(s)},u={transform:"translate(".concat(a/2*-1," -256)")};return{outer:i,inner:f,path:u}}function Ar(n){var t=n.transform,e=n.width,a=e===void 0?Fn:e,i=n.height,r=i===void 0?Fn:i,o=n.startCentered,s=o===void 0?!1:o,f="";return s&&qe?f+="translate(".concat(t.x/O-a/2,"em, ").concat(t.y/O-r/2,"em) "):s?f+="translate(calc(-50% + ".concat(t.x/O,"em), calc(-50% + ").concat(t.y/O,"em)) "):f+="translate(".concat(t.x/O,"em, ").concat(t.y/O,"em) "),f+="scale(".concat(t.size/O*(t.flipX?-1:1),", ").concat(t.size/O*(t.flipY?-1:1),") "),f+="rotate(".concat(t.rotate,"deg) "),f}var Ir=`:root, :host {
  --fa-font-solid: normal 900 1em/1 'Font Awesome 7 Free';
  --fa-font-regular: normal 400 1em/1 'Font Awesome 7 Free';
  --fa-font-light: normal 300 1em/1 'Font Awesome 7 Pro';
  --fa-font-thin: normal 100 1em/1 'Font Awesome 7 Pro';
  --fa-font-duotone: normal 900 1em/1 'Font Awesome 7 Duotone';
  --fa-font-duotone-regular: normal 400 1em/1 'Font Awesome 7 Duotone';
  --fa-font-duotone-light: normal 300 1em/1 'Font Awesome 7 Duotone';
  --fa-font-duotone-thin: normal 100 1em/1 'Font Awesome 7 Duotone';
  --fa-font-brands: normal 400 1em/1 'Font Awesome 7 Brands';
  --fa-font-sharp-solid: normal 900 1em/1 'Font Awesome 7 Sharp';
  --fa-font-sharp-regular: normal 400 1em/1 'Font Awesome 7 Sharp';
  --fa-font-sharp-light: normal 300 1em/1 'Font Awesome 7 Sharp';
  --fa-font-sharp-thin: normal 100 1em/1 'Font Awesome 7 Sharp';
  --fa-font-sharp-duotone-solid: normal 900 1em/1 'Font Awesome 7 Sharp Duotone';
  --fa-font-sharp-duotone-regular: normal 400 1em/1 'Font Awesome 7 Sharp Duotone';
  --fa-font-sharp-duotone-light: normal 300 1em/1 'Font Awesome 7 Sharp Duotone';
  --fa-font-sharp-duotone-thin: normal 100 1em/1 'Font Awesome 7 Sharp Duotone';
  --fa-font-slab-regular: normal 400 1em/1 'Font Awesome 7 Slab';
  --fa-font-slab-press-regular: normal 400 1em/1 'Font Awesome 7 Slab Press';
  --fa-font-slab-duo-regular: normal 400 1em/1 'Font Awesome 7 Slab Duo';
  --fa-font-slab-press-duo-regular: normal 400 1em/1 'Font Awesome 7 Slab Press Duo';
  --fa-font-pixel-regular: normal 400 1em/1 'Font Awesome 7 Pixel';
  --fa-font-mosaic-solid: normal 900 1em/1 'Font Awesome 7 Mosaic';
  --fa-font-vellum-solid: normal 900 1em/1 'Font Awesome 7 Vellum';
  --fa-font-whiteboard-semibold: normal 600 1em/1 'Font Awesome 7 Whiteboard';
  --fa-font-thumbprint-light: normal 300 1em/1 'Font Awesome 7 Thumbprint';
  --fa-font-notdog-solid: normal 900 1em/1 'Font Awesome 7 Notdog';
  --fa-font-notdog-duo-solid: normal 900 1em/1 'Font Awesome 7 Notdog Duo';
  --fa-font-etch-solid: normal 900 1em/1 'Font Awesome 7 Etch';
  --fa-font-graphite-thin: normal 100 1em/1 'Font Awesome 7 Graphite';
  --fa-font-jelly-regular: normal 400 1em/1 'Font Awesome 7 Jelly';
  --fa-font-jelly-fill-regular: normal 400 1em/1 'Font Awesome 7 Jelly Fill';
  --fa-font-jelly-duo-regular: normal 400 1em/1 'Font Awesome 7 Jelly Duo';
  --fa-font-chisel-regular: normal 400 1em/1 'Font Awesome 7 Chisel';
  --fa-font-utility-semibold: normal 600 1em/1 'Font Awesome 7 Utility';
  --fa-font-utility-duo-semibold: normal 600 1em/1 'Font Awesome 7 Utility Duo';
  --fa-font-utility-fill-semibold: normal 600 1em/1 'Font Awesome 7 Utility Fill';
}

.svg-inline--fa {
  box-sizing: content-box;
  display: var(--fa-display, inline-block);
  height: 1em;
  overflow: visible;
  vertical-align: -0.125em;
  width: var(--fa-width, 1.25em);
}
.svg-inline--fa.fa-2xs {
  vertical-align: 0.1em;
}
.svg-inline--fa.fa-xs {
  vertical-align: 0em;
}
.svg-inline--fa.fa-sm {
  vertical-align: -0.0714285714em;
}
.svg-inline--fa.fa-lg {
  vertical-align: -0.2em;
}
.svg-inline--fa.fa-xl {
  vertical-align: -0.25em;
}
.svg-inline--fa.fa-2xl {
  vertical-align: -0.3125em;
}
.svg-inline--fa.fa-pull-left,
.svg-inline--fa .fa-pull-start {
  float: inline-start;
  margin-inline-end: var(--fa-pull-margin, 0.3em);
}
.svg-inline--fa.fa-pull-right,
.svg-inline--fa .fa-pull-end {
  float: inline-end;
  margin-inline-start: var(--fa-pull-margin, 0.3em);
}
.svg-inline--fa.fa-li {
  width: var(--fa-li-width, 2em);
  inset-inline-start: calc(-1 * var(--fa-li-width, 2em));
  inset-block-start: 0.25em; /* syncing vertical alignment with Web Font rendering */
}

.fa-layers-counter, .fa-layers-text {
  display: inline-block;
  position: absolute;
  text-align: center;
}

.fa-layers {
  display: inline-block;
  height: 1em;
  position: relative;
  text-align: center;
  vertical-align: -0.125em;
  width: var(--fa-width, 1.25em);
}
.fa-layers .svg-inline--fa {
  inset: 0;
  margin: auto;
  position: absolute;
  transform-origin: center center;
}

.fa-layers-text {
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  transform-origin: center center;
}

.fa-layers-counter {
  background-color: var(--fa-counter-background-color, #ff253a);
  border-radius: var(--fa-counter-border-radius, 1em);
  box-sizing: border-box;
  color: var(--fa-inverse, #fff);
  line-height: var(--fa-counter-line-height, 1);
  max-width: var(--fa-counter-max-width, 5em);
  min-width: var(--fa-counter-min-width, 1.5em);
  overflow: hidden;
  padding: var(--fa-counter-padding, 0.25em 0.5em);
  right: var(--fa-right, 0);
  text-overflow: ellipsis;
  top: var(--fa-top, 0);
  transform: scale(var(--fa-counter-scale, 0.25));
  transform-origin: top right;
}

.fa-layers-bottom-right {
  bottom: var(--fa-bottom, 0);
  right: var(--fa-right, 0);
  top: auto;
  transform: scale(var(--fa-layers-scale, 0.25));
  transform-origin: bottom right;
}

.fa-layers-bottom-left {
  bottom: var(--fa-bottom, 0);
  left: var(--fa-left, 0);
  right: auto;
  top: auto;
  transform: scale(var(--fa-layers-scale, 0.25));
  transform-origin: bottom left;
}

.fa-layers-top-right {
  top: var(--fa-top, 0);
  right: var(--fa-right, 0);
  transform: scale(var(--fa-layers-scale, 0.25));
  transform-origin: top right;
}

.fa-layers-top-left {
  left: var(--fa-left, 0);
  right: auto;
  top: var(--fa-top, 0);
  transform: scale(var(--fa-layers-scale, 0.25));
  transform-origin: top left;
}

.fa-1x {
  font-size: 1em;
}

.fa-2x {
  font-size: 2em;
}

.fa-3x {
  font-size: 3em;
}

.fa-4x {
  font-size: 4em;
}

.fa-5x {
  font-size: 5em;
}

.fa-6x {
  font-size: 6em;
}

.fa-7x {
  font-size: 7em;
}

.fa-8x {
  font-size: 8em;
}

.fa-9x {
  font-size: 9em;
}

.fa-10x {
  font-size: 10em;
}

.fa-2xs {
  font-size: calc(10 / 16 * 1em); /* converts a 10px size into an em-based value that's relative to the scale's 16px base */
  line-height: calc(1 / 10 * 1em); /* sets the line-height of the icon back to that of it's parent */
  vertical-align: calc((6 / 10 - 0.375) * 1em); /* vertically centers the icon taking into account the surrounding text's descender */
}

.fa-xs {
  font-size: calc(12 / 16 * 1em); /* converts a 12px size into an em-based value that's relative to the scale's 16px base */
  line-height: calc(1 / 12 * 1em); /* sets the line-height of the icon back to that of it's parent */
  vertical-align: calc((6 / 12 - 0.375) * 1em); /* vertically centers the icon taking into account the surrounding text's descender */
}

.fa-sm {
  font-size: calc(14 / 16 * 1em); /* converts a 14px size into an em-based value that's relative to the scale's 16px base */
  line-height: calc(1 / 14 * 1em); /* sets the line-height of the icon back to that of it's parent */
  vertical-align: calc((6 / 14 - 0.375) * 1em); /* vertically centers the icon taking into account the surrounding text's descender */
}

.fa-lg {
  font-size: calc(20 / 16 * 1em); /* converts a 20px size into an em-based value that's relative to the scale's 16px base */
  line-height: calc(1 / 20 * 1em); /* sets the line-height of the icon back to that of it's parent */
  vertical-align: calc((6 / 20 - 0.375) * 1em); /* vertically centers the icon taking into account the surrounding text's descender */
}

.fa-xl {
  font-size: calc(24 / 16 * 1em); /* converts a 24px size into an em-based value that's relative to the scale's 16px base */
  line-height: calc(1 / 24 * 1em); /* sets the line-height of the icon back to that of it's parent */
  vertical-align: calc((6 / 24 - 0.375) * 1em); /* vertically centers the icon taking into account the surrounding text's descender */
}

.fa-2xl {
  font-size: calc(32 / 16 * 1em); /* converts a 32px size into an em-based value that's relative to the scale's 16px base */
  line-height: calc(1 / 32 * 1em); /* sets the line-height of the icon back to that of it's parent */
  vertical-align: calc((6 / 32 - 0.375) * 1em); /* vertically centers the icon taking into account the surrounding text's descender */
}

.fa-width-auto {
  --fa-width: auto;
}

.fa-fw,
.fa-width-fixed {
  --fa-width: 1.25em;
}

.fa-canvas-square {
  padding-block: 0.125em;
  margin-block-end: -0.125em;
}

.fa-canvas-roomy {
  padding-block: 0.25em;
  padding-inline: 0.125em;
  margin-block-end: -0.25em;
  box-sizing: content-box;
}

.fa-ul {
  list-style-type: none;
  margin-inline-start: var(--fa-li-margin, 2.5em);
  padding-inline-start: 0;
}
.fa-ul > li {
  position: relative;
}

.fa-li {
  inset-inline-start: calc(-1 * var(--fa-li-width, 2em));
  position: absolute;
  text-align: center;
  width: var(--fa-li-width, 2em);
  line-height: inherit;
}

/* Heads Up: Bordered Icons will not be supported in the future!
  - This feature will be deprecated in the next major release of Font Awesome (v8)!
  - You may continue to use it in this version *v7), but it will not be supported in Font Awesome v8.
*/
/* Notes:
* --@{v.$css-prefix}-border-width = 1/16 by default (to render as ~1px based on a 16px default font-size)
* --@{v.$css-prefix}-border-padding =
  ** 3/16 for vertical padding (to give ~2px of vertical whitespace around an icon considering it's vertical alignment)
  ** 4/16 for horizontal padding (to give ~4px of horizontal whitespace around an icon)
*/
.fa-border {
  border-color: var(--fa-border-color, #eee);
  border-radius: var(--fa-border-radius, 0.1em);
  border-style: var(--fa-border-style, solid);
  border-width: var(--fa-border-width, 0.0625em);
  box-sizing: var(--fa-border-box-sizing, content-box);
  padding: var(--fa-border-padding, 0.1875em 0.25em);
}

.fa-pull-left,
.fa-pull-start {
  float: inline-start;
  margin-inline-end: var(--fa-pull-margin, 0.3em);
}

.fa-pull-right,
.fa-pull-end {
  float: inline-end;
  margin-inline-start: var(--fa-pull-margin, 0.3em);
}

.fa-beat {
  animation-name: fa-beat;
  animation-delay: var(--fa-animation-delay, 0s);
  animation-direction: var(--fa-animation-direction, normal);
  animation-duration: var(--fa-animation-duration, 1s);
  animation-iteration-count: var(--fa-animation-iteration-count, infinite);
  animation-timing-function: var(--fa-animation-timing, ease-in-out);
}

.fa-bounce {
  animation-name: fa-bounce;
  animation-delay: var(--fa-animation-delay, 0s);
  animation-direction: var(--fa-animation-direction, normal);
  animation-duration: var(--fa-animation-duration, 1s);
  animation-iteration-count: var(--fa-animation-iteration-count, infinite);
  animation-timing-function: var(--fa-animation-timing, cubic-bezier(0.28, 0.84, 0.42, 1));
}

.fa-fade {
  animation-name: fa-fade;
  animation-delay: var(--fa-animation-delay, 0s);
  animation-direction: var(--fa-animation-direction, normal);
  animation-duration: var(--fa-animation-duration, 1s);
  animation-iteration-count: var(--fa-animation-iteration-count, infinite);
  animation-timing-function: var(--fa-animation-timing, ease-in-out);
}

.fa-beat-fade {
  animation-name: fa-beat-fade;
  animation-delay: var(--fa-animation-delay, 0s);
  animation-direction: var(--fa-animation-direction, normal);
  animation-duration: var(--fa-animation-duration, 1s);
  animation-iteration-count: var(--fa-animation-iteration-count, infinite);
  animation-timing-function: var(--fa-animation-timing, ease-in-out);
}

.fa-flip {
  animation-name: fa-flip;
  animation-delay: var(--fa-animation-delay, 0s);
  animation-direction: var(--fa-animation-direction, normal);
  animation-duration: var(--fa-animation-duration, 1.5s);
  animation-iteration-count: var(--fa-animation-iteration-count, infinite);
  animation-timing-function: var(--fa-animation-timing, ease-in-out);
}

.fa-flip-360 {
  animation-name: fa-flip-360;
  animation-delay: var(--fa-animation-delay, 0s);
  animation-direction: var(--fa-animation-direction, normal);
  animation-duration: var(--fa-animation-duration, 1s);
  animation-iteration-count: var(--fa-animation-iteration-count, infinite);
  animation-timing-function: var(--fa-animation-timing, ease-in-out);
}

.fa-shake {
  animation-name: fa-shake;
  animation-delay: var(--fa-animation-delay, 0s);
  animation-direction: var(--fa-animation-direction, normal);
  animation-duration: var(--fa-animation-duration, 0.75s);
  animation-iteration-count: var(--fa-animation-iteration-count, infinite);
  animation-timing-function: var(--fa-animation-timing, ease-in-out);
}

.fa-spin {
  animation-name: fa-spin;
  animation-delay: var(--fa-animation-delay, 0s);
  animation-direction: var(--fa-animation-direction, normal);
  animation-duration: var(--fa-animation-duration, 2s);
  animation-iteration-count: var(--fa-animation-iteration-count, infinite);
  animation-timing-function: var(--fa-animation-timing, linear);
}

.fa-spin-reverse {
  --fa-animation-direction: reverse;
}

.fa-pulse,
.fa-spin-pulse {
  animation-name: fa-spin;
  animation-direction: var(--fa-animation-direction, normal);
  animation-duration: var(--fa-animation-duration, 1s);
  animation-iteration-count: var(--fa-animation-iteration-count, infinite);
  animation-timing-function: var(--fa-animation-timing, steps(8));
}

.fa-spin-snap {
  animation-name: fa-spin-snap;
  animation-delay: var(--fa-animation-delay, 0s);
  animation-direction: var(--fa-animation-direction, normal);
  animation-duration: var(--fa-animation-duration, 3s);
  animation-iteration-count: var(--fa-animation-iteration-count, infinite);
  animation-timing-function: var(--fa-animation-timing, linear);
}

.fa-spin-snap-4 {
  animation-name: fa-spin-snap-4;
  animation-delay: var(--fa-animation-delay, 0s);
  animation-direction: var(--fa-animation-direction, normal);
  animation-duration: var(--fa-animation-duration, 2.4s);
  animation-iteration-count: var(--fa-animation-iteration-count, infinite);
  animation-timing-function: var(--fa-animation-timing, linear);
}

.fa-spin-snap-8 {
  animation-name: fa-spin-snap-8;
  animation-delay: var(--fa-animation-delay, 0s);
  animation-direction: var(--fa-animation-direction, normal);
  animation-duration: var(--fa-animation-duration, 4s);
  animation-iteration-count: var(--fa-animation-iteration-count, infinite);
  animation-timing-function: var(--fa-animation-timing, linear);
}

.fa-buzz {
  animation-name: fa-buzz;
  animation-delay: var(--fa-animation-delay, 0s);
  animation-direction: var(--fa-animation-direction, normal);
  animation-duration: var(--fa-animation-duration, 0.6s);
  animation-iteration-count: var(--fa-animation-iteration-count, infinite);
  animation-timing-function: var(--fa-animation-timing, linear);
}

.fa-wag {
  animation-name: fa-wag;
  animation-delay: var(--fa-animation-delay, 0s);
  animation-direction: var(--fa-animation-direction, normal);
  animation-duration: var(--fa-animation-duration, 0.9s);
  animation-iteration-count: var(--fa-animation-iteration-count, infinite);
  animation-timing-function: var(--fa-animation-timing, ease-out);
  transform-origin: bottom center;
}

.fa-float {
  animation-name: fa-float;
  animation-delay: var(--fa-animation-delay, 0s);
  animation-direction: var(--fa-animation-direction, normal);
  animation-duration: var(--fa-animation-duration, 3s);
  animation-iteration-count: var(--fa-animation-iteration-count, infinite);
  animation-timing-function: var(--fa-animation-timing, ease-in-out);
  will-change: transform;
}

.fa-swing {
  animation-name: fa-swing;
  animation-delay: var(--fa-animation-delay, 0s);
  animation-direction: var(--fa-animation-direction, normal);
  animation-duration: var(--fa-animation-duration, 1.2s);
  animation-iteration-count: var(--fa-animation-iteration-count, infinite);
  animation-timing-function: var(--fa-animation-timing, ease-out);
  transform-origin: top center;
}

.fa-jello {
  animation-name: fa-jello;
  animation-delay: var(--fa-animation-delay, 0s);
  animation-direction: var(--fa-animation-direction, normal);
  animation-duration: var(--fa-animation-duration, 0.9s);
  animation-iteration-count: var(--fa-animation-iteration-count, infinite);
  animation-timing-function: var(--fa-animation-timing, ease-out);
}

@media (prefers-reduced-motion: reduce) {
  .fa-beat,
  .fa-bounce,
  .fa-fade,
  .fa-beat-fade,
  .fa-flip,
  .fa-flip-360,
  .fa-pulse,
  .fa-shake,
  .fa-spin,
  .fa-spin-pulse,
  .fa-buzz,
  .fa-float,
  .fa-jello,
  .fa-spin-snap,
  .fa-spin-snap-4,
  .fa-spin-snap-8,
  .fa-swing,
  .fa-wag {
    animation: none !important;
    transition: none !important;
  }
}
@keyframes fa-beat {
  0% {
    transform: scale(1);
  }
  25% {
    transform: scale(calc(1.25 * var(--fa-beat-scale, 1.25)));
  }
  45% {
    transform: scale(calc(1.22 * var(--fa-beat-scale, 1.22)));
  }
  65% {
    transform: scale(calc(1.25 * var(--fa-beat-scale, 1.25)));
  }
  90% {
    transform: scale(1);
  }
}
@keyframes fa-bounce {
  0% {
    transform: scale(1, 1) translateY(0);
    animation-timing-function: var(--fa-animation-timing);
  }
  14% {
    transform: scale(var(--fa-bounce-start-scale-x, 1.06), var(--fa-bounce-start-scale-y, 0.94)) translateY(var(--fa-bounce-anticipation, 3px));
    animation-timing-function: cubic-bezier(0.33, 0, 0.66, 0.33);
  }
  32% {
    transform: scale(var(--fa-bounce-jump-scale-x, 0.94), var(--fa-bounce-jump-scale-y, 1.12)) translateY(calc(-1 * var(--fa-bounce-height, 0.5em)));
    animation-timing-function: cubic-bezier(0.33, 0.66, 0.66, 1);
  }
  52% {
    transform: scale(1, 1) translateY(calc(-1 * var(--fa-bounce-height, 0.5em) * 1.1));
    animation-timing-function: cubic-bezier(0.5, 0, 1, 0.5);
  }
  70% {
    transform: scale(var(--fa-bounce-land-scale-x, 1.06), var(--fa-bounce-land-scale-y, 0.92)) translateY(0);
    animation-timing-function: cubic-bezier(0.33, 0.33, 0.66, 1);
  }
  85% {
    transform: scale(0.98, 1.04) translateY(calc(-2px * var(--fa-bounce-rebound, 1)));
    animation-timing-function: cubic-bezier(0.33, 0, 0.66, 1);
  }
  100% {
    transform: scale(1, 1) translateY(0);
  }
}
@keyframes fa-fade {
  0% {
    opacity: 1;
    transform: scale(1);
    animation-timing-function: cubic-bezier(0.2, 0, 0.4, 1);
  }
  40% {
    opacity: var(--fa-fade-opacity, 0.4);
    transform: scale(0.98);
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}
@keyframes fa-beat-fade {
  0% {
    opacity: var(--fa-beat-fade-opacity, 0.4);
    transform: scale(1);
    animation-timing-function: cubic-bezier(0.2, 0, 0.4, 1);
  }
  25% {
    opacity: calc(var(--fa-beat-fade-opacity, 0.4) + 0.4);
    transform: scale(var(--fa-beat-fade-scale, 1.28));
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  45% {
    opacity: 1;
    transform: scale(var(--fa-beat-fade-scale, 1.25));
    animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  }
  65% {
    opacity: calc(var(--fa-beat-fade-opacity, 0.4) + 0.4);
    transform: scale(var(--fa-beat-fade-scale, 1.28));
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  100% {
    opacity: var(--fa-beat-fade-opacity, 0.4);
    transform: scale(1);
  }
}
@keyframes fa-flip {
  0% {
    transform: perspective(2em) scale(1) rotate3d(var(--fa-flip-x, 0), var(--fa-flip-y, 1), var(--fa-flip-z, 0), 0deg);
    animation-timing-function: cubic-bezier(0.2, 0, 0.4, 1);
  }
  8% {
    transform: perspective(2em) scale(var(--fa-flip-anticipation-scale, 0.95)) rotate3d(var(--fa-flip-x, 0), var(--fa-flip-y, 1), var(--fa-flip-z, 0), 0deg);
    animation-timing-function: cubic-bezier(0.33, 0, 0.66, 0.33);
  }
  35% {
    transform: perspective(2em) scale(1) rotate3d(var(--fa-flip-x, 0), var(--fa-flip-y, 1), var(--fa-flip-z, 0), calc(var(--fa-flip-angle, -360deg) * 0.6));
    animation-timing-function: linear;
  }
  65% {
    transform: perspective(2em) scale(1) rotate3d(var(--fa-flip-x, 0), var(--fa-flip-y, 1), var(--fa-flip-z, 0), calc(var(--fa-flip-angle, -360deg) * 0.5));
    animation-timing-function: cubic-bezier(0.33, 0.66, 0.66, 1);
  }
  92% {
    transform: perspective(2em) scale(1) rotate3d(var(--fa-flip-x, 0), var(--fa-flip-y, 1), var(--fa-flip-z, 0), calc(var(--fa-flip-angle, -360deg) * var(--fa-flip-overshoot, 1.04)));
    animation-timing-function: cubic-bezier(0.33, 0, 0.66, 1);
  }
  100% {
    transform: perspective(2em) scale(1) rotate3d(var(--fa-flip-x, 0), var(--fa-flip-y, 1), var(--fa-flip-z, 0), var(--fa-flip-angle, -360deg));
  }
}
@keyframes fa-flip-360 {
  0% {
    transform: perspective(2em) scale(1) rotate3d(var(--fa-flip-x, 0), var(--fa-flip-y, 1), var(--fa-flip-z, 0), 0deg);
    animation-timing-function: cubic-bezier(0.2, 0, 0.4, 1);
  }
  8% {
    transform: perspective(2em) scale(var(--fa-flip-anticipation-scale, 0.95)) rotate3d(var(--fa-flip-x, 0), var(--fa-flip-y, 1), var(--fa-flip-z, 0), 0deg);
    animation-timing-function: cubic-bezier(0.33, 0, 0.66, 0.33);
  }
  50% {
    transform: perspective(2em) scale(1) rotate3d(var(--fa-flip-x, 0), var(--fa-flip-y, 1), var(--fa-flip-z, 0), calc(var(--fa-flip-angle, -360deg) * 0.6));
    animation-timing-function: cubic-bezier(0.33, 0.66, 0.66, 1);
  }
  80% {
    transform: perspective(2em) scale(1) rotate3d(var(--fa-flip-x, 0), var(--fa-flip-y, 1), var(--fa-flip-z, 0), calc(var(--fa-flip-angle, -360deg) * var(--fa-flip-overshoot, 1.04)));
    animation-timing-function: cubic-bezier(0.33, 0, 0.66, 1);
  }
  100% {
    transform: perspective(2em) scale(1) rotate3d(var(--fa-flip-x, 0), var(--fa-flip-y, 1), var(--fa-flip-z, 0), var(--fa-flip-angle, -360deg));
  }
}
@keyframes fa-shake {
  0% {
    transform: rotate(0deg);
    animation-timing-function: cubic-bezier(0.2, 0, 0.8, 1);
  }
  8% {
    transform: rotate(35deg) translateX(1px);
    animation-timing-function: cubic-bezier(0.3, 0, 0.7, 1);
  }
  20% {
    transform: rotate(-22deg) translateX(-1px);
    animation-timing-function: cubic-bezier(0.3, 0, 0.7, 1);
  }
  35% {
    transform: rotate(15deg) translateX(1px);
    animation-timing-function: cubic-bezier(0.3, 0, 0.7, 1);
  }
  50% {
    transform: rotate(-9deg);
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  65% {
    transform: rotate(5deg);
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  78% {
    transform: rotate(-3deg);
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  90% {
    transform: rotate(1deg);
    animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  }
  100% {
    transform: rotate(0deg);
  }
}
@keyframes fa-spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
@keyframes fa-spin-snap {
  0% {
    transform: rotate(0deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  12% {
    transform: rotate(60deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  16.67% {
    transform: rotate(60deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  28.67% {
    transform: rotate(120deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  33.33% {
    transform: rotate(120deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  45.33% {
    transform: rotate(180deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  50% {
    transform: rotate(180deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  62% {
    transform: rotate(240deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  66.67% {
    transform: rotate(240deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  78.67% {
    transform: rotate(300deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  83.33% {
    transform: rotate(300deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  95.33% {
    transform: rotate(360deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  100% {
    transform: rotate(360deg);
  }
}
@keyframes fa-spin-snap-4 {
  0% {
    transform: rotate(0deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  15% {
    transform: rotate(90deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  25% {
    transform: rotate(90deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  40% {
    transform: rotate(180deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  50% {
    transform: rotate(180deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  65% {
    transform: rotate(270deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  75% {
    transform: rotate(270deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  90% {
    transform: rotate(360deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  100% {
    transform: rotate(360deg);
  }
}
@keyframes fa-spin-snap-8 {
  0% {
    transform: rotate(0deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  9% {
    transform: rotate(45deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  12.5% {
    transform: rotate(45deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  21.5% {
    transform: rotate(90deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  25% {
    transform: rotate(90deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  34% {
    transform: rotate(135deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  37.5% {
    transform: rotate(135deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  46.5% {
    transform: rotate(180deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  50% {
    transform: rotate(180deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  59% {
    transform: rotate(225deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  62.5% {
    transform: rotate(225deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  71.5% {
    transform: rotate(270deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  75% {
    transform: rotate(270deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  84% {
    transform: rotate(315deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  87.5% {
    transform: rotate(315deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  96.5% {
    transform: rotate(360deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  100% {
    transform: rotate(360deg);
  }
}
@keyframes fa-buzz {
  0% {
    transform: translateX(0) rotate(0deg);
    animation-timing-function: cubic-bezier(0.1, 0, 0.9, 1);
  }
  5% {
    transform: translateX(var(--fa-buzz-distance, 4px)) rotate(0.5deg);
  }
  10% {
    transform: translateX(calc(-1 * var(--fa-buzz-distance, 4px))) rotate(-0.5deg);
  }
  15% {
    transform: translateX(var(--fa-buzz-distance, 4px)) rotate(0.3deg);
  }
  20% {
    transform: translateX(calc(-1 * var(--fa-buzz-distance, 4px))) rotate(-0.3deg);
  }
  25% {
    transform: translateX(calc(var(--fa-buzz-distance, 4px) * 0.7)) rotate(0.2deg);
  }
  30% {
    transform: translateX(calc(-1 * var(--fa-buzz-distance, 4px) * 0.7)) rotate(-0.2deg);
  }
  35% {
    transform: translateX(calc(var(--fa-buzz-distance, 4px) * 0.4)) rotate(0.1deg);
  }
  40% {
    transform: translateX(0) rotate(0deg);
  }
  100% {
    transform: translateX(0) rotate(0deg);
  }
}
@keyframes fa-wag {
  0% {
    transform: rotate(0deg);
    animation-timing-function: cubic-bezier(0.2, 0, 0.6, 1);
  }
  12% {
    transform: rotate(var(--fa-wag-angle, 12deg));
    animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  }
  24% {
    transform: rotate(2deg);
    animation-timing-function: cubic-bezier(0.2, 0, 0.6, 1);
  }
  36% {
    transform: rotate(calc(var(--fa-wag-angle, 12deg) * 0.85));
    animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  }
  48% {
    transform: rotate(1deg);
    animation-timing-function: cubic-bezier(0.2, 0, 0.6, 1);
  }
  58% {
    transform: rotate(calc(var(--fa-wag-angle, 12deg) * 0.6));
    animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  }
  68% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(0deg);
  }
}
@keyframes fa-float {
  0% {
    transform: translateY(0) translateX(0) rotate(0deg) scale(var(--fa-float-squash-x, 1.02), var(--fa-float-squash-y, 0.98));
    animation-timing-function: cubic-bezier(0.33, 0, 0.66, 0.33);
  }
  15% {
    transform: translateY(calc(-0.4 * var(--fa-float-height, 6px))) translateX(var(--fa-float-drift, 1px)) rotate(var(--fa-float-tilt, 1deg)) scale(1, 1);
    animation-timing-function: cubic-bezier(0.33, 0.66, 0.66, 1);
  }
  35% {
    transform: translateY(calc(-1 * var(--fa-float-height, 6px))) translateX(0) rotate(0deg) scale(var(--fa-float-stretch-x, 0.98), var(--fa-float-stretch-y, 1.03));
    animation-timing-function: cubic-bezier(0.5, 0, 0.5, 0);
  }
  50% {
    transform: translateY(calc(-0.92 * var(--fa-float-height, 6px))) translateX(calc(-0.5 * var(--fa-float-drift, 1px))) rotate(calc(-0.5 * var(--fa-float-tilt, 1deg))) scale(0.995, 1.01);
    animation-timing-function: cubic-bezier(0.33, 0, 0.66, 0.33);
  }
  70% {
    transform: translateY(calc(-0.3 * var(--fa-float-height, 6px))) translateX(calc(-1 * var(--fa-float-drift, 1px))) rotate(calc(-1 * var(--fa-float-tilt, 1deg))) scale(1, 1);
    animation-timing-function: cubic-bezier(0.33, 0.66, 0.66, 1);
  }
  90% {
    transform: translateY(calc(0.05 * var(--fa-float-height, 6px))) translateX(0) rotate(0deg) scale(var(--fa-float-squash-x, 1.02), var(--fa-float-squash-y, 0.98));
    animation-timing-function: cubic-bezier(0.33, 0, 0.66, 1);
  }
  100% {
    transform: translateY(0) translateX(0) rotate(0deg) scale(var(--fa-float-squash-x, 1.02), var(--fa-float-squash-y, 0.98));
  }
}
@keyframes fa-swing {
  0% {
    transform: rotate(0deg);
    animation-timing-function: cubic-bezier(0.2, 0, 0.8, 1);
  }
  8% {
    transform: rotate(var(--fa-swing-angle, 22deg));
    animation-timing-function: cubic-bezier(0.3, 0, 0.7, 1);
  }
  18% {
    transform: rotate(calc(-1 * var(--fa-swing-angle, 22deg) * 0.85));
    animation-timing-function: cubic-bezier(0.3, 0, 0.7, 1);
  }
  28% {
    transform: rotate(calc(var(--fa-swing-angle, 22deg) * 0.65));
    animation-timing-function: cubic-bezier(0.35, 0, 0.65, 1);
  }
  38% {
    transform: rotate(calc(-1 * var(--fa-swing-angle, 22deg) * 0.45));
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  48% {
    transform: rotate(calc(var(--fa-swing-angle, 22deg) * 0.25));
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  56% {
    transform: rotate(calc(-1 * var(--fa-swing-angle, 22deg) * 0.1));
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  64% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(0deg);
  }
}
@keyframes fa-jello {
  0% {
    transform: scale(1, 1);
    animation-timing-function: cubic-bezier(0.2, 0, 0.8, 1);
  }
  12% {
    transform: scale(var(--fa-jello-scale-x, 1.15), calc(2 - var(--fa-jello-scale-x, 1.15)));
    animation-timing-function: cubic-bezier(0.3, 0, 0.7, 1);
  }
  24% {
    transform: scale(calc(2 - var(--fa-jello-scale-y, 1.12)), var(--fa-jello-scale-y, 1.12));
    animation-timing-function: cubic-bezier(0.3, 0, 0.7, 1);
  }
  36% {
    transform: scale(calc(1 + (var(--fa-jello-scale-x, 1.15) - 1) * 0.5), calc(2 - (1 + (var(--fa-jello-scale-x, 1.15) - 1) * 0.5)));
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  48% {
    transform: scale(calc(2 - (1 + (var(--fa-jello-scale-y, 1.12) - 1) * 0.3)), calc(1 + (var(--fa-jello-scale-y, 1.12) - 1) * 0.3));
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  58% {
    transform: scale(1.02, 0.98);
    animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  }
  68% {
    transform: scale(1, 1);
  }
  100% {
    transform: scale(1, 1);
  }
}
.fa-rotate-90 {
  transform: rotate(90deg);
}

.fa-rotate-180 {
  transform: rotate(180deg);
}

.fa-rotate-270 {
  transform: rotate(270deg);
}

.fa-flip-horizontal {
  transform: scale(-1, 1);
}

.fa-flip-vertical {
  transform: scale(1, -1);
}

.fa-flip-both,
.fa-flip-horizontal.fa-flip-vertical {
  transform: scale(-1, -1);
}

.fa-rotate-by {
  transform: rotate(var(--fa-rotate-angle, 0));
}

.svg-inline--fa .fa-primary {
  fill: var(--fa-primary-color, currentColor);
  opacity: var(--fa-primary-opacity, 1);
}

.svg-inline--fa .fa-secondary {
  fill: var(--fa-secondary-color, currentColor);
  opacity: var(--fa-secondary-opacity, 0.4);
}

.svg-inline--fa.fa-swap-opacity .fa-primary {
  opacity: var(--fa-secondary-opacity, 0.4);
}

.svg-inline--fa.fa-swap-opacity .fa-secondary {
  opacity: var(--fa-primary-opacity, 1);
}

.svg-inline--fa mask .fa-primary,
.svg-inline--fa mask .fa-secondary {
  fill: black;
}

.svg-inline--fa.fa-inverse {
  fill: var(--fa-inverse, #fff);
}

.fa-stack {
  display: inline-block;
  height: 2em;
  line-height: 2em;
  position: relative;
  vertical-align: middle;
  width: 2.5em;
}

.fa-inverse {
  color: var(--fa-inverse, #fff);
}

.svg-inline--fa.fa-stack-1x {
  --fa-width: 1.25em;
  height: 1em;
  width: var(--fa-width);
}
.svg-inline--fa.fa-stack-2x {
  --fa-width: 2.5em;
  height: 2em;
  width: var(--fa-width);
}

.fa-stack-1x,
.fa-stack-2x {
  inset: 0;
  margin: auto;
  position: absolute;
  z-index: var(--fa-stack-z-index, auto);
}`;function Dt(){var n=At,t=It,e=m.cssPrefix,a=m.replacementClass,i=Ir;if(e!==n||a!==t){var r=new RegExp("\\.".concat(n,"\\-"),"g"),o=new RegExp("\\--".concat(n,"\\-"),"g"),s=new RegExp("\\.".concat(t),"g");i=i.replace(r,".".concat(e,"-")).replace(o,"--".concat(e,"-")).replace(s,".".concat(a))}return i}var Ie=!1;function kn(){m.autoAddCss&&!Ie&&(xr(Dt()),Ie=!0)}var zr={mixout:function(){return{dom:{css:Dt,insertCss:kn}}},hooks:function(){return{beforeDOMElementCreation:function(){kn()},beforeI2svg:function(){kn()}}}},D=j||{};D[E]||(D[E]={});D[E].styles||(D[E].styles={});D[E].hooks||(D[E].hooks={});D[E].shims||(D[E].shims=[]);var C=D[E],Mt=[],Ot=function(){h.removeEventListener("DOMContentLoaded",Ot),un=1,Mt.map(function(t){return t()})},un=!1;M&&(un=(h.documentElement.doScroll?/^loaded|^c/:/^loaded|^i|^c/).test(h.readyState),un||h.addEventListener("DOMContentLoaded",Ot));function Cr(n){M&&(un?setTimeout(n,0):Mt.push(n))}function Z(n){var t=n.tag,e=n.attributes,a=e===void 0?{}:e,i=n.children,r=i===void 0?[]:i;return typeof n=="string"?Et(n):"<".concat(t," ").concat(Sr(a),">").concat(r.map(Z).join(""),"</").concat(t,">")}function ze(n,t,e){if(n&&n[t]&&n[t][e])return{prefix:t,iconName:e,icon:n[t][e]}}var Pr=function(t,e){return function(a,i,r,o){return t.call(e,a,i,r,o)}},An=function(t,e,a,i){var r=Object.keys(t),o=r.length,s=i!==void 0?Pr(e,i):e,f,u,d;for(a===void 0?(f=1,d=t[r[0]]):(f=0,d=a);f<o;f++)u=r[f],d=s(d,t[u],u,t);return d};function jt(n){return P(n).length!==1?null:n.codePointAt(0).toString(16)}function Ce(n){return Object.keys(n).reduce(function(t,e){var a=n[e],i=!!a.icon;return i?t[a.iconName]=a.icon:t[e]=a,t},{})}function On(n,t){var e=arguments.length>2&&arguments[2]!==void 0?arguments[2]:{},a=e.skipHooks,i=a===void 0?!1:a,r=Ce(t);typeof C.hooks.addPack=="function"&&!i?C.hooks.addPack(n,Ce(t)):C.styles[n]=l(l({},C.styles[n]||{}),r),n==="fas"&&On("fa",t)}var K=C.styles,Fr=C.shims,Tt=Object.keys(Vn),Nr=Tt.reduce(function(n,t){return n[t]=Object.keys(Vn[t]),n},{}),qn=null,$t={},_t={},Lt={},Rt={},Wt={};function Er(n){return~vr.indexOf(n)}function Dr(n,t){var e=t.split("-"),a=e[0],i=e.slice(1).join("-");return a===n&&i!==""&&!Er(i)?i:null}var Ht=function(){var t=function(r){return An(K,function(o,s,f){return o[f]=An(s,r,{}),o},{})};$t=t(function(i,r,o){if(r[3]&&(i[r[3]]=o),r[2]){var s=r[2].filter(function(f){return typeof f=="number"});s.forEach(function(f){i[f.toString(16)]=o})}return i}),_t=t(function(i,r,o){if(i[o]=o,r[2]){var s=r[2].filter(function(f){return typeof f=="string"});s.forEach(function(f){i[f]=o})}return i}),Wt=t(function(i,r,o){var s=r[2];return i[o]=o,s.forEach(function(f){i[f]=o}),i});var e="far"in K||m.autoFetchSvg,a=An(Fr,function(i,r){var o=r[0],s=r[1],f=r[2];return s==="far"&&!e&&(s="fas"),typeof o=="string"&&(i.names[o]={prefix:s,iconName:f}),typeof o=="number"&&(i.unicodes[o.toString(16)]={prefix:s,iconName:f}),i},{names:{},unicodes:{}});Lt=a.names,Rt=a.unicodes,qn=gn(m.styleDefault,{family:m.familyDefault})};yr(function(n){qn=gn(n.styleDefault,{family:m.familyDefault})});Ht();function Kn(n,t){return($t[n]||{})[t]}function Mr(n,t){return(_t[n]||{})[t]}function L(n,t){return(Wt[n]||{})[t]}function Ut(n){return Lt[n]||{prefix:null,iconName:null}}function Or(n){var t=Rt[n],e=Kn("fas",n);return t||(e?{prefix:"fas",iconName:e}:null)||{prefix:null,iconName:null}}function T(){return qn}var Yt=function(){return{prefix:null,iconName:null,rest:[]}};function jr(n){var t=w,e=Tt.reduce(function(a,i){return a[i]="".concat(m.cssPrefix,"-").concat(i),a},{});return xt.forEach(function(a){(n.includes(e[a])||n.some(function(i){return Nr[a].includes(i)}))&&(t=a)}),t}function gn(n){var t=arguments.length>1&&arguments[1]!==void 0?arguments[1]:{},e=t.family,a=e===void 0?w:e,i=cr[a][n];if(a===J&&!n)return"fad";var r=Se[a][n]||Se[a][i],o=n in C.styles?n:null,s=r||o||null;return s}function Tr(n){var t=[],e=null;return n.forEach(function(a){var i=Dr(m.cssPrefix,a);i?e=i:a&&t.push(a)}),{iconName:e,rest:t}}function Pe(n){return n.sort().filter(function(t,e,a){return a.indexOf(t)===e})}var Fe=St.concat(wt);function pn(n){var t=arguments.length>1&&arguments[1]!==void 0?arguments[1]:{},e=t.skipLookups,a=e===void 0?!1:e,i=null,r=Pe(n.filter(function(p){return Fe.includes(p)})),o=Pe(n.filter(function(p){return!Fe.includes(p)})),s=r.filter(function(p){return i=p,!Je.includes(p)}),f=dn(s,1),u=f[0],d=u===void 0?null:u,c=jr(r),v=l(l({},Tr(o)),{},{prefix:gn(d,{family:c})});return l(l(l({},v),Rr({values:n,family:c,styles:K,config:m,canonical:v,givenPrefix:i})),$r(a,i,v))}function $r(n,t,e){var a=e.prefix,i=e.iconName;if(n||!a||!i)return{prefix:a,iconName:i};var r=t==="fa"?Ut(i):{},o=L(a,i);return i=r.iconName||o||i,a=r.prefix||a,a==="far"&&!K.far&&K.fas&&!m.autoFetchSvg&&(a="fas"),{prefix:a,iconName:i}}var _r=xt.filter(function(n){return n!==w||n!==J}),Lr=Object.keys(Pn).filter(function(n){return n!==w}).map(function(n){return Object.keys(Pn[n])}).flat();function Rr(n){var t=n.values,e=n.family,a=n.canonical,i=n.givenPrefix,r=i===void 0?"":i,o=n.styles,s=o===void 0?{}:o,f=n.config,u=f===void 0?{}:f,d=e===J,c=t.includes("fa-duotone")||t.includes("fad"),v=u.familyDefault==="duotone",p=a.prefix==="fad"||a.prefix==="fa-duotone";if(!d&&(c||v||p)&&(a.prefix="fad"),(t.includes("fa-brands")||t.includes("fab"))&&(a.prefix="fab"),!a.prefix&&_r.includes(e)){var y=Object.keys(s).find(function(S){return Lr.includes(S)});if(y||u.autoFetchSvg){var b=Xa.get(e).defaultShortPrefixId;a.prefix=b,a.iconName=L(a.prefix,a.iconName)||a.iconName}}return(a.prefix==="fa"||r==="fa")&&(a.prefix=T()||"fas"),a}var Wr=(function(){function n(){fa(this,n),this.definitions={}}return la(n,[{key:"add",value:function(){for(var e=this,a=arguments.length,i=new Array(a),r=0;r<a;r++)i[r]=arguments[r];var o=i.reduce(this._pullDefinitions,{});Object.keys(o).forEach(function(s){e.definitions[s]=l(l({},e.definitions[s]||{}),o[s]),On(s,o[s]);var f=Vn[w][s];f&&On(f,o[s]),Ht()})}},{key:"reset",value:function(){this.definitions={}}},{key:"_pullDefinitions",value:function(e,a){var i=a.prefix&&a.iconName&&a.icon?{0:a}:a;return Object.keys(i).map(function(r){var o=i[r],s=o.prefix,f=o.iconName,u=o.icon,d=u[2];e[s]||(e[s]={}),d.length>0&&d.forEach(function(c){typeof c=="string"&&(e[s][c]=u)}),e[s][f]=u}),e}}])})(),Ne=[],U={},Y={},Hr=Object.keys(Y);function Ur(n,t){var e=t.mixoutsTo;return Ne=n,U={},Object.keys(Y).forEach(function(a){Hr.indexOf(a)===-1&&delete Y[a]}),Ne.forEach(function(a){var i=a.mixout?a.mixout():{};if(Object.keys(i).forEach(function(o){typeof i[o]=="function"&&(e[o]=i[o]),ln(i[o])==="object"&&Object.keys(i[o]).forEach(function(s){e[o]||(e[o]={}),e[o][s]=i[o][s]})}),a.hooks){var r=a.hooks();Object.keys(r).forEach(function(o){U[o]||(U[o]=[]),U[o].push(r[o])})}a.provides&&a.provides(Y)}),e}function jn(n,t){for(var e=arguments.length,a=new Array(e>2?e-2:0),i=2;i<e;i++)a[i-2]=arguments[i];var r=U[n]||[];return r.forEach(function(o){t=o.apply(null,[t].concat(a))}),t}function W(n){for(var t=arguments.length,e=new Array(t>1?t-1:0),a=1;a<t;a++)e[a-1]=arguments[a];var i=U[n]||[];i.forEach(function(r){r.apply(null,e)})}function $(){var n=arguments[0],t=Array.prototype.slice.call(arguments,1);return Y[n]?Y[n].apply(null,t):void 0}function Tn(n){n.prefix==="fa"&&(n.prefix="fas");var t=n.iconName,e=n.prefix||T();if(t)return t=L(e,t)||t,ze(Xt.definitions,e,t)||ze(C.styles,e,t)}var Xt=new Wr,Yr=function(){m.autoReplaceSvg=!1,m.observeMutations=!1,W("noAuto")},Xr={i2svg:function(){var t=arguments.length>0&&arguments[0]!==void 0?arguments[0]:{};return M?(W("beforeI2svg",t),$("pseudoElements2svg",t),$("i2svg",t)):Promise.reject(new Error("Operation requires a DOM of some kind."))},watch:function(){var t=arguments.length>0&&arguments[0]!==void 0?arguments[0]:{},e=t.autoReplaceSvgRoot;m.autoReplaceSvg===!1&&(m.autoReplaceSvg=!0),m.observeMutations=!0,Cr(function(){Br({autoReplaceSvgRoot:e}),W("watch",t)})}},Vr={icon:function(t){if(t===null)return null;if(ln(t)==="object"&&t.prefix&&t.iconName)return{prefix:t.prefix,iconName:L(t.prefix,t.iconName)||t.iconName};if(Array.isArray(t)&&t.length===2){var e=t[1].indexOf("fa-")===0?t[1].slice(3):t[1],a=gn(t[0]);return{prefix:a,iconName:L(a,e)||e}}if(typeof t=="string"&&(t.indexOf("".concat(m.cssPrefix,"-"))>-1||t.match(dr))){var i=pn(t.split(" "),{skipLookups:!0});return{prefix:i.prefix||T(),iconName:L(i.prefix,i.iconName)||i.iconName}}if(typeof t=="string"){var r=T();return{prefix:r,iconName:L(r,t)||t}}}},I={noAuto:Yr,config:m,dom:Xr,parse:Vr,library:Xt,findIconDefinition:Tn,toHtml:Z},Br=function(){var t=arguments.length>0&&arguments[0]!==void 0?arguments[0]:{},e=t.autoReplaceSvgRoot,a=e===void 0?h:e;(Object.keys(C.styles).length>0||m.autoFetchSvg)&&M&&m.autoReplaceSvg&&I.dom.i2svg({node:a})};function vn(n,t){return Object.defineProperty(n,"abstract",{get:t}),Object.defineProperty(n,"html",{get:function(){return n.abstract.map(function(a){return Z(a)})}}),Object.defineProperty(n,"node",{get:function(){if(M){var a=h.createElement("div");return a.innerHTML=n.html,a.children}}}),n}function Gr(n){var t=n.children,e=n.main,a=n.mask,i=n.attributes,r=n.styles,o=n.transform;if(Gn(o)&&e.found&&!a.found){var s=e.width,f=e.height,u={x:s/f/2,y:.5};i.style=mn(l(l({},r),{},{"transform-origin":"".concat(u.x+o.x/16,"em ").concat(u.y+o.y/16,"em")}))}return[{tag:"svg",attributes:i,children:t}]}function qr(n){var t=n.prefix,e=n.iconName,a=n.children,i=n.attributes,r=n.symbol,o=r===!0?"".concat(t,"-").concat(m.cssPrefix,"-").concat(e):r;return[{tag:"svg",attributes:{style:"display: none;"},children:[{tag:"symbol",attributes:l(l({},i),{},{id:o}),children:a}]}]}function Kr(n){var t=["aria-label","aria-labelledby","title","role"];return t.some(function(e){return e in n})}function Jn(n){var t=n.icons,e=t.main,a=t.mask,i=n.prefix,r=n.iconName,o=n.transform,s=n.symbol,f=n.maskId,u=n.extra,d=n.watchable,c=d===void 0?!1:d,v=a.found?a:e,p=v.width,y=v.height,b=[m.replacementClass,r?"".concat(m.cssPrefix,"-").concat(r):""].filter(function(N){return u.classes.indexOf(N)===-1}).filter(function(N){return N!==""||!!N}).concat(u.classes).join(" "),S={children:[],attributes:l(l({},u.attributes),{},{"data-prefix":i,"data-icon":r,class:b,role:u.attributes.role||"img",viewBox:"0 0 ".concat(p," ").concat(y)})};!Kr(u.attributes)&&!u.attributes["aria-hidden"]&&(S.attributes["aria-hidden"]="true"),c&&(S.attributes[R]="");var x=l(l({},S),{},{prefix:i,iconName:r,main:e,mask:a,maskId:f,transform:o,symbol:s,styles:l({},u.styles)}),A=a.found&&e.found?$("generateAbstractMask",x)||{children:[],attributes:{}}:$("generateAbstractIcon",x)||{children:[],attributes:{}},z=A.children,H=A.attributes;return x.children=z,x.attributes=H,s?qr(x):Gr(x)}function Ee(n){var t=n.content,e=n.width,a=n.height,i=n.transform,r=n.extra,o=n.watchable,s=o===void 0?!1:o,f=l(l({},r.attributes),{},{class:r.classes.join(" ")});s&&(f[R]="");var u=l({},r.styles);Gn(i)&&(u.transform=Ar({transform:i,startCentered:!0,width:e,height:a}),u["-webkit-transform"]=u.transform);var d=mn(u);d.length>0&&(f.style=d);var c=[];return c.push({tag:"span",attributes:f,children:[t]}),c}function Jr(n){var t=n.content,e=n.extra,a=l(l({},e.attributes),{},{class:e.classes.join(" ")}),i=mn(e.styles);i.length>0&&(a.style=i);var r=[];return r.push({tag:"span",attributes:a,children:[t]}),r}var In=C.styles;function $n(n){var t=n[0],e=n[1],a=n.slice(4),i=dn(a,1),r=i[0],o=null;return Array.isArray(r)?o={tag:"g",attributes:{class:"".concat(m.cssPrefix,"-").concat(Sn.GROUP)},children:[{tag:"path",attributes:{class:"".concat(m.cssPrefix,"-").concat(Sn.SECONDARY),fill:"currentColor",d:r[0]}},{tag:"path",attributes:{class:"".concat(m.cssPrefix,"-").concat(Sn.PRIMARY),fill:"currentColor",d:r[1]}}]}:o={tag:"path",attributes:{fill:"currentColor",d:r}},{found:!0,width:t,height:e,icon:o}}var Qr={found:!1,width:512,height:512};function Zr(n,t){!Ct&&!m.showMissingIcons&&n&&console.error('Icon with name "'.concat(n,'" and prefix "').concat(t,'" is missing.'))}function _n(n,t){var e=t;return t==="fa"&&m.styleDefault!==null&&(t=T()),new Promise(function(a,i){if(e==="fa"){var r=Ut(n)||{};n=r.iconName||n,t=r.prefix||t}if(n&&t&&In[t]&&In[t][n]){var o=In[t][n];return a($n(o))}Zr(n,t),a(l(l({},Qr),{},{icon:m.showMissingIcons&&n?$("missingIconAbstract")||{}:{}}))})}var De=function(){},Ln=m.measurePerformance&&en&&en.mark&&en.measure?en:{mark:De,measure:De},B='FA "7.3.0"',no=function(t){return Ln.mark("".concat(B," ").concat(t," begins")),function(){return Vt(t)}},Vt=function(t){Ln.mark("".concat(B," ").concat(t," ends")),Ln.measure("".concat(B," ").concat(t),"".concat(B," ").concat(t," begins"),"".concat(B," ").concat(t," ends"))},Qn={begin:no,end:Vt},sn=function(){};function Me(n){var t=n.getAttribute?n.getAttribute(R):null;return typeof t=="string"}function eo(n){var t=n.getAttribute?n.getAttribute(Yn):null,e=n.getAttribute?n.getAttribute(Xn):null;return t&&e}function to(n){return n&&n.classList&&n.classList.contains&&n.classList.contains(m.replacementClass)}function ao(){if(m.autoReplaceSvg===!0)return fn.replace;var n=fn[m.autoReplaceSvg];return n||fn.replace}function io(n){return h.createElementNS("http://www.w3.org/2000/svg",n)}function ro(n){return h.createElement(n)}function Bt(n){var t=arguments.length>1&&arguments[1]!==void 0?arguments[1]:{},e=t.ceFn,a=e===void 0?n.tag==="svg"?io:ro:e;if(typeof n=="string")return h.createTextNode(n);var i=a(n.tag);Object.keys(n.attributes||[]).forEach(function(o){i.setAttribute(o,n.attributes[o])});var r=n.children||[];return r.forEach(function(o){i.appendChild(Bt(o,{ceFn:a}))}),i}function oo(n){var t=" ".concat(n.outerHTML," ");return t="".concat(t,"Font Awesome fontawesome.com "),t}var fn={replace:function(t){var e=t[0];if(e.parentNode)if(t[1].forEach(function(i){e.parentNode.insertBefore(Bt(i),e)}),e.getAttribute(R)===null&&m.keepOriginalSource){var a=h.createComment(oo(e));e.parentNode.replaceChild(a,e)}else e.remove()},nest:function(t){var e=t[0],a=t[1];if(~Bn(e).indexOf(m.replacementClass))return fn.replace(t);var i=new RegExp("".concat(m.cssPrefix,"-.*"));if(delete a[0].attributes.id,a[0].attributes.class){var r=a[0].attributes.class.split(" ").reduce(function(s,f){return f===m.replacementClass||f.match(i)?s.toSvg.push(f):s.toNode.push(f),s},{toNode:[],toSvg:[]});a[0].attributes.class=r.toSvg.join(" "),r.toNode.length===0?e.removeAttribute("class"):e.setAttribute("class",r.toNode.join(" "))}var o=a.map(function(s){return Z(s)}).join(`
`);e.setAttribute(R,""),e.innerHTML=o}};function Oe(n){n()}function Gt(n,t){var e=typeof t=="function"?t:sn;if(n.length===0)e();else{var a=Oe;m.mutateApproach===lr&&(a=j.requestAnimationFrame||Oe),a(function(){var i=ao(),r=Qn.begin("mutate");n.map(i),r(),e()})}}var Zn=!1;function qt(){Zn=!0}function Rn(){Zn=!1}var cn=null;function je(n){if(be&&m.observeMutations){var t=n.treeCallback,e=t===void 0?sn:t,a=n.nodeCallback,i=a===void 0?sn:a,r=n.pseudoElementsCallback,o=r===void 0?sn:r,s=n.observeMutationsRoot,f=s===void 0?h:s;cn=new be(function(u){if(!Zn){var d=T();V(u).forEach(function(c){if(c.type==="childList"&&c.addedNodes.length>0&&!Me(c.addedNodes[0])&&(m.searchPseudoElements&&o(c.target),e(c.target)),c.type==="attributes"&&c.target.parentNode&&m.searchPseudoElements&&o([c.target],!0),c.type==="attributes"&&Me(c.target)&&~pr.indexOf(c.attributeName))if(c.attributeName==="class"&&eo(c.target)){var v=pn(Bn(c.target)),p=v.prefix,y=v.iconName;c.target.setAttribute(Yn,p||d),y&&c.target.setAttribute(Xn,y)}else to(c.target)&&i(c.target)})}}),M&&cn.observe(f,{childList:!0,attributes:!0,characterData:!0,subtree:!0})}}function so(){cn&&cn.disconnect()}function fo(n){var t=n.getAttribute("style"),e=[];return t&&(e=t.split(";").reduce(function(a,i){var r=i.split(":"),o=r[0],s=r.slice(1);return o&&s.length>0&&(a[o]=s.join(":").trim()),a},{})),e}function lo(n){var t=n.getAttribute("data-prefix"),e=n.getAttribute("data-icon"),a=n.innerText!==void 0?n.innerText.trim():"",i=pn(Bn(n));return i.prefix||(i.prefix=T()),t&&e&&(i.prefix=t,i.iconName=e),i.iconName&&i.prefix||(i.prefix&&a.length>0&&(i.iconName=Mr(i.prefix,n.innerText)||Kn(i.prefix,jt(n.innerText))),!i.iconName&&m.autoFetchSvg&&n.firstChild&&n.firstChild.nodeType===Node.TEXT_NODE&&(i.iconName=n.firstChild.data)),i}function uo(n){var t=V(n.attributes).reduce(function(e,a){return e.name!=="class"&&e.name!=="style"&&(e[a.name]=a.value),e},{});return t}function co(){return{iconName:null,prefix:null,transform:F,symbol:!1,mask:{iconName:null,prefix:null,rest:[]},maskId:null,extra:{classes:[],styles:{},attributes:{}}}}function Te(n){var t=arguments.length>1&&arguments[1]!==void 0?arguments[1]:{styleParser:!0},e=lo(n),a=e.iconName,i=e.prefix,r=e.rest,o=uo(n),s=jn("parseNodeAttributes",{},n),f=t.styleParser?fo(n):[];return l({iconName:a,prefix:i,transform:F,mask:{iconName:null,prefix:null,rest:[]},maskId:null,symbol:!1,extra:{classes:r,styles:f,attributes:o}},s)}var mo=C.styles;function Kt(n){var t=m.autoReplaceSvg==="nest"?Te(n,{styleParser:!1}):Te(n);return~t.extra.classes.indexOf(Ft)?$("generateLayersText",n,t):$("generateSvgReplacementMutation",n,t)}function go(){return[].concat(P(wt),P(St))}function $e(n){var t=arguments.length>1&&arguments[1]!==void 0?arguments[1]:null;if(!M)return Promise.resolve();var e=h.documentElement.classList,a=function(c){return e.add("".concat(we,"-").concat(c))},i=function(c){return e.remove("".concat(we,"-").concat(c))},r=m.autoFetchSvg?go():Je.concat(Object.keys(mo));r.includes("fa")||r.push("fa");var o=[".".concat(Ft,":not([").concat(R,"])")].concat(r.map(function(d){return".".concat(d,":not([").concat(R,"])")})).join(", ");if(o.length===0)return Promise.resolve();var s=[];try{s=V(n.querySelectorAll(o))}catch(d){}if(s.length>0)a("pending"),i("complete");else return Promise.resolve();var f=Qn.begin("onTree"),u=s.reduce(function(d,c){try{var v=Kt(c);v&&d.push(v)}catch(p){Ct||p.name==="MissingIcon"&&console.error(p)}return d},[]);return new Promise(function(d,c){Promise.all(u).then(function(v){Gt(v,function(){a("active"),a("complete"),i("pending"),typeof t=="function"&&t(),f(),d()})}).catch(function(v){f(),c(v)})})}function po(n){var t=arguments.length>1&&arguments[1]!==void 0?arguments[1]:null;Kt(n).then(function(e){e&&Gt([e],t)})}function vo(n){return function(t){var e=arguments.length>1&&arguments[1]!==void 0?arguments[1]:{},a=(t||{}).icon?t:Tn(t||{}),i=e.mask;return i&&(i=(i||{}).icon?i:Tn(i||{})),n(a,l(l({},e),{},{mask:i}))}}var ho=function(t){var e=arguments.length>1&&arguments[1]!==void 0?arguments[1]:{},a=e.transform,i=a===void 0?F:a,r=e.symbol,o=r===void 0?!1:r,s=e.mask,f=s===void 0?null:s,u=e.maskId,d=u===void 0?null:u,c=e.classes,v=c===void 0?[]:c,p=e.attributes,y=p===void 0?{}:p,b=e.styles,S=b===void 0?{}:b;if(t){var x=t.prefix,A=t.iconName,z=t.icon;return vn(l({type:"icon"},t),function(){return W("beforeDOMElementCreation",{iconDefinition:t,params:e}),Jn({icons:{main:$n(z),mask:f?$n(f.icon):{found:!1,width:null,height:null,icon:{}}},prefix:x,iconName:A,transform:l(l({},F),i),symbol:o,maskId:d,extra:{attributes:y,styles:S,classes:v}})})}},bo={mixout:function(){return{icon:vo(ho)}},hooks:function(){return{mutationObserverCallbacks:function(e){return e.treeCallback=$e,e.nodeCallback=po,e}}},provides:function(t){t.i2svg=function(e){var a=e.node,i=a===void 0?h:a,r=e.callback,o=r===void 0?function(){}:r;return $e(i,o)},t.generateSvgReplacementMutation=function(e,a){var i=a.iconName,r=a.prefix,o=a.transform,s=a.symbol,f=a.mask,u=a.maskId,d=a.extra;return new Promise(function(c,v){Promise.all([_n(i,r),f.iconName?_n(f.iconName,f.prefix):Promise.resolve({found:!1,width:512,height:512,icon:{}})]).then(function(p){var y=dn(p,2),b=y[0],S=y[1];c([e,Jn({icons:{main:b,mask:S},prefix:r,iconName:i,transform:o,symbol:s,maskId:u,extra:d,watchable:!0})])}).catch(v)})},t.generateAbstractIcon=function(e){var a=e.children,i=e.attributes,r=e.main,o=e.transform,s=e.styles,f=mn(s);f.length>0&&(i.style=f);var u;return Gn(o)&&(u=$("generateAbstractTransformGrouping",{main:r,transform:o,containerWidth:r.width,iconWidth:r.width})),a.push(u||r.icon),{children:a,attributes:i}}}},yo={mixout:function(){return{layer:function(e){var a=arguments.length>1&&arguments[1]!==void 0?arguments[1]:{},i=a.classes,r=i===void 0?[]:i;return vn({type:"layer"},function(){W("beforeDOMElementCreation",{assembler:e,params:a});var o=[];return e(function(s){Array.isArray(s)?s.map(function(f){o=o.concat(f.abstract)}):o=o.concat(s.abstract)}),[{tag:"span",attributes:{class:["".concat(m.cssPrefix,"-layers")].concat(P(r)).join(" ")},children:o}]})}}}},xo={mixout:function(){return{counter:function(e){var a=arguments.length>1&&arguments[1]!==void 0?arguments[1]:{},i=a.title,r=i===void 0?null:i,o=a.classes,s=o===void 0?[]:o,f=a.attributes,u=f===void 0?{}:f,d=a.styles,c=d===void 0?{}:d;return vn({type:"counter",content:e},function(){return W("beforeDOMElementCreation",{content:e,params:a}),Jr({content:e.toString(),title:r,extra:{attributes:u,styles:c,classes:["".concat(m.cssPrefix,"-layers-counter")].concat(P(s))}})})}}}},wo={mixout:function(){return{text:function(e){var a=arguments.length>1&&arguments[1]!==void 0?arguments[1]:{},i=a.transform,r=i===void 0?F:i,o=a.classes,s=o===void 0?[]:o,f=a.attributes,u=f===void 0?{}:f,d=a.styles,c=d===void 0?{}:d;return vn({type:"text",content:e},function(){return W("beforeDOMElementCreation",{content:e,params:a}),Ee({content:e,transform:l(l({},F),r),extra:{attributes:u,styles:c,classes:["".concat(m.cssPrefix,"-layers-text")].concat(P(s))}})})}}},provides:function(t){t.generateLayersText=function(e,a){var i=a.transform,r=a.extra,o=null,s=null;if(qe){var f=parseInt(getComputedStyle(e).fontSize,10),u=e.getBoundingClientRect();o=u.width/f,s=u.height/f}return Promise.resolve([e,Ee({content:e.innerHTML,width:o,height:s,transform:i,extra:r,watchable:!0})])}}},Jt=new RegExp('"',"ug"),_e=[1105920,1112319],Le=l(l(l(l({},{FontAwesome:{normal:"fas",400:"fas"}}),Ya),sr),Za),Wn=Object.keys(Le).reduce(function(n,t){return n[t.toLowerCase()]=Le[t],n},{}),So=Object.keys(Wn).reduce(function(n,t){var e=Wn[t];return n[t]=e[900]||P(Object.entries(e))[0][1],n},{});function ko(n){var t=n.replace(Jt,"");return jt(P(t)[0]||"")}function Ao(n){var t=n.getPropertyValue("font-feature-settings").includes("ss01"),e=n.getPropertyValue("content"),a=e.replace(Jt,""),i=a.codePointAt(0),r=i>=_e[0]&&i<=_e[1],o=a.length===2?a[0]===a[1]:!1;return r||o||t}function Io(n,t){var e=n.replace(/^['"]|['"]$/g,"").toLowerCase(),a=parseInt(t),i=isNaN(a)?"normal":a;return(Wn[e]||{})[i]||So[e]}function Re(n,t){var e="".concat(fr).concat(t.replace(":","-"));return new Promise(function(a,i){if(n.getAttribute(e)!==null)return a();var r=V(n.children),o=r.filter(function(hn){return hn.getAttribute(Nn)===t})[0],s=j.getComputedStyle(n,t),f=s.getPropertyValue("font-family"),u=f.match(mr),d=s.getPropertyValue("font-weight"),c=s.getPropertyValue("content");if(o&&!u)return n.removeChild(o),a();if(u&&c!=="none"&&c!==""){var v=s.getPropertyValue("content"),p=Io(f,d),y=ko(v),b=u[0].startsWith("FontAwesome"),S=Ao(s),x=Kn(p,y),A=x;if(b){var z=Or(y);z.iconName&&z.prefix&&(x=z.iconName,p=z.prefix)}if(x&&!S&&(!o||o.getAttribute(Yn)!==p||o.getAttribute(Xn)!==A)){n.setAttribute(e,A),o&&n.removeChild(o);var H=co(),N=H.extra;N.attributes[Nn]=t,_n(x,p).then(function(hn){var ia=Jn(l(l({},H),{},{icons:{main:hn,mask:Yt()},prefix:p,iconName:A,extra:N,watchable:!0})),bn=h.createElementNS("http://www.w3.org/2000/svg","svg");t==="::before"?n.insertBefore(bn,n.firstChild):n.appendChild(bn),bn.outerHTML=ia.map(function(ra){return Z(ra)}).join(`
`),n.removeAttribute(e),a()}).catch(i)}else a()}else a()})}function zo(n){return Promise.all([Re(n,"::before"),Re(n,"::after")])}function Co(n){return n.parentNode!==document.head&&!~ur.indexOf(n.tagName.toUpperCase())&&!n.getAttribute(Nn)&&(!n.parentNode||n.parentNode.tagName!=="svg")}var Po=function(t){return!!t&&zt.some(function(e){return t.includes(e)})},Fo=function(t){if(!t)return[];var e=new Set,a=t.split(/,(?![^()]*\))/).map(function(f){return f.trim()});a=a.flatMap(function(f){return f.includes("(")?f:f.split(",").map(function(u){return u.trim()})});var i=on(a),r;try{for(i.s();!(r=i.n()).done;){var o=r.value;if(Po(o)){var s=zt.reduce(function(f,u){return f.replace(u,"")},o);s!==""&&s!=="*"&&e.add(s)}}}catch(f){i.e(f)}finally{i.f()}return e};function We(n){var t=arguments.length>1&&arguments[1]!==void 0?arguments[1]:!1;if(M){var e;if(t)e=n;else if(m.searchPseudoElementsFullScan)e=n.querySelectorAll("*");else{var a=new Set,i=on(document.styleSheets),r;try{for(i.s();!(r=i.n()).done;){var o=r.value;try{var s=on(o.cssRules),f;try{for(s.s();!(f=s.n()).done;){var u=f.value,d=Fo(u.selectorText),c=on(d),v;try{for(c.s();!(v=c.n()).done;){var p=v.value;a.add(p)}}catch(b){c.e(b)}finally{c.f()}}}catch(b){s.e(b)}finally{s.f()}}catch(b){m.searchPseudoElementsWarnings&&console.warn("Font Awesome: cannot parse stylesheet: ".concat(o.href," (").concat(b.message,`)
If it declares any Font Awesome CSS pseudo-elements, they will not be rendered as SVG icons. Add crossorigin="anonymous" to the <link>, enable searchPseudoElementsFullScan for slower but more thorough DOM parsing, or suppress this warning by setting searchPseudoElementsWarnings to false.`))}}}catch(b){i.e(b)}finally{i.f()}if(!a.size)return;var y=Array.from(a).join(", ");try{e=n.querySelectorAll(y)}catch(b){}}return new Promise(function(b,S){var x=V(e).filter(Co).map(zo),A=Qn.begin("searchPseudoElements");qt(),Promise.all(x).then(function(){A(),Rn(),b()}).catch(function(){A(),Rn(),S()})})}}var No={hooks:function(){return{mutationObserverCallbacks:function(e){return e.pseudoElementsCallback=We,e}}},provides:function(t){t.pseudoElements2svg=function(e){var a=e.node,i=a===void 0?h:a;m.searchPseudoElements&&We(i)}}},He=!1,Eo={mixout:function(){return{dom:{unwatch:function(){qt(),He=!0}}}},hooks:function(){return{bootstrap:function(){je(jn("mutationObserverCallbacks",{}))},noAuto:function(){so()},watch:function(e){var a=e.observeMutationsRoot;He?Rn():je(jn("mutationObserverCallbacks",{observeMutationsRoot:a}))}}}},Ue=function(t){var e={size:16,x:0,y:0,flipX:!1,flipY:!1,rotate:0};return t.toLowerCase().split(" ").reduce(function(a,i){var r=i.toLowerCase().split("-"),o=r[0],s=r.slice(1).join("-");if(o&&s==="h")return a.flipX=!0,a;if(o&&s==="v")return a.flipY=!0,a;if(s=parseFloat(s),isNaN(s))return a;switch(o){case"grow":a.size=a.size+s;break;case"shrink":a.size=a.size-s;break;case"left":a.x=a.x-s;break;case"right":a.x=a.x+s;break;case"up":a.y=a.y-s;break;case"down":a.y=a.y+s;break;case"rotate":a.rotate=a.rotate+s;break}return a},e)},Do={mixout:function(){return{parse:{transform:function(e){return Ue(e)}}}},hooks:function(){return{parseNodeAttributes:function(e,a){var i=a.getAttribute("data-fa-transform");return i&&(e.transform=Ue(i)),e}}},provides:function(t){t.generateAbstractTransformGrouping=function(e){var a=e.main,i=e.transform,r=e.containerWidth,o=e.iconWidth,s={transform:"translate(".concat(r/2," 256)")},f="translate(".concat(i.x*32,", ").concat(i.y*32,") "),u="scale(".concat(i.size/16*(i.flipX?-1:1),", ").concat(i.size/16*(i.flipY?-1:1),") "),d="rotate(".concat(i.rotate," 0 0)"),c={transform:"".concat(f," ").concat(u," ").concat(d)},v={transform:"translate(".concat(o/2*-1," -256)")},p={outer:s,inner:c,path:v};return{tag:"g",attributes:l({},p.outer),children:[{tag:"g",attributes:l({},p.inner),children:[{tag:a.icon.tag,children:a.icon.children,attributes:l(l({},a.icon.attributes),p.path)}]}]}}}},zn={x:0,y:0,width:"100%",height:"100%"};function Ye(n){var t=arguments.length>1&&arguments[1]!==void 0?arguments[1]:!0;return n.attributes&&(n.attributes.fill||t)&&(n.attributes.fill="black"),n}function Mo(n){return n.tag==="g"?n.children:[n]}var Oo={hooks:function(){return{parseNodeAttributes:function(e,a){var i=a.getAttribute("data-fa-mask"),r=i?pn(i.split(" ").map(function(o){return o.trim()})):Yt();return r.prefix||(r.prefix=T()),e.mask=r,e.maskId=a.getAttribute("data-fa-mask-id"),e}}},provides:function(t){t.generateAbstractMask=function(e){var a=e.children,i=e.attributes,r=e.main,o=e.mask,s=e.maskId,f=e.transform,u=r.width,d=r.icon,c=o.width,v=o.icon,p=kr({transform:f,containerWidth:c,iconWidth:u}),y={tag:"rect",attributes:l(l({},zn),{},{fill:"white"})},b=d.children?{children:d.children.map(Ye)}:{},S={tag:"g",attributes:l({},p.inner),children:[Ye(l({tag:d.tag,attributes:l(l({},d.attributes),p.path)},b))]},x={tag:"g",attributes:l({},p.outer),children:[S]},A="mask-".concat(s||Ae()),z="clip-".concat(s||Ae()),H={tag:"mask",attributes:l(l({},zn),{},{id:A,maskUnits:"userSpaceOnUse",maskContentUnits:"userSpaceOnUse"}),children:[y,x]},N={tag:"defs",children:[{tag:"clipPath",attributes:{id:z},children:Mo(v)},H]};return a.push(N,{tag:"rect",attributes:l({fill:"currentColor","clip-path":"url(#".concat(z,")"),mask:"url(#".concat(A,")")},zn)}),{children:a,attributes:i}}}},jo={provides:function(t){var e=!1;j.matchMedia&&(e=j.matchMedia("(prefers-reduced-motion: reduce)").matches),t.missingIconAbstract=function(){var a=[],i={fill:"currentColor"},r={attributeType:"XML",repeatCount:"indefinite",dur:"2s"};a.push({tag:"path",attributes:l(l({},i),{},{d:"M156.5,447.7l-12.6,29.5c-18.7-9.5-35.9-21.2-51.5-34.9l22.7-22.7C127.6,430.5,141.5,440,156.5,447.7z M40.6,272H8.5 c1.4,21.2,5.4,41.7,11.7,61.1L50,321.2C45.1,305.5,41.8,289,40.6,272z M40.6,240c1.4-18.8,5.2-37,11.1-54.1l-29.5-12.6 C14.7,194.3,10,216.7,8.5,240H40.6z M64.3,156.5c7.8-14.9,17.2-28.8,28.1-41.5L69.7,92.3c-13.7,15.6-25.5,32.8-34.9,51.5 L64.3,156.5z M397,419.6c-13.9,12-29.4,22.3-46.1,30.4l11.9,29.8c20.7-9.9,39.8-22.6,56.9-37.6L397,419.6z M115,92.4 c13.9-12,29.4-22.3,46.1-30.4l-11.9-29.8c-20.7,9.9-39.8,22.6-56.8,37.6L115,92.4z M447.7,355.5c-7.8,14.9-17.2,28.8-28.1,41.5 l22.7,22.7c13.7-15.6,25.5-32.9,34.9-51.5L447.7,355.5z M471.4,272c-1.4,18.8-5.2,37-11.1,54.1l29.5,12.6 c7.5-21.1,12.2-43.5,13.6-66.8H471.4z M321.2,462c-15.7,5-32.2,8.2-49.2,9.4v32.1c21.2-1.4,41.7-5.4,61.1-11.7L321.2,462z M240,471.4c-18.8-1.4-37-5.2-54.1-11.1l-12.6,29.5c21.1,7.5,43.5,12.2,66.8,13.6V471.4z M462,190.8c5,15.7,8.2,32.2,9.4,49.2h32.1 c-1.4-21.2-5.4-41.7-11.7-61.1L462,190.8z M92.4,397c-12-13.9-22.3-29.4-30.4-46.1l-29.8,11.9c9.9,20.7,22.6,39.8,37.6,56.9 L92.4,397z M272,40.6c18.8,1.4,36.9,5.2,54.1,11.1l12.6-29.5C317.7,14.7,295.3,10,272,8.5V40.6z M190.8,50 c15.7-5,32.2-8.2,49.2-9.4V8.5c-21.2,1.4-41.7,5.4-61.1,11.7L190.8,50z M442.3,92.3L419.6,115c12,13.9,22.3,29.4,30.5,46.1 l29.8-11.9C470,128.5,457.3,109.4,442.3,92.3z M397,92.4l22.7-22.7c-15.6-13.7-32.8-25.5-51.5-34.9l-12.6,29.5 C370.4,72.1,384.4,81.5,397,92.4z"})});var o=l(l({},r),{},{attributeName:"opacity"}),s={tag:"circle",attributes:l(l({},i),{},{cx:"256",cy:"364",r:"28"}),children:[]};return e||s.children.push({tag:"animate",attributes:l(l({},r),{},{attributeName:"r",values:"28;14;28;28;14;28;"})},{tag:"animate",attributes:l(l({},o),{},{values:"1;0;1;1;0;1;"})}),a.push(s),a.push({tag:"path",attributes:l(l({},i),{},{opacity:"1",d:"M263.7,312h-16c-6.6,0-12-5.4-12-12c0-71,77.4-63.9,77.4-107.8c0-20-17.8-40.2-57.4-40.2c-29.1,0-44.3,9.6-59.2,28.7 c-3.9,5-11.1,6-16.2,2.4l-13.1-9.2c-5.6-3.9-6.9-11.8-2.6-17.2c21.2-27.2,46.4-44.7,91.2-44.7c52.3,0,97.4,29.8,97.4,80.2 c0,67.6-77.4,63.5-77.4,107.8C275.7,306.6,270.3,312,263.7,312z"}),children:e?[]:[{tag:"animate",attributes:l(l({},o),{},{values:"1;0;0;0;0;1;"})}]}),e||a.push({tag:"path",attributes:l(l({},i),{},{opacity:"0",d:"M232.5,134.5l7,168c0.3,6.4,5.6,11.5,12,11.5h9c6.4,0,11.7-5.1,12-11.5l7-168c0.3-6.8-5.2-12.5-12-12.5h-23 C237.7,122,232.2,127.7,232.5,134.5z"}),children:[{tag:"animate",attributes:l(l({},o),{},{values:"0;0;1;1;0;0;"})}]}),{tag:"g",attributes:{class:"missing"},children:a}}}},To={hooks:function(){return{parseNodeAttributes:function(e,a){var i=a.getAttribute("data-fa-symbol"),r=i===null?!1:i===""?!0:i;return e.symbol=r,e}}}},$o=[zr,bo,yo,xo,wo,No,Eo,Do,Oo,jo,To];Ur($o,{mixoutsTo:I});var is=I.noAuto,Qt=I.config,rs=I.library,Zt=I.dom,na=I.parse,os=I.findIconDefinition,ss=I.toHtml,ea=I.icon,fs=I.layer,_o=I.text,Lo=I.counter;var Ro=["*"],Wo=(()=>{class n{defaultPrefix="fas";fallbackIcon=null;fixedWidth;set autoAddCss(e){Qt.autoAddCss=e,this._autoAddCss=e}get autoAddCss(){return this._autoAddCss}_autoAddCss=!0;static \u0275fac=function(a){return new(a||n)};static \u0275prov=yn({token:n,factory:n.\u0275fac,providedIn:"root"})}return n})(),Ho=(()=>{class n{definitions={};addIcons(...e){for(let a of e){a.prefix in this.definitions||(this.definitions[a.prefix]={}),this.definitions[a.prefix][a.iconName]=a;for(let i of a.icon[2])typeof i=="string"&&(this.definitions[a.prefix][i]=a)}}addIconPacks(...e){for(let a of e){let i=Object.keys(a).map(r=>a[r]);this.addIcons(...i)}}getIconDefinition(e,a){return e in this.definitions&&a in this.definitions[e]?this.definitions[e][a]:null}static \u0275fac=function(a){return new(a||n)};static \u0275prov=yn({token:n,factory:n.\u0275fac,providedIn:"root"})}return n})(),Uo=n=>{throw new Error(`Could not find icon with iconName=${n.iconName} and prefix=${n.prefix} in the icon library.`)},Yo=()=>{throw new Error("Property `icon` is required for `fa-icon`/`fa-duotone-icon` components.")},aa=n=>n!=null&&(n===90||n===180||n===270||n==="90"||n==="180"||n==="270"),Xo=n=>{let t=aa(n.rotate),e={[`fa-${n.animation}`]:n.animation!=null&&!n.animation.startsWith("spin"),"fa-spin":n.animation==="spin"||n.animation==="spin-reverse","fa-spin-pulse":n.animation==="spin-pulse"||n.animation==="spin-pulse-reverse","fa-spin-reverse":n.animation==="spin-reverse"||n.animation==="spin-pulse-reverse","fa-pulse":n.animation==="spin-pulse"||n.animation==="spin-pulse-reverse","fa-fw":n.fixedWidth,"fa-border":n.border,"fa-inverse":n.inverse,"fa-layers-counter":n.counter,"fa-flip-horizontal":n.flip==="horizontal"||n.flip==="both","fa-flip-vertical":n.flip==="vertical"||n.flip==="both",[`fa-${n.size}`]:n.size!==null,[`fa-rotate-${n.rotate}`]:t,"fa-rotate-by":n.rotate!=null&&!t,[`fa-pull-${n.pull}`]:n.pull!==null,[`fa-stack-${n.stackItemSize}`]:n.stackItemSize!=null};return Object.keys(e).map(a=>e[a]?a:null).filter(a=>a!=null)},ne=new WeakSet,ta="fa-auto-css";function Vo(n,t){if(!t.autoAddCss||ne.has(n))return;if(n.getElementById(ta)!=null){t.autoAddCss=!1,ne.add(n);return}let e=n.createElement("style");e.setAttribute("type","text/css"),e.setAttribute("id",ta),e.innerHTML=Zt.css();let a=n.head.childNodes,i=null;for(let r=a.length-1;r>-1;r--){let o=a[r],s=o.nodeName.toUpperCase();["STYLE","LINK"].indexOf(s)>-1&&(i=o)}n.head.insertBefore(e,i),t.autoAddCss=!1,ne.add(n)}var Bo=n=>n.prefix!==void 0&&n.iconName!==void 0,Go=(n,t)=>Bo(n)?n:Array.isArray(n)&&n.length===2?{prefix:n[0],iconName:n[1]}:{prefix:t,iconName:n},qo=(()=>{class n{stackItemSize=nn("1x");size=nn();_effect=ie(()=>{if(this.size())throw new Error('fa-icon is not allowed to customize size when used inside fa-stack. Set size on the enclosing fa-stack instead: <fa-stack size="4x">...</fa-stack>.')});static \u0275fac=function(a){return new(a||n)};static \u0275dir=oe({type:n,selectors:[["fa-icon","stackItemSize",""],["fa-duotone-icon","stackItemSize",""]],inputs:{stackItemSize:[1,"stackItemSize"],size:[1,"size"]}})}return n})(),Ko=(()=>{class n{size=nn();classes=wn(()=>{let e=this.size(),a=e?{[`fa-${e}`]:!0}:{};return te(ee({},a),{"fa-stack":!0})});static \u0275fac=function(a){return new(a||n)};static \u0275cmp=xn({type:n,selectors:[["fa-stack"]],hostVars:2,hostBindings:function(a,i){a&2&&ce(i.classes())},inputs:{size:[1,"size"]},ngContentSelectors:Ro,decls:1,vars:0,template:function(a,i){a&1&&(le(),ue(0))},encapsulation:2,changeDetection:0})}return n})(),ks=(()=>{class n{icon=k();title=k();animation=k();mask=k();flip=k();size=k();pull=k();border=k();inverse=k();symbol=k();rotate=k();fixedWidth=k();transform=k();a11yRole=k();renderedIconHTML=wn(()=>{let e=this.icon()??this.config.fallbackIcon;if(!e)return Yo(),"";let a=this.findIconDefinition(e);if(!a)return"";let i=this.buildParams();Vo(this.document,this.config);let r=ea(a,i);return this.sanitizer.bypassSecurityTrustHtml(r.html.join(`
`))});document=_(ae);sanitizer=_(de);config=_(Wo);iconLibrary=_(Ho);stackItem=_(qo,{optional:!0});stack=_(Ko,{optional:!0});constructor(){this.stack!=null&&this.stackItem==null&&console.error('FontAwesome: fa-icon and fa-duotone-icon elements must specify stackItemSize attribute when wrapped into fa-stack. Example: <fa-icon stackItemSize="2x" />.')}findIconDefinition(e){let a=Go(e,this.config.defaultPrefix);if("icon"in a)return a;let i=this.iconLibrary.getIconDefinition(a.prefix,a.iconName);return i??(Uo(a),null)}buildParams(){let e=this.fixedWidth(),a={flip:this.flip(),animation:this.animation(),border:this.border(),inverse:this.inverse(),size:this.size(),pull:this.pull(),rotate:this.rotate(),fixedWidth:typeof e=="boolean"?e:this.config.fixedWidth,stackItemSize:this.stackItem!=null?this.stackItem.stackItemSize():void 0},i=this.transform(),r=typeof i=="string"?na.transform(i):i,o=this.mask(),s=o!=null?this.findIconDefinition(o):null,f={},u=this.a11yRole();u!=null&&(f.role=u);let d={};return a.rotate!=null&&!aa(a.rotate)&&(d["--fa-rotate-angle"]=`${a.rotate}`),{title:this.title(),transform:r,classes:Xo(a),mask:s??void 0,symbol:this.symbol(),attributes:f,styles:d}}static \u0275fac=function(a){return new(a||n)};static \u0275cmp=xn({type:n,selectors:[["fa-icon"]],hostAttrs:[1,"ng-fa-icon"],hostVars:2,hostBindings:function(a,i){a&2&&(fe("innerHTML",i.renderedIconHTML(),re),se("title",i.title()??void 0))},inputs:{icon:[1,"icon"],title:[1,"title"],animation:[1,"animation"],mask:[1,"mask"],flip:[1,"flip"],size:[1,"size"],pull:[1,"pull"],border:[1,"border"],inverse:[1,"inverse"],symbol:[1,"symbol"],rotate:[1,"rotate"],fixedWidth:[1,"fixedWidth"],transform:[1,"transform"],a11yRole:[1,"a11yRole"]},outputs:{icon:"iconChange",title:"titleChange",animation:"animationChange",mask:"maskChange",flip:"flipChange",size:"sizeChange",pull:"pullChange",border:"borderChange",inverse:"inverseChange",symbol:"symbolChange",rotate:"rotateChange",fixedWidth:"fixedWidthChange",transform:"transformChange",a11yRole:"a11yRoleChange"},decls:0,vars:0,template:function(a,i){},encapsulation:2,changeDetection:0})}return n})();export{ks as a};
