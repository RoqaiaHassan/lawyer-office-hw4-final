from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from lawyer.models import Lawyer, Service, ContactMessage, CaseRequest
from store.models import Branch, ServiceType

User = get_user_model()

class Command(BaseCommand):
    help = 'يُعيد تهيئة البيانات التجريبية في قاعدة البيانات ويُنشئ حساب مدير نموذجي.'

    def handle(self, *args, **options):
        self.stdout.write('مسح البيانات الموجودة...')
        ContactMessage.objects.all().delete()
        CaseRequest.objects.all().delete()
        Lawyer.objects.all().delete()
        Service.objects.all().delete()
        Branch.objects.all().delete()
        ServiceType.objects.all().delete()

        self.stdout.write('مسح المستخدمين الغير مدراء...')
        User.objects.exclude(is_superuser=True).delete()

        self.stdout.write('إنشاء حساب مدير افتراضي...')
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            },
        )
        if created:
            admin.set_password('admin1234')
            admin.save()
            self.stdout.write('تم إنشاء حساب المدّير: admin / admin1234')
        else:
            self.stdout.write('حساب المدّير موجود بالفعل.')

        self.stdout.write('إنشاء بيانات نموذجية...')
        lawyer1 = Lawyer.objects.create(
            name='أحمد عبد الله',
            phone='0599999999',
            email='ahmed@example.com',
            specialization='قانون تجاري',
            experience_years=8,
        )
        lawyer2 = Lawyer.objects.create(
            name='سارة فيصل',
            phone='0555555555',
            email='sara@example.com',
            specialization='قانون عائلي',
            experience_years=6,
        )

        Service.objects.create(title='استشارة قانونية', description='جلسة استشارية مع محامي مختص.', price=250.00)
        Service.objects.create(title='صياغة عقد', description='إعداد وصياغة عقود قانونية احترافية.', price=450.00)

        Branch.objects.create(name='فرع الرياض', city='الرياض', address='شارع العليا، مبنى ١٠')
        Branch.objects.create(name='فرع جدة', city='جدة', address='شارع التحلية، مبنى ٢٣')

        ServiceType.objects.create(name='استشارة فردية', description='جلسة قانونية لعرض الحالة ومناقشة الحلول.', base_fee=150.00)
        ServiceType.objects.create(name='مرافعة قضائية', description='تمثيل قانوني كامل أمام المحاكم.', base_fee=1200.00)

        self.stdout.write(self.style.SUCCESS('تمت إعادة التهيئة بنجاح.'))
        self.stdout.write('استخدم: python manage.py resetdb')
