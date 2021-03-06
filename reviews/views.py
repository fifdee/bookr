import django.utils.timezone
from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Review, Contributor, Publisher
from .utils import average_rating
from .forms import SearchForm, PublisherForm, ReviewForm
from django.contrib import messages


def book_list(request):
    books = Book.objects.all()
    book_list = []
    for book in books:
        reviews = book.review_set.all()
        if reviews:
            book_rating = average_rating([review.rating for review in reviews])
            number_of_reviews = len(reviews)
        else:
            book_rating = None
            number_of_reviews = 0
        book_list.append({'book': book, 'book_rating': book_rating, 'number_of_reviews': number_of_reviews})

    context = {'book_list': book_list}

    return render(request, 'reviews/books_list.html', context)


def book_details(request, id):
    book = get_object_or_404(Book, pk=id)
    reviews = book.review_set.all()
    if reviews:
        book_rating = average_rating([review.rating for review in reviews])
    else:
        book_rating = None
    item = {'book': book, 'book_rating': book_rating, 'reviews': reviews}
    context = {'item': item}

    return render(request, 'reviews/book_details.html', context)


def book_search(request):
    form = SearchForm(request.GET)
    books = set()
    context = {}
    contributors = []
    if form.is_valid():
        search = form.cleaned_data['search']
        search_in = form.cleaned_data['search_in']

        if search and search_in != 'contributor':
            books.update(Book.objects.filter(title__icontains=search))

        if search and search_in == 'contributor':
            books.update(Book.objects.filter(contributors__last_names__icontains=search))
            books.update(Book.objects.filter(contributors__first_names__icontains=search))

        for book in books:
            for contributor in book.bookcontributor_set.all():
                contributors.append(contributor.contributor.first_names + ' ' + contributor.contributor.last_names)

        context = {'form': form, 'search': search, 'books': books, 'contributors': ', '.join(contributors)}

    return render(request, 'reviews/book_search.html', context)


def publisher_edit(request, pk=None):
    if pk is not None:
        publisher = get_object_or_404(Publisher, pk=pk)
    else:
        publisher = None

    if request.method == "POST":
        form = PublisherForm(request.POST, instance=publisher)
        if form.is_valid():
            updated_publisher = form.save()
            if publisher is None:
                messages.success(request, f'Publisher "{updated_publisher}" was created.')
            else:
                messages.success(request, f'Publisher "{updated_publisher}" was updated.')
            return redirect('publisher_edit', updated_publisher.pk)
    else:
        form = PublisherForm(instance=publisher)

    return render(request, 'reviews/instance-form.html', {'instance': publisher, 'model_type': 'Publisher',
                                                          'form': form})


def review_edit(request, book_pk, review_pk=None):
    book_instance = get_object_or_404(Book, pk=book_pk)
    if review_pk is not None:
        review_instance = get_object_or_404(Review, book_id=book_pk, pk=review_pk)
    else:
        review_instance = None

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review_instance)
        if form.is_valid():
            updated_review = form.save(commit=False)
            updated_review.book = book_instance
            if review_instance:
                updated_review.date_edited = django.utils.timezone.now()
                messages.success(request, f'Review for "{book_instance.title}" updated.')
            else:
                messages.success(request, f'Review for "{book_instance.title}" created.')
            updated_review.save()

            return redirect('book_details', updated_review.book.pk)
    else:
        form = ReviewForm(instance=review_instance)

    return render(request, 'reviews/instance-form.html', {'form': form, 'instance': review_instance,
                                                          'model_type': "Review", 'related_model_type': "Book",
                                                          'related_instance': book_instance})