// ui-snapshot verify: node shot.mjs <snapshot.html> <outDir> "d-home=home" "m-list=list" ...
// "d-" prefix = desktop 1440x900, "m-" = mobile 390x844. Prints NO ERRORS or the console/page errors.
import { chromium } from "playwright";
import { mkdirSync } from "fs";
import { resolve } from "path";
const [file, outDir, ...specs] = process.argv.slice(2);
mkdirSync(outDir, { recursive: true });
const url = "file://" + resolve(file), b = await chromium.launch(), errs = [];
for (const spec of specs) {
  const [name, hash] = spec.split("=");
  const p = await b.newPage({ viewport: name.startsWith("m-") ? { width: 390, height: 844 } : { width: 1440, height: 900 } });
  p.on("pageerror", (e) => errs.push(`${name}: ${e.message}`));
  p.on("console", (m) => m.type() === "error" && errs.push(`${name}: ${m.text()}`));
  await p.goto(`${url}#/${hash}`); await p.waitForTimeout(500);
  await p.screenshot({ path: `${outDir}/${name}.png` }); await p.close();
}
console.log(errs.length ? errs.join("\n") : "NO ERRORS");
await b.close();
