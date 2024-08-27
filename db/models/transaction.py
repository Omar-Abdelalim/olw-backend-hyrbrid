from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date,Float,JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class Transaction(Base):
    id = Column(Integer, primary_key=True, index=True)
    dateTime=Column(String,nullable=False)

    fromAccountNo=Column(String,nullable=False)
    toAccountNo=Column(String,nullable=False)
    
    
    transactionStatus=Column(String,nullable=False)
    description=Column(String,nullable=True)
    amount=Column(Float,nullable=False)

    sendID=Column(Integer,nullable=False)
    recID = Column(Integer,nullable=False)

    transactionIdentifier = Column(String,nullable = True)
    counterPart = Column(Integer,nullable = True)
    
    

    def __str__(self):
        return self.id