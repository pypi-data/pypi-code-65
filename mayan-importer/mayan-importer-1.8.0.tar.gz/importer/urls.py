from django.conf.urls import url

from .views import (
    ImportSetupActionCreateView, ImportSetupActionDeleteView,
    ImportSetupActionEditView, ImportSetupActionListView,
    ImportSetupActionBackendSelectionView, ImportSetupBackendSelectionView,
    ImportSetupCreateView, ImportSetupDeleteView, ImportSetupEditView,
    ImportSetupProcessView, ImportSetupClearView, ImportSetupListView,
    ImportSetupPopulateView, ImportSetupItemDeleteView,
    ImportSetupItemListView, ImportSetupItemLoadView,
    ImportSetupItemProcessView, ImportSetupItemSaveConfirmView,
    ImportSetupItemSaveDownloadView
)

urlpatterns_import_setup = [
    url(
        regex=r'^import_setups/$', name='import_setup_list',
        view=ImportSetupListView.as_view()
    ),
    url(
        regex=r'^import_setups/backend/selection/$',
        name='import_setup_backend_selection',
        view=ImportSetupBackendSelectionView.as_view()
    ),
    url(
        regex=r'^import_setups/(?P<class_path>[a-zA-Z0-9_.]+)/create/$',
        name='import_setup_create',
        view=ImportSetupCreateView.as_view()
    ),
    url(
        regex=r'^import_setups/(?P<import_setup_id>\d+)/delete/$',
        name='import_setup_delete', view=ImportSetupDeleteView.as_view()
    ),
    url(
        regex=r'^import_setups/(?P<import_setup_id>\d+)/edit/$',
        name='import_setup_edit', view=ImportSetupEditView.as_view()
    ),
]

urlpatterns_import_setup_actions = [
    url(
        regex=r'^import_setups/(?P<import_setup_id>\d+)/actions/$',
        name='import_setup_action_list',
        view=ImportSetupActionListView.as_view()
    ),
    url(
        regex=r'^import_setups/(?P<import_setup_id>\d+)/actions/(?P<class_path>[a-zA-Z0-9_.]+)/create/$',
        name='import_setup_action_create',
        view=ImportSetupActionCreateView.as_view()
    ),
    url(
        regex=r'^import_setups/actions/(?P<import_setup_action_id>\d+)/delete/$',
        name='import_setup_action_delete',
        view=ImportSetupActionDeleteView.as_view()
    ),
    url(
        regex=r'^import_setups/actions/(?P<import_setup_action_id>\d+)/edit/$',
        name='import_setup_action_edit',
        view=ImportSetupActionEditView.as_view()
    ),
    url(
        regex=r'^import_setups/(?P<import_setup_id>\d+)/actions/selection/$',
        name='import_setup_action_backend_selection',
        view=ImportSetupActionBackendSelectionView.as_view()
    ),
]

urlpatterns_import_setup_items = [
    url(
        regex=r'^import_setups/(?P<import_setup_id>\d+)/clear/$',
        name='import_setup_clear',
        view=ImportSetupClearView.as_view()
    ),
    url(
        regex=r'^import_setups/multiple/clear/$',
        name='import_setup_multiple_clear',
        view=ImportSetupClearView.as_view()
    ),
    url(
        regex=r'^import_setups/(?P<import_setup_id>\d+)/load/$',
        name='import_setup_load', view=ImportSetupItemLoadView.as_view()
    ),
    url(
        regex=r'^import_setups/(?P<import_setup_id>\d+)/populate/$',
        name='import_setup_populate', view=ImportSetupPopulateView.as_view()
    ),
    url(
        regex=r'^import_setups/multiple/populate/$',
        name='import_setup_multiple_populate',
        view=ImportSetupPopulateView.as_view()
    ),
    url(
        regex=r'^import_setups/(?P<import_setup_id>\d+)/process/$',
        name='import_setup_process', view=ImportSetupProcessView.as_view()
    ),
    url(
        regex=r'^import_setups/multiple/process/$',
        name='import_setup_multiple_process',
        view=ImportSetupProcessView.as_view()
    ),
    url(
        regex=r'^import_setups/(?P<import_setup_id>\d+)/save/$',
        name='import_setup_save', view=ImportSetupItemSaveConfirmView.as_view()
    ),
    url(
        regex=r'^import_setups/(?P<shared_upload_file_id>\d+)/save/download/$',
        name='import_setup_save_download', view=ImportSetupItemSaveDownloadView.as_view()
    ),
    url(
        regex=r'^import_setups/(?P<import_setup_id>\d+)/items/$',
        name='import_setup_items_list',
        view=ImportSetupItemListView.as_view()
    ),
    url(
        regex=r'^import_setups/items/(?P<import_setup_item_id>\d+)/delete/$',
        name='import_setup_item_delete',
        view=ImportSetupItemDeleteView.as_view()
    ),
    url(
        regex=r'^import_setups/items/multiple/delete/$',
        name='import_setup_item_multiple_delete',
        view=ImportSetupItemDeleteView.as_view()
    ),
    url(
        regex=r'^import_setups/items/multiple/process/$',
        name='import_setup_item_multiple_process',
        view=ImportSetupItemProcessView.as_view()
    ),
]

urlpatterns = []
urlpatterns.extend(urlpatterns_import_setup)
urlpatterns.extend(urlpatterns_import_setup_actions)
urlpatterns.extend(urlpatterns_import_setup_items)
