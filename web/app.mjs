import { visibleOutline, resolvedSelection, keyboardSelection, siblingsOf } from "./tree-model.mjs";

const elements = {
  picker: document.getElementById("project-picker"),
  tree: document.getElementById("tree"),
  empty: document.getElementById("empty-tree"),
  detail: document.getElementById("selection-detail"),
  actions: document.getElementById("node-actions"),
  form: document.getElementById("edit-form"),
  heading: document.getElementById("form-heading"),
  title: document.getElementById("node-title"),
  feedback: document.getElementById("feedback"),
};

const state = {
  data: null,
  projectId: null,
  selectedId: null,
  expanded: new Set(),
  visible: [],
  busy: false,
  formAction: null,
  firstLoad: true,
};

try {
  const saved = JSON.parse(sessionStorage.getItem("art-t2.1-view") || "null");
  if (saved && typeof saved === "object") {
    if (typeof saved.projectId === "string") state.projectId = saved.projectId;
    if (typeof saved.selectedId === "string") state.selectedId = saved.selectedId;
    if (Array.isArray(saved.expanded)) {
      state.expanded = new Set(saved.expanded.filter((item) => typeof item === "string").slice(0, 2000));
    }
    state.firstLoad = false;
  }
} catch { /* View preferences must never prevent loading canonical state. */ }

function saveView() {
  try {
    sessionStorage.setItem("art-t2.1-view", JSON.stringify({
      projectId: state.projectId, selectedId: state.selectedId,
      expanded: Array.from(state.expanded).slice(0, 2000),
    }));
  } catch { /* Optional view preferences only. */ }
}

function notice(message, error = false) {
  elements.feedback.textContent = message;
  elements.feedback.classList.toggle("error", error);
}

function outline() {
  return state.data?.outlines[state.projectId] ?? [];
}

function selectedNode() {
  return outline().find((item) => item.id === state.selectedId) ?? null;
}

function focusSelected() {
  for (const item of elements.tree.querySelectorAll('[role="treeitem"]')) {
    if (item.dataset.id === state.selectedId) {
      item.focus();
      break;
    }
  }
}

function renderProjects() {
  elements.picker.replaceChildren();
  for (const project of state.data.projects) {
    const option = document.createElement("option");
    option.value = project.id;
    option.textContent = project.name;
    elements.picker.append(option);
  }
  elements.picker.value = state.projectId ?? "";
  elements.picker.disabled = !state.data.projects.length || state.busy;
}

function renderTree() {
  const all = outline();
  const rows = visibleOutline(all, state.expanded);
  state.visible = rows;
  state.selectedId = resolvedSelection(all, rows, state.selectedId);
  elements.tree.replaceChildren();
  elements.empty.hidden = all.length > 0;
  elements.empty.textContent = state.data.projects.length
    ? "No nodes yet. Create a root node to start the roadmap."
    : "No projects yet. Create a project first.";

  for (const node of rows) {
    const li = document.createElement("li");
    li.className = "tree-item";
    li.setAttribute("role", "none");
    const row = document.createElement("div");
    row.className = "tree-row";
    if (node.archived) row.classList.add("archived");
    row.dataset.id = node.id;
    row.style.setProperty("--visual-depth", String(Math.min(node.depth, 10)));
    row.setAttribute("role", "treeitem");
    row.setAttribute("aria-level", String(node.depth + 1));
    row.setAttribute("aria-selected", String(node.id === state.selectedId));
    row.tabIndex = node.id === state.selectedId ? 0 : -1;
    if (node.has_children) {
      row.setAttribute("aria-expanded", String(state.expanded.has(node.id)));
    }

    const twisty = document.createElement("button");
    twisty.type = "button";
    twisty.className = "twisty";
    twisty.dataset.toggle = node.id;
    twisty.textContent = node.has_children ? (state.expanded.has(node.id) ? "⌄" : "›") : "";
    twisty.setAttribute("aria-label", (state.expanded.has(node.id) ? "Collapse " : "Expand ") + node.title);
    twisty.disabled = !node.has_children;
    if (!node.has_children) twisty.classList.add("no-children");

    const label = document.createElement("span");
    label.className = "node-label";
    label.textContent = node.title;
    const kind = document.createElement("span");
    kind.className = "node-kind";
    kind.textContent = node.kind;
    row.append(twisty, label, kind);
    li.append(row);
    elements.tree.append(li);
  }
  saveView();
}

function renderDetail() {
  const node = selectedNode();
  elements.detail.replaceChildren();
  elements.actions.hidden = !node;
  for (const button of elements.actions.querySelectorAll("button")) button.disabled = state.busy;

  if (!node) {
    const p = document.createElement("p");
    p.className = "muted";
    p.textContent = "Select a node in the roadmap tree.";
    elements.detail.append(p);
    return;
  }
  const title = document.createElement("h3");
  title.className = "detail-title";
  title.textContent = node.title;
  const kind = document.createElement("p");
  kind.className = "detail-meta";
  kind.textContent = node.kind + (node.archived ? " · Archived" : " · Active");
  const id = document.createElement("p");
  id.className = "detail-meta";
  id.textContent = "Stable ID: " + node.id;
  const location = document.createElement("p");
  location.className = "detail-meta";
  location.textContent = "Level " + (node.depth + 1) + " · Position " + (node.position + 1);
  elements.detail.append(title, kind, id, location);

  const related = siblingsOf(outline(), node);
  const place = related.findIndex((item) => item.id === node.id);
  for (const button of elements.actions.querySelectorAll("[data-action]")) {
    const action = button.dataset.action;
    if (action === "archive") button.textContent = node.archived ? "Restore" : "Archive";
    if (action === "up" && place === 0) button.disabled = true;
    if (action === "down" && place === related.length - 1) button.disabled = true;
    if (node.archived && !["archive"].includes(action)) button.disabled = true;
  }
}

function render() {
  if (!state.data) return;
  if (!state.data.projects.some((p) => p.id === state.projectId)) {
    state.projectId = state.data.projects[0]?.id ?? null;
    state.selectedId = null;
  }
  renderProjects();
  renderTree();
  renderDetail();
  document.getElementById("new-root").disabled = state.busy || !state.projectId;
  document.getElementById("new-project").disabled = state.busy;
  document.getElementById("refresh").disabled = state.busy;
}

async function refresh() {
  const response = await fetch("/api/workspace", { cache: "no-store" });
  if (!response.ok) throw new Error("Cannot load workspace (" + response.status + ")");
  state.data = await response.json();
  if (state.firstLoad) {
    for (const rows of Object.values(state.data.outlines)) {
      for (const node of rows) {
        if (node.has_children && node.depth < 2) state.expanded.add(node.id);
      }
    }
    state.firstLoad = false;
  }
  render();
}

function setSelected(id, focus = false) {
  state.selectedId = id;
  cancelForm();
  render();
  if (focus) focusSelected();
}

function toggle(id, focus = false) {
  if (state.expanded.has(id)) state.expanded.delete(id);
  else state.expanded.add(id);
  cancelForm();
  render();
  if (focus) focusSelected();
}

elements.tree.addEventListener("click", (event) => {
  const toggleButton = event.target.closest("button[data-toggle]");
  if (toggleButton && !toggleButton.disabled) {
    event.stopPropagation();
    toggle(toggleButton.dataset.toggle, true);
    return;
  }
  const row = event.target.closest('[role="treeitem"]');
  if (row) setSelected(row.dataset.id, true);
});

elements.tree.addEventListener("keydown", (event) => {
  const row = event.target.closest('[role="treeitem"]');
  // A focused expand button has its own native Enter/Space click behavior.
  // Do not also interpret its bubbled keydown as a tree-row command.
  if (!row || event.target !== row) return;
  const key = event.key;
  if (["ArrowDown", "ArrowUp", "Home", "End"].includes(key)) {
    event.preventDefault();
    setSelected(keyboardSelection(state.visible, row.dataset.id, key), true);
    return;
  }
  const selected = selectedNode();
  if (!selected) return;
  if (key === "ArrowRight") {
    event.preventDefault();
    if (selected.has_children && !state.expanded.has(selected.id)) toggle(selected.id, true);
    else {
      const next = state.visible.find((node) => node.parent_id === selected.id);
      if (next) setSelected(next.id, true);
    }
  } else if (key === "ArrowLeft") {
    event.preventDefault();
    if (selected.has_children && state.expanded.has(selected.id)) toggle(selected.id, true);
    else if (selected.parent_id) setSelected(selected.parent_id, true);
  } else if (key === "Enter") {
    event.preventDefault();
    if (selected.has_children) toggle(selected.id, true);
  }
});

elements.picker.addEventListener("change", () => {
  state.projectId = elements.picker.value;
  state.selectedId = null;
  cancelForm();
  render();
});

function cancelForm() {
  state.formAction = null;
  elements.form.hidden = true;
  elements.title.value = "";
}

function openForm(action) {
  if (state.busy) return;
  const node = selectedNode();
  if (["child", "sibling", "rename"].includes(action) && !node) return;
  state.formAction = action;
  const captions = {
    project: "Create project", root: "Create root node",
    child: "Create child node", sibling: "Create sibling node", rename: "Rename node",
  };
  elements.heading.textContent = captions[action];
  elements.title.value = action === "rename" ? node.title : "";
  elements.title.setAttribute("aria-label", action === "project" ? "Project name" : "Node title");
  elements.form.hidden = false;
  elements.title.focus();
  elements.title.select();
}

async function issue(command) {
  if (state.busy) return;
  state.busy = true;
  render();
  try {
    const response = await fetch("/api/commands", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...command, expected_revision: state.data.revision }),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (response.status === 409) {
        await refresh();
        throw new Error("Workspace changed in another window. Reloaded; please retry.");
      }
      throw new Error(data.error || "Command failed (" + response.status + ")");
    }
    if (command.type === "project.create") state.projectId = data.id;
    if (command.type === "node.create") {
      state.selectedId = data.id;
      if (command.parent_id) state.expanded.add(command.parent_id);
    }
    cancelForm();
    await refresh();
    notice("Saved through the validated command engine · revision " + state.data.revision);
  } catch (error) {
    notice(error.message || "Command failed", true);
  } finally {
    state.busy = false;
    render();
  }
}

elements.form.addEventListener("submit", (event) => {
  event.preventDefault();
  const title = elements.title.value.trim();
  const action = state.formAction;
  const node = selectedNode();
  if (!title || !action) return;
  if (action === "project") {
    issue({ type: "project.create", name: title });
  } else if (action === "rename" && node) {
    issue({ type: "node.rename", project_id: state.projectId, node_id: node.id, title });
  } else if (action === "root") {
    issue({ type: "node.create", project_id: state.projectId, parent_id: null, title });
  } else if (node) {
    issue({
      type: "node.create", project_id: state.projectId,
      parent_id: action === "child" ? node.id : node.parent_id, title,
    });
  }
});

document.getElementById("new-project").addEventListener("click", () => openForm("project"));
document.getElementById("new-root").addEventListener("click", () => openForm("root"));
document.getElementById("cancel-edit").addEventListener("click", cancelForm);
document.getElementById("refresh").addEventListener("click", async () => {
  try { await refresh(); notice("Workspace refreshed"); }
  catch (error) { notice(error.message, true); }
});

elements.actions.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button || button.disabled || state.busy) return;
  const action = button.dataset.action;
  const node = selectedNode();
  if (!node) return;
  if (["child", "sibling", "rename"].includes(action)) {
    openForm(action);
    return;
  }
  if (action === "archive") {
    issue({
      type: node.archived ? "node.restore" : "node.archive",
      project_id: state.projectId, node_id: node.id,
    });
  } else if (action === "up" || action === "down") {
    const siblings = siblingsOf(outline(), node);
    const index = siblings.findIndex((item) => item.id === node.id);
    const target = index + (action === "up" ? -1 : 1);
    if (target >= 0 && target < siblings.length) {
      issue({
        type: "node.move", project_id: state.projectId, node_id: node.id,
        new_parent_id: node.parent_id, position: target,
      });
    }
  }
});

refresh().then(() => notice("Ready · canonical workspace loaded"))
  .catch((error) => notice(error.message, true));
