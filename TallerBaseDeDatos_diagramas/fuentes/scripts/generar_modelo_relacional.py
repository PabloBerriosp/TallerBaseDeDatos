from pathlib import Path
import json,math,heapq
from collections import Counter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A1,landscape
from reportlab.graphics.shapes import Drawing,Rect,Line,Ellipse,String
from reportlab.graphics import renderSVG,renderPDF
from reportlab.pdfgen import canvas
import pypdfium2 as pdfium
ROOT=Path(__file__).resolve().parents[2];W=ROOT/'fuentes';O=ROOT/'diagramas/relacional';D=O
D.mkdir(parents=True,exist_ok=True)
for name,file in [('Body','arial.ttf'),('Bold','arialbd.ttf')]:pdfmetrics.registerFont(TTFont(name,str(Path('C:/Windows/Fonts')/file)))
m=json.loads((W/'modelo_relacional.json').read_text(encoding='utf8'))
rows=[['REGISTRO_ORIGEN','RECINTO','EVENTO_ARTISTA','ARTISTA','PERSONA_NATURAL','CAUSA_DESVIACION_EVENTO'],['VERSION_PRESUPUESTO','EVENTO','GASTO','INGRESO','CONTRAPARTE','ORGANIZACION'],['LINEA_PRESUPUESTO','CATEGORIA','PAGO_GASTO','LIQUIDACION','MOVIMIENTO_TICKETERA','CORTE_VENTA']]
BW=480;GAP=210;PAD=100;RH=27;HH=34;WIDTH=6*BW+5*GAP+2*PAD
def clean(a):return a.replace('*','').replace('?','')
def sqltype(a,table=None):
    a=clean(a)
    if a=='id_externo':return 'varchar(200)'
    if table=='RECINTO' and a=='numero':return 'varchar(20)'
    if a.startswith('id_'):return 'bigint'
    if 'monto' in a or 'clp' in a:return 'numeric(18,2)'
    if a in ['numero','nro_linea','orden_presentacion','capacidad','aforo_plan','entradas_acumuladas']:return 'integer'
    if a in ['instante','fecha_corte','fecha_revision','fecha_validacion']:return 'timestamp'
    if a.startswith('fecha'):return 'date'
    if a=='codigo_proyecto' or a=='codigo_recibido':return 'varchar(30)'
    if a=='numero' :return 'integer'
    if a in ['estado','naturaleza','tipo','fuente','tipo_gasto','tipo_show','tipo_acto','tipo_recinto']:return 'varchar(30)'
    if a=='pais':return 'varchar(80)'
    if a in ['descripcion','observacion','motivo_anulacion']:return 'text'
    return 'varchar(200)'
nodes={};y=PAD
for row in rows:
    for c,n in enumerate(row):
        h=HH+len(m[n]['attrs'])*RH+8;nodes[n]={'x':PAD+c*(BW+GAP),'y':y,'w':BW,'h':h}
    y+=max(nodes[n]['h'] for n in row)+180
HEIGHT=y-100
draw=Drawing(WIDTH,HEIGHT)
def text(x,y,s,size=16,font='Body',anchor='start'):
    draw.add(String(x,HEIGHT-y-5,s,fontName=font,fontSize=size,textAnchor=anchor,fillColor=colors.HexColor('#202428')))
def line(p,q,width=1.6,color='#303438'):
    draw.add(Line(p[0],HEIGHT-p[1],q[0],HEIGHT-q[1],strokeColor=colors.HexColor(color),strokeWidth=width))
STEP=10;blocked=set();used={};labels=[]
for b in nodes.values():
    for xx in range(int((b['x']-15)/STEP),int((b['x']+BW+15)/STEP)+1):
        for yy in range(int((b['y']-15)/STEP),int((b['y']+b['h']+15)/STEP)+1):blocked.add((xx,yy))
def side_pair(a,b):
    dx=(b['x']+BW/2)-(a['x']+BW/2);dy=(b['y']+b['h']/2)-(a['y']+a['h']/2)
    if abs(dx)>abs(dy)*1.2:return ('R','L') if dx>0 else ('L','R')
    return ('B','T') if dy>0 else ('T','B')
edges=[]
verbs={'id_recinto':'Se realiza en','id_version':'Tiene detalle','id_categoria':'Clasifica','id_contraparte':'Tiene contraparte','codigo_proyecto':'Corresponde a','id_artista':'Presenta','id_gasto':'Documenta','id_ticketera':'Comercializa','id_liquidacion':'Se imputa a'}
for n,t in m.items():
    for f in t['fks']:
        s,e=side_pair(nodes[n],nodes[f['parent']]);edges.append({'child':n,'fk':f,'s':s,'e':e})
tot=Counter([(v['child'],v['s']) for v in edges]+[(v['fk']['parent'],v['e']) for v in edges]);portused=Counter()
def port(n,side):
    b=nodes[n];count=portused[(n,side)];portused[(n,side)]+=1;total=tot[(n,side)]
    f=(count+1)/(total+1)
    if side in ['L','R']:return (b['x']+(BW if side=='R' else 0),b['y']+HH+20+f*(b['h']-HH-40))
    return (b['x']+45+f*(BW-90),b['y']+(b['h'] if side=='B' else 0))
vec={'L':(-1,0),'R':(1,0),'T':(0,-1),'B':(0,1)}
def route(s,e,source_side,target_side):
    start_exact=s;end_exact=e
    # Respect the direction of the table ports, including the final approach.
    # Otherwise a shortest grid route may double back over the connector stub.
    directions={'R':0,'B':1,'L':2,'T':3}
    start_dir=directions[source_side];end_dir=(directions[target_side]+2)%4
    def snap(p,side):
        x,y=p
        if side=='R':x=math.ceil(x/STEP)*STEP
        elif side=='L':x=math.floor(x/STEP)*STEP
        elif side=='B':y=math.ceil(y/STEP)*STEP
        else:y=math.floor(y/STEP)*STEP
        return (round(x/STEP),round(y/STEP))
    s=snap(s,source_side);e=snap(e,target_side);q=[(0,0,s,start_dir)];best={(s,start_dir):0};prev={};last=None
    while q:
        _,cost,p,d=heapq.heappop(q)
        if best.get((p,d))!=cost:continue
        if p==e:
            if d!=directions[target_side]:last=(p,d);break
            continue
        for nd,(dx,dy) in enumerate([(1,0),(0,1),(-1,0),(0,-1)]):
            if nd==(d+2)%4 or p==s and nd!=start_dir:continue
            v=(p[0]+dx,p[1]+dy)
            if v in blocked or not(2<v[0]<WIDTH/STEP-2 and 2<v[1]<HEIGHT/STEP-2):continue
            terminal=min(abs(v[0]-s[0])+abs(v[1]-s[1]),abs(v[0]-e[0])+abs(v[1]-e[1]))<6
            nc=cost+1+(15 if d!=-1 and d!=nd else 0)+(0 if terminal else used.get(v,0)*8)
            if nc<best.get((v,nd),1e12):best[(v,nd)]=nc;prev[(v,nd)]=(p,d);heapq.heappush(q,(nc+abs(v[0]-e[0])+abs(v[1]-e[1]),nc,v,nd))
    if last is None:raise RuntimeError(('Unroutable',s,e))
    out=[]
    while last in prev:out.append(last[0]);last=prev[last]
    out.append(s);out.reverse()
    for p in out:
        for dx,dy in [(0,0),(1,0),(-1,0),(0,1),(0,-1)]:used[(p[0]+dx,p[1]+dy)]=used.get((p[0]+dx,p[1]+dy),0)+1
    simple=[out[0]]
    for i in range(1,len(out)-1):
        if (out[i][0]-out[i-1][0],out[i][1]-out[i-1][1])!=(out[i+1][0]-out[i][0],out[i+1][1]-out[i][1]):simple.append(out[i])
    simple.append(out[-1]);points=[(a*STEP,b*STEP) for a,b in simple]
    # Match exact continuous port coordinates rather than stitching the snapped
    # grid to them with tiny U-shaped corrections at the endpoints.
    if len(points)==2:
        if source_side in ['L','R']:
            x=(points[0][0]+points[-1][0])/2
            points=[(points[0][0],start_exact[1]),(x,start_exact[1]),(x,end_exact[1]),(points[-1][0],end_exact[1])]
        else:
            y=(points[0][1]+points[-1][1])/2
            points=[(start_exact[0],points[0][1]),(start_exact[0],y),(end_exact[0],y),(end_exact[0],points[-1][1])]
    else:
        if points[0][1]==points[1][1]:points[1]=(points[1][0],start_exact[1])
        else:points[1]=(start_exact[0],points[1][1])
        points[0]=start_exact
        if points[-1][1]==points[-2][1]:points[-2]=(points[-2][0],end_exact[1])
        else:points[-2]=(end_exact[0],points[-2][1])
        points[-1]=end_exact
    return points
def cardinality(p,side,many=False,optional=False):
    vx,vy=vec[side];px,py=-vy,vx
    def at(d,t=0):return (p[0]+vx*d+px*t,p[1]+vy*d+py*t)
    if many:
        for t in [-9,0,9]:line(at(0,t),at(16),width=1.8)
        pos=29
    else:
        line(at(7,-9),at(7,9),width=1.8);pos=23
    if optional:
        cx,cy=at(pos);draw.add(Ellipse(cx,HEIGHT-cy,6,6,fillColor=colors.white,strokeColor=colors.HexColor('#303438'),strokeWidth=1.8))
    else:line(at(pos,-9),at(pos,9),width=1.8)
paths=[]
edges.sort(key=lambda v:abs(nodes[v['child']]['x']-nodes[v['fk']['parent']]['x'])+abs(nodes[v['child']]['y']-nodes[v['fk']['parent']]['y']))
for ed in edges:
    n,f,sa,sb=ed['child'],ed['fk'],ed['s'],ed['e'];a=port(n,sa);b=port(f['parent'],sb);av=vec[sa];bv=vec[sb]
    aa=(a[0]+av[0]*50,a[1]+av[1]*50);bb=(b[0]+bv[0]*30,b[1]+bv[1]*30);mid=route(aa,bb,sa,sb)
    pts=[a,aa,*mid,bb,b]
    pts=[p for i,p in enumerate(pts) if i==0 or p!=pts[i-1]]
    # Collapse collinear vertices and any redundant outward-and-back stub.
    simple=[]
    for p in pts:
        simple.append(p)
        while len(simple)>=3:
            p0,p1,p2=simple[-3:]
            if abs(p0[0]-p1[0])<1e-8 and abs(p1[0]-p2[0])<1e-8 or abs(p0[1]-p1[1])<1e-8 and abs(p1[1]-p2[1])<1e-8:simple.pop(-2)
            else:break
    pts=simple
    for p,q in zip(pts,pts[1:]):line(p,q)
    subtype=n in ['PERSONA_NATURAL','ORGANIZACION'];optional=any(clean(a) in f['fields'] and '?' in a for a in m[n]['attrs'])
    cardinality(a,sa,many=not subtype,optional=True);cardinality(b,sb,many=False,optional=optional)
    label='Es' if subtype else 'Paga' if n=='PAGO_GASTO' else 'Explica desviación' if n=='CAUSA_DESVIACION_EVENTO' else verbs.get(f['fields'][0],'Se relaciona')
    tw=pdfmetrics.stringWidth(label,'Body',15)+18
    candidates=[]
    for p,q in zip(pts[2:-2],pts[3:-1]):
        if abs(p[1]-q[1])<0.1 and abs(p[0]-q[0])>tw+35:
            cx,cy=(p[0]+q[0])/2,p[1]
            if all(abs(cx-lx)>tw/2+lw/2+10 or abs(cy-ly)>30 for lx,ly,_,lw in labels):candidates.append((abs(p[0]-q[0]),cx,cy))
    if candidates:
        _,cx,cy=max(candidates);labels.append((cx,cy,label,tw))
    paths.append({'child':n,'parent':f['parent'],'fields':f['fields'],'keys':f['keys'],'points':pts})
# Conventional SQL-table figures: key | attribute | datatype, matching the supplied reference.
for n,b in nodes.items():
    x,y,h=b['x'],b['y'],b['h'];draw.add(Rect(x,HEIGHT-y-h,BW,h,rx=8,ry=8,fillColor=colors.HexColor('#e4e7eb'),strokeColor=colors.HexColor('#42464b'),strokeWidth=1.6))
    draw.add(Rect(x,HEIGHT-y-HH,BW,HH,fillColor=colors.HexColor('#d5dbe2'),strokeColor=colors.HexColor('#42464b'),strokeWidth=1))
    text(x+BW/2,y+HH/2,n,size=18,anchor='middle')
    line((x+64,y+HH),(x+64,y+h),width=0.8,color='#9ca3ab');line((x+335,y+HH),(x+335,y+h),width=0.8,color='#9ca3ab')
    for i,a in enumerate(m[n]['attrs']):
        yy=y+HH+RH/2+i*RH;k=[];c=clean(a)
        if c in m[n]['pk']:k.append('PK')
        if '*' in a:k.append('FK')
        text(x+7,yy,'/'.join(k),size=15);text(x+71,yy,a.replace('*',''),size=16);text(x+342,yy,sqltype(a,n),size=15)
for cx,cy,label,tw in labels:
    draw.add(Rect(cx-tw/2,HEIGHT-cy-12,tw,24,fillColor=colors.white,strokeColor=None));text(cx,cy,label,size=15,anchor='middle')
text(PAD,HEIGHT-45,'PK = clave primaria   FK = clave foránea   ? = atributo opcional   | = uno   O = cero   pata de cuervo = muchos',size=18)
text(WIDTH-PAD,HEIGHT-45,'18 tablas · 25 referencias · Tipos SQL propuestos',size=18,anchor='end')
assert len(nodes)==18 and len(paths)==25
renderSVG.drawToFile(draw,str(D/'mr_completo.svg'));tmp=W/'mr_completo_canvas.pdf';c=canvas.Canvas(str(tmp),pagesize=(WIDTH,HEIGHT));renderPDF.draw(draw,c,0,0);c.save();pd=pdfium.PdfDocument(str(tmp));pd[0].render(scale=1.5).to_pil().save(D/'mr_completo.png')
pw,ph=landscape(A1);c=canvas.Canvas(str(O/'modelo_completo_A1.pdf'),pagesize=(pw,ph));sc=min((pw-65)/WIDTH,(ph-65)/HEIGHT);c.translate((pw-WIDTH*sc)/2,(ph-HEIGHT*sc)/2);c.scale(sc,sc);renderPDF.draw(draw,c,0,0);c.save()
(W/'conectores_relacionales.json').write_text(json.dumps({'width':WIDTH,'height':HEIGHT,'style':'SQL tables with crow-foot connectors','references':paths},indent=2),encoding='utf8')
(W/'tipos_datos_modelo.json').write_text(json.dumps({n:{clean(a):sqltype(a,n) for a in t['attrs']} for n,t in m.items()},indent=2),encoding='utf8')
print(json.dumps({'width':WIDTH,'height':HEIGHT,'tables':18,'references':25}))
