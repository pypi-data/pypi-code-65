from collections import OrderedDict
from amaascore.config import DEFAULT_LOGGING, DEFAULT_ENVIRONMENT
from amaascore.assets.interface import AssetsInterface
from amaascore.transactions.transaction import Transaction
import logging


def create_transaction(
    asset_manager_id, rownum, rowdata, fixed_properties, assets_interface
):
    """Create Transaction object from row data."""
    row = Row(rownum, rowdata)
    # Add any data conversions
    for attr in ("asset", "asset_book", "counterparty_book"):
        if attr in row.attr_map and f"{attr}_id" not in row.attr_map:
            key = row.attr_map[attr]
            row[key + " Id"] = row[key]

    # FX asset creation support
    fx_type = row.attr_get("fx.type", "")
    if fx_type:
        raise ValueError("FX Mapper not supported yet")

    # Find asset_id by exchange code
    asset_ref = row.attr_get("asset_ref", "")
    if asset_ref and not row.attr_get("asset_id", ""):
        assets = assets_interface.search(
            asset_manager_id,
            asset_statuses=["Active"],
            reference_primary=True,
            reference_values=[asset_ref],
            fields=["asset_id", "currency"],
        )
        if len(assets) == 1:
            asset = assets[0]
            row["Asset Id"] = asset.get("asset_id")
            if "transaction_currency" not in row.attr_map:
                row["Transaction Currency"] = asset.get("currency")

            if "settlement_currency" not in row.attr_map:
                row["Settlement Currency"] = asset.get("currency")

        elif len(assets) > 1:
            logging.error(">1 assets found: %r", assets)
            msg = "Asset ref {} is ambiguous"
            raise ValidationError(
                msg.format(asset_ref), field=row.attr_map["asset_ref"]
            )
        else:
            msg = "Asset ref {} not recognised or asset not active"
            raise ValidationError(
                msg.format(asset_ref), field=row.attr_map["asset_ref"]
            )

    else:
        assets = assets_interface.search(
            asset_manager_id,
            asset_ids=[row.attr_get("asset_id")],
            asset_statuses=["Active"],
            fields=["asset_id", "currency"],
        )
        if len(assets) == 1:
            asset = assets[0]
            if "transaction_currency" not in row.attr_map:
                row["Transaction Currency"] = asset.get("currency")

            if "settlement_currency" not in row.attr_map:
                row["Settlement Currency"] = asset.get("currency")

        else:
            # will probably blow up later when asset is missing
            logging.warning(
                "No single asset for asset_id=%s: %r", row.attr_get("asset_id"), assets
            )

    # Merge the fields with one--many relationship and construct objects
    for attr, cls in Transaction.children().items():

        def attr_match(colname):
            return heading2attr(colname.split(".", 1)[0]) == attr

        matches = row.filter(attr_match)
        if matches:
            row[attr] = _construct_children(matches, cls)

    # Construct the Transaction objects
    fixed = {"asset_manager_id": int(asset_manager_id)}
    fixed.update(fixed_properties)
    transaction, op = _construct_transaction(row, fixed)
    logging.debug("Transaction object created: %r (%s)", transaction, op)
    return transaction, op


def heading2attr(s):
    """Convert row heading to attribute."""
    return s.strip().lower().replace(" ", "_")


def attr2heading(s):
    """Convert attribute to row heading."""
    return s.replace("_", " ").title()


def _construct_children(row, cls):
    try:
        return _do_construct_children(row, cls)
    except Exception as err:
        raise ValidationError(cls.__name__, exc=err)


def _do_construct_children(row, cls):
    logging.debug("Processing children for %s:\n%s", cls, row)

    itemargs = {}
    for colname, value in row.items():
        # Skip empty values
        if not value:
            continue

        parts = colname.split(".")
        # This is very permissive. Maybe too much, but hey, let's try our best.
        if len(parts) == 1:
            # Col "tags" = val -> [Tag(val, ...)]
            itemargs.setdefault("0", ArgSet()).a.append(value)
        elif len(parts) == 2:
            # Col "parties.partner" = val -> {partner: Party(val, ...)}
            itemargs.setdefault(attr2heading(parts[1]), ArgSet()).a.append(value)
        elif len(parts) == 3:
            # Col "charges.commission.*"
            key = heading2attr(parts[2])
            # Ignore unrecognised keys
            if key in cls.stored_attributes():
                itemargs.setdefault(attr2heading(parts[1]), ArgSet()).kw[key] = value
            else:
                logging.debug("Ignoring %r", colname)
        else:
            logging.debug("Ignoring %r", colname)

    logging.debug("%s arguments collected: %s", cls.__name__, itemargs)

    if all(k.isdigit() for k in itemargs):
        items = []
        for ind, argset in sorted((int(i), s) for i, s in itemargs.items()):
            obj = _build_object(cls, argset, ind)
            items.append(obj)
    else:
        items = {k: _build_object(cls, s, k) for k, s in itemargs.items()}

    return items


def _construct_transaction(row, fixed_properties):
    try:
        return _do_construct_transaction(row, fixed_properties)
    except Exception as err:
        raise ValidationError("Transaction", err)


def _do_construct_transaction(row, fixed_properties):
    logging.debug("Processing %s:\n%s", Transaction, row)

    kw = {}
    op = "new"
    kwnames = Transaction.stored_attributes() | set(Transaction.children())
    for colname, value in row.items():
        # Skip empty values
        if not value:
            continue

        keyname = heading2attr(colname)
        if keyname in fixed_properties:
            raise ValueError("{} is a fixed value".format(colname))

        if keyname in kwnames:
            kw[keyname] = row[colname]

        if keyname == "transaction_id":
            op = "amend"

    logging.debug("Transaction arguments collected: %s", kw)

    kw.update(fixed_properties)
    return Transaction(**kw), op


def _build_object(cls, argset, key):
    try:
        return cls(*argset.a, **argset.kw)
    except Exception as err:
        raise ValidationError(key, err)


class _Empty:
    pass


class Row(OrderedDict):
    """A thin wrapper around row data to store the name as well, and provide some convenience methods."""

    def __init__(self, name, *a, **kw):
        """
        Create a new row.

        :param name: The row name
        The remaining args are passed through to OrderedDict constructor.
        """
        self.name = name
        self.attr_map = {}
        super().__init__(*a, **kw)

    def filter(self, method):
        """
        Filter the row based on column names, returning a new row with only matching columns included.

        :param method: A function that should accept the column name and return True/False
        :returns: A new Row
        """
        matches = ((key, self[key]) for key in self if method(key))
        return type(self)(self.name, matches)

    def __setitem__(self, key, value, *a, **kw):
        """Set self[key] to value."""
        self.attr_map[heading2attr(key)] = key
        super().__setitem__(key, value, *a, **kw)

    def __delitem__(self, key, *a, **kw):
        """Delete self[key]."""
        try:
            del self.attr_map[heading2attr(key)]
        except KeyError:
            pass

        super().__delitem__(key, *a, **kw)

    def attr_get(self, attr, default=_Empty):
        """Get self[key] for attr."""
        if default is not _Empty and attr not in self.attr_map:
            return default

        return self[self.attr_map[attr]]


class ValidationError(Exception):
    """Imported document has failed validation on a particular item."""

    def __init__(self, msg="", exc=None, **kw):
        if isinstance(msg, Exception) and exc is None:
            exc = msg
            msg = ""

        if not msg and isinstance(exc, ValidationError):
            return exc

        msg = str(msg)
        if exc:
            assert isinstance(exc, Exception)
            msg = "{} {}".format(msg, exc)
            for k, v in vars(exc).items():
                setattr(self, k, v)

        for k, v in kw.items():
            setattr(self, k, v)

        super().__init__(msg)


class ArgSet(object):
    """Mutable collection of arguments."""

    def __init__(self, *a, **kw):
        self.a = list(a)
        self.kw = kw

    def __repr__(self):
        return "{}(*{}, **{})".format(type(self).__name__, self.a, self.kw)
