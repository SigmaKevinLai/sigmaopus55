// Run through playwright-cli run-code --filename. Chromium CDP lab, not field CWV.
// Uses the active page's site root. Slow 4G-like: 150ms latency, 1.6Mbps down,
// 750Kbps up, 4x CPU slowdown. Three fresh contexts; no cache reuse.
async (page) => {
 const url=new URL('./',page.url()).href, results=[];
 for(let sample=1;sample<=3;sample++){
  const context=await page.context().browser().newContext({viewport:{width:390,height:844},deviceScaleFactor:1});
  try{
   await context.addInitScript(()=>{window.lab={lcp:0,cls:0};new PerformanceObserver(l=>{for(const e of l.getEntries())window.lab.lcp=e.startTime;}).observe({type:'largest-contentful-paint',buffered:true});new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.lab.cls+=e.value;}).observe({type:'layout-shift',buffered:true});});
   const p=await context.newPage(),cdp=await context.newCDPSession(p);
   await cdp.send('Network.enable');await cdp.send('Network.setCacheDisabled',{cacheDisabled:true});
   await cdp.send('Network.emulateNetworkConditions',{offline:false,latency:150,downloadThroughput:1600000/8,uploadThroughput:750000/8});
   await cdp.send('Emulation.setCPUThrottlingRate',{rate:4});
   await p.goto(url,{waitUntil:'networkidle',timeout:60000});await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(1500);
   results.push(await p.evaluate(sample=>({sample,lcpMs:Math.round(window.lab.lcp),cls:Number(window.lab.cls.toFixed(4)),transferBytes:performance.getEntriesByType('resource').reduce((n,r)=>n+r.transferSize,0),externalRequests:performance.getEntriesByType('resource').filter(r=>!r.name.startsWith(location.origin)).length}),sample));
  }catch(error){results.push({sample,error:String(error.message||error).split('\n')[0]});}finally{await context.close();}
 }
 return JSON.stringify(results);
}
