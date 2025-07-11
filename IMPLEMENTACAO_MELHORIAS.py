# Implementações Práticas das Melhorias Propostas
# Sistema Multi-Agente Mangaba.AI

import redis
import hashlib
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from celery import Celery
from flask_socketio import SocketIO, emit
import sqlite3
from functools import wraps
import logging

# =============================================================================
# MELHORIA 1: SISTEMA DE CACHE INTELIGENTE
# =============================================================================

class IntelligentCache:
    """
    Sistema de cache inteligente para otimizar chamadas da API Gemini
    Reduz latência e custos através de cache baseado em hash de prompts
    """
    
    def __init__(self, cache_type='redis', redis_url='redis://localhost:6379'):
        self.cache_type = cache_type
        
        if cache_type == 'redis':
            self.cache = redis.Redis.from_url(redis_url, decode_responses=True)
        else:
            self.cache = self._init_sqlite_cache()
        
        # TTL configurável por tipo de análise
        self.ttl_config = {
            'strategic_planning': 3600,    # 1 hora
            'competitive_analysis': 1800,  # 30 min
            'data_analysis': 1800,         # 30 min
            'sales_analysis': 900,         # 15 min
            'creative': 600,               # 10 min
            'general': 1200                # 20 min
        }
    
    def _init_sqlite_cache(self):
        """Inicializa cache SQLite como fallback"""
        conn = sqlite3.connect('cache.db', check_same_thread=False)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT,
                expires_at TIMESTAMP
            )
        ''')
        conn.commit()
        return conn
    
    def _generate_cache_key(self, goal: str, context: str, agent_type: str) -> str:
        """Gera chave única baseada no hash do conteúdo"""
        content = f"{goal}|{context}|{agent_type}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, goal: str, context: str, agent_type: str) -> Optional[Dict]:
        """Recupera resultado do cache se existir e válido"""
        cache_key = self._generate_cache_key(goal, context, agent_type)
        
        try:
            if self.cache_type == 'redis':
                cached_data = self.cache.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
            else:
                cursor = self.cache.execute(
                    'SELECT value FROM cache WHERE key = ? AND expires_at > ?',
                    (cache_key, datetime.now())
                )
                result = cursor.fetchone()
                if result:
                    return json.loads(result[0])
        except Exception as e:
            logging.error(f"Cache get error: {e}")
        
        return None
    
    def set(self, goal: str, context: str, agent_type: str, result: Dict) -> bool:
        """Armazena resultado no cache com TTL apropriado"""
        cache_key = self._generate_cache_key(goal, context, agent_type)
        ttl = self.ttl_config.get(agent_type, self.ttl_config['general'])
        
        try:
            if self.cache_type == 'redis':
                self.cache.setex(cache_key, ttl, json.dumps(result))
            else:
                expires_at = datetime.now() + timedelta(seconds=ttl)
                self.cache.execute(
                    'INSERT OR REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, ?)',
                    (cache_key, json.dumps(result), expires_at)
                )
                self.cache.commit()
            return True
        except Exception as e:
            logging.error(f"Cache set error: {e}")
            return False
    
    def clear_expired(self):
        """Remove entradas expiradas do cache"""
        if self.cache_type == 'sqlite':
            self.cache.execute('DELETE FROM cache WHERE expires_at <= ?', (datetime.now(),))
            self.cache.commit()

# =============================================================================
# MELHORIA 2: SISTEMA DE PROCESSAMENTO ASSÍNCRONO
# =============================================================================

# Configuração do Celery
celery_app = Celery('mangaba_ai')
celery_app.conf.update(
    broker_url='redis://localhost:6379',
    result_backend='redis://localhost:6379',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@dataclass
class AnalysisTask:
    """Estrutura para tarefas de análise"""
    task_id: str
    goal: str
    context: str
    agent_types: List[str]
    user_id: str
    status: str = 'pending'
    progress: int = 0
    result: Optional[Dict] = None
    error: Optional[str] = None
    created_at: datetime = None
    completed_at: Optional[datetime] = None

class AsyncAnalysisManager:
    """
    Gerenciador de análises assíncronas com WebSocket para updates em tempo real
    """
    
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.active_tasks: Dict[str, AnalysisTask] = {}
    
    def start_analysis(self, goal: str, context: str, agent_types: List[str], user_id: str) -> str:
        """Inicia análise assíncrona e retorna task_id"""
        task_id = f"analysis_{int(time.time())}_{user_id}"
        
        task = AnalysisTask(
            task_id=task_id,
            goal=goal,
            context=context,
            agent_types=agent_types,
            user_id=user_id,
            created_at=datetime.now()
        )
        
        self.active_tasks[task_id] = task
        
        # Inicia processamento assíncrono
        process_multi_agent_analysis.delay(task_id, goal, context, agent_types, user_id)
        
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Retorna status atual da tarefa"""
        task = self.active_tasks.get(task_id)
        if not task:
            return None
        
        return {
            'task_id': task.task_id,
            'status': task.status,
            'progress': task.progress,
            'result': task.result,
            'error': task.error,
            'created_at': task.created_at.isoformat() if task.created_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None
        }
    
    def update_task_progress(self, task_id: str, progress: int, status: str = None):
        """Atualiza progresso da tarefa e notifica via WebSocket"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.progress = progress
            if status:
                task.status = status
            
            # Notifica cliente via WebSocket
            self.socketio.emit('task_progress', {
                'task_id': task_id,
                'progress': progress,
                'status': status or task.status
            }, room=task.user_id)
    
    def complete_task(self, task_id: str, result: Dict = None, error: str = None):
        """Marca tarefa como completa"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = 'completed' if result else 'failed'
            task.result = result
            task.error = error
            task.completed_at = datetime.now()
            task.progress = 100
            
            # Notifica conclusão via WebSocket
            self.socketio.emit('task_completed', {
                'task_id': task_id,
                'status': task.status,
                'result': result,
                'error': error
            }, room=task.user_id)

@celery_app.task(bind=True)
def process_multi_agent_analysis(self, task_id: str, goal: str, context: str, agent_types: List[str], user_id: str):
    """
    Processa análise multi-agente de forma assíncrona
    """
    try:
        # Simula processamento com updates de progresso
        total_agents = len(agent_types)
        
        for i, agent_type in enumerate(agent_types):
            # Atualiza progresso
            progress = int((i / total_agents) * 100)
            async_manager.update_task_progress(task_id, progress, f'processing_{agent_type}')
            
            # Simula processamento do agente
            time.sleep(2)  # Substituir por chamada real da API
            
        # Resultado final
        result = {
            'goal': goal,
            'analysis': 'Análise completa multi-agente',
            'agents_used': agent_types,
            'timestamp': datetime.now().isoformat()
        }
        
        async_manager.complete_task(task_id, result)
        
    except Exception as e:
        async_manager.complete_task(task_id, error=str(e))
        raise

# =============================================================================
# MELHORIA 3: DASHBOARD DE ANALYTICS E MÉTRICAS
# =============================================================================

class AnalyticsTracker:
    """
    Sistema de tracking de métricas e analytics
    """
    
    def __init__(self):
        self.db = sqlite3.connect('analytics.db', check_same_thread=False)
        self._init_tables()
    
    def _init_tables(self):
        """Inicializa tabelas de analytics"""
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS usage_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                agent_type TEXT,
                goal_type TEXT,
                execution_time REAL,
                api_calls INTEGER,
                tokens_used INTEGER,
                success BOOLEAN,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS quality_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id TEXT,
                completeness_score REAL,
                accuracy_score REAL,
                relevance_score REAL,
                actionability_score REAL,
                overall_score REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id TEXT,
                user_id TEXT,
                rating INTEGER,
                feedback_text TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        self.db.commit()
    
    def track_usage(self, user_id: str, agent_type: str, goal_type: str, 
                   execution_time: float, api_calls: int, tokens_used: int, success: bool):
        """Registra métricas de uso"""
        self.db.execute('''
            INSERT INTO usage_metrics 
            (user_id, agent_type, goal_type, execution_time, api_calls, tokens_used, success)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, agent_type, goal_type, execution_time, api_calls, tokens_used, success))
        self.db.commit()
    
    def track_quality(self, analysis_id: str, scores: Dict[str, float]):
        """Registra scores de qualidade"""
        self.db.execute('''
            INSERT INTO quality_scores 
            (analysis_id, completeness_score, accuracy_score, relevance_score, actionability_score, overall_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (analysis_id, scores.get('completeness', 0), scores.get('accuracy', 0),
              scores.get('relevance', 0), scores.get('actionability', 0), scores.get('overall', 0)))
        self.db.commit()
    
    def get_usage_stats(self, days: int = 30) -> Dict:
        """Retorna estatísticas de uso dos últimos N dias"""
        cursor = self.db.execute('''
            SELECT 
                agent_type,
                COUNT(*) as total_uses,
                AVG(execution_time) as avg_execution_time,
                SUM(api_calls) as total_api_calls,
                SUM(tokens_used) as total_tokens,
                AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate
            FROM usage_metrics 
            WHERE timestamp >= datetime('now', '-{} days')
            GROUP BY agent_type
        '''.format(days))
        
        stats = {}
        for row in cursor.fetchall():
            stats[row[0]] = {
                'total_uses': row[1],
                'avg_execution_time': row[2],
                'total_api_calls': row[3],
                'total_tokens': row[4],
                'success_rate': row[5]
            }
        
        return stats

# =============================================================================
# MELHORIA 5: SISTEMA DE AUTENTICAÇÃO E AUTORIZAÇÃO
# =============================================================================

class UserManager:
    """
    Sistema de gestão de usuários com autenticação JWT
    """
    
    def __init__(self):
        self.db = sqlite3.connect('users.db', check_same_thread=False)
        self._init_tables()
    
    def _init_tables(self):
        """Inicializa tabelas de usuários"""
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                plan TEXT DEFAULT 'free',
                api_calls_used INTEGER DEFAULT 0,
                api_calls_limit INTEGER DEFAULT 100,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                key_hash TEXT UNIQUE,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
        ''')
        self.db.commit()
    
    def create_user(self, email: str, password: str, plan: str = 'free') -> Dict:
        """Cria novo usuário"""
        import bcrypt
        
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        try:
            cursor = self.db.execute(
                'INSERT INTO users (email, password_hash, plan) VALUES (?, ?, ?)',
                (email, password_hash, plan)
            )
            self.db.commit()
            
            return {
                'user_id': cursor.lastrowid,
                'email': email,
                'plan': plan,
                'success': True
            }
        except sqlite3.IntegrityError:
            return {'success': False, 'error': 'Email already exists'}
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Autentica usuário e retorna dados"""
        import bcrypt
        
        cursor = self.db.execute(
            'SELECT id, email, password_hash, plan, api_calls_used, api_calls_limit FROM users WHERE email = ?',
            (email,)
        )
        user = cursor.fetchone()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user[2]):
            # Atualiza último login
            self.db.execute(
                'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
                (user[0],)
            )
            self.db.commit()
            
            return {
                'user_id': user[0],
                'email': user[1],
                'plan': user[3],
                'api_calls_used': user[4],
                'api_calls_limit': user[5]
            }
        
        return None
    
    def check_api_limit(self, user_id: int) -> bool:
        """Verifica se usuário ainda tem calls disponíveis"""
        cursor = self.db.execute(
            'SELECT api_calls_used, api_calls_limit FROM users WHERE id = ?',
            (user_id,)
        )
        user = cursor.fetchone()
        
        return user and user[0] < user[1]
    
    def increment_api_usage(self, user_id: int):
        """Incrementa contador de uso da API"""
        self.db.execute(
            'UPDATE users SET api_calls_used = api_calls_used + 1 WHERE id = ?',
            (user_id,)
        )
        self.db.commit()

def require_api_limit(f):
    """Decorator para verificar limite de API"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        
        if not user_manager.check_api_limit(user_id):
            return jsonify({
                'error': 'API limit exceeded',
                'message': 'Upgrade your plan to continue using the service'
            }), 429
        
        # Incrementa uso após verificação
        user_manager.increment_api_usage(user_id)
        
        return f(*args, **kwargs)
    
    return decorated_function

# =============================================================================
# MELHORIA 6: API RESTFUL COMPLETA
# =============================================================================

class MangabaAPI:
    """
    API RESTful completa para o sistema Mangaba.AI
    """
    
    def __init__(self, app: Flask):
        self.app = app
        self.setup_routes()
    
    def setup_routes(self):
        """Configura todas as rotas da API"""
        
        @self.app.route('/api/v1/auth/login', methods=['POST'])
        def login():
            """Endpoint de login"""
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            
            user = user_manager.authenticate_user(email, password)
            if user:
                access_token = create_access_token(identity=user['user_id'])
                return jsonify({
                    'access_token': access_token,
                    'user': user
                })
            
            return jsonify({'error': 'Invalid credentials'}), 401
        
        @self.app.route('/api/v1/analysis', methods=['POST'])
        @jwt_required()
        @require_api_limit
        def create_analysis():
            """Cria nova análise"""
            data = request.get_json()
            goal = data.get('goal')
            context = data.get('context', '')
            agent_types = data.get('agent_types', [])
            async_mode = data.get('async', False)
            
            user_id = get_jwt_identity()
            
            if async_mode:
                task_id = async_manager.start_analysis(goal, context, agent_types, str(user_id))
                return jsonify({
                    'task_id': task_id,
                    'status': 'processing',
                    'message': 'Analysis started. Use /api/v1/analysis/{task_id}/status to check progress.'
                })
            else:
                # Processamento síncrono (implementação existente)
                result = process_synchronous_analysis(goal, context, agent_types)
                return jsonify(result)
        
        @self.app.route('/api/v1/analysis/<task_id>/status', methods=['GET'])
        @jwt_required()
        def get_analysis_status(task_id):
            """Retorna status de análise assíncrona"""
            status = async_manager.get_task_status(task_id)
            if status:
                return jsonify(status)
            return jsonify({'error': 'Task not found'}), 404
        
        @self.app.route('/api/v1/templates', methods=['GET'])
        @jwt_required()
        def get_templates():
            """Lista templates disponíveis"""
            templates = template_manager.get_all_templates()
            return jsonify(templates)
        
        @self.app.route('/api/v1/analytics/usage', methods=['GET'])
        @jwt_required()
        def get_usage_analytics():
            """Retorna analytics de uso"""
            days = request.args.get('days', 30, type=int)
            stats = analytics_tracker.get_usage_stats(days)
            return jsonify(stats)

# =============================================================================
# INICIALIZAÇÃO DOS SISTEMAS
# =============================================================================

# Instâncias globais
cache_system = IntelligentCache()
analytics_tracker = AnalyticsTracker()
user_manager = UserManager()

# Configuração Flask
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Mudar para produção
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Gerenciador assíncrono
async_manager = AsyncAnalysisManager(socketio)

# API RESTful
api = MangabaAPI(app)

def process_synchronous_analysis(goal: str, context: str, agent_types: List[str]) -> Dict:
    """
    Processa análise de forma síncrona (implementação simplificada)
    """
    start_time = time.time()
    
    # Verifica cache primeiro
    for agent_type in agent_types:
        cached_result = cache_system.get(goal, context, agent_type)
        if cached_result:
            return cached_result
    
    # Simula processamento
    result = {
        'goal': goal,
        'context': context,
        'agents_used': agent_types,
        'analysis': 'Análise completa baseada nos agentes especificados',
        'timestamp': datetime.now().isoformat(),
        'execution_time': time.time() - start_time
    }
    
    # Armazena no cache
    for agent_type in agent_types:
        cache_system.set(goal, context, agent_type, result)
    
    return result

if __name__ == '__main__':
    # Inicia aplicação com WebSocket
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)