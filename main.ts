// news-image-20261123: write the drawn Monday front page to /output/entry.png.
// The drawing itself lives in draw.py (PIL, no network, no clock); this
// entrypoint only invokes it and verifies the output, so the result is
// byte-identical on every run. Node 22, standard library only.
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT_DIR = "/output";
const OUT = join(OUT_DIR, "entry.png");

mkdirSync(OUT_DIR, { recursive: true });
execFileSync("python3", [join(HERE, "draw.py"), OUT], { stdio: "inherit" });
if (!existsSync(OUT)) {
  throw new Error("draw.py did not produce " + OUT);
}
const bytes = readFileSync(OUT);
// Validate the PNG before reporting it: 8-byte signature, then the IHDR
// chunk must say 1024x1024, matching the front-page format.
const PNG_SIG = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (bytes.length < 33 || !bytes.subarray(0, 8).equals(PNG_SIG)) {
  throw new Error(OUT + " is not a PNG");
}
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width !== 1024 || height !== 1024) {
  throw new Error(`${OUT} is ${width}x${height}, expected 1024x1024`);
}
const sha = createHash("sha256").update(bytes).digest("hex");
console.log(`wrote ${OUT} ${statSync(OUT).size} bytes sha256=${sha}`);
