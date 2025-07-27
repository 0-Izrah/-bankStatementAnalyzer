"""
Bank statement parser package.
"""

from .base import BaseStatementParser
from .access_bank import AccessBankParser
from .zenith_bank import ZenithBankParser
from .gtbank import GTBankParser
from .uba import UBAParser

BANK_PARSERS = {
    'Access Bank': AccessBankParser,
    'Zenith Bank': ZenithBankParser,
    'GTBank': GTBankParser,
    'UBA': UBAParser,
}