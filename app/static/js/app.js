/**
 * 前端主逻辑
 * P0: 系统状态检查
 * P2: 图谱渲染、搜索、交互
 * P3: 问答对话、图谱联动
 */

document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
});

/**
 * 检查系统健康状态
 */
async function checkHealth() {
    const statusContent = document.getElementById('statusContent');
    try {
        const resp = await fetch('/health');
        const data = await resp.json();

        const items = [
            { label: '系统', status: data.status, detail: `v${data.version} / Python ${data.python_version}` },
            { label: 'Ollama', status: data.ollama.status, detail: data.ollama.models ? data.ollama.models.join(', ') : data.ollama.message },
            { label: 'GLM API', status: data.glm_api.status, detail: data.glm_api.model || data.glm_api.message },
            { label: '向量库', status: data.vector_store.status, detail: data.vector_store.path || data.vector_store.message },
            { label: '图数据库', status: data.graph_db.status, detail: data.graph_db.path || data.graph_db.message },
        ];

        statusContent.innerHTML = items.map(item => {
            const dotClass = item.status === 'ok' || item.status === 'configured' ? 'ok' :
                             item.status === 'degraded' ? 'warn' : 'error';
            return `<div class="status-item">
                <span class="status-dot ${dotClass}"></span>
                <strong>${item.label}</strong>: ${item.status}
                <span style="color:#a0aec0;margin-left:4px">${item.detail || ''}</span>
            </div>`;
        }).join('');

        // 如果所有组件正常，启用问答和搜索
        const allOk = data.status === 'ok';
        document.getElementById('questionInput').disabled = !allOk;
        document.getElementById('sendBtn').disabled = !allOk;
        document.getElementById('searchInput').disabled = !allOk;
        document.getElementById('searchBtn').disabled = !allOk;

    } catch (e) {
        statusContent.innerHTML = `<div class="status-item"><span class="status-dot error"></span>无法连接后端服务: ${e.message}</div>`;
    }
}

// ===== P2: 图谱相关函数（待实现） =====
// function renderGraph(graphData) { ... }
// function searchEntity(keyword) { ... }
// function highlightEntities(ids) { ... }

// ===== P3: 问答相关函数（待实现） =====
// async function sendQuestion() { ... }
// function appendMessage(role, content) { ... }
