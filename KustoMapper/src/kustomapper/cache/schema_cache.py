import json
import hashlib
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from kustomapper.models.schema import TableInfo, ColumnInfo

class SchemaCache:
    DEFAULT_CACHE_DIR = Path.home() / '.kustomapper_cache'
    
    def __init__(self, cluster, database, cache_dir=None):
        self._cluster = cluster
        self._database = database
        self._base_dir = Path(cache_dir) if cache_dir else self.DEFAULT_CACHE_DIR
        cluster_hash = hashlib.md5(cluster.encode()).hexdigest()[:12]
        safe_db = ''.join(c if c.isalnum() or c in '-_.' else '_' for c in database)
        self._cache_dir = self._base_dir / cluster_hash / safe_db
    
    def _ensure_dir(self):
        self._cache_dir.mkdir(parents=True, exist_ok=True)
    
    def save_tables(self, tables):
        self._ensure_dir()
        data = {'tables': [t.to_dict() for t in tables], 'cached_at': datetime.utcnow().isoformat()}
        with open(self._cache_dir / 'tables.json', 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_tables(self):
        tf = self._cache_dir / 'tables.json'
        if not tf.exists():
            return None
        try:
            with open(tf, 'r') as f:
                data = json.load(f)
            return [TableInfo.from_dict(t) for t in data.get('tables', [])]
        except:
            return None
    
    def save_schema(self, table_name, columns):
        self._ensure_dir()
        sn = ''.join(c if c.isalnum() or c in '-_.' else '_' for c in table_name)
        data = {'columns': [c.to_dict() for c in columns], 'cached_at': datetime.utcnow().isoformat()}
        with open(self._cache_dir / f'schema_{sn}.json', 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_schema(self, table_name):
        sn = ''.join(c if c.isalnum() or c in '-_.' else '_' for c in table_name)
        sf = self._cache_dir / f'schema_{sn}.json'
        if not sf.exists():
            return None
        try:
            with open(sf, 'r') as f:
                data = json.load(f)
            return [ColumnInfo.from_dict(c) for c in data.get('columns', [])]
        except:
            return None
    
    def invalidate(self):
        if self._cache_dir.exists():
            shutil.rmtree(self._cache_dir)
    
    def is_valid(self):
        return (self._cache_dir / 'tables.json').exists()
