import logging

from django.utils.translation import ugettext_lazy as _

from mayan.apps.metadata.models import MetadataType

from .classes import ImportSetupActionBackend


logger = logging.getLogger(name=__name__)


class ImportSetupActionDocumentMetadata(ImportSetupActionBackend):
    fields = {
        'metadata_type': {
            'label': _('Metadata type'),
            'class': 'django.forms.ModelChoiceField', 'kwargs': {
                'help_text': _(
                    'Metadata types associated with the document '
                    'type of the import setup.'
                ),
                'queryset': MetadataType.objects.none(), 'required': True
            }
        },
        'value': {
            'label': _('Value'),
            'class': 'django.forms.CharField', 'kwargs': {
                'help_text': _(
                    'Value to assign to the metadata. '
                    'Can be a literal value or template code. '
                    'Object availabe: {{ self }} and {{ document }}.'
                ),
                'required': True
            }
        },
    }
    field_order = ('metadata_type', 'value')
    label = _('Add metadata')
    widgets = {
        'metadata_types': {
            'class': 'django.forms.widgets.Select', 'kwargs': {
                'attrs': {'class': 'select2'},
            }
        },
        'value': {
            'class': 'django.forms.widgets.Textarea', 'kwargs': {
                'attrs': {'rows': '10'},
            }
        }
    }

    def execute(self, context):
        value = self.render_field(
            field_name='value', context=context
        )

        context['document'].metadata.create(
            metadata_type=MetadataType.objects.get(pk=self.metadata_type),
            value=value
        )

    def get_form_schema(self, **kwargs):
        import_setup = kwargs.pop('import_setup')

        result = super().get_form_schema(**kwargs)

        queryset = MetadataType.objects.get_for_document_type(
            document_type=import_setup.document_type
        )

        result['fields']['metadata_type']['kwargs']['queryset'] = queryset

        return result
