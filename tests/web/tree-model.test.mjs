import test from "node:test";
import assert from "node:assert/strict";
import {
  visibleOutline, resolvedSelection, keyboardSelection, siblingsOf,
} from "../../web/tree-model.mjs";

function fixture() {
  return [
    { id: "root", parent_id: null, depth: 0, has_children: true },
    { id: "child", parent_id: "root", depth: 1, has_children: true },
    { id: "leaf", parent_id: "child", depth: 2, has_children: false },
    { id: "sibling", parent_id: "root", depth: 1, has_children: false },
    { id: "other", parent_id: null, depth: 0, has_children: false },
  ];
}

test("folding hides all descendants but not later roots; canonical outline stays intact", () => {
  const outline = fixture();
  const folded = visibleOutline(outline, new Set());
  assert.deepEqual(folded.map((row) => row.id), ["root", "other"]);
  assert.deepEqual(outline.map((row) => row.id), [
    "root", "child", "leaf", "sibling", "other",
  ]);
  const oneLevel = visibleOutline(outline, new Set(["root"]));
  assert.deepEqual(oneLevel.map((row) => row.id), [
    "root", "child", "sibling", "other",
  ]);
  const all = visibleOutline(outline, new Set(["root", "child"]));
  assert.equal(all.length, outline.length);
});

test("selection follows the nearest visible ancestor after folding", () => {
  const outline = fixture();
  assert.equal(resolvedSelection(outline, visibleOutline(outline, new Set()), "leaf"), "root");
  assert.equal(resolvedSelection(
    outline, visibleOutline(outline, new Set(["root"])), "leaf",
  ), "child");
  assert.equal(resolvedSelection(outline, visibleOutline(outline, new Set()), "missing"), "root");
  assert.equal(resolvedSelection([], [], "missing"), null);
});

test("keyboard navigation retains stable node identity", () => {
  const rows = visibleOutline(fixture(), new Set(["root", "child"]));
  assert.equal(keyboardSelection(rows, "child", "ArrowDown"), "leaf");
  assert.equal(keyboardSelection(rows, "child", "ArrowUp"), "root");
  assert.equal(keyboardSelection(rows, "root", "ArrowUp"), "root");
  assert.equal(keyboardSelection(rows, "other", "ArrowDown"), "other");
  assert.equal(keyboardSelection(rows, "child", "Home"), "root");
  assert.equal(keyboardSelection(rows, "child", "End"), "other");
  assert.equal(keyboardSelection(rows, "leaf", "Escape"), "leaf");
});

test("deep trees have no fixed depth or number-of-nodes limit", () => {
  const items = Array.from({ length: 320 }, (_, i) => ({
    id: "n" + i, parent_id: i ? "n" + (i - 1) : null,
    depth: i, has_children: i < 319,
  }));
  assert.equal(visibleOutline(items, new Set(items.map((item) => item.id))).length, 320);
  assert.deepEqual(visibleOutline(items, new Set()).map((item) => item.id), ["n0"]);
});

test("siblings derive from canonical parent identity", () => {
  const nodes = fixture();
  assert.deepEqual(siblingsOf(nodes, nodes[1]).map((node) => node.id), ["child", "sibling"]);
  assert.deepEqual(siblingsOf(nodes, nodes[4]).map((node) => node.id), ["root", "other"]);
});
