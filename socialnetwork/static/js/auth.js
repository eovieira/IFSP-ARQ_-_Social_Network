/**
 * Módulo de Autenticação
 * Gerencia login, logout e estado de autenticação
 */

const Auth = {
    
    currentUser: null,
    isAuthenticated: false,
    
    /**
     * Inicializa o módulo de autenticação
     */
    init() {
        this.checkCurrentUser();
        this.setupEventListeners();
    },
    
    /**
     * Verifica se há usuário logado
     */
    async checkCurrentUser() {
        const result = await API.obterUsuarioAtual();
        if (result.ok && result.data.usuario) {
            this.currentUser = result.data.usuario;
            this.isAuthenticated = true;
            UI.renderizarAppAutenticada();
        } else {
            this.currentUser = null;
            this.isAuthenticated = false;
            UI.renderizarAppNaoAutenticada();
        }
    },
    
    /**
     * Realiza login
     */
    async login(username, password) {
        const result = await API.login(username, password);
        
        if (result.ok) {
            this.currentUser = result.data.usuario;
            this.isAuthenticated = true;
            UI.renderizarAppAutenticada();
            UI.mostrarNotificacao('Login realizado com sucesso!', 'sucesso');
            return true;
        } else {
            UI.mostrarNotificacao(result.data.erro || 'Erro ao fazer login', 'erro');
            return false;
        }
    },
    
    /**
     * Realiza registro
     */
    async register(username, email, password) {
        const result = await API.register(username, email, password);
        
        if (result.ok) {
            UI.mostrarNotificacao('Conta criada com sucesso! Faça login.', 'sucesso');
            return true;
        } else {
            UI.mostrarNotificacao(result.data.erro || 'Erro ao registrar', 'erro');
            return false;
        }
    },
    
    /**
     * Realiza logout
     */
    async logout() {
        await API.logout();
        this.currentUser = null;
        this.isAuthenticated = false;
        UI.renderizarAppNaoAutenticada();
        UI.mostrarNotificacao('Logout realizado!', 'sucesso');
    },
    
    /**
     * Retorna o usuário atual
     */
    getUsuarioAtual() {
        return this.currentUser;
    },
    
    /**
     * Verifica se está autenticado
     */
    estaAutenticado() {
        return this.isAuthenticated;
    },
    
    /**
     * Configura event listeners para formulários
     */
    setupEventListeners() {
        // Login
        document.addEventListener('submit', async (e) => {
            if (e.target.id === 'form-login') {
                e.preventDefault();
                const username = document.querySelector('#form-login [name="username"]').value;
                const password = document.querySelector('#form-login [name="password"]').value;
                await this.login(username, password);
            }
        });
        
        // Registro
        document.addEventListener('submit', async (e) => {
            if (e.target.id === 'form-registro') {
                e.preventDefault();
                const username = document.querySelector('#form-registro [name="username"]').value;
                const email = document.querySelector('#form-registro [name="email"]').value;
                const password = document.querySelector('#form-registro [name="password"]').value;
                await this.register(username, email, password);
            }
        });
        
        // Logout
        document.addEventListener('click', async (e) => {
            if (e.target.id === 'btn-logout') {
                e.preventDefault();
                await this.logout();
            }
        });
    }
};
