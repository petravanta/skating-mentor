// Checks what the JSON Schema can't: ids are unique, every reference points at a skill that exists,
// and the requires links never loop back on themselves.
// Run: node scripts/check-data.js
const fs = require('fs'), path = require('path');
const skills = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'data', 'skills.json'), 'utf8'));
const errors = [];

const byId = new Map();
for (const s of skills) {
  if (byId.has(s.id)) errors.push(`skills.json: id "${s.id}" is used more than once`);
  byId.set(s.id, s);
}
for (const s of skills) {
  for (const r of s.requires) if (!byId.has(r)) errors.push(`skills.json: "${s.id}" requires "${r}", which doesn't exist`);
  for (const r of s.supports || []) if (!byId.has(r)) errors.push(`skills.json: "${s.id}" supports "${r}", which doesn't exist`);
  if (s.supports && s.style !== 'off-skate') errors.push(`skills.json: "${s.id}" has supports, which is only for off-skate drills`);
  if (s.requires.includes(s.id)) errors.push(`skills.json: "${s.id}" requires itself`);
}
// Loop check: walk each skill's requires chain
const state = new Map(); // 1 = visiting, 2 = done
const visit = (id, trail) => {
  if (state.get(id) === 2 || !byId.has(id)) return;
  if (state.get(id) === 1) { errors.push(`skills.json: requires loop ${trail.concat(id).join(' → ')}`); return; }
  state.set(id, 1);
  for (const r of byId.get(id).requires) visit(r, trail.concat(id));
  state.set(id, 2);
};
for (const s of skills) visit(s.id, []);

if (errors.length) { console.error(errors.join('\n')); process.exit(1); }
console.log(`data ok: ${skills.length} skills`);
