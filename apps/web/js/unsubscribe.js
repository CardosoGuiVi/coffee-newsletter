const form = document.getElementById('unsubscribeForm');
const emailInput = document.getElementById('email');
const submitBtn = document.getElementById('submitBtn');
const messageEl = document.getElementById('formMessage');

// Prefill the email from the query string (e.g. /unsubscribe?email=you@example.com)
const prefill = new URLSearchParams(window.location.search).get('email');
if (prefill) emailInput.value = prefill;

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = emailInput.value.trim();
    if (!email) return;

    submitBtn.disabled = true;
    submitBtn.textContent = 'Cancelando…';
    messageEl.className = 'form-message';
    messageEl.textContent = '';

    try {
        const res = await fetch(`${window.API_BASE ?? ''}/v1/unsubscribe`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email }),
        });
        const data = await res.json().catch(() => ({}));

        if (res.ok) {
            messageEl.className = 'form-message success';
            messageEl.textContent = 'Pronto, você foi removido da lista. Sentiremos sua falta. ☕';
            form.reset();
        } else if (res.status === 404) {
            messageEl.className = 'form-message error';
            messageEl.textContent = 'Não encontramos esse e-mail na nossa lista.';
        } else {
            messageEl.className = 'form-message error';
            messageEl.textContent = data.detail ?? 'Não foi possível cancelar. Tente novamente.';
        }
    } catch {
        messageEl.className = 'form-message error';
        messageEl.textContent = 'Erro ao conectar. Tente novamente.';
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Cancelar inscrição';
    }
});
