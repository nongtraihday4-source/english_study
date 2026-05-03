"""apps/notifications/views.py"""
from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")[:50]


class NotificationMarkReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            notif = Notification.objects.get(pk=pk, user=request.user)
        except Notification.DoesNotExist:
            return Response({"detail": "Không tìm thấy thông báo."}, status=404)
        notif.is_read = True
        notif.read_at = timezone.now()
        notif.save(update_fields=["is_read", "read_at"])
        return Response({"message": "Đã đánh dấu đã đọc."})
