from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date,Float,JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class Customer(Base):
    id = Column(Integer, primary_key=True, index=True)
    firstName=Column(String,nullable=False)
    lastName=Column(String,nullable=False)
    email=Column(String,nullable=False,unique=True)
    birthdate = Column(String,nullable=False)
    customerStatus=Column(String,nullable=False)
    customerNumber=Column(String,nullable=False)    
    phoneNumber=Column(String,nullable=True)
    countryCode = Column(String,nullable=True)
    pin=Column(String,nullable=True)
    smsCode = Column(String,nullable=True)
    emailCode = Column(String,nullable=True)
    smsValid = Column(String,nullable=True)
    comment=Column(String,nullable=True)
    IDIqama=Column(String,nullable=True)


    def __str__(self):
        return self.id