(() => {
  const describe=el=>{
    const s=getComputedStyle(el),r=el.getBoundingClientRect();
    const backgrounds=[];
    for(let e=el;e;e=e.parentElement) backgrounds.push({tag:e.tagName,cls:e.className,background:getComputedStyle(e).backgroundColor,image:getComputedStyle(e).backgroundImage});
    return {text:el.textContent.trim()||el.value||'',style:Object.fromEntries(['fontFamily','fontSize','fontWeight','color','backgroundColor','backgroundImage','boxShadow','borderRadius','borderColor','borderWidth','paddingTop','paddingBottom','paddingLeft','paddingRight','marginBottom','lineHeight','textShadow'].map(k=>[k,s[k]])),rect:{x:r.x,y:r.y,width:r.width,height:r.height},backgrounds};
  };
  return {url:location.href,viewport:{width:innerWidth,height:innerHeight},documentWidth:document.documentElement.scrollWidth,controls:Array.from(document.querySelectorAll('main button:not([disabled]),main input:not([type=checkbox]),main select,main label,.alert,.card-body,.callout-title-container,.navbar .nav-link.active')).map(describe)};
})()
