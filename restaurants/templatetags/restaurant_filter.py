from django import template

register = template.Library()

@register.filter
def filter_hero_images(images):
    """Filter images to get hero images for the specific page"""
    return images.filter(alt_text__startswith='hero_').order_by('-created_at')[:1]