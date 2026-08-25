const resultsElement = document.querySelector("#results");
const detailElement = document.querySelector("#detail");
const messageElement = document.querySelector("#message");
const statusElement = document.querySelector("#snapshot-status");
const formElement = document.querySelector("#search-form");
const inputElement = document.querySelector("#query-input");
const refreshButton = document.querySelector("#refresh-button");

async function request(path, options = {}) {
  const response = await fetch(path, { cache: "no-store", ...options });
  const payload = await response.json().catch(() => ({ code: "invalid_response", message: "本地服务返回了无效响应。" }));
  if (!response.ok) {
    const error = new Error(payload.message || "本地请求失败。");
    error.payload = payload;
    throw error;
  }
  return payload;
}

function setMessage(message = "", isError = false) {
  messageElement.textContent = message;
  messageElement.classList.toggle("error", isError);
}

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function renderStatus(status) {
  if (!status.persistent) {
    statusElement.textContent = "尚未建立持久索引";
    return;
  }
  statusElement.textContent = `快照 ${String(status.snapshot_id || "").slice(0, 24)} · ${status.nodes} 节点`;
}

async function loadStatus() {
  try {
    renderStatus(await request("/api/status"));
  } catch (error) {
    setMessage(error.message, true);
  }
}

function renderResults(payload) {
  resultsElement.replaceChildren();
  if (!payload.matches.length) {
    resultsElement.append(element("div", "empty-state", "没有匹配节点。请尝试更具体的主题、知识卡标题或 Python 符号。"));
    return;
  }
  const summary = element("p", "metadata", `共 ${payload.total_candidates} 个候选节点 · ${payload.ranking}`);
  resultsElement.append(summary);
  for (const match of payload.matches) {
    const card = element("button", "result-card");
    card.type = "button";
    const topline = element("div", "result-topline");
    topline.append(element("span", "result-kind", match.kind), element("span", "score", `评分 ${match.score}`));
    card.append(topline, element("h3", "", match.title));
    card.append(element("div", "path", `${match.path}:${match.line_start}-${match.line_end}`));
    if (match.snippet) card.append(element("p", "snippet", match.snippet));
    card.addEventListener("click", () => showNode(match.id));
    resultsElement.append(card);
  }
}

async function search(query = inputElement.value.trim()) {
  if (!query) return;
  setMessage("正在本地检索…");
  detailElement.replaceChildren(element("div", "empty-state", "选择一个检索结果以查看可追溯证据。"));
  try {
    const payload = await request(`/api/search?q=${encodeURIComponent(query)}&limit=12`);
    renderResults(payload);
    setMessage(`已返回 ${payload.matches.length} 条结果。`);
  } catch (error) {
    setMessage(error.message, true);
  }
}

function detailMetadata(node) {
  return [
    `类型：${node.kind}`,
    `位置：${node.path}:${node.line_start}-${node.line_end}`,
    node.attributes.document_title ? `文档：${node.attributes.document_title}` : null,
    node.attributes.domain ? `领域：${node.attributes.domain}` : null,
  ].filter(Boolean).join("\n");
}

async function showNode(nodeId) {
  setMessage("正在读取节点详情…");
  try {
    const payload = await request(`/api/node?id=${encodeURIComponent(nodeId)}`);
    const node = payload.node;
    detailElement.replaceChildren();
    const header = element("section", "detail-block");
    header.append(element("h3", "", node.title));
    header.append(element("pre", "", detailMetadata(node)));
    const actions = element("div", "detail-actions");
    const connections = element("button", "button button-secondary", "浏览关系");
    connections.type = "button";
    connections.addEventListener("click", () => showConnections(node.id));
    const context = element("button", "button button-secondary", "生成上下文包");
    context.type = "button";
    context.addEventListener("click", () => showContext(node.title));
    actions.append(connections, context);
    header.append(actions);
    detailElement.append(header);

    const content = element("section", "detail-block");
    content.append(element("h3", "", "节点内容"), element("pre", "", node.content || "此节点未保存正文。"));
    detailElement.append(content);

    const relationships = element("section", "detail-block");
    relationships.append(element("h3", "", `直接关系 (${payload.relationships.length})`));
    if (!payload.relationships.length) {
      relationships.append(element("p", "metadata", "没有直接关系。"));
    }
    for (const relationship of payload.relationships) {
      const row = element("div", "relationship");
      row.append(element("strong", "", `${relationship.direction} · ${relationship.type}`));
      if (relationship.type === "shares_terms") row.append(element("span", "weak", "弱关联：词项重合，不代表引用或因果。"));
      row.append(element("div", "metadata", relationship.reason));
      relationships.append(row);
    }
    detailElement.append(relationships);
    setMessage("节点详情已加载。选择“浏览关系”可展开局部图。" );
  } catch (error) {
    setMessage(error.message, true);
  }
}

async function showConnections(nodeId) {
  try {
    const payload = await request(`/api/connections?id=${encodeURIComponent(nodeId)}&depth=2`);
    const block = element("section", "detail-block");
    block.append(element("h3", "", `两跳邻域 (${payload.connections.length})`));
    for (const item of payload.connections) {
      const row = element("div", "relationship");
      row.append(element("strong", "", item.node.title));
      row.append(element("div", "metadata", `${item.relationship.type} · ${item.relationship.reason}`));
      if (item.relationship.type === "shares_terms") row.append(element("span", "weak", "弱关联"));
      block.append(row);
    }
    if (payload.truncated) block.append(element("p", "metadata", "结果已按安全上限裁剪。"));
    detailElement.append(block);
    block.scrollIntoView({ behavior: "smooth", block: "nearest" });
  } catch (error) {
    setMessage(error.message, true);
  }
}

async function showContext(query) {
  try {
    const payload = await request(`/api/context?q=${encodeURIComponent(query)}&max_chars=4000`);
    const block = element("section", "detail-block");
    block.append(element("h3", "", `上下文包 · ${payload.node_ids.length} 节点 / ${payload.citations.length} 条定位`));
    block.append(element("pre", "", payload.context));
    if (payload.truncated) block.append(element("p", "metadata", "正文已按 4,000 字符预算裁剪。"));
    detailElement.append(block);
    block.scrollIntoView({ behavior: "smooth", block: "nearest" });
  } catch (error) {
    setMessage(error.message, true);
  }
}

formElement.addEventListener("submit", (event) => {
  event.preventDefault();
  search();
});

refreshButton.addEventListener("click", async () => {
  refreshButton.disabled = true;
  setMessage("正在显式刷新本地派生索引…");
  try {
    const report = await request("/api/refresh", { method: "POST" });
    setMessage(`刷新完成：${report.index_mode} · ${report.nodes} 节点 · ${report.changed_files} 个变化文件。`);
    await loadStatus();
    if (inputElement.value.trim()) await search();
  } catch (error) {
    setMessage(error.message, true);
  } finally {
    refreshButton.disabled = false;
  }
});

loadStatus();
