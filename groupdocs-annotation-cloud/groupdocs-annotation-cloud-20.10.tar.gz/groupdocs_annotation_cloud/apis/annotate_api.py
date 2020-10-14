# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd">
#   Copyright (c) 2003-2020 Aspose Pty Ltd
# </copyright>
# <summary>
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
# </summary>
# -----------------------------------------------------------------------------------

from __future__ import absolute_import

import re  # noqa: F401

# python 2 and python 3 compatibility library
import six

from groupdocs_annotation_cloud.auth import Auth
from groupdocs_annotation_cloud.api_client import ApiClient
from groupdocs_annotation_cloud.api_exception import ApiException
from groupdocs_annotation_cloud.configuration import Configuration

class AnnotateApi(object):
    """
    GroupDocs.Annotation Cloud API

    :param configuration: API configuration
    """

    def __init__(self, configuration):
        api_client = ApiClient(configuration)

        self.auth = Auth(configuration, api_client)
        self.api_client = api_client
        self.configuration = configuration

    def close(self):  # noqa: E501
        """
        Closes thread pool. This method should be called when 
        methods are executed asynchronously (is_async=True is passed as parameter)
        and this instance of AnnotateApi is not going to be used any more.
        """
        if self.api_client is not None:
            if(self.api_client.pool is not None):
                self.api_client.pool.close()
                self.api_client.pool.join()
                self.api_client.pool = None

    @classmethod
    def from_keys(cls, app_sid, app_key):
        """
        Initializes new instance of AnnotateApi with API keys

        :param app_sid Application identifier (App SID)
        :param app_key Application private key (App Key)
        """
        configuration = Configuration(app_sid, app_key)
        return AnnotateApi(configuration)

    @classmethod
    def from_config(cls, configuration):
        """
        Initializes new instance of AnnotateApi with configuration options

        :param configuration API configuration
        """
        return AnnotateApi(configuration)

    def delete_annotations(self, request,**kwargs):  # noqa: E501
        """Removes annotations from document  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True

        :param is_async bool
        :param str file_path: Document path in storage (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True

        if kwargs.get('is_async'):
            return self._delete_annotations_with_http_info(request, **kwargs)  # noqa: E501
        
        self._delete_annotations_with_http_info(request, **kwargs)  # noqa: E501
        

    def _delete_annotations_with_http_info(self, request, **kwargs):  # noqa: E501
        """Removes annotations from document  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True

        :param is_async bool
        :param DeleteAnnotationsRequest request object with parameters
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        params = locals()
        params['is_async'] = ''
        params['_return_http_data_only'] = False
        params['_preload_content'] = True
        params['_request_timeout'] = ''
        for key, val in six.iteritems(params['kwargs']):
            if key not in params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_annotations" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'file_path' is set
        if request.file_path is None:
            raise ValueError("Missing the required parameter `file_path` when calling `delete_annotations`")  # noqa: E501

        collection_formats = {}
        path = '/annotation'
        path_params = {}

        query_params = []
        if self.__downcase_first_letter('filePath') in path:
            path = path.replace('{' + self.__downcase_first_letter('filePath' + '}'), request.file_path if request.file_path is not None else '')
        else:
            if request.file_path is not None:
                query_params.append((self.__downcase_first_letter('filePath'), request.file_path))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = []

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        call_kwargs = {
            'resource_path':path, 
            'method':'DELETE',
            'path_params':path_params,
            'query_params':query_params,
            'header_params':header_params,
            'body':body_params,
            'post_params':form_params,
            'files':local_var_files,
            'response_type':None,  # noqa: E501
            'auth_settings':self.auth.get_auth_settings(),
            'is_async':params.get('is_async'),
            '_return_http_data_only':params.get('_return_http_data_only'),
            '_preload_content':params.get('_preload_content', True),
            '_request_timeout':params.get('_request_timeout'),
            'collection_formats':collection_formats
        }

        return self.api_client.call_api(**call_kwargs)  # noqa: E501

    def get_export(self, request,**kwargs):  # noqa: E501
        """Retrieves document with annotations  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True

        :param is_async bool
        :param str file_path: Document path in storage (required)
        :param str annotation_types: Annotation types that will be exported. All annotation types will be exported if not specified
        :param bool annotated_pages: Indicates whether to export only annotated pages
        :param int first_page: Determines number of first exported page
        :param int last_page: Determines number of last exported page
        :param str password: Source document password
        :return: file
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True

        if kwargs.get('is_async'):
            return self._get_export_with_http_info(request, **kwargs)  # noqa: E501
        
        (data) = self._get_export_with_http_info(request, **kwargs)  # noqa: E501
        return data

    def _get_export_with_http_info(self, request, **kwargs):  # noqa: E501
        """Retrieves document with annotations  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True

        :param is_async bool
        :param GetExportRequest request object with parameters
        :return: file
                 If the method is called asynchronously,
                 returns the request thread.
        """
        params = locals()
        params['is_async'] = ''
        params['_return_http_data_only'] = False
        params['_preload_content'] = True
        params['_request_timeout'] = ''
        for key, val in six.iteritems(params['kwargs']):
            if key not in params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_export" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'file_path' is set
        if request.file_path is None:
            raise ValueError("Missing the required parameter `file_path` when calling `get_export`")  # noqa: E501

        collection_formats = {}
        path = '/annotation/result'
        path_params = {}

        query_params = []
        if self.__downcase_first_letter('filePath') in path:
            path = path.replace('{' + self.__downcase_first_letter('filePath' + '}'), request.file_path if request.file_path is not None else '')
        else:
            if request.file_path is not None:
                query_params.append((self.__downcase_first_letter('filePath'), request.file_path))  # noqa: E501
        if self.__downcase_first_letter('annotationTypes') in path:
            path = path.replace('{' + self.__downcase_first_letter('annotationTypes' + '}'), request.annotation_types if request.annotation_types is not None else '')
        else:
            if request.annotation_types is not None:
                query_params.append((self.__downcase_first_letter('annotationTypes'), request.annotation_types))  # noqa: E501
        if self.__downcase_first_letter('annotatedPages') in path:
            path = path.replace('{' + self.__downcase_first_letter('annotatedPages' + '}'), request.annotated_pages if request.annotated_pages is not None else '')
        else:
            if request.annotated_pages is not None:
                query_params.append((self.__downcase_first_letter('annotatedPages'), request.annotated_pages))  # noqa: E501
        if self.__downcase_first_letter('firstPage') in path:
            path = path.replace('{' + self.__downcase_first_letter('firstPage' + '}'), request.first_page if request.first_page is not None else '')
        else:
            if request.first_page is not None:
                query_params.append((self.__downcase_first_letter('firstPage'), request.first_page))  # noqa: E501
        if self.__downcase_first_letter('lastPage') in path:
            path = path.replace('{' + self.__downcase_first_letter('lastPage' + '}'), request.last_page if request.last_page is not None else '')
        else:
            if request.last_page is not None:
                query_params.append((self.__downcase_first_letter('lastPage'), request.last_page))  # noqa: E501
        if self.__downcase_first_letter('password') in path:
            path = path.replace('{' + self.__downcase_first_letter('password' + '}'), request.password if request.password is not None else '')
        else:
            if request.password is not None:
                query_params.append((self.__downcase_first_letter('password'), request.password))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = []

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        call_kwargs = {
            'resource_path':path, 
            'method':'GET',
            'path_params':path_params,
            'query_params':query_params,
            'header_params':header_params,
            'body':body_params,
            'post_params':form_params,
            'files':local_var_files,
            'response_type':'file',  # noqa: E501
            'auth_settings':self.auth.get_auth_settings(),
            'is_async':params.get('is_async'),
            '_return_http_data_only':params.get('_return_http_data_only'),
            '_preload_content':params.get('_preload_content', True),
            '_request_timeout':params.get('_request_timeout'),
            'collection_formats':collection_formats
        }

        return self.api_client.call_api(**call_kwargs)  # noqa: E501

    def get_import(self, request,**kwargs):  # noqa: E501
        """Extracts annotations from document  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True

        :param is_async bool
        :param str file_path: Document path in storage (required)
        :return: list[AnnotationInfo]
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True

        if kwargs.get('is_async'):
            return self._get_import_with_http_info(request, **kwargs)  # noqa: E501
        
        (data) = self._get_import_with_http_info(request, **kwargs)  # noqa: E501
        return data

    def _get_import_with_http_info(self, request, **kwargs):  # noqa: E501
        """Extracts annotations from document  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True

        :param is_async bool
        :param GetImportRequest request object with parameters
        :return: list[AnnotationInfo]
                 If the method is called asynchronously,
                 returns the request thread.
        """
        params = locals()
        params['is_async'] = ''
        params['_return_http_data_only'] = False
        params['_preload_content'] = True
        params['_request_timeout'] = ''
        for key, val in six.iteritems(params['kwargs']):
            if key not in params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_import" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'file_path' is set
        if request.file_path is None:
            raise ValueError("Missing the required parameter `file_path` when calling `get_import`")  # noqa: E501

        collection_formats = {}
        path = '/annotation'
        path_params = {}

        query_params = []
        if self.__downcase_first_letter('filePath') in path:
            path = path.replace('{' + self.__downcase_first_letter('filePath' + '}'), request.file_path if request.file_path is not None else '')
        else:
            if request.file_path is not None:
                query_params.append((self.__downcase_first_letter('filePath'), request.file_path))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = []

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        call_kwargs = {
            'resource_path':path, 
            'method':'GET',
            'path_params':path_params,
            'query_params':query_params,
            'header_params':header_params,
            'body':body_params,
            'post_params':form_params,
            'files':local_var_files,
            'response_type':'list[AnnotationInfo]',  # noqa: E501
            'auth_settings':self.auth.get_auth_settings(),
            'is_async':params.get('is_async'),
            '_return_http_data_only':params.get('_return_http_data_only'),
            '_preload_content':params.get('_preload_content', True),
            '_request_timeout':params.get('_request_timeout'),
            'collection_formats':collection_formats
        }

        return self.api_client.call_api(**call_kwargs)  # noqa: E501

    def post_annotations(self, request,**kwargs):  # noqa: E501
        """Adds annotations to document  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True

        :param is_async bool
        :param str file_path: Document path in storage (required)
        :param list[AnnotationInfo] annotations: Array of annotation descriptions (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True

        if kwargs.get('is_async'):
            return self._post_annotations_with_http_info(request, **kwargs)  # noqa: E501
        
        self._post_annotations_with_http_info(request, **kwargs)  # noqa: E501
        

    def _post_annotations_with_http_info(self, request, **kwargs):  # noqa: E501
        """Adds annotations to document  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True

        :param is_async bool
        :param PostAnnotationsRequest request object with parameters
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        params = locals()
        params['is_async'] = ''
        params['_return_http_data_only'] = False
        params['_preload_content'] = True
        params['_request_timeout'] = ''
        for key, val in six.iteritems(params['kwargs']):
            if key not in params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_annotations" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'file_path' is set
        if request.file_path is None:
            raise ValueError("Missing the required parameter `file_path` when calling `post_annotations`")  # noqa: E501
        # verify the required parameter 'annotations' is set
        if request.annotations is None:
            raise ValueError("Missing the required parameter `annotations` when calling `post_annotations`")  # noqa: E501

        collection_formats = {}
        path = '/annotation'
        path_params = {}

        query_params = []
        if self.__downcase_first_letter('filePath') in path:
            path = path.replace('{' + self.__downcase_first_letter('filePath' + '}'), request.file_path if request.file_path is not None else '')
        else:
            if request.file_path is not None:
                query_params.append((self.__downcase_first_letter('filePath'), request.file_path))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = []

        body_params = None
        if request.annotations is not None:
            body_params = request.annotations
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        call_kwargs = {
            'resource_path':path, 
            'method':'POST',
            'path_params':path_params,
            'query_params':query_params,
            'header_params':header_params,
            'body':body_params,
            'post_params':form_params,
            'files':local_var_files,
            'response_type':None,  # noqa: E501
            'auth_settings':self.auth.get_auth_settings(),
            'is_async':params.get('is_async'),
            '_return_http_data_only':params.get('_return_http_data_only'),
            '_preload_content':params.get('_preload_content', True),
            '_request_timeout':params.get('_request_timeout'),
            'collection_formats':collection_formats
        }

        return self.api_client.call_api(**call_kwargs)  # noqa: E501

    def __downcase_first_letter(self, s):
        if len(s) == 0:
            return str
        else:
            return s[0].lower() + s[1:]

# coding: utf-8

# --------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="delete_annotations_request.py">
#   Copyright (c) 2003-2020 Aspose Pty Ltd
# </copyright>
# <summary>
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
# 
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
# 
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
# </summary>
# --------------------------------------------------------------------------------

class DeleteAnnotationsRequest(object):
    """
    Request model for delete_annotations operation.
    :param file_path Document path in storage
    """

    def __init__(self, file_path):
        """Initializes new instance of DeleteAnnotationsRequest."""  # noqa: E501
        self.file_path = file_path
# coding: utf-8

# --------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="get_export_request.py">
#   Copyright (c) 2003-2020 Aspose Pty Ltd
# </copyright>
# <summary>
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
# 
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
# 
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
# </summary>
# --------------------------------------------------------------------------------

class GetExportRequest(object):
    """
    Request model for get_export operation.
    :param file_path Document path in storage
    :param annotation_types Annotation types that will be exported. All annotation types will be exported if not specified
    :param annotated_pages Indicates whether to export only annotated pages
    :param first_page Determines number of first exported page
    :param last_page Determines number of last exported page
    :param password Source document password
    """

    def __init__(self, file_path, annotation_types=None, annotated_pages=None, first_page=None, last_page=None, password=None):
        """Initializes new instance of GetExportRequest."""  # noqa: E501
        self.file_path = file_path
        self.annotation_types = annotation_types
        self.annotated_pages = annotated_pages
        self.first_page = first_page
        self.last_page = last_page
        self.password = password
# coding: utf-8

# --------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="get_import_request.py">
#   Copyright (c) 2003-2020 Aspose Pty Ltd
# </copyright>
# <summary>
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
# 
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
# 
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
# </summary>
# --------------------------------------------------------------------------------

class GetImportRequest(object):
    """
    Request model for get_import operation.
    :param file_path Document path in storage
    """

    def __init__(self, file_path):
        """Initializes new instance of GetImportRequest."""  # noqa: E501
        self.file_path = file_path
# coding: utf-8

# --------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="post_annotations_request.py">
#   Copyright (c) 2003-2020 Aspose Pty Ltd
# </copyright>
# <summary>
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
# 
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
# 
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
# </summary>
# --------------------------------------------------------------------------------

class PostAnnotationsRequest(object):
    """
    Request model for post_annotations operation.
    :param file_path Document path in storage
    :param annotations Array of annotation descriptions
    """

    def __init__(self, file_path, annotations):
        """Initializes new instance of PostAnnotationsRequest."""  # noqa: E501
        self.file_path = file_path
        self.annotations = annotations
