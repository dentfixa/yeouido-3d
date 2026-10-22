import {NodeIO} from '@gltf-transform/core';
import {ALL_EXTENSIONS} from '@gltf-transform/extensions';
import {prune} from '@gltf-transform/functions';
import draco3d from 'draco3dgltf';
const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'draco3d.decoder':await draco3d.createDecoderModule(),'draco3d.encoder':await draco3d.createEncoderModule()});
const doc=await io.read(process.argv[2]);
const C={'stone.001':[0.28,0.28,0.27],'ground_urban':[0.16,0.165,0.17],'embankment.001':[0.36,0.37,0.36],'grass_pbr':[0.13,0.26,0.08],'park_path.001':[0.30,0.29,0.27],'road.001':[0.07,0.07,0.075],'bridge_concrete.001':[0.50,0.50,0.49]};
for(const m of doc.getRoot().listMaterials()){const c=C[m.getName()]; if(!c) continue;
 m.setBaseColorTexture(null).setNormalTexture(null).setMetallicRoughnessTexture(null).setBaseColorFactor([...c,1]).setMetallicFactor(0).setRoughnessFactor(0.95);
 console.log('fixed',m.getName());}
for(const me of doc.getRoot().listMeshes()){ if(me.getName()!=='proxy_tree') continue;
 const ps=me.listPrimitives(); ps.sort((a,b)=>a.getAttribute('POSITION').getCount()-b.getAttribute('POSITION').getCount());
 ps.forEach((p,i)=>{const m=doc.createMaterial(i===ps.length-1?'leaf':'trunk').setBaseColorFactor(i===ps.length-1?[0.09,0.2,0.06,1]:[0.18,0.12,0.07,1]).setMetallicFactor(0).setRoughnessFactor(0.9);p.setMaterial(m);console.log('tree prim',i,p.getAttribute('POSITION').getCount());});}
import('fs');
const fs=await import('fs');
for(const t of doc.getRoot().listTextures()) if(t.getName()==='PaletteBaseColor'){t.setImage(fs.readFileSync('/tmp/pal_new.png')).setMimeType('image/png');}
const g=doc.getRoot().listMaterials().find(m=>m.getName()==='glass_tower'); g.setBaseColorTexture(null).setBaseColorFactor([0.55,0.56,0.58,1]).setMetallicFactor(0.3).setRoughnessFactor(0.35);
await doc.transform(prune());
await io.write(process.argv[3],doc);
