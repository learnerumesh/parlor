from pickle import FALSE
from django.shortcuts import redirect, render
from django.http import HttpResponse
from flask import jsonify
from posApp.models import Category, Products, Sales, salesItems
from django.db.models import Count, Sum
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
import json, sys
from .models import *
from datetime import date, datetime, timedelta
from django.http import HttpResponseRedirect

# Login
def login_user(request):
    logout(request)
    resp = {"status":'failed','msg':''}
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status']='success'
            else:
                resp['msg'] = "Incorrect username or password"
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp),content_type='application/json')

#Logout
def logoutuser(request):
    logout(request)
    return redirect('/')

# Create your views here.
@login_required
def home(request):
    now = datetime.now()
    current_year = now.strftime("%Y")
    current_month = now.strftime("%m")
    current_day = now.strftime("%d")
    categories = len(Category.objects.all())
    products = len(Products.objects.all())
    transaction = len(Sales.objects.filter(
        date_added__year=current_year,
        date_added__month = current_month,
        date_added__day = current_day
    ))
    today_sales = Sales.objects.filter(
        date_added__year=current_year,
        date_added__month = current_month,
        date_added__day = current_day
    ).all()
    total_sales = sum(today_sales.values_list('grand_total',flat=True))
    month_sales = Sales.objects.filter(
        date_added__year=current_year,
        date_added__month = current_month
    ).all()
    this_month = sum(month_sales.values_list('grand_total',flat=True))
    # print("yo mahina ko : "+str(this_month))
    #products added this months
    this_month_prod=Products.objects.filter(
        date_added__year=current_year,
        date_added__month = current_month
    ).all()
    this_month_product=len(this_month_prod.values_list('code',flat=True))

    #getting this month salary payment to all employees
    month_sal = Payroll.objects.filter(
        Paid_Date__year=current_year,
        Paid_Date__month = current_month
    ).all()
    month_salary = sum(month_sal.values_list('Amount',flat=True))
    lastMonth = date.today().replace(day=1) - timedelta(days=1)
    lastMonth=lastMonth.strftime("%m")
    last_month_sales = Sales.objects.filter(
        date_added__year=current_year,
        date_added__month = lastMonth
    ).all()
    last_month_sales = sum(last_month_sales.values_list('grand_total',flat=True))
    dct=['Last Month','This Month']
    dct1=[last_month_sales,this_month]

    #for today and yesterday sales
    
    yesterday = int(current_day)-1
    yesterday_sales = Sales.objects.filter(
        date_added__year=current_year,
        date_added__month = current_month,
        date_added__day=str(yesterday)
    ).all()
    yesterday_sales = sum(yesterday_sales.values_list('grand_total',flat=True))
    days=['Yesterday','Today']
    sales=[yesterday_sales,total_sales]

    context = {
        'page_title':'Home',
        'categories' : categories,
        'products' : products,
        'transaction' : transaction,
        'total_sales' : total_sales,
        'this_month':this_month,
        'this_month_product':this_month_product,
        'month_salary':month_salary,
        'dct':dct,
        'dct1':dct1,
        'days':days,
        'sales':sales,
    }
    
    return render(request, 'posApp/home.html',context)


def about(request):
    context = {
        'page_title':'About',
    }
    return render(request, 'posApp/about.html',context)

#Categories
@login_required
def category(request):
    category_list = Category.objects.all()
    # category_list = {}
    context = {
        'page_title':'Category List',
        'category':category_list,
    }
    return render(request, 'posApp/category.html',context)
@login_required
def manage_category(request):
    category = {}
    if request.method == 'GET':
        data =  request.GET
        id = ''
        if 'id' in data:
            id= data['id']
        if id.isnumeric() and int(id) > 0:
            category = Category.objects.filter(id=id).first()
    
    context = {
        'category' : category
    }
    return render(request, 'posApp/manage_category.html',context)

@login_required
def save_category(request):
    data =  request.POST
    resp = {'status':'failed'}
    try:
        if (data['id']).isnumeric() and int(data['id']) > 0 :
            save_category = Category.objects.filter(id = data['id']).update(name=data['name'], description = data['description'],status = data['status'])
        else:
            save_category = Category(name=data['name'], description = data['description'],status = data['status'])
            save_category.save()
        resp['status'] = 'success'
        messages.success(request, 'Category Successfully saved.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def delete_category(request):
    data =  request.POST
    resp = {'status':''}
    try:
        Category.objects.filter(id = data['id']).delete()
        resp['status'] = 'success'
        messages.success(request, 'Category Successfully deleted.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

# Products
@login_required
def products(request):
    # product_list = Products.objects.all()
    product_list = Products.objects.all().order_by()
    context = {
        'page_title':'Product List',
        'products':product_list,
    }
    return render(request, 'posApp/products.html',context)
@login_required
def manage_products(request):
    product = {}
    categories = Category.objects.filter(status = 1).all()
    if request.method == 'GET':
        data =  request.GET
        id = ''
        if 'id' in data:
            id = data['id']
        if id.isnumeric() and int(id) > 0:
            product = Products.objects.filter(id=id).first()
    context = {
        'product' : product,
        'categories' : categories
    }
    return render(request, 'posApp/manage_product.html',context)
def test(request):
    categories = Category.objects.all()
    context = {
        'categories' : categories
    }
    return render(request, 'posApp/test.html',context)
@login_required
def save_product(request):
    data =  request.POST
    resp = {'status':'failed'}
    id= ''
    if 'id' in data:
        id = data['id']
    if id.isnumeric() and int(id) > 0:
        check = Products.objects.exclude(id=id).filter(code=data['code']).all()
    else:
        check = Products.objects.filter(code=data['code']).all()
    if len(check) > 0 :
        resp['msg'] = "Product Code Already Exists in the database"
    else:
        category = Category.objects.filter(id = data['category_id']).first()
        try:
            if (data['id']).isnumeric() and int(data['id']) > 0 :
                save_product = Products.objects.filter(id = data['id']).update(code=data['code'], category_id=category, name=data['name'], description = data['description'], price = float(data['price']),status = data['status'])
            else:
                save_product = Products(code=data['code'], category_id=category, name=data['name'], description = data['description'], price = float(data['price']),status = data['status'])
                save_product.save()
            resp['status'] = 'success'
            messages.success(request, 'Product Successfully saved.')
        except:
            resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")



@login_required
def delete_product(request):
    data =  request.POST
    resp = {'status':''}
    try:
        Products.objects.filter(id = data['id']).delete()
        resp['status'] = 'success'
        messages.success(request, 'Product Successfully deleted.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")
@login_required
def pos(request):
    products = Products.objects.filter(status = 1)
    product_json = []
    for product in products:
        product_json.append({'id':product.id, 'name':product.name, 'price':float(product.price)})
    context = {
        'page_title' : "Point of Sale",
        'products' : products,
        'product_json' : json.dumps(product_json)
    }
    # return HttpResponse('')
    return render(request, 'posApp/pos.html',context)

@login_required
def checkout_modal(request):
    grand_total = 0
    if 'grand_total' in request.GET:
        grand_total = request.GET['grand_total']
    context = {
        'grand_total' : grand_total,
    }
    return render(request, 'posApp/checkout.html',context)

@login_required
def save_pos(request):
    resp = {'status':'failed','msg':''}
    data = request.POST
    pref = datetime.now().year + datetime.now().year
    i = 1
    while True:
        code = '{:0>5}'.format(i)
        i += int(1)
        check = Sales.objects.filter(code = str(pref) + str(code)).all()
        if len(check) <= 0:
            break
    code = str(pref) + str(code)

    try:
        sales = Sales(code=code, sub_total = data['sub_total'], tax = data['tax'], tax_amount = data['tax_amount'], grand_total = data['grand_total'], tendered_amount = data['tendered_amount'], amount_change = data['amount_change']).save()
        sale_id = Sales.objects.last().pk
        i = 0
        for prod in data.getlist('product_id[]'):
            product_id = prod 
            sale = Sales.objects.filter(id=sale_id).first()
            product = Products.objects.filter(id=product_id).first()
            qty = data.getlist('qty[]')[i] 
            price = data.getlist('price[]')[i] 
            total = float(qty) * float(price)
            # print({'sale_id' : sale, 'product_id' : product, 'qty' : qty, 'price' : price, 'total' : total})
            salesItems(sale_id = sale, product_id = product, qty = qty, price = price, total = total).save()
            i += int(1)
        resp['status'] = 'success'
        resp['sale_id'] = sale_id
        messages.success(request, "Sale Record has been saved.")
    except:
        resp['msg'] = "An error occured"
        # print("Unexpected error:", sys.exc_info()[0])
    return HttpResponse(json.dumps(resp),content_type="application/json")

@login_required
def salesList(request):
    sales = Sales.objects.all()
    sale_data = []
    for sale in sales:
        data = {}
        for field in sale._meta.get_fields(include_parents=False):
            if field.related_model is None:
                data[field.name] = getattr(sale,field.name)
        data['items'] = salesItems.objects.filter(sale_id = sale).all()
        data['item_count'] = len(data['items'])
        if 'tax_amount' in data:
            data['tax_amount'] = format(float(data['tax_amount']),'.2f')
        # print(data)
        sale_data.append(data)
    # print(sale_data)
    context = {
        'page_title':'Sales Transactions',
        'sale_data':sale_data,
    }
    # return HttpResponse('')
    return render(request, 'posApp/sales.html',context)

@login_required
def receipt(request):
    id = request.GET.get('id')
    sales = Sales.objects.filter(id = id).first()
    transaction = {}
    for field in Sales._meta.get_fields():
        if field.related_model is None:
            transaction[field.name] = getattr(sales,field.name)
    if 'tax_amount' in transaction:
        transaction['tax_amount'] = format(float(transaction['tax_amount']))
    ItemList = salesItems.objects.filter(sale_id = sales).all()
    context = {
        "transaction" : transaction,
        "salesItems" : ItemList
    }

    return render(request, 'posApp/receipt.html',context)
    # return HttpResponse('')

@login_required
def delete_sale(request):
    resp = {'status':'failed', 'msg':''}
    id = request.POST.get('id')
    try:
        delete = Sales.objects.filter(id = id).delete()
        resp['status'] = 'success'
        messages.success(request, 'Sale Record has been deleted.')
    except:
        resp['msg'] = "An error occured"
        # print("Unexpected error:", sys.exc_info()[0])
    return HttpResponse(json.dumps(resp), content_type='application/json')

@login_required()
def employee(request):
    employees=Employee.objects.all().order_by('Full_Name')
    today = date.today()
    if request.method == 'POST':
        fullName = request.POST.get('fullName')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        contact = request.POST.get('contact')
        salary = request.POST.get('salary')
        role = request.POST.get('role')
        joinedDate = request.POST.get('joinedDate')
        data=Employee(Full_Name=fullName,Address=address,Gender=gender,Contact=contact,Salary=salary,Role=role,Joined_Date=joinedDate)
        data.save()
        messages.success(request, 'New Employee Added Successfully!')
        return redirect('employee-page')
    else:
        context = {
            'page_title' : "Employee",
            'employee':employees,
            'today':today
            
        }
        return render(request, 'posApp/employee.html',context)

@login_required
def delete_employee(request,id):
    employee=Employee.objects.get(pk=id).delete()
    messages.success(request, "Deleted Successfully!")
    return redirect('employee-page')

@login_required
def edit_employee(request,id):
    employee=Employee.objects.get(pk=id)
    context={
            'emp':employee,
            'page_title':'Edit Employee'
        }
    if request.method == 'POST':        
        employee.Full_Name=request.POST.get('fullName')
        employee.Address=request.POST.get('address')
        employee.Salary=request.POST.get('salary')
        employee.Joined_Date=request.POST.get('joinedDate')
        employee.Contact=request.POST.get('contact')
        employee.Role=request.POST.get('role')
        employee.Gender=request.POST.get('gender')
        employee.save()
        messages.success(request, employee.Full_Name+" Updated Successfully")
        return redirect('employee-page')
    else:
        return render(request, 'posApp/editEmployee.html',context)

#Salary Function
def salary(request,id,name):
    sal=Payroll.objects.filter(Empid=id)
    if request.method == 'POST':
        empid=id
        fromDate=request.POST.get('fromDate')
        toDate=request.POST.get('toDate')
        amount=request.POST.get('amount')
        paymentMethod=request.POST.get('paymentMethod')
        paidDate=request.POST.get('paidDate')
        remarks=request.POST.get('remarks')
        data=Payroll(Empid_id=empid,From_Date=fromDate,To_Date=toDate,Amount=amount,Payment_Method=paymentMethod,
        Remarks=remarks,Paid_Date=paidDate)
        data.save()
        messages.success(request, "New salary added from "+fromDate+" to "+toDate)
        # return redirect(employee)
        return HttpResponseRedirect("")

    else:
        if not sal:
            messages.info(request, "No salary records found!")
        context={
            'salary':sal,
            'name':name
        }
        return render(request, 'posApp/salary.html',context)

#delete salary
def delete_salary(request,sal_id,emp_id,name):
    salary=Payroll.objects.get(pk=sal_id).delete()
    messages.success(request, "Deleted Successfully!")
    return redirect('salary',emp_id,name)

#edit salary
def edit_salary(request,sal_id,emp_id,name):
    sal=Payroll.objects.get(pk=sal_id)
    context={
        'sal':sal,
        'emp_id':emp_id,
        'name':name     
    }
    if request.method == 'POST':
        sal.From_Date=request.POST.get('fromDate')
        sal.To_Date=request.POST.get('toDate')
        sal.Amount=request.POST.get('amount')
        sal.Paid_Date=request.POST.get('paidDate')
        sal.Remarks=request.POST.get('remarks')
        sal.save()
        messages.success(request, "Updated Successfully!")
        return redirect('salary',emp_id,name)
    else:
        return render(request, 'posApp/editSalary.html',context)