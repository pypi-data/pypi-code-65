# -*- coding: utf-8 -*-
import sys

from halo import Halo

from suite_py.lib import logger
from suite_py.lib.handler.captainhook_handler import CaptainHook
from suite_py.lib.handler import prompt_utils


class Aggregator:
    def __init__(self, config, show_list, change):
        self._captainhook = CaptainHook(config)
        self._show_list = show_list
        self._change = change

    def run(self):
        if self._show_list:
            self._list_aggregators()
            return

        if self._change:
            aggregator = self._select_aggregator()
            address = prompt_utils.ask_questions_input(
                "Inserisci l'indirizzo del QA o premi invio per impostare l'indirizzo di staging: ",
                default_text="staging.prima.it",
            )

            change_request = self._captainhook.change_aggregator(aggregator, address)
            self._handle_captainhook_response(change_request, aggregator, address)

    def _handle_captainhook_response(self, request, aggregator, address):
        if request.status_code == 200:
            change_request = request.json()
            if change_request["success"]:
                logger.info(
                    f"Puntamento aggiornato! Ora {aggregator} punta a {address}"
                )
            else:
                cases = {
                    "cloudflare_error": "Errore durante la chiamata a Cloudflare.",
                    "unknown_dns_record": "Impossibile trovare il record DNS associato all'aggregatore.",
                    "unknown_aggregator": "Aggregatore non trovato.",
                    "invalid_qa_address": "L'indirizzo del QA non rispetta i requisiti.",
                }
                logger.error(cases.get(change_request["error"], "errore sconociuto"))
        else:
            logger.error("Si è verificato un errore su Captainhook.")

    def _select_aggregator(self):
        with Halo(text="Loading aggregators...", spinner="dots", color="magenta"):
            choices = [
                {"name": agg["name"], "value": agg["name"]}
                for agg in self._captainhook.aggregators().json()
            ]
        if choices:
            choices.sort(key=lambda x: x["name"])
            return prompt_utils.ask_choices("Seleziona aggregatore: ", choices)

        logger.error("Non ci sono aggregatori su Captainhook.")
        sys.exit(-1)

    def _list_aggregators(self):
        with Halo(text="Loading...", spinner="dots", color="magenta"):
            aggregators = self._captainhook.aggregators()

        if aggregators.status_code != 200:
            logger.error("Impossibile recuperare la lista degli aggregatori.")
            return

        message = "\n".join(
            [f"* {a['name']} => {a['content']:>12}" for a in aggregators.json()]
        )

        logger.info(f"\nAggregatori disponibili:\n{message}\n")
