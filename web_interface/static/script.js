const chat = document.getElementById('chat');
const input = document.getElementById('input');
const sendBtn = document.getElementById('send-btn');
const modelSelect = document.getElementById('model-select');
const filesList = document.getElementById('files-list');
const refreshFilesBtn = document.getElementById('refresh-files-btn');
const syncDot = document.getElementById('sync-dot');

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function showToast(text) {
  let toast = document.querySelector('.toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.className = 'toast';
    document.body.appendChild(toast);
  }
  toast.textContent = text;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 1800);
}

function guessExtension(lang) {
  const map = {
    python: 'py', py: 'py', javascript: 'js', js: 'js', typescript: 'ts',
    bash: 'sh', sh: 'sh', shell: 'sh', json: 'json', html: 'html',
    css: 'css', java: 'java', c: 'c', cpp: 'cpp', go: 'go', rust: 'rs',
    sql: 'sql', yaml: 'yml', yml: 'yml', markdown: 'md', md: 'md',
  };
  return map[(lang || '').toLowerCase()] || 'txt';
}

// Splits a message into alternating text/code segments using ``` fences
function renderMessage(text) {
  const wrapper = document.createElement('div');
  const parts = text.split(/```(\w*)\n?/);
  // parts alternates: [text, lang, code, text, lang, code, ...]
  for (let i = 0; i < parts.length; i++) {
    if (i % 3 === 0) {
      if (parts[i]) {
        const span = document.createElement('span');
        span.innerHTML = escapeHtml(parts[i]).replace(/\n/g, '<br>');
        wrapper.appendChild(span);
      }
    } else if (i % 3 === 1) {
      const lang = parts[i];
      const code = parts[i + 1] || '';
      i++; // consumed code
      const pre = document.createElement('pre');
      const codeEl = document.createElement('code');
      if (lang) codeEl.className = 'language-' + lang;
      codeEl.textContent = code;
      pre.appendChild(codeEl);

      const actions = document.createElement('div');
      actions.className = 'code-actions';

      const copyBtn = document.createElement('button');
      copyBtn.textContent = 'Copy';
      copyBtn.onclick = () => {
        navigator.clipboard.writeText(code);
        showToast('Copied to clipboard');
      };

      const saveBtn = document.createElement('button');
      saveBtn.textContent = 'Save file';
      saveBtn.onclick = () => saveAsFile(code, lang);

      actions.appendChild(copyBtn);
      actions.appendChild(saveBtn);
      pre.appendChild(actions);
      wrapper.appendChild(pre);

      if (window.hljs) hljs.highlightElement(codeEl);
    }
  }
  return wrapper;
}

async function saveAsFile(code, lang) {
  const ext = guessExtension(lang);
  const suggested = `snippet.${ext}`;
  const filename = prompt('Save as filename (in generated/):', suggested);
  if (!filename) return;

  try {
    const resp = await fetch('/api/save-file', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename, content: code }),
    });
    const data = await resp.json();
    if (data.saved) {
      showToast(`Saved: ${data.path}`);
      // Also trigger a browser download of the same content
      const blob = new Blob([code], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename.split('/').pop();
      a.click();
      URL.revokeObjectURL(url);
    } else {
      showToast('Save failed: ' + (data.error || 'unknown error'));
    }
  } catch (err) {
    showToast('Save failed: ' + err.message);
  }
}

function addMessage(role, text) {
  const el = document.createElement('div');
  el.className = 'msg ' + role;
  el.appendChild(renderMessage(text));
  chat.appendChild(el);
  chat.scrollTop = chat.scrollHeight;
}

async function refreshFiles() {
  try {
    const resp = await fetch('/api/files');
    const data = await resp.json();
    const paths = data.files || [];
    filesList.innerHTML = '';
    if (paths.length === 0) {
      const empty = document.createElement('div');
      empty.className = 'empty';
      empty.textContent = 'Nothing generated yet.';
      filesList.appendChild(empty);
      return;
    }
    paths.forEach(p => {
      const a = document.createElement('a');
      a.href = '/generated/' + p;
      a.textContent = p;
      a.target = '_blank';
      filesList.appendChild(a);
    });
  } catch (err) {
    filesList.innerHTML = '<div class="empty">Could not load files.</div>';
  }
}

refreshFilesBtn.addEventListener('click', refreshFiles);
refreshFiles();

async function send() {
  const message = input.value.trim();
  if (!message) return;
  addMessage('user', message);
  input.value = '';
  input.style.height = 'auto';
  sendBtn.disabled = true;

  try {
    const resp = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, model: modelSelect.value }),
    });
    const data = await resp.json();
    addMessage('assistant', data.response || data.error || 'No response.');
    if (typeof data.last_id === 'number') {
      lastSeenId = Math.max(lastSeenId, data.last_id);
    }

    if (data.saved_files && data.saved_files.length > 0) {
      const banner = document.createElement('div');
      banner.className = 'msg assistant saved-banner';
      banner.style.color = 'var(--mint)';
      banner.innerHTML = 'saved: ' + data.saved_files
        .map(p => `<a href="/generated/${p}" target="_blank" style="color:var(--mint);">${p}</a>`)
        .join(', ');
      chat.appendChild(banner);
      chat.scrollTop = chat.scrollHeight;
      refreshFiles();
    }

    if (data.deleted_files && data.deleted_files.length > 0) {
      const banner = document.createElement('div');
      banner.className = 'msg assistant saved-banner';
      banner.style.color = 'var(--danger)';
      banner.textContent = 'deleted (backed up first): ' + data.deleted_files.join(', ');
      chat.appendChild(banner);
      chat.scrollTop = chat.scrollHeight;
      refreshFiles();
    }
  } catch (err) {
    addMessage('assistant', 'Error: ' + err.message);
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
}

sendBtn.addEventListener('click', send);
input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    send();
  }
});
input.addEventListener('input', () => {
  input.style.height = 'auto';
  input.style.height = Math.min(input.scrollHeight, 140) + 'px';
});

let lastSeenId = 0;

async function loadResumeRecap() {
  try {
    const resp = await fetch('/api/history');
    const data = await resp.json();
    const turns = data.turns || [];
    if (turns.length === 0) return; // first run ever, nothing to resume

    const banner = document.createElement('div');
    banner.className = 'resume-banner';
    banner.textContent = 'picking up where you left off';
    chat.appendChild(banner);

    turns.forEach(t => {
      const role = t.role === 'user' ? 'user' : 'assistant';
      addMessage(role, t.content);
      lastSeenId = Math.max(lastSeenId, t.id);
    });

    const divider = document.createElement('div');
    divider.className = 'resume-divider';
    divider.textContent = 'new messages';
    chat.appendChild(divider);
    chat.scrollTop = chat.scrollHeight;
  } catch (err) {
    // No history yet or backend not ready — silently skip the recap
  }
}

loadResumeRecap();

async function pollForExternalUpdates() {
  // Skip while a send from this tab is in flight, so we never render our
  // own just-saved message twice (once locally, once via poll).
  if (sendBtn.disabled) return;

  try {
    const resp = await fetch(`/api/poll?after_id=${lastSeenId}`);
    const data = await resp.json();
    const turns = data.turns || [];
    if (turns.length === 0) return;

    let addedDivider = false;
    turns.forEach(t => {
      if (!addedDivider) {
        const divider = document.createElement('div');
        divider.className = 'resume-divider';
        divider.textContent = 'from another session';
        chat.appendChild(divider);
        addedDivider = true;
      }
      const role = t.role === 'user' ? 'user' : 'assistant';
      addMessage(role, t.content);
      lastSeenId = Math.max(lastSeenId, t.id);
    });

    if (addedDivider) {
      syncDot.classList.remove('flash');
      // Force reflow so the animation restarts if it fired recently
      void syncDot.offsetWidth;
      syncDot.classList.add('flash');
    }
  } catch (err) {
    // Silently skip — a missed poll just tries again next interval
  }
}

setInterval(pollForExternalUpdates, 4000);
