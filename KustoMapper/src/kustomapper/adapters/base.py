from abc import ABC, abstractmethod
from typing import List, Dict, Any
import pandas as pd

from kustomapper.models.schema import TableInfo, ColumnInfo

class DataSourceAdapter(ABC):
    @abstractmethod
    def connect(self, **kwargs) -> bool: pass
    
    @abstractmethod
    def get_tables(self) -> List[TableInfo]: pass
    
    @abstractmethod
    def get_table_schema(self, table_name: str) -> List[ColumnInfo]: pass
    
    @abstractmethod
    def sample_table(self, table_name: str, sample_size: int = 1000) -> pd.DataFrame: pass
    
    @abstractmethod
    def disconnect(self) -> None: pass
    
    @property
    @abstractmethod
    def is_connected(self) -> bool: pass
    
    @property
    @abstractmethod
    def connection_info(self) -> Dict[str, Any]: pass
