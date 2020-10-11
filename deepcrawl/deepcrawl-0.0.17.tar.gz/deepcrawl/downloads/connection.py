"""
Downloads Connection
====================
"""

from typing import List, Union, Optional

from requests import Response

from deepcrawl.api import ApiConnection
from deepcrawl.api.api_endpoints import get_api_endpoint
from deepcrawl.downloads.download import DeepCrawlReportDownload
from .download import DeepCrawlCrawlDownloads


class DownloadConnection(ApiConnection):
    """
    CRAWL DOWNLOADS
        * endpoint: /accounts/{account_id}/projects/{project_id}/crawls/{crawl_id}/downloads
        * http methods: GET
        * methods: get_downloads

    REPORT DOWNLOAD
        * endpoint: /accounts/{account_id}/projects/{project_id}/crawls/{crawl_id}/reports/{report_id}/downloads
        * http method: GET, POST
        * methods: get_report_downloads, create_report_download

        - endpoint: /accounts/{account_id}/projects/{project_id}/crawls/{crawl_id}/reports/{report_id}/downloads/{report_download_id}
        - http method: GET, DELETE
        - methods: get_report_download, delete_report_download
    """

    """
    CRAWL DOWNLOADS
    """

    def get_crawl_downloads(
            self, account_id: Union[int, str], project_id: Union[int, str], crawl_id: Union[int, str],
            filters: Optional[dict] = None, **kwargs
    ) -> List[DeepCrawlCrawlDownloads]:
        """Get crawl downloads

        >>> connection.get_crawl_downloads(0, 1, 2)
        [[6] Report Template_11_basic - csv_zip (draft),
        [7] Report Template_12_basic - csv_zip (draft)]

        :param account_id: account id
        :type account_id: int or str
        :param project_id: project id
        :type project_id: int or str
        :param crawl_id: crawl id
        :type crawl_id: int or str
        :param filters: filters dict
        :type filters: dict
        :param kwargs: extra arguments like pagination arguments
        :type kwargs: dict
        :return: Requested crawl downloads
        :rtype: list
        """
        endpoint_url: str = get_api_endpoint(
            endpoint='crawl_downloads',
            account_id=account_id, project_id=project_id, crawl_id=crawl_id
        )
        downloads: List[dict] = self.get_paginated_data(url=endpoint_url, method='get', filters=filters, **kwargs)

        list_of_downloads = []
        for download in downloads:
            list_of_downloads.append(
                DeepCrawlCrawlDownloads(
                    download_data=download, account_id=account_id, project_id=project_id, crawl_id=crawl_id)
            )
        return list_of_downloads

    """
    REPORT DOWNLOAD
    """

    def create_report_download(
            self, account_id: Union[int, str], project_id: Union[int, str], crawl_id: Union[int, str],
            report_id: str, download_data: dict
    ) -> DeepCrawlReportDownload:
        """Create report download

        .. code-block::

            download_data = {
                "q": str,
                "output_type": str
            }

        >>> connection.create_report_download(0, 1, 2, "4:duplicate_body_content:basic", download_data)
        <deepcrawl.downloads.download.DeepCrawlReportDownload at 0x108a20600>

        :param account_id: account id
        :type account_id: int or str
        :param project_id: project id
        :type project_id: int or str
        :param crawl_id: crawl id
        :type crawl_id: int or str
        :param report_id: report id
        :type report_id: str
        :param download_data: Download configuration
        :type download_data: dict
        :return: Created download
        :rtype: DeepCrawlReportDownload
        """
        url: str = get_api_endpoint(
            "report_downloads",
            account_id=account_id, project_id=project_id, crawl_id=crawl_id, report_id=report_id
        )
        response = self.dc_request(url=url, method='post', json=download_data)
        return DeepCrawlReportDownload(
            account_id=account_id, project_id=project_id, crawl_id=crawl_id,
            report_id=report_id, download_data=response.json()
        )

    def get_report_download(
            self, account_id: Union[int, str], project_id: Union[int, str], crawl_id: Union[int, str],
            report_id: str, report_download_id: Union[int, str]
    ) -> DeepCrawlReportDownload:
        """Get report download

        >>> connection.get_report_download(0, 1, 2, "duplicate_body_content:basic", 6)
        <deepcrawl.downloads.download.DeepCrawlReportDownload at 0x108a20600>

        :param account_id: account id
        :type account_id: int or str
        :param project_id: project id
        :type project_id: int or str
        :param crawl_id: crawl id
        :type crawl_id: int or str
        :param report_id: report id
        :type report_id: str
        :param report_download_id: report download id
        :type report_download_id: int
        :return: Requested report download
        :rtype: DeepCrawlReportDownload
        """
        request_url: str = get_api_endpoint(
            "report_download",
            account_id=account_id, project_id=project_id, crawl_id=crawl_id,
            report_id=report_id, report_download_id=report_download_id
        )
        response = self.dc_request(url=request_url, method='get')
        return DeepCrawlReportDownload(
            account_id=account_id, project_id=project_id, crawl_id=crawl_id, report_id=report_id,
            download_data=response.json()
        )

    def delete_report_download(
            self, account_id: Union[int, str], project_id: Union[int, str], crawl_id: Union[int, str],
            report_id: str, report_download_id: Union[int, str]
    ) -> Response:
        """Delete report download

        >>> response = connection.delete_report_download(0, 1, 2, "duplicate_body_content:basic", 6)
        >>> response.status_code
        204

        :param account_id: account id
        :type account_id: int or str
        :param project_id: project id
        :type project_id: int or str
        :param crawl_id: crawl id
        :type crawl_id: int or str
        :param report_id: report id
        :type report_id: str
        :param report_download_id: report download id
        :type report_download_id: int
        :return: HTTP 204 No Content
        """
        request_url: str = get_api_endpoint(
            "report_download",
            account_id=account_id, project_id=project_id, crawl_id=crawl_id,
            report_id=report_id, report_download_id=report_download_id
        )
        return self.dc_request(url=request_url, method='delete')

    def get_report_downloads(
            self, account_id: Union[int, str], project_id: Union[int, str], crawl_id: Union[int, str],
            report_id: str, filters: Optional[dict] = None, **kwargs
    ) -> List[DeepCrawlReportDownload]:
        """Get report downloads

        >>> connection.get_report_downloads(0, 1, 2)
        [<deepcrawl.downloads.download.DeepCrawlReportDownload at 0x108a20600>,
        <deepcrawl.downloads.download.DeepCrawlReportDownload at 0x208n20701>]

        :param account_id: account id
        :type account_id: int or str
        :param project_id: project id
        :type project_id: int or str
        :param crawl_id: crawl id
        :type crawl_id: int or str
        :param report_id: report id
        :type report_id: str
        :param filters: filters dict
        :type filters: dict
        :param kwargs: extra arguments like pagination arguments
        :type kwargs: dict
        :return: Requested report downloads
        :rtype: list
        """
        request_url: str = get_api_endpoint(
            "report_downloads",
            account_id=account_id, project_id=project_id, crawl_id=crawl_id,
            report_id=report_id
        )
        downloads_response: List[dict] = self.get_paginated_data(request_url, method='get', filters=filters, **kwargs)

        list_of_downloads = []
        for download in downloads_response:
            list_of_downloads.append(DeepCrawlReportDownload(
                project_id=project_id, account_id=account_id, crawl_id=crawl_id,
                report_id=report_id, download_data=download
            ))
        return list_of_downloads
