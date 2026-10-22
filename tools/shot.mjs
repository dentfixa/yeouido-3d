import p from 'puppeteer-core';
const b=await p.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const pg=await b.newPage(); await pg.setCacheEnabled(false); await pg.setViewport({width:1280,height:800});
pg.on('console',m=>console.log('C',m.text()));
for(const [f,q] of [['initial',''],['close_parc1','?target=30m%2060m%2020m&orbit=200deg%2075deg%20260m'],['street','?target=60m%2010m%2080m&orbit=160deg%2085deg%2040m']]){
 await pg.goto(process.argv[2]+q);
 await pg.waitForFunction(()=>document.getElementById('mv').loaded,{timeout:240000});
 await new Promise(r=>setTimeout(r,8000));
 const el=await pg.$('#mv'); await el.screenshot({path:`/workspace/shot_${f}.png`}); console.log('ok',f);
}
await b.close();
