from pathlib import Path
import json,math,shutil
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing,Rect,Line,Polygon,Ellipse,String
from reportlab.graphics import renderSVG,renderPDF
import pypdfium2 as pdfium
ROOT=Path(__file__).resolve().parents[2];WORK=ROOT/'fuentes';DIAG=ROOT/'diagramas'
DIAG.mkdir(exist_ok=True)
for name,file in [('Body','arial.ttf'),('Bold','arialbd.ttf')]:pdfmetrics.registerFont(TTFont(name,str(Path('C:/Windows/Fonts')/file)))
class Diagram:
    def __init__(self,w,h): self.w=w; self.h=h; self.d=Drawing(w,h)
    def rect(self,x,y,w,h,label=None,fill='#ffffff',double=False,round=False,size=12):
        self.d.add(Rect(x,self.h-y-h,w,h,rx=7 if round else 0,ry=7 if round else 0,fillColor=colors.HexColor(fill),strokeColor=colors.black,strokeWidth=1))
        if double: self.d.add(Rect(x+4,self.h-y-h+4,w-8,h-8,fillColor=None,strokeColor=colors.black,strokeWidth=1))
        if label:self.text(x+w/2,y+h/2,label,size=size)
    def text(self,x,y,text,size=11,anchor='middle',bold=False):
        lines=text.split('\n')
        for i,t in enumerate(lines): self.d.add(String(x,self.h-y+(len(lines)-1)/2*size*1.2-i*size*1.2-3,t,fontName='Bold' if bold else 'Body',fontSize=size,textAnchor=anchor,fillColor=colors.black))
    def line(self,x1,y1,x2,y2,arrow=False,dash=False):
        self.d.add(Line(x1,self.h-y1,x2,self.h-y2,strokeColor=colors.black,strokeWidth=1,strokeDashArray=[4,3] if dash else None))
        if arrow:
            import math
            a=math.atan2(y2-y1,x2-x1); k=7; b=3
            pts=[x2,self.h-y2,x2-k*math.cos(a)+b*math.sin(a),self.h-(y2-k*math.sin(a)-b*math.cos(a)),x2-k*math.cos(a)-b*math.sin(a),self.h-(y2-k*math.sin(a)+b*math.cos(a))]
            self.d.add(Polygon(pts,fillColor=colors.black,strokeColor=colors.black))
    def path(self,pts,arrow=False,dash=False):
        for i,(a,b) in enumerate(zip(pts,pts[1:])):self.line(*a,*b,arrow=arrow and i==len(pts)-2,dash=dash)
    def diamond(self,x,y,w,h,label,size=10,double=False):
        self.d.add(Polygon([x-w/2,self.h-y,x,self.h-y+h/2,x+w/2,self.h-y,x,self.h-y-h/2],fillColor=colors.white,strokeColor=colors.black))
        if double:self.d.add(Polygon([x-w/2+4,self.h-y,x,self.h-y+h/2-4,x+w/2-4,self.h-y,x,self.h-y-h/2+4],fillColor=None,strokeColor=colors.black))
        self.text(x,y,label,size=size)
    def oval(self,x,y,w,h,label,double=False,dash=False,key=False,partial=False,size=11):
        self.d.add(Ellipse(x,self.h-y,w/2,h/2,fillColor=colors.white,strokeColor=colors.black,strokeDashArray=[4,3] if dash else None))
        if double:self.d.add(Ellipse(x,self.h-y,(w-8)/2,(h-8)/2,fillColor=None,strokeColor=colors.black))
        self.text(x,y,label,size=size)
        if key or partial:
            tw=pdfmetrics.stringWidth(label,'Body',size)
            self.d.add(Line(x-tw/2,self.h-y-6,x+tw/2,self.h-y-6,strokeColor=colors.black,strokeDashArray=[3,2] if partial else None))
    def circle(self,x,y,r,label='',end=False):
        self.d.add(Ellipse(x,self.h-y,r,r,fillColor=colors.white,strokeColor=colors.black,strokeWidth=2.4 if end else 1))
        if label:self.text(x,y,label,size=9)
    def save(self,name):
        renderSVG.drawToFile(self.d,str(DIAG/(name+'.svg')))
        c=__import__('reportlab.pdfgen.canvas',fromlist=['Canvas']).Canvas(str(WORK/(name+'.pdf')),pagesize=(self.w,self.h))
        renderPDF.draw(self.d,c,0,0);c.save()
        p=pdfium.PdfDocument(str(WORK/(name+'.pdf')))
        p[0].render(scale=2).to_pil().save(DIAG/(name+'.png'))


model=json.loads((WORK/'modelo_relacional.json').read_text(encoding='utf8'))
labels={'VERSION_PRESUPUESTO':'Versión presupuesto','LINEA_PRESUPUESTO':'Línea presupuesto','REGISTRO_ORIGEN':'Registro origen','PAGO_GASTO':'Pago gasto','CORTE_VENTA':'Corte venta','MOVIMIENTO_TICKETERA':'Movimiento ticketera','PERSONA_NATURAL':'Persona natural','ORGANIZACION':'Organización'}
def lab(n):return labels.get(n,n.replace('_',' ').capitalize())
def entity(z,n,x,y,w=170):
    z.rect(x,y+20,w,26,lab(n),double=n=='LINEA_PRESUPUESTO',size=12)
    key='nro_linea' if n=='LINEA_PRESUPUESTO' else model[n]['pk'][0]
    z.line(x+w/2,y+20,x+w/2,y+14);z.oval(x+w/2,y+6,w-10,20,key,key=n!='LINEA_PRESUPUESTO',partial=n=='LINEA_PRESUPUESTO',size=10)
relations=[]
skip={'EVENTO_ARTISTA','PERSONA_NATURAL','ORGANIZACION','CAUSA_DESVIACION_EVENTO'}
for n,t in model.items():
    if n in skip:continue
    for fk in t['fks']:
        optional=any(a.replace('*','').replace('?','') in fk['fields'] and '?' in a for a in t['attrs'])
        parent=fk['parent'];weak=n=='LINEA_PRESUPUESTO' and parent=='VERSION_PRESUPUESTO'
        pc='(0,1)' if n=='LIQUIDACION' and parent=='EVENTO' else '(0,N)'
        # Liquidación única por evento/ticketera: ambos vínculos por separado son 1:N.
        if n=='LIQUIDACION':pc='(0,N)'
        verb={'id_recinto':'Se realiza en','codigo_proyecto':'Corresponde a','id_categoria':'Se clasifica en','id_contraparte':'Se relaciona con','id_version':'Identificada por','id_gasto':'Documenta','id_ticketera':'Reportado por','id_liquidacion':'Se imputa a'}.get(fk['fields'][0],'Se relaciona')
        if n=='PAGO_GASTO':verb='Paga'
        verb={'Se realiza en':'Alberga','Corresponde a':'Asigna','Se clasifica en':'Clasifica','Se relaciona con':'Vincula','Identificada por':'Identifica','Reportado por':'Reporta','Se imputa a':'Imputa'}.get(verb,verb)
        relations.append((n,parent,verb,'(0,1)' if optional else '(1,1)',pc,weak))
relations.insert(1,('EVENTO','ARTISTA','Presenta','(0,N)','(0,N)',False))
for pg,rows in enumerate([relations[:10],relations[10:]],1):
    z=Diagram(600,710)
    for j,(child,parent,verb,cc,pc,weak) in enumerate(rows):
        y=12+j*61;entity(z,child,8,y);entity(z,parent,422,y)
        yy=y+33;z.line(178,yy,257,yy);z.line(343,yy,422,yy);z.diamond(300,yy,86,30,verb.replace(' ','\n',1),size=9,double=weak)
        if weak:z.line(178,yy+3,257,yy+3)
        z.text(214,yy-11,cc,size=11);z.text(386,yy-11,pc,size=11)
    z.text(300,700,'Participación min/máx junto a cada entidad. Entidades repetidas = misma definición.',size=10)
    z.save(f'eer_{pg}')
z=Diagram(600,670)
z.rect(220,112,160,36,'Contraparte',size=14)
for x,y,w,t,opts in [(95,58,158,'id_contraparte',{'key':True}),(300,50,110,'nombre',{}),(505,58,150,'identificador',{}),(510,180,105,'pais',{})]:
    start=(240,112) if x<300 and y<130 else (360,112) if x>300 and y<130 else (300,112) if x==300 else (220,140) if x<300 else (380,140)
    z.line(*start,x,y);z.oval(x,y,w,30,t,size=12,**opts)
z.rect(20,168,130,32,'Evento',size=13);z.line(85,200,85,219);z.oval(95,235,175,28,'causas_desviacion',double=True,size=11)
z.line(296,148,296,235);z.line(304,148,304,235)
z.d.add(Polygon([270,670-270,330,670-270,300,670-230],fillColor=colors.white,strokeColor=colors.black));z.text(300,253,'ISA',size=12)
z.line(270,270,125,318);z.line(330,270,475,318);z.text(300,290,'Total y disjunta',size=12)
z.rect(40,318,170,32,'Persona natural',size=13);z.rect(390,318,170,32,'Organización',size=13)
for x,t in [(85,'nombres'),(225,'apellidos')]:z.line(125,350,x,390);z.oval(x,400,120,28,t,size=12)
z.line(475,350,475,390);z.oval(475,400,145,28,'razon_social',size=12)
z.rect(15,450,100,32,'Recinto',size=12);z.line(115,466,188,466);z.oval(245,466,112,30,'direccion',size=12)
for x,t in [(70,'calle'),(205,'numero'),(340,'comuna'),(475,'ciudad')]:z.line(245,481,x,516);z.oval(x,531,110,26,t,size=12)
z.rect(15,593,100,30,'Evento',size=12);z.line(115,608,141,608);z.oval(210,608,134,28,'resultado_final',dash=True,size=11)
z.rect(355,593,90,30,'Gasto',size=12);z.line(445,608,468,608);z.oval(528,608,118,28,'saldo_gasto',dash=True,size=11)
z.text(300,651,'Vínculo Presenta: orden_presentacion y honorario_estimado_clp (lámina 1).',size=11)
# Atributos del vínculo dibujados explícitamente en un pequeño rombo con óvalos.
# Aprovechar el espacio entre dirección y derivados.
z.save('eer_3')
# Añadir los atributos de relación a la lámina 1, encima de la última fila libre.
# La primera lámina usa 10 filas (hasta y=594), quedando 65 unidades libres.
z=Diagram(600,710)
for j,(child,parent,verb,cc,pc,weak) in enumerate(relations[:10]):
    y=12+j*61;entity(z,child,8,y);entity(z,parent,422,y);yy=y+33
    z.line(178,yy,257,yy);z.line(343,yy,422,yy);z.diamond(300,yy,86,30,verb.replace(' ','\n',1),size=9,double=weak)
    if weak:z.line(178,yy+3,257,yy+3)
    z.text(214,yy-11,cc,size=11);z.text(386,yy-11,pc,size=11)
z.diamond(300,659,82,30,'Presenta',size=10)
for x,w,t in [(105,182,'orden_presentacion'),(492,196,'honorario_estimado_clp')]:
    z.line(259 if x<300 else 341,659,x+(w/2 if x<300 else -w/2),659);z.oval(x,659,w,28,t,size=10)
z.text(300,700,'El rombo inferior desarrolla los atributos del vínculo Evento–Artista.',size=10);z.save('eer_1')
# BPMN portrait layout with operational IDs used by CRUD.
z=Diagram(600,740);z.rect(8,8,584,724)
for x,t in [(12,'Área originadora'),(205,'Contabilidad'),(398,'Tesorería')]:z.rect(x,36,193,687,fill='#fafafa' if x!=205 else '#ffffff');z.text(x+96,53,t,size=12,bold=True)
z.text(300,22,'Productora de Eventos',size=14,bold=True)
z.circle(108,80,9);z.rect(37,99,142,39,'T01 Registrar show\ny presupuesto',round=True,size=11);z.line(108,89,108,99,arrow=True)
z.rect(37,163,142,37,'T02 Entregar\nantecedente',round=True,size=11);z.line(108,138,108,163,arrow=True)
z.rect(226,163,150,37,'T03 Cargar origen',round=True,size=11);z.line(179,181,226,181,arrow=True)
z.rect(226,221,150,37,'T04 Resolver\nproyecto e integridad',round=True,size=11);z.line(301,200,301,221,arrow=True)
z.diamond(301,299,56,38,'G1',size=12);z.line(301,258,301,280,arrow=True)
z.rect(32,280,152,40,'T11 Registrar\nobservación',round=True,size=11);z.line(273,299,184,299,arrow=True);z.text(225,288,'No',size=11)
z.circle(108,348,10,end=True);z.line(108,320,108,338,arrow=True)
z.rect(226,345,150,37,'T05 Conciliar\nantecedentes',round=True,size=11);z.line(301,318,301,345,arrow=True);z.text(316,331,'Sí',size=10)
z.diamond(301,420,56,38,'G2',size=12);z.line(301,382,301,401,arrow=True)
z.rect(226,468,150,40,'T06 Preparar gasto\no vincular existente',round=True,size=11)
z.path([(273,420),(212,420),(212,487),(226,487)],arrow=True);z.text(233,407,'Existente',size=9)
z.path([(329,420),(389,420),(389,487),(376,487)],arrow=True);z.text(360,407,'Nuevo',size=9)
z.path([(301,439),(301,452),(194,452),(194,299),(184,299)],arrow=True);z.text(274,450,'Duda',size=9)
z.rect(421,468,150,40,'T07 Revisar\nrespaldo y atribución',round=True,size=11);z.line(376,488,421,488,arrow=True)
z.diamond(496,548,56,38,'G3',size=12);z.line(496,508,496,529,arrow=True)
z.path([(468,548),(404,548),(404,323),(184,323),(184,307)],arrow=True);z.text(438,537,'No',size=10)
z.rect(421,588,150,35,'T08 Validar gasto',round=True,size=11);z.line(496,567,496,588,arrow=True);z.text(510,579,'Sí',size=10)
z.rect(421,645,150,40,'T09 Registrar ingresos,\nticketing y pagos',round=True,size=11);z.line(496,623,496,645,arrow=True)
z.rect(226,645,150,40,'T10 Consolidar\ny revisar resultado',round=True,size=11);z.line(421,665,376,665,arrow=True)
z.circle(108,665,10,end=True);z.line(226,665,118,665,arrow=True)
z.text(300,712,'G1 integridad · G2 identidad económica · G3 revisión independiente',size=10);z.save('bpmn')
# Las imágenes finales se organizan por tipo en el repositorio.
for name,folder in [('bpmn','bpmn'),('eer_1','eer'),('eer_2','eer'),('eer_3','eer')]:
    (DIAG/folder).mkdir(exist_ok=True)
    for ext in ['png','svg']:(DIAG/(name+'.'+ext)).replace(DIAG/folder/(name+'.'+ext))
print('Diagrams generated: BPMN + 3 EER')
