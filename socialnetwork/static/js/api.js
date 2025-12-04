/**
 * Módulo API - Gerencia todas as requisições HTTP
 * Padrão: Retorna Promise com {ok: boolean, data: any, error?: string}
 */

const API = {
    
    // Usar URL relativa para evitar problemas com CORS
    baseURL: '',
    
    /**
     * Faz uma requisição HTTP genérica
     * @param {string} method - GET, POST, PUT, DELETE
     * @param {string} endpoint - /login, /publicacoes, etc
     * @param {object} data - Dados a enviar
     * @returns {Promise}
     */
    async request(method, endpoint, data = null) {
        try {
            const options = {
                method,
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                }
            };
            
            if (data) {
                options.body = JSON.stringify(data);
            }
            
            const response = await fetch(`${this.baseURL}${endpoint}`, options);
            
            // Verificar se é JSON
            const contentType = response.headers.get('content-type');
            let result = {};
            
            if (contentType && contentType.includes('application/json')) {
                result = await response.json();
            } else {
                // Se não é JSON (ex: HTML de erro), retornar o texto
                result = { erro: 'Resposta não é JSON' };
            }
            
            return {
                ok: response.ok,
                status: response.status,
                data: result
            };
        } catch (error) {
            console.error(`Erro na requisição ${method} ${endpoint}:`, error);
            return {
                ok: false,
                status: 0,
                error: error.message,
                data: { erro: error.message }
            };
        }
    },
    
    /**
     * POST genérico
     */
    post(endpoint, data) {
        return this.request('POST', endpoint, data);
    },
    
    /**
     * GET genérico
     */
    get(endpoint) {
        return this.request('GET', endpoint);
    },
    
    /**
     * PUT genérico
     */
    put(endpoint, data) {
        return this.request('PUT', endpoint, data);
    },
    
    /**
     * DELETE genérico
     */
    delete(endpoint) {
        return this.request('DELETE', endpoint);
    },
    
    // ==================== AUTH ====================
    
    async login(username, password) {
        return this.post('/login', { username, password });
    },
    
    async register(username, email, password) {
        return this.post('/registrar', { username, email, password });
    },
    
    async logout() {
        return this.post('/logout', {});
    },
    
    // ==================== PUBLICAÇÕES ====================
    
    async criarPublicacao(texto) {
        return this.post('/adicionar_publicacao', { texto });
    },
    
    async obterPublicacoes() {
        return this.get('/publicacoes_json');
    },
    
    async obterPublicacoesPerfil(username) {
        return this.get(`/perfil/${username}/publicacoes_json`);
    },
    
    async deletarPublicacao(publicacao_id) {
        return this.delete(`/deletar/publicacao/${publicacao_id}`);
    },
    
    // ==================== COMENTÁRIOS ====================
    
    async adicionarComentario(publicacao_id, texto) {
        return this.post(`/comentar/publicacao/${publicacao_id}`, { texto });
    },
    
    async obterComentarios(publicacao_id) {
        return this.get(`/comentarios/${publicacao_id}`);
    },
    
    async deletarComentario(comentario_id) {
        return this.delete(`/deletar/comentario/${comentario_id}`);
    },
    
    // ==================== RESPOSTAS ====================
    
    async adicionarResposta(comentario_id, texto) {
        return this.post(`/responder/comentario/${comentario_id}`, { texto });
    },
    
    async adicionarRespostaEmResposta(resposta_id, texto) {
        return this.post(`/responder/resposta/${resposta_id}`, { texto });
    },
    
    async deletarResposta(resposta_id) {
        return this.delete(`/deletar/resposta/${resposta_id}`);
    },
    
    // ==================== CURTIDAS ====================
    
    async curtirPublicacao(publicacao_id) {
        return this.post(`/curtir/publicacao/${publicacao_id}`, {});
    },
    
    async descurtirPublicacao(publicacao_id) {
        return this.post(`/descurtir/publicacao/${publicacao_id}`, {});
    },
    
    async curtirComentario(comentario_id) {
        return this.post(`/curtir/comentario/${comentario_id}`, {});
    },
    
    async descurtirComentario(comentario_id) {
        return this.post(`/descurtir/comentario/${comentario_id}`, {});
    },
    
    async curtirResposta(resposta_id) {
        return this.post(`/curtir/resposta/${resposta_id}`, {});
    },
    
    async descurtirResposta(resposta_id) {
        return this.post(`/descurtir/resposta/${resposta_id}`, {});
    },
    
    // ==================== SEGUIR/BLOQUEAR ====================
    
    async seguirUsuario(username) {
        return this.post(`/seguir_ajax/${username}`, {});
    },
    
    async deixarDeSeguir(username) {
        return this.post(`/deixar_de_seguir_ajax/${username}`, {});
    },
    
    async bloquearUsuario(username) {
        return this.post(`/bloquear_ajax/${username}`, {});
    },
    
    async desbloquearUsuario(username) {
        return this.post(`/desbloquear_ajax/${username}`, {});
    },
    
    // ==================== PERFIL ====================
    
    async obterPerfil(username) {
        return this.get(`/perfil_json/${username}`);
    },
    
    async obterUsuarioAtual() {
        return this.get('/usuario_atual_json');
    }
};

// Exportar para uso em outros módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = API;
}
