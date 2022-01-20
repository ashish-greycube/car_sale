# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe


def execute(filters=None):
    from erpnext.stock.report.stock_balance.stock_balance import (
        execute as stock_balance,
    )
    from erpnext.stock.report.stock_ledger.stock_ledger import execute as stock_ledger

    columns, data = stock_balance(filters)

    # filter items with non zero bal_qty
    data = filter(lambda x: x.get("bal_qty") > 0, data)

    # set balance serial no column from Stock Ledger report
    filters.from_date = "2000-01-01"
    ledger_columns, ledger_data = stock_ledger(filters)

    # copy column def from ledger report to stock balance report
    for col in ledger_columns:
        if col["fieldname"] == "balance_serial_no":
            columns.insert(2, col)
            break

    # Old logic
    # for d in data:
    #     # out_data.append(d[0:2] + d[3:5])
    #     print(d[0:2])
    # for d in data:
    #     ledger = list(
    #         filter(
    #             lambda x: x["item_code"] == d["item_code"]
    #             and x["warehouse"] == d["warehouse"],
    #             ledger_data,
    #         )
    #     )
    #     if ledger:
    #         d["balance_serial_no"] = ledger and ledger[-1]["balance_serial_no"]

    # return columns, data

    # New logic: create row for each serial no
    out_fields = [
        "item_code",
        "item_name",
        "balance_serial_no",
        "item_group",
        "warehouse",
        "stock_uom",
        # "bal_qty",
        "val_rate",
        # "company",
    ]

    out_columns, out_data = [], []

    out_columns = [d for d in columns if d["fieldname"] in out_fields]
    for d in data:
        ledger = list(
            filter(
                lambda x: x["item_code"] == d["item_code"]
                and x["warehouse"] == d["warehouse"],
                ledger_data,
            )
        )
        if ledger:
            item = {field: d.get(field) for field in out_fields}
            balance_serial_nos = ledger and ledger[-1]["balance_serial_no"].strip(
                "'"
            ).split("\n")
            for srno in balance_serial_nos:
                tmp = item.copy()
                tmp["balance_serial_no"] = srno
                out_data.append(tmp)
        else:
            out_data.append({field: d.get(field) for field in out_fields})

    def _set_widths():
        for o in out_columns:
            if o["fieldname"] in ("item_code", "item_name", "warehouse"):
                o["width"] = 210
            elif o["fieldname"] in ("balance_serial_no"):
                o["width"] = 180
                o["label"] = "Serial No"

    _set_widths()

    return out_columns, out_data
