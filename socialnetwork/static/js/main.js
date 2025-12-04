/**
 * Arquivo Principal - Inicializa a SPA
 */

document.addEventListener('DOMContentLoaded', async () => {
    // Inicializar módulos
    Auth.init();
    UI.init();
    
    // Configurar navegação por URL hash
    window.addEventListener('hashchange', () => {
        const hash = window.location.hash;
        
        if (hash.startsWith('#feed')) {
            UI.mudarPagina('feed');
            Feed.carregarPublicacoes();
        } else if (hash.startsWith('#perfil/')) {
            UI.mudarPagina('perfil');
            const username = hash.split('/')[1];
            Perfil.carregarPerfil(username);
        } else if (hash.startsWith('#topics')) {
            UI.mudarPagina('topics');
        } else {
            // Redirecionar para feed se autenticado
            if (Auth.estaAutenticado()) {
                window.location.hash = '#feed';
            }
        }
    });
    
    // Disparar navegação inicial
    const hash = window.location.hash;
    if (hash) {
        window.dispatchEvent(new Event('hashchange'));
    } else if (Auth.estaAutenticado()) {
        window.location.hash = '#feed';
    }
});

// Exportar módulos globalmente
window.API = API;
window.Auth = Auth;
window.UI = UI;
window.Feed = Feed;
window.Perfil = Perfil;
