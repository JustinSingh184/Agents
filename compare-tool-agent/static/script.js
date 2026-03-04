let file1Data = null;
let file2Data = null;
let lastResult = null;

// window.ADMIN_TOKEN is injected by the backend in index.html

document.getElementById('file1Input').addEventListener('change', (e) => uploadFile(e.target.files[0], 1));
document.getElementById('file2Input').addEventListener('change', (e) => uploadFile(e.target.files[0], 2));

async function uploadFile(file, index) {
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/upload', { method: 'POST', body: formData });
        const data = await response.json();
        
        if (index === 1) {
            file1Data = data;
            updateRowKeyOptions(data.headers);
        } else {
            file2Data = data;
        }

        checkReady();
        clearResults();
    } catch (err) {
        alert("Upload failed: " + err.message);
    }
}

function clearResults() {
    document.getElementById('table1Container').innerHTML = '';
    document.getElementById('table2Container').innerHTML = '';
    document.getElementById('summaryBar').textContent = 'Ready to compare.';
    document.getElementById('llmSummary').textContent = '';
    document.getElementById('exportBtn').disabled = true;
}

function updateRowKeyOptions(headers) {
    const select = document.getElementById('rowKeySelect');
    select.innerHTML = '';
    headers.forEach(h => {
        const opt = document.createElement('option');
        opt.value = h;
        opt.textContent = h;
        select.appendChild(opt);
    });
}

function checkReady() {
    if (file1Data && file2Data) {
        document.getElementById('compareBtn').disabled = false;
    }
}

async function handleCompare() {
    const btn = document.getElementById('compareBtn');
    btn.disabled = true;
    btn.textContent = "Comparing...";

    const formData = new FormData();
    formData.append('path1', file1Data.path);
    formData.append('path2', file2Data.path);
    formData.append('row_key', document.getElementById('rowKeySelect').value);
    formData.append('use_llm', document.getElementById('useLlmToggle').checked);

    try {
        const response = await fetch('/compare', { method: 'POST', body: formData });
        const result = await response.json();
        lastResult = result;
        
        renderTables(result);
        updateSummary(result);
        document.getElementById('exportBtn').disabled = false;
    } catch (err) {
        alert("Comparison failed: " + err.message);
    } finally {
        btn.disabled = false;
        btn.textContent = "Compare";
    }
}

function renderTables(result) {
    const container1 = document.getElementById('table1Container');
    const container2 = document.getElementById('table2Container');
    
    container1.innerHTML = generateTableHtml(result.file1_data, result.file1_highlights, 'highlight-f1');
    container2.innerHTML = generateTableHtml(result.file2_data, result.file2_highlights, 'highlight-f2');
}

function generateTableHtml(data, highlights, highlightClass) {
    if (!data.length) return "<p>No data</p>";
    const cols = Object.keys(data[0]);
    
    let html = "<table><thead><tr>";
    cols.forEach(c => html += `<th>${c}</th>`);
    html += "</tr></thead><tbody>";
    
    data.forEach((row, idx) => {
        const rowHighlights = highlights[idx] || highlights[String(idx)] || [];
        const isFullRow = rowHighlights.length === cols.length;
        
        html += `<tr class="${isFullRow ? highlightClass : ''}">`;
        cols.forEach(c => {
            const isCellHighlighted = !isFullRow && rowHighlights.includes(c);
            html += `<td class="${isCellHighlighted ? highlightClass : ''}">${row[c]}</td>`;
        });
        html += "</tr>";
    });
    
    html += "</tbody></table>";
    return html;
}

function updateSummary(result) {
    const s = result.stats;
    document.getElementById('summaryBar').textContent = 
        `Rows added: ${s.rows_added}, removed: ${s.rows_removed}, changed cells: ${s.cells_modified}`;
    
    if (result.summary) {
        document.getElementById('llmSummary').textContent = "Agent Insight: " + result.summary;
    } else {
        document.getElementById('llmSummary').textContent = "";
    }
}

function handleExport() {
    if (!lastResult) return;
    
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(lastResult, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", "diff_report.json");
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
}

async function handleKillServer() {
    if (!confirm("Are you sure you want to stop the server? This will kill the backend process immediately. You will need to manually restart it from the terminal.")) {
        return;
    }

    const btn = document.getElementById('killServerBtn');
    btn.disabled = true;
    btn.textContent = "Stopping...";

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 2000);

        await fetch('/admin/shutdown', { 
            method: 'POST', 
            headers: { 
                'X-ADMIN-TOKEN': window.ADMIN_TOKEN 
            },
            signal: controller.signal
        });
        clearTimeout(timeoutId);
    } catch (err) {
        console.log("Server shutdown signal sent.");
    }

    document.body.innerHTML = `
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100vh; background: #f8f9fa; color: #333; font-family: sans-serif;">
            <h1 style="color: #dc3545;">Server Stopped</h1>
            <p>The backend process has been terminated.</p>
            <p>Port 8000 should now be free.</p>
            <p style="margin-top: 1rem; color: #666;">Return to your terminal to restart the app.</p>
        </div>
    `;
}
