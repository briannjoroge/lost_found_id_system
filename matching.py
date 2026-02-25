import difflib
from db import get_db_connection

def get_similarity(str1, str2):
    """Returns a similarity score between 0.0 and 100.0"""
    if not str1 or not str2:
        return 0.0
    s1 = str(str1).upper().replace(" ", "").strip()
    s2 = str(str2).upper().replace(" ", "").strip()
    return difflib.SequenceMatcher(None, s1, s2).ratio() * 100

def check_for_ai_match(reg_number, phone_number=None, new_found_id=None, submitting_user_id=None):
    """
    Checks for a match between lost and found IDs using the Registration Number.
    Automatically creates a Pending claim if a match is found.
    """
    if not reg_number:
        return 

    conn = get_db_connection()
    THRESHOLD = 80.0 
    best_score = 0
    best_match_data = None

    # SCENARIO A: A student just submitted a LOST report
    # Also check if a Good Samaritan already found it
    if submitting_user_id:
        found_items = conn.execute('SELECT id, extracted_reg_number, extracted_phone FROM found_ids WHERE status != "Returned"').fetchall()
        
        for item in found_items:
            reg_score = get_similarity(reg_number, item['extracted_reg_number'])
            
            if phone_number and item['extracted_phone']:
                phone_score = get_similarity(phone_number, item['extracted_phone'])
                total_score = (reg_score + phone_score) / 2
            else:
                total_score = reg_score
                
            if total_score > best_score and total_score >= THRESHOLD:
                best_score = total_score
                best_match_data = {'found_id': item['id'], 'user_id': submitting_user_id}

    # SCENARIO B: A Good Samaritan just submitted a FOUND report
    # Also check if the owner is already looking for it
    elif new_found_id:
        lost_items = conn.execute('SELECT user_id, reg_number, phone_number FROM lost_ids WHERE status = "Lost"').fetchall()
        
        for item in lost_items:
            reg_score = get_similarity(reg_number, item['reg_number'])
            
            if phone_number and item['phone_number']:
                phone_score = get_similarity(phone_number, item['phone_number'])
                total_score = (reg_score + phone_score) / 2
            else:
                total_score = reg_score
                
            if total_score > best_score and total_score >= THRESHOLD:
                best_score = total_score
                best_match_data = {'found_id': new_found_id, 'user_id': item['user_id']}

    # IF WE FOUND A HIGH CONFIDENCE MATCH ---
    if best_match_data:
        found_id = best_match_data['found_id']
        user_id = best_match_data['user_id']
        
        existing = conn.execute('SELECT id FROM claims WHERE found_id = ? AND user_id = ?', (found_id, user_id)).fetchone()
        
        if not existing:
            formatted_score = f"{best_score:.1f}%"
            note = f"🤖 AI Match: {formatted_score} Confidence"
            
            conn.execute(
                'INSERT INTO claims (found_id, user_id, status, admin_notes) VALUES (?, ?, ?, ?)',
                (found_id, user_id, 'Pending', note)
            )

    conn.commit()
    conn.close()