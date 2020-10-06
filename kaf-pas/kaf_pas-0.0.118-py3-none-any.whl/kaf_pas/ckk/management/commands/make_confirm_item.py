import logging

from django.core.management import BaseCommand
from django.db import IntegrityError
from tqdm import tqdm

from isc_common.logger.Logger import Logger
from kaf_pas.ckk.models.item import Item, ItemManager
from kaf_pas.kd.models.documents_ext import DocumentManagerExt

logger = logging.getLogger(__name__)
logger.__class__ = Logger


class Command(BaseCommand):
    help = "Make confirmed Items"
    documentManagerExt = DocumentManagerExt(logger=logger)

    def handle(self, *args, **options):
        items = Item.objects.filter(props=~Item.props.confirmed)

        pbar = tqdm(total=items.count())
        # with transaction.atomic():
        for item in items:
            item.props |= Item.props.confirmed

            try:
                item.version = ItemManager.get_verstion(
                    STMP_1=item.STMP_1,
                    STMP_2=item.STMP_2,
                    props=item.props._value,
                    version=item.version
                )

                item.save()
            except IntegrityError:
                print(f'IntegrityError: {item}')
            else:
                pbar.update()

        pbar.close()
