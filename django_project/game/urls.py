from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import CategoryViewSet, GameViewSet, RoundViewSet


router = SimpleRouter()
router.register('category', CategoryViewSet)
router.register('game', GameViewSet)
router.register('round', RoundViewSet)


urlpatterns = router.urls