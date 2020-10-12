from sheetpakage import sheetops


#you have to add client_secret yourself
x = sheetops.sheet(spreadsheet_id="1YLNuBLQGv798vl-5s44qCd18cer3c8eBiEOkye3e5oo", sheet_id=0, x_axis="timestamp", y_axis="average_sales")
x.call_spreadsheet_n_create_graph()