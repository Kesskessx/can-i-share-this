# BrandMyVan

Standalone static 3D sponsor demo. Serve this folder over HTTP, or set the Vercel project root to `brandmyvan`, framework Other, no build command, output `.`.

- `van-realistic.glb`: original user-supplied OBJ geometry, 15,601 triangles, eight source groups, four embedded JPEG textures at original dimensions.
- `viewer.js`: Three.js 0.185.1 GLTFLoader and OrbitControls, eight camera-linked sponsor markers, zoom, reset, auto-rotate, and load/error status.
- All browser dependencies are local; no CDN or runtime remote model dependency.
- Sponsorship locations and prices are illustrative. Auctions and payments are not implemented.
- `scripts/convert_obj.py` can reproduce the GLB from the supplied `Van Car 1` OBJ/MTL/BMP folder (requires Pillow).

This folder is independent of the CanIShareThis scanner and its root deployment configuration.
