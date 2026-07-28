"""
CMS views split into one module per screen (CLAUDE.md ch.2 "single
responsibility") — re-exported here so `apps/cms/urls.py` keeps working
with `views.XxxView` regardless of which submodule actually defines it.
"""

from .activity_log import ActivityLogListView
from .advertisement import (
    AdCreateView,
    AdDeleteView,
    AdListView,
    AdPermanentDeleteView,
    AdRestoreView,
    AdUpdateView,
)
from .category import (
    CategoryCreateView,
    CategoryDeleteView,
    CategoryListView,
    CategoryPermanentDeleteView,
    CategoryReorderView,
    CategoryRestoreView,
    CategoryUpdateView,
)
from .contact_message import (
    ContactMessageDetailView,
    ContactMessageListView,
    ContactMessageToggleStatusView,
)
from .dashboard import DashboardView
from .media import (
    CKEditorImageUploadView,
    FolderCreateView,
    FolderDeleteView,
    FolderUpdateView,
    MediaCropConfirmView,
    MediaDeleteView,
    MediaLibraryListView,
    MediaMoveView,
    MediaPickerListView,
    MediaTempPreviewView,
    MediaUploadStageView,
)
from .news import (
    NewsBulkActionView,
    NewsCreateView,
    NewsDeleteView,
    NewsDuplicateView,
    NewsListView,
    NewsPermanentDeleteView,
    NewsRestoreView,
    NewsUpdateView,
)
from .page import (
    PageCreateView,
    PageDeleteView,
    PageListView,
    PageUpdateView,
)
from .profile import ChangePasswordView
from .seo import SeoOverviewView
from .settings import SettingsUpdateView
from .social_link import (
    SocialLinkCreateView,
    SocialLinkDeleteView,
    SocialLinkListView,
    SocialLinkUpdateView,
)
from .tag import (
    TagCreateView,
    TagDeleteView,
    TagListView,
    TagMergeView,
    TagUpdateView,
)
from .user import (
    UserActivateView,
    UserCreateView,
    UserDeactivateView,
    UserDeleteView,
    UserListView,
    UserResetPasswordView,
    UserUpdateView,
)

__all__ = [
    'ActivityLogListView',
    'AdCreateView',
    'AdDeleteView',
    'AdListView',
    'AdPermanentDeleteView',
    'AdRestoreView',
    'AdUpdateView',
    'CKEditorImageUploadView',
    'CategoryCreateView',
    'CategoryDeleteView',
    'CategoryListView',
    'CategoryPermanentDeleteView',
    'CategoryReorderView',
    'CategoryRestoreView',
    'CategoryUpdateView',
    'ChangePasswordView',
    'ContactMessageDetailView',
    'ContactMessageListView',
    'ContactMessageToggleStatusView',
    'DashboardView',
    'FolderCreateView',
    'FolderDeleteView',
    'FolderUpdateView',
    'MediaCropConfirmView',
    'MediaDeleteView',
    'MediaLibraryListView',
    'MediaMoveView',
    'MediaPickerListView',
    'MediaUploadStageView',
    'NewsBulkActionView',
    'NewsCreateView',
    'NewsDeleteView',
    'NewsDuplicateView',
    'NewsListView',
    'NewsPermanentDeleteView',
    'NewsRestoreView',
    'NewsUpdateView',
    'PageCreateView',
    'PageDeleteView',
    'PageListView',
    'PageUpdateView',
    'SeoOverviewView',
    'SettingsUpdateView',
    'SocialLinkCreateView',
    'SocialLinkDeleteView',
    'SocialLinkListView',
    'SocialLinkUpdateView',
    'TagCreateView',
    'TagDeleteView',
    'TagListView',
    'TagMergeView',
    'TagUpdateView',
    'UserActivateView',
    'UserCreateView',
    'UserDeactivateView',
    'UserDeleteView',
    'UserListView',
    'UserResetPasswordView',
    'UserUpdateView',
]
