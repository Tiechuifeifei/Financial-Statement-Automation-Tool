from decimal import Decimal, InvalidOperation
from dataclasses import dataclass, field
from typing import Optional
import csv
import datetime
import re

# Global constants
CURRENCY = "$"
UNIT = "m"  # could be "k", "m", "b"
COMPANY_NAME = "Wokki Company"
CURRENT_YEAR_NUMBER = 2023
LAST_YEAR_NUMBER = 2022

# Row indices for specific financial items in the CSV
DEFAULT_COLUMN_ROW_INDEX = {
    "current_asset": 7,
    "current_liability": 10,
    "ncib_debt": 9,
    "equity": 13,
    "ebit": 2,
    "interest_costs": 3,
    "debt_service_of_principal": 12,
    "revenue": 1,
    "profit": 4,
    "assets": 8,
    "liabilities": 11,
    "cash_flow": 15,
    "current_ratio": None,
    "dte_ratio": None,
    "dsc_ratio": None,
}

# Calculations for additional rows
ADDITIONAL_ROWS = {
    "Current Ratio": (
        lambda current_asset, current_liability: current_asset / current_liability,
        "current_asset",
        "current_liability",
    ),
    "Debt to Equity Ratio": (
        lambda ncib_debt, equity: ncib_debt / equity,
        "ncib_debt",
        "equity",
    ),
    "Debt Service Coverage Ratio": (
        lambda ebit, interest_costs, principal: ebit / (interest_costs + principal),
        "ebit",
        "interest_costs",
        "debt_service_of_principal",
    ),
}

# For formatting output
tail_dot_rgx = re.compile(r"(?:(\.)|(\.\d*?[1-9]\d*?))0+(?=\b|[^0-9])")


def remove_tail_dot_zeros(a):
    return tail_dot_rgx.sub(r"\2", a)


def safe_decimal(value):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError):
        return None


@dataclass
class Row:
    name: str
    current_year: Decimal
    last_year: Decimal
    difference: Decimal = field(init=False)
    ratio: Optional[Decimal] = field(init=False)

    def __post_init__(self):
        self.current_year = safe_decimal(self.current_year)
        self.last_year = safe_decimal(self.last_year)
        if self.current_year is not None and self.last_year is not None:
            self.difference = self.current_year - self.last_year
            self.ratio = (
                self.difference / self.last_year
                if self.last_year != 0
                and self.current_year * self.last_year >= 0
                else None
            )
        else:
            self.difference = None
            self.ratio = None


class Table:
    def __init__(self):
        self.rows: list[Row] = []
        self.row_name_index_dict = DEFAULT_COLUMN_ROW_INDEX.copy()

    def get_row_by_name(self, row_name: str) -> Optional[Row]:
        index = self.row_name_index_dict.get(row_name)
        if index is None or index >= len(self.rows):
            return None
        return self.rows[index]

    def add_row(self, row: Row):
        self.rows.append(row)

    def get_values_from_lambda_tuple(self, func, *names):
        args_current = [self.get_row_by_name(n).current_year for n in names]
        args_last = [self.get_row_by_name(n).last_year for n in names]
        return func(*args_current), func(*args_last)

    def generate_additional_rows(self):
        for name, (func, *args) in ADDITIONAL_ROWS.items():
            try:
                current, last = self.get_values_from_lambda_tuple(func, *args)
                self.rows.append(Row(name, current, last))
                self.row_name_index_dict[name.lower().replace(" ", "_")] = len(self.rows) - 1
            except Exception:
                self.rows.append(Row(name, "", ""))


def format_decimal(value: Optional[Decimal], as_percent=False, with_commas=True):
    if value is None:
        return ""
    try:
        if as_percent:
            return f"{value:.2%}"
        formatted = f"{value:,.2f}" if with_commas else f"{value:.2f}"
        return remove_tail_dot_zeros(formatted)
    except Exception:
        return ""


def write_text_report(file, table: Table):
    # This function writes human-readable analysis
    for name in ["revenue", "profit", "assets", "liabilities", "equity", "current_ratio", "dte_ratio", "dsc_ratio"]:
        row = table.get_row_by_name(name)
        if not row:
            continue
        change_type = "an increase" if row.difference >= 0 else "a decrease"
        unit = UNIT
        currency = CURRENCY
        file.write(
            f"{COMPANY_NAME} has seen {change_type} in {name.replace('_', ' ')} in "
            f"{LAST_YEAR_NUMBER} of {currency}{format_decimal(row.difference)}{unit} "
            f"({format_decimal(row.ratio, as_percent=True)}) from "
            f"{currency}{format_decimal(row.last_year)}{unit} to {currency}{format_decimal(row.current_year)}{unit}.\n\n"
        )
        if row.ratio and abs(row.ratio) > 1:
            file.write("!!! Ratio > 1.0 – may require further explanation\n\n")


def analyse_file(input_csv_file_name, delimiter=",", output_csv_file_name=None):
    table = Table()
    with open(input_csv_file_name, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            table.add_row(Row(*row.values()))

    table.generate_additional_rows()

    csv_out_name = output_csv_file_name or f"result_{datetime.date.today():%m-%d-%y}.csv"
    txt_out_name = f"result_{datetime.date.today():%m-%d-%y}.txt"

    # Write CSV
    with open(csv_out_name, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["name", "current_year", "last_year", "difference", "ratio"])
        writer.writeheader()
        for row in table.rows:
            writer.writerow({
                "name": row.name,
                "current_year": format_decimal(row.current_year),
                "last_year": format_decimal(row.last_year),
                "difference": format_decimal(row.difference),
                "ratio": format_decimal(row.ratio, as_percent=True),
            })

    # Write TXT summary
    with open(txt_out_name, "w") as txtfile:
        write_text_report(txtfile, table)

# Uncomment this to run:
# analyse_file("sample.csv")