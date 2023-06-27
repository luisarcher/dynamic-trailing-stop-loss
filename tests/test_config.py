# -*- coding: utf-8 -*-

from dtsl.config import Config

import unittest


class ConfigTestSuite(unittest.TestCase):
    """Config test cases."""

    def test_kv(self):
        config = Config()
        api_id = config.get_config_value("telegram_api").get("api_id")
        assert api_id == "api_id_example"


if __name__ == '__main__':
    unittest.main()
