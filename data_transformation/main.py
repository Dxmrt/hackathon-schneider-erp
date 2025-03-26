import json
import yaml
import logging
from typing import List, Dict, Any, Optional, ClassVar
from pydantic import BaseModel
from datetime import date
from pathlib import Path
import time

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------------------
#     ConfigLoader Class
# ------------------------------


class ConfigLoader:
    """Loads and stores configuration from a YAML file."""

    def __init__(self, yaml_file: Path):
        with yaml_file.open("r") as file:
            self.config = yaml.safe_load(file)

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from the config."""
        return self.config.get(key, default)


# ------------------------------
#        Pydantic Models
# ------------------------------


class Transaction(BaseModel):
    config: ClassVar[ConfigLoader] = None

    transaction_id: int
    customer_name: Optional[str]
    purchase_date: date
    total_amount: float
    status: str

    @classmethod
    def set_config(cls, config: ConfigLoader):
        cls.config = config

    # Implement Class atributes if needed


class ItemDetail(BaseModel):
    details_id: int
    transaction_id: int
    item: str
    quantity: int
    price: float

    # Implement Class atributes if needed


def parse_json_to_csv(
    json_data: List[Dict[str, Any]],
    transaction_file: Path,
    details_file: Path,
    config: ClassVar[ConfigLoader],
):
    pass  # To implement


def process_single_file(filename: Path, transaction_file: Path, details_file: Path):
    with filename.open("r", encoding="utf-8") as file:
        json_data = json.load(file)

    parse_json_to_csv(json_data, transaction_file, details_file)


if __name__ == "__main__":
    start = time.time()

    # ------------------------------
    #      Load Configuration
    # ------------------------------

    config = ConfigLoader(Path("data_transformation/config.yml"))

    input_files = config.get("files", {}).get("input", [])
    output_file = Path(
        config.get("files", {}).get("transaction_output", "transactions.csv")
    )
    details_file = Path(config.get("files", {}).get("details_output", "details.csv"))

    if isinstance(input_files, str):
        input_files = [input_files]  # Wrap single file in a list if input is a string

    for filename in input_files:
        process_single_file(Path(filename), output_file, details_file, config)
