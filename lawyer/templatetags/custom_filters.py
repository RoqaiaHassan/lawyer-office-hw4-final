from django import template

register = template.Library()

# قاموس المصطلحات القانونية وتبسيطها للموكل
LEGAL_TERMS = {
    "المدعي": "طالب الحق / الموكل",
    "المدعى عليه": "الطرف الثاني",
    "العقود المسماة": "العقود القانونية المعتمدة",
    "الفسخ": "إنهاء العقد",
    "أتعاب": "تكلفة الخدمة القانونية",
    "جلسة": "جلسة المحاكمة",
    "قانون الأعمال": "قانون تجاري",
    "قانون الأعمال التجارية": "قانون تجاري",
}

@register.filter(name="legal_simplify")
def legal_simplify(value):
    """
    فلتر يقوم بتبسيط المصطلحات القانونية المعقدة لتصبح مفهومة للعملاء
    """
    text = str(value)
    for term, simple in LEGAL_TERMS.items():
        text = text.replace(term, simple)
    return text


@register.filter(name='to_hashtag')
def to_hashtag(value):
    """تحويل النص إلى هاشتاج بإزالة المسافات وإضافة رمز #"""
    if not value:
        return ""
    cleaned_value = str(value).strip().replace(" ", "_")
    return f"#{cleaned_value}"


@register.filter(name='fees_format')
def fees_format(value):
    """تنسيق الأتعاب المالية وإضافة العملة"""
    try:
        formatted_val = f"{int(value):,}"
        return f"{formatted_val} ر.ي"
    except (ValueError, TypeError):
        return value