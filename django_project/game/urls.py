from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import CategoryViewSet, GameViewSet, RoundViewSet, top_players


router = SimpleRouter()
router.register('category', CategoryViewSet)
router.register('game', GameViewSet)
router.register('round', RoundViewSet)

urlpatterns = [
    path('top_players/', top_players, name='top_players'),
]

urlpatterns += router.urls