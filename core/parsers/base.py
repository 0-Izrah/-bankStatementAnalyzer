"""
Base parser class for bank statements.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any
import pdfplumber
import re

class BaseStatementParser(ABC):
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.transactions = []

    def parse(self) -> List[Dict[str, Any]]:
        """Parse the PDF and return a list of transactions."""
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                self.parse_page(text)
        return self.transactions

    @abstractmethod
    def parse_page(self, text: str) -> None:
        """Parse a single page of text and extract transactions."""
        pass

    def clean_amount(self, amount_str: str) -> Decimal:
        """Convert amount string to Decimal."""
        # Remove currency symbols and commas
        cleaned = re.sub(r'[₦,]', '', amount_str.strip())
        return Decimal(cleaned)

    def parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object."""
        try:
            # Try common date formats
            formats = [
                '%d/%m/%Y',
                '%d-%m-%Y',
                '%Y-%m-%d',
                '%d/%m/%y',
                '%d-%b-%Y',
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(date_str.strip(), fmt)
                except ValueError:
                    continue
            raise ValueError(f"Could not parse date: {date_str}")
        except Exception as e:
            raise ValueError(f"Error parsing date {date_str}: {str(e)}")

    def categorize_transaction(self, description: str) -> str:
        """Categorize transaction based on description."""
        description = description.lower()
        
        categories = {
            'food': [
                'restaurant', 'cafe', 'food', 'grocery', 'supermarket',
                'burger', 'pizza', 'chicken', 'market'
            ],
            'transport': [
                'uber', 'bolt', 'taxi', 'transport', 'fuel', 'petrol',
                'bus', 'train', 'flight', 'airline'
            ],
            'utilities': [
                'electricity', 'water', 'gas', 'dstv', 'gotv', 'internet',
                'wifi', 'phone', 'mobile', 'utility'
            ],
            'entertainment': [
                'cinema', 'movie', 'theatre', 'netflix', 'spotify',
                'game', 'betting', 'entertainment'
            ],
            'shopping': [
                'mall', 'store', 'shop', 'retail', 'clothing', 'fashion',
                'electronics', 'gadget', 'amazon'
            ],
            'health': [
                'hospital', 'clinic', 'pharmacy', 'medical', 'doctor',
                'dental', 'health', 'drug', 'medicine'
            ],
            'education': [
                'school', 'college', 'university', 'tuition', 'course',
                'training', 'education', 'book'
            ]
        }

        for category, keywords in categories.items():
            if any(keyword in description for keyword in keywords):
                return category
        return 'other'