from pydantic import BaseModel, Field

class SoilInput(BaseModel):
    N: float = Field(..., example=5.1)
    P: float = Field(..., example=3.5)
    K: float = Field(..., example=1.4)
    temperature: float = Field(..., example=0.2)
    humidity: float = Field(..., example=0.9)
    ph: float = Field(..., example=2.3)
    rainfall: float = Field(..., example=1.1)

    def to_list(self):
        return [self.N, self.P, self.K, self.temperature, self.humidity, self.ph, self.rainfall]


