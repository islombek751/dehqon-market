from django.db import models
from rest_framework.authtoken.models import Token

# Create your models here.
from django.db import models
from ckeditor.fields import RichTextField
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField
# Create your models here.
from parler.models import TranslatableModel,TranslatedFields

from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have an username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            username=username,
            password=password,
            
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    username = models.CharField(max_length=200, unique=True)
    
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    # EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
        
    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
    
    @property
    def token(self):
        try:
            token = Token.objects.get(user=self)
        except Token.DoesNotExist:
            token = Token.objects.create(user=self)
        print(token)
        return token.key

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
    

	


class Main(models.Model):
	main_background = models.ImageField(verbose_name='asosiy sahifadagi orqa fon rasmi: ', help_text='1920x753 px')
	main_text = models.CharField(verbose_name='asosiy sahifa fon rasmi ustidagi tekst:', help_text='',max_length=250)



def image_folder(instance, filename):
	filename = instance.title +'.'+filename.split('.')[1]
	return"{0}/{1}".format(instance.title, filename) 


class Posts(TranslatableModel):
	translations = TranslatedFields(
	title = models.CharField('Nomi',max_length=250),
	description = RichTextField())
	image = models.ImageField('Foto', upload_to=image_folder)
	date = models.DateTimeField( auto_now_add = True)
	class Meta:
		verbose_name = 'Maqola'
		verbose_name_plural = 'Maqolalar'
	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('app:posts',kwargs={'id':self.id})


class Contact_m(models.Model):
	name = models.CharField('Ism',max_length=30)
	email = models.CharField('Email',max_length=60)
	subject = models.CharField('Mavzu',max_length=100)
	message = models.TextField('Xabar')
	class Meta:
		verbose_name = 'Contact'
		verbose_name_plural = 'Contacts'
	def __str__(self):
		return self.name

class Informations(models.Model):
	title_of_site = models.CharField('Sayt sarlavhasi',max_length=250)
	image = models.ImageField('Logotip', upload_to=image_folder)
	favicon = models.ImageField('Sayt sarlavhasi yonidagi rasm', upload_to=image_folder)
	address = models.CharField('Address',max_length=1024)
	call = models.CharField('Telefon raqam',max_length=1024)
	email = models.CharField('Email address',max_length=1024)
	
	class Meta:
		verbose_name = 'Info'
		verbose_name_plural = 'Informations'
	def __str__(self):
		return self.title

class Category(models.Model):
	title = models.CharField('Kategoriyalar', max_length=50)
	class Meta:
		verbose_name = 'Kategoriya'
		verbose_name_plural = 'Kategoriyalar'

	def __str__(self):
		return self.title

class Subcategory(models.Model):
	title = models.CharField('Kategoriyalar', max_length=50)
	category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name='category')
	class Meta:
		verbose_name = 'SubKategoriya'
		verbose_name_plural = 'Kategoriya ichidagi kategoriyalar'

	def __str__(self):
		return f"{self.title}"

class Tags(models.Model):
	tag = models.CharField(max_length=20)
	def __str__(self):
		return self.tag

	
	class Meta:
		verbose_name = "teg"
		verbose_name_plural = "Teglar ro'yhati"


class Product(models.Model):
	title = models.CharField(max_length=150, verbose_name="Name/Nomi")
	desc = RichTextField(verbose_name="Description/Mahsulot haqida")
	category = models.ForeignKey(Subcategory, on_delete=models.CASCADE, verbose_name="Category/Turi")
	kg = models.BooleanField(help_text="Agar maxsulot 'kg' da o'lchanadigan bo'lsa, ushbu belgini yoqing!")
	price = models.PositiveIntegerField(default=0,verbose_name="Narxi")
	sale = models.BooleanField(verbose_name="Sale/Aksiya")
	price_in_sale = models.PositiveIntegerField(default=0,blank=True,help_text="Agar tepadagi 'Aksiya' belgisi yoqilgan bo'lsagina inobatga olinadi!", verbose_name="Aksiyadagi narxi")
	cr_date = models.DateTimeField(auto_now=True)
	tags = models.ManyToManyField(Tags,null=True,blank=True)
	img = models.ImageField(verbose_name='Rasm')
	rating = models.PositiveSmallIntegerField(default=1)

	def __str__(self):
		return self.title

	class Meta:
		verbose_name="Mahsulot"
		verbose_name_plural = "Mahsulotlar"

class Photo(models.Model):
	img = models.ImageField(upload_to="img")
	product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='image')


class Profile(models.Model):
	user = models.OneToOneField("api.User",on_delete=models.CASCADE)
	name = models.CharField(max_length=35)
	phone = models.CharField(max_length=35)
	adress = models.CharField(max_length=150)
	image = models.ImageField(upload_to="profile_image")

	def __str__(self):
		return str(self.number)

	def __str__(self):
		return self.adress


class Wishlist(models.Model):
	user = models.OneToOneField(User,on_delete = models.CASCADE,blank=True)
	product_list = models.ManyToManyField(Product,blank=True,null=True,related_name="product_list")


class Review(models.Model):
	product =models.ForeignKey(Product,on_delete = models.CASCADE,blank =True)
	user = models.ForeignKey(User,on_delete = models.CASCADE,blank=True)
	review = models.TextField()
	date = models.DateTimeField(auto_now_add=True)
	rating = models.PositiveSmallIntegerField(default=1)
	class Meta:
		ordering = ["-date"]
		verbose_name = 'Review'
		verbose_name_plural = 'Reviews'



class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price_ht = models.IntegerField(blank=True,default=1)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,related_name="cart")
    check = models.BooleanField(default=False)

    # def price(self):
    #     return self.price_ht + 
class Mahalla(models.Model):
	mahalla = models.CharField(max_length=200)
	dostavka = models.PositiveIntegerField(default=7000)

	def __str__(self):
		return self.mahalla

	class Meta:
		verbose_name = "mahalla"
		verbose_name_plural = "Mahallalar ro'yhati"


class Order(models.Model):
	mahalla = models.ForeignKey(Mahalla,on_delete=models.CASCADE,related_name='mahall')
	phone = models.CharField(max_length=17)
	cart = models.ForeignKey(Cart,on_delete=models.CASCADE,null=True)
	over_all_products = models.PositiveIntegerField(default=0)
	dostavka = models.PositiveIntegerField(default=0)
	date = models.DateTimeField(auto_now_add=True)
	def __str__(self):
		return f"{self.mahalla} ga {self.phone}"

class OrderId(models.Model):
	date = models.DateTimeField(auto_now_add=True)

	
# class MyModel(models.Model):
#     location = OSMField()
#     location_lat = LatitudeField()
#     location_lon = LongitudeField()

class Hamkorlar(models.Model):
	manzil = models.URLField(blank=True,help_text='Url manzili')
	photo = models.ImageField(help_text='132x84')

# Telegram

class UserTelegram(models.Model):
	phone = models.CharField(max_length=17)
	otp = models.CharField(max_length=30)
	telegram_id = models.CharField(max_length=50)
	date = models.DateTimeField(auto_now_add=True)
	def __str__(self):
		return f"{self.otp} ga {self.phone}"


class CartTelegram(models.Model):
	user = models.ForeignKey(UserTelegram,on_delete=models.CASCADE)

class CartItemTelegram(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	quantity = models.IntegerField(default=1)
	price_ht = models.IntegerField(blank=True,default=1)
	cart = models.ForeignKey(CartTelegram,on_delete=models.CASCADE)
	check = models.BooleanField(default=False)

class TelegramOrder(models.Model):
	mahalla = models.CharField(Mahalla,max_length=100)
	phone = models.CharField(max_length=17)
	cart = models.ForeignKey(CartTelegram,on_delete=models.CASCADE,null=True)
	over_all_products = models.PositiveIntegerField(default=0)
	km = models.DecimalField(max_digits=10,decimal_places=2)
	dostavka = models.DecimalField(max_digits=20,decimal_places=2)
	date = models.DateTimeField(auto_now_add=True)
	def __str__(self):
		return f"{self.mahalla} ga {self.phone}"