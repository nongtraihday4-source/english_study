"""
Custom DRF Renderer: VN-aware JSON.
Numbers in API responses keep their original values (for JS use),
but a companion `*_display` field is added for monetary/stat fields
when explicitly requested via `fmt_vn()` in serializers.
"""
import json

from rest_framework.renderers import JSONRenderer


class VNNumberJSONRenderer(JSONRenderer):
    """
    Extends Django REST Framework's JSONRenderer.
    Adds Vietnamese locale metadata in the response envelope.
    Actual number formatting is handled at serializer level via SerializerMethodField.
    """
    media_type = "application/json"
    charset = "utf-8"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context is None:
            renderer_context = {}

        response = renderer_context.get("response")

        # Wrap in envelope: {success, data, meta}
        if isinstance(data, dict) and ("results" in data or "count" in data):
            # Paginated response — keep DRF standard format
            envelope = data
        elif response and response.status_code >= 400:
            # Error response — keep as-is
            envelope = data
        else:
            envelope = {
                "success": True,
                "data": data,
            }

        return json.dumps(envelope, ensure_ascii=False, indent=None).encode(self.charset)
