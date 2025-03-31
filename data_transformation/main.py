import json
import yaml
import logging
from typing import List, Dict, Any, Union
from pydantic import BaseModel, ValidationError
from datetime import date, datetime
from pathlib import Path
import csv
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Configuration
class ConfigLoader:
    def __init__(self, yaml_file: Path):
        with yaml_file.open("r") as file:
            self.config = yaml.safe_load(file)

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

# Utility Functions
def clean_string(value: str) -> str:
    return value.strip() if isinstance(value, str) else str(value).strip()

def parse_date(date_str: str, date_formats: List[str]) -> date:
    date_str = clean_string(date_str)
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    logger.warning(f"Invalid date: {date_str}. Using today's date.")
    return date.today()

def parse_amount(amount_str: str) -> float:
    amount_str = re.sub(r'[^0-9.]', '', str(amount_str))
    try:
        return float(amount_str)
    except ValueError:
        logger.warning(f"Invalid amount: {amount_str}. Using 0.")
        return 0.0

# Pydantic Models
class Transaction(BaseModel):
    transaction_id: int
    customer_name: str
    purchase_date: date
    total_amount: float
    status: str

class ItemDetail(BaseModel):
    details_id: int
    transaction_id: int | str
    item: str
    quantity: int
    price: float

# Processing JSON to CSV
def parse_json_to_csv(json_data: List[Dict[str, Any]], transaction_file: Path, details_file: Path,
                     config: ConfigLoader):
    transactions = []
    item_details = []
    details_id_counter = 1

    for entry in json_data:
        try:
            transaction = Transaction(
                transaction_id=int(entry.get(config.get('id_fields')[0], 0)),
                customer_name=clean_string(entry.get(config.get('name_fields')[0], '')),
                purchase_date=parse_date(entry.get(config.get('date_fields')[0], ''), config.get('date_formats', [])),
                total_amount=parse_amount(entry.get(config.get('amount_fields')[0], 0)),
                status=entry.get(config.get('status_fields')[0], 'Unknown')
            )
            transactions.append(transaction)

            for item in entry.get('items', []):
                item_details.append(ItemDetail(
                    details_id=details_id_counter,
                    transaction_id=int(entry.get(config.get('id_fields')[0], 0)),
                    item=clean_string(item.get('item', 'Unknown')),
                    quantity=int(item.get('quantity', 1)),
                    price=parse_amount(item.get('price', 0))
                ))
                details_id_counter += 1
        except ValidationError as e:
            logger.error(f"Error validating transaction: {entry}. Error: {e}")

    # Save CSV
    with transaction_file.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(Transaction.model_fields.keys())
        for trans in transactions:
            writer.writerow(trans.model_dump().values())

    with details_file.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(ItemDetail.model_fields.keys())
        for detail in item_details:
            writer.writerow(detail.model_dump().values())

    logger.info(f"Processed {len(transactions)} transactions and {len(item_details)} item details")

# Execute Pipeline
if __name__ == "__main__":
    config = ConfigLoader(Path("data_transformation/config.yml"))

    input_file = Path(config.get("files")["input"])
    transaction_output = Path(config.get("files")["transaction_output"])
    details_output = Path(config.get("files")["details_output"])

    with input_file.open("r", encoding="utf-8") as file:
        json_data = json.load(file)

    parse_json_to_csv(json_data, transaction_output, details_output, config)