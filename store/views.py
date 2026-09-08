from django.shortcuts import render

def store_index(request):
    """
    عرض الصفحة الرئيسية لتطبيق store مع قائمة الفروع والخدمات
    """
    branches = [
        {"id": 1, "city": "صنعاء", "address": "شارع حدة", "is_active": True},
        {"id": 2, "city": "عدن", "address": "خور مكسر", "is_active": True},
        {"id": 3, "city": "إب", "address": "شارع العدين", "is_active": False},
    ]
    
    services = [
        {"id": 1, "title": "استشارات تجارية", "price": 15000},
        {"id": 2, "title": "صياغة عقود", "price": 25000},
        {"id": 3, "title": "قضايا أحوال شخصية", "price": 20000},
    ]

    context = {
        "page_title": "فروعنا وخدماتنا",
        "branches": branches,
        "services": services,
    }
    return render(request, "store/store_index.html", context)


def branch_detail(request, branch_id):
    """
    عرض تفاصيل فرع محدد بواسطة id
    """
    context = {
        "branch_id": branch_id,
    }
    return render(request, "store/branch_detail.html", context)