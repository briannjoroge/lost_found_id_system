from db import get_db_connection

def check_for_ai_match(reg_number, new_found_id=None, submitting_user_id=None):
    """
    Checks for a match between lost and found IDs using the Registration Number.
    Automatically creates a Pending claim if a match is found.
    """
    if not reg_number:
        return 

    clean_reg = reg_number.upper().strip()
    conn = get_db_connection()

    # SCENARIO A: A student just submitted a LOST report
    # Also check if a Good Samaritan already found it
    if submitting_user_id:
        found_match = conn.execute(
            'SELECT id FROM found_ids WHERE UPPER(extracted_reg_number) = UPPER(?) AND status != "Returned"', 
            (clean_reg,)
        ).fetchone()
        
        if found_match:
            found_id = found_match['id']
            existing = conn.execute('SELECT id FROM claims WHERE found_id = ? AND user_id = ?', (found_id, submitting_user_id)).fetchone()
            if not existing:
                conn.execute(
                    'INSERT INTO claims (found_id, user_id, status, admin_notes) VALUES (?, ?, ?, ?)',
                    (found_id, submitting_user_id, 'Pending', f'🤖 Auto-Matched by AI (Reg No: {clean_reg})')
                )

    # SCENARIO B: A Good Samaritan just submitted a FOUND report
    # Also check if the owner is already looking for it
    elif new_found_id:
        lost_match = conn.execute(
            'SELECT user_id FROM lost_ids WHERE UPPER(reg_number) = UPPER(?) AND status = "Lost"', 
            (clean_reg,)
        ).fetchone()
        
        if lost_match:
            user_id = lost_match['user_id']
            existing = conn.execute('SELECT id FROM claims WHERE found_id = ? AND user_id = ?', (new_found_id, user_id)).fetchone()
            if not existing:
                conn.execute(
                    'INSERT INTO claims (found_id, user_id, status, admin_notes) VALUES (?, ?, ?, ?)',
                    (new_found_id, user_id, 'Pending', f'🤖 Auto-Matched by AI (Reg No: {clean_reg})')
                )

    conn.commit()
    conn.close()