FONT_FAMILIES = {
    'serif': {
        'Times New Roman': 'Times New Roman, serif',
        'Georgia': 'Georgia, serif',
        'Garamond': 'Garamond, serif',
        'Palatino Linotype': 'Palatino Linotype, serif',
        'Book Antiqua': 'Book Antiqua, serif',
        'Baskerville': 'Baskerville, serif',
    },
    'sans-serif': {
        'Arial': 'Arial, sans-serif',
        'Helvetica': 'Helvetica, sans-serif',
        'Verdana': 'Verdana, sans-serif',
        'Trebuchet MS': 'Trebuchet MS, sans-serif',
        'Tahoma': 'Tahoma, sans-serif',
        'Gill Sans': 'Gill Sans, sans-serif',
        'Century Gothic': 'Century Gothic, sans-serif',
    },
    'monospace': {
        'Courier New': 'Courier New, monospace',
        'Lucida Console': 'Lucida Console, monospace',
        'Consolas': 'Consolas, monospace',
        'Monaco': 'Monaco, monospace',
        'Andale Mono': 'Andale Mono, monospace',
    },
    'cursive': {
        'Comic Sans MS': 'Comic Sans MS, cursive',
        'Brush Script MT': 'Brush Script MT, cursive',
    },
    'fantasy': {
        'Impact': 'Impact, fantasy',
        'Papyrus': 'Papyrus, fantasy',
    }
}

FONT_SIZES = {
    'heading': {
        'Small': 'text-3xl',
        'Medium': 'text-4xl',
        'Large': 'text-5xl',
        'Extra Large': 'text-6xl'
    },
    'subheading': {
        'Small': 'text-lg',
        'Medium': 'text-xl',
        'Large': 'text-2xl'
    }
}

# Helper functions
def get_font_choices():
    """Get alphabetically sorted list of fonts"""
    all_fonts = [
        (font_value, font_name) 
        for category in FONT_FAMILIES.values() 
        for font_name, font_value in category.items()
    ]
    return sorted(all_fonts, key=lambda x: x[1])  # Sort by display name

def get_font_sizes(type_):
    """Get font sizes for a specific type"""
    return [(size, label) for label, size in FONT_SIZES[type_].items()]