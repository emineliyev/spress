from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, TemplateView

from apps.settings_app.models import AboutStat

from .forms import ContactForm
from .models import ContactMessage, Page
from .tasks import send_contact_email

# Deliberately a fixed literal, not az_slugify('Haqqımızda') (which
# produces 'haqqimizda') — the editor managing this page is free to use
# whatever URL slug reads best ('about' is what's actually in use),
# and this constant only needs to match whatever that turns out to be.
ABOUT_SLUG = 'about'


class AboutView(TemplateView):
    template_name = 'pages/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = get_object_or_404(Page, slug=ABOUT_SLUG, is_published=True)
        context['page'] = page
        context['breadcrumb_items'] = [(page.title, None)]
        # CMS-managed (apps/cms/views/about_stat.py) — previously three
        # of these were hardcoded directly in about.html with no way to
        # edit or remove them.
        context['about_stats'] = AboutStat.objects.all()
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
        # Saved as a real CMS-visible row, not just emailed — the inbox
        # (apps/cms/views/contact_message.py) is the durable record; the
        # email is a same-moment notification on top of it, not the
        # source of truth (an editor whose mailbox drops/filters it can
        # still see it in the CMS).
        ContactMessage.objects.create(**form.cleaned_data)
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
