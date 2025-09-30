#!/usr/bin/env python3
"""
Persistence System
Sistema di persistenza per job, risultati e stato del Lambda Visualizer.
Risolve la criticità 3.2: Persistenza dei Dati e dei Job.
"""

import sqlite3
import json
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import pickle
import threading
import logging
from dataclasses import dataclass, asdict
from enum import Enum

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobStatus(Enum):
    """Stati possibili per un job."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class JobPriority(Enum):
    """Priorità dei job."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

@dataclass
class JobRecord:
    """Record di un job nel database."""
    job_id: str
    job_type: str
    status: JobStatus
    priority: JobPriority
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    input_data: Dict[str, Any] = None
    result_data: Dict[str, Any] = None
    error_message: Optional[str] = None
    progress: float = 0.0
    estimated_duration: Optional[float] = None
    actual_duration: Optional[float] = None
    worker_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = None

class PersistenceManager:
    """Gestore principale della persistenza."""
    
    def __init__(self, db_path: str = "./lambda_visualizer.db"):
        self.db_path = Path(db_path)
        self.connection_pool = {}
        self.lock = threading.RLock()
        self._initialize_database()
        
    def _get_connection(self) -> sqlite3.Connection:
        """Ottiene una connessione thread-safe al database."""
        thread_id = threading.get_ident()
        
        if thread_id not in self.connection_pool:
            conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            self.connection_pool[thread_id] = conn
        
        return self.connection_pool[thread_id]
    
    def _initialize_database(self):
        """Inizializza il database con le tabelle necessarie."""
        
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Jobs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    job_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    input_data TEXT,  -- JSON
                    result_data TEXT, -- JSON
                    error_message TEXT,
                    progress REAL DEFAULT 0.0,
                    estimated_duration REAL,
                    actual_duration REAL,
                    worker_id TEXT,
                    retry_count INTEGER DEFAULT 0,
                    max_retries INTEGER DEFAULT 3,
                    metadata TEXT     -- JSON
                )
            ''')
            
            # Results table (for large results)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS results (
                    result_id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    result_type TEXT NOT NULL,
                    data_blob BLOB,
                    file_path TEXT,
                    created_at TIMESTAMP NOT NULL,
                    size_bytes INTEGER,
                    checksum TEXT,
                    FOREIGN KEY (job_id) REFERENCES jobs (job_id)
                )
            ''')
            
            # System state table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_state (
                    key TEXT PRIMARY KEY,
                    value TEXT,  -- JSON
                    updated_at TIMESTAMP NOT NULL
                )
            ''')
            
            # Performance metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    metric_id TEXT PRIMARY KEY,
                    job_id TEXT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    metadata TEXT,  -- JSON
                    FOREIGN KEY (job_id) REFERENCES jobs (job_id)
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs (status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_jobs_priority ON jobs (priority)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs (created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_results_job_id ON results (job_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_job_id ON performance_metrics (job_id)')
            
            conn.commit()
            logger.info("✅ Database initialized successfully")

class JobManager:
    """Gestore dei job con persistenza."""
    
    def __init__(self, persistence_manager: PersistenceManager):
        self.pm = persistence_manager
        self.active_jobs = {}  # In-memory cache for active jobs
        
    def create_job(self, job_type: str, input_data: Dict[str, Any], 
                   priority: JobPriority = JobPriority.NORMAL,
                   estimated_duration: Optional[float] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """Crea un nuovo job e lo salva nel database."""
        
        job_id = str(uuid.uuid4())
        
        job_record = JobRecord(
            job_id=job_id,
            job_type=job_type,
            status=JobStatus.PENDING,
            priority=priority,
            created_at=datetime.now(),
            input_data=input_data,
            estimated_duration=estimated_duration,
            metadata=metadata or {}
        )
        
        self._save_job(job_record)
        logger.info(f"✅ Job created: {job_id} ({job_type})")
        
        return job_id
    
    def get_job(self, job_id: str) -> Optional[JobRecord]:
        """Recupera un job dal database."""
        
        with self.pm.lock:
            conn = self.pm._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM jobs WHERE job_id = ?', (job_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_job_record(row)
            
            return None
    
    def update_job_status(self, job_id: str, status: JobStatus, 
                         progress: Optional[float] = None,
                         error_message: Optional[str] = None,
                         worker_id: Optional[str] = None):
        """Aggiorna lo stato di un job."""
        
        with self.pm.lock:
            conn = self.pm._get_connection()
            cursor = conn.cursor()
            
            update_fields = ['status = ?']
            params = [status.value]
            
            if progress is not None:
                update_fields.append('progress = ?')
                params.append(progress)
            
            if error_message is not None:
                update_fields.append('error_message = ?')
                params.append(error_message)
            
            if worker_id is not None:
                update_fields.append('worker_id = ?')
                params.append(worker_id)
            
            # Update timestamps based on status
            if status == JobStatus.RUNNING and not self._job_has_started(job_id):
                update_fields.append('started_at = ?')
                params.append(datetime.now())
            
            if status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                update_fields.append('completed_at = ?')
                params.append(datetime.now())
                
                # Calculate actual duration
                job = self.get_job(job_id)
                if job and job.started_at:
                    duration = (datetime.now() - job.started_at).total_seconds()
                    update_fields.append('actual_duration = ?')
                    params.append(duration)
            
            params.append(job_id)
            
            query = f"UPDATE jobs SET {', '.join(update_fields)} WHERE job_id = ?"
            cursor.execute(query, params)
            conn.commit()
            
            logger.info(f"📊 Job {job_id} status updated to {status.value}")
    
    def save_job_result(self, job_id: str, result_data: Dict[str, Any], 
                       large_data: Optional[bytes] = None,
                       file_path: Optional[str] = None):
        """Salva il risultato di un job."""
        
        with self.pm.lock:
            conn = self.pm._get_connection()
            cursor = conn.cursor()
            
            # Update job with result
            cursor.execute(
                'UPDATE jobs SET result_data = ? WHERE job_id = ?',
                (json.dumps(result_data), job_id)
            )
            
            # Save large data separately if provided
            if large_data or file_path:
                result_id = str(uuid.uuid4())
                
                cursor.execute('''
                    INSERT INTO results (result_id, job_id, result_type, data_blob, 
                                       file_path, created_at, size_bytes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    result_id,
                    job_id,
                    result_data.get('type', 'unknown'),
                    large_data,
                    file_path,
                    datetime.now(),
                    len(large_data) if large_data else 0
                ))
            
            conn.commit()
            logger.info(f"💾 Result saved for job {job_id}")
    
    def get_pending_jobs(self, limit: int = 10) -> List[JobRecord]:
        """Recupera job in attesa, ordinati per priorità e data di creazione."""
        
        with self.pm.lock:
            conn = self.pm._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM jobs 
                WHERE status = ? 
                ORDER BY priority DESC, created_at ASC 
                LIMIT ?
            ''', (JobStatus.PENDING.value, limit))
            
            return [self._row_to_job_record(row) for row in cursor.fetchall()]
    
    def get_jobs_by_status(self, status: JobStatus, limit: int = 100) -> List[JobRecord]:
        """Recupera job per stato."""
        
        with self.pm.lock:
            conn = self.pm._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM jobs 
                WHERE status = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (status.value, limit))
            
            return [self._row_to_job_record(row) for row in cursor.fetchall()]
    
    def cleanup_old_jobs(self, days_old: int = 30):
        """Rimuove job vecchi dal database."""
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        with self.pm.lock:
            conn = self.pm._get_connection()
            cursor = conn.cursor()
            
            # Delete old completed/failed jobs
            cursor.execute('''
                DELETE FROM jobs 
                WHERE status IN (?, ?, ?) AND completed_at < ?
            ''', (JobStatus.COMPLETED.value, JobStatus.FAILED.value, 
                  JobStatus.CANCELLED.value, cutoff_date))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            logger.info(f"🧹 Cleaned up {deleted_count} old jobs")
    
    def get_job_statistics(self) -> Dict[str, Any]:
        """Ottiene statistiche sui job."""
        
        with self.pm.lock:
            conn = self.pm._get_connection()
            cursor = conn.cursor()
            
            # Count by status
            cursor.execute('''
                SELECT status, COUNT(*) as count 
                FROM jobs 
                GROUP BY status
            ''')
            status_counts = {row['status']: row['count'] for row in cursor.fetchall()}
            
            # Average duration by job type
            cursor.execute('''
                SELECT job_type, AVG(actual_duration) as avg_duration, COUNT(*) as count
                FROM jobs 
                WHERE actual_duration IS NOT NULL 
                GROUP BY job_type
            ''')
            duration_stats = {
                row['job_type']: {
                    'avg_duration': row['avg_duration'],
                    'count': row['count']
                }
                for row in cursor.fetchall()
            }
            
            # Recent activity (last 24 hours)
            yesterday = datetime.now() - timedelta(hours=24)
            cursor.execute('''
                SELECT COUNT(*) as recent_jobs 
                FROM jobs 
                WHERE created_at > ?
            ''', (yesterday,))
            recent_jobs = cursor.fetchone()['recent_jobs']
            
            return {
                'status_counts': status_counts,
                'duration_stats': duration_stats,
                'recent_jobs_24h': recent_jobs,
                'total_jobs': sum(status_counts.values())
            }
    
    def _save_job(self, job_record: JobRecord):
        """Salva un job record nel database."""
        
        with self.pm.lock:
            conn = self.pm._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO jobs (
                    job_id, job_type, status, priority, created_at, started_at, 
                    completed_at, input_data, result_data, error_message, progress,
                    estimated_duration, actual_duration, worker_id, retry_count,
                    max_retries, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_record.job_id,
                job_record.job_type,
                job_record.status.value,
                job_record.priority.value,
                job_record.created_at,
                job_record.started_at,
                job_record.completed_at,
                json.dumps(job_record.input_data) if job_record.input_data else None,
                json.dumps(job_record.result_data) if job_record.result_data else None,
                job_record.error_message,
                job_record.progress,
                job_record.estimated_duration,
                job_record.actual_duration,
                job_record.worker_id,
                job_record.retry_count,
                job_record.max_retries,
                json.dumps(job_record.metadata) if job_record.metadata else None
            ))
            
            conn.commit()
    
    def _row_to_job_record(self, row: sqlite3.Row) -> JobRecord:
        """Converte una riga del database in JobRecord."""
        
        return JobRecord(
            job_id=row['job_id'],
            job_type=row['job_type'],
            status=JobStatus(row['status']),
            priority=JobPriority(row['priority']),
            created_at=datetime.fromisoformat(row['created_at']),
            started_at=datetime.fromisoformat(row['started_at']) if row['started_at'] else None,
            completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None,
            input_data=json.loads(row['input_data']) if row['input_data'] else None,
            result_data=json.loads(row['result_data']) if row['result_data'] else None,
            error_message=row['error_message'],
            progress=row['progress'],
            estimated_duration=row['estimated_duration'],
            actual_duration=row['actual_duration'],
            worker_id=row['worker_id'],
            retry_count=row['retry_count'],
            max_retries=row['max_retries'],
            metadata=json.loads(row['metadata']) if row['metadata'] else None
        )
    
    def _job_has_started(self, job_id: str) -> bool:
        """Verifica se un job è già stato avviato."""
        
        with self.pm.lock:
            conn = self.pm._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT started_at FROM jobs WHERE job_id = ?', (job_id,))
            row = cursor.fetchone()
            
            return row and row['started_at'] is not None


class SystemStateManager:
    """Gestore dello stato del sistema."""
    
    def __init__(self, persistence_manager: PersistenceManager):
        self.pm = persistence_manager
    
    def save_state(self, key: str, value: Any):
        """Salva uno stato del sistema."""
        
        with self.pm.lock:
            conn = self.pm._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO system_state (key, value, updated_at)
                VALUES (?, ?, ?)
            ''', (key, json.dumps(value), datetime.now()))
            
            conn.commit()
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Recupera uno stato del sistema."""
        
        with self.pm.lock:
            conn = self.pm._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT value FROM system_state WHERE key = ?', (key,))
            row = cursor.fetchone()
            
            if row:
                return json.loads(row['value'])
            
            return default
    
    def get_all_states(self) -> Dict[str, Any]:
        """Recupera tutti gli stati del sistema."""
        
        with self.pm.lock:
            conn = self.pm._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT key, value FROM system_state')
            
            return {
                row['key']: json.loads(row['value'])
                for row in cursor.fetchall()
            }


class PerformanceTracker:
    """Tracker delle performance con persistenza."""
    
    def __init__(self, persistence_manager: PersistenceManager):
        self.pm = persistence_manager
    
    def record_metric(self, metric_name: str, value: float, 
                     job_id: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None):
        """Registra una metrica di performance."""
        
        metric_id = str(uuid.uuid4())
        
        with self.pm.lock:
            conn = self.pm._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_metrics 
                (metric_id, job_id, metric_name, metric_value, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                metric_id,
                job_id,
                metric_name,
                value,
                datetime.now(),
                json.dumps(metadata) if metadata else None
            ))
            
            conn.commit()
    
    def get_metrics(self, metric_name: str, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Recupera metriche per nome."""
        
        since = datetime.now() - timedelta(hours=hours_back)
        
        with self.pm.lock:
            conn = self.pm._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM performance_metrics 
                WHERE metric_name = ? AND timestamp > ?
                ORDER BY timestamp DESC
            ''', (metric_name, since))
            
            return [
                {
                    'metric_id': row['metric_id'],
                    'job_id': row['job_id'],
                    'value': row['metric_value'],
                    'timestamp': row['timestamp'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else None
                }
                for row in cursor.fetchall()
            ]


# Test and demonstration
def test_persistence_system():
    """Testa il sistema di persistenza."""
    
    print("🧪 Testing Persistence System")
    print("=" * 50)
    
    # Initialize system
    pm = PersistenceManager("./test_lambda_visualizer.db")
    jm = JobManager(pm)
    ssm = SystemStateManager(pm)
    pt = PerformanceTracker(pm)
    
    # Test job creation and management
    print("\n1. Testing Job Management...")
    
    job_id = jm.create_job(
        job_type="lambda_analysis",
        input_data={"expression": "λx.x", "complexity": 1},
        priority=JobPriority.HIGH,
        estimated_duration=5.0
    )
    
    print(f"   Created job: {job_id}")
    
    # Update job status
    jm.update_job_status(job_id, JobStatus.RUNNING, progress=0.5)
    jm.update_job_status(job_id, JobStatus.COMPLETED, progress=1.0)
    
    # Save result
    jm.save_job_result(job_id, {"result": "identity_function", "complexity": 1})
    
    # Test job retrieval
    job = jm.get_job(job_id)
    print(f"   Retrieved job status: {job.status.value}")
    
    # Test system state
    print("\n2. Testing System State...")
    
    ssm.save_state("engine_config", {"gpu_enabled": True, "max_workers": 4})
    config = ssm.get_state("engine_config")
    print(f"   Saved and retrieved config: {config}")
    
    # Test performance tracking
    print("\n3. Testing Performance Tracking...")
    
    pt.record_metric("processing_time", 2.5, job_id, {"operation": "analysis"})
    pt.record_metric("memory_usage", 128.5, job_id, {"unit": "MB"})
    
    metrics = pt.get_metrics("processing_time")
    print(f"   Recorded {len(metrics)} performance metrics")
    
    # Test statistics
    print("\n4. Testing Statistics...")
    
    stats = jm.get_job_statistics()
    print(f"   Job statistics: {stats}")
    
    print("\n🎉 Persistence system tests completed!")


if __name__ == "__main__":
    test_persistence_system()
