import logging

from django.core.management import BaseCommand
from django.db import transaction
from tqdm import tqdm

from isc_common.auth.models.user import User
from isc_common.logger.Logger import Logger
from kaf_pas.kd.models.cdws import Cdws
from kaf_pas.kd.models.documents import Documents
from kaf_pas.kd.models.documents_ext import DocumentManagerExt

logger = logging.getLogger(__name__)
logger.__class__ = Logger


class Command(BaseCommand):
    help = "Test Make CDW"
    documentManagerExt = DocumentManagerExt(logger=logger)

    def handle(self, *args, **options):
        cdws = [cdw for cdw in Cdws.objects.filter(props=~Documents.props.beenItemed) if cdw.file_document.lower().find('мусор') == -1]

        with transaction.atomic():
            pbar = tqdm(total=len(cdws))
            for document in cdws:
                self.documentManagerExt.make_cdw(document=document, user=User.objects.get(id=2))
                pbar.update()
        pbar.close()
