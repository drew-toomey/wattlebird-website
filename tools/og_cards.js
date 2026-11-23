// Makes blog/<slug>/card.jpg (1200x630 share card) for each built post. Run after build_blog.py.
// Needs Playwright (node). Usage: node tools/og_cards.js
const {chromium} = require('playwright'); const fs = require('fs'); const path = require('path');
const ROOT = path.join(__dirname, '..'), BLOG = path.join(ROOT, 'blog');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({viewport: {width: 1200, height: 630}});
  for (const slug of fs.readdirSync(BLOG)) {
    const page = path.join(BLOG, slug, 'index.html'); if (!fs.existsSync(page)) continue;
    const src = fs.readFileSync(page, 'utf8');
    const title = (src.match(/<h1>(.*?)<\/h1>/) || [])[1] || '';
    const issue = (src.match(/ISSUE #([^<]+)<\/span>/) || [])[1] || '';
    const cover = (src.match(/og:image" content="[^"]*"/) && fs.readdirSync(path.join(BLOG, slug)).find(f => f.startsWith('cover'))) || '';
    const html = `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:Bangers;src:url(file://${ROOT}/fonts/Bangers.ttf)}@font-face{font-family:Baloo;src:url(file://${ROOT}/fonts/Baloo2.ttf);font-weight:400 800}
body{margin:0;width:1200px;height:630px;background:radial-gradient(circle,#2b3560 1.6px,transparent 2px) 0 0/14px 14px,#1c2340;font-family:Baloo;overflow:hidden;position:relative}
.img{position:absolute;right:40px;top:60px;width:640px;height:460px;border:5px solid #1c2340;box-shadow:10px 10px 0 #05070f;transform:rotate(2deg);background:url("file://${path.join(BLOG, slug, cover)}") 50% 50%/cover}
.t{position:absolute;left:56px;top:70px;width:500px}
.issue{display:inline-block;background:#f4b82e;border:3px solid #1c2340;font-family:Bangers;font-size:38px;padding:2px 16px;transform:rotate(-3deg);box-shadow:4px 4px 0 #05070f;color:#1c2340}
h1{font-family:Bangers;font-weight:400;font-size:82px;line-height:.95;color:#f4b82e;-webkit-text-stroke:2px #05070f;text-shadow:4px 4px 0 #05070f;margin:26px 0 0}
.by{position:absolute;left:56px;bottom:50px;color:#fbf1d8;font-size:28px;font-weight:700;display:flex;align-items:center;gap:14px}
.by img{width:60px;height:60px;border:3px solid #1c2340;background:#fbf1d8;transform:rotate(-3deg)}
</style></head><body><div class="img"></div><div class="t"><span class="issue">DEV BLOG · ISSUE #${issue}</span><h1>${title}</h1></div>
<div class="by"><img src="file://${ROOT}/img/mark.png">wattlebirdgames.com/blog</div></body></html>`;
    const tmp = path.join(require('os').tmpdir(), 'og-' + slug + '.html'); fs.writeFileSync(tmp, html);
    await p.goto('file://' + tmp); await p.waitForTimeout(400);
    await p.screenshot({path: path.join(BLOG, slug, 'card.jpg'), type: 'jpeg', quality: 88});
    console.log('card', slug);
  }
  await b.close();
})();
