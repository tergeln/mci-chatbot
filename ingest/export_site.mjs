// mci-web сайтын өгөгдлийг (src/data/*.js) knowledge/ руу JSON болгон экспортлоно.
// Сайт өөрчлөгдөхөд дахин ажиллуулахад л чатбот ижил мэдээлэлтэй болно.
//
//   node export_site.mjs [mci-web хавтас]     (анхдагч: ../../mci-web)
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const site = resolve(process.argv[2] ?? join(here, "../../mci-web"));
const knowledge = join(here, "../knowledge");

const load = (file) => import(pathToFileURL(join(site, "src/data", file)).href);

function write(relPath, data) {
  const out = join(knowledge, relPath);
  mkdirSync(dirname(out), { recursive: true });
  // "_"-ээр эхэлсэн талбарыг json_reader мэдлэгийн санд оруулахгүй
  const doc = { _generated_from: "mci-web/src/data (export_site.mjs), гараар бүү засаарай", ...data };
  writeFileSync(out, JSON.stringify(doc, null, 2) + "\n");
  console.log(`✓ ${relPath}`);
}

const { activities } = await load("activities.js");
write("web/web_packages.json", {
  title: "Вебсайт хөгжүүлэлтийн багц, үнэ",
  packages: activities.map((a) => ({
    name: a.title.mn,
    summary: a.text.mn,
    price: a.price,
    includes: a.features.map((f) => f.mn),
  })),
});

const { homeCourses } = await load("courses.js");
write("course/site_courses.json", {
  title: "Вебсайт дээр бүртгэл авч буй сургалтууд",
  courses: homeCourses.map((c) => ({
    name: c.title.mn,
    category: c.tag.mn,
    description: c.text.mn,
    level_and_topics: c.meta.mn,
    enrollment: c.status?.mn,
  })),
});

const { cartProducts } = await load("merch.js");
write("merch/site_merch.json", {
  title: "Мерч бүтээгдэхүүнүүд",
  products: cartProducts.map((p) => ({ name: p.mn })),
});
