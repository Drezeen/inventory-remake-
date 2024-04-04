from django.shortcuts import get_object_or_404, redirect, render
from .models import Inventoryandy
from django.contrib.auth.decorators import login_required
from .forms import AddInventoryForm, UpdateInventoryForm
from django.contrib import messages
from django_pandas.io import  read_frame
import pandas as pd
import plotly
import plotly.express as px
from celery import shared_task
import json
from django.db.models import Max, Min
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.http import HttpResponse
from django.template import Context, loader
from django.conf import settings
import os
import os


@login_required
def inventoryandy_list(request):
    inventories = Inventoryandy.objects.all()
    for inventory in inventories:
        inventory.sales_or_revenue = inventory.quantity_sold * inventory.cost_per_item
        inventory.remaining_quantity = inventory.quantity_in_stock - inventory.quantity_sold
    context ={
        "title": "Inventoryandy List",
        "inventories": inventories
    }
    return render(request, 'inventoryandy/inventoryandy_list.html', context=context)


@login_required
def per_product_view(request, pk):
    inventoryandy = get_object_or_404(Inventoryandy, pk=pk)
    context = {
        'inventoryandy': inventoryandy
    }
    
    return render(request, "inventoryandy/per_product.html", context=context)

@login_required
def add_product(request):
    if request.method == 'POST':
        add_form = AddInventoryForm(data=request.POST)
        if add_form.is_valid():
            new_inventoryandy =add_form.save(commit=False)
            new_inventoryandy.sales = float (add_form.data['cost_per_item']) * float(add_form.data['quantity_sold'])
            new_inventoryandy.remaining_quantity = float (add_form.data['quantity_in_stock']) - float(add_form.data['quantity_sold'])
            new_inventoryandy.save()
            messages.success(request, "Successfully Added Product")
            return redirect("/inventoryandy/")
    else:
        add_form = AddInventoryForm()
    return render (request, "inventoryandy/inventory_add.html",{"form": add_form})

@login_required
def delete_inventory(request, pk):
    inventoryandy = get_object_or_404(Inventoryandy, pk=pk)
    inventoryandy.delete()
    messages.success(request, "Successfully deleted Product")
    return redirect("/inventoryandy/")


@login_required
def product_analysis(request):
    # Find the inventory item with the highest sales
    best_performing_product = Inventoryandy.objects.aggregate(Max('sales'))
    highest_sales = best_performing_product['sales__max']
    best_performing_product = Inventoryandy.objects.filter(sales=highest_sales).first()
    
    most_product_in_stock = Inventoryandy.objects.aggregate(Max('quantity_in_stock'))
    highest_quantity = most_product_in_stock['quantity_in_stock__max']
    most_product_in_stock = Inventoryandy.objects.filter(quantity_in_stock=highest_quantity).first()
    
    worst_performing_product = Inventoryandy.objects.aggregate(Min('quantity_sold'))
    least_quantity_sold = worst_performing_product['quantity_sold__min']
    worst_performing_product = Inventoryandy.objects.filter(quantity_sold=least_quantity_sold).first()
    
    least_product_in_stock = Inventoryandy.objects.aggregate(Min('remaining_quantity'))
    least_quantity = least_product_in_stock['remaining_quantity__min']
    least_product_in_stock = Inventoryandy.objects.filter(remaining_quantity=least_quantity).first()
    
    most_purchased_product = Inventoryandy.objects.aggregate(Max('quantity_sold'))
    max_quantity_sold = most_purchased_product['quantity_sold__max']
    most_purchased_product = Inventoryandy.objects.filter(quantity_sold=max_quantity_sold).first()
    
    least_purchased_product = Inventoryandy.objects.aggregate(Min('quantity_sold'))
    min_quantity_sold = least_purchased_product['quantity_sold__min']
    least_purchased_product = Inventoryandy.objects.filter(quantity_sold=min_quantity_sold).first()
    
    lowest_income_product = Inventoryandy.objects.aggregate(Min('sales'))
    min_sales = lowest_income_product['sales__min']
    lowest_income_product = Inventoryandy.objects.filter(sales=min_sales).first()
    
    context = {
        "best_performing_product": best_performing_product,
        "most_product_in_stock":most_product_in_stock,
        "worst_performing_product": worst_performing_product,
        "least_product_in_stock": least_product_in_stock,
        "least_purchased_product" : least_purchased_product,
        "most_purchased_product" : most_purchased_product,
        "lowest_income_product" : lowest_income_product

    }
    return render(request, 'inventoryandy/product_analysis.html', context=context)




@login_required
def update_inventory(request, pk):
    inventoryandy = get_object_or_404(Inventoryandy, pk=pk)
    if request.method == "POST":
        updateForm = UpdateInventoryForm(request.POST, instance=inventoryandy)
        if updateForm.is_valid():
            updateForm.save()
            # Calculate sales based on the updated quantity sold and cost per item
            inventoryandy.sales = float(inventoryandy.cost_per_item) * float(inventoryandy.quantity_sold)
            inventoryandy.save()
            messages.success(request, "Product Successfully Updated")
            return redirect("/inventoryandy/")
    else:
        updateForm = UpdateInventoryForm(instance=inventoryandy)
    context = {"form": updateForm}
    return render(request, "inventoryandy/inventory_update.html", context)

@login_required
def dashboard(request):
    inventories = Inventoryandy.objects.all()
    
    df = read_frame(inventories)
    
    df['last_sales_date'] = pd.to_datetime(df['last_sales_date'])
    
    sales_graph = df.groupby(by="last_sales_date", as_index=False, sort=False)['sales'].sum()
    sales_graph = px.line(sales_graph, x="last_sales_date", y="sales", title="ANDY Sales Trend")
    sales_graph = json.dumps(sales_graph, cls=plotly.utils.PlotlyJSONEncoder)
    
    numeric_columns = ['quantity_sold', 'sales']
    best_performing_product_df = df.groupby(by="name")[numeric_columns].sum().sort_values(by="quantity_sold")
    best_performing_product = px.bar(best_performing_product_df, x = best_performing_product_df.index, y = best_performing_product_df.quantity_sold, title = "Andy's Best Performing Product")
    best_performing_product = json.dumps(best_performing_product, cls = plotly.utils.PlotlyJSONEncoder)
    
    numeric_columns = ['quantity_sold', 'sales',]
    best_income_generating_product_df = df.groupby(by="name")[numeric_columns].sum().sort_values(by="sales")
    best_income_generating_product = px.bar(best_income_generating_product_df, x = best_income_generating_product_df.index, y = best_income_generating_product_df.sales, title = "Andy's Best Income Generating Product")
    best_income_generating_product = json.dumps(best_income_generating_product, cls = plotly.utils.PlotlyJSONEncoder)
    
    numeric_columns = ['quantity_sold', 'sales', 'quantity_in_stock']
    most_product_in_stock_df = df.groupby(by="name")[numeric_columns].sum().sort_values(by="quantity_in_stock")
    most_product_in_stock =px.pie(most_product_in_stock_df, names = most_product_in_stock_df.index, values = most_product_in_stock_df.quantity_in_stock, title = " Andy's intial Most Product in Stock")
    most_product_in_stock = json.dumps(most_product_in_stock, cls = plotly.utils.PlotlyJSONEncoder)
    
    numeric_columns = ['remaining_quantity']
    current_product_in_stock_df = df.groupby(by="name")[numeric_columns].sum().sort_values(by="remaining_quantity")
    current_product_in_stock = px.pie(current_product_in_stock_df, names = current_product_in_stock_df.index, values = current_product_in_stock_df.remaining_quantity, title="Andy's Current Product in Stock")
    current_product_in_stock = json.dumps(current_product_in_stock, cls=plotly.utils.PlotlyJSONEncoder)
    
    
    # Calculate the remaining quantity for each product
    df['remaining_quantity'] = df['quantity_in_stock'] - df['quantity_sold']
    
    # Group the products by name and sum up the remaining quantities
    remaining_product_in_stock_df = df.groupby(by="name")['remaining_quantity'].sum()
    
    # Create a pie chart for the remaining products
    remaining_product_chart = px.pie(remaining_product_in_stock_df, names=remaining_product_in_stock_df.index, values=remaining_product_in_stock_df.values, title="Andy's Remaining Product in Stock")
    remaining_product_chart = json.dumps(remaining_product_chart, cls=plotly.utils.PlotlyJSONEncoder)
    
    # Calculate the total sales for each product
    total_sales_per_product_df = df.groupby(by="name")['sales'].sum().sort_values(ascending=False)
    
    # Get the most trending product (product with the highest total sales)
    most_trending_product = total_sales_per_product_df.head(1).index[0]
    
    # Filter the dataframe to get data only for the most trending product
    most_trending_product_data = df[df['name'] == most_trending_product]
    
    # Create a line graph for the most trending product
    most_trending_product_graph = px.line(most_trending_product_data, x='last_sales_date', y='sales', title=f"Sales Trend for {most_trending_product}")
    most_trending_product_graph = json.dumps(most_trending_product_graph, cls=plotly.utils.PlotlyJSONEncoder)
    
    
    context = { 
            "sales_graph": sales_graph,
            "best_performing_product" : best_performing_product,
            "best_income_generating_product" : best_income_generating_product,
            "most_product_in_stock" : most_product_in_stock,
            "remaining_product_chart": remaining_product_chart,
            "most_trending_product_graph": most_trending_product_graph,
            "current_product_in_stock" : current_product_in_stock
    }
    
    return render(request, "inventoryandy/dashboard.html", context=context)

def generate_barcode(data):
    # Create a Code128 barcode object
    code128 = barcode.get_barcode_class('code128')
    
    # Generate the barcode
    generated_code = code128(data, writer=ImageWriter())
    
    # Set the path where the barcode image will be saved
    barcode_filename = f"{data}.png"
    barcode_path = os.path.join(settings.MEDIA_ROOT, "barcodes", barcode_filename)
    
    # Save the barcode image
    generated_code.save(barcode_path)

    # Debugging output
    print("Barcode saved at:", barcode_path)

    # Return the filename of the saved barcode image
    return barcode_filename

from django.http import JsonResponse

def generate_barcode_view(request):
    if request.method == 'GET':
        barcode_value = request.GET.get('barcode_value')
        if barcode_value:
            # Find the inventory item associated with the scanned barcode
            inventory_item = get_object_or_404(Inventoryandy, barcode=barcode_value)
            # Increment the quantity sold by 1
            inventory_item.quantity_sold += 1
            inventory_item.save()
            # Generate a unique ID for the scanned item
            unique_id = inventory_item.pk  # Assuming primary key is used as the unique ID
            
            # Return a JSON response with the unique ID and updated quantity sold
            return JsonResponse({'success': True, 'unique_id': unique_id, 'quantity_sold': inventory_item.quantity_sold})
    
    # Return a JSON response indicating failure
    return JsonResponse({'success': False}, status=400)
