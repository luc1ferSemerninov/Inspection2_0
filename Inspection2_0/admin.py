from django.contrib import admin
from .models import Start
from .models import Operator
from .models import log
from .models import User
from .models import Admin
from .models import Animator
from .models import Cashier
from .models import AdminHBD
from .models import Waiter



admin.site.register(Start)
admin.site.register(Operator)
admin.site.register(log)
admin.site.register(User)
admin.site.register(Admin)
admin.site.register(Animator)
admin.site.register(Cashier)
admin.site.register(AdminHBD)
admin.site.register(Waiter)