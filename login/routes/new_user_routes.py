import datetime , gspread ,uuid, secrets # type: ignore
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, Request # type: ignore
from sqlalchemy.orm import Session # type: ignore
from fastapi.responses import JSONResponse # type: ignore
from passlib.hash import bcrypt # type: ignore
from login import models
from login.schemas import DeleteAccountRequest, ForgotRequest, ForgotRequest2, ResetPasswordRequest, VerifySchema, newusercreate, newuserlogin, newusernextstep
from login.database import SessionLocal
from login.utils import   send_login_email, send_otp_email, send_registration_email
from google.oauth2.service_account import Credentials  # type: ignore
import logging


router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_unique_token():
    return str(uuid.uuid4())

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def has_two_unique_chars(value):
    return len(set(value.replace(" ", "").lower())) >= 2

SERVICE_ACCOUNT_FILE = "D:\\BHARATHTECH TASKS\\collegcue-firebase-adminsdk-p63yc-498e419897.json"

SPREADSHEET_ID = '1UCiJsKfBT6eejyx07Tr7vEJylyfldVMbDyH0Au_kkdg'

def write_to_google_sheet(user_data):
    try:
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        credentials = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=scopes
        )

        client = gspread.authorize(credentials)

        worksheet = client.open_by_key(SPREADSHEET_ID).sheet1

        existing_data = worksheet.get_all_records()
        headers = worksheet.row_values(1)

        email_column = 'email'

        if email_column not in headers:
            raise ValueError(f"'{email_column}' column not found in the Google Sheet")

        email_index = headers.index(email_column)

        if any(record.get(email_column) == user_data['email'] for record in existing_data):
            return

        today_date = datetime.date.today().isoformat()

        new_row = [
            user_data.get('firstname', ''),
            user_data.get('lastname', ''),
            user_data.get('email', ''),
            user_data.get('country_code', ''),
            user_data.get('phonenumber', ''),
            user_data.get('gender', ''),
            user_data.get('password', ''),
            user_data.get('agreed_to_terms', ''),
            today_date
        ]

        worksheet.append_row(new_row)

    except Exception as e:
        raise RuntimeError(f"Failed to write user data to Google Sheet: {str(e)}")

@router.post("/register")
def register_user(user: newusercreate, db: Session = Depends(get_db)):
    print("Register function called", flush=True)
    logger.info("Processing registration logic")
    
    try:
        errors: Dict[str, str] = {}

        existing_user = db.query(models.new_user).filter_by(email=user.email).first()

        if existing_user:
            if existing_user.firstname != user.firstname or existing_user.lastname != user.lastname:
                errors['email'] = 'Email already registered with different name'
            else:
                errors['email'] = 'Email already registered'

        phone_exists = db.query(models.new_user).filter_by(
            country_code=user.country_code,
            phonenumber=user.phonenumber
        ).first()
        if phone_exists:
            errors['phonenumber'] = 'Phone number already registered'

        if '@' in user.email:
            email_username = user.email.split('@')[0]
            if not has_two_unique_chars(email_username):
                errors['email'] = 'Email must contain at least 2 unique characters before @'
        
        if user.password != user.confirm_password:
            errors['password'] = 'Passwords do not match'
        
        if errors:
            raise HTTPException(status_code=400, detail=errors)
        
        hashed_password = bcrypt.hash(user.password)
        hashed_password1 = bcrypt.hash(user.confirm_password)

        new_user = models.new_user(
            firstname=user.firstname,
            lastname=user.lastname,
            email=user.email,
            country_code=user.country_code,
            phonenumber=user.phonenumber,
            password=hashed_password,
            confirm_password =hashed_password1,
            gender=user.gender,
            agreed_to_terms=user.agreed_to_terms
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        user_data = {
            'firstname':user.firstname,
            'lastname':user.lastname,
            'email':user.email,
            'country_code':user.country_code,
            'phonenumber':user.phonenumber,
            'password':hashed_password,
            'gender':user.gender,
            'agreed_to_terms':user.agreed_to_terms
                
        }
        
        write_to_google_sheet(user_data)
        
        try:
            send_registration_email(user.firstname, user.email)
            print("Sending email...", flush=True)
            logger.info("Email sent successfully")
        except HTTPException as e:
            logger.error(f"Email failed: {e}")
            raise HTTPException(status_code=500, detail=f"Email sending failed: {str(e)}")

        
        return JSONResponse({'message': 'Registration successful'})

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


# @router.post("/next")
# def complete_registration(user: newusernextstep, db: Session = Depends(get_db)):
#     try:
#         errors: Dict[str, str] = {}

#         if not user.entrance:
#             errors['entrance'] = 'Check box not clicked'
#         if not user.passport:
#             errors['passport'] = 'Check box not clicked'

#         if errors:
#             raise HTTPException(status_code=400, detail=errors)

#         hashed_password = bcrypt.hash(user.password)

#         new_user = models.new_user(
#             firstname=user.firstname,
#             lastname=user.lastname,
#             email=user.email,
#             country_code=user.country_code,
#             phonenumber=user.phonenumber,
#             password=hashed_password,
#             course=user.course,
#             educations=user.education,
#             percentage=user.percentage,
#             preferred_destination=user.preferred_destination,
#             start_date=user.start_date,
#             mode_study=user.mode_study,
#             entrance=user.entrance,
#             passport=user.passport
#         )

#         db.add(new_user)
#         db.commit()
#         db.refresh(new_user)

#         return JSONResponse({'message': 'Registration successful'})

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login")
def login(user: newuserlogin, db: Session = Depends(get_db)):
    try:
        user_db = db.query(models.new_user).filter_by(email=user.email, is_deleted=False).first()
        if not user_db or not bcrypt.verify(user.password, user_db.password):
            raise HTTPException(status_code=400, detail="Invalid credentials")

        token = generate_unique_token()
        user_db.token = token
        user_db.is_online = True

        status_record = db.query(models.OnlineStatus).filter_by(email=user.email).first()
        if status_record:
            status_record.is_online = True
        else:
            db.add(models.OnlineStatus(email=user.email, is_online=True))

        db.commit()

        try:
            send_login_email(user.email, user_db.firstname)
            print("Sending email...", flush=True)
            logger.info("Email sent successfully")
        except HTTPException as e:
            logger.error(f"Email failed: {e}")
            raise HTTPException(status_code=500, detail=f"Email sending failed: {str(e)}")

        return {
            "message": "Login successful",
            "unique_token": token,
            "firstname": user_db.firstname,
            "lastname": user_db.lastname,
            "phone": user_db.phonenumber,
            "email": user_db.email,
            "id": user_db.id,
            "model": "new_user"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@router.post("/logout")
async def logout_new_user(request: Request, db: Session = Depends(get_db)):
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=400, detail="Token is missing or in invalid format")

        token = auth_header.removeprefix("Bearer ").strip()

        user = db.query(models.new_user).filter_by(token=token).first()
        if not user:
            raise HTTPException(status_code=404, detail="Invalid or expired token")

        user.token = None
        user.is_online = False
        db.query(models.OnlineStatus).filter_by(email=user.email).update({"is_online": False})

        db.commit()

        return JSONResponse({"success": True, "message": "Logout successful"}, status_code=200)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")

@router.post("/forgot")
def forgot_password(request: Request, data: ForgotRequest, db: Session = Depends(get_db)):
    try:
        user = db.query(models.new_user).filter_by(email=data.email).first()
        if not user:
            raise HTTPException(status_code=404, detail="Email does not exist")

        new_otp = ''.join([str(secrets.randbelow(10)) for _ in range(4)])

        request.session['otp'] = new_otp
        request.session['email'] = data.email
        
        user_email = models.Forgot(
           email=data.email,
       
       )

        db.add(user_email)
        db.commit()
        db.refresh(user_email)

        try:
            send_otp_email(user.email, new_otp, user.firstname)
            print("Sending email...", flush=True)
            logger.info("Email sent successfully")
        except HTTPException as e:
            logger.error(f"Email failed: {e}")
            raise HTTPException(status_code=500, detail=f"Email sending failed: {str(e)}")

        return JSONResponse(content={'message': 'OTP sent successfully'}, status_code=200)

    except Exception as e:
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@router.post("/verify")
def verify_otp(request: Request, data: VerifySchema, db: Session = Depends(get_db)):
    try:
        stored_otp = request.session.get("otp")
        if not stored_otp:
            raise HTTPException(status_code=400, detail="Session data not found")

        if str(stored_otp) != str(data.otp):
            raise HTTPException(status_code=400, detail="Invalid OTP")

        otp = models.Verify(
            otp=data.otp
        )
        
        db.add(otp)
        db.commit()
        db.refresh(otp)

        del request.session["otp"]

        return {"message": "OTP verification successful"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/resend-otp")
def resend_otp(request: Request, db: Session = Depends(get_db)):
    try:
        stored_email = request.session.get("email")
        if not stored_email:
            raise HTTPException(status_code=400, detail="Session data not found")
        
        user = db.query(models.new_user).filter_by(email=stored_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        new_otp = ''.join([str(secrets.randbelow(10)) for _ in range(4)])

        request.session["otp"] = new_otp

        if not  send_otp_email(user.email, new_otp, user.firstname):
            raise HTTPException(status_code=500, detail="Failed to send OTP email")

        return JSONResponse(content={"message": "OTP sent successfully"}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)
    
@router.post("/forgot2")
def forgot2(request: Request, data: ForgotRequest2, db: Session = Depends(get_db)):
    try:
        password = data.password
        confirm_password = data.confirm_password

        if not password or not confirm_password:
            raise HTTPException(status_code=400, detail="Password and confirm_password are required")

        if password != confirm_password:
            return JSONResponse(content={'error': 'Passwords did not match'}, status_code=400)

        stored_email = request.session.get("email")
        if not stored_email:
            raise HTTPException(status_code=400, detail="Session expired or not found")

        user = db.query(models.new_user).filter_by(email=stored_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if bcrypt.verify(password, user.password):
            raise HTTPException(
                status_code=400,
                detail="New password cannot be the same as the current password"
            )

        user.password = bcrypt.hash(password)
        db.commit()

        del request.session["email"]

        return JSONResponse(content={"message": "Password updated successfully"}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Password reset failed: {str(e)}")
    
@router.post("/reset-password")
def reset_password(request: Request, data: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=400, detail="Token is missing or invalid format")

        token = auth_header.removeprefix("Bearer ").strip()

        email = data.email
        old_password = data.old_password
        new_password = data.new_password
        confirm_password = data.confirm_password

        if new_password != confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")

        if old_password == new_password:
            raise HTTPException(status_code=400, detail="New password cannot be the same as the old password")

        user = db.query(models.new_user).filter_by(email=email, token=token, is_deleted=False).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found or invalid token")

        if not bcrypt.verify(old_password, user.password):
            raise HTTPException(status_code=400, detail="Old password is incorrect")

        user.password = bcrypt.hash(new_password)
        db.commit()

        return {"success": True, "message": "Password has been reset successfully"}

    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(content={"error": f"Password reset failed: {str(e)}"}, status_code=500)

@router.post("/delete-account")
def delete_account(request: Request, request_data: DeleteAccountRequest, db: Session = Depends(get_db)):
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=400, detail="Authorization token missing or invalid format")

        token = auth_header.removeprefix("Bearer ").strip()

        user = db.query(models.new_user).filter_by(token=token).first()
        if not user:
            raise HTTPException(status_code=404, detail="Invalid or expired token")

        if request_data.confirmation:
            user.is_deleted = True
            user.token = None
            user.is_online = False
            db.delete(user)
            db.commit()

            return {"success": True, "message": "Account deleted successfully"}

        else:
            return {"success": False, "message": "Account deletion canceled by user"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Account deletion failed: {str(e)}")
