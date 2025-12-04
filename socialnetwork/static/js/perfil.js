/**
 * Módulo Perfil - Gerencia visualização de perfis
 */

const Perfil = {
    
    usuarioAtual: null,
    
    /**
     * Carrega e renderiza um perfil
     */
    async carregarPerfil(username) {
        const result = await API.obterPerfil(username);
        
        if (!result.ok) {
            UI.mostrarNotificacao('Perfil não encontrado', 'erro');
            UI.mudarPagina('feed');
            return;
        }
        
        this.usuarioAtual = result.data.usuario;
        this.renderizarPerfil();
    },
    
    /**
     * Renderiza o perfil na tela
     */
    renderizarPerfil() {
        const container = document.getElementById('perfil-container');
        if (!container) return;
        
        const usuario = this.usuarioAtual;
        const usuarioLogado = Auth.getUsuarioAtual();
        const eProprioUsuario = usuarioLogado && usuarioLogado.id === usuario.id;
        
        let statusSeguimento = 'não_seguindo';
        let statusBloqueio = 'não_bloqueado';
        
        // Verificar status de relacionamento
        if (usuario.seguidores && usuario.seguidores.length > 0) {
            if (usuario.seguidores.some(s => s.seguidor_id === usuarioLogado.id)) {
                statusSeguimento = 'seguindo';
            }
        }
        
        if (usuario.bloqueados && usuario.bloqueados.length > 0) {
            if (usuario.bloqueados.some(b => b.bloqueado_id === usuarioLogado.id)) {
                statusBloqueio = 'bloqueado';
            }
        }
        
        container.innerHTML = `
            <div class="perfil-header">
                <h2>${usuario.username}</h2>
                <p class="email">${usuario.email}</p>
                
                <div class="perfil-stats">
                    <div class="stat">
                        <span class="stat-numero">${usuario.publicacoes ? usuario.publicacoes.length : 0}</span>
                        <span class="stat-label">Publicações</span>
                    </div>
                    <div class="stat">
                        <span class="stat-numero">${usuario.seguindo ? usuario.seguindo.length : 0}</span>
                        <span class="stat-label">Seguindo</span>
                    </div>
                    <div class="stat">
                        <span class="stat-numero">${usuario.seguidores ? usuario.seguidores.length : 0}</span>
                        <span class="stat-label">Seguidores</span>
                    </div>
                </div>
                
                ${!eProprioUsuario ? `
                    <div class="perfil-actions">
                        <button class="btn-seguir" data-username="${usuario.username}" data-status="${statusSeguimento}">
                            ${statusSeguimento === 'seguindo' ? 'Deixar de seguir' : 'Seguir'}
                        </button>
                        <button class="btn-bloquear" data-username="${usuario.username}" data-status="${statusBloqueio}">
                            ${statusBloqueio === 'bloqueado' ? 'Desbloquear' : 'Bloquear'}
                        </button>
                    </div>
                ` : ''}
            </div>
            
            <div class="perfil-publicacoes">
                <h3>Publicações</h3>
                <div id="lista-publicacoes-perfil"></div>
            </div>
        `;
        
        this.carregarPublicacoesPerfil(usuario.username);
        this.setupEventListeners();
    },
    
    /**
     * Carrega publicações do perfil
     */
    async carregarPublicacoesPerfil(username) {
        const result = await API.obterPublicacoesPerfil(username);
        
        if (result.ok) {
            const publicacoes = result.data.publicacoes || [];
            const container = document.getElementById('lista-publicacoes-perfil');
            
            if (!container) return;
            
            container.innerHTML = '';
            
            if (publicacoes.length === 0) {
                container.innerHTML = '<p class="sem-publicacoes">Este usuário ainda não fez publicações</p>';
                return;
            }
            
            publicacoes.forEach(pub => {
                const pubElement = Feed.criarElementoPublicacao(pub);
                container.appendChild(pubElement);
            });
        }
    },
    
    /**
     * Segue um usuário
     */
    async seguirUsuario(username) {
        const result = await API.seguirUsuario(username);
        
        if (result.ok) {
            UI.mostrarNotificacao('Seguindo!', 'sucesso');
            const btn = document.querySelector(`.btn-seguir[data-username="${username}"]`);
            if (btn) {
                btn.textContent = 'Deixar de seguir';
                btn.dataset.status = 'seguindo';
            }
        } else {
            UI.mostrarNotificacao(result.data.erro || 'Erro ao seguir', 'erro');
        }
    },
    
    /**
     * Deixa de seguir um usuário
     */
    async deixarDeSeguir(username) {
        const result = await API.deixarDeSeguir(username);
        
        if (result.ok) {
            UI.mostrarNotificacao('Deixou de seguir', 'sucesso');
            const btn = document.querySelector(`.btn-seguir[data-username="${username}"]`);
            if (btn) {
                btn.textContent = 'Seguir';
                btn.dataset.status = 'não_seguindo';
            }
        } else {
            UI.mostrarNotificacao(result.data.erro || 'Erro ao deixar de seguir', 'erro');
        }
    },
    
    /**
     * Bloqueia um usuário
     */
    async bloquearUsuario(username) {
        const result = await API.bloquearUsuario(username);
        
        if (result.ok) {
            UI.mostrarNotificacao('Usuário bloqueado!', 'sucesso');
            const btn = document.querySelector(`.btn-bloquear[data-username="${username}"]`);
            if (btn) {
                btn.textContent = 'Desbloquear';
                btn.dataset.status = 'bloqueado';
            }
        } else {
            UI.mostrarNotificacao(result.data.erro || 'Erro ao bloquear', 'erro');
        }
    },
    
    /**
     * Desbloqueia um usuário
     */
    async desbloquearUsuario(username) {
        const result = await API.desbloquearUsuario(username);
        
        if (result.ok) {
            UI.mostrarNotificacao('Usuário desbloqueado!', 'sucesso');
            const btn = document.querySelector(`.btn-bloquear[data-username="${username}"]`);
            if (btn) {
                btn.textContent = 'Bloquear';
                btn.dataset.status = 'não_bloqueado';
            }
        } else {
            UI.mostrarNotificacao(result.data.erro || 'Erro ao desbloquear', 'erro');
        }
    },
    
    /**
     * Setup de event listeners
     */
    setupEventListeners() {
        document.addEventListener('click', (e) => {
            // Seguir/deixar de seguir
            if (e.target.classList.contains('btn-seguir')) {
                const username = e.target.dataset.username;
                const status = e.target.dataset.status;
                if (status === 'seguindo') {
                    this.deixarDeSeguir(username);
                } else {
                    this.seguirUsuario(username);
                }
            }
            
            // Bloquear/desbloquear
            if (e.target.classList.contains('btn-bloquear')) {
                const username = e.target.dataset.username;
                const status = e.target.dataset.status;
                if (status === 'bloqueado') {
                    this.desbloquearUsuario(username);
                } else {
                    this.bloquearUsuario(username);
                }
            }
        });
    }
};
