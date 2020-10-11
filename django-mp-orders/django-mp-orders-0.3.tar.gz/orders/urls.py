
from django.urls import path, include

from django.conf.urls.i18n import i18n_patterns

from orders import views


orders_urlpatterns = i18n_patterns(

    path(
        'orders/',
        include(
            (
                [
                    path('checkout/', views.checkout, name='checkout')
                ],
                'orders'
            )
        )
    ),

    path('delivery/', include('delivery.urls'))

)
