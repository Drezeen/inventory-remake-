from django.urls import path
from .views import delete_inventory, inventoryandy_list, per_product_view, add_product, update_inventory,product_analysis, dashboard, generate_barcode
from . import views
urlpatterns = [
    path("", inventoryandy_list, name="inventoryandy_list"),
    path("per_product/<int:pk>", per_product_view, name="per_product"),
    path("add_inventory/", add_product, name="add_inventory"),
    path("delete/<int:pk>", delete_inventory, name="delete_inventory"),
    path("update/<int:pk>", update_inventory, name="update_inventory"),
    path("dashboard/", dashboard, name="dashboard"),
    path('generate_barcode/', views.generate_barcode, name='generate_barcode'),
    path("product_analysis/", product_analysis, name="product_analysis")
    
    
]

