try {
 await import('./funding-viewer-3d.js');
} catch(error) {
 console.warn('Using the 2D van preview:',error);
 const {startFallback}=await import('./funding-viewer-2d.js');
 startFallback();
}
