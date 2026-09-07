"""Convert the user's original OBJ + BMP textures to a standalone glTF 2 GLB.
Usage: python convert_obj.py SOURCE_DIRECTORY OUTPUT_GLB
Requires Pillow. Positions, UV seams, groups and materials are retained.
"""
import sys,json,struct,math,io,hashlib
from pathlib import Path
from collections import defaultdict
from PIL import Image
src=Path(sys.argv[1]);out=Path(sys.argv[2])
positions=[];uvs=[];groups=defaultdict(list);group='Van';material=None
for line in (src/'Van Car 1.obj').read_text().splitlines():
 a=line.split()
 if not a:continue
 if a[0]=='v':positions.append(tuple(map(float,a[1:4])))
 elif a[0]=='vt':uvs.append(tuple(map(float,a[1:3])))
 elif a[0]=='g':group=a[1]
 elif a[0]=='usemtl':material=a[1]
 elif a[0]=='f':
  refs=[tuple(int(v)-1 for v in r.split('/')[:2]) for r in a[1:]]
  for i in range(1,len(refs)-1):groups[group,material].append((refs[0],refs[i],refs[i+1]))
mats={};current=None
for line in (src/'Van Car 1.mtl').read_text().splitlines():
 a=line.split()
 if not a:continue
 if a[0]=='newmtl':current={};mats[a[1]]=current
 elif a[0]=='map_Kd':current['texture']=line.strip().split('\\')[-1]
 elif a[0]=='Kd':current['color']=list(map(float,a[1:4]))
 elif a[0]=='d':current['opacity']=float(a[1])
g={'asset':{'version':'2.0','generator':'BrandMyVan original OBJ converter'},'scene':0,'scenes':[{'nodes':[]}],'nodes':[],'meshes':[],'materials':[],'textures':[],'images':[],'samplers':[{'magFilter':9729,'minFilter':9987,'wrapS':10497,'wrapT':10497}],'bufferViews':[],'accessors':[]}
bin=bytearray()
def view(data,target=None):
 while len(bin)%4:bin.append(0)
 v={'buffer':0,'byteOffset':len(bin),'byteLength':len(data)}
 if target:v['target']=target
 g['bufferViews'].append(v);bin.extend(data);return len(g['bufferViews'])-1
def acc(values,kind,n,component=5126,bounds=False):
 flat=[x for row in values for x in row] if n>1 else values
 fmt='f' if component==5126 else 'I'
 a={'bufferView':view(struct.pack('<'+fmt*len(flat),*flat),34963 if n==1 else 34962),'componentType':component,'count':len(values),'type':kind}
 if bounds:
  a['min']=[min(v[i] for v in values) for i in range(n)];a['max']=[max(v[i] for v in values) for i in range(n)]
 g['accessors'].append(a);return len(g['accessors'])-1
for name,m in mats.items():
 pbr={'metallicFactor':0,'roughnessFactor':0.8}
 mat={'name':name,'pbrMetallicRoughness':pbr,'doubleSided':True}
 if 'texture' in m:
  im=Image.open(src/'Van Car 1.fbm'/m['texture']).convert('RGB');buf=io.BytesIO();im.save(buf,format='JPEG',quality=95,optimize=True)
  g['images'].append({'name':m['texture'],'bufferView':view(buf.getvalue()),'mimeType':'image/jpeg'})
  g['textures'].append({'source':len(g['images'])-1,'sampler':0});pbr['baseColorTexture']={'index':len(g['textures'])-1}
 else:
  pbr['baseColorFactor']=m['color']+[m['opacity']];pbr['roughnessFactor']=0.15
  if m['opacity']<1:mat['alphaMode']='BLEND'
 g['materials'].append(mat)
# Area-weighted normals share original vertex indices, including UV seams.
normals=defaultdict(lambda:[0.,0.,0.])
for (name,mat),tris in groups.items():
 for tri in tris:
  a,b,c=[positions[r[0]] for r in tri];u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
  n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
  for r in tri:
   for i in range(3):normals[name,r[0]][i]+=n[i]
for name in dict.fromkeys(k[0] for k in groups):
 primitives=[]
 for (gn,mat),tris in groups.items():
  if gn!=name:continue
  keys={};pos=[];tex=[];ns=[];indices=[]
  for tri in tris:
   for r in tri:
    if r not in keys:
     keys[r]=len(pos);pos.append(positions[r[0]]);t=uvs[r[1]];tex.append((t[0],1-t[1]));n=normals[name,r[0]];mag=math.sqrt(sum(x*x for x in n)) or 1;ns.append(tuple(x/mag for x in n))
    indices.append(keys[r])
  primitives.append({'attributes':{'POSITION':acc(pos,'VEC3',3,bounds=True),'TEXCOORD_0':acc(tex,'VEC2',2),'NORMAL':acc(ns,'VEC3',3)},'indices':acc(indices,'SCALAR',1,5125),'material':list(mats).index(mat)})
 g['meshes'].append({'name':name,'primitives':primitives});g['nodes'].append({'name':name,'mesh':len(g['meshes'])-1});g['scenes'][0]['nodes'].append(len(g['nodes'])-1)
g['buffers']=[{'byteLength':len(bin)}]
while len(bin)%4:bin.append(0)
j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4)
data=struct.pack('<4sII',b'glTF',2,12+8+len(j)+8+len(bin))+struct.pack('<I4s',len(j),b'JSON')+j+struct.pack('<I4s',len(bin),b'BIN\0')+bin
out.write_bytes(data)
print(json.dumps({'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'originalVertices':len(positions),'triangles':sum(len(v) for v in groups.values()),'groups':len(g['nodes']),'textures':len(g['images'])}))
