"""
Parser for Access Bank statements.
"""
from .base import BaseStatementParser
import re
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any

class AccessBankParser(BaseStatementParser):
    def parse_page(self, text: str) -> None:
        """Parse Access Bank statement page."""
        # Access Bank transaction pattern
        pattern = r'(\d{2}-[A-Za-z]{3}-\d{2})\s+(.*?)\s+([\d,]+\.\d{2})\s+([\d,]+\.\d{2})'
        
        for line in text.split('\n'):
            match = re.search(pattern, line)
            if match:
                date_str, description, debit_str, credit_str = match.groups()
                
                try:
                    date = self.parse_date(date_str)
                    amount = Decimal('0')
                    
                    # Determine if it's a debit or credit
                    if debit_str.strip() != '0.00':
                        amount = -self.clean_amount(debit_str)
                    else:
                        amount = self.clean_amount(credit_str)

                    category = self.categorize_transaction(description)
                    
                    transaction = {
                        'date': date,
                        'description': description.strip(),
                        'amount': amount,
                        'category': category,
                        'balance': self.clean_amount(credit_str)
                    }
                    
                    self.transactions.append(transaction)
                except (ValueError, Exception) as e:
                    print(f"Error parsing line: {line}. Error: {str(e)}")
                    continue