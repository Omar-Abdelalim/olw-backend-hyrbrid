from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date,Float,JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class EmailCode(Base):
    id = Column(Integer, primary_key=True, index=True)
    customerID=Column(Integer,nullable=False)
    dateTime=Column(String,nullable=False)
    email = Column(String,nullable=False)
    code=Column(String,nullable=False)
    expiration=Column(String,nullable=False)
    result=Column(String,nullable=True)
    
    

    def __str__(self):
        return self.id