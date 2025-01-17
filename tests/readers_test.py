import pytest

from testing.testifycompat import (
    assert_equal,
    assert_raises,
    mock,
)
from staticconf import config, readers, proxy, errors, testing


class TestBuildReader:

    @pytest.fixture(autouse=True)
    def namespace(self):
        self.namespace = mock.create_autospec(config.ConfigNamespace)

    def test_read_config_success(self):
        config_key = 'the_key'
        value = readers._read_config(config_key, self.namespace, None)
        self.namespace.get.assert_called_with(config_key, default=None)
        assert_equal(value, self.namespace.get.return_value)

    def test_read_config_failed(self):
        self.namespace.get.return_value = proxy.UndefToken
        assert_raises(
                errors.ConfigurationError,
                readers._read_config,
                'some_key',
                self.namespace,
                None)

    @mock.patch('staticconf.readers.config.get_namespace', autospec=True)
    def test_build_reader(self, mock_get_namespace):
        config_key, validator, self.namespace = 'the_key', mock.Mock(), 'the_name'
        reader = readers.build_reader(validator, self.namespace)
        value = reader(config_key)
        mock_get_namespace.assert_called_with(self.namespace)
        validator.assert_called_with(
            mock_get_namespace.return_value.get.return_value)
        assert_equal(value, validator.return_value)


class TestNamespaceReader:

    config = {
        'one':     '1',
        'three':   '3.0',
        'options': ['seven', 'stars']
    }

    @pytest.yield_fixture(autouse=True)
    def patch_config(self):
        self.namespace = 'the_name'
        with testing.MockConfiguration(self.config, namespace=self.namespace):
            yield

    def test_readers(self):
        read_conf = readers.NamespaceReaders(self.namespace)
        assert_equal(read_conf.read_int('one'), 1)
        assert_equal(read_conf.read_float('three'), 3.0)
        assert_equal(
            read_conf.read_list_of_string('options'), ['seven', 'stars'])
