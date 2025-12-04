import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import threading

class JSONDatabase:
    """Sistema de banco de dados usando JSON em vez de SQL"""
    
    def __init__(self, db_folder='instance'):
        self.db_folder = db_folder
        os.makedirs(db_folder, exist_ok=True)
        self.lock = threading.RLock()
        
        # Arquivos de dados
        self.usuarios_file = os.path.join(db_folder, 'usuarios.json')
        self.publicacoes_file = os.path.join(db_folder, 'publicacoes.json')
        self.comentarios_file = os.path.join(db_folder, 'comentarios.json')
        self.respostas_file = os.path.join(db_folder, 'respostas.json')
        self.curtidas_file = os.path.join(db_folder, 'curtidas.json')
        self.seguir_file = os.path.join(db_folder, 'seguir.json')
        self.bloquear_file = os.path.join(db_folder, 'bloquear.json')
        
        # Inicializar arquivos se não existirem
        self._init_files()
        
        self.session = None
    
    def _init_files(self):
        """Inicializa os arquivos JSON se não existirem"""
        for file_path in [
            self.usuarios_file, self.publicacoes_file, self.comentarios_file,
            self.respostas_file, self.curtidas_file, self.seguir_file, self.bloquear_file
        ]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump([], f)
    
    def _read_file(self, file_path: str) -> List[Dict]:
        """Lê dados do arquivo JSON"""
        with self.lock:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
            except (FileNotFoundError, json.JSONDecodeError):
                return []
    
    def _write_file(self, file_path: str, data: List[Dict]):
        """Escreve dados no arquivo JSON"""
        with self.lock:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
    
    def _get_next_id(self, file_path: str) -> int:
        """Gera o próximo ID para um arquivo"""
        data = self._read_file(file_path)
        if not data:
            return 1
        return max(item.get('id', 0) for item in data) + 1
    
    # ============ USUÁRIOS ============
    def save_usuario(self, usuario_dict: Dict) -> Dict:
        """Salva um usuário ou atualiza se já existir"""
        usuarios = self._read_file(self.usuarios_file)
        if 'id' not in usuario_dict:
            usuario_dict['id'] = self._get_next_id(self.usuarios_file)
        
        # Procura se já existe
        idx = next((i for i, u in enumerate(usuarios) if u['id'] == usuario_dict['id']), None)
        if idx is not None:
            usuarios[idx] = usuario_dict
        else:
            usuarios.append(usuario_dict)
        
        self._write_file(self.usuarios_file, usuarios)
        return usuario_dict
    
    def get_usuario_by_id(self, user_id: int) -> Optional[Dict]:
        """Busca usuário por ID"""
        usuarios = self._read_file(self.usuarios_file)
        return next((u for u in usuarios if u['id'] == user_id), None)
    
    def get_usuario_by_username(self, username: str) -> Optional[Dict]:
        """Busca usuário por username"""
        usuarios = self._read_file(self.usuarios_file)
        return next((u for u in usuarios if u.get('username', '').lower() == username.lower()), None)
    
    def get_all_usuarios(self) -> List[Dict]:
        """Retorna todos os usuários"""
        return self._read_file(self.usuarios_file)
    
    # ============ PUBLICAÇÕES ============
    def save_publicacao(self, publicacao_dict: Dict) -> Dict:
        """Salva uma publicação"""
        publicacoes = self._read_file(self.publicacoes_file)
        if 'id' not in publicacao_dict:
            publicacao_dict['id'] = self._get_next_id(self.publicacoes_file)
        
        idx = next((i for i, p in enumerate(publicacoes) if p['id'] == publicacao_dict['id']), None)
        if idx is not None:
            publicacoes[idx] = publicacao_dict
        else:
            publicacoes.append(publicacao_dict)
        
        self._write_file(self.publicacoes_file, publicacoes)
        return publicacao_dict
    
    def get_publicacao_by_id(self, pub_id: int) -> Optional[Dict]:
        """Busca publicação por ID"""
        publicacoes = self._read_file(self.publicacoes_file)
        return next((p for p in publicacoes if p['id'] == pub_id), None)
    
    def get_publicacoes_by_usuario(self, user_id: int) -> List[Dict]:
        """Busca todas as publicações de um usuário"""
        publicacoes = self._read_file(self.publicacoes_file)
        return [p for p in publicacoes if p.get('id_usuario') == user_id]
    
    def get_all_publicacoes(self) -> List[Dict]:
        """Retorna todas as publicações"""
        return self._read_file(self.publicacoes_file)
    
    def delete_publicacao(self, pub_id: int):
        """Deleta uma publicação"""
        publicacoes = self._read_file(self.publicacoes_file)
        publicacoes = [p for p in publicacoes if p['id'] != pub_id]
        self._write_file(self.publicacoes_file, publicacoes)
    
    # ============ COMENTÁRIOS ============
    def save_comentario(self, comentario_dict: Dict) -> Dict:
        """Salva um comentário"""
        comentarios = self._read_file(self.comentarios_file)
        if 'id' not in comentario_dict:
            comentario_dict['id'] = self._get_next_id(self.comentarios_file)
        
        idx = next((i for i, c in enumerate(comentarios) if c['id'] == comentario_dict['id']), None)
        if idx is not None:
            comentarios[idx] = comentario_dict
        else:
            comentarios.append(comentario_dict)
        
        self._write_file(self.comentarios_file, comentarios)
        return comentario_dict
    
    def get_comentario_by_id(self, com_id: int) -> Optional[Dict]:
        """Busca comentário por ID"""
        comentarios = self._read_file(self.comentarios_file)
        return next((c for c in comentarios if c['id'] == com_id), None)
    
    def get_comentarios_by_publicacao(self, pub_id: int) -> List[Dict]:
        """Busca comentários de uma publicação"""
        comentarios = self._read_file(self.comentarios_file)
        return [c for c in comentarios if c.get('id_publicacao') == pub_id]
    
    def delete_comentario(self, com_id: int):
        """Deleta um comentário"""
        comentarios = self._read_file(self.comentarios_file)
        comentarios = [c for c in comentarios if c['id'] != com_id]
        self._write_file(self.comentarios_file, comentarios)
    
    # ============ RESPOSTAS ============
    def save_resposta(self, resposta_dict: Dict) -> Dict:
        """Salva uma resposta"""
        respostas = self._read_file(self.respostas_file)
        if 'id' not in resposta_dict:
            resposta_dict['id'] = self._get_next_id(self.respostas_file)
        
        idx = next((i for i, r in enumerate(respostas) if r['id'] == resposta_dict['id']), None)
        if idx is not None:
            respostas[idx] = resposta_dict
        else:
            respostas.append(resposta_dict)
        
        self._write_file(self.respostas_file, respostas)
        return resposta_dict
    
    def get_resposta_by_id(self, resp_id: int) -> Optional[Dict]:
        """Busca resposta por ID"""
        respostas = self._read_file(self.respostas_file)
        return next((r for r in respostas if r['id'] == resp_id), None)
    
    def get_respostas_by_comentario(self, com_id: int) -> List[Dict]:
        """Busca respostas de um comentário"""
        respostas = self._read_file(self.respostas_file)
        return [r for r in respostas if r.get('id_comentario') == com_id]
    
    def delete_resposta(self, resp_id: int):
        """Deleta uma resposta"""
        respostas = self._read_file(self.respostas_file)
        respostas = [r for r in respostas if r['id'] != resp_id]
        self._write_file(self.respostas_file, respostas)
    
    # ============ CURTIDAS ============
    def save_curtida(self, curtida_dict: Dict) -> Dict:
        """Salva uma curtida"""
        curtidas = self._read_file(self.curtidas_file)
        if 'id' not in curtida_dict:
            curtida_dict['id'] = self._get_next_id(self.curtidas_file)
        
        # Verifica se a curtida já existe para evitar duplicatas
        existe = next((c for c in curtidas if 
                      c.get('id_usuario') == curtida_dict.get('id_usuario') and
                      c.get('id_publicacao') == curtida_dict.get('id_publicacao') and
                      c.get('id_comentario') == curtida_dict.get('id_comentario') and
                      c.get('id_resposta') == curtida_dict.get('id_resposta')), None)
        
        if existe:
            return existe
        
        curtidas.append(curtida_dict)
        self._write_file(self.curtidas_file, curtidas)
        return curtida_dict
    
    def get_curtida(self, user_id: int, pub_id: Optional[int] = None, 
                   com_id: Optional[int] = None, resp_id: Optional[int] = None) -> Optional[Dict]:
        """Busca uma curtida específica"""
        curtidas = self._read_file(self.curtidas_file)
        return next((c for c in curtidas if
                    c.get('id_usuario') == user_id and
                    c.get('id_publicacao') == pub_id and
                    c.get('id_comentario') == com_id and
                    c.get('id_resposta') == resp_id), None)
    
    def get_curtidas_by_publicacao(self, pub_id: int) -> List[Dict]:
        """Busca curtidas de uma publicação"""
        curtidas = self._read_file(self.curtidas_file)
        return [c for c in curtidas if c.get('id_publicacao') == pub_id]
    
    def get_curtidas_by_comentario(self, com_id: int) -> List[Dict]:
        """Busca curtidas de um comentário"""
        curtidas = self._read_file(self.curtidas_file)
        return [c for c in curtidas if c.get('id_comentario') == com_id]
    
    def get_curtidas_by_resposta(self, resp_id: int) -> List[Dict]:
        """Busca curtidas de uma resposta"""
        curtidas = self._read_file(self.curtidas_file)
        return [c for c in curtidas if c.get('id_resposta') == resp_id]
    
    def delete_curtida(self, curtida_id: int):
        """Deleta uma curtida"""
        curtidas = self._read_file(self.curtidas_file)
        curtidas = [c for c in curtidas if c['id'] != curtida_id]
        self._write_file(self.curtidas_file, curtidas)
    
    # ============ RELACIONAMENTOS: SEGUIR ============
    def save_seguir(self, seguir_dict: Dict) -> Dict:
        """Salva um relacionamento de seguimento"""
        seguires = self._read_file(self.seguir_file)
        if 'id' not in seguir_dict:
            seguir_dict['id'] = self._get_next_id(self.seguir_file)
        
        idx = next((i for i, s in enumerate(seguires) if s['id'] == seguir_dict['id']), None)
        if idx is not None:
            seguires[idx] = seguir_dict
        else:
            seguires.append(seguir_dict)
        
        self._write_file(self.seguir_file, seguires)
        return seguir_dict
    
    def get_seguindo(self, user_id: int) -> List[Dict]:
        """Retorna usuários que um usuário está seguindo"""
        seguires = self._read_file(self.seguir_file)
        return [s for s in seguires if s.get('id_seguidor') == user_id]
    
    def get_seguidores(self, user_id: int) -> List[Dict]:
        """Retorna seguidores de um usuário"""
        seguires = self._read_file(self.seguir_file)
        return [s for s in seguires if s.get('id_seguido') == user_id]
    
    def get_seguindo_rel(self, seguidor_id: int, seguido_id: int) -> Optional[Dict]:
        """Busca relacionamento específico de seguimento"""
        seguires = self._read_file(self.seguir_file)
        return next((s for s in seguires if 
                    s.get('id_seguidor') == seguidor_id and 
                    s.get('id_seguido') == seguido_id), None)
    
    def delete_seguir(self, seguidor_id: int, seguido_id: int):
        """Deleta um relacionamento de seguimento"""
        seguires = self._read_file(self.seguir_file)
        seguires = [s for s in seguires if not (
            s.get('id_seguidor') == seguidor_id and s.get('id_seguido') == seguido_id
        )]
        self._write_file(self.seguir_file, seguires)
    
    # ============ RELACIONAMENTOS: BLOQUEAR ============
    def save_bloquear(self, bloquear_dict: Dict) -> Dict:
        """Salva um bloqueio"""
        bloqueios = self._read_file(self.bloquear_file)
        if 'id' not in bloquear_dict:
            bloquear_dict['id'] = self._get_next_id(self.bloquear_file)
        
        idx = next((i for i, b in enumerate(bloqueios) if b['id'] == bloquear_dict['id']), None)
        if idx is not None:
            bloqueios[idx] = bloquear_dict
        else:
            bloqueios.append(bloquear_dict)
        
        self._write_file(self.bloquear_file, bloqueios)
        return bloquear_dict
    
    def get_bloqueados(self, user_id: int) -> List[Dict]:
        """Retorna usuários bloqueados por um usuário"""
        bloqueios = self._read_file(self.bloquear_file)
        return [b for b in bloqueios if b.get('id_bloqueador') == user_id]
    
    def get_bloqueado_por(self, user_id: int) -> List[Dict]:
        """Retorna usuários que bloquearam um usuário"""
        bloqueios = self._read_file(self.bloquear_file)
        return [b for b in bloqueios if b.get('id_bloqueado') == user_id]
    
    def get_bloquear_rel(self, bloqueador_id: int, bloqueado_id: int) -> Optional[Dict]:
        """Busca relacionamento específico de bloqueio"""
        bloqueios = self._read_file(self.bloquear_file)
        return next((b for b in bloqueios if 
                    b.get('id_bloqueador') == bloqueador_id and 
                    b.get('id_bloqueado') == bloqueado_id), None)
    
    def delete_bloquear(self, bloqueador_id: int, bloqueado_id: int):
        """Deleta um bloqueio"""
        bloqueios = self._read_file(self.bloquear_file)
        bloqueios = [b for b in bloqueios if not (
            b.get('id_bloqueador') == bloqueador_id and b.get('id_bloqueado') == bloqueado_id
        )]
        self._write_file(self.bloquear_file, bloqueios)


# Instância global do banco de dados
db = JSONDatabase()