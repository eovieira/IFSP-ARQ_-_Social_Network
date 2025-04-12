function submitForm(formId) {
    var form = document.getElementById(formId);
    if (form) {
        form.submit();
    }
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
    if (formulario.style.display === 'none' || formulario.style.display === '') {
        formulario.style.display = 'flex';
        formulario.querySelector('input[name="texto"]').focus();
    } else {
        formulario.style.display = 'none';
    }
}