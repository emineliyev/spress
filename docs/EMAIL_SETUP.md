# Email (SMTP) quraşdırılması — sonradan tamamlamaq üçün

İlk deploy zamanı bu addım təxirə salınıb (korporativ email gözlənilir).
Bu sənəd, email hazır olanda `.env`-də dəqiq nəyi dəyişəcəyinizi göstərir.

## Bu olmadan nə işləmir

- **Əlaqə formu** (`/contacts/`) — istifadəçi formu göndərə bilir, sayt
  "Mesajınız göndərildi" deyir (mesaj CMS-də "Müraciətlər" bölməsində
  görünür), amma redaksiyaya bildiriş email-i getmir.
- **CMS → İstifadəçilər → Yeni istifadəçi** — bu, **500 xətası ilə
  uğursuz olacaq**. Yeni istifadəçiyə şifrə təyin etmək linki email
  vasitəsilə göndərilir; SMTP qurulmayıbsa, bu email göndərmə addımı
  xəta atır və bütün əməliyyat (istifadəçi yaradılması daxil) geri
  qaytarılır.
- **"Şifrəni sıfırla"** düyməsi (istənilən istifadəçi üçün) — eyni
  səbəbdən 500 xətası verəcək.

**Bunlara təsir etmir**: ilk admin hesabınız (7-ci addımda
`createsuperuser` ilə yaradılan) — bu, email göndərmədən birbaşa
terminalda şifrə təyin edir, SMTP-dən asılı deyil.

## Email hazır olanda nə etmək lazımdır

VPS-də bu faylı redaktə edin:

```bash
sudo -u spress nano /opt/spress/.env
```

Bu dörd sətri tapıb real dəyərlərlə doldurun:

```env
EMAIL_HOST=<SMTP server ünvanı>
EMAIL_HOST_USER=<istifadəçi adı / email ünvanı>
EMAIL_HOST_PASSWORD=<şifrə və ya app password>
DEFAULT_FROM_EMAIL=<göndərən kimi görünəcək email ünvanı>
```

`EMAIL_PORT` (587) və `EMAIL_USE_TLS` (True) adətən dəyişmədən qala
bilər — əksər SMTP xidmətləri (Gmail, korporativ Microsoft 365/Google
Workspace, Hostinger email və s.) bu standart TLS portunu dəstəkləyir.
Yalnız sizin provayderiniz fərqli port/protokol tələb edirsə dəyişin
(məsələn bəzi provayderlər 465 + SSL istifadə edir — belə olsa mənə
deyin, ayrıca tənzimləmə lazımdır).

### Nümunə 1 — Gmail (App Password ilə)

Tələb: Google hesabında 2 addımlı doğrulama aktiv olmalıdır.
https://myaccount.google.com/apppasswords ünvanından 16 xanalı kod alın.

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=sizin.hesabiniz@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
DEFAULT_FROM_EMAIL=sizin.hesabiniz@gmail.com
```

### Nümunə 2 — Korporativ email (Microsoft 365 / Google Workspace / öz domeniniz)

Provayderinizin "SMTP relay" məlumatlarını IT şöbənizdən və ya xidmət
təminatçınızdan alın — adətən bunlara bənzəyir:

```env
EMAIL_HOST=smtp.office365.com          # və ya smtp-relay.gmail.com, smtp.spress.az və s.
EMAIL_HOST_USER=xeber@spress.az
EMAIL_HOST_PASSWORD=<real şifrə>
DEFAULT_FROM_EMAIL=xeber@spress.az
```

### Nümunə 3 — Hostinger-in öz email xidməti

Əgər domeninizi Hostinger-də idarə edirsinizsə və orada email qutusu
yaratmısınızsa, adətən:

```env
EMAIL_HOST=smtp.hostinger.com
EMAIL_HOST_USER=xeber@spress.az
EMAIL_HOST_PASSWORD=<email qutusunun şifrəsi>
DEFAULT_FROM_EMAIL=xeber@spress.az
```

## Dəyişiklikdən sonra

`.env` faylını saxladıqdan sonra (`Ctrl+O`, `Enter`, `Ctrl+X`), tətbiqi
yenidən başladın ki, yeni dəyərləri oxusun:

```bash
sudo systemctl restart spress-gunicorn spress-celery-worker
```

## Test etmək

CMS-ə daxil olub **İstifadəçilər → Yeni istifadəçi** ilə (öz email
ünvanınızla) test hesabı yaradın. Xəta olmadan "İstifadəçi yaradıldı,
şifrə təyin etmək üçün email göndərildi" mesajı görünsə və email
qutunuza link gəlsə — SMTP düzgün işləyir.
