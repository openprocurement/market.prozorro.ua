from rest_framework import routers

from criteria.views import CriteriaViewset


router = routers.SimpleRouter()
router.register('', CriteriaViewset)

urlpatterns = router.urls
