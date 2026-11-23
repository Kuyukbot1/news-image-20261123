// news-image-20261123: write the drawn Monday front page to the output dir.
// Node 22, standard library only. The image is pre-drawn (see draw.py) and
// this program only places its exact bytes at /output/entry.png, so every
// run produces identical output with no network access.
import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
// The grader mounts the output volume: create it if needed, never remove it.
mkdirSync(outputDir, { recursive: true });

const entryDir = dirname(fileURLToPath(import.meta.url));
const pngBytes = readFileSync(join(entryDir, "entry.png"));

// Guard against a corrupt or truncated bundle: refuse to ship anything
// that is not a real PNG before writing it to the output volume.
const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (pngBytes.length < 1000 || !pngBytes.subarray(0, 8).equals(PNG_MAGIC)) {
  throw new Error("entry.png is missing or is not a valid PNG");
}

const outPath = join(outputDir, "entry.png");
writeFileSync(outPath, pngBytes);
const sha256 = createHash("sha256").update(pngBytes).digest("hex");
console.log(`wrote ${outPath} ${pngBytes.length} bytes sha256=${sha256}`);
