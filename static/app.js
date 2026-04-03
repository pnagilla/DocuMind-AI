const API = '';

// ── Auth guard ──
const token = localStorage.getItem('token');
const username = localStorage.getItem('username');
if (!token) window.location.href = '/login';

function authHeaders() {
  return { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };
}

let activeDocumentId = null;

// ── DOM refs ──
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const uploadStatus = document.getElementById('uploadStatus');
const documentList = document.getElementById('documentList');
const messages = document.getElementById('messages');
const questionInput = document.getElementById('questionInput');
const sendBtn = document.getElementById('sendBtn');
const scopeLabel = document.getElementById('scopeLabel');
const logoutBtn = document.getElementById('logoutBtn');

// ── Profile ──
const profileAvatar = document.getElementById('profileAvatar');
const profileName = document.getElementById('profileName');
const profileSection = document.getElementById('profileSection');
const profileDropdown = document.getElementById('profileDropdown');
const dropdownUsername = document.getElementById('dropdownUsername');

if (username) {
  profileName.textContent = username;
  profileAvatar.textContent = username.charAt(0).toUpperCase();
  if (dropdownUsername) dropdownUsername.textContent = username;
}

// Toggle dropdown on click
profileSection.addEventListener('click', (e) => {
  if (e.target.closest('#logoutBtn')) return;
  profileDropdown.classList.toggle('hidden');
  profileSection.classList.toggle('open');
});

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
  if (!profileSection.contains(e.target)) {
    profileDropdown.classList.add('hidden');
    profileSection.classList.remove('open');
  }
});

// ── Logout ──
logoutBtn.addEventListener('click', () => {
  localStorage.removeItem('token');
  localStorage.removeItem('username');
  window.location.href = '/login';
});

// ── Upload ──
dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));

dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('dragover');
  const file = e.dataTransfer.files[0];
  if (file) uploadFile(file);
});

fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) uploadFile(fileInput.files[0]);
});

async function uploadFile(file) {
  if (!file.name.endsWith('.pdf')) {
    showUploadStatus('Only PDF files are supported.', 'error');
    return;
  }

  showUploadStatus('Uploading & processing...', 'loading');

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch(`${API}/api/v1/documents/upload`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData,
    });

    const data = await res.json();

    if (res.status === 401) { logout(); return; }

    if (!res.ok) {
      showUploadStatus(data.detail || 'Upload failed.', 'error');
      return;
    }

    showUploadStatus(`"${data.filename}" uploaded!`, 'success');
    fileInput.value = '';
    await loadDocuments();
  } catch {
    showUploadStatus('Upload failed. Is the server running?', 'error');
  }
}

function showUploadStatus(msg, type) {
  uploadStatus.textContent = msg;
  uploadStatus.className = `upload-status ${type}`;
  uploadStatus.classList.remove('hidden');
  if (type === 'success') setTimeout(() => uploadStatus.classList.add('hidden'), 3000);
}

// ── Documents ──
async function loadDocuments() {
  try {
    const res = await fetch(`${API}/api/v1/documents/`, { headers: authHeaders() });
    if (res.status === 401) { logout(); return; }
    const data = await res.json();
    renderDocuments(data.documents || []);
  } catch { /* silently fail */ }
}

function renderDocuments(docs) {
  if (docs.length === 0) {
    documentList.innerHTML = '<li class="empty-state">No documents uploaded yet</li>';
    return;
  }

  documentList.innerHTML = '';
  docs.forEach((doc) => {
    const li = document.createElement('li');
    li.className = 'document-item' + (doc.document_id === activeDocumentId ? ' active' : '');
    li.innerHTML = `
      <div class="doc-info">
        <div class="doc-name" title="${doc.filename}">${doc.filename}</div>
        <div class="doc-chunks">${doc.chunk_count} chunks indexed</div>
      </div>
      <button class="delete-btn" title="Delete">✕</button>
    `;

    li.addEventListener('click', (e) => {
      if (e.target.classList.contains('delete-btn')) return;
      setActiveDocument(doc.document_id, doc.filename);
      document.querySelectorAll('.document-item').forEach(el => el.classList.remove('active'));
      if (activeDocumentId === doc.document_id) li.classList.add('active');
    });

    li.querySelector('.delete-btn').addEventListener('click', () => deleteDocument(doc.document_id));
    documentList.appendChild(li);
  });
}

function setActiveDocument(id, name) {
  if (activeDocumentId === id) {
    activeDocumentId = null;
    scopeLabel.textContent = 'All documents';
  } else {
    activeDocumentId = id;
    scopeLabel.textContent = name;
  }
}

async function deleteDocument(id) {
  if (!confirm('Delete this document?')) return;
  try {
    await fetch(`${API}/api/v1/documents/${id}`, { method: 'DELETE', headers: authHeaders() });
    if (activeDocumentId === id) {
      activeDocumentId = null;
      scopeLabel.textContent = 'All documents';
    }
    await loadDocuments();
  } catch { alert('Failed to delete document.'); }
}

// ── Chat ──
sendBtn.addEventListener('click', sendMessage);
questionInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) sendMessage();
});

async function sendMessage() {
  const question = questionInput.value.trim();
  if (!question) return;

  appendMessage('user', question);
  questionInput.value = '';
  sendBtn.disabled = true;

  const thinking = appendThinking();

  try {
    const res = await fetch(`${API}/api/v1/chat/`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ question, document_id: activeDocumentId || null }),
    });

    if (res.status === 401) { logout(); return; }

    const data = await res.json();
    thinking.remove();

    if (!res.ok) {
      appendMessage('assistant', data.detail || 'Something went wrong.');
    } else {
      appendMessage('assistant', data.answer, data.sources || []);
    }
  } catch {
    thinking.remove();
    appendMessage('assistant', 'Could not reach the server. Is it running?');
  } finally {
    sendBtn.disabled = false;
    questionInput.focus();
  }
}

function appendMessage(role, text, sources = []) {
  const div = document.createElement('div');
  div.className = `message ${role}`;

  const bubbleWrapper = document.createElement('div');
  bubbleWrapper.className = 'bubble-wrapper';

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = text;
  bubbleWrapper.appendChild(bubble);

  if (role === 'assistant' && sources.length > 0) {
    // Group pages by filename
    const fileMap = {};
    sources.forEach(s => {
      const name = s.document_name || 'Unknown file';
      if (!fileMap[name]) fileMap[name] = new Set();
      if (s.page_number) fileMap[name].add(s.page_number);
    });

    const tooltip = document.createElement('div');
    tooltip.className = 'source-tooltip';

    const tooltipTitle = document.createElement('div');
    tooltipTitle.className = 'tooltip-title';
    tooltipTitle.textContent = `Sources (${Object.keys(fileMap).length} file${Object.keys(fileMap).length > 1 ? 's' : ''})`;
    tooltip.appendChild(tooltipTitle);

    Object.entries(fileMap).forEach(([filename, pages]) => {
      const row = document.createElement('div');
      row.className = 'tooltip-row';
      const pageList = [...pages].sort((a, b) => a - b).map(p => `p.${p}`).join(', ');
      row.innerHTML = `<span class="tooltip-file">📄 ${filename}</span><span class="tooltip-page">${pageList}</span>`;
      tooltip.appendChild(row);
    });

    bubbleWrapper.appendChild(tooltip);
    bubble.classList.add('has-sources');
  }

  div.appendChild(bubbleWrapper);
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
  return div;
}

function appendThinking() {
  const div = document.createElement('div');
  div.className = 'message assistant';
  div.innerHTML = '<div class="thinking">Thinking...</div>';
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
  return div;
}

function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('username');
  window.location.href = '/login';
}

// ── Init ──
loadDocuments();
