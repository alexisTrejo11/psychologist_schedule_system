from rest_framework import serializers


class PaginationMetadataSerializer(serializers.Serializer):
    total_items = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    current_page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    has_next = serializers.BooleanField()
    has_previous = serializers.BooleanField()


class PaginatedResponseSerializer(serializers.Serializer):
    def __init__(self, *args, item_serializer=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['items'] = serializers.ListField(child=item_serializer())

    metadata = PaginationMetadataSerializer()