"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserSettings
from app.schemas.auth import SignUpRequest, SignInRequest, AuthResponse, UserResponse, UserUpdateRequest
from app.core.security import verify_password, get_password_hash
from app.core.dependencies import get_user_or_create_default

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse)
@router.post("/signup", response_model=AuthResponse)
async def register(request_data: dict = Body(...), db: Session = Depends(get_db)):
    """User registration (aliases: /register, /signup) - handles both camelCase and snake_case"""
    # Convert camelCase to snake_case
    data = request_data.copy()
    if "firstName" in data:
        data["first_name"] = data.pop("firstName")
    if "lastName" in data:
        data["last_name"] = data.pop("lastName")
    
    # Validate
    try:
        request = SignUpRequest(**data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(e)}"
        )
    
    # Check if user exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    first_name = request.first_name
    last_name = request.last_name
    
    user = User(
        email=request.email,
        password_hash=get_password_hash(request.password),
        first_name=first_name,
        last_name=last_name,
        phone=request.phone,
        role=request.role or "user",
        is_active=1
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create default user settings
    settings = UserSettings(user_id=user.id)
    db.add(settings)
    db.commit()
    
    # NO TOKEN - Just return user info
    user_response = UserResponse.model_validate(user)
    return AuthResponse(
        access_token="no_auth_required",  # Dummy token for frontend compatibility
        token_type="bearer",
        user=user_response
    )


@router.post("/login", response_model=AuthResponse)
@router.post("/signin", response_model=AuthResponse)  # Alias for login
async def login(request: SignInRequest, db: Session = Depends(get_db)):
    """User login"""
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # NO TOKEN - Just return user info
    return AuthResponse(
        access_token="no_auth_required",  # Dummy token for frontend compatibility
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(db: Session = Depends(get_db)):
    """Get current user information - NO AUTH REQUIRED"""
    import json
    # Return default user or first user
    user = db.query(User).filter(User.is_active == 1).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user found"
        )
    
    # Parse JSON fields from database strings
    user_dict = {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": user.phone,
        "role": user.role,
        "qualification": user.qualification,
        "occupation": user.occupation,
        "professional_summary": user.professional_summary,
        "avatar_url": user.avatar_url,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        # Parse JSON fields
        "skills": json.loads(user.skills) if user.skills else [],
        "experience": json.loads(user.experience) if user.experience else [],
        "publications": json.loads(user.publications) if user.publications else [],
        "awards": json.loads(user.awards) if user.awards else [],
        "social_links": json.loads(user.social_links) if user.social_links else {}
    }
    
    return UserResponse.model_validate(user_dict)


@router.patch("/profile", response_model=UserResponse)
async def update_profile(
    update_data: UserUpdateRequest,
    db: Session = Depends(get_db)
):
    # Get default user - NO AUTH REQUIRED
    current_user = get_user_or_create_default(db)
    """Update user profile"""
    # Update only provided fields
    update_dict = update_data.dict(exclude_unset=True)
    
    # Handle JSON fields
    if 'skills' in update_dict and update_dict['skills'] is not None:
        current_user.set_skills(update_dict['skills'])
        update_dict.pop('skills')
    if 'experience' in update_dict and update_dict['experience'] is not None:
        import json
        current_user.experience = json.dumps(update_dict['experience'])
        update_dict.pop('experience')
    if 'publications' in update_dict and update_dict['publications'] is not None:
        import json
        current_user.publications = json.dumps(update_dict['publications'])
        update_dict.pop('publications')
    if 'awards' in update_dict and update_dict['awards'] is not None:
        import json
        current_user.awards = json.dumps(update_dict['awards'])
        update_dict.pop('awards')
    if 'social_links' in update_dict and update_dict['social_links'] is not None:
        import json
        current_user.social_links = json.dumps(update_dict['social_links'])
        update_dict.pop('social_links')
    
    # Update other fields
    for field, value in update_dict.items():
        if hasattr(current_user, field) and value is not None:
            setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)

