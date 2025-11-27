"""Text Layout Collision Detection and Resolution"""

def bbox_intersects(bbox1, bbox2):
    """Check if two bounding boxes intersect
    
    Args:
        bbox1, bbox2: [x1, y1, x2, y2]
    
    Returns:
        bool: True if boxes intersect
    """
    return not (bbox1[2] <= bbox2[0] or bbox1[0] >= bbox2[2] or 
                bbox1[3] <= bbox2[1] or bbox1[1] >= bbox2[3])

def calculate_text_bbox(text_bbox, lines, font, draw):
    """Calculate actual text bounding box after wrapping
    
    Args:
        text_bbox: [x1, y1, x2, y2] original bbox
        lines: list of text lines
        font: PIL font
        draw: PIL ImageDraw
    
    Returns:
        [x1, y1, x2, y2] actual text bbox
    """
    if not lines:
        return text_bbox
    
    x1, y1 = text_bbox[0], text_bbox[1]
    max_width = 0
    total_height = 0
    
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        line_height = bbox[3] - bbox[1]
        max_width = max(max_width, line_width)
        total_height += line_height + 5
    
    return [x1, y1, x1 + max_width, y1 + total_height]

def is_inside_image(bbox, image_bbox):
    """Check if bbox center is inside image region"""
    if not image_bbox:
        return False
    center_y = (bbox[1] + bbox[3]) / 2
    return image_bbox[1] <= center_y <= image_bbox[3]

def resolve_text_positions(text_elements, poster_size, image_bbox):
    """Resolve text position collisions
    
    Rules:
    1. Text inside image stays inside, text outside stays outside
    2. Move minimal distance, process sequentially
    3. Don't move element if it would cause new collision
    4. Larger gap between title and captions (30px)
    5. Move text away from image border if on boundary
    
    Args:
        text_elements: list of dicts with 'bbox', 'name', 'priority'
        poster_size: (width, height)
        image_bbox: [x1, y1, x2, y2] or None
    
    Returns:
        list of adjusted text_elements with updated 'bbox'
    """
    import random
    poster_w, poster_h = poster_size
    adjusted = []
    
    # Track original region and sort by Y position
    for elem in text_elements:
        bbox = elem['bbox'][:]
        adjusted.append({
            'bbox': bbox,
            'name': elem['name'],
            'priority': elem.get('priority', 0),
            'inside_image': is_inside_image(bbox, image_bbox),
            'original_y': bbox[1]
        })
    
    adjusted.sort(key=lambda x: x['original_y'])
    
    # Resolve collisions with multiple passes
    max_passes = 5
    for pass_num in range(max_passes):
        collision_found = False
        
        for i in range(len(adjusted) - 1):
            upper = adjusted[i]
            lower = adjusted[i + 1]
            
            if bbox_intersects(upper['bbox'], lower['bbox']):
                collision_found = True
                print(f"    [Layout] Collision: {upper['name']} vs {lower['name']}")
                
                gap = 30 if 'title' in upper['name'].lower() or 'title' in lower['name'].lower() else 5
                move_dist = upper['bbox'][3] - lower['bbox'][1] + gap
                
                new_lower = [lower['bbox'][0], lower['bbox'][1] + move_dist,
                            lower['bbox'][2], lower['bbox'][3] + move_dist]
                
                lower_ok = (new_lower[3] <= poster_h)
                if lower['inside_image'] and image_bbox:
                    lower_ok = lower_ok and is_inside_image(new_lower, image_bbox)
                elif not lower['inside_image'] and image_bbox:
                    lower_ok = lower_ok and not bbox_intersects(new_lower, image_bbox)
                
                if lower_ok:
                    lower['bbox'] = new_lower
                    print(f"    [Layout] Moved {lower['name']} down {move_dist}px")
                else:
                    new_upper = [upper['bbox'][0], upper['bbox'][1] - move_dist,
                                upper['bbox'][2], upper['bbox'][3] - move_dist]
                    
                    margin = 50
                    upper_ok = (new_upper[1] >= margin)
                    if upper['inside_image'] and image_bbox:
                        upper_ok = upper_ok and is_inside_image(new_upper, image_bbox)
                    elif not upper['inside_image'] and image_bbox:
                        upper_ok = upper_ok and not bbox_intersects(new_upper, image_bbox)
                    
                    if upper_ok:
                        upper['bbox'] = new_upper
                        print(f"    [Layout] Moved {upper['name']} up {move_dist}px")
                    else:
                        print(f"    [Layout] WARNING: Cannot resolve {upper['name']} vs {lower['name']}")
        
        if not collision_found:
            print(f"    [Layout] ✓ No collisions after {pass_num + 1} pass(es)")
            break
    
    # Clip text to poster boundaries with 50px margin
    margin = 50
    for elem in adjusted:
        bbox = elem['bbox']
        
        # Check poster boundaries with margin
        if bbox[2] > poster_w - margin:
            shift = bbox[2] - (poster_w - margin)
            bbox[0] -= shift
            bbox[2] -= shift
            print(f"    [Layout] {elem['name']} out of right border, moved left {shift}px")
        
        if bbox[0] < margin:
            shift = margin - bbox[0]
            bbox[0] += shift
            bbox[2] += shift
            print(f"    [Layout] {elem['name']} out of left border, moved right {shift}px")
        
        if bbox[3] > poster_h - margin:
            shift = bbox[3] - (poster_h - margin)
            bbox[1] -= shift
            bbox[3] -= shift
            print(f"    [Layout] {elem['name']} out of bottom border, moved up {shift}px")
        
        if bbox[1] < margin:
            shift = margin - bbox[1]
            bbox[1] += shift
            bbox[3] += shift
            print(f"    [Layout] {elem['name']} out of top border, moved down {shift}px")
    
    # Move text away from image border if on boundary
    if image_bbox:
        border_threshold = 20
        for elem in adjusted:
            bbox = elem['bbox']
            # Check if text is near image border
            near_top = abs(bbox[1] - image_bbox[1]) < border_threshold
            near_bottom = abs(bbox[3] - image_bbox[3]) < border_threshold
            
            if near_top or near_bottom:
                print(f"    [Layout] {elem['name']} near image border")
                
                if near_top:
                    # Move up into background
                    shift = border_threshold + 10
                    new_bbox = [bbox[0], bbox[1] - shift, bbox[2], bbox[3] - shift]
                    if new_bbox[1] >= margin:
                        elem['bbox'] = new_bbox
                        print(f"    [Layout] Moved {elem['name']} up {shift}px away from border")
                
                elif near_bottom:
                    # Randomly choose: move down or move up
                    if random.choice([True, False]):
                        # Move down into background
                        shift = border_threshold + 10
                        new_bbox = [bbox[0], bbox[1] + shift, bbox[2], bbox[3] + shift]
                        if new_bbox[3] <= poster_h - margin:
                            elem['bbox'] = new_bbox
                            print(f"    [Layout] Moved {elem['name']} down {shift}px away from border")
                    else:
                        # Move up into image
                        shift = border_threshold + 10
                        new_bbox = [bbox[0], bbox[1] - shift, bbox[2], bbox[3] - shift]
                        if new_bbox[1] >= image_bbox[1]:
                            elem['bbox'] = new_bbox
                            print(f"    [Layout] Moved {elem['name']} up {shift}px away from border")
    
    print(f"    [Layout] ✓ Layout adjustment complete")
    return adjusted
