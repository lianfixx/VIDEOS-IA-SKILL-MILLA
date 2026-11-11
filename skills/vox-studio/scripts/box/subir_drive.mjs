// Sube un archivo a la carpeta de Google Drive abierta en una pestaña del Chrome del box.
// Corre DENTRO del box (Node 24, Chrome con --remote-debugging-port=9222 y la sesión de Emi abierta).
// Uso: node subir_drive.mjs TAB_ID /ruta/al/archivo
// TAB_ID sale de: curl -s -X PUT "http://127.0.0.1:9222/json/new?https://drive.google.com/drive/folders/ID"
const [tab, ruta] = process.argv.slice(2);
if (!tab || !ruta) { console.error('uso: node subir_drive.mjs TAB_ID RUTA'); process.exit(2); }
const ws = new WebSocket(`ws://127.0.0.1:9222/devtools/page/${tab}`);
let n = 0; const espera = new Map(); let selector = null;
const cmd = (method, params = {}) => new Promise((ok) => { const id = ++n; espera.set(id, ok); ws.send(JSON.stringify({id, method, params})); });
ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && espera.has(d.id)) { espera.get(d.id)(d); espera.delete(d.id); } else if (d.method === 'Page.fileChooserOpened') selector = d.params; };
const dormir = (ms) => new Promise((r) => setTimeout(r, ms));
const tecla = async (key, code, vk, mod = 0) => { for (const type of ['keyDown', 'keyUp']) await cmd('Input.dispatchKeyEvent', {type, key, code, windowsVirtualKeyCode: vk, modifiers: mod, text: type === 'keyDown' && !mod && key.length === 1 ? key : undefined}); };
const ev = async (expr) => (await cmd('Runtime.evaluate', {expression: expr, returnByValue: true})).result?.result?.value;
await new Promise((r) => (ws.onopen = r));
await cmd('Page.enable'); await cmd('DOM.enable'); await cmd('Page.bringToFront');
await cmd('Page.setInterceptFileChooserDialog', {enabled: true});
await tecla('Escape', 'Escape', 27); await dormir(400);
await tecla('c', 'KeyC', 67, 1); await dormir(700);   // Alt+C abre «Nuevo»
await tecla('u', 'KeyU', 85); await dormir(2500);      // U = subir archivo
let ok = false;
if (selector) {
  await cmd('DOM.setFileInputFiles', {backendNodeId: selector.backendNodeId, files: [ruta]});
  const nombre = JSON.stringify(ruta.split('/').pop());
  for (let i = 0; i < 20 && !ok; i++) { await dormir(2000); ok = await ev(`document.body.innerText.includes(${nombre})`); }
}
await cmd('Page.setInterceptFileChooserDialog', {enabled: false}); ws.close();
console.log(ok ? 'subido' : (selector ? 'no se confirmó la subida' : 'Drive no abrió el selector de archivos'));
process.exit(ok ? 0 : 1);
