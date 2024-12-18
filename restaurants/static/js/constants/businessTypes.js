// Business Categories - Main classification level
export const BUSINESS_CATEGORIES = {
    FOOD_SERVICE: 'Food & Beverage',
    RETAIL: 'Retail',
    PROFESSIONAL_SERVICES: 'Professional Services',
    HEALTH_WELLNESS: 'Health & Wellness',
    ENTERTAINMENT: 'Entertainment & Recreation',
    AUTOMOTIVE: 'Automotive',
    EDUCATION: 'Education & Training',
    PERSONAL_SERVICES: 'Personal Services',
    CONSTRUCTION: 'Construction & Home Services',
    TECHNOLOGY: 'Technology',
    MANUFACTURING: 'Manufacturing',
    AGRICULTURE: 'Agriculture',
    TRANSPORTATION: 'Transportation & Logistics',
    HOSPITALITY: 'Hospitality & Tourism',
    FINANCIAL: 'Financial Services',
    OTHER: 'Other'
};

// Detailed business types by category
export const BUSINESS_TYPES = {
    [BUSINESS_CATEGORIES.FOOD_SERVICE]: [
        { id: 'restaurant_full', label: 'Full-Service Restaurant' },
        { id: 'restaurant_fast', label: 'Fast-Food Restaurant' },
        { id: 'restaurant_casual', label: 'Casual Dining' },
        { id: 'cafe', label: 'Café' },
        { id: 'bar', label: 'Bar/Pub' },
        { id: 'nightclub', label: 'Nightclub' },
        { id: 'food_truck', label: 'Food Truck' },
        { id: 'bakery', label: 'Bakery' },
        { id: 'deli', label: 'Delicatessen' },
        { id: 'catering', label: 'Catering Service' },
        { id: 'coffee_shop', label: 'Coffee Shop' },
        { id: 'ice_cream', label: 'Ice Cream Shop' },
        { id: 'juice_bar', label: 'Juice/Smoothie Bar' },
        { id: 'brewery', label: 'Brewery' },
        { id: 'winery', label: 'Winery' },
        { id: 'distillery', label: 'Distillery' },
        { id: 'food_service_other', label: 'Other Food Service' }
    ],

    [BUSINESS_CATEGORIES.RETAIL]: [
        { id: 'clothing', label: 'Clothing Store' },
        { id: 'grocery', label: 'Grocery Store' },
        { id: 'supermarket', label: 'Supermarket' },
        { id: 'convenience', label: 'Convenience Store' },
        { id: 'department_store', label: 'Department Store' },
        { id: 'electronics', label: 'Electronics Store' },
        { id: 'furniture', label: 'Furniture Store' },
        { id: 'hardware', label: 'Hardware Store' },
        { id: 'bookstore', label: 'Bookstore' },
        { id: 'jewelry', label: 'Jewelry Store' },
        { id: 'sporting_goods', label: 'Sporting Goods' },
        { id: 'toy_store', label: 'Toy Store' },
        { id: 'pet_store', label: 'Pet Store' },
        { id: 'pharmacy', label: 'Pharmacy' },
        { id: 'retail_other', label: 'Other Retail' }
    ],

    [BUSINESS_CATEGORIES.PROFESSIONAL_SERVICES]: [
        { id: 'law_firm', label: 'Law Firm' },
        { id: 'accounting', label: 'Accounting Firm' },
        { id: 'consulting', label: 'Consulting' },
        { id: 'marketing', label: 'Marketing Agency' },
        { id: 'advertising', label: 'Advertising Agency' },
        { id: 'real_estate', label: 'Real Estate Agency' },
        { id: 'insurance', label: 'Insurance Agency' },
        { id: 'architecture', label: 'Architecture Firm' },
        { id: 'engineering', label: 'Engineering Firm' },
        { id: 'web_design', label: 'Web Design/Development' },
        { id: 'professional_other', label: 'Other Professional Service' }
    ],

    [BUSINESS_CATEGORIES.HEALTH_WELLNESS]: [
        { id: 'medical_clinic', label: 'Medical Clinic' },
        { id: 'dental', label: 'Dental Office' },
        { id: 'chiropractic', label: 'Chiropractic Office' },
        { id: 'physical_therapy', label: 'Physical Therapy' },
        { id: 'mental_health', label: 'Mental Health Practice' },
        { id: 'gym', label: 'Gym/Fitness Center' },
        { id: 'yoga_studio', label: 'Yoga Studio' },
        { id: 'spa', label: 'Spa' },
        { id: 'massage', label: 'Massage Therapy' },
        { id: 'nutrition', label: 'Nutrition Services' },
        { id: 'wellness_other', label: 'Other Health & Wellness' }
    ],

    [BUSINESS_CATEGORIES.ENTERTAINMENT]: [
        { id: 'theater', label: 'Theater' },
        { id: 'cinema', label: 'Cinema' },
        { id: 'museum', label: 'Museum' },
        { id: 'art_gallery', label: 'Art Gallery' },
        { id: 'arcade', label: 'Arcade' },
        { id: 'bowling', label: 'Bowling Alley' },
        { id: 'sports_venue', label: 'Sports Venue' },
        { id: 'amusement', label: 'Amusement Park' },
        { id: 'recreation_center', label: 'Recreation Center' },
        { id: 'entertainment_other', label: 'Other Entertainment' }
    ],

    [BUSINESS_CATEGORIES.AUTOMOTIVE]: [
        { id: 'auto_dealer', label: 'Car Dealership' },
        { id: 'auto_repair', label: 'Auto Repair Shop' },
        { id: 'auto_body', label: 'Auto Body Shop' },
        { id: 'auto_parts', label: 'Auto Parts Store' },
        { id: 'car_wash', label: 'Car Wash' },
        { id: 'gas_station', label: 'Gas Station' },
        { id: 'tire_shop', label: 'Tire Shop' },
        { id: 'automotive_other', label: 'Other Automotive' }
    ],

    [BUSINESS_CATEGORIES.EDUCATION]: [
        { id: 'school', label: 'School' },
        { id: 'college', label: 'College/University' },
        { id: 'trade_school', label: 'Trade School' },
        { id: 'tutoring', label: 'Tutoring Service' },
        { id: 'language_school', label: 'Language School' },
        { id: 'music_school', label: 'Music School' },
        { id: 'art_school', label: 'Art School' },
        { id: 'driving_school', label: 'Driving School' },
        { id: 'education_other', label: 'Other Educational Service' }
    ],

    [BUSINESS_CATEGORIES.PERSONAL_SERVICES]: [
        { id: 'salon', label: 'Hair Salon' },
        { id: 'barber', label: 'Barber Shop' },
        { id: 'nail_salon', label: 'Nail Salon' },
        { id: 'beauty_salon', label: 'Beauty Salon' },
        { id: 'tailor', label: 'Tailor/Alterations' },
        { id: 'dry_cleaning', label: 'Dry Cleaning' },
        { id: 'laundromat', label: 'Laundromat' },
        { id: 'pet_grooming', label: 'Pet Grooming' },
        { id: 'personal_other', label: 'Other Personal Service' }
    ],

    [BUSINESS_CATEGORIES.HOSPITALITY]: [
        { id: 'hotel', label: 'Hotel' },
        { id: 'motel', label: 'Motel' },
        { id: 'bed_breakfast', label: 'Bed & Breakfast' },
        { id: 'resort', label: 'Resort' },
        { id: 'vacation_rental', label: 'Vacation Rental' },
        { id: 'travel_agency', label: 'Travel Agency' },
        { id: 'tour_operator', label: 'Tour Operator' },
        { id: 'hospitality_other', label: 'Other Hospitality' }
    ],

    [BUSINESS_CATEGORIES.OTHER]: [
        { id: 'custom', label: 'Custom Business Type' }
    ]
};

// Metadata about business types
export const BUSINESS_TYPE_METADATA = {
    requiresCuisineSelection: [
        'restaurant_full',
        'restaurant_fast',
        'restaurant_casual',
        'food_truck',
        'catering'
    ],
    requiresSpecialty: [
        'law_firm',
        'medical_clinic',
        'consulting'
    ]
};

// Validation rules
export const BUSINESS_TYPE_VALIDATION = {
    maxCustomLength: 50,
    restrictedWords: ['forbidden', 'inappropriate'],
    requiredFields: {
        'restaurant_full': ['cuisine', 'seating_capacity'],
        'hotel': ['room_count', 'star_rating']
    }
};

// Helper functions
export const businessTypeHelpers = {
    requiresCuisine(businessType) {
        return BUSINESS_TYPE_METADATA.requiresCuisineSelection.includes(businessType);
    },

    getRequiredFields(businessType) {
        return BUSINESS_TYPE_VALIDATION.requiredFields[businessType] || [];
    },

    isValidCustomType(customType) {
        if (!customType || customType.length > BUSINESS_TYPE_VALIDATION.maxCustomLength) {
            return false;
        }
        return !BUSINESS_TYPE_VALIDATION.restrictedWords.some(word => 
            customType.toLowerCase().includes(word)
        );
    }
};