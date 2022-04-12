import os
from .base import BaseConfig
configuration = os.environ.get('SETTINGS_CONFIGURATION', 'develop')


Config = BaseConfig

if configuration == 'develop':
    from .dev import DevConfig
    Config = DevConfig

if configuration == 'prod':
    from .prod import ProdConfig
    Config = ProdConfig

if configuration == 'test':
    from .test import TestConfig
    Config = TestConfig

