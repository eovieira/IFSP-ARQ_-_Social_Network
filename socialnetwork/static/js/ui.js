/**
 * Módulo UI - Gerencia renderização de interface
 */

const UI = {
    
    currentPage: 'feed',
    
    /**
     * Inicializa a interface
     */
    init() {
        this.setupNavigation();
        this.setupFormularios();
    },
    
    /**
     * Renderiza aplicação autenticada
     */
    renderizarAppAutenticada() {
        const app = document.getElementById('app');
        const usuario = Auth.getUsuarioAtual();
        
        app.innerHTML = `
            <header class="header">
                <div class="header-container">
                    <a href="#feed" class="logo">Social Network</a>
                    <nav class="nav">
                        <a href="#feed" class="nav-item">Feed</a>
                        <a href="#perfil/${usuario.username}" class="nav-item">Perfil</a>
                        <a href="#topics" class="nav-item">Topics</a>
                    </nav>
                    <div class="user-info">
                        <span class="username">${usuario.username}</span>
                        <button id="btn-logout" class="btn-logout">Logout</button>
                    </div>
                </div>
            </header>
            
            <main class="container">
                <div id="page-feed" class="page">
                    <div class="publicacao-form-wrapper">
                        <textarea id="novo-post" 
                            class="textarea-publicacao" 
                            placeholder="O que está pensando?"></textarea>
                        <button id="btn-publicar" class="btn-publicar">Publicar</button>
                    </div>
                    <div id="feed-container" class="feed-container"></div>
                </div>
                
                <div id="page-perfil" class="page" style="display: none;">
                    <div id="perfil-container"></div>
                </div>
                
                <div id="page-topics" class="page" style="display: none;">
                    <h2>Topics</h2>
                    <p>Em desenvolvimento...</p>
                </div>
            </main>
            
            <div id="notificacao" class="notificacao" style="display: none;"></div>
        `;
        
        // Inicializar módulos
        Feed.init();
        this.setupNavigationListeners();
    },
    
    /**
     * Renderiza aplicação não autenticada
     */
    renderizarAppNaoAutenticada() {
        const app = document.getElementById('app');
        
        app.innerHTML = `
            <div class="auth-container">
                <div class="auth-box">
                    <h1>Social Network</h1>
                    
                    <div class="auth-tabs">
                        <button class="tab-btn active" data-tab="login">Login</button>
                        <button class="tab-btn" data-tab="registro">Registro</button>
                    </div>
                    
                    <div class="tab-content">
                        <form id="form-login" class="auth-form active">
                            <input type="text" 
                                name="username" 
                                placeholder="Usuário" 
                                required>
                            <input type="password" 
                                name="password" 
                                placeholder="Senha" 
                                required>
                            <button type="submit" class="btn-auth">Login</button>
                        </form>
                        
                        <form id="form-registro" class="auth-form">
                            <input type="text" 
                                name="username" 
                                placeholder="Usuário" 
                                required>
                            <input type="email" 
                                name="email" 
                                placeholder="E-mail" 
                                required>
                            <input type="password" 
                                name="password" 
                                placeholder="Senha" 
                                required>
                            <button type="submit" class="btn-auth">Registrar</button>
                        </form>
                    </div>
                </div>
            </div>
            
            <div id="notificacao" class="notificacao" style="display: none;"></div>
        `;
        
        this.setupAuthTabListener();
    },
    
    /**
     * Muda a página visível
     */
    mudarPagina(pagina) {
        // Esconder todas as páginas
        document.querySelectorAll('.page').forEach(p => {
            p.style.display = 'none';
        });
        
        // Mostrar página selecionada
        const pageElement = document.getElementById(`page-${pagina}`);
        if (pageElement) {
            pageElement.style.display = 'block';
        }
        
        this.currentPage = pagina;
    },
    
    /**
     * Mostra notificação
     */
    mostrarNotificacao(mensagem, tipo = 'info') {
        const notificacao = document.getElementById('notificacao');
        if (!notificacao) return;
        
        notificacao.textContent = mensagem;
        notificacao.className = `notificacao ${tipo}`;
        notificacao.style.display = 'block';
        
        setTimeout(() => {
            notificacao.style.display = 'none';
        }, 3000);
    },
    
    /**
     * Setup listener para abas de autenticação
     */
    setupAuthTabListener() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('tab-btn')) {
                const tab = e.target.dataset.tab;
                
                // Atualizar abas
                document.querySelectorAll('.tab-btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                e.target.classList.add('active');
                
                // Atualizar formulários
                document.querySelectorAll('.auth-form').forEach(form => {
                    form.classList.remove('active');
                });
                const form = document.getElementById(`form-${tab}`);
                if (form) form.classList.add('active');
            }
        });
    },
    
    /**
     * Setup listeners para navegação
     */
    setupNavigationListeners() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('nav-item')) {
                e.preventDefault();
                const href = e.target.getAttribute('href');
                this.handleNavigation(href);
            }
            
            // Botão publicar
            if (e.target.id === 'btn-publicar') {
                const textarea = document.getElementById('novo-post');
                if (textarea) {
                    Feed.criarPublicacao(textarea.value);
                    textarea.value = '';
                }
            }
        });
    },
    
    /**
     * Trata navegação por URL
     */
    handleNavigation(href) {
        if (href.startsWith('#feed')) {
            this.mudarPagina('feed');
            Feed.carregarPublicacoes();
        } else if (href.startsWith('#perfil/')) {
            this.mudarPagina('perfil');
            const username = href.split('/')[1];
            Perfil.carregarPerfil(username);
        } else if (href.startsWith('#topics')) {
            this.mudarPagina('topics');
        }
    },
    
    /**
     * Setup geral
     */
    setupFormularios() {
        // Vazio por enquanto, método para futura expansão
    },
    
    setupNavigation() {
        // Gerar menu dinamicamente
    }
};
