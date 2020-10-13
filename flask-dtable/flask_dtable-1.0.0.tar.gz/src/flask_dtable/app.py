import json
from datetime import datetime


"""
CLASS: flask_dtable.
INFO: Create an variable table and return it as an str.
"""
class flask_dtable:
    '''
    Creates and returns an HTML Table as an str.\n

    Parameters
    ----------
    `data: (list)` Holds the data type for the Header and Body as an list.
    
    `section: (dict)` Holds the data sections that are printed as an dict:\n
    - active: (bool) Holds the section status,\n
    - position: (list) Holds the section position,\n
    - value: (list) Holds the value for the current position as list,\n
    - check: (list) Holds the operator for the current value as str
    
    `header: (dict)` Holds an header inside the Table as an dict:\n
    - value: (list) Holds each header text as str,\n
    - class: (str) Holds the header class as str,\n
    - id: (str) Holds the header id as str

    `footer: (dict)` Holds an Footer class as an dict:\n
    - active: (bool) Holds the Froms status,\n
    - class: (str) Holds the class for some opperations,\n
    - id: (str) Holds the footer id as str,\n
    - calculate: (list) Holds the footer calculates id´s as int,\n
    - decimal_places: (int) Holds the calculate format precision numbers\n
    
    `form: (dict)` Holds an form inside the Table Body as an dict:\n
    - active: (bool) Holds the Froms status,\n
    - position: (list) Holds the Froms td position,\n
    - action: (str or list) Holds the action link (`action`, `column`),\n
    - class: (str) Holds the html classes,\n
    - request_out: (dict) Holds the inputs outside an form:\n
        - request_name: (list) Holds the post input field Name,\n
        - request_id: (list) Holds the post input field id,\n
        - request_value: (list) Holds the post input field value,\n
        - value: (list) Holds the value for the current position as list,\n
        - check: (list) Holds the operator for the current value as str\n
    - request_in: (dict) Holds the inputs inside an form:\n
        - request_name: (list) Holds the post input field Name,\n
        - request_id: (list) Holds the post input field id,\n
        - request_value: (list) Holds the post input field value,\n
        - value: (list) Holds the value for the current position as list,\n
        - check: (list) Holds the operator for the current value as str\n
    - tooltip_text: (list) Holds the Button tooltip test,\n
    - button_color: (list) Holds the Bootstrap btn color,\n
    - icon: (list) Holds the Font Awesome btn icon

    `script: (dict)` Holds an script tag under the Table Footer:\n
    - active: (bool) Holds the Script status,\n
    - responsive: (bool) Holds the responsive status,\n
    - fixed: (bool) Holds the Fixed Columns,\n
    - order: (list) Holds the defalut Table order as int,\n
    - length_menu: (bool) Holds the Table lenght,\n
    - buttons: (list) Holds the action buttons as dicts:\n
        - button_name: (str) Holds the action button display name,\n
        - export: (list) Holds the export buttons,\n
        - hidde: (bool) Holds the hidde buttons status,\n
        - noHidde: (list) Holds the not hidde columns by index as int,\n
        - filter: (list) Holds the column filters as int,\n
        - custom_filter: (list) Holds an custom column filter as dicts:\n
            - name: (str) Holds the filter name,\n
            - labels: (list) Holds the filter display name as str,\n
            - values: (list) Holds the filter value check by data index as str\n
        - data_filter: (list) Holds an custom data filter as dicts:\n
            - name: (str) Holds the filter name,\n
            - labels: (list) Holds the filter data display name as str,\n
            - values: (list) Holds the filter data value as str\n
    - child_rows: (list) Holds the child rows as dicts:\n
        - label: (str) Holds the Label name,\n
        - column: (int) Holds the fallback data by data index,\n
    - live_feed: (dict) Holds the live feedbacks as dicts:\n
        - label: (str) Holds the feed display name,\n
        - column: (int) Holds the data by data index,\n
        - update: (dict) Holds an custom column filter as dicts:\n
            - url: (str) Holds the ajax call url,\n
            - value: (list) Holds the post value by data index as dicts\n
        - handler: (list) Holds an custom data filter as dicts:\n
            - type: (str) Holds the field form type,\n
            - post: (str) Holds the field id, name for ajax post,\n
            - column: (int) Holds the data by data index\n
    
    `editor: (dict)` Holds an column editor:\n
    - active: (bool) Holds the editor status,\n
    - action: (str) Holds the form action link,\n
    - label: (str) Holds the editor name,\n
    - size: (str) Holds the editor size (`small`, `large`),\n
    - fields: (list) Holds the editor fields:\n
        - label: (str) Holds the field display Name,\n
        - column: (int) Holds the field value from column,\n
        - check: (str, int) Holds the field value to check if type is radio,\n
        - class: (str) Holds the field html classes,\n
        - name: (str) Holds the field name,\n
        - id: (str) Holds the field id,\n
        - type: (str) Holds the field type (`text`, `textarea`, `radio`),\n
        - required: (bool) Holds the field required status,\n
        - disabled: (bool) Holds the field disabled status\n
        - hidden: (bool) Holds the field hidden status\n
    - order: (dict) Holds the editor order:\n
        - index: (int) Holds the order index (How many fields in one div are shown),\n
        - index_lower: (int) Holds the order index (if index is to short index_lower is active),\n
        - class: (str) Holds the order classes (fields div class),\n
        - class_lower: (str) Holds the order classes (if index_lower is active class_lower is set)\n
    - chars: (dict) Holds the editor replace tags (special characters)\n

    `popup: (dict)` Holds an column popup:\n
    - active: (bool) Holds the popup status,\n
    - url: (str) Holds the popup window url,\n
    - width: (int) Holds the popup window width,\n
    - height: (int) Holds the popup window height,\n
    - params: (list) Holds the popup window url parameter\n
    
    `settings: (dict)` Holds the default settings:\n
    - date_format: (str) Holds the output date format,\n
    '''
    """
    FUN: Create the __init__ function.
    INFO: Setup the data and create the table.
    """
    def __new__(cls,
            data: (list) = [],
            section: (dict) = {
                "active": False,
                "position": [],
                "value": [],
                "check": []
            },
            header: (dict) = {
                "value": [],
                "class": "",
                "id": ""
            },
            footer: (dict) = {
                "active": False,
                "class": "",
                "id": "",
                "calculate": [],
                "decimal_places": 2
            },
            form: (dict) = {
                "active": False,
                "position": [],
                "action": "",
                "class": "",
                "request_out": {
                    "request_name": [],
                    "request_id": [],
                    "request_value": [],
                    "value": [],
                    "check": []
                },
                "request_in": {
                    "request_name": [],
                    "request_id": [],
                    "request_value": [],
                    "value": [],
                    "check": []
                },
                "tooltip_text": [],
                "button_color": [],
                "icon": []
            },
            script: (dict) = {
                "active": False,
                "responsive": False,
                "fixed": None,
                "order": [],
                "length_menu": True,
                "buttons": [{
                    "button_name": "Actions",
                    "export": [],
                    "hidde": False,
                    "noHidde": [],
                    "filter": [],
                    "custom_filter": [],
                    "data_filter": []
                }],
                "child_rows": [
                    {
                        "label": "_set",
                        "column": 0
                    }
                ],
                "live_feed": {
                    "label": "",
                    "column": 0,
                    "update": {
                        "url": "",
                        "value": []
                    },
                    "handler": {
                        "type": "",
                        "post": "",
                        "column": 0
                    }
                }
            },
            editor: (dict) = {
                "active": False,
                "action": "",
                "label": "",
                "size": "small",
                "fields": [
                    {
                        "label": "",
                        "column": 0,
                        "check": 1,
                        "class": "",
                        "name": "",
                        "id": "",
                        "type": "",
                        "required": False,
                        "disabled": False,
                        "hidden": False
                    }
                ],
                "order": {
                    "index": 2,
                    "index_lower": 4,
                    "class": "",
                    "class_lower": ""
                },
                "chars": {
                    ord('ä'):'ae',
                    ord('ü'):'ue',
                    ord('ö'):'oe'
                }
            },
            popup: (dict) = {
                "active": False,
                "url": "",
                "width": 1600,
                "height": 1000,
                "params": []
            },
            settings: (dict) = {
                "date_format": "%d.%m.%Y"
            }
        ):
        # HELP: Check all attributes.
        try:
            # Check the data attribute.
            if data is None:
                raise AttributeError("Parameter (data) is empty.")
            # Check the section attribute.
            if section is None:
                raise AttributeError("Parameter (section) is empty.")
            # Check the header attribute.
            if header is None:
                raise AttributeError("Parameter (header) is empty.")
            else:
                if "id" not in header:
                    header["id"] = "dataTable"
                if "class" not in header:
                    header["class"] = ""
            # Check the footer attribute.
            if footer is None:
                raise AttributeError("Parameter (footer) is empty.")
            else:
                if "class" not in footer:
                    footer["class"] = ""
                if "id" not in footer:
                    footer["id"] = ""
                if "calculate" not in footer:
                    footer["calculate"] = None
                if "decimal_places" not in footer:
                    footer["decimal_places"] = 2
            # Check the form attribute.
            if form is None:
                raise AttributeError("Parameter (form) is empty.")
            else:
                if "request_out" in form:
                    if "request_name" not in form["request_out"]:
                        form["request_out"]["request_name"] = None
                    if "request_id" not in form["request_out"]:
                        form["request_out"]["request_id"] = None
                    if "request_value" not in form["request_out"]:
                        form["request_out"]["request_value"] = None
                    if "value" not in form["request_out"]:
                        form["request_out"]["value"] = None
                    if "check" not in form["request_out"]:
                        form["request_out"]["check"] = None
                else:
                    form["request_out"] = None
                if "request_in" in form:
                    if "request_name" not in form["request_in"]:
                        form["request_in"]["request_name"] = None
                    if "request_id" not in form["request_in"]:
                        form["request_in"]["request_id"] = None
                    if "request_value" not in form["request_in"]:
                        form["request_in"]["request_value"] = None
                    if "value" not in form["request_in"]:
                        form["request_in"]["value"] = None
                    if "check" not in form["request_in"]:
                        form["request_in"]["check"] = None
                else:
                    form["request_in"] = None
                if "class" not in form:
                    form["class"] = ""
                if "tooltip_text" not in form:
                    form["tooltip_text"] = "Berabeiten"
                if "button_color" not in form:
                    form["button_color"] = "text-warning"
                elif type(form["button_color"]) is list and any(x not in ['text-warning', 'text-danger', 'text-success', 'text-primary', 'text-secondary', 'text-info'] for x in form["button_color"]) or type(form["button_color"]) is str and form["button_color"] not in ['text-warning', 'text-danger', 'text-success', 'text-primary', 'text-secondary', 'text-info']:
                    raise AttributeError("Parameter (form button color) muss eine von diesen sein ('text-warning', 'text-danger', 'text-success', 'text-primary', 'text-secondary', 'text-info')")
                if "icon" not in form:
                    form["icon"] = "fas fa-edit"
            # Check the script attribute.
            if script is None:
                raise AttributeError("Parameter (script) is empty.")
            else:
                if "responsive" not in script:
                    script["responsive"] = False
                if "fixed" not in script:
                    script["fixed"] = None
                if "order" not in script:
                    script["order"] = None
                if "length_menu" not in script:
                    script["length_menu"] = True
                if "buttons" not in script:
                    script["buttons"] = None
                else:
                    for i, b in enumerate(script["buttons"]):
                        if "button_name" not in script["buttons"][i]:
                            script["buttons"][i].update({"button_name": "Actions"})
                        if "export" not in script["buttons"][i]:
                            script["buttons"][i].update({"export": None})
                        if "hidde" not in script["buttons"][i]:
                            script["buttons"][i].update({"hidde": False})
                        if "noHidde" not in script["buttons"][i]:
                            script["buttons"][i].update({"noHidde": None})
                        if "filter" not in script["buttons"][i]:
                            script["buttons"][i].update({"filter": None})
                        if "custom_filter" not in script["buttons"][i] and "filter" in script["buttons"][i]:
                            script["buttons"][i].update({"custom_filter": None})
                        if "data_filter" not in script["buttons"][i]:
                            script["buttons"][i].update({"data_filter": None})
                if "child_rows" not in script:
                    script["child_rows"] = None
                if "live_feed" not in script:
                    script["live_feed"] = None
                else:
                    if "label" not in script["live_feed"]:
                        script["live_feed"]["label"] = "Live: "
                    if "url" not in script["live_feed"]:
                        script["live_feed"]["url"] = None
                    if "column" not in script["live_feed"]:
                        script["live_feed"]["column"] = 0
                    if "update" not in script["live_feed"]:
                        script["live_feed"]["update"] = None
                    if "handler" not in script["live_feed"]:
                        script["live_feed"]["handler"] = None
            # Check the editor attribute.
            if editor is None:
                raise AttributeError("Parameter (editor) is empty.")
            else:
                if "action" not in editor:
                    editor["action"] = "table_update"
                if "label" not in editor:
                    editor["label"] = "Eintrag Bearbeiten"
                if "fields" not in editor:
                    raise AttributeError("Parameter (editor fields) is empty.")
                if "size" not in editor:
                    editor["size"] = "small"
                if "order" not in editor:
                    editor["order"] = None
                else:
                    if "index" not in editor["order"]:
                        editor["order"]["index"] = 2
                    if "index_lower" not in editor["order"]:
                        editor["order"]["index_lower"] = 4 if editor["order"]["index"] == 2 else int(editor["order"]["index"] * 2)
                    if "class" not in editor["order"]:
                        editor["order"]["class"] = "col-md-12 col-lg-12"
                    if "class_lower" not in editor["order"]:
                        editor["order"]["class_lower"] = "col-md-12 col-lg-12"
                if "chars" not in editor:
                    editor["chars"] = {ord('ä'):'ae', ord('ü'):'ue', ord('ö'):'oe'}
            # Check the popup attribute.
            if popup is None:
                raise AttributeError("Parameter (popup) is empty.")
            else:
                if "url" not in popup:
                    raise AttributeError("Parameter (popup url) is empty.")
                if "params" not in popup:
                    raise AttributeError("Parameter (popup) is empty.")
                if "width" not in popup:
                    popup["width"] = 1600
                if "height" not in popup:
                    popup["height"] = 1000
            # Check the settings attribute.
            if settings is None:
                raise AttributeError("Parameter (settings) is empty.")
            else:
                if "date_format" not in settings:
                    settings["date_format"] = "%d.%m.%Y"
        except Exception as e:
            raise Exception(e)

        """
        # FUN: Create the format_number function.
        # INFO: Return the formated number value.
        """
        def format_number(self, data, decimal_places = 2):
            # build format string.
            RS = '{{:,.{}f}}'.format(decimal_places)
            # make number string.
            RRS = RS.format(data)
            # Return the replaced chars.
            return RRS.replace(".", "%").replace(",", ".").replace("%", ",")

        """
        FUN: Create the get_date_format function.
        INFO: Check an format from an date and return it.
        """
        def get_date_format(self, date):
            formats: (list) = ['%Y-%m-%dT%H:%M:%S*%f%z', '%Y %b %d %H:%M:%S.%f %Z', '%b %d %H:%M:%S %z %Y', '%d/%b/%Y:%H:%M:%S %z', '%b %d, %Y %I:%M:%S %p', '%b %d %Y %H:%M:%S', '%b %d %H:%M:%S %Y', '%b %d %H:%M:%S %z', '%b %d %H:%M:%S', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%S.%f%z', '%Y-%m-%d %H:%M:%S %z', '%Y-%m-%d %H:%M:%S%z', '%Y-%m-%d %H:%M:%S,%f', '%Y/%m/%d*%H:%M:%S', '%Y %b %d %H:%M:%S.%f*%Z', '%Y %b %d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S,%f%z', '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S.%f%z', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S%Z', '%Y-%m-%d*%H:%M:%S:%f', '%Y-%m-%d*%H:%M:%S', '%y-%m-%d %H:%M:%S,%f %z', '%y-%m-%d %H:%M:%S,%f', '%y-%m-%d %H:%M:%S', '%y/%m/%d %H:%M:%S', '%y%m%d %H:%M:%S', '%Y%m%d %H:%M:%S.%f', '%m/%d/%y*%H:%M:%S', '%m/%d/%Y*%H:%M:%S', '%m/%d/%Y*%H:%M:%S*%f', '%m/%d/%y %H:%M:%S %z', '%m/%d/%Y %H:%M:%S %z', '%H:%M:%S', '%H:%M:%S.%f', '%H:%M:%S,%f', '%d/%b %H:%M:%S,%f', '%d/%b/%Y:%H:%M:%S', '%d/%b/%Y %H:%M:%S', '%d-%b-%Y %H:%M:%S', '%d-%b-%Y %H:%M:%S.%f', '%d %b %Y %H:%M:%S', '%d %b %Y %H:%M:%S*%f', '%m%d_%H:%M:%S', '%m%d_%H:%M:%S.%f', '%m/%d/%Y %I:%M:%S %p:%f', '%m/%d/%Y %H:%M:%S %p', '%Y-%d-%m %H:%M:%S', '%Y-%d-%m %H:%S:%M', '%Y-%d-%m %M:%S:%H', '%Y-%d-%m %S:%M:%H', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%S:%M', '%Y-%m-%d %M:%S:%H', '%Y-%m-%d %S:%M:%H', '%Y-%H-%d %M:%S:%W', '%Y-%H-%d %S:%M:%W', '%Y-%H-%d %W:%M:%S', '%Y-%H-%d %W:%S:%M', '%Y-%H-%M %U:%S:%W', '%Y-%H-%M %W:%S:%U', '%Y-%H-%S %U:%M:%W', '%Y-%H-%S %W:%M:%U', '%Y-%I-%d %M:%S:%W', '%Y-%I-%d %S:%M:%W', '%Y-%I-%d %W:%M:%S', '%Y-%I-%d %W:%S:%M', '%Y-%I-%M %U:%S:%W', '%Y-%I-%M %W:%S:%U', '%Y-%I-%S %U:%M:%W', '%Y-%I-%S %W:%M:%U', '%Y-%M-%d %H:%S:%W', '%Y-%M-%d %W:%S:%H', '%Y-%M-%H %U:%S:%W', '%Y-%M-%H %W:%S:%U', '%Y-%M-%I %U:%S:%W', '%Y-%M-%I %W:%S:%U', '%Y-%S-%d %H:%M:%W', '%Y-%S-%d %W:%M:%H', '%Y-%S-%H %U:%M:%W', '%Y-%S-%H %W:%M:%U', '%Y-%S-%I %U:%M:%W', '%Y-%S-%I %W:%M:%U', '%d-%m-%Y', '%d-%H-%Y', '%d-%I-%Y', '%d-%M-%Y', '%d-%S-%Y', '%m-%d-%Y', '%m-%H-%Y', '%m-%I-%Y', '%m-%M-%Y', '%m-%S-%Y', '%H-%d-%Y', '%H-%m-%Y', '%H-%M-%Y', '%H-%S-%Y', '%I-%d-%Y', '%I-%m-%Y', '%I-%M-%Y', '%I-%S-%Y', '%M-%d-%Y', '%M-%m-%Y', '%M-%H-%Y', '%M-%I-%Y', '%M-%S-%Y', '%S-%d-%Y', '%S-%m-%Y', '%S-%H-%Y', '%S-%I-%Y', '%S-%M-%Y', '%d-%m-%y', '%d-%m-%H', '%d-%m-%I', '%d-%m-%M', '%d-%m-%S', '%d-%y-%m', '%d-%y-%H', '%d-%y-%I', '%d-%y-%M', '%d-%y-%S', '%d-%H-%m', '%d-%H-%y', '%d-%H-%M', '%d-%H-%S', '%d-%I-%m', '%d-%I-%y', '%d-%I-%M', '%d-%I-%S', '%d-%M-%m', '%d-%M-%y', '%d-%M-%H', '%d-%M-%I', '%d-%M-%S', '%d-%S-%m', '%d-%S-%y', '%d-%S-%H', '%d-%S-%I', '%d-%S-%M', '%d-%U-%H', '%d-%U-%I', '%d-%U-%M', '%d-%U-%S', '%y-%d-%m', '%y-%d-%H', '%y-%d-%I', '%y-%d-%M', '%y-%d-%S', '%y-%m-%d', '%y-%m-%H', '%y-%m-%I', '%y-%m-%M', '%y-%m-%S', '%y-%H-%d', '%y-%H-%m', '%y-%H-%M', '%y-%H-%S', '%y-%I-%d', '%y-%I-%m', '%y-%I-%M', '%y-%I-%S', '%y-%M-%d', '%y-%M-%m', '%y-%M-%H', '%y-%M-%I', '%y-%M-%S', '%y-%S-%d', '%y-%S-%m', '%y-%S-%H', '%y-%S-%I', '%y-%S-%M', '%H-%d-%m', '%H-%d-%y', '%H-%d-%M', '%H-%d-%S', '%H-%m-%d', '%H-%m-%y', '%H-%m-%M', '%H-%m-%S', '%H-%y-%d', '%H-%y-%m', '%H-%y-%M', '%H-%y-%S', '%H-%M-%d', '%H-%M-%m', '%H-%M-%y', '%H-%M-%S', '%H-%S-%d', '%H-%S-%m', '%H-%S-%y', '%H-%S-%M', '%M-%d-%m', '%M-%d-%y', '%M-%d-%H', '%M-%d-%I', '%M-%d-%S', '%M-%m-%d', '%M-%m-%y', '%M-%m-%H', '%M-%m-%I', '%M-%m-%S', '%M-%y-%d', '%M-%y-%m', '%M-%y-%H', '%M-%y-%I', '%M-%y-%S', '%M-%H-%d', '%M-%H-%m', '%M-%H-%y', '%M-%H-%S', '%M-%I-%d', '%M-%I-%m', '%M-%I-%y', '%M-%I-%S', '%M-%S-%d', '%M-%S-%m', '%M-%S-%y', '%M-%S-%H', '%M-%S-%I', '%S-%d-%m', '%S-%d-%y', '%S-%d-%H', '%S-%d-%I', '%S-%d-%M', '%S-%m-%d', '%S-%m-%y', '%S-%m-%H', '%S-%m-%I', '%S-%m-%M', '%S-%y-%d', '%S-%y-%m', '%S-%y-%H', '%S-%y-%I', '%S-%y-%M', '%S-%H-%d', '%S-%H-%m', '%S-%H-%y', '%S-%H-%M', '%S-%I-%d', '%S-%I-%m', '%S-%I-%y', '%S-%I-%M', '%S-%M-%d', '%S-%M-%m', '%S-%M-%y', '%S-%M-%H', '%S-%M-%I', '%Y-%m-%d']
            for f in formats:
                try:
                    d = datetime.strptime(date, f)
                except:
                    continue
                return f
            return False
    
        """
        FUN: Create the index_exists function.
        INFO: Check if an index is in an list.
        """
        def index_exists(self, data, index):
            try:
                if type(data) is list:
                    return (0 <= int(index) < len(data)) or (-len(data) <= int(index) < 0)
                else:
                    raise TypeError("Parameter (data) must be a list.")
            except Exception as e:
                raise e

        """
        # FUN: Create the get_request function.
        # INFO: Return the in or out inputs from the Form.
        """
        def get_request(my_type, data):
            RS: (str) = ""
            # Check the type from request_value.
            if type(form[my_type]["request_value"]) is list:
                # Loop trougth the request_value.
                for i in range(len(form[my_type]["request_value"])):
                    name: (str) = form[my_type]["request_name"][i]
                    # Check if the id is set.
                    if form[my_type]["request_id"] is None:
                        id: (str) = form[my_type]["request_name"][i]
                    else:
                        id: (str) = form[my_type]["request_id"][i]
                    
                    # Check if there is an _sec.
                    if form[my_type]["request_value"][i] == "_sec":
                        # Check the type from value.
                        if type(form[my_type]["value"]) is list:
                            # Loop trougth the value.
                            for x in range(len(form[my_type]["value"])):
                                # Run the check code.
                                check = eval(form[my_type]["check"][x][0])
                                # Check if there is an _var key.
                                if type(form[my_type]["value"][x][0]) is list and str(form[my_type]["value"][x][0][0]) == "_var":
                                    RS += "<input type='text' name='"+ name +"' id='"+ id +"' value='"+ str(data[int(form[my_type]["value"][x][0][1])] if check else form[my_type]["value"][x][1]) +"' hidden/>"
                                elif type(form[my_type]["value"][x][1]) is list and str(form[my_type]["value"][x][1][0]) == "_var":
                                    RS += "<input type='text' name='"+ name +"' id='"+ id +"' value='"+ str(form[my_type]["value"][x][0] if check else data[int(form[my_type]["value"][x][1][1])]) +"' hidden/>"
                                else:
                                    RS += "<input type='text' name='"+ name +"' id='"+ id +"' value='"+ str(form[my_type]["value"][x][0] if check else form[my_type]["value"][x][1]) +"' hidden/>"
                        else:
                            raise TypeError("Parameter (form value) must be a list.")
                    else:
                        RS += "<input type='text' name='"+ name +"' id='"+ id +"' value='"+ str(data[int(form[my_type]["request_value"][i])]) +"' hidden/>"
            else:
                name: (str) = form[my_type]["request_name"]
                # Check if the id is set.
                if form[my_type]["request_id"] is None:
                    id: (str) = form[my_type]["request_name"]
                else:
                    id: (str) = form[my_type]["request_id"]

                # Check if there is an _sec.
                if form[my_type]["request_value"] == "_sec":
                    # Run the check code.
                    check = eval(form[my_type]["check"])
                    RS += "<input type='text' name='"+ name +"' id='"+ id +"' value='"+ str(form[my_type]["value"][0] if check else form[my_type]["value"][1]) +"' hidden/>"
                else:
                    RS += "<input type='text' name='"+ name +"' id='"+ id +"' value='"+ str(data[int(form[my_type]["request_value"])]) +"' hidden/>"
            # Return the inputs.
            return RS
        
        """
        # FUN: Create the get_section function.
        # INFO: Return the td from section.
        """
        def get_section(check, data, section, sec = False):
            RS: (str) = ""
            # Check if sec is True.
            if sec:
                if type(section[0]) is list and str(section[0][0]) == "_var":
                    # Check the check eval variable function.
                    if eval(check):
                        # Check the table_format type.
                        if type(data[section[0][1]]) == str:
                            RS += '<td>'+ str(data[section[0][1]]).strip()
                        elif type(data[section[0][1]]) in (datetime, datetime.date, datetime.time):
                            RS += '<td>'+ datetime.strptime(str(data[section[0][1]]).strip(), get_date_format(data[section[0][1]].strip()) if get_date_format(data[section[0][1]].strip()) else '%Y-%m-%d %H:%M:%S').strftime(settings["date_format"])
                        else:
                            RS += '<td class="text-right">'+ str(format_number(data[section[0][1]], footer["decimal_places"])).strip()
                    else:
                        # Check the table_format type.
                        if type(section[1]) == str:
                            RS += '<td>'+ str(section[1]).strip()
                        elif type(section[1]) in (datetime, datetime.date, datetime.time):
                            RS += '<td>'+ datetime.strptime(str(section[1]).strip(), get_date_format(section[1].strip()) if get_date_format(section[1].strip()) else '%Y-%m-%d %H:%M:%S').strftime(settings["date_format"])
                        else:
                            RS += '<td class="text-right">'+ str(format_number(section[1], footer["decimal_places"])).strip()
                elif type(section[1]) is list and str(section[1][0]) == "_var":
                    # Check the check eval variable function.
                    if eval(check):
                        # Check the table_format type.
                        if type(data[section[1][1]]) == str:
                            RS += '<td>'+ str(data[section[1][1]]).strip()
                        elif type(data[section[1][1]]) in (datetime, datetime.date, datetime.time):
                            RS += '<td>'+ datetime.strptime(str(data[section[1][1]]).strip(), get_date_format(data[section[1][1]].strip()) if get_date_format(data[section[1][1]].strip()) else '%Y-%m-%d %H:%M:%S').strftime(settings["date_format"])
                        else:
                            RS += '<td class="text-right">'+ str(format_number(data[section[1][1]], footer["decimal_places"])).strip()
                    else:
                        # Check the table_format type.
                        if type(section[0]) == str:
                            RS += '<td>'+ str(section[0]).strip()
                        elif type(section[0]) in (datetime, datetime.date, datetime.time):
                            RS += '<td>'+ datetime.strptime(str(section[0]).strip(), get_date_format(section[0].strip()) if get_date_format(section[0].strip()) else '%Y-%m-%d %H:%M:%S').strftime(settings["date_format"])
                        else:
                            RS += '<td class="text-right">'+ str(format_number(section[0], footer["decimal_places"])).strip()
                else:
                    # Check the check eval variable function.
                    if eval(check):
                        # Check the table_format type.
                        if type(section[1]) == str:
                            RS += '<td>'+ str(section[1]).strip()
                        elif type(section[1]) in (datetime, datetime.date, datetime.time):
                            RS += '<td>'+ datetime.strptime(str(section[1]).strip(), get_date_format(section[1].strip()) if get_date_format(section[1].strip()) else '%Y-%m-%d %H:%M:%S').strftime(settings["date_format"])
                        else:
                            RS += '<td class="text-right">'+ str(format_number(section[1], footer["decimal_places"])).strip()
                    else:
                        # Check the table_format type.
                        if type(section[0]) == str:
                            RS += '<td>'+ str(section[0]).strip()
                        elif type(section[0]) in (datetime, datetime.date, datetime.time):
                            RS += '<td>'+ datetime.strptime(str(section[0]).strip(), get_date_format(section[0].strip()) if get_date_format(section[0].strip()) else '%Y-%m-%d %H:%M:%S').strftime(settings["date_format"])
                        else:
                            RS += '<td class="text-right">'+ str(format_number(section[0], footer["decimal_places"])).strip()
            else:
                if type(data[section]) == str:
                    RS += '<td>'+ str(data[section]).strip()
                elif type(data[section]) in (datetime, datetime.date, datetime.time):
                    RS += '<td>'+ datetime.strptime(str(data[section]), get_date_format(data[section]) if get_date_format(data[section]) else '%Y-%m-%d %H:%M:%S').strftime(settings["date_format"])
                else:
                    RS += '<td class="text-right">'+ str(format_number(data[section], footer["decimal_places"])).strip()
            # Return the inputs.
            return RS

        # Start Creating the table.
        table: (str) = "<table class='table table-hover "+ str(header["class"]) +"' id='"+ str(header["id"]) +"' style='width:100%'>"

        # HELP: Create the Header.
        try:
            # Start the table Hader.
            table += "<thead class='table-head'><tr>"
            
            # Loop trought the header.
            for i in range(len(header["value"])):
                if form["active"]:
                    try:
                        # Check if position is an list.
                        if type(form["position"]) is list:
                            # Check if the check fun has an index.
                            if int(i) == int(form["position"][i]):
                                table += '<th class="sorting_desc_disabled sorting_asc_disabled text-right">'+ str(header["value"][i]) +'</th>'
                            else:
                                table += '<th>'+ str(header["value"][i]) +'</th>'
                        else:
                            # Check if the check fun has an index.
                            if int(i) == int(form["position"]):
                                table += '<th class="sorting_desc_disabled sorting_asc_disabled text-right">'+ str(header["value"][i]) +'</th>'
                            else:
                                table += '<th>'+ str(header["value"][i]) +'</th>'
                    except IndexError as e:
                        table += '<th>'+ str(header["value"][i]) +'</th>'
                else:
                    table += '<th>'+ str(header["value"][i]) +'</th>'
                
            # End of table Header.
            table += "</tr></thead>"
        except Exception as e:
            raise Exception(e)

        # HELP: Create the Body.
        try:
            # Start the table Body.
            table += "<tbody>"

            # Loop trought the data.
            for i in range(len(data)):
                # HELP: Create the popup window.
                if popup["active"]:
                    # Check the params type.
                    if type(popup["params"]) is list:
                        # Check the params length.
                        if len(popup["params"]) > 1:
                            # Start the table tr.
                            table += "<tr onclick=\"window.open('popup"+ str(popup["url"]) +"?"+ str(popup["params"][0][0]) +"="+ str(data[i][int(popup["params"][0][1])].strip()) + "".join('&{}={}'.format(pi[0], data[i][int(pi[1])].strip()) for pi in popup["params"][1:]) +"', '', 'width="+ str(popup["width"]) +",height="+ str(popup["height"]) +"')\">"
                        else:
                            # Start the table tr.
                            table += "<tr onclick=\"window.open('popup"+ str(popup["url"]) +"?"+ str(popup["params"][0][0]) +"="+ str(data[i][int(popup["params"][0][1])].strip()) +"', '', 'width="+ str(popup["width"]) +",height="+ str(popup["height"]) +"')\">"
                    else:
                        raise TypeError("Parameter (popup) must be a list that is filled with lists.")
                else:
                    # Start the table tr.
                    table += "<tr>"
                tcount: (int) = 0
                vcount: (int) = 0
                
                # Loop trought the length.
                for y in range(len(data[i])):
                    data[i] = list(data[i])
                    # HELP: Create the form.
                    try:
                        # Start the table form.
                        if form["active"]:
                            tform: (str) = ""
                            tcheck: (bool) = True

                            # Check if there is an out request.
                            if form["request_out"] is not None:
                                tform += get_request("request_out", data[i])
                            
                            # Create the form header.
                            if type(form["action"]) is list:
                                # Check if there is an _tab in action.
                                if form["action"][0] == "_tab":
                                    tform += "<a href='/"+ str(data[i][int(form["action"][-1])]) +"' target='_blank' data-toggle='tooltip' data-placement='left' title='"+ str(form["tooltip_text"]) +"' class='mr-2'><i class='"+ str(form["button_color"]) +" "+ str(form["icon"]) +"'></i></a>"
                                    tcheck = False
                            else:
                                tform += "<form action='"+ str(form["action"]) +"' class='"+ str(form["class"]) +"' id='send_form_"+ str(i) +"' name='send_form_"+ str(i) +"' method='POST'>"
                            
                            # Check if there is an in request.
                            if form["request_in"] is not None:
                                tform += get_request("request_in", data[i])
                            
                            # Check if there is an button.
                            if form["tooltip_text"] is not None:
                                # Check the type from tooltip_text.
                                if type(form["tooltip_text"]) is list:
                                    for k in range(len(form["tooltip_text"])):
                                        # Create the form buttons.
                                        if tcheck:
                                            tform += "<a href='javascript:{}' onclick='document.getElementById(\"send_form_"+ str(i) +"\").submit();' data-toggle='tooltip' data-placement='left' title='"+ str(form["tooltip_text"][k]) +"' class='mr-2'><i class='"+ str(form["button_color"][k]) +" "+ str(form["icon"][k]) +"'></i></a>"
                                else:
                                    if tcheck:
                                        tform += "<a href='javascript:{}' onclick='document.getElementById(\"send_form_"+ str(i) +"\").submit();' data-toggle='tooltip' data-placement='left' title='"+ str(form["tooltip_text"]) +"' class='mr-2'><i class='"+ str(form["button_color"]) +" "+ str(form["icon"]) +"'></i></a>"

                            # Create the form footer.
                            if tcheck:
                                tform += "</form>"
                            form["active"] = "del"
                    except Exception as e:
                        raise Exception(e)

                    # HELP: Create the section.
                    try:
                        # Start the table form.
                        if section["active"]:
                            td: (bool) = False

                            # Check the type from position.
                            if type(section["position"]) is list:
                                # Check if there is an _sec.
                                if "value" in section:
                                    # Check the type from value.
                                    if type(section["value"]) is list:
                                        # Loop trougth the value.
                                        for s in range(len(section["position"])):
                                            # INFO: Here is the important if statement.
                                            # Check if there is an index on the list length.
                                            if s == y:
                                                # Check if there is an match.
                                                if type(section["position"][s]) is int:
                                                    # Check the table_format type.
                                                    try:
                                                        table += get_section(None, data[i], section["position"][s])
                                                        tcount += 1
                                                        table += "</td>"
                                                    except Exception as e:
                                                        continue
                                                elif type(section["position"][s]) == str and str(section["position"][s]) == "_sec":
                                                    # Check the table_format type.
                                                    try:
                                                        table += get_section(section["check"][vcount][0], data[i], section["value"][vcount], True)
                                                        tcount += 1
                                                        vcount += 1
                                                        table += "</td>"
                                                    except Exception as e:
                                                        continue
                                                else:
                                                    raise TypeError("Parameter (section position) must be a list that is filled with str ('_ sec') or int.")
                                                # Check if the form position is machting tcount.
                                                if form["active"] == "del" and int(form["position"]) == int(tcount):
                                                    table += "<td class='text-right'>" + str(tform) + "</td>"
                                                elif form["active"] == "del" and len(data[i]) == 1 and int(tcount) == 0:
                                                    table += "<td class='text-right'>"+ str(tform) +"</td>"
                                    else:
                                        raise TypeError("Parameter (section position) must be a list that is filled with int.")
                                else:
                                    # Loop trougth the value.
                                    for s in range(len(section["position"])):
                                        # INFO: Here is the important if statement.
                                        # Check if there is an index on the list length.
                                        if s == y:
                                            # Check if there is an match.
                                            if type(section["position"][s]) is int:
                                                # Check the table_format type.
                                                try:
                                                    table += get_section(None, data[i], section["position"][s])
                                                    tcount += 1
                                                    table += "</td>"
                                                except Exception as e:
                                                    continue
                                            else:
                                                raise TypeError("Parameter (section position) must be an int.")
                                            # Check if the form position is machting tcount.
                                            if form["active"] == "del" and int(form["position"]) == int(tcount):
                                                table += "<td class='text-right'>"+ str(tform) +"</td>"
                                            elif form["active"] == "del" and len(data[i]) == 1 and int(tcount) == 0:
                                                table += "<td class='text-right'>"+ str(tform) +"</td>"
                            else:
                                raise TypeError("Parameter (section position) must be a list that is filled with int.")
                        else:
                            # Check the table_format type.
                            try:
                                table += get_section(None, data[i], y)

                                # Check if the form position is machting tcount.
                                if form["active"] == "del" and int(form["position"]) == int(tcount):
                                    table += str(tform) +"</td>"
                                elif form["active"] == "del" and len(data[i]) == 1 and int(tcount) == 0:
                                    table += "<td class='text-right'>"+ str(tform) +"</td>"
                                else:
                                    table += "</td>"
                                tcount += 1
                            except Exception as e:
                                continue
                    except Exception as e:
                        raise e
                # End of table tr.
                table += "</tr>"
            # End of table Body.
            table += "</tbody>"
        except Exception as e:
            raise e
            
        # HELP: Create the Footer.
        if footer["active"]:
            # Create the table Footer form data.
            try:
                # Start the table Footer.
                table += "<tfoot>"
                # Start the table tr.
                table += "<tr>"
                # Check if td is created.
                td_check: (bool) = False

                # Loop trought the footer.
                for i in range(len(header["value"])):
                    # Check if there is an calculate.
                    if footer["calculate"] is not None:
                        # Check if there is an calculate class.
                        if type(footer["calculate"]) is list:
                            # Loop trought the calculate.
                            for y in range(len(footer["calculate"])):
                                # Check if there is an match.
                                if i == int(footer["calculate"][y]):
                                    td_check = True
                                    table += "<td class='calculate text-right "+ str(footer["class"]) +"' id='"+ str(footer["id"]) +"'></td>"
                            # Check if the td is set.
                            if not td_check:
                                td_check = False
                                table += "<td class='"+ str(footer["class"]) +"' id='"+ str(footer["id"]) +"'></td>"
                        else:
                            raise TypeError("Parameter (calculate) must be a list filled with int.")
                    else:
                        # Check if there is an live_feed.
                        if script["active"] and script["live_feed"] is not None:
                            table += "<td colspan='"+ str(len(header["value"])) +"' class='"+ str(footer["class"]) +"' id='"+ str(footer["id"]) +"'></td>"
                            break
                        else:
                            table += "<td class='"+ str(footer["class"]) +"' id='"+ str(footer["id"]) +"'></td>"
                # End of table tr.
                table += "</tr>"

                # End of table Footer.
                table += "</tfoot>"
            except Exception as e:
                raise e
        
        # HELP: Create the Script.
        if script["active"]:
            # Create the table script.
            try:
                # Create all variables we need.
                order = "order: "+ str(script["order"]) +"," if script["order"] != None else ''
                lengthChange = '' if script["length_menu"] else 'lengthChange: false,\n       iDisplayLength: -1,'
                
                # Start with the script tag.
                table += "<script> "\
                            "$(document).ready(function () {\n"\
                            "   var table = $('#"+ str(header["id"]) +"').DataTable({\n"\
                            "       dom: \"<'row'"+ ("<'col'B>" if script["buttons"] is not None else "<'col'>") +"<'col-sm-10 d-inline-flex justify-content-end'<'#dataTable_info.col text-center'>fl>>" + "<'row'<'col-sm-12'tr>>" + "<'row'<'col-sm-5'i><'col-sm-7'p>>\",\n"\
                            "       scrollY: '50vh',\n"\
                            f"       scrollX: {'true' if footer['active'] and footer['calculate'] is not None else 'false'},\n"\
                            "       scrollCollapse: true,\n"\
                            f"       {lengthChange}\n"
                
                # Check if there are responsive.
                if script["responsive"] == True:
                    table += "       responsive: {\n"\
                            "           display: $.fn.dataTable.Responsive.display.modal( {\n"\
                            "               header: function ( row ) {\n"\
                            "                   var data = row.data();\n"\
                            "                   return 'Details for '+data[0]+' '+data[1];\n"\
                            "               }\n"\
                            "           }),\n"\
                            "           renderer: $.fn.dataTable.Responsive.renderer.tableAll()\n"\
                            "       },\n"

                # End of baisc table configurations.
                table += "       language: {\n"\
                        "           url: '{{url_for('static', filename='json/datatables.json')}}',\n"\
                        "           decimal: ',',\n"\
                        "           thousands: '.',\n"\
                        "           search: '_INPUT_',\n"\
                        "           searchPlaceholder: 'Suchen...',\n"
                
                # Check if there are buttons.
                if script["buttons"] is not None:
                    # Loop trough the buttons.
                    for b, btn in enumerate(script["buttons"]):
                        # Check if there is an filter.
                        if script["buttons"][b]["filter"] or script["buttons"][b]["custom_filter"]:
                            table += "            searchPanes: {\n"\
                                    "               collapse: {\n"\
                                    "                   _: 'Filter',\n"\
                                    "                   0: 'Filter'\n"\
                                    "               },\n"\
                                    "               title: {\n"\
                                    "                   _: 'Aktive Filters - %d',\n"\
                                    "                   0: 'Keine Filter Aktiv',\n"\
                                    "                   1: 'Ein Filter Aktiv',\n"\
                                    "               }\n"\
                                    "           }\n"
                        # Leave the loop.
                        continue
                
                # End of table language.
                table += "        },\n"\
                        f"{order}\n"\
                        "       pagingType: 'full_numbers',\n"
                
                # Check if the length menu is enabled.
                if script["length_menu"]:
                    table += "       lengthMenu: [\n"\
                            "           [10, 25, 50, -1], [10, 25, 50, 'All']\n"\
                            "       ],\n"
                
                # Check if there are buttons.
                if script["buttons"] is not None:
                    # Loop trough the buttons.
                    for b, btn in enumerate(script["buttons"]):
                        # Check if there is noVis.
                        if script["buttons"][b]["noHidde"] is not None:
                            # Check the type from noHidde.
                            if type(script["buttons"][b]["noHidde"]) is list:
                                table += "       columnDefs: [{\n"\
                                        "           targets: [\n"
                                # Get all noVis columns.
                                for i in range(len(script["buttons"][b]["noHidde"])):
                                    table += str(script["buttons"][b]["noHidde"][i]) + ",\n"
                                table += "],\n"\
                                        "           className: 'noVis'\n"\
                                        "       }],\n"
                        # Leave the loop.
                        continue
                
                # Check if there are buttons.
                if script["buttons"] is not None:
                    table += "        buttons: [ \n"\
                    # Loop trough the buttons.
                    for b, btn in enumerate(script["buttons"]):
                        table += "        {\n"\
                                "           extend: 'collection',\n"\
                                f"           text: '{script['buttons'][b]['button_name']}',\n"\
                                "           className: 'btn-sm btn-outline-warning animation-on-hover',\n"\
                                "           buttons: [\n"
                        # Loop trough the buttons.
                        for bkey, brow in script["buttons"][b].items():
                            # Check if there are export buttons.
                            if bkey == "export" and script["buttons"][b]["export"] is not None:
                                # Loop trougth the export buttons.
                                for i in range(len(script["buttons"][b]["export"])):
                                    table += "'"+ str(script["buttons"][b]["export"][i]) +"',\n"
                            
                            # Check if there are column hidde buttons.
                            if bkey == "hidde" and script["buttons"][b]["hidde"]:
                                table += "       {\n"\
                                        "           text: 'Aus-/Einblenden',\n"\
                                        "           extend: 'colvis',\n"\
                                        "           className: 'colVisBtn hidde',\n"\
                                        "           columns: ':not(.noVis)'\n"\
                                        "        },\n"
                        
                            # Check if there are column filter buttons.
                            if bkey == "filter" and script["buttons"][b]["filter"] or bkey == "custom_filter" and script["buttons"][b]["custom_filter"]:
                                # Check if there is an filter.
                                if script["buttons"][b]["filter"] is None:
                                    script["buttons"][b]["filter"] = ['false']
                                table += "        {\n"\
                                        "           extend: 'searchPanes',\n"\
                                        "           className: 'filterBtn filter',\n"\
                                        "           config: {\n"\
                                        "               cascadePanes: true,\n"\
                                        "               controls: false,\n"\
                                        "               threshold: 1,\n"\
                                        "               clear: false,\n"\
                                        "               dataLength: 15,\n"\
                                        f"               columns: [{', '.join(str(i) for i in script['buttons'][b]['filter'])}],\n"
                                # Check if there are an custom filter pan.
                                if script["buttons"][b]["custom_filter"] is not None:
                                    table += "               panes: [\n"
                                    # Loop trougth the custom filter buttons.
                                    for i in range(len(script["buttons"][b]["custom_filter"])):
                                        # Check the filter structure.
                                        if "name" not in script["buttons"][b]["custom_filter"][i]:
                                            raise AttributeError("Parameter (custom filter) has no 'name' assigned: "+ str(i))
                                        if "labels" not in script["buttons"][b]["custom_filter"][i]:
                                            raise AttributeError("Parameter (custom filter) has no 'labels' assigned: "+ str(i))
                                        
                                        # Create each custom filter.
                                        table += "                   {\n"\
                                                f"                       header:'{script['buttons'][b]['custom_filter'][i]['name']}',\n"\
                                                "                       options: [\n"
                                        # Check if labels is an list.
                                        if type(script["buttons"][b]["custom_filter"][i]["labels"]) is list:
                                            # Loop trougth the custom filter labels.
                                            for x in range(len(script["buttons"][b]["custom_filter"][i]["labels"])):
                                                table += "                           {\n"\
                                                        f"                               label:'{script['buttons'][b]['custom_filter'][i]['labels'][x]}',\n"\
                                                        "                               value: function(data, index) {\n"
                                                # Check if there is an check attribute in the filter.
                                                if "values" not in script["buttons"][b]["custom_filter"][i]:
                                                    table += f"                                   return '{script['buttons'][b]['custom_filter'][i]['labels'][x]}';\n"
                                                else:
                                                    table += f"                                   return {script['buttons'][b]['custom_filter'][i]['values'][x]};\n"
                                                # End of check attribute.
                                                table += "                               }\n"\
                                                        "                           },\n"
                                        else:
                                            raise TypeError("Parameter (custom_filter 'labels', 'values') must be a list that is filled with str.")
                                        # End of custom pan.
                                        table += "                       ]\n"\
                                                "                   },\n"
                                    # End of custom filter pans.
                                    table += "               ]\n"
                                # End of filter buttons.
                                table +="           }\n"\
                                        "        },\n"
                        
                            # Check if there are data_filter.
                            if bkey == "data_filter" and script["buttons"][b]["data_filter"] is not None:
                                # Loop trougth the custom data filter buttons.
                                for i in range(len(script["buttons"][b]["data_filter"])):
                                    # Check the filter structure.
                                    if "name" not in script["buttons"][b]["data_filter"][i]:
                                        raise AttributeError("Parameter (data filter) has no 'name' assigned: "+ str(i))
                                    if "labels" not in script["buttons"][b]["data_filter"][i]:
                                        raise AttributeError("Parameter (data filter) has no 'labels' assigned: "+ str(i))

                                    # Create each data filter.
                                    table += "        {\n"\
                                            "           extend: 'collection',\n"\
                                            "           text: '"+ str(script["buttons"][b]["data_filter"][i]["name"]) +"',\n"\
                                            "           className: 'colVisBtn data_filter',\n"\
                                            "           fade: true,\n"\
                                            "           buttons: [\n"
                                    # Check if labels is an list.
                                    if type(script["buttons"][b]["data_filter"][i]["labels"]) is list:
                                        # Loop trougth the custom data filter labels.
                                        for x in range(len(script["buttons"][b]["data_filter"][i]["labels"])):
                                            # Check if there is an value on this label.
                                            if "values" in script["buttons"][b]["data_filter"][i] and index_exists(script["buttons"][b]["data_filter"][i]["values"], x):
                                                table += "{text: '"+ str(script["buttons"][b]["data_filter"][i]["labels"][x]) +"', action: function() {window.location = updateURLParameter(window.location.href, '"+ str(script["buttons"][b]["data_filter"][i]["name"]) +"', '"+ str(script["buttons"][b]["data_filter"][i]["values"][x]) +"');} },\n"
                                            else:
                                                table += "{text: '"+ str(script["buttons"][b]["data_filter"][i]["labels"][x]) +"', action: function() {window.location = updateURLParameter(window.location.href, '"+ str(script["buttons"][b]["data_filter"][i]["name"]) +"', '"+ str(script["buttons"][b]["data_filter"][i]["labels"][x]) +"');} },\n"
                                    else:
                                        raise TypeError("Parameter (data_filter 'labels', 'values') must be a list that is filled with str.")
                                    # End of custom data filter.
                                    table += "           ]\n"\
                                            "        },\n"
                        # End of table buttons.
                        table += "]},\n"
                    table += "],\n"
                
                # Check if there are fixed columns.
                if script["fixed"] is not None:
                    table += "        fixedColumns: true,\n"\
                            "        fixedColumns: {\n"\
                            "            leftColumns: "+ str(script["fixed"]) +"\n"\
                            "        },\n"
                
                # Check if there are calculate columns.
                if footer["active"] and footer["calculate"] is not None:
                    table += "        'footerCallback': function ( row, data, start, end, display ) {\n"\
                            "           var api = this.api(), data;\n"\
                            "           var intVal = function (i) {\n"\
                            "               return typeof i === 'string' ?"\
                            "               i.replace(/\./g,'').replace(/[\$,]/g, '.')*1 :"\
                            "               typeof i === 'number' ?"\
                            "               i : 0;"\
                            "           }\n"\
                            "           $('tfoot .calculate').each(function() {\n"\
                            "               pageTotal = api.column(this.cellIndex, {page: 'current'}).data().reduce(function (a, b) {\n"\
                            "                   return intVal(a) + intVal(b);\n"\
                            "               }, 0 );\n"\
                            "               $(api.column(this.cellIndex).footer()).html(\n"\
                            "                   pageTotal.toLocaleString('de')\n"\
                            "               );\n"\
                            "           });\n"\
                            "       },\n"
                # End of datatables script.
                table += "    });\n"
                
                # HELP: Check if there are editor.
                if editor["active"] and editor["fields"] is not None:
                    # Create the tr click.
                    table += "    $('#"+ str(header["id"]) +"').on('dblclick', 'tbody tr[role=\"row\"]', function(e) {\n"\
                            "        replaceElementTag('myform', '<form></form>');\n"
                    # Create the Fields.
                    for i in range(len(editor["fields"])):
                        # Check if there is an index.
                        if int(editor["fields"][i]["column"]) <= len(header["value"]):
                            # Check if there is an special key (radio).
                            if "type" in editor["fields"][i] and editor["fields"][i]["type"] == "radio":
                                table += "         if($(this).find('td').eq("+ str(editor["fields"][i]["column"]) +").text() == "+ str(editor["fields"][i]["check"]) +") {\n"\
                                        "             $('#"+ str(editor["fields"][i]["id"] if "id" in editor["fields"][i] else header["value"][i].lower().translate(editor["chars"]).replace(" ", "_")) +"_1').click();\n"\
                                        "         } else {\n"\
                                        "             $('#"+ str(editor["fields"][i]["id"] if "id" in editor["fields"][i] else header["value"][i].lower().translate(editor["chars"]).replace(" ", "_")) +"_0').click();\n"\
                                        "         }\n"
                            # Check if there is an special key (textarea).
                            if "type" in editor["fields"][i] and editor["fields"][i]["type"] == "textarea":
                                table += "         $('#"+ str(editor["fields"][i]["id"] if "id" in editor["fields"][i] else header["value"][i].lower().translate(editor["chars"]).replace(" ", "_")) +"').val($(this).find('td').eq("+ str(editor["fields"][i]["column"] if editor["fields"][i]["column"] is not None else i) +").text());\n"
                            # Check if there is an special key (select).
                            if "type" in editor["fields"][i] and editor["fields"][i]["type"] == "select":
                                table += "var opt = $.trim($(this).find('td').eq("+ str(editor["fields"][i]["column"] if editor["fields"][i]["column"] is not None else i) +").text());\n"\
                                        "         $('#"+ str(editor["fields"][i]["id"] if "id" in editor["fields"][i] else header["value"][i].lower().translate(editor["chars"]).replace(" ", "_")) +" option[value=\"'+ opt +'\"]').attr('selected', 'selected');\n"
                            # Check if there is an special key (date).
                            if "type" in editor["fields"][i] and editor["fields"][i]["type"] == "date":
                                table += "         $('#"+ str(editor["fields"][i]["id"] if "id" in editor["fields"][i] else header["value"][i].lower().translate(editor["chars"]).replace(" ", "_")) +"').attr('value', moment($(this).find('td').eq("+ str(editor["fields"][i]["column"] if editor["fields"][i]["column"] is not None else i) +").text(), 'DD.MM.YYYY').format('YYYY-MM-DD'));\n"
                            else:
                                table += "         $('#"+ str(editor["fields"][i]["id"] if "id" in editor["fields"][i] else header["value"][i].lower().translate(editor["chars"]).replace(" ", "_")) +"').attr('value', $(this).find('td').eq("+ str(editor["fields"][i]["column"] if editor["fields"][i]["column"] is not None else i) +").text());\n"
                        else:
                            raise ValueError("The column index is not in the table index: "+ str(editor["fields"][i]["column"]))
                    # Create the open modal dialog.
                    table += "        $('#editor_modal').appendTo('body').modal('show');\n"
                    # End of tr click.
                    table += "    });\n"

                # HELP: Check if there are script child_rows.
                if script["child_rows"] is not None and script["child_rows"][0]["label"] != "_set":
                    # Check the type from child_rows.
                    if type(script["child_rows"]) is list:
                        # Create the details dialog.
                        table += " $('#"+ str(header["id"]) +"').on('click', 'tbody tr[role=\"row\"]', function () {\n"\
                            "var tr = $(this).closest('tr');\n"\
                            "var row = table.row( tr );\n"\
                            "if ( row.child.isShown() ) {\n"\
                                "row.child.hide();\n"\
                                "tr.removeClass('shown');\n"\
                            "} else {\n"\
                                "row.child( format(row.data(), ["+ str(', '.join(json.dumps(row) for i, row in enumerate(script["child_rows"]))) +"]) ).show();\n"\
                                "tr.addClass('shown');\n"\
                            "}\n"\
                        "});\n"
                
                # HELP: Check if there are script live_feed.
                if footer["active"] and footer["calculate"] is None and script["live_feed"] is not None:
                    # Create the tr click.
                    table += "       $.fn.clicker = function(data_data) {\n"\
                            "            $('#"+ str(header["id"]) +" tbody tr.selected').removeClass('selected').trigger('click', [data_data]);\n"\
                            "        };\n"\
                            "        $('#"+ str(header["id"]) +"').on('click', 'tbody tr[role=\"row\"]', function (e, data_data) {\n"\
                            "           if ($(this).hasClass('selected')) {\n"\
                            "               $(this).removeClass('selected');\n"\
                            "               $(table.column(0).footer()).html('');\n"\
                            "           } else {\n"\
                            "               table.$('tr.selected').removeClass('selected');\n"\
                            "               $(this).addClass('selected');\n"\
                            "               $(table.column(0).footer()).html('');\n"\
                            "               var fallback = $(this).find('td').eq("+ str(script["live_feed"]["column"]) +").text();\n"
                    # Check if there is an handler.
                    if script["live_feed"]["handler"] is not None:
                        table += "               var fallback_data = $(this).find('td').eq("+ str(script["live_feed"]["handler"]["column"]) +").text();\n"
                        # Check the event hander type.
                        if script["live_feed"]["handler"]["type"] == "input":
                            changer = "               $('#"+ str(script["live_feed"]["handler"]["post"]) +"').attr('value', data_data == null ? fallback_data : data_data);\n"
                            handler = "<input type=\"text\" class=\"form-control form-control-sm\" id=\""+ str(script["live_feed"]["handler"]["post"]) +"\" name=\""+ str(script["live_feed"]["handler"]["post"]) +"\" onchange=\"$(this).clicker(this.value);\">"
                            formData = "                   formData.append('"+ str(script["live_feed"]["handler"]["post"]) +"', data_data);\n"
                        if script["live_feed"]["handler"]["type"] == "date":
                            # Create the event hander type value changer.
                            changer = "               $('#"+ str(script["live_feed"]["handler"]["post"]) +"').attr('value', data_data == null ? moment(fallback_data, 'DD.MM.YYYY').format('YYYY-MM-DD') : data_data);\n"
                            # Create the event hander.
                            handler = "<input type=\"date\" class=\"form-control form-control-sm\" id=\""+ str(script["live_feed"]["handler"]["post"]) +"\" name=\""+ str(script["live_feed"]["handler"]["post"]) +"\" onchange=\"$(this).clicker(this.value);\">"
                            # Create the event hander formData.
                            formData = "                   formData.append('"+ str(script["live_feed"]["handler"]["post"]) +"', moment(data_data, 'YYYY-MM-DD').format('DD.MM.YYYY'));\n"
                        else:
                            changer = ""
                            handler = ""
                            formData = ""
                    # Check if there is an update.
                    if script["live_feed"]["update"] is not None:
                        table += "               var formData = new FormData();\n"

                        # Loop trougth the update values.
                        for i in range(len(script["live_feed"]["update"]["value"])):
                            table += "                   formData.append('"+ str(script["live_feed"]["update"]["value"][i]["post"]) +"', $(this).find('td').eq("+ str(script["live_feed"]["update"]["value"][i]["column"]) +").text());\n"
                        table += formData
                        # End of the update values.
                        table += "                $.ajax({\n"\
                                "                     url: '"+ str(script["live_feed"]["update"]["url"]) +"',\n"\
                                "                     type: 'POST',\n"\
                                "                     data: formData,\n"\
                                "                     contentType: false,\n"\
                                "                     cache: false,\n"\
                                "                     processData: false,\n"\
                                "                     success: function (response) {\n"\
                                "                         response = (response['data'] ? response['data'] : fallback);\n"\
                                "                         $(table.column(0).footer()).html('"+ str(handler) +"<span class=\"text-warning\">"+ str(script["live_feed"]["label"]) +": </span><br>'+ response);\n"\
                                "                     },\n"\
                                "                     fail: function (fail) {\n"\
                                "                         console.log('No parameter (live_feed) was found in the Ajax call.');\n"\
                                "                     }\n"\
                                "                 });\n"
                    else:
                        table += "                $(table.column(0).footer()).html('"+ str(handler) +"<span class=\"text-warning\">"+ str(script["live_feed"]["label"]) +": </span><br>'+ fallback);\n"
                    # End of the handler.
                    table += "                $(document).ajaxComplete(function(event, xhr, settings) {\n"\
                            "                    "+ changer + "\n"\
                            "                });\n"
                    # End of live_feed.
                    table += "           }\n"\
                            "       });\n"

                # End of table script tag.
                table += "});\n"\
                "</script>\n"
            except Exception as e:
                raise e

        # HELP: Create the Editor.
        if editor["active"]:
            # Create the table Editor.
            try:
                # Start the Editor.
                table += "<div class='modal fade' id='editor_modal' tabindex='-1' role='dialog' aria-labelledby='editor_modal_label' aria-hidden='true'>\n"\
                            f"<div class='modal-dialog {'modal-lg' if editor['size'] == 'large' else ''} modal-dialog-centered' role='document'>\n"\
                                "<div class='modal-content'>\n"\
                                    "<myform action='"+ str(editor["action"]) +"' id='send_form' method='post' class='form needs-validation' novalidate>\n"\
                                        "<div class='modal-header'>\n"\
                                            "<h5 class='modal-title' id='editor_modal_label'>"+ str(editor["label"]) +"</h5>\n"\
                                            "<button type='button' class='close' data-dismiss='modal' aria-label='Close'>\n"\
                                                "<span aria-hidden='true'>&times;</span>\n"\
                                            "</button>\n"\
                                        "</div>\n"\
                                        "<div class='modal-body'>\n"\
                                            "<div class='row'>\n"
                # Check if there are order.
                if editor["order"] is not None:
                    # Create the order div.
                    table += "<div class='"+ str(editor["order"]["class"]) +"'>\n"
                else:
                    # Create the order div.
                    table += "<div class='col-md-12 col-lg-12'>\n"
                # Create the Fields.
                for i in range(len(editor["fields"])):
                    # Check if there are order.
                    if editor["order"] is not None:
                        # Check if i is matching.
                        if int(i) == int(editor["order"]["index"]):
                            # Update the order index.
                            editor["order"]["index"] += editor["order"]["index"]
                            
                            # Check if there are order.
                            if int(i) == int(editor["order"]["index_lower"]):
                                # Create the order div.
                                table += "</div> "\
                                    "<div class='"+ str(editor["order"]["class_lower"]) +"'>\n"
                            else:
                                # Create the order div.
                                table += "</div> "\
                                    "<div class='"+ str(editor["order"]["class"]) +"'>\n"
                    # Create an Field and check the type.
                    if "type" in editor["fields"][i]:
                        # Create an Field with type textarea.
                        if editor["fields"][i]["type"] == "textarea":
                            table += "<div class='form-group'>\n"\
                                        "<label for='"+ str(editor["fields"][i]["id"] if "id" in editor["fields"][i] else header["value"][i].lower().translate(editor["chars"]).replace(" ", "_")) +"' class='col-form-label'>"+ str(editor["fields"][i]["label"]) +"</label>\n"\
                                        "<textarea type='textarea' id='"+ str(editor["fields"][i]["id"] if "id" in editor["fields"][i] else header["value"][i].lower().translate(editor["chars"]).replace(" ", "_")) +"' name='"+ str(editor["fields"][i]["name"] if "name" in editor["fields"][i] else header["value"][i].lower().translate(editor["chars"]).replace(" ", "_")) +"' class='form-control "+ str(editor["fields"][i]["class"] if "class" in editor["fields"][i] else "") +"' "+ str("disabled" if "disabled" in editor["fields"][i] else "") +" "+ str("required" if "required" in editor["fields"][i] else "") +"></textarea>\n"
                        # Create an Field with type select.
                        elif editor["fields"][i]["type"] == "select":
                            table += "<div class='form-group'>\n"\
                                        "<label for='"+ str(editor["fields"][i]["id"] if "id" in editor["fields"][i] else header["value"][i].lower().translate(editor["chars"]).replace(" ", "_")) +"' class='col-form-label'>"+ str(editor["fields"][i]["label"][0]) +"</label>\n"\
                                        "<select type='text' id='"+ str(editor["fields"][i]["id"] if "id" in editor["fields"][i] else header["value"][i].lower().translate(editor["chars"]).replace(" ", "_")) +"' name='"+ str(editor["fields"][i]["name"] if "name" in editor["fields"][i] else header["value"][i].lower().translate(editor["chars"]).replace(" ", "_")) +"' class='selectpicker show-tick dark "+ str(editor["fields"][i]["class"] if "class" in editor["fields"][i] else "") +"' "+ str("disabled" if "disabled" in editor["fields"][i] else "") +" "+ str("required" if "required" in editor["fields"][i] else "") +">\n"
                            # Check if there are special values.
                            if len(editor["fields"][i]["label"]) == 3:
                                # Loop trough the labels.
                                for l in range(len(editor["fields"][i]["label"][-1])):
                                    # Check if there is an subtext.
                                    table += f"<option value='{editor['fields'][i]['label'][1][l]}' data-subtext='{editor['fields'][i]['label'][-1][l] if editor['fields'][i]['label'][-1][l] is not None else ''}'>{editor['fields'][i]['label'][1][l]}</option>\n"
                            else:
                                # Loop trough the labels.
                                for l in range(len(editor["fields"][i]["label"][-1])):
                                    # Check if there is an subtext.
                                    table += f"<option value='{editor['fields'][i]['label'][-1][l]}'>{editor['fields'][i]['label'][-1][l]}</option>\n"
                            # End of the select options.
                            table += "</select>\n"
                        # Create an Field with type radio.
                        elif editor["fields"][i]["type"] == "radio":
                            # Check the type from label.
                            if type(editor["fields"][i]["label"]) is list:
                                table += "<div class='form-group'>\n"\
                                            "<label for='"+ str(editor["fields"][i]["id"] if "id" in editor["fields"][i] else header["value"][i].lower().translate(editor["chars"]).replace(" ", "_")) +"' class='col-form-label w-100'>"+ str(editor["fields"][i]["label"][0]) +"</label>\n"\
                                            "<div class='form-check form-check-inline mt-auto'>\n"\
                                                "<label class='form-check-label m-auto'><input class='radio-inline mr-1' type='radio' name='"+ str(editor["fields"][i]["name"] if "name" in editor["fields"][i] else header["value"][i].lower().translate(editor["chars"]).replace(" ", "_")) +"' id='"+ str(editor["fields"][i]["id"] if "id" in editor["fields"][i] else header["value"][i].lower().translate(editor["chars"]).replace(" ", "_")) +"_1' value='1'/>"+ str(editor["fields"][i]["label"][1]) +"</label>\n"\
                                            "</div>\n"\
                                            "<div class='form-check form-check-inline mt-auto'>\n"\
                                                "<label class='form-check-label m-auto'><input class='radio-inline mr-1' type='radio' name='"+ str(editor["fields"][i]["name"] if "name" in editor["fields"][i] else header["value"][i].lower().translate(editor["chars"]).replace(" ", "_")) +"' id='"+ str(editor["fields"][i]["id"] if "id" in editor["fields"][i] else header["value"][i].lower().translate(editor["chars"]).replace(" ", "_")) +"_0' value='0'/>"+ str(editor["fields"][i]["label"][2]) +"</label>\n"\
                                            "</div>\n"
                            # Return an Type Error.
                            else:
                                raise TypeError("Parameter (editor fields 'lable') must be a list if the (type) is equal to (radio).")
                        # Create an Field with type date.
                        elif editor["fields"][i]["type"] == "date":
                            # Create an Field with type date.
                            table += "<div class='form-group'>\n"\
                                        "<label for='"+ str(editor["fields"][i]["id"] if "id" in editor["fields"][i] else header["value"][i].lower().translate(editor["chars"]).replace(" ", "_")) +"' class='col-form-label'>"+ str(editor["fields"][i]["label"]) +"</label>\n"\
                                        "<input type='date' id='"+ str(editor["fields"][i]["id"] if "id" in editor["fields"][i] else header["value"][i].lower().translate(editor["chars"]).replace(" ", "_")) +"' name='"+ str(editor["fields"][i]["name"] if "name" in editor["fields"][i] else header["value"][i].lower().translate(editor["chars"]).replace(" ", "_")) +"' class='form-control "+ str(editor["fields"][i]["class"] if "class" in editor["fields"][i] else "") +"' "+ str("disabled" if "disabled" in editor["fields"][i] else "") +" "+ str("required" if "required" in editor["fields"][i] else "") +"/>\n"
                        else:
                            # Create an Field with type text.
                            table += "<div class='form-group'>\n"\
                                        "<label for='"+ str(editor["fields"][i]["id"] if "id" in editor["fields"][i] else header["value"][i].lower().translate(editor["chars"]).replace(" ", "_")) +"' class='col-form-label'>"+ str(editor["fields"][i]["label"]) +"</label>\n"\
                                        "<input type='text' id='"+ str(editor["fields"][i]["id"] if "id" in editor["fields"][i] else header["value"][i].lower().translate(editor["chars"]).replace(" ", "_")) +"' name='"+ str(editor["fields"][i]["name"] if "name" in editor["fields"][i] else header["value"][i].lower().translate(editor["chars"]).replace(" ", "_")) +"' class='form-control "+ str(editor["fields"][i]["class"] if "class" in editor["fields"][i] else "") +"' "+ str("disabled" if "disabled" in editor["fields"][i] else "") +" "+ str("required" if "required" in editor["fields"][i] else "") +" "+ str("hidden" if "hidden" in editor["fields"][i] and editor["fields"][i]["hidden"] else "") +"/>\n"
                    # There is no type set the default type.
                    else:
                        # Create an Field with type text.
                        table += "<div class='form-group'>\n"
                        
                        # Check if the field is hidden.
                        if "hidden" not in editor["fields"][i]:
                            table += "<label for='"+ str(editor["fields"][i]["id"] if "id" in editor["fields"][i] else header["value"][i].lower().translate(editor["chars"]).replace(" ", "_")) +"' class='col-form-label'>"+ str(editor["fields"][i]["label"]) +"</label>\n"\
                            
                        table += "<input type='text' id='"+ str(editor["fields"][i]["id"] if "id" in editor["fields"][i] else header["value"][i].lower().translate(editor["chars"]).replace(" ", "_")) +"' name='"+ str(editor["fields"][i]["name"] if "name" in editor["fields"][i] else header["value"][i].lower().translate(editor["chars"]).replace(" ", "_")) +"' class='form-control "+ str(editor["fields"][i]["class"] if "class" in editor["fields"][i] else "") +"' "+ str("disabled" if "disabled" in editor["fields"][i] else "") +" "+ str("required" if "required" in editor["fields"][i] else "") +" "+ str("hidden" if "hidden" in editor["fields"][i] and editor["fields"][i]["hidden"] else "") +"/>\n"
                    # Check if there is an required field.
                    if "required" in editor["fields"][i]:
                        table += "<div class='invalid-feedback'>\n"\
                                    ""+ str(editor["fields"][i]["label"]) +" eingeben.\n"\
                                "</div>\n"
                    # End of an Field.
                    table += "</div>\n"
                    continue
                # Create the Buttons.
                table += "<div class='form-group'>\n"\
                            "<button type='submit' class='btn btn-outline-success animation-on-hover float-right'>Speichern</button>\n"\
                            "<button type='button' class='btn btn-outline-danger animation-on-hover float-right mr-2' data-dismiss='modal'>Abbrechen</button>\n"\
                        "</div>\n"
                # End of Table Editor.
                table +=                "</div>\n"\
                                    "</div>\n"\
                                "</div>\n"\
                            "</myform>\n"\
                        "</div>\n"\
                    "</div>\n"\
                "</div>\n"
            except Exception as e:
                raise e
        # return the table.
        return table + "</table>\n"