# schema/user_schema

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserRegisterInput(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    password: str
    phoneNumber: str
    departmentId: int
    roleId: int
    subscriptionTypeId: int


class PaymentInfo(BaseModel):
    transactionId: Optional[str]= None
    paymentEvidence: Optional[str]= None


class UserRegisterResponse(BaseModel):
    userId: int
    firstName: str
    lastName: str
    email: EmailStr
    registrationStatus: bool
    payment: PaymentInfo




class LoginRequest(BaseModel):
    user_email: str
    user_password: str


class UserLoginResponse(BaseModel):
    status_code: int
    message: str
    userId: Optional[int] = None
    token: Optional[str] = None
    roleId: Optional[int] = None
    firstName: Optional[str] = None
    email: Optional[str] = None



class UserOut(BaseModel):
    userId: int
    firstName: str
    lastName: str
    email: EmailStr
    phoneNumber: str
    departmentName: str
    roleId: int
    subscriptionTypeName: str
    registrationStatus: bool
    isActive: bool
    createdAt: datetime



class RegistrationStatusUpdate(BaseModel):
    status: bool


class DepartmentSchema(BaseModel):
    departmentId: int
    departmentName: str


class SubscriptionTypeSchema(BaseModel):
    subscriptionTypeId: int
    subscriptionTypeName: str


# UserUpdate Schema
class UserUpdateRequest(BaseModel):
    firstName: Optional[str]
    lastName: Optional[str]
    phoneNumber: Optional[str]

# UserActiveStatusUpdate Schema
class UserActiveStatusUpdate(BaseModel):
    isActive: bool


# SubscriptionType Schemas
class SubscriptionTypeResponse(BaseModel):
    subscriptionTypeId: int
    subscriptionTypeName: str
    price: int

# Department types Schemas
class DepartmentResponse(BaseModel):
    departmentId: int
    departmentName: str



# Add Required Schemas
class DepartmentData(BaseModel):
    id: int
    name: str

class SubscriptionTypeData(BaseModel):
    id: int
    name: str
    price: float

class PaymentData(BaseModel):
    userPaymentId: Optional[int]
    paymentEvidence: Optional[str]
    transactionId: Optional[str]
    createdAt: Optional[datetime]

class FetchUserResponse(BaseModel):
    userId: int
    firstName: str
    lastName: str
    email: EmailStr
    phoneNumber: str
    roleId: int
    registrationStatus: bool
    isActive: bool
    createdAt: datetime
    department: DepartmentData
    subscriptionType: SubscriptionTypeData
    payment: Optional[PaymentData]