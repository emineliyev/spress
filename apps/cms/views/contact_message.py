from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import DetailView, ListView

from apps.pages.models import ContactMessage

CONTACT_MESSAGE_LIST_PER_PAGE = 20


class ContactMessageListView(LoginRequiredMixin, ListView):
    template_name = 'cms/contact_message_list.html'
    context_object_name = 'contact_messages'
    paginate_by = CONTACT_MESSAGE_LIST_PER_PAGE

    def get_queryset(self):
        queryset = ContactMessage.objects.all()
        self.status = self.request.GET.get('status', '')
        if self.status:
            queryset = queryset.filter(status=self.status)

        self.query = self.request.GET.get('q', '').strip()
        if self.query:
            queryset = queryset.filter(name__icontains=self.query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'status_choices': ContactMessage.Status.choices,
            'selected_status': self.status,
            'query': self.query,
        })
        return context


class ContactMessageDetailView(LoginRequiredMixin, DetailView):
    model = ContactMessage
    template_name = 'cms/contact_message_detail.html'
    context_object_name = 'contact_message'

    def get_object(self, queryset=None):
        """Opening a message is what "read" means here — the same
        implicit-read pattern an email inbox uses, so an editor doesn't
        need an extra click just to acknowledge it."""
        message = super().get_object(queryset)
        if message.status == ContactMessage.Status.NEW:
            message.status = ContactMessage.Status.READ
            message.save(update_fields=['status', 'updated_at'])
        return message


class ContactMessageToggleStatusView(LoginRequiredMixin, View):
    """Manual override for when an editor wants to flag a message back to
    "Yeni" (e.g. to come back to it later) — the detail view above already
    covers the common "opening it marks it read" case."""

    def post(self, request, pk):
        message = get_object_or_404(ContactMessage, pk=pk)
        message.status = (
            ContactMessage.Status.NEW if message.status == ContactMessage.Status.READ
            else ContactMessage.Status.READ
        )
        message.save(update_fields=['status', 'updated_at'])
        return redirect('cms:contact_message_list')
