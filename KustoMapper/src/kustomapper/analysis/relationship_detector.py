"""Relationship detection between Kusto tables."""
from typing import List
from kustomapper.models.schema import TableInfo, ColumnInfo, RelationshipInfo, RelationshipType

TYPE_COMPAT = [{"string","str"},{"int","int32","long","int64"},{"guid"},{"datetime","date"},{"real","double","float"},{"bool","boolean"}]

IGNORED_COLUMNS = {
    "timestamp", "time", "datetime", "date", "created", "modified", "updated",
    "createddate", "modifieddate", "updateddate", "createdat", "updatedat",
    "starttime", "endtime", "eventtime", "ingesttime", "ingestiontime",
    "rowid", "rowkey", "partitionkey", "etag", "version",
    "name", "type", "kind", "status", "state", "value", "count", "size",
    "description", "message", "details", "data", "properties", "tags",
    "region", "location", "source", "target", "level", "severity"
}

def are_types_compatible(a,b):
    a,b=a.lower(),b.lower()
    if a==b: return True
    for g in TYPE_COMPAT:
        if a in g and b in g: return True
    return False

def is_ignored_column(name):
    return name.lower() in IGNORED_COLUMNS

class RelationshipDetector:
    def __init__(self,tables): self._tables=tables
    def detect_all(self):
        if not self._tables: return []
        rels,seen=[],set()
        for ta in self._tables:
            for tb in self._tables:
                for ca in ta.columns:
                    for cb in tb.columns:
                        if is_ignored_column(ca.name) or is_ignored_column(cb.name): continue
                        if not are_types_compatible(ca.data_type,cb.data_type): continue
                        r=self._check(ta,ca,tb,cb)
                        if r:
                            k=self._key(r)
                            if k not in seen: seen.add(k); rels.append(r)
        return rels
    def detect_for_table(self,name):
        n=name.lower()
        return [r for r in self.detect_all() if r.source_table.lower()==n or r.target_table.lower()==n]
    def _check(self,ta,ca,tb,cb):
        if ta.name==tb.name and ca.name==cb.name: return None
        if ta.name!=tb.name and ca.name.lower()==cb.name.lower():
            return RelationshipInfo(ta.name,ca.name,tb.name,cb.name,RelationshipType.EXACT_MATCH)
        if ca.name.lower()=="id" and cb.name.lower()==(ta.name+"id").lower():
            return RelationshipInfo(ta.name,ca.name,tb.name,cb.name,RelationshipType.ID_SUFFIX)
        return None
    def _key(self,r):
        if r.relationship_type==RelationshipType.EXACT_MATCH:
            t=sorted([(r.source_table.lower(),r.source_column.lower()),(r.target_table.lower(),r.target_column.lower())])
            return(t[0][0],t[0][1],t[1][0],t[1][1])
        return(r.source_table.lower(),r.source_column.lower(),r.target_table.lower(),r.target_column.lower())
