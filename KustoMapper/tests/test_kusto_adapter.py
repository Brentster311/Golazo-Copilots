import pytest
from unittest.mock import Mock, MagicMock, patch
import pandas as pd
from kustomapper.adapters.kusto_adapter import KustoAdapter
from kustomapper.adapters.base import DataSourceAdapter
from kustomapper.models.schema import TableInfo, ColumnInfo


class TestKustoAdapterInterface:
    def test_inherits_from_base(self):
        adapter = KustoAdapter()
        assert isinstance(adapter, DataSourceAdapter)

    def test_has_required_methods(self):
        adapter = KustoAdapter()
        assert hasattr(adapter, 'connect')
        assert hasattr(adapter, 'get_tables')
        assert hasattr(adapter, 'get_table_schema')
        assert hasattr(adapter, 'sample_table')
        assert hasattr(adapter, 'disconnect')
        assert hasattr(adapter, 'is_connected')
        assert hasattr(adapter, 'connection_info')


class TestKustoAdapterConnect:
    @pytest.fixture
    def mock_handler(self):
        with patch('kustomapper.adapters.kusto_adapter.KustoHandler') as mock:
            handler = MagicMock()
            mock.return_value = handler
            yield handler

    def test_connect_success(self, mock_handler):
        mock_handler.GetDataFrameFromKustoQuery.return_value = pd.DataFrame({'Table': ['T1']})
        adapter = KustoAdapter()
        result = adapter.connect(cluster='https://test.kusto.net', database='TestDB')
        assert result is True
        assert adapter.is_connected is True
        assert adapter.connection_info['cluster'] == 'https://test.kusto.net'

    def test_connect_missing_params(self):
        adapter = KustoAdapter()
        with pytest.raises(ConnectionError) as exc:
            adapter.connect(cluster='https://test.kusto.net')
        assert 'database' in str(exc.value).lower()

    def test_connect_auth_failure(self, mock_handler):
        mock_handler.GetDataFrameFromKustoQuery.side_effect = Exception('Authentication failed')
        adapter = KustoAdapter()
        with pytest.raises(ConnectionError) as exc:
            adapter.connect(cluster='https://test.kusto.net', database='db')
        assert 'az login' in str(exc.value).lower()


class TestKustoAdapterGetTables:
    @pytest.fixture
    def connected_adapter(self):
        with patch('kustomapper.adapters.kusto_adapter.KustoHandler') as mock:
            handler = MagicMock()
            mock.return_value = handler
            handler.GetDataFrameFromKustoQuery.return_value = pd.DataFrame({'TableName': ['T1', 'T2']})
            adapter = KustoAdapter()
            adapter.connect(cluster='https://test.kusto.net', database='TestDB')
            yield adapter, handler

    def test_get_tables_success(self, connected_adapter):
        adapter, handler = connected_adapter
        handler.GetDataFrameFromKustoQuery.return_value = pd.DataFrame({'TableName': ['T1', 'T2']})
        tables = adapter.get_tables()
        assert len(tables) == 2
        assert all(isinstance(t, TableInfo) for t in tables)

    def test_get_tables_not_connected(self):
        adapter = KustoAdapter()
        with pytest.raises(RuntimeError) as exc:
            adapter.get_tables()
        assert 'connect' in str(exc.value).lower()


class TestKustoAdapterDisconnect:
    def test_disconnect(self):
        with patch('kustomapper.adapters.kusto_adapter.KustoHandler'):
            adapter = KustoAdapter()
            adapter._connected = True
            adapter._cluster = 'test'
            adapter.disconnect()
            assert adapter.is_connected is False
            assert adapter._cluster is None
