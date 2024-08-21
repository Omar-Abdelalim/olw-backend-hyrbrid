from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date,Float,JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class LastAccount(Base):
    id = Column(Integer, primary_key=True, index=True)
    lastNumber = Column(Integer,nullable = False)

    lastAccountNumber = Column(Integer,nullable = True)
    busy = Column(Boolean,nullable = False)
    status = Column(String,nullable=False)

    def __str__(self):
        return self.id