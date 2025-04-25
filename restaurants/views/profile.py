def profile(request):
    business_list = Business.objects.all()
    owner_business = []
    owner_check = False
    print(business_list)
    for business in business_list:
        if business.owner == request.user:
            owner_business.append(business)
            owner_check = True
    return render(request, "profile.html", {"profile": profile, "owner_check" : owner_check, "owner_business" : owner_business})



@login_required
def create(request):
    user = request.user
    gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

    if request.method == "GET":
        context = {
            "create": BusinessCreateForm(),
            "owner": user,
            "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY
        }
        return render(request, "create.html", context)

    if request.method == "POST":
        form = BusinessCreateForm(request.POST)
        if form.is_valid():
            new_business = form.save(commit=False)
            new_business.owner = user
            cuisine_data = request.POST.get('cuisine', '')
            if cuisine_data:
                cuisine_names = cuisine_data.split(',')
                cuisine_names = [name.strip() for name in cuisine_names if name.strip()]
            else:
                cuisine_names = None
            # Combine address components for geocoding
            full_address = f"{new_business.address}, {new_business.city}, {new_business.state} {new_business.zip_code}"

            try:
                # Geocode the address
                geocode_result = gmaps.geocode(full_address)

                if geocode_result:
                    location = geocode_result[0]['geometry']['location']
                    formatted_address = geocode_result[0]['formatted_address']
                    coordinates = f"{location['lat']},{location['lng']}"
                    timezone_result = gmaps.timezone(
                        location=(location['lat'], location['lng']),
                        timestamp=datetime.now().timestamp()
                    )
                    if timezone_result:
                        new_business.timezone = timezone_result['timeZoneId']
                    
                    if Business.verified_business_exists(formatted_address):
                        raise ValidationError("A verified business already exists at this address.")
                    
                    new_business.address = formatted_address

                    new_business.save()
                    # Create home page
                    home_page = SubPage.objects.create(
                        business=new_business,
                        page_type='home',
                        title=f"{new_business.business_name} Home",
                        is_published=True,
                        hero_heading=f"Welcome to {new_business.business_name}",
                        hero_subheading="We're excited to serve you!",
                        show_hero_heading=True,
                        show_hero_subheading=True
                    )
                    # Add cuisines to the menu if specified
                    if cuisine_names:
                        menu_page = SubPage.objects.create(
                            business=new_business,
                            page_type='menu',
                            title=f"{new_business.business_name} Menu",
                            is_published=True,
                            hero_heading="Our Menu",
                            hero_subheading="Explore our delicious offerings",
                            show_hero_heading=True,
                            show_hero_subheading=True
                        )

                        # Create menu and link it to the menu page
                        default_menu = Menu.objects.create(
                            business=new_business,
                            name=f"{new_business.business_name} Menu",
                            description="Our main menu",
                            subpage=menu_page,  # Link menu to the menu page
                            display_style='grid'
                        )
                        for cuisine_name in cuisine_names:
                            cuisine_category, created = CuisineCategory.objects.get_or_create(
                                cuisine=cuisine_name
                            )
                            default_menu.cuisine.add(cuisine_category)

                    messages.success(request, 'business created successfully!')
                    return redirect(reverse('business_home', kwargs={'business_subdirectory': new_business.subdirectory}))
                else:
                    messages.error(request, 'Unable to validate the address. Please check and try again.')
            except Exception as e:
                logger.error(f"Error creating Business: {str(e)}", exc_info=True)
                messages.error(request, f'An error occurred: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
            logger.error(f"Form validation errors: {form.errors}")

        context = {
            "create": form,
            "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY
        }
        return render(request, "create.html", context)