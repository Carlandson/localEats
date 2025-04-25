def menu(request, business_subdirectory):
    business = get_object_or_404(Business, subdirectory=business_subdirectory)
    
    # First get the menu subpage
    menu_subpage = get_object_or_404(SubPage, business=business, page_type='menu')
    course_options = [
        'Appetizers',
        'Lunch',
        'Entrees',
        'Main Courses',
        'Soup and Salad',
        'Salads',
        'Desserts',
        'Drinks',
        'Specials',
        'Dinner',
        'Breakfast',
        'Brunch',
        'Kids Menu',
        'Beverages',
        'Vegan',
        'Gluten Free',
        'Dairy Free',
        'Nut Free',
        'Halal',
        'Kosher'
    ]
    try:
        # Then get the menu associated with this subpage
        menu = Menu.objects.get(subpage=menu_subpage)
        courses = Course.objects.filter(menu=menu).prefetch_related('side_options').order_by('order')
        dishes = Dish.objects.filter(menu=menu)
        existing_course_names = list(courses.values_list('name', flat=True))
        available_course_options = [option for option in course_options 
                            if option not in existing_course_names]
    except Menu.DoesNotExist:
        # If no menu exists yet, create one
        menu = Menu.objects.create(
            business=business,
            name=f"{business.business_name} Menu",
            subpage=menu_subpage
        )
        courses = []
        dishes = []
        existing_course_names = []
        available_course_options = course_options
    
    context = {
        "business_subdirectory": business_subdirectory,
        "business_details": business,
        "courses": courses,
        "dishes": dishes,
        "course_options": available_course_options,
        "existing_courses": existing_course_names,
        "owner": request.user == business.owner,
        "is_verified": business.is_verified,
        "menu": menu,
        "is_edit_page": True,
        "is_owner": request.user == business.owner
    }

    if request.method != "GET":
        return JsonResponse({"error": "GET request required."}, status=400)

    if not business.is_verified and request.user != business.owner:
        return render(request, "business_under_construction.html", context)
        
    elif request.user != business.owner:
        return render(request, "visitor_pages/menu.html", context)
    
    else:
        return render(request, "subpages/menu.html", context)
    

@login_required
def new_dish(request, business_name):
    if request.method == "GET":
        return render(request, "newdish.html", {"new_dish" : DishSubmit()})
    if request.method == "POST":
        print("post request", request.POST)
        form = Dish(request.POST)
        user = request.user
        # image = Image(
        #     image=file,
        #     uploaded_by=request.user,
        #     content_type=ContentType.objects.get_for_model(gallery_page),
        #     object_id=gallery_page.id,
        #     alt_text=file.name
        # )
        # image.full_clean()  # This will validate the image
        # image.save()
        if form.is_valid():
            name = form.cleaned_data["name"]
            price = form.cleaned_data["price"]
            recipe_owner = business_name
            image_url = form.cleaned_data["image_url"]
            course = form.cleaned_data["course"]
            description = form.cleaned_data["description"]
        else:
            print(form.errors)
            return render(request, "newdish.html", {"new_dish" : DishSubmit()})
        new = Dish(name=name, price=price, image_url=image_url, course=course, description=description, recipe_owner=recipe_owner)
        new.save()
        messages.add_message(request, messages.INFO, f"'{name}' successfully added to menu")
        return HttpResponseRedirect(reverse('business_subdirectory', kwargs={"business_name": business_name}))


@ensure_csrf_cookie
def add_course(request, business_subdirectory):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    business = get_object_or_404(Business, subdirectory=business_subdirectory)
    
    # Check if user is owner
    if request.user != business.owner:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    try:
        data = json.loads(request.body)
        course_name = data.get('course_name')
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if not course_name:
        return JsonResponse({"error": "Course name is required"}, status=400)

    # First try to get menu through subpage
    try:
        menu_subpage = SubPage.objects.get(business=business, page_type='menu')
        menu = Menu.objects.get(subpage=menu_subpage)
    except (SubPage.DoesNotExist, Menu.DoesNotExist):
        # If that fails, try to get menu directly through business
        menu = get_object_or_404(Menu, business=business)

        # Check for existing course with the same name (case-insensitive)
    if Course.objects.filter(menu=menu, name__iexact=course_name).exists():
        return JsonResponse({
            "error": "A course with this name already exists"
        }, status=400)
    
    # Create new course
    highest_order = Course.objects.filter(menu=menu).aggregate(Max('order'))['order__max'] or 0
    course = Course.objects.create(
        menu=menu,
        name=course_name,
        order=highest_order + 1
    )

    return JsonResponse({
        "message": "Course added successfully",
        "course_id": course.id
    })

@login_required
def add_dish(request, business_subdirectory):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    try:
        data = json.loads(request.body)
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        
        # Check if user is owner
        if request.user != business.owner:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        # Get the menu
        menu_subpage = get_object_or_404(SubPage, business=business, page_type='menu')
        menu = get_object_or_404(Menu, subpage=menu_subpage)

        # Get or create the course
        course_name = data.get("course", "")
        course = Course.objects.get(menu=menu, name=course_name)

        dish_name = data.get("name", "").strip()
        if Dish.objects.filter(course=course, name__iexact=dish_name).exists():
            return JsonResponse({
                "error": f"A dish with the name '{dish_name}' already exists in the {course_name} course."
            }, status=400)
        
        image_data = data.get('image')
        image = None
        if image_data and 'base64,' in image_data:
            # Split the base64 string
            format, imgstr = image_data.split('base64,')
            # Get the file extension
            ext = format.split('/')[-1].split(';')[0]
            # Generate filename
            filename = f"{business.subdirectory}_{data.get('name')}_{uuid.uuid4().hex[:6]}.{ext}"
            
            # Create ContentFile from base64 data
            image = ContentFile(base64.b64decode(imgstr), name=filename)

        # Create new dish
        new_dish = Dish.objects.create(
            menu=menu,
            name=data.get("name", ""),
            description=data.get("description", ""),
            price=data.get("price", ""),
            image=image,
            course=course
        )

        return JsonResponse({
            "message": "Dish added successfully",
            "dish_id": new_dish.id,
            "image_url": new_dish.image.url if new_dish.image else ""
        }, status=201)

    except Course.DoesNotExist:
        return JsonResponse({
            "error": f"Course '{course_name}' not found"
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            "error": "Invalid JSON"
        }, status=400)
    except IntegrityError:
        return JsonResponse({
            "error": "A dish with this name already exists in your menu."
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "error": str(e)
        }, status=400)
    
@ensure_csrf_cookie
@login_required
def edit_dish(request, business_subdirectory, dishid):
    try:
        dish = Dish.objects.get(id=dishid)
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        
        # Verify owner
        if request.user != business.owner:
            return JsonResponse({"error": "Unauthorized"}, status=403)
            
        data = json.loads(request.body)
        new_name = data.get('name', '').strip()

        # Check if new name already exists in this course (excluding current dish)
        if new_name.lower() != dish.name.lower() and \
           Dish.objects.filter(course=dish.course, name__iexact=new_name).exists():
            return JsonResponse({
                "error": f"A dish with the name '{new_name}' already exists in the {dish.course.name} course."
            }, status=400)
                
        # Update dish fields
        dish.name = data.get('name', dish.name)
        dish.price = data.get('price', dish.price)
        dish.description = data.get('description', dish.description)

        # Handle image data
        image_data = data.get('image')
        if image_data and 'base64,' in image_data:
            # Split the base64 string
            format, imgstr = image_data.split('base64,')
            # Get the file extension
            ext = format.split('/')[-1].split(';')[0]
            # Generate filename
            filename = f"{business.subdirectory}_{dish.name}_{uuid.uuid4().hex[:6]}.{ext}"
            
            # Create ContentFile from base64 data
            image = ContentFile(base64.b64decode(imgstr), name=filename)
            dish.image = image

        dish.save()
        
        return JsonResponse({
            "message": "Dish updated successfully",
            "dish_id": dishid,
            "image_url": dish.image.url if dish.image else ""
        }, status=200)
        
    except Dish.DoesNotExist:
        return JsonResponse({"error": "Dish does not exist."}, status=404)
    except IntegrityError:
        return JsonResponse({
            "error": "A dish with this name already exists in your menu."
        }, status=400)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    
@csrf_exempt
@login_required
def delete_dish(request, business_subdirectory, dishid):
    try:
        dish = Dish.objects.get(id=dishid)
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        
        # Verify owner
        if request.user != business.owner:
            return JsonResponse({"error": "Unauthorized"}, status=403)
        
        # Add owner verification
        if request.user != dish.menu.subpage.business.owner:
            return JsonResponse({"error": "Unauthorized"}, status=403)
            
        if request.method != "DELETE":  # Changed to DELETE method
            return JsonResponse({"error": "DELETE request required."}, status=400)
            
        dish.delete()
        return JsonResponse({
            "message": "Dish deleted successfully",
            "dish_id": dishid
        }, status=200)
        
    except Dish.DoesNotExist:
        return JsonResponse({"error": "Dish does not exist."}, status=404)
    
@csrf_exempt
@login_required
def delete_course(request, business_subdirectory, courseid):
    if request.method != "DELETE":
        return JsonResponse({"error": "DELETE request required."}, status=400)
    
    try:
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        
        # Check if user is owner
        if request.user != business.owner:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        course = get_object_or_404(Course, id=courseid)
        
        # Verify the course belongs to this Business's menu
        if course.menu.subpage.business != business:
            return JsonResponse({"error": "Course not found."}, status=404)

        # Delete the course (this will cascade delete all associated dishes)
        course.delete()

        return JsonResponse({
            "message": "Course and all associated dishes deleted successfully"
        }, status=200)

    except Exception as e:
        return JsonResponse({
            "error": str(e)
        }, status=400)
    
def get_dish(request, dish_id):
    try:
        dish_obj = Dish.objects.get(id=dish_id)
        return JsonResponse(dish_obj.serialize())
    except Dish.DoesNotExist:
        return JsonResponse({"error": "Dish not found"}, status=404)
    
def get_cuisine_categories(request):
    categories = CuisineCategory.objects.all()
    return JsonResponse([category.serialize() for category in categories], safe=False)

def update_course_description(request, business_subdirectory, course_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    try:
        course = Course.objects.get(id=course_id)
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        
        # Verify owner
        if request.user != business.owner:
            return JsonResponse({"error": "Unauthorized"}, status=403)
            
        data = json.loads(request.body)
        course.description = data.get('description', '').strip()
        course.save()
        
        return JsonResponse({
            "message": "Course description updated successfully",
            "course_id": course_id
        }, status=200)
        
    except Course.DoesNotExist:
        return JsonResponse({"error": "Course does not exist."}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    
def update_course_note(request, business_subdirectory, course_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    try:
        course = Course.objects.get(id=course_id)
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        
        # Verify owner
        if request.user != business.owner:
            return JsonResponse({"error": "Unauthorized"}, status=403)
            
        data = json.loads(request.body)
        course.note = data.get('note', '').strip()
        course.save()
        
        return JsonResponse({
            "message": "Course note updated successfully",
            "course_id": course_id
        }, status=200)
        
    except Course.DoesNotExist:
        return JsonResponse({"error": "Course does not exist."}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    
@require_http_methods(["GET", "POST", "DELETE"])
def side_options(request, business_subdirectory, id=None):
    try:
        business = get_object_or_404(Business, subdirectory=business_subdirectory)
        if request.user != business.owner:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        if request.method == "GET":
            # If no id is provided or id is 'all', return all side options for the business
            if id is None or id == 'all':
                side_options = SideOption.objects.filter(
                    course__menu__business=business
                ).select_related('course', 'course__menu')  # For efficiency
                
                return JsonResponse([{
                    'id': side.id,
                    'name': side.name,
                    'description': side.description,
                    'price': str(side.price),
                    'is_premium': side.is_premium,
                    'course_id': side.course.id,
                    'course_name': side.course.name,
                    'menu_name': side.course.menu.name
                } for side in side_options], safe=False)

            try:
                # Try to get a specific side option
                side = SideOption.objects.get(
                    id=id,
                    course__menu__business=business  # Ensure it belongs to this business
                )
                return JsonResponse({
                    'id': side.id,
                    'name': side.name,
                    'description': side.description,
                    'price': str(side.price),
                    'is_premium': side.is_premium,
                    'course_id': side.course.id
                })
            except SideOption.DoesNotExist:
                # If not found, assume id is course_id and return all side options for that course
                course = get_object_or_404(
                    Course, 
                    id=id,
                    menu__business=business  # Ensure it belongs to this business
                )
                side_options = course.side_options.all()
                return JsonResponse([{
                    'id': side.id,
                    'name': side.name,
                    'description': side.description,
                    'price': str(side.price),
                    'is_premium': side.is_premium
                } for side in side_options], safe=False)

        # POST request handling
        elif request.method == "POST":
            data = json.loads(request.body)
            try:
                # Try to get existing side option (update case)
                # Make sure the side option belongs to this business
                side = SideOption.objects.get(
                    id=id,
                    course__menu__business=business  # Add this filter
                )
                side.name = data.get('name', side.name)
                side.description = data.get('description', side.description)
                side.is_premium = data.get('is_premium', side.is_premium)
                side.price = data.get('price', side.price)
                side.save()
                course = side.course
            except SideOption.DoesNotExist:
                # If not found, create new side option
                # Make sure the course belongs to this business
                course = get_object_or_404(
                    Course, 
                    id=id,
                    menu__business=business  # Add this filter
                )
                side = SideOption.objects.create(
                    course=course,
                    name=data.get('name'),
                    description=data.get('description', ''),
                    is_premium=data.get('is_premium', False),
                    price=data.get('price', 0)
                )

            # Get all side options for the course and return them
            side_options = course.side_options.all()
            return JsonResponse({
                'message': 'Side option saved successfully',
                'course_id': course.id,
                'side_options': [{
                    'id': side.id,
                    'name': side.name,
                    'description': side.description,
                    'price': str(side.price),
                    'is_premium': side.is_premium,
                    'course_id': course.id
                } for side in side_options]
            })

        # DELETE request handling
        elif request.method == "DELETE":
            side = get_object_or_404(SideOption, id=id)
            course_id = side.course.id
            side.delete()
            return JsonResponse({
                'message': 'Side option deleted successfully',
                'course_id': course_id
            })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)