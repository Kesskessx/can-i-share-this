(function(root){
  const clamp=(value,min,max)=>Math.min(max,Math.max(min,value));
  function fit(width,height,imageWidth,imageHeight,scale=1,x=.5,y=.5){
    // This inset rectangle is inside every printed panel contour, including bevels.
    const marginX=width*.13,marginY=height*.13,availableW=width-2*marginX,availableH=height-2*marginY;
    const ratio=Math.min(availableW/imageWidth,availableH/imageHeight)*clamp(scale,.3,1);
    const w=imageWidth*ratio,h=imageHeight*ratio;
    return {x:marginX+(availableW-w)*clamp(x,0,1),y:marginY+(availableH-h)*clamp(y,0,1),width:w,height:h,slackX:availableW-w,slackY:availableH-h};
  }
  const api={fit,clamp};if(typeof module==='object'&&module.exports)module.exports=api;else root.BMV_LAYOUT=api;
})(globalThis);
