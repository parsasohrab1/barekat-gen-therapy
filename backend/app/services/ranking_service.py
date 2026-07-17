"""Multi-criteria candidate ranking."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RankingWeights:
    efficacy: float = 0.4
    safety: float = 0.3
    synthesizability: float = 0.2
    cost: float = 0.1

    def normalized(self) -> RankingWeights:
        total = self.efficacy + self.safety + self.synthesizability + self.cost
        if total <= 0:
            return RankingWeights()
        return RankingWeights(
            efficacy=self.efficacy / total,
            safety=self.safety / total,
            synthesizability=self.synthesizability / total,
            cost=self.cost / total,
        )


class RankingService:
    def rank_candidates(
        self,
        candidates: list[dict],
        weights: RankingWeights,
        only_synthesizable: bool = True,
    ) -> list[dict]:
        w = weights.normalized()
        ranked: list[dict] = []

        for candidate in candidates:
            if only_synthesizable and not candidate.get("synthesizable", True):
                continue

            efficacy = float(candidate.get("efficacy_score", 0.5))
            safety = float(candidate.get("safety_score", 0.5))
            synth = float(candidate.get("synthesizability_score", 0.5))
            cost = float(candidate.get("cost_score", 0.5))

            final_score = (
                w.efficacy * efficacy
                + w.safety * safety
                + w.synthesizability * synth
                + w.cost * cost
            )

            ranked.append(
                {
                    **candidate,
                    "final_score": round(final_score, 4),
                    "score_breakdown": {
                        "efficacy": round(w.efficacy * efficacy, 4),
                        "safety": round(w.safety * safety, 4),
                        "synthesizability": round(w.synthesizability * synth, 4),
                        "cost": round(w.cost * cost, 4),
                    },
                    "weights_used": {
                        "efficacy": w.efficacy,
                        "safety": w.safety,
                        "synthesizability": w.synthesizability,
                        "cost": w.cost,
                    },
                }
            )

        ranked.sort(key=lambda x: x["final_score"], reverse=True)
        for i, item in enumerate(ranked, start=1):
            item["rank"] = i
        return ranked
