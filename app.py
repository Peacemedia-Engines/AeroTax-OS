"""
AeroTax OS Mobile Web Dashboard
Built with Streamlit for pure rule-evaluation tracking.
"""

import streamlit as st
from pydantic import BaseModel, Field, field_validator

# =====================================================================
# 1. CORE ARCHITECTURE & SCHEMAS (From your existing backend)
# =====================================================================
class FlightManifest(BaseModel):
    manifest_id: str = Field(..., pattern=r"^MNF-[0-9]{6}-[A-Z]{3,4}$")
    aircraft_max_takeoff_weight_kg: float = Field(..., gt=0)
    jurisdiction_waypoints: list[str] = Field(..., min_length=2)
    is_cabotage_applicable: bool

    @field_validator("jurisdiction_waypoints")
    @classmethod
    def validate_icao_codes(cls, v: list[str]) -> list[str]:
        for code in v:
            if len(code) != 4 or not code.isupper():
                raise ValueError(f"Invalid ICAO airport code: {code}")
        return v

class AeroTaxEngine:
    @staticmethod
    def calculate_structural_liability(manifest: FlightManifest) -> dict:
        base_rate = 150.00 if manifest.aircraft_max_takeoff_weight_kg > 40000 else 75.00
        sector_count = len(manifest.jurisdiction_waypoints) - 1
        subtotal = base_rate * sector_count
        tax_multiplier = 1.25 if manifest.is_cabotage_applicable else 1.00
        
        return {
            "manifest_id": manifest.manifest_id,
            "base_rate_usd": base_rate,
            "sectors_evaluated": sector_count,
            "calculated_liability_usd": round(subtotal * tax_multiplier, 2),
            "execution_strategy": "DETERMINISTIC_RULE_TREE_V1"
        }

# =====================================================================
# 2. STREAMLIT VISUAL UI LAYER
# =====================================================================
st.set_page_config(page_title="AeroTax OS Control Desk", layout="centered")

st.title("🛩️ AeroTax OS")
st.subheader("Deterministic Tax Control Control Desk")
st.markdown("---")

# UI Form Fields
st.sidebar.header("Manifest Ingress Parameters")
manifest_num = st.sidebar.text_input("Manifest ID", value="MNF-202606-LHR")
weight = st.sidebar.number_input("Max Takeoff Weight (KG)", value=41000.0, step=1000.0)
waypoints_raw = st.sidebar.text_input("Jurisdiction Waypoints (Comma Separated ICAO)", value="EGLL, LFPG, KJFK")
cabotage = st.sidebar.checkbox("Apply Cabotage Penalty Multiplier", value=False)

# Parse waypoints input string into a standard clean list
waypoints = [code.strip().upper() for code in waypoints_raw.split(",") if code.strip()]

if st.sidebar.button("Execute Compliance Verification", type="primary"):
    try:
        # 1. Run Data through Ingress Validation Schema
        validated_manifest = FlightManifest(
            manifest_id=manifest_num,
            aircraft_max_takeoff_weight_kg=weight,
            jurisdiction_waypoints=waypoints,
            is_cabotage_applicable=cabotage
        )
        
        # 2. Pass Validated Schema directly to the Pure Rule Engine
        metrics = AeroTaxEngine.calculate_structural_liability(validated_manifest)
        
        # 3. Render Visual Metric UI Blocks
        st.success("✅ Transaction Processing Complete. Execution Pathway Secure.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Calculated Corporate Liability", value=f"${metrics['calculated_liability_usd']} USD")
            st.metric(label="Evaluated Flight Sectors", value=f"{metrics['sectors_evaluated']} Segments")
        with col2:
            st.metric(label="Base System Frame Rate", value=f"${metrics['base_rate_usd']} USD")
            st.metric(label="Engine Strategy", value=metrics['execution_strategy'])
            
        # Display raw payload trace for verification logs
        st.json(metrics)
        
    except Exception as e:
        st.error(f"⚠️ Validation Isolation Breach: {str(e)}")
else:
    st.info("Awaiting structural manifest ingress submission from control sidebar.")
