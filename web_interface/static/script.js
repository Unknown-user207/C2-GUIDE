async function send() {
    const input = document.getElementById('input');
    const message = input.value.trim();
    if (!message) return;
    const chat = document.getElementById('chat');
    chat.innerHTML += `<div><strong>You:</strong> ${message}</div>`;
    input.value = '';
    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
    });
    const data = await response.json();
    chat.innerHTML += `<div><strong>Guide:</strong> ${data.response}</div>`;
    chat.scrollTop = chat.scrollHeight;
}