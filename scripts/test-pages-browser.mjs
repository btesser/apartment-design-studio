import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { resolve, extname, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const root = fileURLToPath(new URL('../_site/', import.meta.url));
const prefix = '/apartment-design-studio/';
const types = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.glb': 'model/gltf-binary' };
const server = createServer(async (request, response) => {
  try {
    const url = new URL(request.url, 'http://localhost');
    assert.ok(url.pathname.startsWith(prefix));
    let path = resolve(root, decodeURIComponent(url.pathname.slice(prefix.length)));
    assert.ok(path === resolve(root) || path.startsWith(resolve(root) + sep));
    if ((await stat(path)).isDirectory()) path = resolve(path, 'index.html');
    const data = await readFile(path);
    response.writeHead(200, { 'Content-Type': types[extname(path)] || 'application/octet-stream', 'Content-Length': data.length });
    response.end(request.method === 'HEAD' ? undefined : data);
  } catch {
    response.writeHead(404); response.end('Not found');
  }
});
await new Promise(done => server.listen(0, '127.0.0.1', done));
const base = `http://127.0.0.1:${server.address().port}${prefix}`;
let browser;
try {
  browser = await chromium.launch({
    ...(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {}),
    headless: true,
    args: ['--enable-unsafe-swiftshader', '--use-gl=angle', '--use-angle=swiftshader'],
  });
  const page = await browser.newPage({ viewport: { width: 1200, height: 850 } });
  const failures = [];
  page.on('pageerror', error => failures.push(error.message));
  page.on('response', response => { if (response.status() >= 400) failures.push(`${response.status()} ${response.url()}`); });
  page.on('requestfailed', request => {
    // Chromium can cancel an unused HEAD stream after headers arrive. HTTP
    // status checks above and complete GLB loads still validate these assets.
    if (request.method() === 'HEAD' && request.failure()?.errorText === 'net::ERR_ABORTED') return;
    failures.push(`${request.method()} ${request.url()}: ${request.failure()?.errorText}`);
  });
  page.on('request', request => { if (/^https?:/.test(request.url()) && !request.url().startsWith(base)) failures.push(`Outside project prefix: ${request.url()}`); });
  for (const [label, api, expected, modeButton] of [
    ['Whole apartment', 'apartmentViewer', 8, '#walk-mode'],
    ['His office', 'officeViewer', 3, '#walk'],
  ]) {
    await page.goto(base);
    await page.getByRole('link', { name: new RegExp(label) }).click();
    await page.waitForFunction(api => window[api]?.ready(), api, { timeout: 120000 });
    const state = await page.evaluate(api => window[api].state(), api);
    assert.equal(Object.keys(state.assets).length, expected);
    assert.ok(Object.values(state.assets).every(value => value === 'loaded'));
    await page.locator(modeButton).click();
    assert.equal(await page.evaluate(api => window[api].state().mode, api), 'walk');
    assert.equal(await page.locator('#viewport canvas').count(), 1);
    if (api === 'apartmentViewer') {
      await page.locator('#panel-toggle').click();
      await page.selectOption('#floor', 'basement');
      assert.equal(await page.evaluate(() => window.apartmentViewer.state().activeFloor), 'basement');
    } else {
      await page.locator('#controls-toggle').click();
      await page.locator('#hide-doors').check();
      assert.equal(await page.evaluate(() => window.officeViewer.state().doorsHidden), true);
    }
    console.log(`${label}: all ${expected} model layers loaded; controls work under ${prefix}`);
  }
  for (const [from, to] of [
    ['apartment-walkthrough.html', 'apartment-walkthrough/'],
    ['apartment-v2/apartment-walkthrough.html', 'apartment-walkthrough/'],
    ['his-office-redesign/his-office-viewer.html', 'his-office-redesign/viewer-source/'],
    ['his-office-redesign/delivery/his-office-viewer.html', 'his-office-redesign/viewer-source/'],
  ]) {
    // Block viewer initialization during redirect checks to avoid interrupting asset loads.
    const redirectPage = await browser.newPage();
    await redirectPage.route('**/*.js', route => route.fulfill({ contentType: 'text/javascript', body: '' }));
    await redirectPage.goto(base + from);
    await redirectPage.waitForURL(base + to);
    await redirectPage.close();
  }
  assert.deepEqual(failures, []);
  console.log('All four legacy redirects passed; no failed requests or browser errors.');
} finally {
  await browser?.close();
  await new Promise(done => server.close(done));
}
