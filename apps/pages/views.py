from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, TemplateView

from apps.core.utils import az_slugify

from .forms import ContactForm
from .models import Page
from .tasks import send_contact_email

ABOUT_SLUG = az_slugify('Haqqımızda')


class AboutView(TemplateView):
    template_name = 'pages/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = get_object_or_404(Page, slug=ABOUT_SLUG, is_published=True)
        context['page'] = page
        context['breadcrumb_items'] = [(page.title, None)]
        return context


class ContactView(FormView):
    template_name = 'pages/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('pages:contact')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb_items'] = [('Əlaqə', None)]
        return context

    def form_valid(self, form):
        send_contact_email.delay(**form.cleaned_data)
        messages.success(self.request, 'Mesajınız göndərildi. Redaksiyamız tezliklə sizinlə əlaqə saxlayacaq.')
        return redirect(self.success_url)


class PageDetailView(DetailView):
    model = Page
    template_name = 'pages/page_detail.html'
    context_object_name = 'page'

    def get_queryset(self):
        return Page.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb_items'] = [(self.object.title, None)]
        return context
