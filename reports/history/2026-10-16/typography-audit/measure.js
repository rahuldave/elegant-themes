() => {
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
}
