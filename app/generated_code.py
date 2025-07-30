def execute_command(image_path, image):
    image_patch = ImagePatch(image)
    
    # Find apples and strawberries in the image
    patches_dict = image_patch.find("apple. strawberry")
    apple_patches = patches_dict["apple"]
    strawberry_patches = patches_dict["strawberry"]
    
    # Delete overlaps
    apple_patches, strawberry_patches = delete_overlaps(apple_patches, strawberry_patches)
    
    # Count the number of apples
    num_apples = len(apple_patches)
    print(f"Number of apples is {num_apples}")
    
    # Count the number of strawberries
    num_strawberries = len(strawberry_patches)
    print(f"Number of strawberries is {num_strawberries}")
    
    # Verify if the counts match the conditions
    anomaly_score = 0
    if num_apples != 2:
        print(f"Expected 2 apples, but found {num_apples}")
        anomaly_score += 1
    
    if num_strawberries != 6:
        print(f"Expected 6 strawberries, but found {num_strawberries}")
        anomaly_score += 1
    
    return formatting_answer(anomaly_score)
