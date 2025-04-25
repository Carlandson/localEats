def get_visitor_context(base_context, business, subpage, page_type):
    """Additional context for visitor view"""
    #    subpage = SubPage.objects.filter(
    #     business=business, 
    #     page_type=page_type if not is_dashboard else 'home'
    # ).first()

    context = base_context.copy()
    model_name = f"{page_type.capitalize()}Page"
    try:
        page_model = apps.get_model('restaurants', model_name)
        # Get or create the specific page instance
        page_instance, created = page_model.objects.get_or_create(
            subpage=subpage
        )
        
        # Convert model instance to dictionary, excluding certain fields
        page_data_dict = {
            field.name: getattr(page_instance, field.name)
            for field in page_model._meta.fields
            if field.name not in ['id', 'subpage']  # Fields to exclude
        }
    except LookupError:
        page_data_dict = {}
    if subpage:
        # Get images for layout
        hero_primary = subpage.get_hero_primary()
        banner_2 = subpage.get_banner_2()
        banner_3 = subpage.get_banner_3()

        # Add layout data needed for display
        context['page_data'] = {
            f'{page_type}_page': page_data_dict,
            'business_subdirectory': business.subdirectory,
            'current_page': subpage,
            # Primary Hero Data
            'hero_heading': subpage.hero_heading,
            'hero_subheading': subpage.hero_subheading,
            'hero_button_text': subpage.hero_button_text,
            'hero_button_link': subpage.hero_button_link,
            'hero_layout': subpage.hero_layout,
            'hero_text_align': subpage.hero_text_align,
            'hero_heading_color': subpage.hero_heading_color,
            'hero_subheading_color': subpage.hero_subheading_color,
            'hero_size': subpage.hero_size,
            'show_hero_heading': subpage.show_hero_heading,
            'show_hero_subheading': subpage.show_hero_subheading,
            'show_hero_button': subpage.show_hero_button,
            'hero_heading_font': subpage.hero_heading_font,
            'hero_subheading_font': subpage.hero_subheading_font,
            'hero_heading_size': subpage.hero_heading_size,
            'hero_subheading_size': subpage.hero_subheading_size,
            'hero_primary': {
                'url': hero_primary.image.url if hero_primary else None,
                'alt_text': hero_primary.alt_text if hero_primary else None
            },
            'hero_button_bg_color': subpage.hero_button_bg_color,
            'hero_button_text_color': subpage.hero_button_text_color,
            
            # Banner 2 Data
            'banner_2': {
                'heading': subpage.banner_2_heading,
                'subheading': subpage.banner_2_subheading,
                'show_heading': subpage.show_banner_2_heading,
                'show_subheading': subpage.show_banner_2_subheading,
                'heading_font': subpage.banner_2_heading_font,
                'subheading_font': subpage.banner_2_subheading_font,
                'heading_size': subpage.banner_2_heading_size,
                'subheading_size': subpage.banner_2_subheading_size,
                'heading_color': subpage.banner_2_heading_color,
                'subheading_color': subpage.banner_2_subheading_color,
                'button_text': subpage.banner_2_button_text,
                'button_link': subpage.banner_2_button_link,
                'text_align': subpage.banner_2_text_align,
                'button_bg_color': subpage.banner_2_button_bg_color,
                'button_text_color': subpage.banner_2_button_text_color,
                'url': banner_2.image.url if banner_2 else None,
                'alt_text': banner_2.alt_text if banner_2 else None
            },
            
            # Banner 3 Data
            'banner_3': {
                'heading': subpage.banner_3_heading,
                'subheading': subpage.banner_3_subheading,
                'show_heading': subpage.show_banner_3_heading,
                'show_subheading': subpage.show_banner_3_subheading,
                'heading_font': subpage.banner_3_heading_font,
                'subheading_font': subpage.banner_3_subheading_font,
                'heading_size': subpage.banner_3_heading_size,
                'subheading_size': subpage.banner_3_subheading_size,
                'heading_color': subpage.banner_3_heading_color,
                'subheading_color': subpage.banner_3_subheading_color,
                'button_text': subpage.banner_3_button_text,
                'button_link': subpage.banner_3_button_link,
                'text_align': subpage.banner_3_text_align,
                'button_bg_color': subpage.banner_3_button_bg_color,
                'button_text_color': subpage.banner_3_button_text_color,
                'url': banner_3.image.url if banner_3 else None,
                'alt_text': banner_3.alt_text if banner_3 else None
            },
            'is_published': subpage.is_published,
        }
    
    # Add page-specific visitor content
    if page_type == 'events':
        events_page = getattr(subpage, 'eventspage', None)
        if events_page:
            context['events_data'] = [{
                'id': event.id,
                'name': event.name,
                'datetime': event.date.isoformat(),
                'description': event.description,
                'image_url': event.image.url if event.image else None
            } for event in events_page.events.filter(
                date__gte=timezone.now()
            ).order_by('date')]
    elif page_type == 'menu':
        context['menu_data'] = {
            'menus': Menu.objects.filter(
                business=business, 
                is_published=True
            ).prefetch_related('courses', 'courses__dishes'),
            'specials': Dish.objects.filter(
                menu__business=business, 
                is_special=True, 
                menu__is_published=True
            ),
        }
    return context

@login_required
def upload_image(request, model_name, object_id):
    if model_name not in ['business', 'dish']:
        return HttpResponseBadRequest("Invalid model type")

    model = Business if model_name == 'business' else Dish
    obj = get_object_or_404(model, id=object_id)

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.uploaded_by = request.user
            image.content_type = ContentType.objects.get_for_model(obj)
            image.object_id = obj.id
            image.save()
            return redirect('object_detail', model_name=model_name, object_id=object_id)
    else:
        form = ImageUploadForm()

    return render(request, 'upload_image.html', {'form': form, 'object': obj})

@login_required
def edit_layout(request, business_subdirectory):
    try:
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            messages.error(request, "You don't have permission to access this page.")  # Optional: add an error message
            return redirect('index')  # Replace 'index' with your index URL name

        # Get or create subpages for each type
        current_page = 'home'
        current_subpage = SubPage.objects.filter(
            business=business,
            page_type=current_page
        ).first()
        model_name = f"{current_page.capitalize()}Page"
        try:
            page_model = apps.get_model('restaurants', model_name)
            # Get or create the specific page instance
            page_instance, created = page_model.objects.get_or_create(
                subpage=current_subpage
            )
            
            # Convert model instance to dictionary, excluding certain fields
            page_data_dict = {
                field.name: getattr(page_instance, field.name)
                for field in page_model._meta.fields
                if field.name not in ['id', 'subpage']  # Fields to exclude
            }
        except LookupError:
            page_data_dict = {}
        # for links
        subpages = SubPage.objects.filter(business=business)
        published_pages = SubPage.get_published_subpages(business)
        existing_page_types = set([page.get('page_type') for page in published_pages])
        existing_page_types.add(current_page)  # Add current page to existing set
        available_pages = SubPage.get_available_subpages(business)
        hero_primary = current_subpage.get_hero_primary()
        banner_2 = current_subpage.get_banner_2()
        banner_3 = current_subpage.get_banner_3()
        page_data = {
            f'{current_page}_page': page_data_dict,
            'business_subdirectory': business_subdirectory,
            'current_page': current_page,
            # Primary Hero Data
            'hero_heading': current_subpage.hero_heading,
            'hero_subheading': current_subpage.hero_subheading,
            'hero_button_text': current_subpage.hero_button_text,
            'hero_button_link': current_subpage.hero_button_link,
            'hero_layout': current_subpage.hero_layout,
            'hero_text_align': current_subpage.hero_text_align,
            'hero_heading_color': current_subpage.hero_heading_color,
            'hero_subheading_color': current_subpage.hero_subheading_color,
            'hero_size': current_subpage.hero_size,
            'show_hero_heading': current_subpage.show_hero_heading,
            'show_hero_subheading': current_subpage.show_hero_subheading,
            'show_hero_button': current_subpage.show_hero_button,
            'hero_heading_font': current_subpage.hero_heading_font,
            'hero_subheading_font': current_subpage.hero_subheading_font,
            'hero_heading_size': current_subpage.hero_heading_size,
            'hero_subheading_size': current_subpage.hero_subheading_size,
            'hero_primary': {
                'url': hero_primary.image.url if hero_primary else None,
                'alt_text': hero_primary.alt_text if hero_primary else None
            },
            # Button Styles
            'hero_button_bg_color': current_subpage.hero_button_bg_color,
            'hero_button_text_color': current_subpage.hero_button_text_color,
            
            # Banner 2 Data
            'banner_2': {
                'heading': current_subpage.banner_2_heading,
                'subheading': current_subpage.banner_2_subheading,
                'show_heading': current_subpage.show_banner_2_heading,
                'show_subheading': current_subpage.show_banner_2_subheading,
                'heading_font': current_subpage.banner_2_heading_font,
                'subheading_font': current_subpage.banner_2_subheading_font,
                'heading_size': current_subpage.banner_2_heading_size,
                'subheading_size': current_subpage.banner_2_subheading_size,
                'heading_color': current_subpage.banner_2_heading_color,
                'subheading_color': current_subpage.banner_2_subheading_color,
                'button_text': current_subpage.banner_2_button_text,
                'button_link': current_subpage.banner_2_button_link,
                'text_align': current_subpage.banner_2_text_align,
                'button_bg_color': current_subpage.banner_2_button_bg_color,
                'button_text_color': current_subpage.banner_2_button_text_color,
                'url': banner_2.image.url if banner_2 else None,
                'alt_text': banner_2.alt_text if banner_2 else None
            },
            
            # Banner 3 Data
            'banner_3': {
                'heading': current_subpage.banner_3_heading,
                'subheading': current_subpage.banner_3_subheading,
                'show_heading': current_subpage.show_banner_3_heading,
                'show_subheading': current_subpage.show_banner_3_subheading,
                'heading_font': current_subpage.banner_3_heading_font,
                'subheading_font': current_subpage.banner_3_subheading_font,
                'heading_size': current_subpage.banner_3_heading_size,
                'subheading_size': current_subpage.banner_3_subheading_size,
                'heading_color': current_subpage.banner_3_heading_color,
                'subheading_color': current_subpage.banner_3_subheading_color,
                'button_text': current_subpage.banner_3_button_text,
                'button_link': current_subpage.banner_3_button_link,
                'text_align': current_subpage.banner_3_text_align,
                'button_bg_color': current_subpage.banner_3_button_bg_color,
                'button_text_color': current_subpage.banner_3_button_text_color,
                'url': banner_3.image.url if banner_3 else None,
                'alt_text': banner_3.alt_text if banner_3 else None
            },
            'is_published': current_subpage.is_published,
        }

        context = {
            # For JavaScript initialization
            'page_data': page_data,
            # For template rendering
            'business_details': business,
            'business_subdirectory': business_subdirectory,
            # changed to published_pages
            'subpages': subpages,
            'subpage': current_subpage,
            'current_page': current_page,
            'available_pages': available_pages,
            'published_pages': published_pages,
            # Choices/Options for template dropdowns and selectors
            'hero_choices': SubPage.HERO_CHOICES,
            'nav_styles': business.NAV_CHOICES,
            'footer_styles': business.FOOTER_CHOICES,
            'text_align_choices': SubPage.TEXT_ALIGN_CHOICES,
            'font_choices': get_font_choices(),
            'heading_sizes': get_font_sizes('heading'),
            'subheading_sizes': get_font_sizes('subheading'),
            'hero_size_choices': SubPage.HERO_SIZE_CHOICES,
            'hero_primary': hero_primary,
            'banner_2': banner_2,
            'banner_3': banner_3,
            'preview_mode': True,
            'hero_heading_font': current_subpage.hero_heading_font,
            'is_owner': True,
            'is_edit_page': True,
        }
        
        return render(request, "edit_layout.html", context)
        
    except Exception as e:
        logger.error(f"Error in edit_layout: {str(e)}\n{traceback.format_exc()}")
        return HttpResponse(f"Error loading layout editor: {str(e)}", status=500)
    

@require_POST
def update_layout(request, business_subdirectory):
    print("update_layout called")
    try:
        data = json.loads(request.body)
        print("Received data:", data)
        
        field_type = data.get('fieldType')
        field_name = data.get('fieldName', '')
        value = data.get('value', '')
        page_type = data.get('page_type')
        is_global = data.get('isGlobal', False)
        return_preview = data.get('return_preview', False)
        print(f"Parsed values: field_type={field_type}, field_name={field_name}, value={value}, page_type={page_type}")

        # Get the business and subpage
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        response_data = {'success': True}
        # Handle new page creation
        if field_type == 'new_page':
            timestamp = timezone.now().strftime('%Y%m%d-%H%M%S')
            unique_slug = f"{business.subdirectory}-{page_type}-{timestamp}"
            page_type_display = dict(SubPage.PAGE_TYPES).get(page_type, page_type.title())
            # Create the subpage
            new_subpage = SubPage.objects.create(
                business=business,
                page_type=page_type,
                title=f"{business.business_name} {page_type_display}",
                slug=unique_slug,
                is_published=False
            )
            # Create the corresponding page content based on type
            if page_type == 'menu':
                # Create menu and link it to the menu page
                Menu.objects.create(
                    business=business,
                    name=f"{business.business_name} Menu",
                    description="Our main menu",
                    subpage=new_subpage,  # Link menu to the menu page
                    display_style='grid'
                )
            elif page_type == 'about':
                AboutUsPage.objects.create(
                    subpage=new_subpage,
                    content=""
                )
            elif page_type == 'events':
                EventsPage.objects.create(
                    subpage=new_subpage
                )
            elif page_type == 'specials':
                SpecialsPage.objects.create(
                    subpage=new_subpage
                )
            subpage = get_object_or_404(SubPage, business=business, page_type=page_type)
            response_data['message'] = f'Created new {page_type} page'

        # Handle brand color updates
        else:
            subpage = get_object_or_404(SubPage, business=business, page_type=page_type)
            if field_type == 'color' and field_name in ['primary', 'secondary', 'text-color', 'hover-color']:
                color_field_map = {
                    'primary': 'primary_color',
                    'secondary': 'secondary_color',
                    'text-color': 'text_color',
                    'hover-color': 'hover_color'
                }
                actual_field_name = color_field_map.get(field_name)
                if actual_field_name:
                    setattr(business, actual_field_name, value)
                    business.save()
            elif is_global:  # Add this block for global components
                # These are business-level settings
                setattr(business, field_name, value)
                business.save()
            else:
                # Handle regular subpage updates
                setattr(subpage, field_name, value)
                print(field_name, value)
                subpage.save()

        if return_preview:
            # First render the content template
            content_html = render_to_string(f'components/preview/{page_type}.html', {
                'business_details': business,
                'subpage': subpage,
                'hero_primary': subpage.get_hero_primary(),
                'banner_2': subpage.get_banner_2(),
                'banner_3': subpage.get_banner_3(),
                'preview_mode': True,
                'current_page': page_type,
            })

            # Then render the navigation
            nav_html = render_to_string(
                f'components/navigation/top-nav/{business.navigation_style}.html',
                {
                    'business_details': business,
                    'subdirectory': business_subdirectory,
                    'primary_color': business.primary_color,
                    'secondary_color': business.secondary_color,
                    'text_color': business.text_color,
                    'hover_color': business.hover_color,
                }
            )

            # Render the footer
            footer_html = render_to_string(
                f'components/footer/{business.footer_style}.html',
                {
                    'business_details': business,
                    'primary_color': business.primary_color,
                    'secondary_color': business.secondary_color,
                    'text_color': business.text_color,
                    'hover_color': business.hover_color,
                }
            )

            # Combine all parts in the preview layout
            preview_html = render_to_string('components/preview/preview_layout.html', {
                'navigation_html': nav_html,
                'content_html': content_html,
                'footer_html': footer_html,
                'business_details': business,
                'subpage': subpage,
                'current_page': page_type,
                'preview_mode': True,
                'hero_primary': subpage.get_hero_primary(),
                'banner_2': subpage.get_banner_2(),
                'banner_3': subpage.get_banner_3(),
                'business_subdirectory': business_subdirectory,
            })
            response_data['preview_html'] = preview_html

        return JsonResponse(response_data)

    except Exception as e:
        print(f"Error in update_layout: {str(e)}")
        print(f"Request body: {request.body}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    
@login_required
def preview_page(request, business_subdirectory, page_type):
    print("preview_page called")
    try:
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            return HttpResponseForbidden()
            
        subpage = SubPage.objects.get(
            business=business,
            page_type=page_type
        )
        
        # Add debug logging
        logger.debug(f"Loading preview for {business_subdirectory}, page type: {page_type}")
        
        # Get all hero images
        hero_primary = subpage.get_hero_primary()
        banner_2 = subpage.get_banner_2()
        banner_3 = subpage.get_banner_3()
        
        # Debug log the images
        logger.debug(f"Hero images found: Primary={hero_primary}, Banner2={banner_2}, Banner3={banner_3}")
        
        context = {
            'business_details': business,
            'subpage': subpage,
            'hero_primary': hero_primary,
            'banner_2': banner_2,
            'banner_3': banner_3,
            'preview_mode': True,
            'business_subdirectory': business_subdirectory,
            'debug': True,  # Make sure debug is True
            # Add specific color context
            'primary_color': business.primary_color,
            'secondary_color': business.secondary_color,
            'text_color': business.text_color,
            'hover_color': business.hover_color,
            'navigation_style': business.navigation_style,
            'footer_style': business.footer_style,
            'current_page': page_type,
            'is_published': subpage.is_published
        }
        
        # Map page_type to template name
        template_mapping = {
            'home': 'home',
            'about': 'about',
            'menu': 'menu',
            'contact': 'contact',
            'gallery': 'gallery',
            'events': 'events',
            'catering': 'catering',
            'order': 'order',
            'reservations': 'reservations'
        }
        
        # Get the template name from mapping or default to home
        template_page = template_mapping.get(page_type, 'home')
        template_name = f'visitor_pages/{template_page}.html'
        
        logger.debug(f"Using template: {template_name}")
        
        return render(request, 'components/preview/preview_layout.html', context)
        
    except Exception as e:
        logger.error(f"Error in preview_page: {str(e)}")
        logger.exception("Full traceback:")
        return HttpResponse(f"Error loading preview: {str(e)}", status=500)
    
@login_required
def get_page_data(request, business_subdirectory, page_type):
    print("get_page_data called")
    try:
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
            
        subpage = get_object_or_404(SubPage, business=business, page_type=page_type)
        
        # Get all images
        hero_primary = subpage.get_hero_primary()
        banner_2 = subpage.get_banner_2()
        banner_3 = subpage.get_banner_3()
        
        # Debug log to verify we have the images
        logger.debug(f"Images found - Primary: {hero_primary}, Banner2: {banner_2}, Banner3: {banner_3}")

        # def get_safe_image_url(image_obj):
        #     if image_obj and hasattr(image_obj, 'image'):
        #         try:
        #             image_url = image_obj.image.url
        #             logger.debug(f"Got image URL: {image_url}")
        #             return image_url
        #         except Exception as e:
        #             logger.error(f"Error getting image URL: {e}")
        #             return None
        #     return None
        
        data = {
            'subpage_id': subpage.id,
            'hero_heading': subpage.hero_heading,
            'hero_subheading': subpage.hero_subheading,
            'hero_button_text': subpage.hero_button_text,
            'hero_layout': subpage.hero_layout,
            'hero_text_align': subpage.hero_text_align,
            'hero_heading_color': subpage.hero_heading_color,
            'hero_subheading_color': subpage.hero_subheading_color,
            'hero_button_link': subpage.hero_button_link,
            'hero_size': subpage.hero_size,
            'is_published': subpage.is_published,
            'hero_primary': {
                'url': hero_primary.image.url if hero_primary else None,
                'alt_text': hero_primary.alt_text if hero_primary else None
            },
            # 'hero_image': {
            #     'url': get_safe_image_url(hero_primary),
            #     'alt': 'hero_primary'
            # },
            # 'banner_2': {
            #     'url': get_safe_image_url(banner_2),
            #     'alt': 'banner_2'
            # },
            # 'banner_3': {
            #     'url': get_safe_image_url(banner_3),
            #     'alt': 'banner_3'
            # },
            # 'images': {
            #     'hero_primary': {
            #         'url': get_safe_image_url(hero_primary),
            #         'alt': 'hero_primary'
            #     },
            #     'banner_2': {
            #         'url': get_safe_image_url(banner_2),
            #         'alt': 'banner_2'
            #     },
            #     'banner_3': {
            #         'url': get_safe_image_url(banner_3),
            #         'alt': 'banner_3'
            #     }
            # },
            'banner_2': {
                'heading': subpage.banner_2_heading,
                'subheading': subpage.banner_2_subheading,
                'show_heading': subpage.show_banner_2_heading,
                'show_subheading': subpage.show_banner_2_subheading,
                'heading_font': subpage.banner_2_heading_font,
                'subheading_font': subpage.banner_2_subheading_font,
                'heading_size': subpage.banner_2_heading_size,
                'subheading_size': subpage.banner_2_subheading_size,
                'heading_color': subpage.banner_2_heading_color,
                'subheading_color': subpage.banner_2_subheading_color,
                'button_text': subpage.banner_2_button_text,
                'button_link': subpage.banner_2_button_link,
                'button_bg_color': subpage.banner_2_button_bg_color,
                'button_text_color': subpage.banner_2_button_text_color,
                'button_size': subpage.banner_2_button_size,
                'show_button': subpage.show_banner_2_button,
                'text_align': subpage.banner_2_text_align,
                'url': banner_2.image.url if banner_2 else None,
                'alt_text': banner_2.alt_text if banner_2 else None

            },
            'banner_3': {
                'heading': subpage.banner_3_heading,
                'subheading': subpage.banner_3_subheading,
                'show_heading': subpage.show_banner_3_heading,
                'show_subheading': subpage.show_banner_3_subheading,
                'heading_font': subpage.banner_3_heading_font,
                'subheading_font': subpage.banner_3_subheading_font,
                'heading_size': subpage.banner_3_heading_size,
                'subheading_size': subpage.banner_3_subheading_size,
                'heading_color': subpage.banner_3_heading_color,
                'subheading_color': subpage.banner_3_subheading_color,
                'button_text': subpage.banner_3_button_text,
                'button_link': subpage.banner_3_button_link,
                'button_bg_color': subpage.banner_3_button_bg_color,
                'button_text_color': subpage.banner_3_button_text_color,
                'button_size': subpage.banner_3_button_size,
                'show_button': subpage.show_banner_3_button,
                'text_align': subpage.banner_3_text_align,
                'url': banner_3.image.url if banner_3 else None,
                'alt_text': banner_3.alt_text if banner_3 else None
            }
        }
        logger.debug(f"get_page_data data: {data}")
        return JsonResponse(data)
        
    except Exception as e:
        logger.error(f"Error in get_page_data: {str(e)}")
        logger.exception("Full traceback:")
        return JsonResponse({'error': str(e)}, status=500)
    
@login_required
def preview_component(request, business_subdirectory):
    print("preview_component called")
    try:
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            return HttpResponseForbidden()

        # Get data from request
        data = json.loads(request.body)
        component = data.get('component')
        value = data.get('value')
        page_type = data.get('page_type', 'home')

        # Get the subpage
        subpage = get_object_or_404(SubPage, business=business, page_type=page_type)

        # Determine which template and context to use based on the component
        template_name = None
        context = {
            'business_details': business,
            'subpage': subpage,
            'business_subdirectory': business_subdirectory,
        }

        # Handle different component types
        if component.startswith('hero_'):
            template_name = f"components/hero/{subpage.hero_layout}.html"
            # Add hero-specific context if needed
            context.update({
                'hero_primary': subpage.get_hero_primary(),
                'banner_2': subpage.get_banner_2(),
                'banner_3': subpage.get_banner_3(),
            })
        elif component == 'navigation':
            template_name = f"components/navigation/top-nav/{business.navigation_style}.html"
            context.update({
                'menu_page': True,
                'about_page': True,
                'events_page': True,
            })
        # Add more component types as needed

        if not template_name:
            return JsonResponse({
                'success': False,
                'error': f'Unknown component: {component}'
            }, status=400)

        try:
            html = render_to_string(template_name, context)
            return JsonResponse({
                'success': True,
                'html': html,
                'component': component
            })
        except Exception as e:
            logger.error(f"Template rendering error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Template rendering error: {str(e)}'
            }, status=500)

    except Exception as e:
        logger.error(f"Preview component error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    
@login_required
def preview_navigation(request, business_subdirectory, style):
    print("preview_navigation called")
    try:
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            return HttpResponseForbidden()
        
        template_name = f"components/navigation/top-nav/{style}.html"
        context = {
            'business_details': business,
            'business_subdirectory': business_subdirectory,
            'menu_page': True,
            'about_page': True,
            'events_page': True,
        }
        
        html = render_to_string(template_name, context)
        return HttpResponse(html)
            
    except Exception as e:
        logger.error(f"Error in preview_navigation: {str(e)}")
        return HttpResponse(f"Error: {str(e)}", status=500)
    
def update_global_component(request, business_subdirectory):
    print("update_global_component called")
    try:
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        data = json.loads(request.body)
        component = data.get('component')
        style = data.get('style')
        page_type = request.GET.get('page_type')

        if not page_type:
            return JsonResponse({'error': 'Page type is required'}, status=400)
        try:
            subpage = SubPage.objects.get(business=business, page_type=page_type)
        except SubPage.DoesNotExist:
            return JsonResponse({'error': f'Page {page_type} not found'}, status=404)

        logger.debug(f"Updating component: {component} with style: {style} for page: {page_type}")

        # Map components to their model, field, and choices
        component_map = {
            # Global components (Business model)
            'navigation': {
                'model': business,
                'field': 'navigation_style',
                'choices': business.NAV_CHOICES,
                'instance': business
            },
            'main_font': {
                'model': business,
                'field': 'main_font',
                'choices': get_font_choices(),  # From your constants.py
                'instance': business
            },
            'hero_layout': {
                'model': SubPage,
                'field': 'hero_layout',
                'choices': SubPage.HERO_CHOICES,
                'instance': SubPage.objects.get(business=business, page_type=page_type)
            },
            'hero_heading_font': {
                'model': SubPage,
                'field': 'hero_heading_font',
                'choices': get_font_choices(),
                'instance': SubPage.objects.get(business=business, page_type=page_type)
            },
            'hero_subheading_font': {
                'model': SubPage,
                'field': 'hero_subheading_font',
                'choices': get_font_choices(),
                'instance': SubPage.objects.get(business=business, page_type=page_type)
            },
            'hero_heading_size': {
                'model': SubPage,
                'field': 'hero_heading_size',
                'choices': get_font_sizes('heading'),
                'instance': SubPage.objects.get(business=business, page_type=page_type)
            },
            'hero_subheading_size': {
                'model': SubPage,
                'field': 'hero_subheading_size',
                'choices': get_font_sizes('subheading'),
                'instance': SubPage.objects.get(business=business, page_type=page_type)
            },
            'footer_style': {
                'model': business,
                'field': 'footer_style',
                'choices': business.FOOTER_CHOICES,
                'instance': business
            },
            'hero_size': {
                'model': SubPage,
                'field': 'hero_size',
                'choices': SubPage.HERO_SIZE_CHOICES,
                'instance': SubPage.objects.get(business=business, page_type=page_type)
            },
            'is_published': {
                'model': SubPage,
                'field': 'is_published',
                'instance': subpage,
            },
            
        }

        if component not in component_map:
            return JsonResponse({'error': f'Invalid component: {component}'}, status=400)

        component_info = component_map[component]

        if component == 'is_published':
            if isinstance(style, str):
                style = style.lower() == 'true'
            logger.debug(f"Updating publish state for page {page_type} to {style}")
            # Update the instance
            instance = component_info['instance']
            setattr(instance, component_info['field'], style)
            instance.save(update_fields=[component_info['field']])
            
            # Log successful update
            logger.debug(f"Successfully updated publish state for page {page_type} to {style}")
            
            return JsonResponse({'success': True})

        else:
            # Validate choices for all other components
            if component == 'main_font':
                valid_styles = [font[0] for font in component_info['choices']]
            else:
                valid_styles = [choice[0] for choice in component_info['choices']]

            # Only validate non-boolean components
            if style not in valid_styles:
                return JsonResponse({
                    'error': f'Invalid {component} style. Got "{style}", expected one of: {valid_styles}'
                }, status=400)

        # Get the instance to update
        instance = component_info['instance']
        field_name = component_info['field']

        # Update the specific field
        setattr(instance, field_name, style)
        
        # Save only the updated field
        instance.save(update_fields=[field_name])
        
        logger.debug(f"Successfully updated {component} to {style}")
        return JsonResponse({'success': True})

    except SubPage.DoesNotExist:
        logger.error(f"SubPage not found for {page_type}")
        return JsonResponse({'error': f'Page {page_type} not found'}, status=404)
    except Exception as e:
        logger.error(f"Error in update_global_component: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
    
@require_POST
@login_required
def save_layout(request, business_subdirectory):
    print("save_layout called")
    """Save layout preferences"""
    business = get_object_or_404(Business, subdirectory=business_subdirectory, owner=request.user)
    
    try:
        data = json.loads(request.body)
        business.navigation_style = data.get('navigation_style')
        business.hero_style = data.get('hero_style')
        business.primary_color = data.get('primary_color')
        business.secondary_color = data.get('secondary_color')
        business.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
@login_required
@require_POST
def upload_hero_image(request, business_subdirectory):
    print("upload_hero_image called")
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})

    try:
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            return JsonResponse({'success': False, 'error': 'Unauthorized'})

        page_type = request.POST.get('page_type', 'home')
        banner_type = request.POST.get('banner_type', 'primary')
        image_file = request.FILES.get('image')
        if not image_file:
            return JsonResponse({'success': False, 'error': 'No image provided'})

        return_preview = request.POST.get('return_preview') == 'true'

        # validate image file
        if not image_file:
            return JsonResponse({'success': False, 'error': 'No image provided'})

        # Check file size
        if image_file.size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
            return JsonResponse({
                'success': False, 
                'error': f'File size cannot exceed {settings.FILE_UPLOAD_MAX_MEMORY_SIZE // (1024*1024)}MB'
            })

        # Check file extension
        ext = image_file.name.split('.')[-1].lower()
        if ext not in Image.ALLOWED_EXTENSIONS:
            return JsonResponse({
                'success': False,
                'error': f'Unsupported file extension. Allowed types: {", ".join(Image.ALLOWED_EXTENSIONS)}'
            })
        
        try:
            with PILImage.open(image_file) as img:
                img.verify()
                # Reset file pointer after verify
                image_file.seek(0)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Invalid image file'
            })
        logger.debug(f"Processing {banner_type} image upload for {business_subdirectory}, page type: {page_type}")
        logger.debug(f"Image file: {image_file.name}, size: {image_file.size}")

        # Get or create the subpage
        subpage, created = SubPage.objects.get_or_create(
            business=business,
            page_type=page_type,
            defaults={
                'title': f"{business.business_name} {page_type.title()}",
            }
        )

        # Determine the alt_text based on banner type
        alt_text_map = {
            'hero_primary': 'hero_primary',
            'banner_2': 'banner_2',
            'banner_3': 'banner_3',
        }
        alt_text = alt_text_map.get(banner_type)
        
        if not alt_text:
            logger.error(f"Invalid banner type received: {banner_type}")
            return JsonResponse({'error': f'Invalid banner type: {banner_type}'}, status=400)

        # Remove existing image for this banner type if it exists
        content_type = ContentType.objects.get_for_model(SubPage)
        old_image = Image.objects.filter(
            content_type=content_type,
            object_id=subpage.id,
            alt_text=alt_text
        ).first()
        
        if old_image:
            logger.debug(f"Removing old {banner_type} image: {old_image.image.url}")
            old_image.delete()

        # Create new image
        try:
            new_image = Image.objects.create(
                image=image_file,
                uploaded_by=request.user,
                content_type=content_type,
                object_id=subpage.id,
                alt_text=alt_text,
                caption=f'{banner_type.title()} image for {business.business_name} {page_type} page'
            )
        except ValidationError as e:
            logger.error(f"Validation error during image upload: {str(e)}")
            # Convert ValidationError to a more readable format
            if hasattr(e, 'message_dict'):
                error_message = '; '.join([f"{k}: {', '.join(v)}" for k, v in e.message_dict.items()])
            else:
                error_message = str(e)
            return JsonResponse({
                'success': False,
                'error': error_message
            })

        image_url = new_image.image.url
        logger.debug(f"New {banner_type} image created with URL: {image_url}")
        response_data = {
            'success': True,
            'image_url': image_url,
            'debug_info': {
                'subpage_id': subpage.id,
                'content_type': str(content_type),
                'alt_text': new_image.alt_text,
                'banner_type': banner_type
            }
        }
        if return_preview:
            preview_html = render_to_string(f'visitor_pages/{page_type}.html', {
                'business_details': business,
                'subpage': subpage,
                'hero_primary': subpage.get_hero_primary(),
                'banner_2': subpage.get_banner_2(),
                'banner_3': subpage.get_banner_3(),
                'hero_primary': subpage.get_hero_primary(),
                'preview_mode': True,
                'business_subdirectory': business_subdirectory,
                'debug': True,
                'primary_color': business.primary_color,
                'secondary_color': business.secondary_color,
                'text_color': business.text_color,
                'hover_color': business.hover_color,
                'navigation_style': business.navigation_style,
                'footer_style': business.footer_style,
                'is_published': subpage.is_published
            })
            response_data['preview_html'] = preview_html

        return JsonResponse(response_data)

    except Exception as e:
        logger.error(f"Error in upload_hero_image: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})
    
@login_required
def remove_hero_image(request, business_subdirectory):
    print("remove_hero_image called")
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})

    try:
        # Parse the JSON body
        data = json.loads(request.body)
        print(f"data={data}")
        page_type = data.get('page_type')
        banner_type = data.get('banner_type')  # Add this
        return_preview = data.get('return_preview', False)  # Add this
        
        if not page_type or not banner_type:
            return JsonResponse({'success': False, 'error': 'Page type and banner type required'})

        # Get the business and verify ownership
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            return JsonResponse({'success': False, 'error': 'Unauthorized'})

        # Get the specific subpage
        subpage = get_object_or_404(SubPage, business=business, page_type=page_type)

        # Get and delete the specific banner image
        content_type = ContentType.objects.get_for_model(SubPage)
        print(f"page_type={page_type},banner_type={banner_type}, content_type={content_type}")
        hero_image = Image.objects.filter(
            content_type=content_type,
            object_id=subpage.id,
            alt_text=banner_type  # Use the specific banner type
        ).first()

        response_data = {'success': True}
        print(hero_image)
        if hero_image:
            print(f"Deleting {banner_type} image: {hero_image.id} for subpage: {subpage.id}")
            hero_image.delete()
            response_data['message'] = f'{banner_type} image removed successfully'
        else:
            print(f"No {banner_type} image found for subpage: {subpage.id}")
            response_data['message'] = f'No {banner_type} image found'

        # Add preview HTML if requested
        if return_preview:
            preview_html = render_to_string(f'visitor_pages/{page_type}.html', {
                'business_details': business,
                'subpage': subpage,
                'banner_2': subpage.get_banner_2(),
                'banner_3': subpage.get_banner_3(),
                'hero_primary': subpage.get_hero_primary(),
                'preview_mode': True,
                'business_subdirectory': business_subdirectory,
                'debug': True,
                'primary_color': business.primary_color,
                'secondary_color': business.secondary_color,
                'text_color': business.text_color,
                'hover_color': business.hover_color,
                'navigation_style': business.navigation_style,
                'footer_style': business.footer_style,
                'is_published': subpage.is_published
            })
            response_data['preview_html'] = preview_html

        return JsonResponse(response_data)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        print(f"Error removing hero image: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})
    
@login_required
@require_http_methods(["POST"])
def update_subpage_hero(request, business_subdirectory, subpage_id):
    print("update_subpage_hero called")
    try:
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

        subpage = get_object_or_404(SubPage, id=subpage_id, business=business)
        data = json.loads(request.body)
        
        field = data.get('field')
        value = data.get('value')

        valid_fields = ['heading', 'subheading', 'button_text', 'layout']
        if field not in valid_fields:
            return JsonResponse({'success': False, 'error': 'Invalid field'}, status=400)

        setattr(subpage, f'hero_{field}', value)
        subpage.save()

        return JsonResponse({'success': True})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
 

@require_POST
def update_hero(request, business_subdirectory):
    # Convert old format to new format
    data = json.loads(request.body)
    new_data = {
        'fieldType': 'text',  # or appropriate type
        'fieldName': data.get('field'),
        'value': data.get('value'),
        'page_type': data.get('page_type')
    }
    request._body = json.dumps(new_data).encode('utf-8')
    return update_layout(request, business_subdirectory)

@login_required
def layout_editor(request, business_subdirectory):
    try:
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            return HttpResponseForbidden()

        # Get current page type from query params or default to 'home'
        current_page = request.GET.get('page_type', 'home')
        # Get available pages for the button links
        published_pages = SubPage.get_published_subpages(business)
        available_pages = [
            page for page in published_pages 
            if page['page_type'] != current_page
        ]

        # Get all subpages for this Business
        subpages = {
            page_type: SubPage.objects.get_or_create(
                business=business,
                page_type=page_type,
                defaults={'title': f"{business.business_name} {page_type.title()}"}
            )[0]
            for page_type in ['home', 'about', 'menu', 'events', 'specials']
        }

        # Get current subpage
        subpage = subpages[current_page]

        context = {
            'business_details': business,
            'business_subdirectory': business_subdirectory,
            'subpages': subpages,
            'subpage': subpage,
            'current_page': current_page,
            'page_type': current_page,    
            'hero_choices': SubPage.HERO_CHOICES,
            'nav_styles': business.NAV_CHOICES,
            'available_pages': available_pages,
        }

        logger.debug(f"Layout editor context: {context}")
        return render(request, 'components/layout_editor/layout_editor.html', context)

    except Exception as e:
        logger.error(f"Error in layout_editor: {str(e)}")
        logger.exception("Full traceback:")
        return HttpResponse(f"Error loading layout editor: {str(e)}", status=500)
    

@login_required
def update_brand_colors(request, business_subdirectory):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})

    try:
        data = json.loads(request.body)
        color_type = data.get('color_type')
        color_value = data.get('color_value')

        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            return JsonResponse({'success': False, 'error': 'Unauthorized'})

        # Update the appropriate color field
        if color_type == 'primary':
            business.primary_color = color_value
        elif color_type == 'secondary':
            business.secondary_color = color_value
        elif color_type == 'hover-color':
            business.hover_color = color_value
        elif color_type == 'text-color':
            business.text_color = color_value
        else:
            return JsonResponse({'success': False, 'error': 'Invalid color type'})

        business.save()
        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})