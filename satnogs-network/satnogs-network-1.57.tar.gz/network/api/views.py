"""SatNOGS Network API django rest framework Views"""
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.schemas.utils import is_list_view
from rest_framework.serializers import ValidationError

from network.api import filters, pagination, serializers
from network.api.perms import StationOwnerPermission
from network.base.models import Observation, Station
from network.base.rating_tasks import rate_observation
from network.base.tasks import sync_to_db
from network.base.validators import NegativeElevationError, NoTleSetError, \
    ObservationOverlapError, SinglePassError


class ViewSchema(AutoSchema):
    """
    AutoSchema override
    """
    def _get_operation_id(self, path, method):
        """
        Compute an operation ID from the view name.
        """
        method_name = getattr(self.view, 'action', method.lower())
        if is_list_view(path, method, self.view):
            action = 'list'
        elif method_name not in self.method_mapping:
            action = method_name
        else:
            action = self.method_mapping[method.lower()]

        name = self.view.__class__.__name__
        if name.endswith('APIView'):
            name = name[:-7]
        elif name.endswith('View'):
            name = name[:-4]

        if name.endswith(action.title()):
            name = name[:-len(action)]

        if action == 'list' and not name.endswith('s'):
            name += 's'

        return action + name


class ObservationView(  # pylint: disable=R0901
        mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
        mixins.CreateModelMixin, viewsets.GenericViewSet):
    """SatNOGS Network Observation API view class"""
    queryset = Observation.objects.prefetch_related('satellite', 'demoddata', 'ground_station')
    filterset_class = filters.ObservationViewFilter
    permission_classes = [StationOwnerPermission]
    pagination_class = pagination.LinkedHeaderPageNumberPagination

    def get_serializer_class(self):
        """Returns the right serializer depending on http method that is used"""
        if self.action == 'create':
            return serializers.NewObservationSerializer
        return serializers.ObservationSerializer

    def create(self, request, *args, **kwargs):
        """Creates observations from a list of observation data"""
        serializer = self.get_serializer(data=request.data, many=True, allow_empty=False)
        try:
            if serializer.is_valid():
                observations = serializer.save()
                serialized_obs = serializers.ObservationSerializer(observations, many=True)
                data = serialized_obs.data
                response = Response(data, status=status.HTTP_200_OK)
            else:
                data = serializer.errors
                response = Response(data, status=status.HTTP_400_BAD_REQUEST)
        except (NegativeElevationError, SinglePassError, ValidationError, ValueError) as error:
            response = Response(str(error), status=status.HTTP_400_BAD_REQUEST)
        except NoTleSetError as error:
            response = Response(str(error), status=status.HTTP_501_NOT_IMPLEMENTED)
        except ObservationOverlapError as error:
            response = Response(str(error), status=status.HTTP_409_CONFLICT)
        return response

    def update(self, request, *args, **kwargs):
        """Updates observation with audio, waterfall or demoded data"""
        instance = self.get_object()
        if request.data.get('client_version'):
            instance.ground_station.client_version = request.data.get('client_version')
            instance.ground_station.save()
        if request.data.get('demoddata'):
            try:
                file_path = 'data_obs/{0}/{1}'.format(instance.id, request.data.get('demoddata'))
                instance.demoddata.get(payload_demod=file_path)
                return Response(
                    data='This data file has already been uploaded',
                    status=status.HTTP_403_FORBIDDEN
                )
            except ObjectDoesNotExist:
                demoddata = instance.demoddata.create(payload_demod=request.data.get('demoddata'))
                sync_to_db.delay(frame_id=demoddata.id)
        if request.data.get('waterfall'):
            if instance.has_waterfall:
                return Response(
                    data='Watefall has already been uploaded', status=status.HTTP_403_FORBIDDEN
                )
        if request.data.get('payload'):
            if instance.has_audio:
                return Response(
                    data='Audio has already been uploaded', status=status.HTTP_403_FORBIDDEN
                )

        # False-positive no-member (E1101) pylint error:
        # Parent class rest_framework.mixins.UpdateModelMixin provides the 'update' method
        super(ObservationView, self).update(request, *args, **kwargs)  # pylint: disable=E1101
        if request.data.get('waterfall'):
            rate_observation.delay(instance.id, 'waterfall_upload')
        if request.data.get('demoddata'):
            rate_observation.delay(instance.id, 'data_upload')
        return Response(status=status.HTTP_200_OK)


class StationView(  # pylint: disable=R0901
        mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """SatNOGS Network Station API view class"""
    queryset = Station.objects.annotate(
        total_obs=Count('observations'),
    ).prefetch_related('antennas', 'antennas__antenna_type', 'antennas__frequency_ranges')
    serializer_class = serializers.StationSerializer
    filterset_class = filters.StationViewFilter
    pagination_class = pagination.LinkedHeaderPageNumberPagination


class TransmitterView(  # pylint: disable=R0901
        mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """SatNOGS Network Transmitter API view class"""
    queryset = Observation.objects.order_by().values('transmitter_uuid').distinct()
    serializer_class = serializers.TransmitterSerializer
    lookup_field = 'transmitter_uuid'
    filterset_class = filters.TransmitterViewFilter
    pagination_class = pagination.LinkedHeaderPageNumberPagination
    schema = ViewSchema()


class JobView(viewsets.ReadOnlyModelViewSet):  # pylint: disable=R0901
    """SatNOGS Network Job API view class"""
    queryset = Observation.objects.filter(payload='')
    serializer_class = serializers.JobSerializer
    filterset_class = filters.ObservationViewFilter
    filterset_fields = ('ground_station')
    schema = ViewSchema()

    def get_queryset(self):
        """Returns queryset for Job API view"""
        queryset = self.queryset.filter(start__gte=now())
        ground_station_id = self.request.query_params.get('ground_station', None)
        if ground_station_id and self.request.user.is_authenticated:
            ground_station = get_object_or_404(Station, id=ground_station_id)
            if ground_station.owner == self.request.user:
                lat = self.request.query_params.get('lat', None)
                lon = self.request.query_params.get('lon', None)
                alt = self.request.query_params.get('alt', None)
                if not (lat is None or lon is None or alt is None):
                    ground_station.lat = float(lat)
                    ground_station.lng = float(lon)
                    ground_station.alt = int(alt)
                ground_station.last_seen = now()
                ground_station.save()
        return queryset
