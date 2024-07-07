from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date,Float,JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class KYC2(Base):
    id = Column(Integer, primary_key=True, index=True)
    customerID=Column(Integer,nullable=False)
    incomeRange=Column(Integer,nullable=False)
    profession=Column(Integer,nullable=False)
    sourceOfIncome=Column(Integer,nullable=False)
    employment=Column(Integer,nullable=False)
    kycStatus= Column(String,nullable=False)
    
    

    def __str__(self):
        return self.id