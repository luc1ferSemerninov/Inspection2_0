from django.contrib import admin
from .models import Start
from .models import Operators
from .models import log


admin.site.register(Start)
admin.site.register(Operators)
admin.site.register(log)