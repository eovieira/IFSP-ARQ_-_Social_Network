function submitForm(formId) {
    var form = document.getElementById(formId);
    if (form) {
        form.submit();
    }
}

function abrirModalComentarios(publicacaoId) {
    fetch(`/comentarios/${publicacaoId}`)
        .then(res => {
            if (!res.ok) throw new Error("Erro na requisição");
            return res.text();
        })
        .then(html => {
            const modalConteudo = document.getElementById("modalComentariosConteudo");
            modalConteudo.innerHTML = html;
            const modal = document.getElementById("modalComentarios");
            modal.style.display = "flex";

            // Para fechar o modal clicando fora do conteúdo
            modal.onclick = fecharModalComentarios;
        })
        .catch(err => console.error("Erro ao carregar comentários:", err));
}

function fecharModalComentarios() {
    const modal = document.getElementById("modalComentarios");
    modal.style.display = "none";
    // Limpa conteúdo para evitar dados antigos
    document.getElementById("modalComentariosConteudo").innerHTML = "";
}

function mostrarFormulario(event, comentarioId) {
    event.stopPropagation();
    comentarioId = parseInt(comentarioId);

    const formularios = document.querySelectorAll('.form-resposta');
    formularios.forEach(form => {
        if (form.id !== `responder-${comentarioId}`) {
            form.style.display = 'none';
        }
    });

    const formulario = document.getElementById(`responder-${comentarioId}`);
    if (!formulario) return;

    if (formulario.style.display === 'none' || formulario.style.display === '') {
        formulario.style.display = 'flex';
        formulario.querySelector('input[name="texto"]').focus();
    } else {
        formulario.style.display = 'none';
    }
}

function mostrarFormularioComentario(event, publicacaoId) {
    event.stopPropagation();
    publicacaoId = parseInt(publicacaoId);

    const formularios = document.querySelectorAll('.form-comentario');
    formularios.forEach(form => {
        if (form.id !== `comentar-${publicacaoId}`) {
            form.style.display = 'none';
        }
    });

    const formulario = document.getElementById(`comentar-${publicacaoId}`);
    if (!formulario) return;

    if (formulario.style.display === 'none' || formulario.style.display === '') {
        formulario.style.display = 'flex';
        formulario.querySelector('input[name="texto"]').focus();
    } else {
        formulario.style.display = 'none';
    }
}

function toggleDropdown(button) {
    const dropdown = button.closest(".dropdown");
    const menu = dropdown.querySelector(".dropdown-menu");

    document.querySelectorAll(".dropdown-menu").forEach(m => {
        if (m !== menu) m.style.display = "none";
    });

    menu.style.display = menu.style.display === "block" ? "none" : "block";
}

document.addEventListener("click", function (event) {
    if (!event.target.closest(".dropdown")) {
        document.querySelectorAll(".dropdown-menu").forEach(m => m.style.display = "none");
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.querySelector('.form-publicar textarea');
    
    if (textarea) {
        textarea.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && e.shiftKey) {
                // Shift+Enter - insere quebra de linha
                e.preventDefault();
                const start = this.selectionStart;
                const end = this.selectionEnd;
                
                // Insere a quebra de linha na posição do cursor
                this.value = this.value.substring(0, start) + "\n" + this.value.substring(end);
                
                // Move o cursor para depois da quebra de linha inserida
                this.selectionStart = this.selectionEnd = start + 1;
            } else if (e.key === 'Enter' && !e.shiftKey) {
                // Apenas Enter - submete o formulário
                e.preventDefault();
                this.closest('form').submit();
            }
        });
    }
});