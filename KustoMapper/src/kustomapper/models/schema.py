from dataclasses import dataclass, field
from enum import Enum
from typing import List


class RelationshipType(Enum):
    EXACT_MATCH = "exact_match"
    ID_SUFFIX = "id_suffix"


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


@dataclass
class RelationshipInfo:
    source_table: str
    source_column: str
    target_table: str
    target_column: str
    relationship_type: RelationshipType = RelationshipType.EXACT_MATCH
    
    def to_dict(self):
        return {
            "source_table": self.source_table,
            "source_column": self.source_column,
            "target_table": self.target_table,
            "target_column": self.target_column,
            "relationship_type": self.relationship_type.value
        }
    
    @classmethod
    def from_dict(cls, d):
        return cls(
            source_table=d["source_table"],
            source_column=d["source_column"],
            target_table=d["target_table"],
            target_column=d["target_column"],
            relationship_type=RelationshipType(d.get("relationship_type", "exact_match"))
        )
