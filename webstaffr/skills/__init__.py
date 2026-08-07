"""Impeccable Skills Pipeline - Python port of the Impeccable design system.

This module implements the 5-stage skill chain from impeccable.style:
1. Strategy - Industry-specific positioning and core angle
2. Copy - Persuasive headlines and messaging
3. Design - Psychological color selection and visual direction
4. Trust - Dynamic assembly of credibility signals
5. Conversion - CTA placement, urgency, and friction reduction

Each skill runs in succession, passing enriched context to the next.
The pipeline transforms raw intake data into strategically refined,
high-converting website content.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("webstaffr.skills")


class StrategySkill:
    """Stage 1: Determine industry-specific positioning and core angle.
    
    Analyzes the business type, target audience, and market position
    to establish a strategic foundation for all downstream decisions.
    """
    
    # Industry-specific positioning angles
    POSITIONING_MAP = {
        "HVAC": {
            "core_angle": "Comfort & Reliability",
            "emotional_hook": "Peace of mind when your home's comfort is at stake",
            "trust_drivers": ["24/7 availability", "Certified technicians", "Upfront pricing"],
            "color_psychology": {"hue": 210, "sat": 75, "light": 45},  # Trustworthy blue
        },
        "Plumber": {
            "core_angle": "Fast Response & Expert Fixes",
            "emotional_hook": "Don't let a plumbing disaster ruin your day",
            "trust_drivers": ["Licensed & insured", "Same-day service", "No surprise fees"],
            "color_psychology": {"hue": 200, "sat": 80, "light": 40},  # Professional blue
        },
        "Electrician": {
            "core_angle": "Safety & Precision",
            "emotional_hook": "Your family's safety depends on expert electrical work",
            "trust_drivers": ["Master electricians", "Code compliance", "Warranty protection"],
            "color_psychology": {"hue": 45, "sat": 90, "light": 50},  # Energy yellow/gold
        },
        "Roofing": {
            "core_angle": "Protection & Durability",
            "emotional_hook": "Your roof is your home's first line of defense",
            "trust_drivers": ["Lifetime warranties", "Storm response", "Free inspections"],
            "color_psychology": {"hue": 25, "sat": 70, "light": 45},  # Earthy terra cotta
        },
        "Landscaping": {
            "core_angle": "Beauty & Curb Appeal",
            "emotional_hook": "Transform your yard into a neighborhood showpiece",
            "trust_drivers": ["Design expertise", "Reliable maintenance", "Seasonal care"],
            "color_psychology": {"hue": 120, "sat": 60, "light": 40},  # Natural green
        },
        "Pest Control": {
            "core_angle": "Health & Hygiene",
            "emotional_hook": "Protect your family from harmful pests",
            "trust_drivers": ["EPA-certified treatments", "Pet-safe options", "Guaranteed results"],
            "color_psychology": {"hue": 150, "sat": 50, "light": 45},  # Clean teal
        },
        "Cleaning Services": {
            "core_angle": "Trust & Thoroughness",
            "emotional_hook": "Come home to a spotless house without lifting a finger",
            "trust_drivers": ["Background-checked staff", "Satisfaction guarantee", "Eco-friendly products"],
            "color_psychology": {"hue": 180, "sat": 40, "light": 60},  # Fresh cyan
        },
        "Water Damage Restoration": {
            "core_angle": "Emergency Response & Recovery",
            "emotional_hook": "Fast action prevents permanent damage",
            "trust_drivers": ["24/7 emergency line", "Insurance coordination", "IICRC certified"],
            "color_psychology": {"hue": 200, "sat": 70, "light": 50},  # Water blue
        },
        "Garage Door Repair": {
            "core_angle": "Security & Convenience",
            "emotional_hook": "A malfunctioning garage door is a security risk",
            "trust_drivers": ["Rapid response", "All brands serviced", "Safety inspections"],
            "color_psychology": {"hue": 25, "sat": 60, "light": 50},  # Reliable bronze
        },
        "Tree Service": {
            "core_angle": "Expert Care & Safety",
            "emotional_hook": "Professional tree care protects your property and family",
            "trust_drivers": ["ISA certified arborists", "Fully insured", "Equipment expertise"],
            "color_psychology": {"hue": 100, "sat": 55, "light": 35},  # Deep forest green
        },
        "Other": {
            "core_angle": "Quality & Dependability",
            "emotional_hook": "Professional service you can count on",
            "trust_drivers": ["Experienced professionals", "Customer-first approach", "Satisfaction guaranteed"],
            "color_psychology": {"hue": 215, "sat": 70, "light": 45},  # Neutral professional blue
        },
    }
    
    def run(self, site_data: dict) -> dict:
        """Execute strategy analysis and return positioning context."""
        industry = site_data.get("industry", "Other")
        normalized_industry = self._normalize_industry(industry)
        
        positioning = self.POSITIONING_MAP.get(normalized_industry, self.POSITIONING_MAP["Other"])
        
        return {
            "industry": normalized_industry,
            "core_angle": positioning["core_angle"],
            "emotional_hook": positioning["emotional_hook"],
            "trust_drivers": positioning["trust_drivers"],
            "palette_config": positioning["color_psychology"],
            "mode": "persuade",  # All local service sites are persuasion-mode
        }
    
    def _normalize_industry(self, industry: str) -> str:
        """Normalize industry name to match positioning map keys."""
        industry_lower = industry.lower()
        
        for key in self.POSITIONING_MAP.keys():
            if key.lower() == industry_lower or key.lower() in industry_lower:
                return key
        
        return "Other"


class CopySkill:
    """Stage 2: Generate persuasive headlines and messaging.
    
    Uses the strategy context to craft compelling copy that resonates
    with the target audience and drives action.
    """
    
    def run(self, site_data: dict, strategy: dict) -> dict:
        """Generate persuasive copy based on strategy context."""
        biz_name = site_data.get("biz_name", "Our Business")
        service_area = site_data.get("service_area", "your area")
        tagline = site_data.get("tagline", "")
        differentiator = site_data.get("differentiator", "")
        
        core_angle = strategy.get("core_angle", "Quality Service")
        emotional_hook = strategy.get("emotional_hook", "")
        
        # Generate hero headline using core angle
        hero_headline = f"{core_angle}-Driven {site_data.get('industry', 'Service')} Experts"
        
        # Generate hero subhead combining emotional hook and service area
        if emotional_hook:
            hero_subhead = f"{emotional_hook}. Serving {service_area} with pride."
        else:
            hero_subhead = f"Trusted {site_data.get('industry', 'service')} professionals in {service_area}."
        
        # Override with existing tagline if it's strong
        if tagline and len(tagline) > 10:
            hero_subhead = tagline
        
        return {
            "hero_headline": hero_headline,
            "hero_subhead": hero_subhead,
            "value_proposition": differentiator or f"Why {service_area} trusts {biz_name}",
            "cta_primary": f"Get Your Free Estimate",
            "cta_secondary": f"Call {site_data.get('phone', 'Us Today')}",
            "urgency_trigger": self._generate_urgency(strategy),
        }
    
    def _generate_urgency(self, strategy: dict) -> str:
        """Generate urgency trigger based on industry."""
        industry = strategy.get("industry", "Other")
        
        urgency_map = {
            "HVAC": "Limited availability this week - book now before the heat/cold hits!",
            "Plumber": "Emergency slots fill fast - don't wait until it's too late!",
            "Electrician": "Safety can't wait - schedule your inspection today!",
            "Roofing": "Storm season is coming - protect your home now!",
            "Water Damage Restoration": "Every hour counts - call within 24hrs for best outcomes!",
            "Other": "Schedule filling quickly - secure your spot today!",
        }
        
        return urgency_map.get(industry, urgency_map["Other"])


class DesignSkill:
    """Stage 3: Apply psychological color theory and visual direction.
    
    Selects colors and visual elements that resonate with the target
    audience and reinforce the brand positioning.
    """
    
    def run(self, site_data: dict, strategy: dict) -> dict:
        """Generate design configuration based on strategy."""
        palette_config = strategy.get("palette_config", {"hue": 215, "sat": 70, "light": 45})
        
        # Adjust based on any brand color preferences
        existing_colors = site_data.get("brand_colors")
        if existing_colors:
            # Keep user's choice but note it overrides psychology-based selection
            logger.info("User-specified brand color overrides psychology-based palette")
            palette_config["user_override"] = True
        
        return {
            "palette_config": palette_config,
            "typography_mood": self._get_typography_mood(strategy),
            "visual_density": "medium",  # Balanced density for trust
            "image_style": "authentic",  # Real photos over stock
            "component_radius": "6px",  # Slightly rounded for friendliness
            "shadow_depth": "subtle",  # Minimal shadows for professionalism
        }
    
    def _get_typography_mood(self, strategy: dict) -> str:
        """Determine typography mood based on industry."""
        industry = strategy.get("industry", "Other")
        
        if industry in ["HVAC", "Plumber", "Electrician"]:
            return "confident-sans"  # Clean, authoritative sans-serif
        elif industry in ["Landscaping", "Tree Service"]:
            return "natural-serif"  # Warm, organic feel
        elif industry in ["Cleaning Services", "Pest Control"]:
            return "clean-modern"  # Crisp, hygienic appearance
        else:
            return "professional-mixed"  # Balanced approach


class TrustSkill:
    """Stage 4: Assemble dynamic trust signals.
    
    Curates credibility elements (reviews, certifications, guarantees)
    based on what the business has provided and what matters most in
    their industry.
    """
    
    def run(self, site_data: dict, strategy: dict) -> dict:
        """Build trust signal configuration."""
        trust_drivers = strategy.get("trust_drivers", [])
        has_reviews = bool(site_data.get("rating_value") and site_data.get("review_count"))
        
        signals = []
        
        # Add reviews if available
        if has_reviews:
            rating = site_data.get("rating_value", 5.0)
            count = site_data.get("review_count", 0)
            signals.append({
                "type": "rating",
                "icon": "⭐",
                "text": f"{rating} / 5 — {count}+ Reviews",
                "priority": 1,
            })
        
        # Add industry-specific trust drivers
        for i, driver in enumerate(trust_drivers[:3]):  # Top 3 only
            icon = self._get_trust_icon(driver)
            signals.append({
                "type": "credential",
                "icon": icon,
                "text": driver,
                "priority": i + 2,
            })
        
        # Add guarantee if differentiator mentions it
        differentiator = site_data.get("differentiator", "").lower()
        if "guarantee" in differentiator or "satisfaction" in differentiator:
            signals.append({
                "type": "guarantee",
                "icon": "✅",
                "text": "100% Satisfaction Guarantee",
                "priority": 5,
            })
        
        return {
            "signals": signals,
            "show_badge_grid": len(signals) >= 3,
            "trust_headline": f"Why {site_data.get('service_area', 'Customers')} Trust {site_data.get('biz_name', 'Us')}",
        }
    
    def _get_trust_icon(self, driver: str) -> str:
        """Map trust driver to emoji icon."""
        icon_map = {
            "24/7": "⚡",
            "certified": "🛡️",
            "licensed": "📜",
            "insured": "🛡️",
            "warranty": "✅",
            "emergency": "🚨",
            "same-day": "⚡",
            "free": "🎁",
        }
        
        driver_lower = driver.lower()
        for key, icon in icon_map.items():
            if key in driver_lower:
                return icon
        
        return "✓"


class ConversionSkill:
    """Stage 5: Optimize for conversions.
    
    Applies conversion rate optimization principles to form placement,
    CTA strategy, and friction reduction.
    """
    
    def run(self, site_data: dict, strategy: dict, copy_data: dict) -> dict:
        """Generate conversion optimization configuration."""
        industry = strategy.get("industry", "Other")
        
        # Determine optimal form position
        form_position = self._determine_form_position(industry, strategy)
        
        # CTA configuration
        sticky_cta = industry in ["HVAC", "Plumber", "Electrician", "Water Damage Restoration"]
        
        return {
            "form_position": form_position,
            "sticky_cta": sticky_cta,
            "form_fields": self._optimize_form_fields(industry),
            "social_proof_placement": "adjacent-to-form",
            "urgency_display": "banner",
            "friction_reducers": [
                "No obligation",
                "Free estimate",
                "Response within 24 hours",
            ],
        }
    
    def _determine_form_position(self, industry: str, strategy: dict) -> str:
        """Determine optimal form position based on urgency."""
        high_urgency = ["HVAC", "Plumber", "Electrician", "Water Damage Restoration", "Pest Control"]
        
        if industry in high_urgency:
            return "above-fold"  # Immediate action for emergencies
        else:
            return "mid-page"  # Considered decision for non-urgent services
    
    def _optimize_form_fields(self, industry: str) -> list[str]:
        """Minimize form fields to reduce friction."""
        base_fields = ["name", "phone", "email", "message"]
        
        # For high-urgency industries, make phone required and prominent
        if industry in ["HVAC", "Plumber", "Electrician", "Water Damage Restoration"]:
            return ["phone", "name", "message"]  # Phone first, email optional
        
        return base_fields


class ImpeccablePipeline:
    """Orchestrates the 5-stage Impeccable skills pipeline.
    
    Runs each skill in succession, passing enriched context downstream.
    The final output contains strategically refined website content
    ready for rendering.
    """
    
    def __init__(self):
        self.strategy = StrategySkill()
        self.copy = CopySkill()
        self.design = DesignSkill()
        self.trust = TrustSkill()
        self.conversion = ConversionSkill()
    
    def run(self, site_data: dict) -> dict:
        """Execute the full skills pipeline and return enriched context.
        
        Args:
            site_data: Raw site data from intake form
            
        Returns:
            Enriched context dictionary with strategy, copy, design,
            trust, and conversion configurations
        """
        logger.info(f"Running Impeccable pipeline for {site_data.get('biz_name', 'Unknown')}")
        
        # Stage 1: Strategy
        strategy_context = self.strategy.run(site_data)
        logger.debug(f"Strategy determined: {strategy_context.get('core_angle')}")
        
        # Stage 2: Copy (depends on Strategy)
        copy_context = self.copy.run(site_data, strategy_context)
        logger.debug(f"Generated headline: {copy_context.get('hero_headline')}")
        
        # Stage 3: Design (depends on Strategy)
        design_context = self.design.run(site_data, strategy_context)
        logger.debug(f"Palette config: hue={design_context['palette_config'].get('hue')}")
        
        # Stage 4: Trust (depends on Strategy + site data)
        trust_context = self.trust.run(site_data, strategy_context)
        logger.debug(f"Assembled {len(trust_context.get('signals', []))} trust signals")
        
        # Stage 5: Conversion (depends on Strategy + Copy)
        conversion_context = self.conversion.run(site_data, strategy_context, copy_context)
        logger.debug(f"Form position: {conversion_context.get('form_position')}")
        
        return {
            "strategy": strategy_context,
            "copy": copy_context,
            "design": design_context,
            "trust": trust_context,
            "conversion": conversion_context,
        }


# Export for use in site_renderer.py
__all__ = ["ImpeccablePipeline", "StrategySkill", "CopySkill", "DesignSkill", "TrustSkill", "ConversionSkill"]
