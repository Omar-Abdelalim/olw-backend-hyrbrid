from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date,Float,JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class Address(Base):
    id = Column(Integer, primary_key=True, index=True)
    customerID=Column(Integer,nullable=False)
    dateTime=Column(String,nullable=False)
    addressStatus=Column(String,nullable=False)
    address1=Column(String,nullable=False)
    address2=Column(String,nullable=True)
    country=Column(String,nullable=False)
    city=Column(String,nullable=False)
    zipCode=Column(String,nullable=False)
    
    

    def __str__(self):
        return self.id