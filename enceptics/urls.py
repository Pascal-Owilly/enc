
from django.contrib import admin
from django.urls import path, include

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.conf import settings
from django.conf.urls.static import static

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from blog_posts.views import BlogPostViewSet, LikeViewSet, CommentViewSet, FollowerViewSet
from accounts.views import ProfileViewset
from accounts.views import Profile
from authentication.views import PlaceViewset, PlaceInfoViewset, BookingViewSet
from authentication import views
router = DefaultRouter()
router.register(r'blogposts', BlogPostViewSet)
router.register(r'profile', ProfileViewset)
router.register(r'places', PlaceViewset)
router.register(r'place-info', PlaceInfoViewset)
router.register(r'book-place', BookingViewSet)
router.register(r'likes', LikeViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'followers', FollowerViewSet)
# router.register(r'create-order', CreateOrderViewSet, basename='create-order')
# router.register(r'capture-order', CaptureOrderView, basename='capture-order')

schema_view = get_schema_view(
   openapi.Info(
      title="Enceptics APIs",
      default_version='v1',
      description="Test description",
      contact=openapi.Contact(email="owillypascal@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [

    path('weather/', include('weather.urls')),  # Include the weather app's URLs
    path('mpesa-payments/', include('mpesa_payment.urls')),  

    # Payments

    # path('paypal/create/order', views.CreateOrderViewRemote.as_view(), name='ordercreate'),
    # path('paypal/capture/order', views.CaptureOrderView.as_view(), name='captureorder'),


    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('api/auth/', include('authentication.urls')),
    path('api/', include(router.urls)),
    path('profile/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    # path('', schema_view),

    # Paypal

    # path('capture-order/', CaptureOrderView.as_view(), name='capture-order'),



    # path('api/', include("rest_framework.urls")),
    # path('accounts/', include('accounts.urls')),

]

# Only add this when we are in debug mode.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
document_root=settings.MEDIA_ROOT)


