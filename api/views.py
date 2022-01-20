from django.contrib.auth import logout
from django.db.models import query
from .serializers import *
from rest_framework import generics,views,filters,status,permissions,viewsets
from rest_framework.response import Response
from .models import *
from django.http import Http404,HttpResponseRedirect, request
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import  get_object_or_404
import telebot

TOKEN = "5061556702:AAEX99Z-11f5OWDzeyb00KPUmT6FPlt_OjI"
chat_id = '-785780604'
bot = telebot.TeleBot(TOKEN,parse_mode='html')
class UserRegisterView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

class UserLoginView(views.APIView):
    def post(self,request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer)
        return Response(serializer.data)


# class ProfileListAPIView(generics.ListAPIView):
#     queryset = Profile.objects.all()
#     serializer_class = ProfileModelSerializer

class ProfileUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileModelSerializer
    permission_classes = [permissions.IsAuthenticated]
# I've sent list of main categories here!
class BigCategoryList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = BigCategorySerializer

# I've sent products list by category id!
class ProductsByCategoryIdList(views.APIView):
    def get_objects(self,pk):
        try:
            return Product.objects.filter(category_id=pk)
        except Category.DoesNotExist:
            raise Http404
    def get(self, request,pk, format=None):
        products = self.get_objects(pk=pk)
        serializer = ProductsList(products, many=True)
        return Response(serializer.data)
    
    
class ProductsBySale(views.APIView):
    def get_objects(self):
        try:
            return Product.objects.filter(sale=True)
        except Product.DoesNotExist:
            raise Http404
    def get(self, request, format=None):
        products = self.get_objects()
        serializer = ProductsList(products, many=True)
        return Response(serializer.data)


class ProductDetailApi(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetail
# it's created for lookup with url: http://127.0.0.1:8000/api/product_search/?search=l
class ProductSearchView(generics.ListAPIView):
      queryset = Product.objects.all()
      serializer_class = ProductsList
      filter_backends = (filters.SearchFilter,)
      search_fields = ['title','tags__tag']
      

class WishListAddApiView(generics.ListAPIView):
    queryset = Wishlist.objects.all()
    serializer_class = WishListSerializer
    permission_classes = [permissions.IsAuthenticated]
    def list(self,request,pk):
        product_id = pk
        product = get_object_or_404(Product,id=product_id)
        user_wishlist, created = Wishlist.objects.get_or_create(user=self.request.user) 
        user_wishlist.product_list.add(product)
        user_wishlist.save()
        serializer = WishListSerializer(user_wishlist,read_only=True)
        return Response(serializer.data) 

class WishListRemoveApiView(generics.ListAPIView):
    queryset = Wishlist.objects.all()
    serializer_class = WishListSerializer
    permission_classes = [permissions.IsAuthenticated]
    def list(self,request,pk):
        product_id = pk
        product = get_object_or_404(Product,id=product_id)
        user_wishlist, created = Wishlist.objects.get_or_create(user=self.request.user) 
        user_wishlist.product_list.remove(product)
        user_wishlist.save()
        serializer = WishListSerializer(user_wishlist,read_only=True)
        return Response(serializer.data) 
class CartAddApiView(generics.ListAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerilizer
    permission_classes = [permissions.IsAuthenticated]
    def list(self,request,pk):
        product_id = pk
        product = get_object_or_404(Product,id=product_id)
        user_cart, created = Cart.objects.get_or_create(user=self.request.user) 
        if CartItem.objects.filter(cart = user_cart, product=product):
            if CartItem.objects.filter(cart = user_cart, product=product,check=False):
                item = CartItem.objects.get(cart = user_cart, product=product)
                item.quantity += 1 
                item.save()
                if product.sale:
                    item.price_ht = item.quantity * product.price_in_sale
                else:
                    item.price_ht = item.quantity * product.price
                item.save()
            else:
                return Response({"message":"This item already not exsisted! "}, status=status.HTTP_404_NOT_FOUND)
        else:    
            item  = CartItem.objects.create(cart = user_cart, product=product,quantity = 1)
            item.save()
            if product.sale:
                item.price_ht = item.quantity * product.price_in_sale
            else:
                item.price_ht = item.quantity * product.price
            item.save()
        user_cart.save()
        serializer = CartSerilizer(user_cart,read_only=True)
        return Response(serializer.data) 


class CartRemoveApiView(generics.ListAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerilizer
    permission_classes = [permissions.IsAuthenticated]
    def list(self,request,pk):
        product_id = pk
        product = get_object_or_404(Product,id=product_id)
        user_cart = get_object_or_404(Cart,user=self.request.user) 
        if CartItem.objects.filter(cart = user_cart, product=product, check = False):
            item = CartItem.objects.get(cart = user_cart, product=product)
            item.quantity -= 1
            item.save()
            if product.sale:
                item.price_ht = item.quantity * product.price_in_sale
            else:
                item.price_ht = item.quantity * product.price
            item.save()

        user_cart.save()
        serializer = CartSerilizer(user_cart,read_only=True)
        return Response(serializer.data) 

class MahallaListApiView(generics.ListAPIView):
    queryset = Mahalla.objects.all()
    serializer_class = MahallaSerializer
    permission_classes = [permissions.IsAuthenticated]

class CreateOrderApiView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class  = CreateOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        cart = get_object_or_404(Cart,user=self.request.user)
        myorder = OrderId()
        myorder.save()
        order_id = myorder.id 
        price = 0
        my_message = ""
        b = 0
        for i in CartItem.objects.filter(cart=cart,check=False):
            price += i.price_ht
            b += 1
            if i.product.kg:
                if i.product.sale:
                    my_message += (f"№: {order_id}\n\n📦{b}-mahsulot: <b>{i.product}</b>\n⚖️Miqdor: <b>{i.quantity} kg</b>\n💸Summa: {i.product.price_in_sale} so'm * {i.quantity} kg = {i.product.price_in_sale*i.quantity} so'm\n\n")    
                else:
                    my_message += (f"№: {order_id}\n\n📦{b}-mahsulot: <b>{i.product}</b>\n⚖️Miqdor: <b>{i.quantity} kg</b>\n💸Summa: {i.product.price} so'm * {i.quantity} kg = {i.product.price*i.quantity} so'm\n\n")    

            else:
                if i.product.sale:
                    my_message += (f"№: {order_id}\n\n📦{b}-mahsulot: <b>{i.product}</b>\n⚖️Miqdor: <b>{i.quantity} dona</b>\n💸Summa: {i.product.price_in_sale}so'm * {i.quantity} dona = {i.product.price_in_sale*i.quantity} so'm\n\n")    
                else:
                    my_message += (f"№: {order_id}\n\n📦{b}-mahsulot: <b>{i.product}</b>\n⚖️Miqdor: <b>{i.quantity} dona</b>\n💸Summa: {i.product.price} so'm * {i.quantity} dona = {i.product.price*i.quantity} so'm\n\n")    
        mahalla_id = serializer.validated_data["mahalla"]
        dostavka = Mahalla.objects.get(id=mahalla_id.id).dostavka
        over_all_products = price
        my_message+= f"📞Telfon raqam: {serializer.validated_data['phone']}\n🪧Mahalla: {mahalla_id}\n\n"
        my_message += f"💸Mahsulotlar summasi:<b> {over_all_products} so'm</b>\n🚚Yetkazib berish xizmati:<b> {dostavka} so'm</b>\n💰Jami summa:<b> {over_all_products+dostavka} so'm</b>\n\n{myorder.date}"
        if CartItem.objects.filter(cart=cart,check=False):
            bot.send_message(chat_id,my_message)
        serializer.save(cart=cart,over_all_products=over_all_products,dostavka=dostavka)
        for i in CartItem.objects.filter(cart=cart,check=False):
            i.check = True 
            i.save()   
        return super().perform_create(serializer)

class Logout(views.APIView):
    def get(self, request, format=None):
        # simply delete the token to force a login
        request.user.auth_token.delete()
        logout(request)
        return HttpResponseRedirect(redirect_to='http://127.0.0.1:8000/api/bigcategory/list')