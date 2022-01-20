from django.urls import path
from .views import *

urlpatterns = [
    path('register/',UserRegisterView.as_view()),
    path('login/',UserLoginView.as_view()),
    path('logout/',Logout.as_view()),
    # path('profile/',ProfileListAPIView.as_view()),
    path('profile/<int:pk>/',ProfileUpdateDestroyAPIView.as_view()),
    path('bigcategory/list', BigCategoryList.as_view()),
    path('products/list/categoryid/<int:pk>', ProductsByCategoryIdList.as_view()),
    path('product/<int:pk>', ProductDetailApi.as_view()),
    path('products/list/sale', ProductsBySale.as_view()),
    path('product_search/',ProductSearchView.as_view()),
    path('wishlist/add/product_id/<int:pk>',WishListAddApiView.as_view()),
    path('wishlist/remove/product_id/<int:pk>',WishListRemoveApiView.as_view()),
    path('cart/add/product_id/<int:pk>',CartAddApiView.as_view()),
    path('cart/remove/product_id/<int:pk>',CartRemoveApiView.as_view()),
    path('mahalla/list', MahallaListApiView.as_view()),
    path('order/create', CreateOrderApiView.as_view()),
    
]


