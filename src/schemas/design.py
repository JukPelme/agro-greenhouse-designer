"""Design variant schemas: what Designer agent produces."""

from pydantic import BaseModel, ConfigDict, Field

from .project import CoveringMaterial


class GreenhouseBlock(BaseModel):
    """A single rectangular greenhouse block within the complex."""

    name: str = Field(..., description="e.g. 'Блок 1 — томат'")
    length_m: float = Field(..., gt=0)
    width_m: float = Field(..., gt=0)
    ridge_height_m: float = Field(..., gt=0, description="Высота в коньке")
    eave_height_m: float = Field(..., gt=0, description="Высота по водостоку")
    covering: CoveringMaterial
    light_transmittance: float = Field(..., ge=0, le=1, description="Светопропускание ограждения, 0..1")
    bays_count: int = Field(default=1, ge=1, description="Число пролётов")

    @property
    def floor_area_m2(self) -> float:
        return self.length_m * self.width_m

    @property
    def volume_m3(self) -> float:
        avg_h = (self.ridge_height_m + self.eave_height_m) / 2
        return self.floor_area_m2 * avg_h

    @property
    def envelope_area_m2(self) -> float:
        """Площадь ограждающих конструкций (упрощённо: крыша + стены)."""
        roof = self.length_m * self.width_m * 1.15  # ~15% надбавка на скат
        walls = 2 * (self.length_m + self.width_m) * self.eave_height_m
        return roof + walls


class LayoutZone(BaseModel):
    name: str
    area_m2: float = Field(..., gt=0)
    purpose: str


class DesignVariant(BaseModel):
    """A proposed design option, before engineering verification."""

    # extra='allow' lets the rules engine attach computed virtual fields
    # (aux_share_pct, min_aisle_width_m, …) without expanding the schema.
    model_config = ConfigDict(extra="allow")

    variant_id: str
    rationale: str = Field(..., description="Why the Designer chose this configuration")
    blocks: list[GreenhouseBlock]
    aux_zones: list[LayoutZone] = Field(
        default_factory=list,
        description="Подсобные зоны: котельная, склад, тарный участок",
    )
    estimated_footprint_m2: float = Field(..., gt=0)

    @property
    def total_growing_area_m2(self) -> float:
        return sum(b.floor_area_m2 for b in self.blocks)
