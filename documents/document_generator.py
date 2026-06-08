def generate_document(row, category):
    if category == "place":
        return f"""
        Place Name: {row.get('name', 'Unknown')}
        Location: {row.get('location', 'Unknown')}
        Description: {row.get('description', 'No description available')}
        History: {row.get('history', 'No historical information')}
        Best Time to Visit: {row.get('best_time', 'Year round')}
        Entry Fee: {row.get('entry_fee', 'Contact for pricing')}
        """
    
    elif category == "hotel":
        return f"""
        Hotel Name: {row.get('name', 'Unknown')}
        Location: {row.get('city', 'Unknown')}
        Rating: {row.get('rating', 'Not rated')}
        Price per Night: {row.get('price_per_night', 'Contact for pricing')}
        Amenities: {row.get('amenities', 'Standard amenities')}
        Description: {row.get('description', 'Comfortable accommodation')}
        """
    
    elif category == "restaurant":
        return f"""
        Restaurant Name: {row.get('name', 'Unknown')}
        Location: {row.get('city', 'Unknown')}
        Cuisine: {row.get('cuisine_type', 'Local & International')}
        Price Range: {row.get('price_range', 'Moderate')}
        Must Try Dishes: {row.get('signature_dishes', 'Ask staff for recommendations')}
        """
    
    elif category == "guide":
        return f"""
        Guide Name: {row.get('name', 'Unknown')}
        Languages: {row.get('languages', 'English')}
        Experience: {row.get('experience_years', 0)} years
        Specialization: {row.get('specialization', 'General tourism')}
        Contact: {row.get('contact_info', 'Available upon request')}
        """
    
    elif category == "package":
        return f"""
        Tour Package: {row.get('name', 'Unknown')}
        Duration: {row.get('duration_days', 0)} days
        Destinations: {row.get('destinations', 'Various locations')}
        Price: {row.get('price', 'Contact for pricing')}
        Includes: {row.get('inclusions', 'Accommodation, transport, guides')}
        Description: {row.get('description', 'An amazing tour experience')}
        """
    
    return f"{category.title()}: {row}"

def generate_all_documents(data):
    documents = []
    metadatas = []
    
    for category, rows in data.items():
        for row in rows:
            doc = generate_document(row, category[:-1] if category.endswith('s') else category)
            documents.append(doc)
            metadatas.append({
                "category": category,
                "id": str(row.get('id', 'unknown')),
                "name": row.get('name', 'Unknown')
            })
    
    return documents, metadatas