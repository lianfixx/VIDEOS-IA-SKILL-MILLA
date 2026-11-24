// Cuadros fijos de la previa: empaqueta el video UNA vez y rinde solo los cuadros pedidos.
// Lo llama `vox.py previa`, que lo copia a la producción (así resuelve los paquetes de su node_modules).
// Uso: node .previa.mjs PROPS.json CARPETA_SALIDA 12,57,210 [NAVEGADOR]
import fs from 'node:fs';
import path from 'node:path';
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';

const [props, salida, cuadros, navegador] = process.argv.slice(2);
const inputProps = JSON.parse(fs.readFileSync(props, 'utf8'));
const browserExecutable = navegador || null;
fs.mkdirSync(salida, {recursive: true});
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
const composition = await selectComposition({serveUrl, id: 'Vox', inputProps, browserExecutable});
for (const f of cuadros.split(',').map(Number)) {
  await renderStill({composition, serveUrl, inputProps, frame: f, output: path.join(salida, `${String(f).padStart(5, '0')}.jpg`),
    imageFormat: 'jpeg', jpegQuality: 88, browserExecutable, logLevel: 'error'});
}
console.log(JSON.stringify({ok: true, cuadros: cuadros.split(',').length}));
