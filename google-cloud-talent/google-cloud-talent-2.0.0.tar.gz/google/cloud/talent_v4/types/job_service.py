# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import proto  # type: ignore


from google.cloud.talent_v4.types import common
from google.cloud.talent_v4.types import filters
from google.cloud.talent_v4.types import histogram
from google.cloud.talent_v4.types import job as gct_job
from google.protobuf import duration_pb2 as duration  # type: ignore
from google.protobuf import field_mask_pb2 as field_mask  # type: ignore
from google.rpc import status_pb2 as gr_status  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.talent.v4",
    manifest={
        "JobView",
        "CreateJobRequest",
        "GetJobRequest",
        "UpdateJobRequest",
        "DeleteJobRequest",
        "ListJobsRequest",
        "ListJobsResponse",
        "SearchJobsRequest",
        "SearchJobsResponse",
        "BatchCreateJobsRequest",
        "BatchUpdateJobsRequest",
        "BatchDeleteJobsRequest",
        "JobResult",
        "BatchCreateJobsResponse",
        "BatchUpdateJobsResponse",
        "BatchDeleteJobsResponse",
    },
)


class JobView(proto.Enum):
    r"""An enum that specifies the job attributes that are returned in the
    [MatchingJob.job][google.cloud.talent.v4.SearchJobsResponse.MatchingJob.job]
    or
    [ListJobsResponse.jobs][google.cloud.talent.v4.ListJobsResponse.jobs]
    fields.
    """
    JOB_VIEW_UNSPECIFIED = 0
    JOB_VIEW_ID_ONLY = 1
    JOB_VIEW_MINIMAL = 2
    JOB_VIEW_SMALL = 3
    JOB_VIEW_FULL = 4


class CreateJobRequest(proto.Message):
    r"""Create job request.

    Attributes:
        parent (str):
            Required. The resource name of the tenant under which the
            job is created.

            The format is "projects/{project_id}/tenants/{tenant_id}".
            For example, "projects/foo/tenants/bar".
        job (~.gct_job.Job):
            Required. The Job to be created.
    """

    parent = proto.Field(proto.STRING, number=1)

    job = proto.Field(proto.MESSAGE, number=2, message=gct_job.Job,)


class GetJobRequest(proto.Message):
    r"""Get job request.

    Attributes:
        name (str):
            Required. The resource name of the job to retrieve.

            The format is
            "projects/{project_id}/tenants/{tenant_id}/jobs/{job_id}".
            For example, "projects/foo/tenants/bar/jobs/baz".
    """

    name = proto.Field(proto.STRING, number=1)


class UpdateJobRequest(proto.Message):
    r"""Update job request.

    Attributes:
        job (~.gct_job.Job):
            Required. The Job to be updated.
        update_mask (~.field_mask.FieldMask):
            Strongly recommended for the best service experience.

            If
            [update_mask][google.cloud.talent.v4.UpdateJobRequest.update_mask]
            is provided, only the specified fields in
            [job][google.cloud.talent.v4.UpdateJobRequest.job] are
            updated. Otherwise all the fields are updated.

            A field mask to restrict the fields that are updated. Only
            top level fields of [Job][google.cloud.talent.v4.Job] are
            supported.
    """

    job = proto.Field(proto.MESSAGE, number=1, message=gct_job.Job,)

    update_mask = proto.Field(proto.MESSAGE, number=2, message=field_mask.FieldMask,)


class DeleteJobRequest(proto.Message):
    r"""Delete job request.

    Attributes:
        name (str):
            Required. The resource name of the job to be deleted.

            The format is
            "projects/{project_id}/tenants/{tenant_id}/jobs/{job_id}".
            For example, "projects/foo/tenants/bar/jobs/baz".
    """

    name = proto.Field(proto.STRING, number=1)


class ListJobsRequest(proto.Message):
    r"""List jobs request.

    Attributes:
        parent (str):
            Required. The resource name of the tenant under which the
            job is created.

            The format is "projects/{project_id}/tenants/{tenant_id}".
            For example, "projects/foo/tenants/bar".
        filter (str):
            Required. The filter string specifies the jobs to be
            enumerated.

            Supported operator: =, AND

            The fields eligible for filtering are:

            -  ``companyName`` (Required)
            -  ``requisitionId``
            -  ``status`` Available values: OPEN, EXPIRED, ALL. Defaults
               to OPEN if no value is specified.

            Sample Query:

            -  companyName = "projects/foo/tenants/bar/companies/baz"
            -  companyName = "projects/foo/tenants/bar/companies/baz"
               AND requisitionId = "req-1"
            -  companyName = "projects/foo/tenants/bar/companies/baz"
               AND status = "EXPIRED".
        page_token (str):
            The starting point of a query result.
        page_size (int):
            The maximum number of jobs to be returned per page of
            results.

            If
            [job_view][google.cloud.talent.v4.ListJobsRequest.job_view]
            is set to
            [JobView.JOB_VIEW_ID_ONLY][google.cloud.talent.v4.JobView.JOB_VIEW_ID_ONLY],
            the maximum allowed page size is 1000. Otherwise, the
            maximum allowed page size is 100.

            Default is 100 if empty or a number < 1 is specified.
        job_view (~.job_service.JobView):
            The desired job attributes returned for jobs in the search
            response. Defaults to
            [JobView.JOB_VIEW_FULL][google.cloud.talent.v4.JobView.JOB_VIEW_FULL]
            if no value is specified.
    """

    parent = proto.Field(proto.STRING, number=1)

    filter = proto.Field(proto.STRING, number=2)

    page_token = proto.Field(proto.STRING, number=3)

    page_size = proto.Field(proto.INT32, number=4)

    job_view = proto.Field(proto.ENUM, number=5, enum="JobView",)


class ListJobsResponse(proto.Message):
    r"""List jobs response.

    Attributes:
        jobs (Sequence[~.gct_job.Job]):
            The Jobs for a given company.
            The maximum number of items returned is based on
            the limit field provided in the request.
        next_page_token (str):
            A token to retrieve the next page of results.
        metadata (~.common.ResponseMetadata):
            Additional information for the API
            invocation, such as the request tracking id.
    """

    @property
    def raw_page(self):
        return self

    jobs = proto.RepeatedField(proto.MESSAGE, number=1, message=gct_job.Job,)

    next_page_token = proto.Field(proto.STRING, number=2)

    metadata = proto.Field(proto.MESSAGE, number=3, message=common.ResponseMetadata,)


class SearchJobsRequest(proto.Message):
    r"""The Request body of the ``SearchJobs`` call.

    Attributes:
        parent (str):
            Required. The resource name of the tenant to search within.

            The format is "projects/{project_id}/tenants/{tenant_id}".
            For example, "projects/foo/tenants/bar".
        search_mode (~.job_service.SearchJobsRequest.SearchMode):
            Mode of a search.

            Defaults to
            [SearchMode.JOB_SEARCH][google.cloud.talent.v4.SearchJobsRequest.SearchMode.JOB_SEARCH].
        request_metadata (~.common.RequestMetadata):
            Required. The meta information collected about the job
            searcher, used to improve the search quality of the service.
            The identifiers (such as ``user_id``) are provided by users,
            and must be unique and consistent.
        job_query (~.filters.JobQuery):
            Query used to search against jobs, such as
            keyword, location filters, etc.
        enable_broadening (bool):
            Controls whether to broaden the search when
            it produces sparse results. Broadened queries
            append results to the end of the matching
            results list.

            Defaults to false.
        histogram_queries (Sequence[~.histogram.HistogramQuery]):
            An expression specifies a histogram request against matching
            jobs.

            Expression syntax is an aggregation function call with
            histogram facets and other options.

            Available aggregation function calls are:

            -  ``count(string_histogram_facet)``: Count the number of
               matching entities, for each distinct attribute value.
            -  ``count(numeric_histogram_facet, list of buckets)``:
               Count the number of matching entities within each bucket.

            Data types:

            -  Histogram facet: facet names with format
               [a-zA-Z][a-zA-Z0-9\_]+.
            -  String: string like "any string with backslash escape for
               quote(")."
            -  Number: whole number and floating point number like 10,
               -1 and -0.01.
            -  List: list of elements with comma(,) separator surrounded
               by square brackets, for example, [1, 2, 3] and ["one",
               "two", "three"].

            Built-in constants:

            -  MIN (minimum number similar to java Double.MIN_VALUE)
            -  MAX (maximum number similar to java Double.MAX_VALUE)

            Built-in functions:

            -  bucket(start, end[, label]): bucket built-in function
               creates a bucket with range of [start, end). Note that
               the end is exclusive, for example, bucket(1, MAX,
               "positive number") or bucket(1, 10).

            Job histogram facets:

            -  company_display_name: histogram by
               [Job.company_display_name][google.cloud.talent.v4.Job.company_display_name].
            -  employment_type: histogram by
               [Job.employment_types][google.cloud.talent.v4.Job.employment_types],
               for example, "FULL_TIME", "PART_TIME".
            -  company_size: histogram by
               [CompanySize][google.cloud.talent.v4.CompanySize], for
               example, "SMALL", "MEDIUM", "BIG".
            -  publish_time_in_month: histogram by the
               [Job.posting_publish_time][google.cloud.talent.v4.Job.posting_publish_time]
               in months. Must specify list of numeric buckets in spec.
            -  publish_time_in_year: histogram by the
               [Job.posting_publish_time][google.cloud.talent.v4.Job.posting_publish_time]
               in years. Must specify list of numeric buckets in spec.
            -  degree_types: histogram by the
               [Job.degree_types][google.cloud.talent.v4.Job.degree_types],
               for example, "Bachelors", "Masters".
            -  job_level: histogram by the
               [Job.job_level][google.cloud.talent.v4.Job.job_level],
               for example, "Entry Level".
            -  country: histogram by the country code of jobs, for
               example, "US", "FR".
            -  admin1: histogram by the admin1 code of jobs, which is a
               global placeholder referring to the state, province, or
               the particular term a country uses to define the
               geographic structure below the country level, for
               example, "CA", "IL".
            -  city: histogram by a combination of the "city name,
               admin1 code". For example, "Mountain View, CA", "New
               York, NY".
            -  admin1_country: histogram by a combination of the "admin1
               code, country", for example, "CA, US", "IL, US".
            -  city_coordinate: histogram by the city center's GPS
               coordinates (latitude and longitude), for example,
               37.4038522,-122.0987765. Since the coordinates of a city
               center can change, customers may need to refresh them
               periodically.
            -  locale: histogram by the
               [Job.language_code][google.cloud.talent.v4.Job.language_code],
               for example, "en-US", "fr-FR".
            -  language: histogram by the language subtag of the
               [Job.language_code][google.cloud.talent.v4.Job.language_code],
               for example, "en", "fr".
            -  category: histogram by the
               [JobCategory][google.cloud.talent.v4.JobCategory], for
               example, "COMPUTER_AND_IT", "HEALTHCARE".
            -  base_compensation_unit: histogram by the
               [CompensationInfo.CompensationUnit][google.cloud.talent.v4.CompensationInfo.CompensationUnit]
               of base salary, for example, "WEEKLY", "MONTHLY".
            -  base_compensation: histogram by the base salary. Must
               specify list of numeric buckets to group results by.
            -  annualized_base_compensation: histogram by the base
               annualized salary. Must specify list of numeric buckets
               to group results by.
            -  annualized_total_compensation: histogram by the total
               annualized salary. Must specify list of numeric buckets
               to group results by.
            -  string_custom_attribute: histogram by string
               [Job.custom_attributes][google.cloud.talent.v4.Job.custom_attributes].
               Values can be accessed via square bracket notations like
               string_custom_attribute["key1"].
            -  numeric_custom_attribute: histogram by numeric
               [Job.custom_attributes][google.cloud.talent.v4.Job.custom_attributes].
               Values can be accessed via square bracket notations like
               numeric_custom_attribute["key1"]. Must specify list of
               numeric buckets to group results by.

            Example expressions:

            -  ``count(admin1)``
            -  ``count(base_compensation, [bucket(1000, 10000), bucket(10000, 100000), bucket(100000, MAX)])``
            -  ``count(string_custom_attribute["some-string-custom-attribute"])``
            -  ``count(numeric_custom_attribute["some-numeric-custom-attribute"], [bucket(MIN, 0, "negative"), bucket(0, MAX, "non-negative"])``
        job_view (~.job_service.JobView):
            The desired job attributes returned for jobs in the search
            response. Defaults to
            [JobView.JOB_VIEW_SMALL][google.cloud.talent.v4.JobView.JOB_VIEW_SMALL]
            if no value is specified.
        offset (int):
            An integer that specifies the current offset (that is,
            starting result location, amongst the jobs deemed by the API
            as relevant) in search results. This field is only
            considered if
            [page_token][google.cloud.talent.v4.SearchJobsRequest.page_token]
            is unset.

            The maximum allowed value is 5000. Otherwise an error is
            thrown.

            For example, 0 means to return results starting from the
            first matching job, and 10 means to return from the 11th
            job. This can be used for pagination, (for example, pageSize
            = 10 and offset = 10 means to return from the second page).
        max_page_size (int):
            A limit on the number of jobs returned in the
            search results. Increasing this value above the
            default value of 10 can increase search response
            time. The value can be between 1 and 100.
        page_token (str):
            The token specifying the current offset within search
            results. See
            [SearchJobsResponse.next_page_token][google.cloud.talent.v4.SearchJobsResponse.next_page_token]
            for an explanation of how to obtain the next set of query
            results.
        order_by (str):
            The criteria determining how search results are sorted.
            Default is ``"relevance desc"``.

            Supported options are:

            -  ``"relevance desc"``: By relevance descending, as
               determined by the API algorithms. Relevance thresholding
               of query results is only available with this ordering.
            -  ``"posting_publish_time desc"``: By
               [Job.posting_publish_time][google.cloud.talent.v4.Job.posting_publish_time]
               descending.
            -  ``"posting_update_time desc"``: By
               [Job.posting_update_time][google.cloud.talent.v4.Job.posting_update_time]
               descending.
            -  ``"title"``: By
               [Job.title][google.cloud.talent.v4.Job.title] ascending.
            -  ``"title desc"``: By
               [Job.title][google.cloud.talent.v4.Job.title] descending.
            -  ``"annualized_base_compensation"``: By job's
               [CompensationInfo.annualized_base_compensation_range][google.cloud.talent.v4.CompensationInfo.annualized_base_compensation_range]
               ascending. Jobs whose annualized base compensation is
               unspecified are put at the end of search results.
            -  ``"annualized_base_compensation desc"``: By job's
               [CompensationInfo.annualized_base_compensation_range][google.cloud.talent.v4.CompensationInfo.annualized_base_compensation_range]
               descending. Jobs whose annualized base compensation is
               unspecified are put at the end of search results.
            -  ``"annualized_total_compensation"``: By job's
               [CompensationInfo.annualized_total_compensation_range][google.cloud.talent.v4.CompensationInfo.annualized_total_compensation_range]
               ascending. Jobs whose annualized base compensation is
               unspecified are put at the end of search results.
            -  ``"annualized_total_compensation desc"``: By job's
               [CompensationInfo.annualized_total_compensation_range][google.cloud.talent.v4.CompensationInfo.annualized_total_compensation_range]
               descending. Jobs whose annualized base compensation is
               unspecified are put at the end of search results.
            -  ``"custom_ranking desc"``: By the relevance score
               adjusted to the
               [SearchJobsRequest.CustomRankingInfo.ranking_expression][google.cloud.talent.v4.SearchJobsRequest.CustomRankingInfo.ranking_expression]
               with weight factor assigned by
               [SearchJobsRequest.CustomRankingInfo.importance_level][google.cloud.talent.v4.SearchJobsRequest.CustomRankingInfo.importance_level]
               in descending order.
            -  Location sorting: Use the special syntax to order jobs by
               distance: ``"distance_from('Hawaii')"``: Order by
               distance from Hawaii. ``"distance_from(19.89, 155.5)"``:
               Order by distance from a coordinate.
               ``"distance_from('Hawaii'), distance_from('Puerto Rico')"``:
               Order by multiple locations. See details below.
               ``"distance_from('Hawaii'), distance_from(19.89, 155.5)"``:
               Order by multiple locations. See details below. The
               string can have a maximum of 256 characters. When
               multiple distance centers are provided, a job that is
               close to any of the distance centers would have a high
               rank. When a job has multiple locations, the job location
               closest to one of the distance centers will be used. Jobs
               that don't have locations will be ranked at the bottom.
               Distance is calculated with a precision of 11.3 meters
               (37.4 feet). Diversification strategy is still applied
               unless explicitly disabled in
               [diversification_level][google.cloud.talent.v4.SearchJobsRequest.diversification_level].
        diversification_level (~.job_service.SearchJobsRequest.DiversificationLevel):
            Controls whether highly similar jobs are returned next to
            each other in the search results. Jobs are identified as
            highly similar based on their titles, job categories, and
            locations. Highly similar results are clustered so that only
            one representative job of the cluster is displayed to the
            job seeker higher up in the results, with the other jobs
            being displayed lower down in the results.

            Defaults to
            [DiversificationLevel.SIMPLE][google.cloud.talent.v4.SearchJobsRequest.DiversificationLevel.SIMPLE]
            if no value is specified.
        custom_ranking_info (~.job_service.SearchJobsRequest.CustomRankingInfo):
            Controls over how job documents get ranked on
            top of existing relevance score (determined by
            API algorithm).
        disable_keyword_match (bool):
            Controls whether to disable exact keyword match on
            [Job.title][google.cloud.talent.v4.Job.title],
            [Job.description][google.cloud.talent.v4.Job.description],
            [Job.company_display_name][google.cloud.talent.v4.Job.company_display_name],
            [Job.addresses][google.cloud.talent.v4.Job.addresses],
            [Job.qualifications][google.cloud.talent.v4.Job.qualifications].
            When disable keyword match is turned off, a keyword match
            returns jobs that do not match given category filters when
            there are matching keywords. For example, for the query
            "program manager," a result is returned even if the job
            posting has the title "software developer," which doesn't
            fall into "program manager" ontology, but does have "program
            manager" appearing in its description.

            For queries like "cloud" that don't contain title or
            location specific ontology, jobs with "cloud" keyword
            matches are returned regardless of this flag's value.

            Use
            [Company.keyword_searchable_job_custom_attributes][google.cloud.talent.v4.Company.keyword_searchable_job_custom_attributes]
            if company-specific globally matched custom field/attribute
            string values are needed. Enabling keyword match improves
            recall of subsequent search requests.

            Defaults to false.
    """

    class SearchMode(proto.Enum):
        r"""A string-represented enumeration of the job search mode. The
        service operate differently for different modes of service.
        """
        SEARCH_MODE_UNSPECIFIED = 0
        JOB_SEARCH = 1
        FEATURED_JOB_SEARCH = 2

    class DiversificationLevel(proto.Enum):
        r"""Controls whether highly similar jobs are returned next to
        each other in the search results. Jobs are identified as highly
        similar based on their titles, job categories, and locations.
        Highly similar results are clustered so that only one
        representative job of the cluster is displayed to the job seeker
        higher up in the results, with the other jobs being displayed
        lower down in the results.
        """
        DIVERSIFICATION_LEVEL_UNSPECIFIED = 0
        DISABLED = 1
        SIMPLE = 2

    class CustomRankingInfo(proto.Message):
        r"""Custom ranking information for
        [SearchJobsRequest][google.cloud.talent.v4.SearchJobsRequest].

        Attributes:
            importance_level (~.job_service.SearchJobsRequest.CustomRankingInfo.ImportanceLevel):
                Required. Controls over how important the score of
                [CustomRankingInfo.ranking_expression][google.cloud.talent.v4.SearchJobsRequest.CustomRankingInfo.ranking_expression]
                gets applied to job's final ranking position.

                An error is thrown if not specified.
            ranking_expression (str):
                Required. Controls over how job documents get ranked on top
                of existing relevance score (determined by API algorithm). A
                combination of the ranking expression and relevance score is
                used to determine job's final ranking position.

                The syntax for this expression is a subset of Google SQL
                syntax.

                Supported operators are: +, -, \*, /, where the left and
                right side of the operator is either a numeric
                [Job.custom_attributes][google.cloud.talent.v4.Job.custom_attributes]
                key, integer/double value or an expression that can be
                evaluated to a number.

                Parenthesis are supported to adjust calculation precedence.
                The expression must be < 100 characters in length.

                The expression is considered invalid for a job if the
                expression references custom attributes that are not
                populated on the job or if the expression results in a
                divide by zero. If an expression is invalid for a job, that
                job is demoted to the end of the results.

                Sample ranking expression (year + 25) \* 0.25 - (freshness /
                0.5)
        """

        class ImportanceLevel(proto.Enum):
            r"""The importance level for
            [CustomRankingInfo.ranking_expression][google.cloud.talent.v4.SearchJobsRequest.CustomRankingInfo.ranking_expression].
            """
            IMPORTANCE_LEVEL_UNSPECIFIED = 0
            NONE = 1
            LOW = 2
            MILD = 3
            MEDIUM = 4
            HIGH = 5
            EXTREME = 6

        importance_level = proto.Field(
            proto.ENUM,
            number=1,
            enum="SearchJobsRequest.CustomRankingInfo.ImportanceLevel",
        )

        ranking_expression = proto.Field(proto.STRING, number=2)

    parent = proto.Field(proto.STRING, number=1)

    search_mode = proto.Field(proto.ENUM, number=2, enum=SearchMode,)

    request_metadata = proto.Field(
        proto.MESSAGE, number=3, message=common.RequestMetadata,
    )

    job_query = proto.Field(proto.MESSAGE, number=4, message=filters.JobQuery,)

    enable_broadening = proto.Field(proto.BOOL, number=5)

    histogram_queries = proto.RepeatedField(
        proto.MESSAGE, number=7, message=histogram.HistogramQuery,
    )

    job_view = proto.Field(proto.ENUM, number=8, enum="JobView",)

    offset = proto.Field(proto.INT32, number=9)

    max_page_size = proto.Field(proto.INT32, number=10)

    page_token = proto.Field(proto.STRING, number=11)

    order_by = proto.Field(proto.STRING, number=12)

    diversification_level = proto.Field(
        proto.ENUM, number=13, enum=DiversificationLevel,
    )

    custom_ranking_info = proto.Field(
        proto.MESSAGE, number=14, message=CustomRankingInfo,
    )

    disable_keyword_match = proto.Field(proto.BOOL, number=16)


class SearchJobsResponse(proto.Message):
    r"""Response for SearchJob method.

    Attributes:
        matching_jobs (Sequence[~.job_service.SearchJobsResponse.MatchingJob]):
            The Job entities that match the specified
            [SearchJobsRequest][google.cloud.talent.v4.SearchJobsRequest].
        histogram_query_results (Sequence[~.histogram.HistogramQueryResult]):
            The histogram results that match with specified
            [SearchJobsRequest.histogram_queries][google.cloud.talent.v4.SearchJobsRequest.histogram_queries].
        next_page_token (str):
            The token that specifies the starting
            position of the next page of results. This field
            is empty if there are no more results.
        location_filters (Sequence[~.common.Location]):
            The location filters that the service applied to the
            specified query. If any filters are lat-lng based, the
            [Location.location_type][google.cloud.talent.v4.Location.location_type]
            is
            [Location.LocationType.LOCATION_TYPE_UNSPECIFIED][google.cloud.talent.v4.Location.LocationType.LOCATION_TYPE_UNSPECIFIED].
        total_size (int):
            Number of jobs that match the specified
            query.
            Note: This size is precise only if the total is
            less than 100,000.
        metadata (~.common.ResponseMetadata):
            Additional information for the API
            invocation, such as the request tracking id.
        broadened_query_jobs_count (int):
            If query broadening is enabled, we may append
            additional results from the broadened query.
            This number indicates how many of the jobs
            returned in the jobs field are from the
            broadened query. These results are always at the
            end of the jobs list. In particular, a value of
            0, or if the field isn't set, all the jobs in
            the jobs list are from the original (without
            broadening) query. If this field is non-zero,
            subsequent requests with offset after this
            result set should contain all broadened results.
        spell_correction (~.common.SpellingCorrection):
            The spell checking result, and correction.
    """

    class MatchingJob(proto.Message):
        r"""Job entry with metadata inside
        [SearchJobsResponse][google.cloud.talent.v4.SearchJobsResponse].

        Attributes:
            job (~.gct_job.Job):
                Job resource that matches the specified
                [SearchJobsRequest][google.cloud.talent.v4.SearchJobsRequest].
            job_summary (str):
                A summary of the job with core information
                that's displayed on the search results listing
                page.
            job_title_snippet (str):
                Contains snippets of text from the
                [Job.title][google.cloud.talent.v4.Job.title] field most
                closely matching a search query's keywords, if available.
                The matching query keywords are enclosed in HTML bold tags.
            search_text_snippet (str):
                Contains snippets of text from the
                [Job.description][google.cloud.talent.v4.Job.description]
                and similar fields that most closely match a search query's
                keywords, if available. All HTML tags in the original fields
                are stripped when returned in this field, and matching query
                keywords are enclosed in HTML bold tags.
            commute_info (~.job_service.SearchJobsResponse.CommuteInfo):
                Commute information which is generated based on specified
                [CommuteFilter][google.cloud.talent.v4.CommuteFilter].
        """

        job = proto.Field(proto.MESSAGE, number=1, message=gct_job.Job,)

        job_summary = proto.Field(proto.STRING, number=2)

        job_title_snippet = proto.Field(proto.STRING, number=3)

        search_text_snippet = proto.Field(proto.STRING, number=4)

        commute_info = proto.Field(
            proto.MESSAGE, number=5, message="SearchJobsResponse.CommuteInfo",
        )

    class CommuteInfo(proto.Message):
        r"""Commute details related to this job.

        Attributes:
            job_location (~.common.Location):
                Location used as the destination in the
                commute calculation.
            travel_duration (~.duration.Duration):
                The number of seconds required to travel to
                the job location from the query location. A
                duration of 0 seconds indicates that the job
                isn't reachable within the requested duration,
                but was returned as part of an expanded query.
        """

        job_location = proto.Field(proto.MESSAGE, number=1, message=common.Location,)

        travel_duration = proto.Field(
            proto.MESSAGE, number=2, message=duration.Duration,
        )

    @property
    def raw_page(self):
        return self

    matching_jobs = proto.RepeatedField(proto.MESSAGE, number=1, message=MatchingJob,)

    histogram_query_results = proto.RepeatedField(
        proto.MESSAGE, number=2, message=histogram.HistogramQueryResult,
    )

    next_page_token = proto.Field(proto.STRING, number=3)

    location_filters = proto.RepeatedField(
        proto.MESSAGE, number=4, message=common.Location,
    )

    total_size = proto.Field(proto.INT32, number=6)

    metadata = proto.Field(proto.MESSAGE, number=7, message=common.ResponseMetadata,)

    broadened_query_jobs_count = proto.Field(proto.INT32, number=8)

    spell_correction = proto.Field(
        proto.MESSAGE, number=9, message=common.SpellingCorrection,
    )


class BatchCreateJobsRequest(proto.Message):
    r"""Request to create a batch of jobs.

    Attributes:
        parent (str):
            Required. The resource name of the tenant under which the
            job is created.

            The format is "projects/{project_id}/tenants/{tenant_id}".
            For example, "projects/foo/tenants/bar".
        jobs (Sequence[~.gct_job.Job]):
            Required. The jobs to be created.
            A maximum of 200 jobs can be created in a batch.
    """

    parent = proto.Field(proto.STRING, number=1)

    jobs = proto.RepeatedField(proto.MESSAGE, number=2, message=gct_job.Job,)


class BatchUpdateJobsRequest(proto.Message):
    r"""Request to update a batch of jobs.

    Attributes:
        parent (str):
            Required. The resource name of the tenant under which the
            job is created.

            The format is "projects/{project_id}/tenants/{tenant_id}".
            For example, "projects/foo/tenants/bar".
        jobs (Sequence[~.gct_job.Job]):
            Required. The jobs to be updated.
            A maximum of 200 jobs can be updated in a batch.
        update_mask (~.field_mask.FieldMask):
            Strongly recommended for the best service experience. Be
            aware that it will also increase latency when checking the
            status of a batch operation.

            If
            [update_mask][google.cloud.talent.v4.BatchUpdateJobsRequest.update_mask]
            is provided, only the specified fields in
            [Job][google.cloud.talent.v4.Job] are updated. Otherwise all
            the fields are updated.

            A field mask to restrict the fields that are updated. Only
            top level fields of [Job][google.cloud.talent.v4.Job] are
            supported.

            If
            [update_mask][google.cloud.talent.v4.BatchUpdateJobsRequest.update_mask]
            is provided, The [Job][google.cloud.talent.v4.Job] inside
            [JobResult][JobOperationResult.JobResult] will only contains
            fields that is updated, plus the Id of the Job. Otherwise,
            [Job][google.cloud.talent.v4.Job] will include all fields,
            which can yield a very large response.
    """

    parent = proto.Field(proto.STRING, number=1)

    jobs = proto.RepeatedField(proto.MESSAGE, number=2, message=gct_job.Job,)

    update_mask = proto.Field(proto.MESSAGE, number=3, message=field_mask.FieldMask,)


class BatchDeleteJobsRequest(proto.Message):
    r"""Request to delete a batch of jobs.

    Attributes:
        parent (str):
            Required. The resource name of the tenant under which the
            job is created.

            The format is "projects/{project_id}/tenants/{tenant_id}".
            For example, "projects/foo/tenants/bar".

            The parent of all of the jobs specified in ``names`` must
            match this field.
        names (Sequence[str]):
            The names of the jobs to delete.

            The format is
            "projects/{project_id}/tenants/{tenant_id}/jobs/{job_id}".
            For example, "projects/foo/tenants/bar/jobs/baz".

            A maximum of 200 jobs can be deleted in a batch.
    """

    parent = proto.Field(proto.STRING, number=1)

    names = proto.RepeatedField(proto.STRING, number=2)


class JobResult(proto.Message):
    r"""Mutation result of a job from a batch operation.

    Attributes:
        job (~.gct_job.Job):
            Here [Job][google.cloud.talent.v4.Job] only contains basic
            information including
            [name][google.cloud.talent.v4.Job.name],
            [company][google.cloud.talent.v4.Job.company],
            [language_code][google.cloud.talent.v4.Job.language_code]
            and
            [requisition_id][google.cloud.talent.v4.Job.requisition_id],
            use getJob method to retrieve detailed information of the
            created/updated job.
        status (~.gr_status.Status):
            The status of the job processed. This field is populated if
            the processing of the
            [job][google.cloud.talent.v4.JobResult.job] fails.
    """

    job = proto.Field(proto.MESSAGE, number=1, message=gct_job.Job,)

    status = proto.Field(proto.MESSAGE, number=2, message=gr_status.Status,)


class BatchCreateJobsResponse(proto.Message):
    r"""The result of
    [JobService.BatchCreateJobs][google.cloud.talent.v4.JobService.BatchCreateJobs].
    It's used to replace
    [google.longrunning.Operation.response][google.longrunning.Operation.response]
    in case of success.

    Attributes:
        job_results (Sequence[~.job_service.JobResult]):
            List of job mutation results from a batch
            create operation. It can change until operation
            status is FINISHED, FAILED or CANCELLED.
    """

    job_results = proto.RepeatedField(proto.MESSAGE, number=1, message=JobResult,)


class BatchUpdateJobsResponse(proto.Message):
    r"""The result of
    [JobService.BatchUpdateJobs][google.cloud.talent.v4.JobService.BatchUpdateJobs].
    It's used to replace
    [google.longrunning.Operation.response][google.longrunning.Operation.response]
    in case of success.

    Attributes:
        job_results (Sequence[~.job_service.JobResult]):
            List of job mutation results from a batch
            update operation. It can change until operation
            status is FINISHED, FAILED or CANCELLED.
    """

    job_results = proto.RepeatedField(proto.MESSAGE, number=1, message=JobResult,)


class BatchDeleteJobsResponse(proto.Message):
    r"""The result of
    [JobService.BatchDeleteJobs][google.cloud.talent.v4.JobService.BatchDeleteJobs].
    It's used to replace
    [google.longrunning.Operation.response][google.longrunning.Operation.response]
    in case of success.

    Attributes:
        job_results (Sequence[~.job_service.JobResult]):
            List of job mutation results from a batch
            delete operation. It can change until operation
            status is FINISHED, FAILED or CANCELLED.
    """

    job_results = proto.RepeatedField(proto.MESSAGE, number=1, message=JobResult,)


__all__ = tuple(sorted(__protobuf__.manifest))
