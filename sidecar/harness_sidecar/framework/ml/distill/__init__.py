"""Model distillation techniques.

Three families:
1. Response-based — student matches teacher soft outputs (KL)
2. Feature-based — student matches intermediate activations
3. Relation-based — student matches pairwise relations between samples
"""

from .techniques import (
    response_distill,
    feature_distill,
    relation_distill,
    list_techniques,
)
