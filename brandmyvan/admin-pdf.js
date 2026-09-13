(function(root){
 const A4={width:1240,height:1754},MODEL={length:4.75,width:1.922155520079944,height:2.0613367643228018};
 const euro=n=>new Intl.NumberFormat('fr-FR',{style:'currency',currency:'EUR',maximumFractionDigits:0}).format(n);
 function rounded(ctx,x,y,w,h,r=14){ctx.beginPath();ctx.roundRect(x,y,w,h,r);}
 function wrap(ctx,text,x,y,maxWidth,lineHeight,maxLines=20){
  const words=String(text).split(/\s+/);let line='',lines=0;
  for(const word of words){const next=line?line+' '+word:word;if(ctx.measureText(next).width>maxWidth&&line){ctx.fillText(line,x,y);y+=lineHeight;lines++;line=word;if(lines>=maxLines)return y;}else line=next;}
  if(line&&lines<maxLines){ctx.fillText(line,x,y);y+=lineHeight;}return y;
 }
 function contain(ctx,image,x,y,w,h){
  const ratio=Math.min(w/image.width,h/image.height),dw=image.width*ratio,dh=image.height*ratio;
  ctx.drawImage(image,x+(w-dw)/2,y+(h-dh)/2,dw,dh);
 }
 function image(src){return new Promise((resolve,reject)=>{const i=new Image();i.onload=()=>resolve(i);i.onerror=()=>reject(Error('Image illisible'));i.src=src;});}
 function dimensions(r){
  const horizontal=(r.placement?.width||0)*(r.placement?.side==='rear'?MODEL.width:MODEL.length)*100;
  const vertical=(r.placement?.height||0)*MODEL.height*100;
  return {horizontal:Math.round(horizontal),vertical:Math.round(vertical)};
 }
 function buildPdf(jpeg,width,height){
  const ascii=s=>new TextEncoder().encode(s),join=parts=>{const size=parts.reduce((n,p)=>n+p.length,0),out=new Uint8Array(size);let at=0;for(const p of parts){out.set(p,at);at+=p.length;}return out;};
  const stream=ascii('q\n595.28 0 0 841.89 0 0 cm\n/Im0 Do\nQ\n');
  const objects=[
   ascii('1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n'),
   ascii('2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n'),
   ascii('3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595.28 841.89] /Resources << /XObject << /Im0 4 0 R >> >> /Contents 5 0 R >>\nendobj\n'),
   join([ascii('4 0 obj\n<< /Type /XObject /Subtype /Image /Width '+width+' /Height '+height+' /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length '+jpeg.length+' >>\nstream\n'),jpeg,ascii('\nendstream\nendobj\n')]),
   join([ascii('5 0 obj\n<< /Length '+stream.length+' >>\nstream\n'),stream,ascii('endstream\nendobj\n')])
  ];
  const header=ascii('%PDF-1.4\n%BMV1\n'),offsets=[];let cursor=header.length;
  for(const o of objects){offsets.push(cursor);cursor+=o.length;}
  const xref=ascii('xref\n0 6\n0000000000 65535 f \n'+offsets.map(n=>String(n).padStart(10,'0')+' 00000 n \n').join('')+'trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n'+cursor+'\n%%EOF\n');
  return join([header,...objects,xref]);
 }
 async function createPartnerPdf(r){
  const [logo,artwork]=await Promise.all([image(r.logo_png),image(r.artwork_png)]),c=document.createElement('canvas');c.width=A4.width;c.height=A4.height;
  const ctx=c.getContext('2d');ctx.fillStyle='#f5f3ed';ctx.fillRect(0,0,c.width,c.height);
  ctx.fillStyle='#111';ctx.fillRect(0,0,c.width,155);ctx.font='900 48px Arial';ctx.fillStyle='#fff';ctx.fillText('BRAND',70,96);const bw=ctx.measureText('BRAND').width;ctx.fillStyle='#dcff29';ctx.fillRect(68+bw,49,194,67);ctx.fillStyle='#111';ctx.fillText('MYVAN',82+bw,98);
  ctx.fillStyle='#fff';ctx.textAlign='right';ctx.font='700 24px Arial';ctx.fillText('FICHE PARTENAIRE',1170,75);ctx.font='20px Arial';ctx.fillText('Référence '+r.id,1170,108);ctx.textAlign='left';
  ctx.fillStyle='#111';ctx.font='900 54px Arial';ctx.fillText(r.company,70,245);ctx.font='25px Arial';ctx.fillStyle='#555';ctx.fillText(r.email,70,286);
  const d=dimensions(r),status=r.status==='confirmed'?'Emplacement confirmé':r.status==='declined'?'Demande refusée':'Demande à étudier',payment=r.payment_status==='paid'?'Paiement reçu':'Paiement non reçu';
  const cards=[['EMPLACEMENT',r.spot_id],['FORMAT ESTIMÉ',d.horizontal+' × '+d.vertical+' cm'],['PRIX',euro(r.price_eur)],['DURÉE',r.duration_months+' mois']];
  cards.forEach(([label,value],i)=>{const x=70+i*277;rounded(ctx,x,335,252,112);ctx.fillStyle='#fff';ctx.fill();ctx.strokeStyle='#aaa';ctx.stroke();ctx.fillStyle='#666';ctx.font='700 17px Arial';ctx.fillText(label,x+18,370);ctx.fillStyle='#111';ctx.font='900 28px Arial';ctx.fillText(value,x+18,416);});
  ctx.font='700 21px Arial';ctx.fillStyle='#111';ctx.fillText(status+'  ·  '+payment+'  ·  '+({waiting:'En attente',ready_to_print:'Prête à imprimer',printed:'Imprimée',installed:'Posée sur le van'})[r.production_status],70,500);
  const drawCard=(x,title,img)=>{rounded(ctx,x,550,530,510);ctx.fillStyle='#fff';ctx.fill();ctx.strokeStyle='#999';ctx.stroke();ctx.fillStyle='#111';ctx.font='800 22px Arial';ctx.fillText(title,x+24,594);contain(ctx,img,x+28,630,474,390);};
  drawCard(70,'LOGO FOURNI',logo);drawCard(640,'APERÇU DU PLACEMENT',artwork);
  ctx.fillStyle='#111';ctx.font='900 31px Arial';ctx.fillText('Informations du placement',70,1145);ctx.font='23px Arial';ctx.fillStyle='#444';
  const side={left:'côté gauche',right:'côté droit',rear:'portes arrière'}[r.placement?.side]||r.placement?.side;
  let y=1195;y=wrap(ctx,'Zone '+r.spot_id+' · '+side+' · format estimé '+d.horizontal+' × '+d.vertical+' cm.',70,y,1100,36);
  y=wrap(ctx,'Le format est calculé à partir du modèle du van. Les dimensions, les couleurs et le fichier d’impression doivent être validés avant fabrication.',70,y+15,1100,36);
  ctx.strokeStyle='#aaa';ctx.beginPath();ctx.moveTo(70,1435);ctx.lineTo(1170,1435);ctx.stroke();
  ctx.fillStyle='#111';ctx.font='800 23px Arial';ctx.fillText('Suivi',70,1485);ctx.font='21px Arial';ctx.fillStyle='#555';
  ctx.fillText('Demande reçue le '+new Date(r.created_at).toLocaleDateString('fr-FR'),70,1527);
  if(r.paid_at)ctx.fillText('Paiement enregistré le '+new Date(r.paid_at).toLocaleDateString('fr-FR'),70,1564);
  ctx.font='18px Arial';ctx.fillStyle='#666';ctx.fillText('Document généré le '+new Date().toLocaleDateString('fr-FR')+' depuis l’espace privé Brand My Van.',70,1660);
  const data=c.toDataURL('image/jpeg',.9).split(',')[1],bytes=Uint8Array.from(atob(data),ch=>ch.charCodeAt(0));return new Blob([buildPdf(bytes,c.width,c.height)],{type:'application/pdf'});
 }
 async function download(r){
  const blob=await createPartnerPdf(r),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='BrandMyVan-'+r.spot_id+'-'+r.company.replace(/[^a-z0-9]+/gi,'-').replace(/^-|-$/g,'').slice(0,50)+'.pdf';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),30000);
 }
 const api={buildPdf,dimensions,createPartnerPdf,download};if(typeof module==='object'&&module.exports)module.exports=api;else root.BMV_PDF=api;
})(globalThis);
