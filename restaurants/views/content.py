@login_required
def page_content(request, business_subdirectory, page_type):
    try:
        logger.debug(f"=== Starting page_content view ===")
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        subpage = get_object_or_404(SubPage, business=business, page_type=page_type)
        
        # Debug the subpage
        logger.debug(f"Found subpage: {subpage.id} with layout: {subpage.hero_layout}")
        
        # Get hero images with detailed logging
        hero_primary = subpage.get_hero_primary()
        logger.debug(f"get_hero_primary() returned: {hero_primary}")
        
        banner_2 = subpage.get_banner_2()
        logger.debug(f"get_banner_2() returned: {banner_2}")
        
        banner_3 = subpage.get_banner_3()
        logger.debug(f"get_banner_3() returned: {banner_3}")
        
        # Create context
        context = {
            'business_details': business,
            'subpage': subpage,
            'hero_primary': hero_primary,
            'banner_2': banner_2,
            'banner_3': banner_3,
            'business_subdirectory': business_subdirectory,
            'is_preview': True,
            'debug': True,
            'page_type': page_type,
        }
        
        # Log the final context
        logger.debug("=== Context being sent to template ===")
        for key, value in context.items():
            logger.debug(f"{key}: {value}")
        
        template_name = f'components/hero/{subpage.hero_layout}.html'
        logger.debug(f"Using template: {template_name}")
        
        response = render(request, template_name, context)
        logger.debug("=== Finished rendering template ===")
        return response
        
    except Exception as e:
        logger.error(f"Error in page_content: {str(e)}")
        logger.exception("Full traceback:")
        return HttpResponse(f"Error loading page content: {str(e)}", status=500)