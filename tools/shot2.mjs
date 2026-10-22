import p from 'puppeteer-core';
const base=process.argv[2], pre=process.argv[3]||'shot9';
const b=await p.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const pg=await b.newPage(); await pg.setCacheEnabled(false); await pg.setViewport({width:1280,height:800});
const V=[['initial',''],['close_apts','?target=-450m%2015m%20-300m&orbit=35deg%2068deg%20220m'],['close_ifc','?target=-90m%2060m%20120m&orbit=200deg%2078deg%20320m'],['street','?target=150m%208m%20-350m&orbit=120deg%2084deg%2060m']];
for(const [f,q] of V){ await pg.goto(base+q); await pg.waitForFunction(()=>document.getElementById('mv').loaded,{timeout:240000});
 await new Promise(r=>setTimeout(r,7000)); await pg.screenshot({path:`/workspace/${pre}_${f}.png`}); console.log('ok',f);}
// keyboard test
await pg.goto(base); await pg.waitForFunction(()=>document.getElementById('mv').loaded,{timeout:240000}); await new Promise(r=>setTimeout(r,3000));
const before=await pg.evaluate(()=>JSON.stringify(document.getElementById('mv').getCameraTarget()));
await pg.keyboard.down('ArrowUp'); await new Promise(r=>setTimeout(r,1200)); await pg.keyboard.up('ArrowUp');
await pg.keyboard.down('+'); await new Promise(r=>setTimeout(r,800)); await pg.keyboard.up('+');
const after=await pg.evaluate(()=>JSON.stringify([document.getElementById('mv').getCameraTarget(),document.getElementById('mv').getCameraOrbit().radius]));
console.log('KEY',before,after); await new Promise(r=>setTimeout(r,2000)); await pg.screenshot({path:`/workspace/${pre}_keys.png`});
await pg.click('#gb'); await new Promise(r=>setTimeout(r,2500)); await pg.screenshot({path:`/workspace/${pre}_gallery.png`});
await b.close();
