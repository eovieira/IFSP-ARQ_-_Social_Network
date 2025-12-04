/**
 * Módulo Feed - Gerencia publicações, comentários e interações
 */

const Feed = {
    
    publicacoes: [],
    publicacaoSelecionada: null,
    
    /**
     * Inicializa o módulo de feed
     */
    init() {
        this.setupEventListeners();
        this.carregarPublicacoes();
    },
    
    /**
     * Carrega todas as publicações
     */
    async carregarPublicacoes() {
        if (!Auth.estaAutenticado()) return;
        
        const result = await API.obterPublicacoes();
        
        if (result.ok) {
            this.publicacoes = result.data.publicacoes || [];
            this.renderizarFeed();
        } else {
            UI.mostrarNotificacao('Erro ao carregar publicações', 'erro');
        }
    },
    
    /**
     * Renderiza o feed na tela
     */
    renderizarFeed() {
        const feedContainer = document.getElementById('feed-container');
        if (!feedContainer) return;
        
        feedContainer.innerHTML = '';
        
        this.publicacoes.forEach(pub => {
            const pubElement = this.criarElementoPublicacao(pub);
            feedContainer.appendChild(pubElement);
        });
    },
    
    /**
     * Cria elemento HTML para uma publicação
     */
    criarElementoPublicacao(pub) {
        const div = document.createElement('div');
        div.className = 'publicacao';
        div.id = `pub-${pub.id}`;
        
        const dataFormatada = new Date(pub.data_criacao).toLocaleString('pt-BR');
        const autor = pub.usuario ? pub.usuario.username : 'Desconhecido';
        const temPerfilAutor = Auth.currentUser && Auth.currentUser.id === pub.usuario_id;
        
        div.innerHTML = `
            <div class="publicacao-header">
                <a href="#perfil/${autor}" class="autor-link">${autor}</a>
                <span class="data">${dataFormatada}</span>
                ${temPerfilAutor ? `
                    <button class="btn-deletar" data-pub-id="${pub.id}">
                        <i class="material-icons">delete</i>
                    </button>
                ` : ''}
            </div>
            
            <div class="publicacao-texto">
                ${pub.texto.replace(/\n/g, '<br>')}
            </div>
            
            <div class="publicacao-stats">
                <span class="curtidas" id="curtidas-${pub.id}">${pub.curtidas || 0} curtidas</span>
                <span class="comentarios">${pub.comentarios ? pub.comentarios.length : 0} comentários</span>
            </div>
            
            <div class="publicacao-actions">
                <button class="btn-curtir" data-pub-id="${pub.id}">
                    <i class="material-icons">favorite_border</i> Curtir
                </button>
                <button class="btn-comentar" data-pub-id="${pub.id}">
                    <i class="material-icons">comment</i> Comentar
                </button>
            </div>
            
            <div class="comentarios-section" id="comentarios-${pub.id}" style="display: none;">
                <div class="form-comentario-wrapper">
                    <input type="text" 
                        class="input-comentario" 
                        placeholder="Escreva um comentário..." 
                        data-pub-id="${pub.id}">
                    <button class="btn-enviar-comentario" data-pub-id="${pub.id}">
                        <i class="material-icons">send</i>
                    </button>
                </div>
                <div class="lista-comentarios" id="lista-comentarios-${pub.id}"></div>
            </div>
        `;
        
        return div;
    },
    
    /**
     * Renderiza comentários de uma publicação
     */
    async renderizarComentarios(publicacao_id) {
        const result = await API.obterComentarios(publicacao_id);
        
        if (!result.ok) return;
        
        const comentarios = result.data.comentarios || [];
        const listaContainer = document.getElementById(`lista-comentarios-${publicacao_id}`);
        
        if (!listaContainer) return;
        
        listaContainer.innerHTML = '';
        
        comentarios.forEach(com => {
            const comElement = this.criarElementoComentario(com, publicacao_id);
            listaContainer.appendChild(comElement);
        });
    },
    
    /**
     * Cria elemento HTML para um comentário
     */
    criarElementoComentario(com, publicacao_id) {
        const div = document.createElement('div');
        div.className = 'comentario';
        div.id = `com-${com.id}`;
        
        const dataFormatada = new Date(com.data_criacao).toLocaleString('pt-BR');
        const autor = com.usuario ? com.usuario.username : 'Desconhecido';
        const temPermissao = Auth.currentUser && Auth.currentUser.id === com.usuario_id;
        
        div.innerHTML = `
            <div class="comentario-header">
                <a href="#perfil/${autor}" class="autor-link">${autor}</a>
                <span class="data">${dataFormatada}</span>
                ${temPermissao ? `
                    <button class="btn-deletar-comentario" data-com-id="${com.id}">
                        <i class="material-icons">delete</i>
                    </button>
                ` : ''}
            </div>
            
            <div class="comentario-texto">
                ${com.texto.replace(/\n/g, '<br>')}
            </div>
            
            <div class="comentario-actions">
                <button class="btn-curtir-comentario" data-com-id="${com.id}">
                    <i class="material-icons">favorite_border</i> Curtir
                </button>
                <button class="btn-responder-comentario" data-com-id="${com.id}">
                    <i class="material-icons">reply</i> Responder
                </button>
            </div>
            
            <div class="respostas-section" id="respostas-${com.id}"></div>
        `;
        
        return div;
    },
    
    /**
     * Cria uma nova publicação
     */
    async criarPublicacao(texto) {
        if (!texto.trim()) {
            UI.mostrarNotificacao('Publicação não pode estar vazia', 'erro');
            return;
        }
        
        const result = await API.criarPublicacao(texto);
        
        if (result.ok) {
            UI.mostrarNotificacao('Publicação criada com sucesso!', 'sucesso');
            this.carregarPublicacoes();
        } else {
            const mensagemErro = result.data && result.data.erro ? result.data.erro : 'Erro ao criar publicação';
            UI.mostrarNotificacao(mensagemErro, 'erro');
        }
    },
    
    /**
     * Adiciona um comentário a uma publicação
     */
    async adicionarComentario(publicacao_id, texto) {
        if (!texto.trim()) {
            UI.mostrarNotificacao('Comentário não pode estar vazio', 'erro');
            return;
        }
        
        const result = await API.adicionarComentario(publicacao_id, texto);
        
        if (result.ok) {
            UI.mostrarNotificacao('Comentário adicionado!', 'sucesso');
            this.renderizarComentarios(publicacao_id);
        } else {
            UI.mostrarNotificacao(result.data.erro || 'Erro ao adicionar comentário', 'erro');
        }
    },
    
    /**
     * Adiciona uma resposta a um comentário
     */
    async adicionarResposta(comentario_id, texto) {
        if (!texto.trim()) {
            UI.mostrarNotificacao('Resposta não pode estar vazia', 'erro');
            return;
        }
        
        const result = await API.adicionarResposta(comentario_id, texto);
        
        if (result.ok) {
            UI.mostrarNotificacao('Resposta adicionada!', 'sucesso');
            // Recarregar comentários
            const pubId = document.getElementById(`com-${comentario_id}`).closest('.publicacao').id.split('-')[1];
            this.renderizarComentarios(pubId);
        } else {
            UI.mostrarNotificacao(result.data.erro || 'Erro ao adicionar resposta', 'erro');
        }
    },
    
    /**
     * Deleta uma publicação
     */
    async deletarPublicacao(publicacao_id) {
        if (!confirm('Tem certeza que deseja deletar esta publicação?')) return;
        
        const result = await API.deletarPublicacao(publicacao_id);
        
        if (result.ok) {
            UI.mostrarNotificacao('Publicação deletada!', 'sucesso');
            this.carregarPublicacoes();
        } else {
            UI.mostrarNotificacao(result.data.erro || 'Erro ao deletar publicação', 'erro');
        }
    },
    
    /**
     * Deleta um comentário
     */
    async deletarComentario(comentario_id) {
        if (!confirm('Tem certeza que deseja deletar este comentário?')) return;
        
        const result = await API.deletarComentario(comentario_id);
        
        if (result.ok) {
            UI.mostrarNotificacao('Comentário deletado!', 'sucesso');
            // Remover do DOM
            const comElement = document.getElementById(`com-${comentario_id}`);
            if (comElement) {
                comElement.remove();
            }
        } else {
            UI.mostrarNotificacao(result.data.erro || 'Erro ao deletar comentário', 'erro');
        }
    },
    
    /**
     * Deleta uma resposta
     */
    async deletarResposta(resposta_id) {
        if (!confirm('Tem certeza que deseja deletar esta resposta?')) return;
        
        const result = await API.deletarResposta(resposta_id);
        
        if (result.ok) {
            UI.mostrarNotificacao('Resposta deletada!', 'sucesso');
            const respElement = document.getElementById(`res-${resposta_id}`);
            if (respElement) {
                respElement.remove();
            }
        } else {
            UI.mostrarNotificacao(result.data.erro || 'Erro ao deletar resposta', 'erro');
        }
    },
    
    /**
     * Curte uma publicação
     */
    async curtirPublicacao(publicacao_id) {
        const result = await API.curtirPublicacao(publicacao_id);
        
        if (result.ok) {
            // Atualizar contador localmente
            const contadorElement = document.getElementById(`curtidas-${publicacao_id}`);
            if (contadorElement) {
                const novoValor = (parseInt(contadorElement.textContent) || 0) + 1;
                contadorElement.textContent = `${novoValor} curtidas`;
            }
        } else {
            UI.mostrarNotificacao(result.data.erro || 'Erro ao curtir', 'erro');
        }
    },
    
    /**
     * Descurte uma publicação
     */
    async descurtirPublicacao(publicacao_id) {
        const result = await API.descurtirPublicacao(publicacao_id);
        
        if (result.ok) {
            const contadorElement = document.getElementById(`curtidas-${publicacao_id}`);
            if (contadorElement) {
                const novoValor = Math.max(0, (parseInt(contadorElement.textContent) || 1) - 1);
                contadorElement.textContent = `${novoValor} curtidas`;
            }
        } else {
            UI.mostrarNotificacao(result.data.erro || 'Erro ao descurtir', 'erro');
        }
    },
    
    /**
     * Configura event listeners para o feed
     */
    setupEventListeners() {
        document.addEventListener('click', (e) => {
            // Comentar
            if (e.target.closest('.btn-comentar')) {
                const pubId = e.target.closest('.btn-comentar').dataset.pubId;
                const secao = document.getElementById(`comentarios-${pubId}`);
                if (secao) {
                    secao.style.display = secao.style.display === 'none' ? 'block' : 'none';
                    if (secao.style.display === 'block') {
                        this.renderizarComentarios(pubId);
                        secao.querySelector('.input-comentario').focus();
                    }
                }
            }
            
            // Enviar comentário
            if (e.target.closest('.btn-enviar-comentario')) {
                const pubId = e.target.closest('.btn-enviar-comentario').dataset.pubId;
                const input = document.querySelector(`.input-comentario[data-pub-id="${pubId}"]`);
                if (input) {
                    this.adicionarComentario(pubId, input.value);
                    input.value = '';
                }
            }
            
            // Curtir publicação
            if (e.target.closest('.btn-curtir')) {
                const pubId = e.target.closest('.btn-curtir').dataset.pubId;
                this.curtirPublicacao(pubId);
            }
            
            // Deletar publicação
            if (e.target.closest('.btn-deletar')) {
                const pubId = e.target.closest('.btn-deletar').dataset.pubId;
                this.deletarPublicacao(pubId);
            }
            
            // Deletar comentário
            if (e.target.closest('.btn-deletar-comentario')) {
                const comId = e.target.closest('.btn-deletar-comentario').dataset.comId;
                this.deletarComentario(comId);
            }
        });
        
        // Enviar comentário com Enter
        document.addEventListener('keypress', (e) => {
            if (e.target.classList.contains('input-comentario') && e.key === 'Enter') {
                e.preventDefault();
                const pubId = e.target.dataset.pubId;
                const btn = document.querySelector(`.btn-enviar-comentario[data-pub-id="${pubId}"]`);
                if (btn) btn.click();
            }
        });
    }
};
