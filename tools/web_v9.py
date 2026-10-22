# blender -b yeouido_v8.blend -P web_v9.py -- out.glb   (does NOT save blend)
import bpy,bmesh,math,json,random,colorsys,sys
from mathutils import Vector,Matrix
OUT=sys.argv[sys.argv.index('--')+1]; D='/workspace/yeouido/'
LAT0,LON0=37.5265,126.927; KX=111320*math.cos(math.radians(LAT0)); KY=110574
P=lambda la,lo:((lo-LON0)*KX,(la-LAT0)*KY)
# ---- OSM building tags, grid index
B=[];seen=set()
for f in ['osm.json','osm3.json','osm4.json','osm2.json']:
    try: d=json.load(open(D+f))
    except: continue
    for e in d.get('elements',[]):
        t=e.get('tags',{})
        if 'building' not in t or e['id'] in seen or 'geometry' not in e: continue
        seen.add(e['id']); pts=[P(g['lat'],g['lon']) for g in e['geometry']]
        xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
        B.append((min(xs),max(xs),min(ys),max(ys),t))
G={}
for i,b in enumerate(B):
    for gx in range(int(b[0]//100),int(b[1]//100)+1):
        for gy in range(int(b[2]//100),int(b[3]//100)+1): G.setdefault((gx,gy),[]).append(i)
def lookup(x,y):
    best=None
    for i in G.get((int(x//100),int(y//100)),[]):
        b=B[i]
        if b[0]-2<=x<=b[1]+2 and b[2]-2<=y<=b[3]+2:
            a=(b[1]-b[0])*(b[3]-b[2])
            if best is None or a<best[0]: best=(a,b[4])
    return best[1] if best else {}
NAMED={'white':(0.85,0.85,0.83),'grey':(0.5,0.5,0.5),'gray':(0.5,0.5,0.5),'silver':(0.7,0.72,0.74),'black':(0.08,0.08,0.08),'red':(0.55,0.12,0.1),'brown':(0.35,0.2,0.12),'maroon':(0.4,0.1,0.1),'beige':(0.82,0.75,0.6),'tan':(0.7,0.58,0.42),'yellow':(0.85,0.72,0.3),'orange':(0.85,0.45,0.15),'blue':(0.2,0.35,0.6),'lightblue':(0.55,0.7,0.85),'green':(0.2,0.42,0.25),'darkgreen':(0.1,0.25,0.15),'teal':(0.15,0.45,0.45),'cream':(0.9,0.87,0.76),'ivory':(0.92,0.9,0.82),'pink':(0.85,0.6,0.6),'gold':(0.75,0.6,0.25)}
def pcol(s):
    if not s: return None
    s=s.strip().lower().replace(' ','').replace('_','')
    if s.startswith('#') and len(s) in (4,7):
        h=s[1:]; h=''.join(c*2 for c in h) if len(h)==3 else h
        try: return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
        except: return None
    return NAMED.get(s)
MAT={'brick':(0.55,0.28,0.2),'concrete':(0.62,0.62,0.6),'glass':(0.25,0.42,0.5),'stone':(0.78,0.74,0.66),'metal':(0.6,0.62,0.65),'plaster':(0.88,0.86,0.8),'wood':(0.45,0.32,0.2),'granite':(0.8,0.78,0.74),'marble':(0.88,0.87,0.84)}
RMAT={'concrete':(0.5,0.5,0.49),'metal':(0.45,0.5,0.5),'tar_paper':(0.2,0.2,0.2),'roof_tiles':(0.45,0.25,0.2),'tile':(0.4,0.25,0.2),'glass':(0.3,0.4,0.45),'grass':(0.2,0.35,0.15)}
def jit(c,r,a=0.06): return tuple(max(0,min(1,x+r.uniform(-a,a))) for x in c)
APT=[(0.9,0.89,0.86),(0.88,0.87,0.84),(0.92,0.91,0.88),(0.85,0.84,0.8),(0.86,0.82,0.74),(0.8,0.8,0.8)]
LOW=[(0.55,0.28,0.2),(0.62,0.35,0.25),(0.45,0.25,0.18),(0.82,0.75,0.62),(0.88,0.86,0.8),(0.7,0.7,0.68),(0.75,0.65,0.5),(0.6,0.55,0.5),(0.5,0.52,0.55)]
OFF=[(0.72,0.72,0.7),(0.8,0.76,0.68),(0.62,0.63,0.64),(0.85,0.83,0.78),(0.55,0.57,0.6),(0.78,0.7,0.6)]
GLS=[(0.25,0.42,0.55),(0.2,0.45,0.48),(0.3,0.5,0.45),(0.35,0.42,0.5),(0.45,0.55,0.6),(0.22,0.3,0.4),(0.5,0.58,0.62)]
ROOF=[(0.45,0.46,0.46),(0.38,0.39,0.4),(0.3,0.45,0.35),(0.55,0.55,0.53),(0.25,0.38,0.32),(0.5,0.48,0.45)]
def facade(cat,t,r,h):
    c=pcol(t.get('building:colour')) or MAT.get(t.get('building:material',''))
    n=t.get('name','')
    if '현대 서울' in n or 'The Hyundai' in n: c=(0.6,0.7,0.75)
    if c: return jit(c,r,0.03)
    if cat in ('glass','glass2'): return jit(r.choice(GLS),r,0.04)
    if cat=='granite': return jit((0.86,0.85,0.81),r,0.02)
    if cat=='apt': return jit(r.choice(APT),r,0.02)
    if cat=='office': return jit(r.choice(OFF) if h<60 else r.choice(GLS+OFF),r,0.03)
    if h>45: return jit(r.choice(OFF+GLS),r,0.03)
    return jit(r.choice(LOW+APT),r,0.04)
def roofc(t,r):
    return pcol(t.get('roof:colour')) or RMAT.get(t.get('roof:material','')) or jit(r.choice(ROOF),r,0.03)
# ---- facade materials
def texmat(name,img,metal,rough):
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; b=nt.nodes['Principled BSDF']
    tx=nt.nodes.new('ShaderNodeTexImage'); tx.image=bpy.data.images.load(D+'tex/'+img)
    ca=nt.nodes.new('ShaderNodeVertexColor'); ca.layer_name='Col'
    mx=nt.nodes.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.blend_type='MULTIPLY'; mx.inputs[0].default_value=1
    nt.links.new(tx.outputs[0],mx.inputs[6]); nt.links.new(ca.outputs[0],mx.inputs[7]); nt.links.new(mx.outputs[2],b.inputs['Base Color'])
    b.inputs['Metallic'].default_value=metal; b.inputs['Roughness'].default_value=rough; return m
MF=texmat('web_facade','web_facade.png',0.0,0.75); MG=texmat('web_glass','web_glass.png',0.5,0.18)
CATS={'Buildings_apt':'apt','Buildings_glass':'glass','Buildings_glass2':'glass2','Buildings_granite':'granite','Buildings_low':'low','Buildings_office':'office'}
for on,cat in CATS.items():
    o=bpy.data.objects[on]; me=o.data; bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
    mw=o.matrix_world
    # islands via union-find on verts
    par=list(range(len(bm.verts)))
    def fd(a):
        while par[a]!=a: par[a]=par[par[a]]; a=par[a]
        return a
    for e in bm.edges:
        a,b=fd(e.verts[0].index),fd(e.verts[1].index)
        if a!=b: par[a]=b
    isl={}
    for f in bm.faces: isl.setdefault(fd(f.verts[0].index),[]).append(f)
    uv=bm.loops.layers.uv.new('UVMap'); col=bm.loops.layers.color.new('Col')
    glass=cat in ('glass','glass2'); BW,FH=(1.6,4.0) if glass else (3.6,3.2)
    hit=0
    for k,fs in isl.items():
        vs={v for f in fs for v in f.verts}; ws=[mw@v.co for v in vs]
        cx=sum(w.x for w in ws)/len(ws); cy=sum(w.y for w in ws)/len(ws); z0=min(w.z for w in ws); h=max(w.z for w in ws)-z0
        t=lookup(cx,cy); hit+=bool(t)
        r=random.Random(int(cx*7.1)^int(cy*13.3))
        fc=facade(cat,t,r,h); rc=roofc(t,r)
        for f in fs:
            n=f.normal; roof=abs(n.z)>0.7
            tg=Vector((-n.y,n.x)).normalized() if not roof else None
            c=(*rc,1) if roof else (*fc,1)
            for l in f.loops:
                w=mw@l.vert.co
                l[uv].uv=(0.5,0.05) if roof else ((w.x*tg.x+w.y*tg.y)/BW,(w.z-z0)/FH)
                l[col]=c
    bm.to_mesh(me); bm.free(); me.uv_layers.active=me.uv_layers['UVMap']
    me.color_attributes.active_color=me.color_attributes['Col']
    me.materials.clear(); me.materials.append(MG if glass else MF)
    print('CAT',on,len(isl),'osm-matched',hit,flush=True)
# roof mesh colour variety: keep material 'roof'
# ---- simplify all other materials
FLAT={'ground_urban':(0.17,0.17,0.175,0,0.95),'road.001':(0.07,0.07,0.075,0,0.9),'major_road.001':(0.06,0.06,0.065,0,0.9),'embankment.001':(0.36,0.37,0.34,0,0.95),'grass_pbr':(0.15,0.3,0.09,0,0.95),'park_path.001':(0.34,0.32,0.29,0,0.95),'stone.001':(0.62,0.61,0.58,0,0.8),'bridge_concrete.001':(0.52,0.52,0.5,0,0.8),'granite_paving':(0.56,0.55,0.52,0,0.8),
 'glass_tower':(0.12,0.2,0.26,0.7,0.12),'glass_tower_green':(0.12,0.3,0.3,0.7,0.12),'gold_glass_63':(0.8,0.58,0.22,0.95,0.18),'granite_facade':(0.86,0.85,0.81,0,0.6),'copper_dome':(0.3,0.5,0.42,0.3,0.45),
 'shrub_02':(0.1,0.22,0.06,0,0.9),'tree_small_02_leaves':(0.12,0.26,0.07,0,0.9),'tree_small_02_branches':(0.22,0.15,0.09,0,0.9),'tree_small_02_trunk':(0.22,0.15,0.09,0,0.9),
 'apartment':(0.88,0.87,0.84,0,0.8),'lowrise':(0.7,0.65,0.58,0,0.8),'office_concrete':(0.7,0.7,0.68,0,0.8),'water':(0.02,0.06,0.07,0,0.05)}
for m in bpy.data.materials:
    if not m.node_tree or m in (MF,MG) or m.name.startswith('colormap'): continue
    b=m.node_tree.nodes.get('Principled BSDF')
    if not b: continue
    v=FLAT.get(m.name)
    if v: 
        for l in list(b.inputs['Base Color'].links): m.node_tree.links.remove(l)
        b.inputs['Base Color'].default_value=(*v[:3],1); b.inputs['Metallic'].default_value=v[3]; b.inputs['Roughness'].default_value=v[4]
        for k in ('Normal','Roughness','Metallic'):
            for l in list(b.inputs[k].links): m.node_tree.links.remove(l)
        b.inputs['Roughness'].default_value=v[4]; b.inputs['Metallic'].default_value=v[3]
# ---- proxies (from glb_v8)
bm=bmesh.new(); bmesh.ops.create_cone(bm,cap_ends=True,segments=6,radius1=0.25,radius2=0.15,depth=4,matrix=Matrix.Translation((0,0,2))); nb=len(bm.faces)
for c,r_ in (((0,0,5.6),2.4),((0.9,0.5,6.6),1.6),((-0.8,-0.4,6.4),1.5)): bmesh.ops.create_icosphere(bm,subdivisions=1,radius=r_,matrix=Matrix.Translation(c))
tm=bpy.data.meshes.new('proxy_tree'); bm.to_mesh(bm_:=tm) if False else bm.to_mesh(tm); bm.free()
def flatmat(n,c):
    m=bpy.data.materials.new(n); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=(*c,1); b.inputs['Roughness'].default_value=0.9; return m
tm.materials.append(flatmat('bark_web',(0.2,0.13,0.08))); tm.materials.append(flatmat('leaves_web',(0.1,0.24,0.07)))
for i,p in enumerate(tm.polygons): p.material_index=0 if i<nb else 1
cp=flatmat('carpaint_web',(0.7,0.7,0.72))
def boxcar(n,L,W,H):
    b=bmesh.new(); bmesh.ops.create_cube(b,size=1,matrix=Matrix.LocRotScale(Vector((0,0,0.35+H*0.3)),None,Vector((L,W,H*0.6))))
    bmesh.ops.create_cube(b,size=1,matrix=Matrix.LocRotScale(Vector((-0.2,0,0.35+H*0.8)),None,Vector((L*0.5,W*0.9,H*0.4))))
    m=bpy.data.meshes.new(n); b.to_mesh(m); b.free(); m.materials.append(cp); return m
carm=boxcar('proxy_car',4.7,1.85,1.45); suvm=boxcar('proxy_suv',4.8,1.95,1.75)
for o in bpy.data.objects:
    if o.type!='MESH': continue
    if o.data.name.startswith(('ph_tree','ph_shrub','tree_')): o.data=tm
    elif o.data.name.startswith('k_'): o.data=suvm if 'suv' in o.data.name else carm
for o in bpy.data.objects: o.select_set(o.type=='MESH' and not o.name.startswith(('Haze','Terrain_DEM','FarWater')))
kw=dict(filepath=OUT,use_selection=True,export_image_format='JPEG',export_gpu_instances=True,export_draco_mesh_compression_enable=False)
try: bpy.ops.export_scene.gltf(export_vertex_color='ACTIVE',**kw)
except TypeError: bpy.ops.export_scene.gltf(export_colors=True,**kw)
print('GLB OK')
