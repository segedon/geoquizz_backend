from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import CategoryViewSet, GameViewSet


router = SimpleRouter()
router.register('category', CategoryViewSet)
router.register('game', GameViewSet)


urlpatterns = router.urls