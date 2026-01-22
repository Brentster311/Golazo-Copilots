import pytest
from kustomapper.models.schema import TableInfo, ColumnInfo, RelationshipInfo, RelationshipType
from kustomapper.analysis.relationship_detector import RelationshipDetector

class TestRelationshipInfo:
    def test_creation(self):
        rel = RelationshipInfo("Users","Id","Orders","UserId",RelationshipType.ID_SUFFIX)
        assert rel.source_table == "Users"
    def test_to_dict(self):
        rel = RelationshipInfo("Users","Id","Orders","UserId")
        d = rel.to_dict()
        assert d["source_table"] == "Users"
    def test_from_dict(self):
        d = {"source_table":"Users","source_column":"Id","target_table":"Orders","target_column":"UserId","relationship_type":"id_suffix"}
        rel = RelationshipInfo.from_dict(d)
        assert rel.relationship_type == RelationshipType.ID_SUFFIX

class TestExactNameMatching:
    def test_detect_exact_match(self):
        tables = [TableInfo("TableA",columns=[ColumnInfo("UserId","string")]),TableInfo("TableB",columns=[ColumnInfo("UserId","string")])]
        det = RelationshipDetector(tables)
        rels = det.detect_all()
        assert len(rels) == 1
        assert rels[0].relationship_type == RelationshipType.EXACT_MATCH
    def test_no_match_different_names(self):
        tables = [TableInfo("TableA",columns=[ColumnInfo("UserId","string")]),TableInfo("TableB",columns=[ColumnInfo("CustomerId","string")])]
        det = RelationshipDetector(tables)
        assert len(det.detect_all()) == 0

class TestIdSuffixPattern:
    def test_detect_id_suffix(self):
        tables = [TableInfo("User",columns=[ColumnInfo("Id","string")]),TableInfo("Orders",columns=[ColumnInfo("UserId","string")])]
        det = RelationshipDetector(tables)
        rels = det.detect_all()
        assert len(rels) == 1
        assert rels[0].relationship_type == RelationshipType.ID_SUFFIX
    def test_id_suffix_case_insensitive(self):
        tables = [TableInfo("user",columns=[ColumnInfo("id","string")]),TableInfo("orders",columns=[ColumnInfo("userid","string")])]
        det = RelationshipDetector(tables)
        assert len(det.detect_all()) == 1

class TestRelationshipMetadata:
    def test_all_fields_present(self):
        tables = [TableInfo("TableA",columns=[ColumnInfo("Id","string")]),TableInfo("TableB",columns=[ColumnInfo("Id","string")])]
        det = RelationshipDetector(tables)
        rels = det.detect_all()
        assert len(rels) == 1
        rel = rels[0]
        assert hasattr(rel, 'source_table')
        assert hasattr(rel, 'relationship_type')

class TestQueryMethods:
    def test_detect_for_specific_table(self):
        tables = [TableInfo("User",columns=[ColumnInfo("Id","string")]),TableInfo("Orders",columns=[ColumnInfo("UserId","string")]),TableInfo("Product",columns=[ColumnInfo("Id","string")])]
        det = RelationshipDetector(tables)
        rels = det.detect_for_table("Orders")
        for rel in rels:
            assert rel.source_table == "Orders" or rel.target_table == "Orders"
    def test_detect_all_returns_all(self):
        tables = [TableInfo("User",columns=[ColumnInfo("Id","string")]),TableInfo("Orders",columns=[ColumnInfo("UserId","string"),ColumnInfo("ProductId","string")]),TableInfo("Product",columns=[ColumnInfo("Id","string")])]
        det = RelationshipDetector(tables)
        assert len(det.detect_all()) >= 2

class TestTypeCompatibility:
    def test_compatible_string(self):
        tables = [TableInfo("TableA",columns=[ColumnInfo("Id","string")]),TableInfo("TableB",columns=[ColumnInfo("Id","string")])]
        det = RelationshipDetector(tables)
        assert len(det.detect_all()) == 1
    def test_compatible_int_long(self):
        tables = [TableInfo("TableA",columns=[ColumnInfo("Id","int")]),TableInfo("TableB",columns=[ColumnInfo("Id","long")])]
        det = RelationshipDetector(tables)
        assert len(det.detect_all()) == 1
    def test_incompatible_string_int(self):
        tables = [TableInfo("TableA",columns=[ColumnInfo("Id","string")]),TableInfo("TableB",columns=[ColumnInfo("Id","int")])]
        det = RelationshipDetector(tables)
        assert len(det.detect_all()) == 0

class TestEdgeCases:
    def test_empty_tables(self):
        det = RelationshipDetector([])
        assert det.detect_all() == []
    def test_no_duplicates(self):
        tables = [TableInfo("TableA",columns=[ColumnInfo("SharedId","string")]),TableInfo("TableB",columns=[ColumnInfo("SharedId","string")])]
        det = RelationshipDetector(tables)
        assert len(det.detect_all()) == 1
    def test_self_referential_excluded(self):
        tables = [TableInfo("Employees",columns=[ColumnInfo("Id","string"),ColumnInfo("ManagerId","string")])]
        det = RelationshipDetector(tables)
        rels = det.detect_all()
        for rel in rels:
            if rel.source_table == rel.target_table:
                assert rel.source_column != rel.target_column
