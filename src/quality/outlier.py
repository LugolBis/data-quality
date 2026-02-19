import pandas as pd
from typing import Any, Optional
from collections import defaultdict
from driver.neo4j_driver import Neo4jSession
from utils.utils import logger
from quality.types import NumericalOutlier, OutlierDetail

def detecter_outliers_numeriques(
    session: Neo4jSession, z_score_threshold: float = 1.96
) -> Optional[list[NumericalOutlier]]:
    """
    [Numerical Outliers] 
    Calculer la moyenne, l'écart-type et l'intervalle de confiance.
    """
    query = "MATCH (n) RETURN elementId(n) as ID, labels(n) as Labels, properties(n) as Props"
    
    try:
        result = session.run_query(query)
        nodes: list[dict[str, Any]] = [record.data() for record in result]
    except Exception as e:
        logger.error(f"Error fetching nodes for outliers: {e}")
        return None

    groups = defaultdict(list)
    for node in nodes:
        label_key = "&".join(sorted(node["Labels"]))
        groups[label_key].append(node)

    detected_outliers: list[NumericalOutlier] = []

    for label_str, group_nodes in groups.items():
        numeric_data = defaultdict(dict)
        
        for node in group_nodes:
            node_id = node["ID"]
            for key, val in node["Props"].items():
                if isinstance(val, (int, float)) and not isinstance(val, bool):
                    numeric_data[key][node_id] = val

        for prop, values_dict in numeric_data.items():
            if len(values_dict) < 3:
                continue
            
            s = pd.Series(values_dict)
            moyenne = float(s.mean())
            ecart_type = float(s.std())

            if pd.isna(ecart_type) or ecart_type == 0:
                continue

            lower_bound = moyenne - (z_score_threshold * ecart_type)
            upper_bound = moyenne + (z_score_threshold * ecart_type)

            outliers = s[(s < lower_bound) | (s > upper_bound)]

            if not outliers.empty:
                details = [
                    OutlierDetail(node_id=str(out_id), value=float(out_val)) 
                    for out_id, out_val in outliers.items()
                ]
                
                detected_outliers.append(
                    NumericalOutlier(
                        label=label_str,
                        property=prop,
                        mean=moyenne,
                        std_dev=ecart_type,
                        lower_bound=lower_bound,
                        upper_bound=upper_bound,
                        outliers=details
                    )
                )

    return detected_outliers if detected_outliers else None
