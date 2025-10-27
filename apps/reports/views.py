from rest_framework import views, response


class HealthCheckView(views.APIView):
    def get(self, request):
        return response.Response({'status': 'ok'})
