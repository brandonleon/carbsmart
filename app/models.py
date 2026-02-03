from pydantic import BaseModel, ConfigDict, Field


class PanBase(BaseModel):
    name: str = Field(..., min_length=1)
    weight_grams: float = Field(..., gt=0)
    capacity_label: str | None = Field(
        default=None,
        description="Capacity or size label (volume or pan size, e.g. 2 qt, 3 L, 11-inch).",
    )
    notes: str | None = None


class PanCreate(PanBase):
    pass


class PanUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    weight_grams: float | None = Field(default=None, gt=0)
    capacity_label: str | None = None
    notes: str | None = None


class Pan(PanBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CalcRequest(BaseModel):
    total_weight_grams: float = Field(..., gt=0)
    pan_id: int = Field(..., gt=0)
    total_carbs: float = Field(..., ge=0)
    target_min_grams: float = Field(default=200, gt=0)
    target_max_grams: float = Field(default=300, gt=0)


class CalcResponse(BaseModel):
    net_weight_grams: float
    servings: int
    serving_weight_grams: float
    carbs_per_serving: float
