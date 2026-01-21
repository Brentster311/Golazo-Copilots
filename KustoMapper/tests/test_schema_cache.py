import pytest
import tempfile
import shutil
from kustomapper.cache.schema_cache import SchemaCache
from kustomapper.models.schema import TableInfo, ColumnInfo


class TestSchemaCache:
    @pytest.fixture
    def temp_cache_dir(self):
        d = tempfile.mkdtemp()
        yield d
        shutil.rmtree(d, ignore_errors=True)

    @pytest.fixture
    def cache(self, temp_cache_dir):
        return SchemaCache(cluster='https://test.kusto.net', database='TestDB', cache_dir=temp_cache_dir)

    def test_save_and_load_tables(self, cache):
        tables = [TableInfo(name='Table1', row_count=100), TableInfo(name='Table2', row_count=200)]
        cache.save_tables(tables)
        loaded = cache.load_tables()
        assert loaded is not None
        assert len(loaded) == 2
        assert loaded[0].name == 'Table1'

    def test_load_tables_not_cached(self, cache):
        loaded = cache.load_tables()
        assert loaded is None

    def test_save_and_load_schema(self, cache):
        columns = [ColumnInfo(name='Id', data_type='int'), ColumnInfo(name='Name', data_type='string')]
        cache.save_schema('MyTable', columns)
        loaded = cache.load_schema('MyTable')
        assert loaded is not None
        assert len(loaded) == 2
        assert loaded[0].name == 'Id'

    def test_invalidate(self, cache):
        tables = [TableInfo(name='T', row_count=1)]
        cache.save_tables(tables)
        assert cache.is_valid()
        cache.invalidate()
        assert not cache.is_valid()

    def test_is_valid(self, cache):
        assert not cache.is_valid()
        cache.save_tables([TableInfo(name='T')])
        assert cache.is_valid()
