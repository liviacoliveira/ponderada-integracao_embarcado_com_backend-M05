import sqlite3
import os
from pathlib import Path
try:
    from . import config
except ImportError:
    import config

DB_FILE = getattr(config, 'DB_FILE', 'dados.db')

def get_db_connection():
    """Retorna uma conexão SQLite configurada com row_factory e suporte a concorrência."""
    conn = sqlite3.connect(DB_FILE, timeout=10)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA busy_timeout=5000') 
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Cria as tabelas se não existirem (executa o schema.sql)."""
    schema_path = Path(__file__).parent / "schema.sql"
    
    with get_db_connection() as conn:
        with open(schema_path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()

def inserir_leitura(temperatura, umidade, pressao=None):
    """Insere uma nova leitura no banco de dados."""
    query = "INSERT INTO leituras (temperatura, umidade, pressao) VALUES (?, ?, ?)"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (temperatura, umidade, pressao))
        conn.commit()
        return cursor.lastrowid

def listar_leituras(limite=50):
    """Retorna as últimas leituras registradas com paginação básica."""
    query = "SELECT * FROM leituras ORDER BY timestamp DESC LIMIT ?"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        rows = cursor.execute(query, (limite,)).fetchall()
        return [dict(row) for row in rows]

def buscar_leitura(id):
    """Busca uma leitura específica pelo ID."""
    query = "SELECT * FROM leituras WHERE id = ?"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        row = cursor.execute(query, (id,)).fetchone()
        return dict(row) if row else None

def atualizar_leitura(id, dados):
    """Atualiza os campos de uma leitura existente."""
    fields = ", ".join([f"{key} = ?" for key in dados.keys()])
    values = list(dados.values())
    values.append(id)
    
    query = f"UPDATE leituras SET {fields} WHERE id = ?"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        return cursor.rowcount > 0

def deletar_leitura(id):
    """Remove uma leitura do banco de dados pelo ID."""
    query = "DELETE FROM leituras WHERE id = ?"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (id,))
        conn.commit()
        return cursor.rowcount > 0

def obter_estatisticas():
    """Calcula estatísticas básicas das leituras (média, min, máx)."""
    query = """
    SELECT 
        AVG(temperatura) as avg_temp, MIN(temperatura) as min_temp, MAX(temperatura) as max_temp,
        AVG(umidade) as avg_umid, MIN(umidade) as min_umid, MAX(umidade) as max_umid,
        AVG(pressao) as avg_pres, MIN(pressao) as min_pres, MAX(pressao) as max_pres,
        COUNT(*) as total
    FROM leituras
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        row = cursor.execute(query).fetchone()
        stats = dict(row) if row else None
        
        if stats and stats.get('total', 0) == 0:
            return None
            
        return stats
