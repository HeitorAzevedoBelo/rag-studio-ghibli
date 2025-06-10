const chatContainer = document.getElementById('chat-container');
const inputPergunta = document.getElementById('pergunta');
const btnEnviar = document.getElementById('enviar');

function appendMessage(text, sender) {
  const wrapper = document.createElement('div');
  wrapper.classList.add(sender);
  const msg = document.createElement('div');
  msg.classList.add('message');
  msg.innerHTML = text.replace(/\n/g, '<br/>');
  wrapper.appendChild(msg);
  chatContainer.appendChild(wrapper);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function enviarPergunta() {
  const pergunta = inputPergunta.value.trim();
  if (!pergunta) return;
  appendMessage(pergunta, 'user');
  inputPergunta.value = '';
  try {
    const resp = await fetch('/explorar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pergunta })
    });
    const data = await resp.json();
    if (resp.ok) {
      appendMessage(data.resposta, 'bot');
    } else {
      appendMessage(`<em>Erro: ${data.erro}</em>`, 'bot');
    }
  } catch (err) {
    appendMessage(`<em>Erro de conexão com os espíritos da floresta</em>`, 'bot');
  }
}

btnEnviar.addEventListener('click', enviarPergunta);
inputPergunta.addEventListener('keypress', e => {
  if (e.key === 'Enter') enviarPergunta();
});
