/** Pure, testable T2.1 display projection. Never owns the canonical hierarchy. */

export function visibleOutline(outline, expanded) {
  const rows = [];
  let collapsedDepth = -1;
  for (const item of outline) {
    if (collapsedDepth >= 0 && item.depth > collapsedDepth) continue;
    collapsedDepth = -1;
    rows.push(item);
    if (item.has_children && !expanded.has(item.id)) collapsedDepth = item.depth;
  }
  return rows;
}

export function resolvedSelection(outline, visible, selectedId) {
  const shown = new Set(visible.map((item) => item.id));
  const index = new Map(outline.map((item) => [item.id, item]));
  let candidate = selectedId;
  const visited = new Set();
  while (candidate && !visited.has(candidate)) {
    if (shown.has(candidate)) return candidate;
    visited.add(candidate);
    candidate = index.get(candidate)?.parent_id ?? null;
  }
  return visible[0]?.id ?? null;
}

export function keyboardSelection(visible, selectedId, key) {
  if (!visible.length) return null;
  const index = Math.max(0, visible.findIndex((item) => item.id === selectedId));
  if (key === "ArrowDown") return visible[Math.min(visible.length - 1, index + 1)].id;
  if (key === "ArrowUp") return visible[Math.max(0, index - 1)].id;
  if (key === "Home") return visible[0].id;
  if (key === "End") return visible[visible.length - 1].id;
  return selectedId;
}

export function siblingsOf(outline, node) {
  return outline.filter((item) => item.parent_id === node.parent_id);
}
