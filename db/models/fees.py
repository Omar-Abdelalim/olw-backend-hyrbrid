from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date,Float,JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class Fee(Base):
    id = Column(Integer, primary_key=True, index=True)
    merchantID = Column(String,nullable=True)
    categoryID = Column(String,nullable=False)
    categoryName = Column(String,nullable=False)
    categoryDescription = Column(String,nullable=True)

    serviceCode = Column(String,nullable=False)
    campaign = Column(String,nullable=False)
    status = Column(String,nullable=False)
    feeDescription = Column(String,nullable=True)

    feeMax= Column(Float,nullable=False)
    feeMin= Column(Float,nullable=False)
    feeFixed = Column(Float,nullable=False)
    feeRate = Column(Float,nullable=False)
    

    def __str__(self):
        return self.id