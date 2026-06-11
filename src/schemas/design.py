"""Design variant schemas: what Designer agent produces.

Expanded with SP 107.13330-relevant geometric and material parameters
so the Validator can check real clauses (5.5, 5.8–5.10, 5.23, etc.).
"""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from .project import CoveringMaterial


class RoofShape(str, Enum):
    STRAIGHT = "straight"  # прямолинейные скаты — уклон ≥45° (СП 5.10)
    ARCHED = "arched"      # криволинейные стрельчатые — уклон ≥20°


class GreenhouseLayoutType(str, Enum):
    ANGAR = "angar"        # ангарная (однопролётная)
    BLOCK = "block"        # блочная (многопролётная)


class GreenhouseBlock(BaseModel):
    """A single rectangular greenhouse block within the complex."""

    name: str
    length_m: float = Field(..., gt=0)
    width_m: float = Field(..., gt=0)
    ridge_height_m: float = Field(..., gt=0, description="Высота в коньке")
    eave_height_m: float = Field(..., gt=0, description="Высота по водостоку")
    covering: CoveringMaterial
    light_transmittance: float = Field(..., ge=0, le=1)

    # ── СП 107.13330 п. 5.5 — пролёты и компоновка ──
    layout: GreenhouseLayoutType = GreenhouseLayoutType.BLOCK
    span_count: int = Field(default=1, ge=1, description="Число пролётов")
    span_width_m: float = Field(
        default=9.0,
        gt=0,
        description="Ширина одного пролёта, м (по умолчанию 9 м, типовая для блочной многопролётной — п. 5.5)",
    )

    # ── СП 107.13330 п. 5.10 — уклоны кровли ──
    roof_shape: RoofShape = RoofShape.STRAIGHT
    roof_slope_pct: float = Field(
        default=45.0,
        ge=0,
        description="Уклон ската кровли, %. ≥45 для straight, ≥20 для arched (п. 5.10)",
    )

    # ── СП 107.13330 п. 5.23 — толщина стекла ──
    glass_thickness_mm: float | None = Field(
        default=None,
        description="Толщина стекла, мм (≤4, по п. 5.23). None если ограждение не стеклянное.",
    )

    # ── СП 107.13330 п. 5.11 — доля светонепроницаемых конструкций ──
    opaque_share_pct: float = Field(
        default=10.0,
        ge=0,
        le=100,
        description="Доля светонепроницаемых конструкций блока, %. ≤15 для стекла, ≤10 для плёнки.",
    )

    @property
    def floor_area_m2(self) -> float:
        return self.length_m * self.width_m

    @property
    def volume_m3(self) -> float:
        avg_h = (self.ridge_height_m + self.eave_height_m) / 2
        return self.floor_area_m2 * avg_h

    @property
    def envelope_area_m2(self) -> float:
        """Площадь ограждающих конструкций: крыша + продольные/торцевые стены."""
        roof = self.length_m * self.width_m * 1.15
        walls = 2 * (self.length_m + self.width_m) * self.eave_height_m
        return roof + walls


class LayoutZone(BaseModel):
    name: str
    area_m2: float = Field(..., gt=0)
    purpose: str


class DesignVariant(BaseModel):
    """A proposed design option, before engineering verification."""

    model_config = ConfigDict(extra="allow")

    variant_id: str
    rationale: str = Field(..., description="Why the Designer chose this configuration")
    blocks: list[GreenhouseBlock]
    aux_zones: list[LayoutZone] = Field(default_factory=list)
    estimated_footprint_m2: float = Field(..., gt=0)

    # ── СП 107.13330 п. 5.8, 5.9, 4.16 — фундамент и территория ──
    plinth_height_m: float = Field(
        default=0.4,
        ge=0,
        description="Высота цоколя теплицы, м (≥0,3 по п. 5.8)",
    )
    foundation_above_soil_m: float = Field(
        default=0.4,
        ge=0,
        description="Превышение верха фундамента над уровнем почвы, м (≥0,3 по п. 5.9)",
    )
    fence_height_m: float = Field(
        default=1.8,
        ge=0,
        description="Высота ограждения территории комплекса, м (≥1,6 по п. 4.16)",
    )

    @property
    def total_growing_area_m2(self) -> float:
        return sum(b.floor_area_m2 for b in self.blocks)
