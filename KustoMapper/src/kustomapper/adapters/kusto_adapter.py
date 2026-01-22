from typing import List, Dict, Any
import pandas as pd
from kustomapper.adapters.base import DataSourceAdapter
from kustomapper.models.schema import TableInfo, ColumnInfo

try:
    from azure.identity import AzureCliCredential
except ImportError:
    AzureCliCredential = None

try:
    from accia.datacollection import KustoHandler
except ImportError:
    KustoHandler = None

class KustoAdapter(DataSourceAdapter):
    def __init__(self):
        self._handler = None
        self._cluster = None
        self._database = None
        self._connected = False
    
    def connect(self, **kwargs):
        cluster = kwargs.get('cluster')
        database = kwargs.get('database')
        if not cluster or not database:
            raise ConnectionError('Both cluster and database are required')
        if KustoHandler is None:
            raise ConnectionError('accia-datacollection package not installed')
        try:
            self._handler = KustoHandler(AlternateAADCredentialsList=[AzureCliCredential()], UseDefaultCredentials=False)
            self._handler.GetDataFrameFromKustoQuery(Cluster=cluster, Database=database, Query='.show tables | take 1', CacheExpiryInMin=0)
            self._cluster = cluster
            self._database = database
            self._connected = True
            return True
        except Exception as e:
            self._connected = False
            msg = str(e).lower()
            if 'auth' in msg or 'credential' in msg or 'token' in msg:
                raise ConnectionError(f'Authentication failed. Run az login. Details: {e}')
            elif 'database' in msg and 'not' in msg:
                raise ConnectionError(f'Database not found: {e}')
            raise ConnectionError(f'Connection failed: {e}')
    
    def get_tables(self):
        if not self._connected:
            raise RuntimeError('Not connected')
        df = self._handler.GetDataFrameFromKustoQuery(Cluster=self._cluster, Database=self._database, Query='.show tables', CacheExpiryInMin=5)
        if df is None or df.empty:
            return []
        return [TableInfo(name=row.get('TableName', row.get('Name', '')), row_count=0) for _, row in df.iterrows() if row.get('TableName', row.get('Name'))]
    
    def get_table_schema(self, table_name):
        if not self._connected:
            raise RuntimeError('Not connected')
        try:
            df = self._handler.GetDataFrameFromKustoQuery(Cluster=self._cluster, Database=self._database, Query=f'{table_name} | getschema', CacheExpiryInMin=5)
            if df is None or df.empty:
                return []
            return [ColumnInfo(name=row.get('ColumnName', ''), data_type=row.get('ColumnType', row.get('DataType', 'unknown'))) for _, row in df.iterrows()]
        except Exception as e:
            if 'not found' in str(e).lower():
                raise ValueError(f'Table not found: {table_name}')
            raise RuntimeError(f'Failed to get schema: {e}')
    
    def sample_table(self, table_name, sample_size=1000):
        if not self._connected:
            raise RuntimeError('Not connected')
        return self._handler.GetDataFrameFromKustoQuery(Cluster=self._cluster, Database=self._database, Query=f'{table_name} | take {sample_size}', CacheExpiryInMin=5)
    
    def disconnect(self):
        self._connected = False
        self._handler = None
        self._cluster = None
        self._database = None
    
    @property
    def is_connected(self):
        return self._connected
    
    @property
    def connection_info(self):
        return {'cluster': self._cluster, 'database': self._database, 'connected': self._connected}
