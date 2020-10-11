"""
Report
======
"""
from typing import Union, Optional, List

from requests import Response

import deepcrawl
from deepcrawl.downloads.download import DeepCrawlReportDownload
from deepcrawl.reports.report_row import DeepCrawlReportRow
from deepcrawl.utils import ImmutableAttributesMixin

report_extra_fields = (
    'id',
    'account_id',
    'project_id',
    'crawl_id',
    'report_rows',
    'downloads'
)

report_mutable_fields = report_extra_fields + (
    'report_type',
    'report_template',
    'total_rows',
    'basic_total',
    'removed_total',
    'added_total',
    'missing_total',
    'change_weight',
    'total_weight',
    'beta',
)

report_immutable_fields = (
    '_datasource_href',
    '_report_template_href',
    '_recent_report_trend_href',
    '_account_href',
    '_project_href',
    '_crawl_href',
    '_report_type_href',
    '_href',
    '_href_alt',
    '_report_downloads_href',
    '_report_rows_href',
    '_statistics_href',
    '_issues_href',
    '_added_report_href',
    '_added_report_href_alt',
    '_basic_report_href',
    '_basic_report_href_alt',
    '_missing_report_href',
    '_missing_report_href_alt',
)

report_fields = report_mutable_fields + report_immutable_fields


class DeepCrawlReport(ImmutableAttributesMixin):
    """
    Report class
    """
    __slots__ = report_fields

    mutable_attributes = report_mutable_fields

    def __init__(
            self, account_id: Union[int, str], project_id: Union[int, str], crawl_id: Union[int, str], report_data: dict
    ):
        # relations
        self.id = report_data.get("id")
        self.account_id = account_id
        self.project_id = project_id
        self.crawl_id = crawl_id
        self.report_rows = []
        self.downloads = []

        # attributes
        self.report_type = report_data.get('report_type')
        self.report_template = report_data.get('report_template')
        self.total_rows = report_data.get('total_rows')
        self.basic_total = report_data.get('basic_total')
        self.removed_total = report_data.get('removed_total')
        self.added_total = report_data.get('added_total')
        self.missing_total = report_data.get('missing_total')
        self.change_weight = report_data.get('change_weight')
        self.total_weight = report_data.get('total_weight')
        self.beta = report_data.get('beta')

        self._datasource_href = report_data.get('_datasource_href')
        self._report_template_href = report_data.get('_report_template_href')
        self._recent_report_trend_href = report_data.get('_recent_report_trend_href')
        self._account_href = report_data.get('_account_href')
        self._project_href = report_data.get('_project_href')
        self._crawl_href = report_data.get('_crawl_href')
        self._report_type_href = report_data.get('_report_type_href')
        self._href = report_data.get('_href')
        self._href_alt = report_data.get('_href_alt')
        self._report_downloads_href = report_data.get('_report_downloads_href')
        self._report_rows_href = report_data.get('_report_rows_href')
        self._statistics_href = report_data.get('_statistics_href')
        self._issues_href = report_data.get('_issues_href')
        self._added_report_href = report_data.get('_added_report_href')
        self._added_report_href_alt = report_data.get('_added_report_href_alt')
        self._basic_report_href = report_data.get('_basic_report_href')
        self._basic_report_href_alt = report_data.get('_basic_report_href_alt')
        self._missing_report_href = report_data.get('_missing_report_href')
        self._missing_report_href_alt = report_data.get('_missing_report_href_alt')

        super(DeepCrawlReport, self).__init__()

    def __repr__(self) -> str:
        return f"[{self.account_id} {self.project_id} {self.crawl_id}] {self.id}"

    def __str__(self) -> str:
        return f"[{self.account_id} {self.project_id} {self.crawl_id}] {self.id}"

    @property
    def to_dict_mutable_fields(self) -> dict:
        """
        :return: dictionary with the mutable fields
        :rtype: dict
        """
        return {x: getattr(self, x, None) for x in report_mutable_fields}

    @property
    def to_dict_immutable_fields(self) -> dict:
        """
        :return: dictionary with the immutable fields
        :rtype: dict
        """
        return {x: getattr(self, x, None) for x in report_immutable_fields}

    def load_report_rows(
            self, connection: 'deepcrawl.DeepCrawlConnection' = None, filters: Optional[dict] = None, **kwargs
    ) -> List[DeepCrawlReportRow]:
        """Loads reports rows into current instance

        >>> self.load_report_rows()
        [<deepcrawl.reports.report_row.DeepCrawlReportRow at 0x108a20600>,
        <deepcrawl.reports.report_row.DeepCrawlReportRow at 0x148a25670>]
        >>> self.report_rows
        [<deepcrawl.reports.report_row.DeepCrawlReportRow at 0x108a20600>,
        <deepcrawl.reports.report_row.DeepCrawlReportRow at 0x148a25670>]

        :param filters: filters dict
        :type filters: dict
        :param kwargs: extra arguments like pagination arguments
        :type kwargs: dict
        :param connection: connection
        :type connection: deepcrawl.DeepCrawlConnection
        :return: list of report rows
        :rtype: list
        """
        connection = connection or deepcrawl.DeepCrawlConnection.get_instance()
        self.report_rows = connection.get_report_rows(
            self.account_id, self.project_id, self.crawl_id, self.id, filters=filters, **kwargs
        )
        return self.report_rows

    def load_downloads(
            self, connection: 'deepcrawl.DeepCrawlConnection' = None, filters: Optional[dict] = None, **kwargs
    ) -> List[DeepCrawlReportDownload]:
        """Loads reports downloads into current instance

        >>> self.load_downloads()
        [<deepcrawl.downloads.download.DeepCrawlReportDownload at 0x108a20600>,
        <deepcrawl.downloads.download.DeepCrawlReportDownload at 0x208n20701>]
        >>> self.downloads
        [<deepcrawl.downloads.download.DeepCrawlReportDownload at 0x108a20600>,
        <deepcrawl.downloads.download.DeepCrawlReportDownload at 0x208n20701>]

        :param filters: filters dict
        :type filters: dict
        :param kwargs: extra arguments like pagination arguments
        :type kwargs: dict
        :param connection: connection
        :type connection: deepcrawl.DeepCrawlConnection
        :return: list of reports
        :rtype: list
        """
        connection = connection or deepcrawl.DeepCrawlConnection.get_instance()
        self.downloads = connection.get_report_downloads(
            self.account_id, self.project_id, self.crawl_id, self.id,
            filters=filters, **kwargs
        )
        return self.downloads

    """
    REPORT ROWS
    """

    def get_report_row(
            self, report_row_id: Union[int, str], connection: 'deepcrawl.DeepCrawlConnection' = None
    ) -> DeepCrawlReportRow:
        """Get report row

        >>> self.get_report_row(1)
        <deepcrawl.reports.report_row.DeepCrawlReportRow at 0x108a20600>

        :param report_row_id: report row id
        :type report_row_id: int or str
        :param connection: connection
        :type connection: deepcrawl.DeepCrawlConnection
        :return: report row instance
        :rtype: DeepCrawlReportRow
        """
        connection = connection or deepcrawl.DeepCrawlConnection.get_instance()
        return connection.get_report_row(self.account_id, self.project_id, self.crawl_id, self.id, report_row_id)

    def get_report_rows(
            self, use_cache: bool = True,
            connection: 'deepcrawl.DeepCrawlConnection' = None, filters: Optional[dict] = None, **kwargs
    ) -> List[DeepCrawlReportRow]:
        """Get report rows for current instance

        * use_cache=True > get_report_rows will return cached report rows or will do a call to DeepCrawl if report_rows attribute is empty.
        * use_cache=False > get_report_rows will call DeepCrawl api and will override report_rows attribute.

        >>> self.get_report_rows()
        [<deepcrawl.reports.report_row.DeepCrawlReportRow at 0x108a20600>,
        <deepcrawl.reports.report_row.DeepCrawlReportRow at 0x148a25670>]

        :param use_cache:
        :type use_cache: bool
        :param filters: filters dict
        :type filters: dict
        :param kwargs: extra arguments like pagination arguments
        :type kwargs: dict
        :param connection: connection
        :type connection: deepcrawl.DeepCrawlConnection
        :return: List of report rows
        :rtype: list
        """
        connection = connection or deepcrawl.DeepCrawlConnection.get_instance()
        if self.report_rows and use_cache:
            return self.report_rows
        return self.load_report_rows(connection=connection, filters=filters, **kwargs)

    def get_report_row_count(
            self, connection: 'deepcrawl.DeepCrawlConnection' = None, filters: Optional[dict] = None
    ) -> str:
        """Get report row count

        >>> self.get_report_row_count()
        "2"

        :param filters: filters dict
        :type filters: dict
        :param connection: connection
        :type connection: deepcrawl.DeepCrawlConnection
        :return: Count of report row
        :rtype: str
        """
        connection = connection or deepcrawl.DeepCrawlConnection.get_instance()
        return connection.get_report_row_count(
            self.account_id, self.project_id, self.crawl_id, self.id, filters=filters
        )

    """
    REPORT DOWNLOADS
    """

    def create_report_download(
            self, download_data: dict, connection: 'deepcrawl.DeepCrawlConnection' = None
    ) -> DeepCrawlReportDownload:
        """Create report download

        .. code-block::

            download_data = {
                "q": str,
                "output_type": str
            }

        >>> self.create_report_download(download_data)
        <deepcrawl.downloads.download.DeepCrawlReportDownload at 0x108a20600>

        :param download_data: Download configuration
        :type download_data: dict
        :param connection: connection
        :type connection: deepcrawl.DeepCrawlConnection
        :return: Created download
        :rtype: DeepCrawlReportDownload
        :return:
        """
        connection = connection or deepcrawl.DeepCrawlConnection.get_instance()
        return connection.create_report_download(
            self.account_id, self.project_id, self.crawl_id, self.id, download_data
        )

    def get_report_download(
            self, report_download_id: Union[int, str], connection: 'deepcrawl.DeepCrawlConnection' = None
    ) -> DeepCrawlReportDownload:
        """Get report download

        >>> self.get_report_download(6)
        <deepcrawl.downloads.download.DeepCrawlReportDownload at 0x108a20600>

        :param report_download_id: report download id
        :type report_download_id: int
        :param connection: connection
        :type connection: deepcrawl.DeepCrawlConnection
        :return: Requested report download
        :rtype: DeepCrawlReportDownload
        """
        connection = connection or deepcrawl.DeepCrawlConnection.get_instance()
        return connection.get_report_download(
            self.account_id, self.project_id, self.crawl_id, self.id, report_download_id
        )

    def delete_report_download(
            self, report_download_id: Union[int, str], connection: 'deepcrawl.DeepCrawlConnection' = None
    ) -> Response:
        """Delete report download

        >>> response = self.delete_report_download(report_download_id)
        >>> response.status_code
        204

        :param report_download_id: report download id
        :type report_download_id: int
        :param connection: connection
        :type connection: deepcrawl.DeepCrawlConnection
        :return: HTTP 204 No Content
        """
        connection = connection or deepcrawl.DeepCrawlConnection.get_instance()
        return connection.delete_report_download(
            self.account_id, self.project_id, self.crawl_id, self.id, report_download_id
        )

    def get_report_downloads(
            self, use_cache: bool = True,
            connection: 'deepcrawl.DeepCrawlConnection' = None, filters: Optional[dict] = None, **kwargs
    ) -> List[DeepCrawlReportDownload]:
        """Get report downloads

        >>> self.get_report_downloads()
        [<deepcrawl.downloads.download.DeepCrawlReportDownload at 0x108a20600>,
        <deepcrawl.downloads.download.DeepCrawlReportDownload at 0x208n20701>]

        :param use_cache:
        :type use_cache: bool
        :param filters: filters dict
        :type filters: dict
        :param kwargs: extra arguments like pagination arguments
        :type kwargs: dict
        :param connection: connection
        :type connection: deepcrawl.DeepCrawlConnection
        :return: List of report rows
        :rtype: list
        """
        connection = connection or deepcrawl.DeepCrawlConnection.get_instance()
        if self.downloads and use_cache:
            return self.downloads
        return self.load_downloads(connection=connection, filters=filters, **kwargs)
