from dataclasses import dataclass, field
from typing import List

@dataclass
class ColumnInfo:
    name: str
    data_type: str
    nullable: bool = True
    
    def to_dict(self):
        return {"name": self.name, "data_type": self.data_type, "nullable": self.nullable}
    
    @classmethod
    def from_dict(cls, d):
        return cls(name=d["name"], data_type=d["data_type"], nullable=d.get("nullable", True))

@dataclass
class TableInfo:
    name: str
    row_count: int = 0
    columns: List[ColumnInfo] = field(default_factory=list)
    
    def to_dict(self):
        return {"name": self.name, "row_count": self.row_count, "columns": [c.to_dict() for c in self.columns]}
    
    @classmethod
    def from_dict(cls, d):
        cols = [ColumnInfo.from_dict(c) for c in d.get("columns", [])]
        return cls(name=d["name"], row_count=d.get("row_count", 0), columns=cols)
