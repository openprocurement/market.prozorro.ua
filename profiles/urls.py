from rest_framework import routers

from profiles.views import ProfileViewSet


router = routers.SimpleRouter()
router.register('', ProfileViewSet)

urlpatterns = router.urls
