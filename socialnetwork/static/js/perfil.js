document.addEventListener("DOMContentLoaded", () => {

    // Função utilitária
    async function postAndUpdate(url, data = {}, method = 'POST') {
        const res = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return res.json();
    }

    // ---------------- SEGUIR / DEIXAR ----------------
    document.querySelectorAll('.botao-seguir').forEach(botao => {
        botao.addEventListener('click', async e => {
            e.preventDefault();
            const username = botao.dataset.username;
            const acao = botao.dataset.acao;
            const url = acao === "seguir"
                ? `/seguir_ajax/${username}`
                : `/deixar_de_seguir_ajax/${username}`;

            const data = await postAndUpdate(url);

            if (data.status === 'seguindo') {
                botao.textContent = 'Deixar de seguir';
                botao.dataset.acao = 'deixar';
            } else if (data.status === 'nao_seguindo') {
                botao.textContent = 'Seguir';
                botao.dataset.acao = 'seguir';
            }

            // Atualiza contagem de seguidores
            const contador = document.querySelector('#contador-seguidores');
            if (contador) contador.textContent = `Seguidores: ${data.quantia_seguidores}, Seguindo: ${data.quantia_seguindo}`;
        });
    });

    // ---------------- BLOQUEAR / DESBLOQUEAR ----------------
    const acoesUsuario = document.getElementById('acoes-usuario');
    const mensagemBloqueio = document.getElementById('mensagem-bloqueio');
    const botaoDesbloquear = document.getElementById('botao-desbloquear');

    // Botão bloquear
    document.querySelectorAll('.botao-bloqueio').forEach(botao => {
        botao.addEventListener('click', async e => {
        e.preventDefault();
        const username = botao.dataset.username;
        const acao = botao.dataset.acao;
        if (acao !== "bloquear") return; // só bloquear aqui

        const res = await fetch(`/bloquear_ajax/${username}`, {
            method: 'POST',
            credentials: 'same-origin'
        });
        const data = await res.json();

        if (data.status === 'bloqueado') {
            // Esconde os botões seguir/bloquear
            if (acoesUsuario) acoesUsuario.style.display = 'none';

            // Exibe mensagem de bloqueio
            if (mensagemBloqueio) mensagemBloqueio.style.display = 'block';

            // Atualiza botão desbloquear com username correto
            if (botaoDesbloquear) {
            botaoDesbloquear.dataset.username = username;
            botaoDesbloquear.dataset.acao = 'desbloquear';
            }
        }
        });
    });

    // Botão desbloquear dentro da mensagem bloqueio
    if (botaoDesbloquear) {
        botaoDesbloquear.addEventListener('click', async e => {
        e.preventDefault();
        const username = botaoDesbloquear.dataset.username;

        const res = await fetch(`/desbloquear_ajax/${username}`, {
            method: 'POST',
            credentials: 'same-origin'
        });
        const data = await res.json();

        if (data.status === 'desbloqueado') {
            // Esconde a mensagem bloqueio
            if (mensagemBloqueio) mensagemBloqueio.style.display = 'none';

            // Mostra os botões seguir/bloquear
            if (acoesUsuario) acoesUsuario.style.display = 'block';

            // Atualiza botões para o estado padrão (seguir e bloquear)
            const botaoSeguir = document.querySelector(`.botao-seguir[data-username="${username}"]`);
            if (botaoSeguir) {
            botaoSeguir.textContent = 'Seguir';
            botaoSeguir.dataset.acao = 'seguir';
            botaoSeguir.disabled = false;
            }
            if (botaoDesbloquear) {
            // Atualiza botão desbloquear para bloquear
            botaoDesbloquear.dataset.acao = 'bloquear';
            botaoDesbloquear.textContent = 'Bloquear';
            }
        }
        });
    }

    // ---------------- CURTIR/ DESCURTIR ----------------
    document.querySelectorAll('.botao-like').forEach(form => {
        form.addEventListener('submit', async e => {
            e.preventDefault();
            const url = form.getAttribute('action');
            const res = await fetch(url, { method: 'POST' });
            const data = await res.json();

            const icon = form.querySelector('i');
            const span = form.nextElementSibling;

            if (data.status === 'curtido') {
                icon.classList.add('liked');
            } else {
                icon.classList.remove('liked');
            }
            if (span) span.textContent = `${data.total} curtidas`;
        });
    });

    // ---------------- COMENTAR ----------------
    document.querySelectorAll('.form-comentario').forEach(form => {
        form.addEventListener('submit', async e => {
            e.preventDefault();
            const url = form.getAttribute('action');
            const texto = form.querySelector('input[name="texto"]').value;

            const res = await postAndUpdate(url, { texto });
            if (res.html) {
                const nova = document.createElement('div');
                nova.innerHTML = res.html;
                form.insertAdjacentElement('beforebegin', nova);
                form.reset();
            }
        });
    });

    // ---------------- RESPONDER ----------------
    document.querySelectorAll('.form-resposta').forEach(form => {
        form.addEventListener('submit', async e => {
            e.preventDefault();
            const url = form.getAttribute('action');
            const texto = form.querySelector('input[name="texto"]').value;

            const res = await postAndUpdate(url, { texto });
            if (res.html) {
                const nova = document.createElement('div');
                nova.innerHTML = res.html;
                form.insertAdjacentElement('beforebegin', nova);
                form.reset();
            }
        });
    });

    // ---------------- DELETAR ----------------
    document.querySelectorAll('.form-deletar').forEach(form => {
        form.addEventListener('submit', async e => {
            e.preventDefault();
            if (!confirm('Tem certeza que deseja excluir?')) return;

            const res = await fetch(form.getAttribute('action'), { method: 'POST' });
            if (res.ok) {
                form.closest('.publicacoes, .comentario, .resposta')?.remove();
            }
        });
    });
});
