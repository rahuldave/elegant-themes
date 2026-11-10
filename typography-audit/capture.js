// Real-browser measurement harness. Run through CUA against the generated site.
const names=['folio','atelier','nocturne','tufte','zephyr-reading','simplex-reading','pulse-reading','litera-reading','darkly-reading'];
const select=document.querySelector('#theme');for(const id of names)select.add(new Option(id,id));
function runIn(frame, capture) { const w=frame.contentWindow; return capture(w.document,w.getComputedStyle.bind(w),w.innerWidth,w.innerHeight,w.devicePixelRatio,w.location); }
const captureType=(document,getComputedStyle,innerWidth,innerHeight,devicePixelRatio,location)=>(() => {
  const round = n => Math.round(n * 100) / 100;
  const rect = el => el ? Object.fromEntries(['x','y','width','height','left','right','top','bottom'].map(k=>[k,round(el.getBoundingClientRect()[k])])) : null;
  const style = el => {
    if (!el) return null;
    const s = getComputedStyle(el);
    return Object.fromEntries(['fontFamily','fontSize','fontWeight','fontStyle','fontKerning','fontSynthesis','lineHeight','letterSpacing','textTransform','textAlign','textIndent','textShadow','color','backgroundColor','backgroundImage','marginTop','marginBottom','paddingLeft','paddingRight','overflowX','whiteSpace','textDecorationLine'].map(k=>[k,s[k]]));
  };
  const backgrounds = el => {
    const out=[];
    for(let e=el;e;e=e.parentElement) out.push({tag:e.tagName,cls:e.className,background:getComputedStyle(e).backgroundColor,image:getComputedStyle(e).backgroundImage});
    return out;
  };
  const lines = p => {
    const nodes=[];
    const visit=e=>{for(const n of e.childNodes){if(n.nodeType===3)nodes.push(n);else visit(n);}};
    visit(p);
    const groups=[];
    for(const node of nodes) {
      for(let i=0;i<node.textContent.length;i++) {
        const r=document.createRange(); r.setStart(node,i); r.setEnd(node,i+1);
        const b=r.getBoundingClientRect();
        if(b.width<0.1 || b.height<1) continue;
        const mid=b.top+b.height/2;
        let line=groups.find(g=>Math.abs(g.mid-mid)<8);
        if(!line){line={mid,text:''};groups.push(line);}
        line.text+=node.textContent[i].replace(/\s/g,' ');
      }
    }
    return groups.sort((a,b)=>a.mid-b.mid).map(g=>({text:g.text.trim().replace(/\s+/g,' '),chars:g.text.trim().replace(/\s+/g,' ').length}));
  };
  const p=document.querySelector('#a-comfortable-measure > p') || document.querySelector('main section p');
  const ps=p ? [p,p.nextElementSibling].filter(e=>e?.tagName==='P') : [];
  const h1=document.querySelector('h1.title'),h2=document.querySelector('main section h2'),h3=document.querySelector('main section h3');
  const code=document.querySelector('pre.sourceCode code') || document.querySelector('pre code');
  const pre=code?.closest('pre');
  const link=document.querySelector('#a-comfortable-measure > p a:not(.anchorjs-link)');
  const inline=document.querySelector('main p code');
  return {
    url:location.href,viewport:{width:innerWidth,height:innerHeight,dpr:devicePixelRatio},
    documentWidth:document.documentElement.scrollWidth,bodyClass:document.body.className,
    body:{style:style(document.body),backgrounds:backgrounds(document.body)},
    main:{rect:rect(document.querySelector('main')),style:style(document.querySelector('main'))},
    paragraphs:ps.map(el=>({text:el.textContent.replace(/\s+/g,' ').trim(),style:style(el),rect:rect(el),lines:lines(el),backgrounds:backgrounds(el)})),
    headings:[h1,h2,h3].filter(Boolean).map(el=>({text:el.textContent.trim(),style:style(el),rect:rect(el)})),
    link:link?{style:style(link),backgrounds:backgrounds(link)}:null,
    inline:inline?{style:style(inline),backgrounds:backgrounds(inline)}:null,
    code:code?{style:style(code),rect:rect(code),preStyle:style(pre),preRect:rect(pre),scrollWidth:pre.scrollWidth,clientWidth:pre.clientWidth,backgrounds:backgrounds(code),tokens:Array.from(code.querySelectorAll('span')).filter(el=>el.textContent.trim()).map(el=>({text:el.textContent.trim(),style:style(el),backgrounds:backgrounds(el)})).filter((el,i,a)=>a.findIndex(v=>v.style.color===el.style.color)===i)}:null,
    fontStatus:document.fonts.status
  };
})();
const captureControls=(document,getComputedStyle,innerWidth,innerHeight,devicePixelRatio,location)=>(() => {
  const describe=el=>{
    const s=getComputedStyle(el),r=el.getBoundingClientRect();
    const backgrounds=[];
    for(let e=el;e;e=e.parentElement) backgrounds.push({tag:e.tagName,cls:e.className,background:getComputedStyle(e).backgroundColor,image:getComputedStyle(e).backgroundImage});
    return {text:el.textContent.trim()||el.value||'',style:Object.fromEntries(['fontFamily','fontSize','fontWeight','color','backgroundColor','backgroundImage','boxShadow','borderRadius','borderColor','borderWidth','paddingTop','paddingBottom','paddingLeft','paddingRight','marginBottom','lineHeight','textShadow'].map(k=>[k,s[k]])),rect:{x:r.x,y:r.y,width:r.width,height:r.height},backgrounds};
  };
  return {url:location.href,viewport:{width:innerWidth,height:innerHeight},documentWidth:document.documentElement.scrollWidth,controls:Array.from(document.querySelectorAll('main button:not([disabled]),main input:not([type=checkbox]),main select,main label,.alert,.card-body,.callout-title-container,.navbar .nav-link.active')).map(describe)};
})();
const captureFoundation=(document,getComputedStyle,innerWidth,innerHeight,devicePixelRatio,location)=>{
 const describe=el=>{if(!el)return null;const s=getComputedStyle(el),r=el.getBoundingClientRect();const backgrounds=[];for(let e=el;e;e=e.parentElement)backgrounds.push({tag:e.tagName,cls:e.className,background:getComputedStyle(e).backgroundColor,image:getComputedStyle(e).backgroundImage});return {text:el.textContent.trim()||el.value||'',style:Object.fromEntries(['fontFamily','fontSize','fontWeight','fontSynthesis','lineHeight','color','backgroundColor','borderColor','borderWidth','borderRadius','opacity','paddingLeft','paddingRight','textDecorationLine','boxShadow','outlineColor','outlineWidth'].map(k=>[k,s[k]])),rect:{width:r.width,height:r.height,left:r.left,right:r.right},backgrounds};};
 return {url:location.href,viewport:{width:innerWidth,height:innerHeight},documentWidth:document.documentElement.scrollWidth,rootSize:getComputedStyle(document.documentElement).fontSize,
 elements:Object.fromEntries(['foundation-prose','foundation-metadata','foundation-primary','foundation-secondary','foundation-outline','foundation-disabled','foundation-error','foundation-title','foundation-invalid','foundation-select','foundation-check','foundation-selected'].map(id=>[id,describe(document.getElementById(id))])),
 states:[...document.querySelectorAll('[data-state]')].map(e=>({state:e.dataset.state,...describe(e)})),alerts:[...document.querySelectorAll('.alert')].map(describe),
 callout:describe(document.querySelector('.callout-body')),heading:describe(document.querySelector('h2')),title:describe(document.querySelector('h1.title')),
 code:describe(document.querySelector('pre code')),codeSpan:describe(document.querySelector('pre code span')),fontStatus:document.fonts.status,
 loadedFonts:[...document.fonts].filter(f=>f.status==='loaded').map(f=>({family:f.family,weight:f.weight,style:f.style})),
 semantics:{disabled:document.querySelector('#foundation-disabled').disabled,invalid:document.querySelector('#foundation-invalid').getAttribute('aria-invalid'),describedBy:document.querySelector('#foundation-invalid').getAttribute('aria-describedby'),current:document.querySelector('#foundation-selected').getAttribute('aria-current')}};
};
const specs=[['typography','desktop',1280,captureType],['typography','mobile',390,captureType],['code','desktop',1280,captureType],['code','mobile',390,captureType],['components','desktop',1280,captureControls],['foundations','desktop',1280,captureFoundation],['foundations','mobile',390,captureFoundation]];
document.querySelector('#load').addEventListener('click',async()=>{
 const id=select.value,mode=document.querySelector('#mode').value,box=document.querySelector('#frames'),out=document.querySelector('#results'),status=document.querySelector('#status');
 out.hidden=true;out.textContent='';status.textContent='Loading '+id+' '+mode;box.replaceChildren();
 try{
 const results=await Promise.all(specs.map(async([page,viewportName,width,capture])=>{
  const section=document.createElement('section'),title=document.createElement('h2');title.textContent=id+' '+mode+' / '+page+' / '+width+'px';section.append(title);const frame=document.createElement('iframe');frame.title=title.textContent;frame.width=width;frame.height=844;section.append(frame);box.append(section);
  await new Promise((resolve,reject)=>{frame.onload=resolve;frame.onerror=reject;frame.src='../../previews/'+id+'/'+page+'.html?mode='+mode;});
  await frame.contentDocument.fonts.ready;
  await new Promise(resolve=>frame.contentWindow.requestAnimationFrame(()=>frame.contentWindow.requestAnimationFrame(resolve)));
  const seconds=v=>v.trim().endsWith('ms')?parseFloat(v)/1000:parseFloat(v);
  const transitionSeconds=Math.max(0,...[...frame.contentDocument.querySelectorAll('body,a,button,input,select,.alert')].map(el=>{const s=frame.contentWindow.getComputedStyle(el);return Math.max(...s.transitionDuration.split(',').map(seconds))+Math.max(...s.transitionDelay.split(',').map(seconds));}));
  const settleMilliseconds=Math.ceil(transitionSeconds*1000)+40;
  await new Promise(resolve=>setTimeout(resolve,settleMilliseconds));
  const r=runIn(frame,capture);r.settleMilliseconds=settleMilliseconds;r.fontStatus=frame.contentDocument.fonts.status;r.id=id;r.mode=mode;r.page=page;r.viewportName=viewportName;r.capturedAt=new Date().toISOString();return r;
 }));
 out.textContent=JSON.stringify(results);out.hidden=false;status.textContent='Ready: '+id+' '+mode+' / '+results.length+' observations';
 }catch(error){status.textContent='Error: '+error.message;throw error;}
});
