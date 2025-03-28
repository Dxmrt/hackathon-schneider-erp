import json
import yaml
import logging
from typing import List, Dict, Any, Optional, ClassVar
from pydantic import BaseModel, ValidationError
from datetime import date, datetime
from pathlib import Path
import csv
import re

#Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



#Cargar Configuración

class ConfigLoader:
    def __init__(self, yaml_file: Path):
        with yaml_file.open("r") as file:
            self.config = yaml.safe_load(file)

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)


#Funciones Utilitarias

def clean_string(value: str) -> str:
    return value.strip() if isinstance(value, str) else str(value).strip()


def parse_date(date_str: str, date_formats: List[str]) -> date:
    date_str = clean_string(date_str)
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    logger.warning(f"Fecha inválida: {date_str}. Usando fecha actual.")
    return date.today()


def parse_amount(amount_str: str) -> float:
    amount_str = re.sub(r'[^0-9.]', '', str(amount_str))
    try:
        return float(amount_str)
    except ValueError:
        logger.warning(f"Monto inválido: {amount_str}. Usando 0.")
        return 0.0



#Modelos Pydantic

class Transaction(BaseModel):
    transaction_id: str
    customer_name: str
    purchase_date: date
    total_amount: float
    status: str


class ItemDetail(BaseModel):
    details_id: int
    transaction_id: str
    item: str
    quantity: int
    price: float


# Procesamiento de JSON a CSV

def parse_json_to_csv(json_data: List[Dict[str, Any]], transaction_file: Path, details_file: Path,
                      config: ConfigLoader):
    transactions = []
    item_details = []
    details_id_counter = 1

    for entry in json_data:
        try:
            transaction = Transaction(
                transaction_id=str(entry.get(config.get('id_fields')[0], '')),
                customer_name=clean_string(entry.get(config.get('name_fields')[0], '')),
                purchase_date=parse_date(entry.get(config.get('date_fields')[0], ''), config.get('date_formats', [])),
                total_amount=parse_amount(entry.get(config.get('amount_fields')[0], 0)),
                status=entry.get(config.get('status_fields')[0], 'Unknown')
            )
            transactions.append(transaction)

            for item in entry.get('items', []):
                item_details.append(ItemDetail(
                    details_id=details_id_counter,
                    transaction_id=transaction.transaction_id,
                    item=clean_string(item.get('item', 'Unknown')),
                    quantity=int(item.get('quantity', 1)),
                    price=parse_amount(item.get('price', 0))
                ))
                details_id_counter += 1
        except ValidationError as e:
            logger.error(f"Error validando transacción: {entry}. Error: {e}")

    #Guardar CSV
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

    logger.info(f"Procesadas {len(transactions)} transacciones y {len(item_details)} detalles de items")



#Ejecutar Pipeline

if __name__ == "__main__":
    config = ConfigLoader(Path("data_transformation/config.yml"))

    input_file = Path(config.get("files")["input"])
    transaction_output = Path(config.get("files")["transaction_output"])
    details_output = Path(config.get("files")["details_output"])

    with input_file.open("r", encoding="utf-8") as file:
        json_data = json.load(file)

    parse_json_to_csv(json_data, transaction_output, details_output, config)
