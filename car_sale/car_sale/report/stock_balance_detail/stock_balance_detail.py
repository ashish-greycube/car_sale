# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

# import frappe


def execute(filters=None):
    from erpnext.stock.report.stock_balance.stock_balance import (
        execute as stock_balance,
    )
    from erpnext.stock.report.stock_ledger.stock_ledger import execute as stock_ledger

    columns, data = stock_balance(filters)

    # set balance serial no column from Stock Ledger report
    filters.from_date = "2000-01-01"
    ledger_columns, ledger_data = stock_ledger(filters)

    balance_serial_no = list(
        filter(lambda x: x["fieldname"] == "balance_serial_no", ledger_columns)
    )[0]
    columns.insert(2, balance_serial_no)

    for d in data:
        ledger = list(
            filter(
                lambda x: x["item_code"] == d["item_code"]
                and x["warehouse"] == d["warehouse"],
                ledger_data,
            )
        )
        if ledger:
            d["balance_serial_no"] = ledger and ledger[-1]["balance_serial_no"]

    return columns, data
