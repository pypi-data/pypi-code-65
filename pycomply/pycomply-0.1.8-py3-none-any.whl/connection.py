from requests import Session
from typing import List, Dict, Sequence
import inspect
from requests.packages.urllib3.util.retry import Retry

from requests.adapters import HTTPAdapter


class WebConnection(Session):
    def __init__(
        self,
        email,
        password,
        url="https://app.complyadvantage.com",
    ):
        super().__init__()
        self.url = url
        login_response = self.post(
            f"{url}/auth/login",
            json={
                "email": email,
                "password": password,
                "remember_me": False,
                "timezone": "Europe/Amsterdam",
            },
        )
        login_response.raise_for_status()
        self.headers.update(
            {"x-csrf-token": login_response.json()["data"]["csrf-token"]}
        )

    def delete_searches(self, search_ids: List[str]) -> Dict:
        response = self.post(
            f"{self.url}/data/searches/bulk-destroy", json={"searches": search_ids}
        )
        response.raise_for_status()
        return response.json()

    def get_tags(self):
        response = self.get(f"{self.url}/data/tags")
        response.raise_for_status()
        return response.json()["data"]

    def get_search(self, search_id):
        response = self.get(f"{self.url}/data/searches/{search_id}")
        response.raise_for_status()
        return response.json()["data"]

    def get_search_tags(self, search_id):
        data = self.get_search(search_id)
        return data["tags"]

    def create_search_tags(self, search_id, tags):
        """
        request payload: {searches: ["1601987800-5W0ZNMKQ"], tags: [{id: 3763, value: "tst"}, {id: 3709, value: "tst"}]}
        :param search_id:
        :param tags:
        :return:
        """
        response = self.post(
            f"{self.url}/data/searches/tags",
            json={"searches": [search_id], "tags": tags},
        )
        response.raise_for_status()
        return response.json()["data"]

    def delete_search_tag(self, search_id, tag_id):
        response = self.delete(f"{self.url}/data/searches/{search_id}/tags/{tag_id}")
        response.raise_for_status()
        return response.json()

    def get_searches(
        self, page=1, per_page=10, sort_by="created_at", sort_order="DESC"
    ):
        """
        {
           "code":200,
           "status":"success",
           "data":{
              "filters":{
                 "q":"\/data\/searches",
                 "page":"1",
                 "perPage":"1",
                 "sort_by":"created_at",
                 "sort_order":"DESC"
              },
              "searches":[
                 {
                    "id":123456789,
                    "name":"123456789-dc9dMXGG",
                    "status":"new",
                    "searcher_id":10000,
                    "assignee_id":10000,
                    "filters":{
                       "birth_year":1900,
                       "country_codes":["NL"],
                       "entity_type":"person",
                       "remove_deceased":0,
                       "sources":[],
                       "types":[
                          "sanction",
                          "warning",
                          "fitness-probity",
                          "pep",
                          "pep-class-1",
                          "pep-class-2",
                          "pep-class-3",
                          "pep-class-4"
                       ]
                    },
                    "match_status":"potential_match",
                    "risk_level":"unknown",
                    "search_term":"Max Jones",
                    "total_hits":2,
                    "created_at":"2020-10-14T14:45:38.062000",
                    "updated_at":"2020-10-14T14:45:38.062000",
                    "searcher":{
                       "id":10000,
                       "name":"Compliance"
                    },
                    "types":["pep-class-2", "fitness-probity","pep"],
                    "grouped_types":[
                       {"type":"sanction"},
                       {"type":"warning"},
                       {"type":"fitness-probity"},
                       {
                          "type":"pep",
                          "subtypes":["pep-class-1","pep-class-2","pep-class-3","pep-class-4"]
                       }
                    ],
                    "ref":{
                       "entity_statuses":[],
                       "client_ref":"abcdefgh-84b8-47dc-9db5-c0e0fc47889a"
                    },
                    "assignee":{
                       "id":10000,
                       "name":"Compliance"
                    },
                    "comments":[],
                    "is_monitored":false,
                    "monitored":{
                       "entity_changes":null,
                       "changed_at":[],
                       "has_changed":false,
                       "is_monitored":false,
                       "suspended_at":null
                    },
                    "tags":[
                       {
                          "id":1234567890,
                          "search_id":1234567890,
                          "name":"investor_url",
                          "color":"#f5d328",
                          "tag_id":1234,
                          "display":1,
                          "value":"https:\/\/google.nl\/",
                          "created_at":"2020-10-14T14:45:38.063000"
                       },
                       {
                          "id":0987654321,
                          "search_id":987654321,
                          "name":"user_url",
                          "color":"#dcbd23",
                          "tag_id":4321,
                          "display":1,
                          "value":"https:\/\/google.nl\/",
                          "created_at":"2020-10-14T14:45:38.063000"
                       }
                    ]
                 }
              ],
              "hasNextPage":true
           }
        }

        :param page:
        :param per_page:
        :param sort_by:
        :param sort_order:
        :return:
        """
        response = self.get(
            f"{self.url}/data/searches",
            params={
                "page": page,
                "perPage": per_page,
                "sort_by": sort_by,
                "sort_order": sort_order,
            },
        )
        response.raise_for_status()
        return response.json()["data"]

    def get_searches_count(
        self, page=1, per_page=10, sort_by="created_at", sort_order="DESC"
    ):
        """
        response {"code":200,"status":"success","data":{"total_searches":8659,"total_pages":866,"per_page":"10","current_page":"1"}}
        :param page:
        :param per_page:
        :param sort_by:
        :param sort_order:
        :return:
        """
        response = self.get(
            f"{self.url}/data/searches/count",
            params={
                "page": page,
                "perPage": per_page,
                "sort_by": sort_by,
                "sort_order": sort_order,
            },
        )
        response.raise_for_status()
        return response.json()["data"]


class ApiConnection(Session):
    def __init__(
        self,
        key,
        url="https://api.complyadvantage.com",
    ):
        super().__init__()
        self.url = url
        self.headers.update({"Authorization": f"Token {key}"})

        # Mount retry adapter for both http and https usage
        retry_strategy = Retry(
            total=3,
            backoff_factor=10,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
        )
        retry_adapter = HTTPAdapter(max_retries=retry_strategy)
        self.mount("https://", retry_adapter)
        self.mount("http://", retry_adapter)

    def get_users(self) -> Sequence[Dict]:
        """
        https://docs.complyadvantage.com/api-docs/#get-users

        :return:
        """
        response = self.get(f"{self.url}/users")
        response.raise_for_status()
        return response.json()["content"]["data"]

    def create_search(
        self,
        search_term: str = None,
        client_ref: str = None,
        search_profile: str = None,
        fuzziness: float = 0.5,
        offset: int = 0,
        limit: int = 100,
        filters: dict = None,
        tags: dict = None,
        share_url: int = 0,
        country_codes: List[str] = None,
        exact_match: bool = False,
    ) -> dict:
        """
        https://docs.complyadvantage.com/api-docs/#post-searches

        :param search_term: (required, max 255 characters) A string representing the name of the entity or an Object
        :param client_ref: (optional) Your reference for this person/entity for which you are searching. Used for tracking searches and auto-whitelisting recurring results
        :param search_profile: (optional) The slug of any of your previously created search profiles, which can be found in the main platform UI for search profiles
        :param fuzziness: (optional) Determines how closely the returned results must match the supplied name. Overridden by exact_match
        :param offset: (optional) Match results from the database, starting from the offset value
        :param limit: (optional) Match results from the database, taking up to this many matches each search
        :param filters: (optional) Specify filters within the search to narrow down the results. These are specified below, and are all optional
        :param tags: (optional) Object of name => value pairs (name must be string), must be existing tags
        :param share_url: (optional) Include a shareable URL to access search publicly
        :param country_codes: (optional) Array of ISO 3166-1 alpha-2 strings. Results are filtered by the entity nationality or country of residence
        :param exact_match: (optional) Exact match disables all standard and optional matching behaviours (Honorifics, affixes, initials, glued name, name variation, equivalent names, extra words in entity,...) 0% fuzziness disables 1 letter typo matching but keeps all other matching behaviours (standard and optional)
        :return:
        """
        argspec = inspect.getargvalues(inspect.currentframe())
        search_data = {
            k: v for (k, v) in argspec.locals.items() if v is not None and k != "self"
        }
        response = self.post(f"{self.url}/searches", json=search_data)
        response.raise_for_status()
        return response.json()["content"]["data"]

    def get_searches(
        self,
        search_term: str = None,
        submitted_term: str = None,
        assignee_id: int = None,
        client_ref: str = None,
        searcher_id: int = None,
        risk_level: str = None,
        created_at_from: str = None,
        created_at_to: str = None,
        sort_by: str = "id",
        sort_dir: str = "DESC",
        per_page: int = 100,
        page: int = 1,
        tags: str = None,
        monitored: str = None,
    ) -> Sequence[Dict]:
        """
        https://docs.complyadvantage.com/api-docs/#get-searches

        :param search_term: Searches that match search term (3 characters min)
        :param submitted_term: Show searches where the term is unsanitised and includes symbols and punctuation marks
        :param assignee_id: Show searches assigned to a specific user
        :param client_ref:
        :param searcher_id: Show searches performed by a specific user
        :param risk_level: Show searches where the risk level is one of the specified options: ('low', 'medium', 'high', 'unknown'). Use commas to separate multiple options, eg &risk_level=medium,high
        :param created_at_from: Searches made from date (yyyy-mm-dd)
        :param created_at_to: Searches made to date (yyyy-mm-dd)
        :param sort_by: One of 'id', 'created_at', 'updated_at', 'assignee_id', 'searcher_id'
        :param sort_dir: One of 'ASC, 'DESC'
        :param per_page: Number of searches to return per "page" (integer, max 100)
        :param page: Which page to fetch (integer)
        :param tags: Searches registered against given tags, comma separated represented as 'name:value', eg 'internal_ref:1234' or internal_ref:1234,t_type:custom'
        :param monitored: Searches with a specific monitored status, eg. suspended for suspended searches, un-suspended for actively monitored searches and false for searches which are not monitored
        :return:
        """
        argspec = inspect.getargvalues(inspect.currentframe())
        search_params = {
            k: v for (k, v) in argspec.locals.items() if v is not None and k != "self"
        }
        response = self.get(f"{self.url}/searches", params=search_params)
        response.raise_for_status()
        return response.json()["content"]["data"]

    def get_search(self, search_id: str = None, share_url: int = 0) -> dict:
        """
        https://docs.complyadvantage.com/api-docs/#get-searches-id

        :param search_id: Either the numeric search ID, or the search REF
        :param share_url: 1 or 0 - include a shareable URL in response.
        :return:
        """
        response = self.get(
            f"{self.url}/searches/{search_id}", params={share_url: share_url}
        )
        response.raise_for_status()
        return response.json()["content"]["data"]

    def get_search_certificate(self, search_id: str = None):
        """
        https://docs.complyadvantage.com/api-docs/#get-searches-id-certificate

        :param search_id: Either the numeric search ID, or the search REF
        :return:
        """
        response = self.get(f"{self.url}/searches/{search_id}/certificate")
        response.raise_for_status()
        return response.content

    def get_search_details(self, search_id: str = None, share_url: int = 0) -> dict:
        """
        https://docs.complyadvantage.com/api-docs/#get-searches-id-details

        :param search_id: Either the numeric search ID, or the search REF
        :param share_url: 1 or 0 - include a shareable URL in response.
        :return:
        """
        response = self.get(
            f"{self.url}/searches/{search_id}/details",
            params={share_url: share_url},
        )
        response.raise_for_status()
        return response.json()["content"]["data"]

    def update_search(
        self,
        search_id: str = None,
        match_status: str = None,
        risk_level: str = None,
        assignee_id: int = None,
        tags: dict = None,
    ):
        """
        https://docs.complyadvantage.com/api-docs/#patch-searches-id

        :param search_id: Either the numeric search ID, or the search REF
        :param match_status: One of 'unknown', 'no_match', 'potential_match', 'false_positive', 'true_positive', 'true_positive_approve', 'true_positive_reject'
        :param risk_level:One of 'low', 'medium', 'high', 'unknown'
        :param assignee_id: The ID of the user to whom the case should be assigned
        :param tags: Object of name => value pairs ( name must be string ), must be existing tags
        :return:
        """
        argspec = inspect.getargvalues(inspect.currentframe())
        request_data = {
            k: v
            for (k, v) in argspec.locals.items()
            if v is not None and k not in ["self", "search_id"]
        }
        response = self.patch(
            f"{self.url}/searches/{search_id}",
            json=request_data,
        )
        response.raise_for_status()
        return response.json()["content"]["data"]

    def update_search_entities(
        self,
        search_id: str = None,
        entities: List[str] = None,
        match_status: str = None,
        risk_level: str = None,
        is_whitelisted: bool = None,
    ):
        """
        https://docs.complyadvantage.com/api-docs/#patch-searches-id-entities

        :param search_id: Either the numeric search ID, or the search REF
        :param entities: Array of entity ids to be updated (list of strings)
        :param match_status: One of 'no_match', 'false_positive', 'potential_match', 'true_positive','unknown'
        :param risk_level: One of 'low', 'medium', 'high', 'unknown'
        :param is_whitelisted: true or false
        :return:
        """
        argspec = inspect.getargvalues(inspect.currentframe())
        request_data = {
            k: v
            for (k, v) in argspec.locals.items()
            if v is not None and k not in ["self", "search_id"]
        }
        response = self.patch(
            f"{self.url}/searches/{search_id}/entities",
            json=request_data,
        )
        response.raise_for_status()
        return response.json()["content"]["data"]

    def get_monitors(self, search_id: str = None) -> dict:
        """
        https://docs.complyadvantage.com/api-docs/#get-searches-id-monitors

        :param search_id: Either the numeric search ID, or the search REF
        """
        response = self.get(f"{self.url}/searches/{search_id}/monitors")
        response.raise_for_status()
        return response.json()["content"]

    def update_monitors(
        self, search_id: str = None, is_monitored: bool = None, monitored_by: int = None
    ) -> dict:
        """
        https://docs.complyadvantage.com/api-docs/#patch-searches-id-monitors

        :param search_id: Either the numeric search ID, or the search REF
        :param is_monitored: Start on true and stop on false. For monitored searches, the original search will be updated with the latest results from monitor runs.
        :param monitored_by: (optional) The ID of the user who will start/stop monitoring (please note if monitored_by is not provided all users will be affected )
        """
        argspec = inspect.getargvalues(inspect.currentframe())
        request_data = {
            k: v
            for (k, v) in argspec.locals.items()
            if v is not None and k not in ["self", "search_id"]
        }
        response = self.patch(
            f"{self.url}/searches/{search_id}/monitors",
            json=request_data,
        )
        response.raise_for_status()
        return response.json()["content"]

    def get_monitor_updates(self, search_id: str = None, date: str = None) -> dict:
        """
        https://docs.complyadvantage.com/api-docs/#get-searches-id-monitor-differences

        :param search_id: Either the numeric search ID, or the search REF
        :param date: (optional) The reference date format: yyyy-mm-dd if missing, the current day will be used
        :return:
        """
        argspec = inspect.getargvalues(inspect.currentframe())
        search_params = {
            k: v
            for (k, v) in argspec.locals.items()
            if v is not None and k not in ["self", "search_id"]
        }
        response = self.get(
            f"{self.url}/searches/{search_id}/monitors/differences",
            params=search_params,
        )
        response.raise_for_status()
        return response.json()["content"]

    def get_comment(self, search_id: str = None) -> dict:
        """
        https://docs.complyadvantage.com/api-docs/#get-searches-id-comments

        :param search_id: Either the numeric search ID, or the search REF
        :return:
        """
        response = self.get(
            f"{self.url}/searches/{search_id}/comments",
        )
        response.raise_for_status()
        return response.json()["content"]

    def create_comment(
        self, search_id: str = None, comment: str = None, entity_id: str = None
    ) -> bool:
        """
        https://docs.complyadvantage.com/api-docs/#post-searches-id-comments

        :param search_id: Either the numeric search ID, or the search REF
        :param comment: The comment that will be added
        :param entity_id: The entity id (required for adding comment on entity)
        """
        argspec = inspect.getargvalues(inspect.currentframe())
        request_data = {
            k: v
            for (k, v) in argspec.locals.items()
            if v is not None and k not in ["self", "search_id"]
        }
        response = self.post(
            f"{self.url}/searches/{search_id}/comments", json=request_data
        )
        response.raise_for_status()

        if response.status_code == 204:
            return True

        return False
