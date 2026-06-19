const form = document.getElementById('subscribeForm');
const emailInput = document.getElementById('email');
const submitBtn = document.getElementById('submitBtn');
const messageEl = document.getElementById('formMessage');
const totalEl = document.getElementById('totalSubscribers');
const weekEl = document.getElementById('weekSubscribers');

loadStats();
setInterval(loadStats, 30000);

async function loadStats() {
    try {
        const res = await fetch(`${window.API_BASE ?? ''}/v1/stats`);
        if (res.ok) {
            const data = await res.json();
            animateCount(totalEl, data.total_subscribers);
            animateCount(weekEl, data.joined_this_week);
        }
    } catch (e) {
        console.error('Erro ao carregar estatísticas:', e);
    }
}

function animateCount(el, target) {
    const current = parseInt(el.textContent.replace(/\D/g, '')) || 0;
    if (current === target) { el.textContent = target.toLocaleString('pt-BR'); return; }
    const step = Math.max(1, Math.ceil(Math.abs(target - current) / 24));
    const dir = target > current ? 1 : -1;
    let val = current;
    const tick = setInterval(() => {
        val += dir * step;
        if ((dir > 0 && val >= target) || (dir < 0 && val <= target)) {
            val = target; clearInterval(tick);
        }
        el.textContent = val.toLocaleString('pt-BR');
    }, 28);
}

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = emailInput.value.trim();
    if (!email) return;

    submitBtn.disabled = true;
    submitBtn.textContent = 'Enviando…';
    messageEl.className = 'form-message';
    messageEl.textContent = '';

    try {
        const res = await fetch(`${window.API_BASE ?? ''}/v1/subscribe`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email }),
        });
        const data = await res.json();

        if (res.ok) {
            messageEl.className = 'form-message success';
            messageEl.textContent = 'Inscrição confirmada! Até segunda-feira. ☕';
            form.reset();
            loadStats();
            setTimeout(() => { messageEl.className = 'form-message'; messageEl.textContent = ''; }, 6000);
        } else {
            messageEl.className = 'form-message error';
            messageEl.textContent = data.detail;
        }
    } catch {
        messageEl.className = 'form-message error';
        messageEl.textContent = 'Erro ao conectar. Tente novamente.';
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Assinar grátis';
    }
});