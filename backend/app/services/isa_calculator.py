"""
ISA - Índice de Saúde Ambiental

Calculates a 0-100 score based on 6 pillars:
  1. Condições Térmicas (Thermal)       - Temperature
  2. Humidade e Condensação (Humidity)   - Relative Humidity + Surface Temp
  3. Ventilação (Ventilation)            - CO2
  4. Estado dos Materiais (Materials)    - Material Moisture
  5. Iluminação (Lighting)               - Illuminance (Lux)
  6. Evidências Visuais (Visual)        - Observations & Photos

Reference ranges (based on ASHRAE, ISO 7730, NBR 16401, NBR 5413, WHO):
"""

from dataclasses import dataclass, field

from app.utils.enums import ISACategory


@dataclass
class PillarResult:
    score: float
    weight: float = 1.0
    details: str = ""


@dataclass
class RoomISAResult:
    room_id: int
    room_name: str
    pillars: dict[str, PillarResult] = field(default_factory=dict)
    overall_score: float = 0.0

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
    """Maps a measurement to 0-100 using linear interpolation."""
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


def score_temperature(temp: float | None) -> float:
    """Pillar 1: Thermal Comfort — ideal 20-24°C, acceptable 18-26°C"""
    return _linear_score(temp, 20.0, 24.0, 10.0, 35.0)


def score_humidity(rh: float | None, surface_temp: float | None, air_temp: float | None) -> float:
    """Pillar 2: Humidity & Condensation risk — ideal 40-60% RH"""
    if rh is None:
        return 0.0
    rh_score = _linear_score(rh, 40.0, 60.0, 15.0, 90.0)
    condensation_penalty = 0.0
    if surface_temp is not None and air_temp is not None:
        temp_diff = air_temp - surface_temp
        if temp_diff > 5:
            condensation_penalty = min(50, (temp_diff - 5) * 10)
    return max(0, rh_score - condensation_penalty)


def score_co2(co2: float | None) -> float:
    """Pillar 3: Ventilation — ideal CO2 < 800 ppm (ASHRAE)"""
    if co2 is None:
        return 0.0
    if co2 <= 800:
        return 100.0
    if co2 >= 2000:
        return 0.0
    return ((2000 - co2) / (2000 - 800)) * 100


def score_materials(moisture: float | None) -> float:
    """Pillar 4: Material State — ideal moisture < 12% for drywall/wood"""
    if moisture is None:
        return 0.0
    if moisture <= 12:
        return 100.0
    if moisture >= 30:
        return 0.0
    return ((30 - moisture) / (30 - 12)) * 100


def score_lighting(lux: float | None) -> float:
    """Pillar 5: Lighting — ideal 300-750 lux for office/living (NBR 5413)"""
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
    """Pillar 6: Visual Evidence — penalize if issues are observed."""
    if not observations and photo_count == 0:
        return 100.0
    issues = [
        "mofo", "bolor", "infiltração", "trinca", "rachadura",
        "mancha", "umidade", "descolamento", "ferrugem", "mofo",
    ]
    score = 100.0
    if observations:
        obs_lower = observations.lower()
        found = sum(1 for word in issues if word in obs_lower)
        score -= found * 15
    return max(0, score)


class ISACalculator:
    """Computes the ISA score for a set of measurements."""

    def calculate_room(self, room_id: int, room_name: str, measurements: list[dict], photo_count: int = 0) -> RoomISAResult:
        result = RoomISAResult(room_id=room_id, room_name=room_name)

        if not measurements:
            result.overall_score = 0.0
            return result

        m = measurements[-1]
        temp = m.get("temperature")
        rh = m.get("relative_humidity")
        co2 = m.get("co2")
        surface_temp = m.get("surface_temperature")
        moisture = m.get("material_moisture")
        lux = m.get("illuminance")
        obs = m.get("observations")

        result.pillars["thermal"] = PillarResult(
            score=score_temperature(temp),
            weight=PILLAR_WEIGHTS["thermal"],
            details=f"Temp: {temp}°C" if temp is not None else "N/A",
        )
        result.pillars["humidity"] = PillarResult(
            score=score_humidity(rh, surface_temp, temp),
            weight=PILLAR_WEIGHTS["humidity"],
            details=f"RH: {rh}%" if rh is not None else "N/A",
        )
        result.pillars["ventilation"] = PillarResult(
            score=score_co2(co2),
            weight=PILLAR_WEIGHTS["ventilation"],
            details=f"CO₂: {co2} ppm" if co2 is not None else "N/A",
        )
        result.pillars["materials"] = PillarResult(
            score=score_materials(moisture),
            weight=PILLAR_WEIGHTS["materials"],
            details=f"Moisture: {moisture}%" if moisture is not None else "N/A",
        )
        result.pillars["lighting"] = PillarResult(
            score=score_lighting(lux),
            weight=PILLAR_WEIGHTS["lighting"],
            details=f"Lux: {lux}" if lux is not None else "N/A",
        )
        result.pillars["visual"] = PillarResult(
            score=score_visual(obs, photo_count),
            weight=PILLAR_WEIGHTS["visual"],
            details=f"Observations: {'Yes' if obs else 'None'}",
        )

        total_weight = sum(p.weight for p in result.pillars.values())
        weighted_sum = sum(p.score * p.weight for p in result.pillars.values())
        result.overall_score = round(weighted_sum / total_weight, 1) if total_weight > 0 else 0.0

        return result

    def calculate_inspection(self, rooms_data: list[dict]) -> dict:
        """Calculate overall inspection ISA from list of room results."""
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
                }
                for r in room_results
            ],
        }

    def calculate_by_room_type(self, rooms_data: list[dict]) -> dict:
        """Calculate ISA grouped by room type."""
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
