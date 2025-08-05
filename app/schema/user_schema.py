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


# class UserOut(BaseModel):
#     userId: int
#     firstName: str
#     lastName: str
#     email: EmailStr
#     phoneNumber: str
#     registrationStatus: bool
#     isActive: bool
#     createdAt: datetime

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



class UserUpdateRequest(BaseModel):
    firstName: Optional[str]
    lastName: Optional[str]
    phoneNumber: Optional[str]


class UserActiveStatusUpdate(BaseModel):
    isActive: bool



class SubscriptionTypeResponse(BaseModel):
    subscriptionTypeId: int
    subscriptionTypeName: str
    price: int


class DepartmentResponse(BaseModel):
    departmentId: int
    departmentName: str
