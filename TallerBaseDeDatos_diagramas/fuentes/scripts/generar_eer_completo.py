from pathlib import Path
import math,json
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing,Rect,Line,Ellipse,Polygon,String
from reportlab.graphics import renderSVG,renderPDF
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A0,landscape
import pypdfium2 as pdfium
ROOT=Path(__file__).resolve().parents[2];W=ROOT/'fuentes';O=ROOT/'diagramas/eer';D=O
D.mkdir(parents=True,exist_ok=True)
for name,file in [('Body','arial.ttf'),('Bold','arialbd.ttf')]:pdfmetrics.registerFont(TTFont(name,str(Path('C:/Windows/Fonts')/file)))
m=json.loads((W/'modelo_relacional.json').read_text(encoding='utf8'))
pos={'EVENTO':(3500,2700),'GASTO':(5100,2700),'CONTRAPARTE':(6700,2100),'ORGANIZACION':(7700,3100),'PERSONA_NATURAL':(7500,900),'RECINTO':(3100,950),'ARTISTA':(4500,900),'VERSION_PRESUPUESTO':(2200,2100),'LINEA_PRESUPUESTO':(2300,3500),'CATEGORIA':(3300,4300),'REGISTRO_ORIGEN':(5200,4400),'PAGO_GASTO':(6500,3800),'INGRESO':(5400,1400),'LIQUIDACION':(6800,4500),'MOVIMIENTO_TICKETERA':(8300,3900),'CORTE_VENTA':(8500,2450)}
WIDTH=10000;HEIGHT=5700;draw=Drawing(WIDTH,HEIGHT);occupied=[];connections=[];relations=[]
draw.add(Rect(0,0,WIDTH,HEIGHT,fillColor=colors.white,strokeColor=None))
ink=colors.black;outline=colors.black
def text(x,y,s,size=29,bold=False):
    draw.add(String(x,HEIGHT-y-9,s,fontName='Bold' if bold else 'Body',fontSize=size,textAnchor='middle',fillColor=ink))
def line(a,b,double=False,dash=False):
    draw.add(Line(a[0],HEIGHT-a[1],b[0],HEIGHT-b[1],strokeColor=ink,strokeWidth=2,strokeDashArray=[9,6] if dash else None))
    if double:
        dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy);ox=-dy/length*6;oy=dx/length*6
        draw.add(Line(a[0]+ox,HEIGHT-a[1]-oy,b[0]+ox,HEIGHT-b[1]-oy,strokeColor=ink,strokeWidth=2))
def rect_edge(n,p):
    x,y=pos[n];dx=p[0]-x;dy=p[1]-y;t=min(190/abs(dx) if dx else 1e9,48/abs(dy) if dy else 1e9)
    return x+t*dx,y+t*dy
def diamond_edge(c,p):
    dx=p[0]-c[0];dy=p[1]-c[1];t=1/(abs(dx)/145+abs(dy)/65)
    return c[0]+t*dx,c[1]+t*dy
def oval_edge(c,p,w=360,h=76):
    dx=p[0]-c[0];dy=p[1]-c[1];t=1/math.sqrt((dx/(w/2))**2+(dy/(h/2))**2)
    return c[0]+t*dx,c[1]+t*dy
def collision(c,w,h):
    return any(abs(c[0]-x)<(w+ww)/2+30 and abs(c[1]-y)<(h+hh)/2+30 for x,y,ww,hh in occupied)
def distance_segment(p,a,b):
    dx=b[0]-a[0];dy=b[1]-a[1];t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)))
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
for n,(x,y) in pos.items():occupied.append((x,y,380,96))
skip={'EVENTO_ARTISTA','PERSONA_NATURAL','ORGANIZACION','CAUSA_DESVIACION_EVENTO'}
verbs={'id_recinto':'Alberga','codigo_proyecto':'Asigna','id_version':'Identifica','id_categoria':'Clasifica','id_contraparte':'Vincula','id_gasto':'Documenta','id_ticketera':'Reporta','id_liquidacion':'Imputa'}
for n,t in m.items():
    if n in skip:continue
    for f in t['fks']:
        parent=f['parent'];optional=any(a.endswith('?') and a.replace('*','').replace('?','') in f['fields'] for a in t['attrs'])
        relations.append((n,parent,'Paga' if n=='PAGO_GASTO' else verbs[f['fields'][0]],'(0,1)' if optional else '(1,1)','(0,N)',n=='LINEA_PRESUPUESTO' and parent=='VERSION_PRESUPUESTO'))
relations.append(('EVENTO','ARTISTA','Presenta','(0,N)','(0,N)',False))
placements=[]
for child,parent,label,cc,pc,weak in relations:
    a=pos[child];b=pos[parent]
    options=[]
    for f in [.5,.4,.6,.3,.7]:
        c=(a[0]+f*(b[0]-a[0]),a[1]+f*(b[1]-a[1]))
        if not collision(c,290,130):options.append((abs(f-.5),c))
    if not options:raise RuntimeError(('No space for relationship',child,parent))
    _,c=min(options);occupied.append((*c,290,130));placements.append((child,parent,label,cc,pc,weak,c))
    connections.extend([(a,c),(c,b)])
# ISA sits between supertype and its two subtypes, away from attribute fans.
isa=(7550,2000);occupied.append((*isa,200,150))
connections.extend([(pos['CONTRAPARTE'],isa),(isa,pos['PERSONA_NATURAL']),(isa,pos['ORGANIZACION'])])
attrs=[]
for n in pos:
    t=m[n];fk={a for f in t['fks'] for a in f['fields']};keys=t['pk'] if n not in ['PERSONA_NATURAL','ORGANIZACION'] else []
    stored=[a.replace('*','') for a in t['attrs'] if a.replace('*','').replace('?','') not in fk]
    if n=='LINEA_PRESUPUESTO':stored=['nro_linea']+[a for a in stored if a!='nro_linea']
    if n=='RECINTO':stored=[a for a in stored if a not in ['calle','numero','comuna','ciudad']]+['direccion']
    if n=='EVENTO':stored+=['causas_desviacion','resultado_final']
    if n=='GASTO':stored+=['saldo_gasto']
    center=pos[n]
    neighbors=[c if child==n else c for child,parent,_,_,_,_,c in placements if child==n or parent==n]
    if n in ['CONTRAPARTE','PERSONA_NATURAL','ORGANIZACION']:neighbors.append(isa)
    angles=sorted(math.atan2(y-center[1],x-center[0])%(2*math.pi) for x,y in neighbors)
    gaps=[(((angles[(i+1)%len(angles)]-ang)%(2*math.pi)),ang) for i,ang in enumerate(angles)]
    gap,start=max(gaps);preferred=(start+gap/2)%(2*math.pi)
    for i,s in enumerate(stored):
        choices=[]
        for radius in [430,560,700,850,1000,1150,1350,1550,1800]:
            for k in range(72):
                angle=2*math.pi*k/72;c=(center[0]+radius*math.cos(angle),center[1]+radius*math.sin(angle))
                if not(250<c[0]<WIDTH-250 and 200<c[1]<HEIGHT-400) or collision(c,360,76):continue
                nearline=min(distance_segment(c,a,b) for a,b in connections)
                if nearline<110:continue
                if any(distance_segment((0,0),((center[0]-ac[0])/200,(center[1]-ac[1])/58),((c[0]-ac[0])/200,(c[1]-ac[1])/58))<1 for _,_,ac,_,_ in attrs):continue
                diff=abs((angle-preferred+math.pi)%(2*math.pi)-math.pi)
                other_entities=min(math.hypot(c[0]-x,c[1]-y) for nn,(x,y) in pos.items() if nn!=n)
                if other_entities<300:continue
                score=radius+diff*160+max(0,420-other_entities)*4
                choices.append((score,c))
        if not choices:raise RuntimeError(('No attribute space',n,s))
        _,c=min(choices);occupied.append((*c,360,76));attrs.append((n,s,c,s.replace('?','') in keys,n=='LINEA_PRESUPUESTO' and s=='nro_linea'));connections.append((center,c))
        if s=='direccion':
            for j,part in enumerate(['calle','numero','comuna','ciudad']):
                q=(c[0]-450+j*300,c[1]+230)
                while collision(q,270,76):q=(q[0],q[1]+110)
                occupied.append((*q,270,76));attrs.append((None,part,q,False,False));connections.append((c,q))
                line(oval_edge(c,q),oval_edge(q,c,w=270))
for child,parent,label,cc,pc,weak,c in placements:
    for n,card in [(child,cc),(parent,pc)]:
        p=rect_edge(n,c);q=diamond_edge(c,pos[n]);line(p,q,double=weak and n==child)
        dx=q[0]-p[0];dy=q[1]-p[1];length=math.hypot(dx,dy)
        along,offset=(320,-55) if n=='EVENTO' and child=='CORTE_VENTA' else (105,35)
        cp=(p[0]+dx/length*along-dy/length*offset,p[1]+dy/length*along+dx/length*offset);text(*cp,card,size=25)
    x,y=c;draw.add(Polygon([x-145,HEIGHT-y,x,HEIGHT-y+65,x+145,HEIGHT-y,x,HEIGHT-y-65],fillColor=colors.white,strokeColor=outline,strokeWidth=2.5))
    if weak:draw.add(Polygon([x-136,HEIGHT-y,x,HEIGHT-y+57,x+136,HEIGHT-y,x,HEIGHT-y-57],fillColor=None,strokeColor=outline,strokeWidth=2))
    text(x,y,label,size=29)
for n in ['CONTRAPARTE','PERSONA_NATURAL','ORGANIZACION']:
    line(rect_edge(n,isa),oval_edge(isa,pos[n],w=180,h=150),double=n=='CONTRAPARTE')
x,y=isa;draw.add(Polygon([x-95,HEIGHT-y-60,x+95,HEIGHT-y-60,x,HEIGHT-y+85],fillColor=colors.white,strokeColor=outline,strokeWidth=2.5));text(x,y,'ISA',size=30);text(x,y+110,'Total y disjunta',size=27)
for n,s,c,key,partial in attrs:
    if n:line(rect_edge(n,c),oval_edge(c,pos[n]))
    x,y=c;w=270 if n is None else 360
    draw.add(Ellipse(x,HEIGHT-y,w/2,38,fillColor=colors.white,strokeColor=outline,strokeWidth=2.5,strokeDashArray=[9,6] if s in ['resultado_final','saldo_gasto'] else None))
    if s=='causas_desviacion':draw.add(Ellipse(x,HEIGHT-y,w/2-7,31,fillColor=None,strokeColor=outline,strokeWidth=2))
    size=min(29,(w-24)/max(1,pdfmetrics.stringWidth(s,'Body',29))*29);text(x,y,s,size=size)
    if key or partial:
        tw=pdfmetrics.stringWidth(s,'Body',size);line((x-tw/2,y+18),(x+tw/2,y+18),dash=partial)
for n,(x,y) in pos.items():
    draw.add(Rect(x-190,HEIGHT-y-48,380,96,fillColor=colors.white,strokeColor=outline,strokeWidth=2.5))
    if n=='LINEA_PRESUPUESTO':draw.add(Rect(x-183,HEIGHT-y-41,366,82,fillColor=None,strokeColor=outline,strokeWidth=2))
    text(x,y,n.title().replace('_',' '),size=29,bold=True)
presenta=next(c for _,_,label,_,_,_,c in placements if label=='Presenta')
for j,s in enumerate(['orden_presentacion','honorario_estimado_clp']):
    c=(presenta[0]-300+j*600,presenta[1]-260);line(diamond_edge(presenta,c),oval_edge(c,presenta,w=420));draw.add(Ellipse(c[0],HEIGHT-c[1],210,38,fillColor=colors.white,strokeColor=outline,strokeWidth=2.5));text(*c,s,size=26)
text(WIDTH/2,HEIGHT-180,'Chen · 16 entidades · 21 relaciones · ISA total y disjunta · cardinalidades (mínimo,máximo)',size=32)
text(WIDTH/2,HEIGHT-110,'Clave subrayada · clave parcial discontinua · atributo multivaluado doble · atributo derivado discontinuo · dirección compuesta',size=29)
renderSVG.drawToFile(draw,str(D/'eer_completo.svg'));tmp=W/'eer_completo_canvas.pdf';cv=canvas.Canvas(str(tmp),pagesize=(WIDTH,HEIGHT));renderPDF.draw(draw,cv,0,0);cv.save();pd=pdfium.PdfDocument(tmp);pd[0].render(scale=.75).to_pil().save(D/'eer_completo.png');pd[0].render(scale=.4).to_pil().save(W/'eer_informe.png')
pw,ph=landscape(A0);cv=canvas.Canvas(str(O/'modelo_completo_A0.pdf'),pagesize=(pw,ph));sc=min((pw-60)/WIDTH,(ph-60)/HEIGHT);cv.translate((pw-WIDTH*sc)/2,(ph-HEIGHT*sc)/2);cv.scale(sc,sc);renderPDF.draw(draw,cv,0,0);cv.save()
(W/'relaciones_conceptuales.json').write_text(json.dumps([{'child':a,'parent':b,'relationship':label,'child_cardinality':cc,'parent_cardinality':pc,'diamond':c,'style':'Chen direct straight segments'} for a,b,label,cc,pc,weak,c in placements],ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'entities':len(pos),'relationships':len(placements),'attributes':len(attrs),'style':'Chen with direct straight lines'}))

