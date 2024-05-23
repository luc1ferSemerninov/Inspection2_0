from django.contrib import admin
from .models import Start
from .models import Operators
from .models import log
from .models import Users



admin.site.register(Start)
admin.site.register(Operators)
admin.site.register(log)
admin.site.register(Users)