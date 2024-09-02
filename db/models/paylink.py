from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date,Float,JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class PayLink(Base):
    paylinkID = Column(String, primary_key=True)
    MerchantId=Column(Integer,nullable=False)
    amount=Column(Float,nullable=False)
    currency=Column(String,nullable=False)
    transactionRefferance=Column(String,nullable=False)
    dateTime=Column(String,nullable=True)
    status=Column(String,nullable=False)
    link=Column(String,nullable=False)
   
    

    def __str__(self):
        return self.id
    
    
