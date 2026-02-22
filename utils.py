import re
import cv2
from ultralytics import YOLO
import easyocr
import numpy as np
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

model = YOLO('best.pt')

reader = easyocr.Reader(['en', 'sw'], gpu=False)

def extract_id_info(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return None
    
    results = model(img, conf=0.4)
    
    data = {
        "student_name": None,
        "reg_number": None,
        "department": None,
        "phone_number": None
    }

    name_x, name_y = None, None
    course_x, course_y = None, None
    
    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        class_name = model.names[cls_id]
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        
        if class_name == 'name':
            name_x = (x1 + x2) / 2
            name_y = (y1 + y2) / 2
        elif class_name == 'course':
            course_x = (x1 + x2) / 2
            course_y = (y1 + y2) / 2

    for result in results:
        for box in result.boxes:
            cls_id = int(box.cls[0])
            class_name = model.names[cls_id]
            
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            h, w, _ = img.shape
            
            box_w = x2 - x1
            box_h = y2 - y1
            
            if box_w > box_h:
                pad_x, pad_y = 25, 5
            else:
                pad_x, pad_y = 5, 25
                
            y1_pad = max(0, y1 - pad_y)
            y2_pad = min(h, y2 + pad_y)
            x1_pad = max(0, x1 - pad_x)
            x2_pad = min(w, x2 + pad_x)
            
            crop = img[y1_pad:y2_pad, x1_pad:x2_pad]
            
            if name_x is not None and course_x is not None:
                if box_w > box_h:  # Image is Horizontal
                    # Image is upside down
                    if name_y > course_y:
                        crop = cv2.rotate(crop, cv2.ROTATE_180)
                else:  # Image is Vertical
                    # Image is rotated 90 degrees Clockwise
                    if name_x < course_x:
                        crop = cv2.rotate(crop, cv2.ROTATE_90_CLOCKWISE)
                    # Image is rotated 90 degrees Counter-Clockwise
                    else:
                        crop = cv2.rotate(crop, cv2.ROTATE_90_COUNTERCLOCKWISE)
            
            # Upscale and Grayscale
            crop = cv2.resize(crop, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            gray_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            
            ocr_result = reader.readtext(gray_crop, detail=0)
            
            if ocr_result:
                cleaned_text = " ".join(ocr_result).strip()
                
                if class_name == 'name':
                    data['student_name'] = cleaned_text
                    
                elif class_name == 'course':
                    # Fix the '0' instead of '.' OCR mistake
                    data['department'] = cleaned_text.replace("0", ".").replace(" .", ".")
                    
                elif class_name in ['reg no', 'phone number']:
                    # Remove whitespaces
                    temp_text = cleaned_text.replace(" ", "")
                    
                    # REG NO. CHECK
                    reg_pattern = r'[A-Za-z0-9]{2,5}[/l\-\\]\d{3,4}[/l\-\\]\d{4}'
                    reg_match = re.search(reg_pattern, temp_text)
                    
                    if reg_match:
                        clean_reg = reg_match.group(0)
                        formatted_reg = re.sub(r'[/l\-\\]', '/', clean_reg).upper()
                        
                        data['reg_number'] = formatted_reg
                        continue
                    
                    # PHONE NUMBER CHECK
                    phone_pattern = r'(?:\+254|0)?[17]\d{8}'
                    phone_match = re.search(phone_pattern, temp_text)
                    
                    if phone_match and not re.search(r'[/l\-\\]', temp_text):
                        raw_phone = phone_match.group(0)
                        
                        if len(raw_phone) == 9 and raw_phone.startswith(('7', '1')):
                            raw_phone = "0" + raw_phone  
                        elif raw_phone.startswith('+254'):
                            raw_phone = "0" + raw_phone[4:]
                            
                        data['phone_number'] = raw_phone
                        continue

    return data