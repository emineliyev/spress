from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.advertisements.models import AdPosition
from apps.categories.models import Category
from apps.core.utils import az_slugify
from apps.logs.models import ActivityLog
from apps.news.models import News
from apps.pages.models import Page
from apps.settings_app.models import SiteSettings
from apps.tags.models import Tag

CATEGORY_TREE = [
    ('Siyasət', [
        'Beynəlxalq',
    ]),
    ('İqtisadiyyat', [
        'Bank sektoru',
    ]),
]

TAGS = ['Büdcə2027', 'Parlament', 'Seçki2026']

# category: top-level name or "Parent / Child" for a subcategory
ARTICLES = [
    {
        'title': 'Parlament yeni büdcə paketini müzakirəyə çıxardı: əsas dəyişikliklər nələrdir',
        'short_description': 'Növbəti ilin dövlət büdcəsi layihəsi bu gün parlamentə təqdim olundu.',
        'content': (
            'Növbəti ilin dövlət büdcəsi layihəsi bu gün parlamentə təqdim olundu. Sənəddə sosial '
            'xərclər, vergi dərəcələri və investisiya proqramları üzrə yeniliklər yer alıb. Deputatlar '
            'layihəni ilk oxunuşda müzakirəyə çıxaracaq.\n\n'
            'Maliyyə Nazirliyinin nümayəndələri büdcə gəlirlərinin əsasən neft-qaz sektorundan '
            'formalaşacağını bildirib. Eyni zamanda qeyri-neft sektorunun payının artırılması hədəflənir.\n\n'
            'Ekspertlərin fikrincə, təklif olunan dəyişikliklər sosial müdafiə xərclərinin artırılmasına '
            'imkan yaradacaq. Layihənin yekun müzakirəsi növbəti ay keçiriləcək.'
        ),
        'category': 'Siyasət',
        'tags': ['Büdcə2027', 'Parlament'],
        'is_featured': True,
        'published_minutes_ago': 24,
    },
    {
        'title': 'Seçki komissiyası yeni qaydaları açıqladı',
        'short_description': 'Mərkəzi Seçki Komissiyası 2026-cı il seçkiləri üçün yenilənmiş prosedurları elan etdi.',
        'content': (
            'Mərkəzi Seçki Komissiyası 2026-cı il seçkiləri üçün yenilənmiş prosedurları elan etdi. '
            'Yeniliklər əsasən elektron qeydiyyat və müşahidə qaydalarına aiddir.\n\n'
            'Komissiya sədri bildirib ki, dəyişikliklərin məqsədi prosesin şəffaflığını artırmaqdır.'
        ),
        'category': 'Siyasət',
        'tags': ['Seçki2026'],
        'published_minutes_ago': 60,
    },
    {
        'title': 'Enerji sammitində yeni saziş imzalandı',
        'short_description': 'Regional enerji əməkdaşlığı çərçivəsində əhəmiyyətli saziş imzalanıb.',
        'content': (
            'Region ölkələrinin nümayəndələri enerji sammitində yeni əməkdaşlıq sazişi imzalayıb. '
            'Sənəd enerji təhlükəsizliyi və infrastruktur layihələrini əhatə edir.\n\n'
            'Tərəflər növbəti görüşün bu il davam etdiriləcəyini bildirib.'
        ),
        'category': 'Siyasət / Beynəlxalq',
        'published_minutes_ago': 180,
    },
    {
        'title': 'Neft qiymətləri üç aylıq zirvəyə çatdı',
        'short_description': 'Dünya bazarlarında neft qiymətləri son üç ayın ən yüksək səviyyəsinə yüksəlib.',
        'content': (
            'Dünya bazarlarında neft qiymətləri son üç ayın ən yüksək səviyyəsinə yüksəlib. Analitiklər '
            'bunu tələbin artması və ehtiyatların azalması ilə izah edir.\n\n'
            'Yerli ekspertlərin fikrincə, bu artım dövlət büdcəsinin gəlir hissəsinə müsbət təsir göstərə bilər.'
        ),
        'category': 'İqtisadiyyat',
        'tags': ['Büdcə2027'],
        'published_minutes_ago': 90,
    },
    {
        'title': 'Kiçik sahibkarlıq üçün yeni güzəştlər',
        'short_description': 'Hökumət kiçik və orta sahibkarlıq subyektləri üçün vergi güzəştləri paketini təqdim edib.',
        'content': (
            'Hökumət kiçik və orta sahibkarlıq subyektləri üçün vergi güzəştləri paketini təqdim edib. '
            'Sənəd sadələşdirilmiş vergitutma və kreditləşmə şərtlərinin yaxşılaşdırılmasını nəzərdə tutur.'
        ),
        'category': 'İqtisadiyyat',
        'published_minutes_ago': 240,
    },
    {
        'title': 'Bank sektorunda birləşmə dalğası',
        'short_description': 'Yerli bank bazarında son aylarda bir neçə birləşmə əməliyyatı qeydə alınıb.',
        'content': (
            'Yerli bank bazarında son aylarda bir neçə birləşmə əməliyyatı qeydə alınıb. Mərkəzi Bank bunu '
            'sektorun sağlamlaşdırılması prosesinin davamı kimi qiymətləndirir.\n\n'
            'Ekspertlər gözləyir ki, bu proses növbəti ildə də davam edəcək.'
        ),
        'category': 'İqtisadiyyat / Bank sektoru',
        'is_breaking': True,
        'published_minutes_ago': 15,
    },
    {
        'title': 'Yeni vergi məcəlləsi layihəsi hazırlanır',
        'short_description': 'Maliyyə Nazirliyi vergi məcəlləsinə dəyişikliklər üzərində işləyir.',
        'content': 'Maliyyə Nazirliyi vergi məcəlləsinə dəyişikliklər üzərində işləyir. Layihə hələ ictimai müzakirəyə çıxarılmayıb.',
        'category': 'İqtisadiyyat',
        'status': 'draft',
    },
    {
        'title': 'Nazirlər Kabinetində iclas keçiriləcək',
        'short_description': 'Növbəti Nazirlər Kabineti iclasının gündəliyi açıqlanıb.',
        'content': 'Növbəti Nazirlər Kabineti iclasının gündəliyi açıqlanıb. İclasda bir sıra sosial layihələr müzakirə olunacaq.',
        'category': 'Siyasət',
        'status': 'scheduled',
        'scheduled_in_hours': 30,
    },
]

PAGES = [
    {
        'title': 'Haqqımızda',
        'slug': 'about',
        'content': (
            'XəbərPortal — Azərbaycanda müstəqil, sürətli və dəqiq xəbər xidməti təqdim edən rəqəmsal '
            'media nəşridir. Məqsədimiz oxucuya hər bir hadisəni tarazlı və yoxlanılmış şəkildə çatdırmaqdır.\n\n'
            'Redaksiyamız siyasət, iqtisadiyyat, dünya, idman və mədəniyyət sahələrində gündəlik xəbərlər, '
            'analitik materiallar və müsahibələr hazırlayır.'
        ),
    },
    {
        'title': 'Məxfilik siyasəti',
        'slug': 'privacy-policy',
        'content': (
            'XəbərPortal istifadəçilərinin məxfiliyinə hörmətlə yanaşır. Bu səhifədə saytımızda hansı '
            'məlumatların toplandığı və onlardan necə istifadə olunduğu izah edilir.\n\n'
            'Sayta daxil olarkən texniki məlumatlar (IP ünvan, brauzer növü, baxılan səhifələr) statistik '
            'məqsədlər üçün toplana bilər. Əlaqə formu vasitəsilə göndərilən şəxsi məlumatlar yalnız '
            'sorğunuza cavab vermək üçün istifadə olunur və üçüncü tərəflərlə paylaşılmır.\n\n'
            'Saytımız funksionallığı təmin etmək üçün minimal say cookie-lərdən istifadə edə bilər. '
            'Məxfilik siyasəti ilə bağlı suallarınız üçün Əlaqə səhifəsindən bizimlə əlaqə saxlaya bilərsiniz.'
        ),
    },
    {
        'title': 'İstifadə şərtləri',
        'slug': 'terms-of-use',
        'content': (
            'XəbərPortal saytından istifadə edərək aşağıdakı şərtləri qəbul etmiş olursunuz.\n\n'
            'Saytda yerləşdirilən bütün materiallar (mətn, şəkil, video) müəllif hüquqları ilə qorunur. '
            'Materiallardan istifadə yalnız mənbəyə istinadla və qeyri-kommersiya məqsədilə mümkündür.\n\n'
            'Redaksiya dərc olunan məlumatların dəqiqliyi üçün səy göstərir, lakin xarici mənbələrdən '
            'gələn məlumatlara görə məsuliyyət daşımır. Sayt istənilən vaxt məzmununu yeniləmək və ya '
            'dəyişmək hüququnu özündə saxlayır.'
        ),
    },
    {
        'title': 'Reklam',
        'slug': 'reklam',
        'content': (
            'XəbərPortal gündəlik minlərlə oxucuya çatır. Saytımızda reklam yerləşdirmək istəyən '
            'şirkətlər üçün müxtəlif banner mövqeləri təklif edirik.\n\n'
            'Əməkdaşlıq şərtləri və mövcud reklam mövqeləri barədə ətraflı məlumat üçün redaksiya ilə '
            'Əlaqə səhifəsi vasitəsilə əlaqə saxlaya bilərsiniz.'
        ),
    },
]

# Matches templates/news/home.html and templates/categories/category_detail.html's
# {% ad_slot "code" %} calls — CLAUDE.md ch.9 "Default advertisement positions" seed data.
AD_POSITIONS = [
    {'name': 'Ana səhifə - sidebar', 'code': 'home-sidebar-1', 'width': 360, 'height': 280},
    {'name': 'Kateqoriya - sidebar', 'code': 'category-sidebar-1', 'width': 360, 'height': 280},
]


class Command(BaseCommand):
    help = 'Idempotently seeds site settings, a category tree, sample news and static pages for local verification.'

    def handle(self, *args, **options):
        self._seed_site_settings()
        categories = self._seed_categories()
        tags = self._seed_tags()
        author = self._seed_author()
        self._seed_articles(categories, tags, author)
        self._seed_pages()
        self._seed_ad_positions()
        self._seed_activity_log(author)

    def _seed_site_settings(self):
        settings_obj = SiteSettings.get_solo()
        settings_obj.footer_text = 'Azərbaycanda gündəlik xəbərləri, analitikanı və rəyi ilk əldən izləyin.'
        settings_obj.contact_email = 'redaksiya@xeberportal.az'
        settings_obj.contact_phone = '+994 12 000 00 00'
        settings_obj.contact_address = 'Bakı, Azərbaycan'
        settings_obj.save()
        self.stdout.write(self.style.SUCCESS(f'Site settings ready: "{settings_obj.site_name}"'))

    def _seed_categories(self):
        by_name = {}
        for order, (name, children) in enumerate(CATEGORY_TREE):
            parent, created = Category.objects.get_or_create(
                slug=az_slugify(name), defaults={'name': name, 'order': order},
            )
            self.stdout.write(self._status(parent.name, created))
            by_name[name] = parent

            for child_order, child_name in enumerate(children):
                child, created = Category.objects.get_or_create(
                    slug=az_slugify(child_name),
                    defaults={'name': child_name, 'parent': parent, 'order': child_order},
                )
                self.stdout.write(self._status(f'  └ {child.name}', created))
                by_name[f'{name} / {child_name}'] = child
        return by_name

    def _seed_tags(self):
        tags = {}
        for name in TAGS:
            tag, created = Tag.objects.get_or_create(slug=az_slugify(name), defaults={'name': name})
            self.stdout.write(self._status(f'Tag: {tag.name}', created))
            tags[name] = tag
        return tags

    def _seed_author(self):
        User = get_user_model()
        author, created = User.objects.get_or_create(
            username='seed_editor',
            defaults={
                'first_name': 'Aygün',
                'last_name': 'Məmmədova',
                'role': User.Role.JOURNALIST,
            },
        )
        if created:
            author.set_unusable_password()
            author.save()
        self.stdout.write(self._status('Seed author: seed_editor', created))
        return author

    def _seed_articles(self, categories, tags, author):
        now = timezone.now()
        for entry in ARTICLES:
            slug = az_slugify(entry['title'])
            if News.objects.filter(slug=slug).exists():
                self.stdout.write(self._status(f'News: {entry["title"]}', False))
                continue

            status = entry.get('status', 'published')
            if status == 'draft':
                published_at, view_count = None, 0
            elif status == 'scheduled':
                published_at = now + timedelta(hours=entry.get('scheduled_in_hours', 24))
                view_count = 0
            else:
                published_at = now - timedelta(minutes=entry['published_minutes_ago'])
                view_count = entry['published_minutes_ago'] * 3

            # ARTICLES writes plain text with blank-line paragraph breaks
            # (easier to read/edit than HTML literals) — wrapped into <p>
            # tags here so it's valid input for News.content (CKEditor5Field,
            # sanitized again on save() regardless).
            content_html = ''.join(f'<p>{paragraph}</p>' for paragraph in entry['content'].split('\n\n'))

            article = News(
                title=entry['title'],
                slug=slug,
                short_description=entry['short_description'],
                content=content_html,
                category=categories[entry['category']],
                author=author,
                status=status,
                is_featured=entry.get('is_featured', False),
                is_breaking=entry.get('is_breaking', False),
                published_at=published_at,
                view_count=view_count,
            )
            article.save()
            article.tags.set([tags[name] for name in entry.get('tags', [])])
            self.stdout.write(self._status(f'News: {entry["title"]}', True))

    def _seed_pages(self):
        for entry in PAGES:
            slug = entry.get('slug') or az_slugify(entry['title'])
            # PAGES writes plain text with blank-line paragraph breaks
            # (easier to read/edit than HTML literals) — wrapped into <p>
            # tags here, same as ARTICLES above, now that Page.content is
            # a CKEditor5Field rendered with |safe on the public site.
            content_html = ''.join(f'<p>{paragraph}</p>' for paragraph in entry['content'].split('\n\n'))
            _, created = Page.objects.get_or_create(
                slug=slug, defaults={'title': entry['title'], 'content': content_html},
            )
            self.stdout.write(self._status(f'Page: {entry["title"]}', created))

    def _seed_ad_positions(self):
        for entry in AD_POSITIONS:
            _, created = AdPosition.objects.get_or_create(
                code=entry['code'],
                defaults={'name': entry['name'], 'width': entry['width'], 'height': entry['height']},
            )
            self.stdout.write(self._status(f'Ad position: {entry["name"]}', created))

    def _seed_activity_log(self, author):
        """Backdated demo entries — otherwise the Dashboard "Son fəaliyyət" widget
        and /cms/fealiyyet-jurnali/ are empty on a fresh checkout. `created_at`
        is `auto_now_add`, so it's set via a follow-up `.update()`, not `.create()`.
        """
        if ActivityLog.objects.exists():
            self.stdout.write(self._status('Activity log demo entries', False))
            return

        User = get_user_model()
        actor = User.objects.filter(is_superuser=True).first() or author
        now = timezone.now()
        demo_entries = [
            (actor, ActivityLog.Action.LOGIN_SUCCESS, '', timedelta(hours=3)),
            (actor, ActivityLog.Action.LOGOUT, '', timedelta(hours=2, minutes=30)),
            (None, ActivityLog.Action.LOGIN_FAILED, 'İstifadəçi adı: naməlum_istifadeci', timedelta(minutes=45)),
            (actor, ActivityLog.Action.LOGIN_SUCCESS, '', timedelta(minutes=40)),
        ]
        for demo_actor, action, description, ago in demo_entries:
            log = ActivityLog.objects.create(
                actor=demo_actor, action=action, description=description, ip_address='127.0.0.1',
            )
            ActivityLog.objects.filter(pk=log.pk).update(created_at=now - ago)
        self.stdout.write(self._status('Activity log demo entries', True))

    def _status(self, label, created):
        if created:
            return self.style.SUCCESS(f'Created: {label}')
        return self.style.WARNING(f'Already exists: {label}')
