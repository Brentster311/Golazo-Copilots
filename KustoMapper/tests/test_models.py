import pytest
from kustomapper.models.schema import TableInfo, ColumnInfo

class TestColumnInfo:
    def test_creation(self):
        col = ColumnInfo(name="Id", data_type="int", nullable=False)
        assert col.name == "Id"
        assert col.data_type == "int"
        assert col.nullable is False

    def test_default_nullable(self):
        col = ColumnInfo(name="Name", data_type="string")
        assert col.nullable is True

    def test_to_dict(self):
        col = ColumnInfo(name="Id", data_type="int", nullable=False)
        d = col.to_dict()
        assert d == {"name": "Id", "data_type": "int", "nullable": False}

    def test_from_dict(self):
        d = {"name": "Id", "data_type": "int", "nullable": False}
        col = ColumnInfo.from_dict(d)
        assert col.name == "Id"

class TestTableInfo:
    def test_creation(self):
        table = TableInfo(name="MyTable", row_count=1000)
        assert table.name == "MyTable"
        assert table.row_count == 1000
        assert table.columns == []

    def test_default_row_count(self):
        table = TableInfo(name="T")
        assert table.row_count == 0

    def test_with_columns(self):
        cols = [ColumnInfo(name="Id", data_type="int")]
        table = TableInfo(name="T", columns=cols)
        assert len(table.columns) == 1

    def test_to_dict(self):
        table = TableInfo(name="T", row_count=10)
        d = table.to_dict()
        assert d["name"] == "T"
        assert d["row_count"] == 10

    def test_from_dict(self):
        d = {"name": "T", "row_count": 10, "columns": []}
        table = TableInfo.from_dict(d)
        assert table.name == "T"
