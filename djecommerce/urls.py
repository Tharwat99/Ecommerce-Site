from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext_lazy as _
admin.autodiscover()
#admin.site.enable_nav_sidebar = False

urlpatterns = i18n_patterns(
	path('',include('core.urls',namespace = 'core')),
    path('accounts/',include('allauth.urls')), 
    path('admin/', admin.site.urls),
    prefix_default_language=False
)

admin.site.index_title = _('My Index Title')
admin.site.site_header = _('My Site Administration')
admin.site.site_title = _('My Site Management')

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
