from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Count, ProtectedError, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

from apps.core.utils import get_client_ip
from apps.logs.models import ActivityLog
from apps.media_manager.models import Folder, MediaFile
from apps.media_manager.services import delete_media_file, process_crop, stage_upload

MEDIA_LIST_PER_PAGE = 24


class MediaLibraryListView(LoginRequiredMixin, ListView):
    template_name = 'cms/media_list.html'
    context_object_name = 'files'
    paginate_by = MEDIA_LIST_PER_PAGE

    def get_queryset(self):
        queryset = MediaFile.objects.select_related('folder')

        self.folder_id = self.request.GET.get('folder', '')
        if self.folder_id:
            queryset = queryset.filter(folder_id=self.folder_id)

        self.file_format = self.request.GET.get('format', '')
        if self.file_format:
            queryset = queryset.filter(file_format=self.file_format)

        self.query = self.request.GET.get('q', '').strip()
        if self.query:
            queryset = queryset.filter(original_filename__icontains=self.query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_bytes = MediaFile.objects.aggregate(total=Sum('file_size'))['total'] or 0

        preserved_params = {
            key: value for key, value in (
                ('folder', self.folder_id), ('format', self.file_format), ('q', self.query),
            ) if value
        }

        context.update({
            'folders': Folder.objects.annotate(files_count=Count('files')),
            'all_files_count': MediaFile.objects.count(),
            'selected_folder': self.folder_id,
            'selected_format': self.file_format,
            'query': self.query,
            'format_choices': MediaFile.Format.choices,
            'total_storage_mb': round(total_bytes / (1024 * 1024), 1),
            'query_string': urlencode(preserved_params) + '&' if preserved_params else '',
        })
        return context


class MediaPickerListView(MediaLibraryListView):
    """Same filtering/pagination as `MediaLibraryListView` — just a
    lighter template (`cms/partials/media_picker_grid.html`, no page
    chrome) meant to be `fetch()`-ed into `media_picker_modal.html`'s
    "Kitabxanadan seç" tab (static/js/cms/image-pickers.js) instead of
    rendered as a full page."""

    template_name = 'cms/partials/media_picker_grid.html'


class MediaUploadStageView(LoginRequiredMixin, View):
    """AJAX step 1: validate + park the file, return it for Cropper.js to load."""

    def post(self, request):
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return JsonResponse({'error': 'Fayl seçilməyib.'}, status=400)
        try:
            result = stage_upload(uploaded_file)
        except ValidationError as exc:
            return JsonResponse({'error': exc.message}, status=400)
        return JsonResponse(result)


class MediaCropConfirmView(LoginRequiredMixin, View):
    """AJAX step 2: crop + process the staged file into a real MediaFile.

    A `replace` field in the POST body targets an existing MediaFile
    (the "Əvəz et" action) — same pipeline, but the row is updated in
    place instead of a new one being created, so every reference to it
    (a News.featured_image, for instance) keeps working unchanged.
    """

    def post(self, request):
        temp_id = request.POST.get('temp_id')
        if not temp_id:
            return JsonResponse({'error': 'temp_id göndərilməyib.'}, status=400)

        crop_box = None
        if all(key in request.POST for key in ('x', 'y', 'width', 'height')):
            crop_box = {
                'x': float(request.POST['x']),
                'y': float(request.POST['y']),
                'width': float(request.POST['width']),
                'height': float(request.POST['height']),
            }

        replace_pk = request.POST.get('replace')
        media_file = get_object_or_404(MediaFile, pk=replace_pk) if replace_pk else None

        try:
            result = process_crop(
                temp_id,
                crop_box=crop_box,
                folder_id=request.POST.get('folder') or None,
                user=request.user,
                alt_text=request.POST.get('alt_text', ''),
                caption=request.POST.get('caption', ''),
                media_file=media_file,
            )
        except ValidationError as exc:
            return JsonResponse({'error': exc.message}, status=400)

        ActivityLog.objects.create(
            actor=request.user,
            action=ActivityLog.Action.MEDIA_REPLACED if media_file else ActivityLog.Action.MEDIA_UPLOADED,
            description=result.original_filename,
            ip_address=get_client_ip(request),
        )

        return JsonResponse({
            'id': result.pk,
            'url': result.file.url,
            'thumbnail_url': result.thumbnail.url if result.thumbnail else result.file.url,
            'width': result.width,
            'height': result.height,
            'file_size': result.file_size,
            'original_filename': result.original_filename,
            'file_format': result.file_format,
        })


class CKEditorImageUploadView(LoginRequiredMixin, View):
    """Single-POST upload target for CKEditor5's `SimpleUploadAdapter`
    (config/settings/base.py's `CK_EDITOR_5_UPLOAD_FILE_VIEW_NAME`).

    Reuses the same stage→process pipeline as the Media Library
    (`crop_box=None` skips the interactive crop step — confirmed: inline
    body images are resized via CKEditor's own resize handles instead),
    so an image dropped into an article gets the same WebP conversion,
    thumbnail and `MediaFile` row as every other upload path, instead of
    django_ckeditor_5's own view, which would just dump the raw file
    under `MEDIA_ROOT` with no processing and no database record.
    """

    def post(self, request):
        uploaded_file = request.FILES.get('upload')
        if not uploaded_file:
            return JsonResponse({'error': {'message': 'Fayl seçilməyib.'}}, status=400)

        try:
            staged = stage_upload(uploaded_file)
            media_file = process_crop(staged['temp_id'], crop_box=None, user=request.user)
        except ValidationError as exc:
            return JsonResponse({'error': {'message': exc.message}}, status=400)

        ActivityLog.objects.create(
            actor=request.user,
            action=ActivityLog.Action.MEDIA_UPLOADED,
            description=media_file.original_filename,
            ip_address=get_client_ip(request),
        )
        return JsonResponse({'url': media_file.file.url})


class MediaDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        media_file = get_object_or_404(MediaFile, pk=pk)
        return render(request, 'cms/media_confirm_delete.html', {'media_file': media_file})

    def post(self, request, pk):
        media_file = get_object_or_404(MediaFile, pk=pk)
        filename = media_file.original_filename

        try:
            # Advertisement.banner is on_delete=PROTECT (Phase 10) — a
            # banner backing a live campaign shouldn't vanish silently the
            # way News.featured_image/SiteSettings.logo do (SET_NULL).
            # usage_count already warns about this on the confirm page;
            # this is the backstop against a raw ProtectedError 500 if the
            # warning is ignored.
            delete_media_file(media_file)
        except ProtectedError:
            messages.error(
                request,
                f'"{filename}" silinmədi — hazırda bir reklam kampaniyasının bannerdi. '
                'Əvvəlcə həmin kampaniyanı silin və ya başqa banner təyin edin.',
            )
            return redirect('cms:media_list')

        ActivityLog.objects.create(
            actor=request.user,
            action=ActivityLog.Action.MEDIA_DELETED,
            description=filename,
            ip_address=get_client_ip(request),
        )
        messages.success(request, f'"{filename}" silindi.')
        return redirect('cms:media_list')


class MediaMoveView(LoginRequiredMixin, View):
    """Moves a `MediaFile` into a different folder (or out of any folder)
    from its card's row-menu — a plain `<select onchange="submit">`, not
    drag-and-drop: same "AJAX only when necessary" reasoning as
    `FolderCreateView`/`FolderUpdateView`, and the simplest thing that
    actually solves "I uploaded this into the wrong folder."

    Redirects back to the exact filtered/paginated grid the move was made
    from — reconstructed from a small whitelist of POSTed `return_*`
    fields via `reverse()`, not a raw "next" URL, so this can't become an
    open redirect (CLAUDE.md ch.12).
    """

    def post(self, request, pk):
        media_file = get_object_or_404(MediaFile, pk=pk)
        folder_id = request.POST.get('folder')

        if folder_id and folder_id != '__unfiled__':
            folder = get_object_or_404(Folder, pk=folder_id)
            media_file.folder = folder
            description = f'{media_file.original_filename} → "{folder.name}"'
        else:
            media_file.folder = None
            description = f'{media_file.original_filename} → (qovluqsuz)'
        media_file.save(update_fields=['folder', 'updated_at'])

        ActivityLog.objects.create(
            actor=request.user,
            action=ActivityLog.Action.MEDIA_MOVED,
            description=description,
            ip_address=get_client_ip(request),
        )
        messages.success(request, f'"{media_file.original_filename}" köçürüldü.')

        params = {
            key: request.POST[source]
            for key, source in (('folder', 'return_folder'), ('format', 'return_format'), ('q', 'return_q'), ('page', 'return_page'))
            if request.POST.get(source)
        }
        url = reverse('cms:media_list')
        if params:
            url += '?' + urlencode(params)
        return redirect(url)


class FolderCreateView(LoginRequiredMixin, View):
    def post(self, request):
        name = request.POST.get('name', '').strip()
        if name:
            folder, created = Folder.objects.get_or_create(name=name)
            if created:
                ActivityLog.objects.create(
                    actor=request.user,
                    action=ActivityLog.Action.FOLDER_CREATED,
                    description=name,
                    ip_address=get_client_ip(request),
                )
            messages.success(request, f'"{name}" qovluğu yaradıldı.')
        return redirect(reverse('cms:media_list'))


class FolderUpdateView(LoginRequiredMixin, View):
    """Plain POST + redirect, not AJAX — mirrors FolderCreateView rather
    than introducing a second interaction pattern for the same sidebar
    (CLAUDE.md ch.8: "AJAX should be used only when necessary")."""

    def post(self, request, pk):
        folder = get_object_or_404(Folder, pk=pk)
        name = request.POST.get('name', '').strip()

        if not name:
            messages.error(request, 'Qovluq adı boş ola bilməz.')
        elif Folder.objects.filter(name=name).exclude(pk=pk).exists():
            messages.error(request, f'"{name}" adlı qovluq artıq mövcuddur.')
        else:
            old_name = folder.name
            folder.name = name
            folder.save(update_fields=['name'])
            ActivityLog.objects.create(
                actor=request.user,
                action=ActivityLog.Action.FOLDER_RENAMED,
                description=f'"{old_name}" → "{name}"',
                ip_address=get_client_ip(request),
            )
            messages.success(request, 'Qovluğun adı dəyişdirildi.')

        return redirect(reverse('cms:media_list'))


class FolderDeleteView(LoginRequiredMixin, View):
    """Files inside the folder are never deleted — `MediaFile.folder` is
    `on_delete=SET_NULL`, so they just fall back into "Bütün fayllar"."""

    def get(self, request, pk):
        folder = get_object_or_404(Folder, pk=pk)
        return render(request, 'cms/folder_confirm_delete.html', {
            'folder': folder,
            'files_count': folder.files.count(),
        })

    def post(self, request, pk):
        folder = get_object_or_404(Folder, pk=pk)
        name = folder.name
        folder.delete()
        ActivityLog.objects.create(
            actor=request.user,
            action=ActivityLog.Action.FOLDER_DELETED,
            description=name,
            ip_address=get_client_ip(request),
        )
        messages.success(request, f'"{name}" qovluğu silindi.')
        return redirect('cms:media_list')
