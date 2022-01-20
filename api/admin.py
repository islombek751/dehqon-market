from django.contrib import admin


from .models import CartItemTelegram,CartTelegram, UserTelegram,Mahalla, Order, Profile, Review,Main, User,Wishlist,Posts, Contact_m, Informations, Category,Cart,CartItem, Subcategory, Product, Photo, Tags,Hamkorlar
# Register your models here.
from parler.admin import TranslatableAdmin,TranslatableTabularInline

# admin.site.register(Posts)
# admin.site.register(Order)
@admin.register(Mahalla)
class MahallaAdmin(admin.ModelAdmin):
	list_display = ['mahalla', 'dostavka']
	fieldsets = (
    ('Main informations about Mahalla', {'fields': ['mahalla','dostavka']}),
  )
admin.site.register(User)
# admin.site.register(Profile)
admin.site.register(UserTelegram)
admin.site.register(CartTelegram)
admin.site.register(CartItemTelegram)
# admin.site.register(Informations)
admin.site.register(Tags)
# admin.site.register(Wishlist)

# admin.site.register(Cart)
# admin.site.register(CartItem)

# admin.site.register(Main)
# admin.site.register(Review)
# admin.site.register(Hamkorlar)


class picture(admin.TabularInline):
	model = Photo
	extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ['title', ]
	fieldsets = (
    ('Main informations about Products', {'fields': ['title']}),
  )

@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
	list_display = ['title']
	fieldsets = (
    ('Main informations about Products', {'fields': ['title','category']}),

  )
	

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ['title', 'category', 'price', "price_in_sale","sale"]
	search_fields = (
        "title",
        "category__title",
    )
	list_filter = [
         "category__title",
         "sale",
    ]
	fieldsets = (
    ('Main informations about Products', {'fields': ['title','category','desc','img','kg','price','sale','price_in_sale','tags']}),
  )
	inlines = [picture]