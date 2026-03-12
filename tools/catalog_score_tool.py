"""Ticket 20 — Composite AI Catalog Score (SEO + taxonomy + attributes)."""
from tools.base import BaseTool, ToolInput, ToolOutput
from tools.registry import register
from evaluation.seo_eval import score_seo_title

class CatalogScoreInput(ToolInput):
    product_name: str
    seo_name: str = ""
    taxonomy_confidence: float = 0.0
    attribute_completeness: float = 0.0

class CatalogScoreOutput(ToolOutput):
    seo_score: float
    taxonomy_score: float
    attribute_score: float
    overall_score: float
    grade: str

_GRADES = [(0.85,"A"),(0.70,"B"),(0.55,"C"),(0.40,"D")]
def _grade(s: float) -> str:
    for t, g in _GRADES:
        if s >= t: return g
    return "F"

class CatalogScoreTool(BaseTool):
    name = "catalog_score"
    description = "Composite product quality score: SEO + taxonomy confidence + attribute completeness"
    input_model = CatalogScoreInput
    output_model = CatalogScoreOutput

    async def execute(self, input: CatalogScoreInput) -> CatalogScoreOutput:
        seo_s  = score_seo_title(input.product_name, input.seo_name or input.product_name)["score"]
        tax_s  = min(max(input.taxonomy_confidence,    0.0), 1.0)
        attr_s = min(max(input.attribute_completeness, 0.0), 1.0)
        overall = round((seo_s + tax_s + attr_s) / 3, 3)
        return CatalogScoreOutput(
            seo_score=round(seo_s,3), taxonomy_score=round(tax_s,3),
            attribute_score=round(attr_s,3), overall_score=overall, grade=_grade(overall),
        )

catalog_score_tool = CatalogScoreTool()
register(catalog_score_tool)