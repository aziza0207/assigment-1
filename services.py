import json
import os
import ijson
import logging
from typing import Dict, List, Any
from collections import defaultdict

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


def get_relative_file_path(filename: str) -> str:
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "..", filename)
        file_path = os.path.normpath(file_path)

        if not os.path.isfile(file_path):
            logging.error(f"The file '{file_path}' does not exist.")

        return file_path
    except Exception as e:
        logging.error(f"Error constructing file path for '{filename}': {e}")


def find_duplicate_combinations_from_large_file(
    file_path: str, combination_fields: List[str]
) -> List[Dict[str, Any]]:
    combination_counts = defaultdict(list)

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            objects = ijson.items(file, "item")
            for obj in objects:
                if not isinstance(obj, dict):
                    logging.debug(f"Warning: Skipping non-dictionary object: {obj}")
                    continue
                try:
                    combination_key = tuple(obj[field] for field in combination_fields)
                except KeyError as e:
                    logging.debug(
                        f"Missing field {e} in object with ID {obj.get('id')}. Skipping."
                    )
                    continue
                combination_counts[combination_key].append(obj["id"])
    except FileNotFoundError:
        logging.error(f"Error: The file '{file_path}' does not exist.")
        return {}
    except ijson.JSONError as e:
        logging.error(f"Error parsing JSON with ijson: {e}")
        return {}
    uniques = {
        combo: ids[0] for combo, ids in combination_counts.items() if len(ids) == 1
    }
    return uniques


def process_uniques(
    uniques: Dict[tuple, List[Any]], combination_fields: List[str]
) -> List[Dict[str, Any]]:
    processed_uniques = []
    if uniques:
        try:
            for combo, ids in uniques.items():
                combo_dict = dict(zip(combination_fields, combo))
                processed_uniques.append(combo_dict)
        except Exception as e:
            logging.error(f"Error processing combination {combo}: {e}")
    return processed_uniques


def calculate_total_price_per_category(
    process_uniques: List[Dict[str, Any]]
) -> Dict[str, Any]:
    total_price_per_category = defaultdict(int)
    try:
        for item in process_uniques:
            category = item.get("category")
            price = item.get("price", 0)

            if category and isinstance(price, (int, float)):
                total_price_per_category[category] += price
            else:
                logging.debug(f"Invalid data for item: {item}")
        return dict(total_price_per_category)
    except Exception as e:
        logging.error(f"Error calculating total price per category: {e}")


def calculate_total_item_per_category(
    process_uniques: List[Dict[str, Any]]
) -> Dict[str, Any]:
    total_price_per_category = defaultdict(int)
    try:
        for item in process_uniques:
            category = item.get("category")
            if category:
                total_price_per_category[category] += 1
            else:
                logging.debug(f"Invalid data for item: {item}")
        return dict(total_price_per_category)
    except Exception as e:
        logging.error(f"Error calculating total price per category: {e}")


def main():
    try:
        combination_fields = ["owner", "price", "category"]
        file_path = get_relative_file_path("f.json")
        if not file_path:
            logging.error("Data file not found. Terminating the program.")
        if not os.path.isfile(file_path):
            logging.error(f"File '{file_path}' doesn't exist.")
        duplicates = find_duplicate_combinations_from_large_file(
            file_path, combination_fields
        )
        if not duplicates:
            logging.debug("Duplicates not found.")
        else:
            logging.debug(f"Found {len(duplicates)} duplicate combinations.")
        processed_uniques = process_uniques(duplicates, combination_fields)
        total_price = calculate_total_price_per_category(processed_uniques)
        total_items = calculate_total_item_per_category(processed_uniques)
        print(total_price)
        print(total_items)

    except Exception as e:
        logging.error(f"Unexpected error in the main execution block:  {e}")
