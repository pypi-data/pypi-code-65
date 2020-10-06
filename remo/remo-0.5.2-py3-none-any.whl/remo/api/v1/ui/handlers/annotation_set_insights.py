from django.db.models import Q
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework import serializers

from remo_app.remo.models import AnnotationSet, NewAnnotation
from remo_app.remo.api.viewsets import BaseNestedModelViewSet


class AnnotationSetInsightSerializer(serializers.Serializer):
    name = serializers.CharField()
    total_annotation_objects = serializers.IntegerField()
    total_images = serializers.IntegerField()
    objects_per_image = serializers.FloatField()


class AnnotationSetInsightsSerializer(serializers.Serializer):
    record_type = serializers.CharField()
    class_ = serializers.SerializerMethodField()
    tag = serializers.SerializerMethodField()

    @property
    def fields(self):
        fields = super().fields
        fields['class'] = fields.pop('class_')

        return fields

    def get_class_(self, instance):
        if instance['record_type'] != 'class':
            return None

        return AnnotationSetInsightSerializer(instance, context=self.context).data

    def get_tag(self, instance):
        if instance['record_type'] != 'tag':
            return None

        return AnnotationSetInsightSerializer(instance, context=self.context).data


class AnnotationSetInsights(mixins.ListModelMixin, BaseNestedModelViewSet):
    parent_lookup = 'annotation_sets'

    def get_parent_queryset(self):
        return AnnotationSet.objects.filter(Q(user=self.request.user) | Q(dataset__is_public=True))

    def list(self, request, *args, **kwargs):
        annotation_set = self.get_parent_object_or_404()

        total_images = annotation_set.dataset.quantity
        split_by_tags = request.query_params.get('split_by_tags', [])
        if isinstance(split_by_tags, str):
            split_by_tags = split_by_tags.split(',')
            split_by_tags = list(map(lambda s: s.lower(), split_by_tags)) if split_by_tags else []

        stat = annotation_set.statistics.first()
        data = []
        if not stat:
            return Response(
                {'total_annotated_images': total_images, 'total_annotation_objects': 0, 'results': data}
            )

        stats_by_tags, total_annotated_images, total_annotation_objects = self.calc_stats_by_tags(split_by_tags, annotation_set)
        for class_name, class_stat in stat.classes.items():
            n_objs = class_stat.get('n_objs', 0)
            n_imgs = class_stat.get('n_imgs', 0)
            objs_per_img = n_objs / n_imgs if n_imgs > 0 and n_objs > 0 else 'N/A'
            class_stat = {
                'record_type': 'class',
                'class': {
                    'name': class_name,
                    'objects_per_image': objs_per_img,
                    'total_annotation_objects': n_objs,
                    'total_images': n_imgs,
                },
            }

            if stats_by_tags and class_name in stats_by_tags:
                class_stat['split_by_tags'] = [
                    {'name': tag, **tag_stat} for tag, tag_stat in stats_by_tags[class_name].items()
                ]

            data.append(class_stat)

        if stat.tags and not split_by_tags:
            for tag_name, count in stat.tags:
                data.append(
                    {
                        'record_type': 'tag',
                        'tag': {'name': tag_name, 'total_images': count, 'total_annotation_objects': 0},
                    }
                )

        results = {
            'total_annotated_images': total_annotated_images if split_by_tags else total_images,
            'total_annotation_objects': total_annotation_objects if split_by_tags else stat.total_annotation_objects,
            'results': data,
        }

        return Response(results)

    def calc_objects_for_class(self, objects: list, class_name: str) -> int:
        return sum(1 for obj in objects if class_name in obj.get('classes', []))

    def calc_stats_by_tags(self, split_by_tags: list, annotation_set: AnnotationSet):
        stats_by_tags = {}
        total_stats = {}
        for annotation in NewAnnotation.objects.filter(annotation_set=annotation_set):
            for tag in split_by_tags:
                for class_name in annotation.classes:
                    class_stat = stats_by_tags.get(class_name, {})
                    tag_stat = class_stat.get(
                        tag, {'objects_per_image': 0, 'total_annotation_objects': 0, 'total_images': 0}
                    )
                    if tag in annotation.tags:
                        tag_stat['total_images'] += 1
                        tag_stat['total_annotation_objects'] += self.calc_objects_for_class(
                            annotation.data.get('objects', []), class_name
                        )
                        tag_stat['objects_per_image'] = (
                            tag_stat['total_annotation_objects'] / tag_stat['total_images']
                        )
                    class_stat[tag] = tag_stat
                    stats_by_tags[class_name] = class_stat

                stat = total_stats.get(tag, {'images': 0, 'objects': 0})
                if tag in annotation.tags:
                    stat['images'] += 1
                    stat['objects'] += len(annotation.data.get('objects', []))
                total_stats[tag] = stat

        total_annotated_images = [
            {'name': tag, 'count': values['images']} for tag, values in total_stats.items()
        ]
        total_annotation_objects = [
            {'name': tag, 'count': values['objects']} for tag, values in total_stats.items()
        ]

        return stats_by_tags, total_annotated_images, total_annotation_objects
