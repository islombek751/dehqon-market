from  rest_framework import serializers
from rest_framework import fields
from  .models import *

from django.contrib.auth import authenticate, get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.fields import ReadOnlyField
from .models import Profile


User = get_user_model()

class UserRegisterSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=64,read_only=True)
    email = serializers.EmailField(max_length=255)
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=200,write_only=True)
    password2 = serializers.CharField(max_length=200,write_only=True)

    def create(self, validated_data):
        email = validated_data.pop('email',None)
        username = validated_data.pop('username',None)
        password = validated_data.pop('password',None)
        password2 = validated_data.pop('password2',None)

        if password!=password2:
            raise serializers.ValidationError({"message":"password not matched"})
        if User.objects.filter(email=email).count()>0:
            raise serializers.ValidationError({"message":"Email already exist"})
        user = User(email=email,username=username,**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255,write_only=True)
    token = serializers.CharField(max_length=64,read_only=True)
    password = serializers.CharField(max_length=200,write_only=True)
    
    def validate(self, attrs):
        email = attrs.get("email",None)
        password = attrs.get("password",None)
        user = authenticate(email=email,password=password)
        print(user)
        if user is None:
            raise serializers.ValidationError({"message":"email or password error"})
        return user

class ProfileModelSerializer(serializers.ModelSerializer):
    user = UserRegisterSerializer(read_only=True)
    class Meta:
        model = Profile
        fields = "__all__"

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields  = ['id','title']

class BigCategorySerializer(serializers.ModelSerializer):
    category = SubCategorySerializer(many=True,read_only=True)
    class Meta:
        model = Category
        fields  = ['id','title','category']

class ProductsList(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','title','price','sale','price_in_sale','img','rating']

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id','img']


        
class ProductDetail(serializers.ModelSerializer):
    image = PhotoSerializer(many=True)
    tags = serializers.StringRelatedField(many=True)
    class Meta:
        model = Product
        fields = ['title','desc','price','sale','price_in_sale','img','rating','tags','image']
class UserSer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","username"]

class WishListSerializer(serializers.ModelSerializer):
    user = UserSer(read_only=True)
    product_list = ProductsList(many=True,read_only =True)
    class Meta:
        model = Wishlist
        fields = ["id","user","product_list"]

    def update(self, instance, validated_data):
        if instance:
            self.user=instance.user
        return super().update(instance, validated_data)



class CartItemSer(serializers.ModelSerializer):
    product = ProductsList(read_only=True)
    class Meta:
        model = CartItem
        fields = ['product',"quantity",'quantity',"price_ht"]

 
class CartSerilizer(serializers.ModelSerializer):
    user = UserSer(read_only=True)
    cart= serializers.SerializerMethodField('get_items')
    class Meta:
        model = Cart
        fields = ['id','user','cart']

    def get_items(self, container):
        items = CartItem.objects.filter(check=False)  # Whatever your query may be
        serializer = CartItemSer(instance=items, many=True)
        return serializer.data

class MahallaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mahalla
        fields = ["id","mahalla"]

class CreateOrderSerializer(serializers.ModelSerializer):
    cart = CartSerilizer(read_only=True)
    class Meta:
        model = Order
        fields = ["mahalla","phone","cart","over_all_products","dostavka"]



