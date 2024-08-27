from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date,Float,JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class TransactionType(Base):

    code=Column(String,primary_key = True,nullable=False)
    name = Column(String,nullable=False)

    status=Column(String,nullable=False)
    description=Column(String,nullable=True)
    
    dd = Column(Integer,nullable=False)
    mm = Column(Integer,nullable=False)
    yy = Column(Integer,nullable=False)

    number = Column(Integer,nullable=False)

    def __str__(self):
        return self.id