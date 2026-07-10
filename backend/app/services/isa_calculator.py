"""
ISA - Índice de Saúde Ambiental (MSBD-360 Method)

Multi-criteria index based on 6 pillars with cross-parameter relationship rules:
  1. Condições Térmicas (Thermal)       - Temperature
  2. Humidade e Condensação (Humidity)   - RH, Surface Temp, Dew Point
  3. Ventilação (Ventilation)            - CO2
  4. Estado dos Materiais (Materials)    - Material Moisture
  5. Iluminação (Lighting)               - Illuminance (Lux)
  6. Evidências Visuais (Visual)        - Observations & Photos

Cross-parameter rules (Pillar 3 of Marília's method):
  - CO₂ > 1000 ppm + RH > 65%  → poor ventilation, condensation risk
  - Surface temp < Dew point    → imminent condensation, major penalty
  - RH > 70% + CO₂ > 1000 + Temp < 20°C  → microbiological risk
  - Low lux + high RH           → fungus persistence risk

Reference ranges: ASHRAE, ISO 7730, NBR 16401, NBR 5413, WHO
"""

import math
from dataclasses import dataclass, field
from typing import Optional

from app.utils.enums import ISACategory


@dataclass
class PillarResult:
    score: float
    weight: float = 1.0
    details: str = ""


@dataclass
class SubLocationResult:
    sub_location: str
    pillars: dict[str, PillarResult] = field(default_factory=dict)
    overall_score: float = 0.0
    alerts: list[str] = field(default_factory=list)


@dataclass
class RoomISAResult:
    room_id: int
    room_name: str
    pillars: dict[str, PillarResult] = field(default_factory=dict)
    overall_score: float = 0.0
    sub_locations: dict[str, SubLocationResult] = field(default_factory=dict)
    alerts: list[str] = field(default_factory=list)

    @property
    def category(self) -> ISACategory:
        return score_to_category(self.overall_score)


PILLAR_WEIGHTS = {
    "thermal": 1.0,
    "humidity": 1.2,
    "ventilation": 1.1,
    "materials": 1.0,
    "lighting": 0.8,
    "visual": 0.9,
}


def score_to_category(score: float) -> ISACategory:
    if score >= 80:
        return ISACategory.EXCELLENT
    if score >= 60:
        return ISACategory.ACCEPTABLE
    if score >= 40:
        return ISACategory.NEEDS_INTERVENTION
    return ISACategory.HIGH_RISK


def _linear_score(value: float | None, ideal_min: float, ideal_max: float, min_out: float, max_out: float) -> float:
    if value is None:
        return 0.0
    if ideal_min <= value <= ideal_max:
        return 100.0
    if value < ideal_min:
        if value <= min_out:
            return 0.0
        return ((value - min_out) / (ideal_min - min_out)) * 100
    if value >= max_out:
        return 0.0
    return ((max_out - value) / (max_out - ideal_max)) * 100


def _calc_dew_point(temp: float, rh: float) -> float:
    """Magnus formula for dew point temperature."""
    a, b = 17.27, 237.7
    gamma = (a * temp) / (b + temp) + math.log(rh / 100.0)
    return (b * gamma) / (a - gamma)


def score_temperature(temp: float | None) -> float:
    return _linear_score(temp, 20.0, 24.0, 10.0, 35.0)


def score_humidity_raw(rh: float | None) -> float:
    return _linear_score(rh, 40.0, 60.0, 15.0, 90.0)


def score_co2(co2: float | None) -> float:
    if co2 is None:
        return 0.0
    if co2 <= 800:
        return 100.0
    if co2 >= 2000:
        return 0.0
    return ((2000 - co2) / (2000 - 800)) * 100


def score_materials(moisture: float | None) -> float:
    if moisture is None:
        return 0.0
    if moisture <= 12:
        return 100.0
    if moisture >= 30:
        return 0.0
    return ((30 - moisture) / (30 - 12)) * 100


def score_lighting(lux: float | None) -> float:
    if lux is None:
        return 0.0
    if 300 <= lux <= 750:
        return 100.0
    if lux < 300:
        if lux <= 50:
            return 10.0
        return ((lux - 50) / (300 - 50)) * 90 + 10
    if lux >= 2000:
        return 20.0
    return ((2000 - lux) / (2000 - 750)) * 80 + 20


def score_visual(observations: str | None, photo_count: int) -> float:
    if not observations and photo_count == 0:
        return 100.0
    issues = [
        "mofo", "bolor", "infiltração", "trinca", "rachadura",
        "mancha", "umidade", "descolamento", "ferrugem",
    ]
    score = 100.0
    if observations:
        obs_lower = observations.lower()
        found = sum(1 for word in issues if word in obs_lower)
        score -= found * 15
    return max(0, score)


def _evaluate_cross_rules(temp: float | None, rh: float | None, co2: float | None,
                          surface_temp: float | None, lux: float | None) -> tuple[float, list[str]]:
    """Apply cross-parameter relationship rules. Returns (total_penalty, alerts)."""
    penalty = 0.0
    alerts = []

    # Rule 1: Condensation risk — surface temp < dew point
    if temp is not None and rh is not None and surface_temp is not None:
        dew_point = _calc_dew_point(temp, rh)
        temp_diff = surface_temp - dew_point
        if temp_diff < 0:
            # Active condensation
            penalty += 30
            alerts.append(f"Condensação ativa: Tsuperfície ({surface_temp:.1f}°C) abaixo do ponto de orvalho ({dew_point:.1f}°C)")
        elif temp_diff < 3:
            # Near condensation
            penalty += 15
            alerts.append(f"Risco de condensação: Tsuperfície ({surface_temp:.1f}°C) próxima ao ponto de orvalho ({dew_point:.1f}°C)")

    # Rule 2: Poor ventilation + high humidity
    if co2 is not None and rh is not None:
        if co2 > 1000 and rh > 65:
            penalty += 10
            alerts.append(f"Ventilação insuficiente: CO₂ elevado ({co2:.0f} ppm) com humidade alta ({rh:.0f}%)")

    # Rule 3: Microbiological risk
    if rh is not None and co2 is not None and temp is not None:
        if rh > 70 and co2 > 1000 and temp < 20:
            penalty += 20
            alerts.append("Risco microbiológico elevado: humidade alta, CO₂ elevado e temperatura baixa")

    # Rule 4: Fungus persistence (dark + humid)
    if lux is not None and rh is not None:
        if lux < 100 and rh > 65:
            penalty += 5
            alerts.append("Ambiente favorável a fungos: pouca luz e humidade elevada")

    return min(penalty, 50.0), alerts


class ISACalculator:
    """Computes the ISA score with multi-criteria analysis per sub-location."""

    def _calculate_measurement_group(self, measurements: list[dict], photo_count: int = 0) -> tuple[dict, list[str]]:
        """Calculate pillar scores from a group of measurements (same sub_location)."""
        m = measurements[-1]
        temp = m.get("temperature")
        rh = m.get("relative_humidity")
        co2 = m.get("co2")
        surface_temp = m.get("surface_temperature")
        moisture = m.get("material_moisture")
        lux = m.get("illuminance")
        obs = m.get("observations")

        penalty, alerts = _evaluate_cross_rules(temp, rh, co2, surface_temp, lux)

        pillars = {
            "thermal": PillarResult(
                score=max(0, score_temperature(temp) - penalty * 0.2),
                weight=PILLAR_WEIGHTS["thermal"],
                details=f"Temp: {temp}°C" if temp is not None else "N/A",
            ),
            "humidity": PillarResult(
                score=max(0, score_humidity_raw(rh) - penalty * 0.3),
                weight=PILLAR_WEIGHTS["humidity"],
                details=f"RH: {rh}% | PO: {_calc_dew_point(temp, rh):.1f}°C" if temp is not None and rh is not None else f"RH: {rh}%" if rh is not None else "N/A",
            ),
            "ventilation": PillarResult(
                score=max(0, score_co2(co2) - penalty * 0.2),
                weight=PILLAR_WEIGHTS["ventilation"],
                details=f"CO₂: {co2} ppm" if co2 is not None else "N/A",
            ),
            "materials": PillarResult(
                score=score_materials(moisture),
                weight=PILLAR_WEIGHTS["materials"],
                details=f"Humidade: {moisture}%" if moisture is not None else "N/A",
            ),
            "lighting": PillarResult(
                score=score_lighting(lux),
                weight=PILLAR_WEIGHTS["lighting"],
                details=f"Lux: {lux}" if lux is not None else "N/A",
            ),
            "visual": PillarResult(
                score=score_visual(obs, photo_count),
                weight=PILLAR_WEIGHTS["visual"],
                details=f"Observações: {'Sim' if obs else 'Nenhuma'}",
            ),
        }

        total_weight = sum(p.weight for p in pillars.values())
        weighted_sum = sum(p.score * p.weight for p in pillars.values())
        overall = round(weighted_sum / total_weight, 1) if total_weight > 0 else 0.0

        return pillars, overall, alerts

    def calculate_room(self, room_id: int, room_name: str, measurements: list[dict], photo_count: int = 0) -> RoomISAResult:
        result = RoomISAResult(room_id=room_id, room_name=room_name)

        if not measurements:
            result.overall_score = 0.0
            return result

        # Group measurements by sub_location
        groups: dict[str, list[dict]] = {}
        for m in measurements:
            loc = m.get("sub_location") or ""
            if loc not in groups:
                groups[loc] = []
            groups[loc].append(m)

        # Calculate ISA per sub_location
        loc_results = []
        for loc, ms in groups.items():
            pillars, overall, alerts = self._calculate_measurement_group(ms, photo_count)
            loc_label = loc if loc else "Geral"
            loc_result = SubLocationResult(
                sub_location=loc_label,
                pillars={k: PillarResult(score=v.score, weight=v.weight, details=v.details) for k, v in pillars.items()},
                overall_score=overall,
                alerts=alerts,
            )
            result.sub_locations[loc_label] = loc_result
            loc_results.append((loc_label, pillars, overall, alerts))
            result.alerts.extend(alerts)

        # Average all sub_locations for the room-level ISA
        if loc_results:
            # Average each pillar across sub_locations
            avg_pillars: dict[str, list[float]] = {}
            for _, pillars, _, _ in loc_results:
                for pk, pv in pillars.items():
                    if pk not in avg_pillars:
                        avg_pillars[pk] = []
                    avg_pillars[pk].append(pv.score)

            result.pillars = {}
            for pk, scores in avg_pillars.items():
                avg_score = sum(scores) / len(scores)
                # Get details from first location
                first_details = loc_results[0][1][pk].details if loc_results else ""
                result.pillars[pk] = PillarResult(
                    score=round(avg_score, 1),
                    weight=PILLAR_WEIGHTS.get(pk, 1.0),
                    details=first_details,
                )

            total_weight = sum(p.weight for p in result.pillars.values())
            weighted_sum = sum(p.score * p.weight for p in result.pillars.values())
            result.overall_score = round(weighted_sum / total_weight, 1) if total_weight > 0 else 0.0

        else:
            result.overall_score = 0.0

        return result

    def calculate_inspection(self, rooms_data: list[dict]) -> dict:
        room_results = []
        for room in rooms_data:
            room_result = self.calculate_room(
                room_id=room["id"],
                room_name=room["name"],
                measurements=room.get("measurements", []),
                photo_count=len(room.get("photos", [])),
            )
            room_results.append(room_result)

        if not room_results:
            return {"overall_score": 0.0, "category": ISACategory.HIGH_RISK, "rooms": []}

        overall = round(
            sum(r.overall_score for r in room_results) / len(room_results), 1
        )

        return {
            "overall_score": overall,
            "category": score_to_category(overall),
            "rooms": [
                {
                    "room_id": r.room_id,
                    "room_name": r.room_name,
                    "overall_score": r.overall_score,
                    "category": r.category,
                    "pillars": {
                        k: {"score": v.score, "details": v.details}
                        for k, v in r.pillars.items()
                    },
                    "sub_locations": {
                        loc: {
                            "overall_score": sl.overall_score,
                            "pillars": {
                                pk: {"score": pv.score, "details": pv.details}
                                for pk, pv in sl.pillars.items()
                            },
                            "alerts": sl.alerts,
                        }
                        for loc, sl in r.sub_locations.items()
                    },
                    "alerts": r.alerts[:5],
                }
                for r in room_results
            ],
        }

    def calculate_by_room_type(self, rooms_data: list[dict]) -> dict:
        type_results: dict[str, list[dict]] = {}
        for room in rooms_data:
            rt = room.get("room_type", "other")
            if rt not in type_results:
                type_results[rt] = []
            room_result = self.calculate_room(
                room_id=room["id"],
                room_name=room["name"],
                measurements=room.get("measurements", []),
                photo_count=len(room.get("photos", [])),
            )
            type_results[rt].append({
                "room_id": room_result.room_id,
                "room_name": room_result.room_name,
                "overall_score": room_result.overall_score,
                "category": room_result.category,
                "pillars": {
                    k: {"score": v.score, "details": v.details}
                    for k, v in room_result.pillars.items()
                },
                "alerts": room_result.alerts[:5],
            })

        grouped = {}
        for rt, rooms in type_results.items():
            avg = round(sum(r["overall_score"] for r in rooms) / len(rooms), 1)
            grouped[rt] = {
                "average_score": avg,
                "category": score_to_category(avg),
                "rooms": rooms,
            }

        all_scores = [r["overall_score"] for rooms in type_results.values() for r in rooms]
        overall = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0.0

        return {
            "overall_score": overall,
            "category": score_to_category(overall),
            "by_type": grouped,
        }
