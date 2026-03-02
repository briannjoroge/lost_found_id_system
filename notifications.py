from flask_mail import Message

def send_approval_email(student_name, student_email):
    """
    Sends an official MUT-branded HTML email to notify a student 
    that their ID is ready for pickup.
    """
    if not student_email:
        return False
        
    # Imported inside the function to prevent circular import crashes
    from app import mail 
    
    try:
        msg = Message(
            "Good News! Your Lost ID is Ready for Pickup",
            recipients=[student_email]
        )
        
        msg.body = f"Hello {student_name},\n\nYour lost ID claim has been officially verified and approved! You can now visit the Admin Block to pick it up.\n\nThank you,\nMUT Admin"
        
        msg.html = f"""
        <div style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: auto; border: 1px solid #ddd; border-radius: 8px; overflow: hidden;">
            <div style="background-color: #2E8B57; color: white; padding: 15px; text-align: center;">
                <h2 style="margin: 0;">Murang'a University of Technology</h2>
                <p style="margin: 5px 0 0 0; font-size: 14px;">Lost & Found Department</p>
            </div>
            <div style="padding: 20px;">
                <p>Hello <b>{student_name}</b>,</p>
                <p>Great news! Your lost ID claim has been officially verified and approved.</p>
                <p>You can now visit the Admin Block to pick it up. Please bring any alternative form of identification if possible.</p>
                <br>
                <p>Thank you,<br><b>MUT Admin</b></p>
            </div>
        </div>
        """
        
        mail.send(msg)
        print(f"Success: Notification email sent to {student_email}")
        return True
        
    except Exception as e:
        print(f"Warning: Email failed to send to {student_email}. Error: {e}")
        return False