from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q, Avg, Count, Max, Min
from django.db.models.functions import TruncMonth, TruncWeek, ExtractHour
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from datetime import timedelta
from .models import UploadedFile, Transaction, Category
from .forms import UploadStatementForm, CategoryForm, TransactionCategoryForm
import json
import os

def home(request):
    return render(request, 'core/home.html')

@login_required
def dashboard(request):
    user_files = UploadedFile.objects.filter(user=request.user).order_by('-uploaded_at')
    transactions = Transaction.objects.filter(uploaded_file__user=request.user)
    
    # Get date range for filtering
    date_filter = request.GET.get('date_range', 'all')
    if date_filter == 'month':
        start_date = timezone.now() - timedelta(days=30)
        transactions = transactions.filter(date__gte=start_date)
    elif date_filter == '3months':
        start_date = timezone.now() - timedelta(days=90)
        transactions = transactions.filter(date__gte=start_date)
    elif date_filter == '6months':
        start_date = timezone.now() - timedelta(days=180)
        transactions = transactions.filter(date__gte=start_date)
    elif date_filter == 'year':
        start_date = timezone.now() - timedelta(days=365)
        transactions = transactions.filter(date__gte=start_date)

    # Basic statistics
    total_spent = transactions.filter(amount__lt=0).aggregate(total=Sum('amount'))['total'] or 0
    total_income = transactions.filter(amount__gt=0).aggregate(total=Sum('amount'))['total'] or 0
    avg_transaction = transactions.aggregate(avg=Avg('amount'))['avg'] or 0
    transaction_count = transactions.count()
    largest_expense = transactions.filter(amount__lt=0).aggregate(max=Min('amount'))['max'] or 0
    largest_income = transactions.filter(amount__gt=0).aggregate(max=Max('amount'))['max'] or 0

    # Get spending by category with percentages
    category_totals = list(transactions.filter(amount__lt=0).values('category__name')
        .annotate(
            total=Sum('amount'),
            count=Count('id'),
            avg=Avg('amount')
        )
        .order_by('total'))
    
    total_spending = abs(sum(cat['total'] for cat in category_totals))
    for cat in category_totals:
        cat['percentage'] = (abs(cat['total']) / total_spending * 100) if total_spending else 0
        cat['total'] = abs(cat['total'])  # Convert to positive for display

    # Get monthly spending trend
    monthly_totals = list(transactions.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        expenses=Sum('amount', filter=Q(amount__lt=0)),
        income=Sum('amount', filter=Q(amount__gt=0)),
        transaction_count=Count('id')
    ).order_by('month'))

    # Get weekly spending pattern
    weekly_totals = list(transactions.filter(amount__lt=0).annotate(
        week=TruncWeek('date')
    ).values('week').annotate(
        total=Sum('amount')
    ).order_by('week'))

    # Recent high-value transactions
    high_value_transactions = transactions.order_by('amount')[:5]  # Top 5 expenses
    
    context = {
        'files': user_files,
        'transactions': transactions.order_by('-date')[:50],  # Show last 50 transactions
        'category_totals': json.dumps(category_totals, cls=DjangoJSONEncoder),
        'monthly_totals': json.dumps(monthly_totals, cls=DjangoJSONEncoder),
        'weekly_totals': json.dumps(weekly_totals, cls=DjangoJSONEncoder),
        'stats': {
            'total_spent': abs(total_spent),
            'total_income': total_income,
            'avg_transaction': abs(avg_transaction),
            'transaction_count': transaction_count,
            'largest_expense': abs(largest_expense),
            'largest_income': largest_income,
        },
        'high_value_transactions': high_value_transactions,
        'date_filter': date_filter,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def upload_statement(request):
    if request.method == 'POST':
        form = UploadStatementForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save(commit=False)
            uploaded_file.user = request.user
            uploaded_file.save()

            try:
                # Get the appropriate parser for the bank
                parser_class = BANK_PARSERS.get(uploaded_file.bank_name)
                if not parser_class:
                    raise ValueError(f"No parser available for {uploaded_file.bank_name}")

                # Parse the PDF file
                parser = parser_class(uploaded_file.file.path)
                transactions = parser.parse()

                # Get or create categories
                categories = {cat.name.lower(): cat for cat in Category.objects.filter(
                    Q(user=request.user) | Q(is_system=True)
                )}

                # Save transactions to database
                for transaction_data in transactions:
                    # Find best matching category
                    category = None
                    desc = transaction_data['description'].lower()
                    
                    for cat in categories.values():
                        if any(keyword in desc for keyword in cat.keyword_list):
                            category = cat
                            break

                    Transaction.objects.create(
                        uploaded_file=uploaded_file,
                        date=transaction_data['date'],
                        description=transaction_data['description'],
                        amount=transaction_data['amount'],
                        category=category,
                        balance=transaction_data['balance']
                    )

                uploaded_file.processed = True
                uploaded_file.save()
                
                messages.success(request, 'Statement uploaded and processed successfully!')
            except Exception as e:
                messages.error(request, f'Error processing statement: {str(e)}')
                # Clean up the uploaded file if processing failed
                if os.path.exists(uploaded_file.file.path):
                    os.remove(uploaded_file.file.path)
                uploaded_file.delete()
            
            return redirect('dashboard')
    else:
        form = UploadStatementForm()
    
    return render(request, 'core/upload.html', {'form': form})

@login_required
def manage_categories(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Category created successfully!')
            return redirect('manage_categories')
    else:
        form = CategoryForm()

    # Get user's custom categories and system categories
    categories = Category.objects.filter(
        Q(user=request.user) | Q(is_system=True)
    ).order_by('name')

    context = {
        'form': form,
        'categories': categories,
    }
    return render(request, 'core/manage_categories.html', context)

@login_required
def edit_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, uploaded_file__user=request.user)
    
    if request.method == 'POST':
        form = TransactionCategoryForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated successfully!')
            return redirect('dashboard')
    else:
        form = TransactionCategoryForm(instance=transaction)

    context = {
        'form': form,
        'transaction': transaction,
    }
    return render(request, 'core/edit_transaction.html', context)