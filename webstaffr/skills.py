"""
Impeccable Skills Pipeline
Applies strategic refinement steps in succession to transform raw tenant data 
into a high-converting, psychologically optimized website context.
"""
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class ImpeccableSkill:
    """Base class for all Impeccable skills."""
    
    def __init__(self):
        self.name = "BaseSkill"
    
    def apply(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply the skill to the context and return the enhanced context."""
        raise NotImplementedError


class StrategySkill(ImpeccableSkill):
    """
    Skill 1: Market Positioning & Strategy
    Defines the core value proposition, target audience, and differentiators.
    """
    def __init__(self):
        self.name = "Strategy"
    
    def apply(self, context: Dict[str, Any]) -> Dict[str, Any]:
        business = context.get('business', {}) or context  # Support both nested and flat structures
        industry_raw = business.get('industry', 'General')
        # Normalize industry for matching (handle "HVAC", "hvac", "Heating & Cooling", etc.)
        industry_lower = industry_raw.lower()
        
        # Define strategic positioning based on industry
        if 'hvac' in industry_lower or 'heating' in industry_lower or 'cooling' in industry_lower or 'air conditioning' in industry_lower:
            strategy = {
                'angle': 'Comfort & Reliability',
                'differentiator': '24/7 Emergency Response & NATE Certified Techs',
                'tone': 'Professional, Reassuring, Urgent',
                'cta_focus': 'Immediate Service Booking'
            }
        elif 'plumb' in industry_lower:
            strategy = {
                'angle': 'Speed & Integrity',
                'differentiator': 'Upfront Pricing & No-Mess Guarantee',
                'tone': 'Direct, Honest, Efficient',
                'cta_focus': 'Fast Quote Request'
            }
        elif 'legal' in industry_lower or 'law' in industry_lower or 'attorney' in industry_lower:
            strategy = {
                'angle': 'Justice & Results',
                'differentiator': 'No Win No Fee & Decades of Courtroom Experience',
                'tone': 'Authoritative, Empathetic, Aggressive',
                'cta_focus': 'Free Case Evaluation'
            }
        else:
            strategy = {
                'angle': 'Quality & Trust',
                'differentiator': 'Local Expertise & Verified Reviews',
                'tone': 'Friendly, Professional, Reliable',
                'cta_focus': 'Contact Us Today'
            }
        
        # Inject strategy into context
        context['strategy'] = {
            'core_angle': strategy['angle'],
            'unique_value_prop': strategy['differentiator'],
            'brand_tone': strategy['tone'],
            'primary_goal': strategy['cta_focus'],
            'target_audience': f"Homeowners and businesses in {business.get('city', 'the area')} seeking reliable {industry_raw} services."
        }
        
        logger.info(f"[Strategy] Applied angle: {strategy['angle']}")
        return context


class CopySkill(ImpeccableSkill):
    """
    Skill 2: Persuasive Copywriting
    Generates headlines, subheads, and body copy based on the strategy.
    """
    def __init__(self):
        self.name = "Copy"
    
    def apply(self, context: Dict[str, Any]) -> Dict[str, Any]:
        strategy = context.get('strategy', {})
        business = context.get('business', {})
        name = business.get('name', 'Our Business')
        angle = strategy.get('core_angle', 'Quality')
        uvp = strategy.get('unique_value_prop', '')
        
        # Generate compelling headlines
        context['copy'] = {
            'hero_headline': f"{angle}-Driven {business.get('industry', 'Services')} in {business.get('city', 'Your Area')}",
            'hero_subhead': f"Experience the {name} difference. {uvp}.",
            'about_headline': f"Why Local Clients Trust {name}",
            'services_headline': 'Comprehensive Solutions for Your Needs',
            'testimonials_headline': 'Don\'t Just Take Our Word For It',
            'cta_text': 'Get Your Free Quote',
            'emergency_banner': f"Need Help Now? {uvp.split('&')[0].strip()}" if 'Emergency' in uvp else None
        }
        
        logger.info(f"[Copy] Generated headline: {context['copy']['hero_headline']}")
        return context


class DesignSkill(ImpeccableSkill):
    """
    Skill 3: Psychological Design & Color Theory
    Selects color palettes and layout structures that evoke the right emotions.
    """
    def __init__(self):
        self.name = "Design"
    
    def apply(self, context: Dict[str, Any]) -> Dict[str, Any]:
        strategy = context.get('strategy', {})
        tone = strategy.get('brand_tone', 'Professional')
        industry = context.get('business', {}).get('industry', '').lower()
        
        # Map tone/industry to color psychology
        palette_map = {
            'hvac': {'base_hue': 210, 'sat': 85, 'light': 55}, # Trustworthy Blue
            'plumbing': {'base_hue': 200, 'sat': 70, 'light': 45}, # Clean Water Blue
            'legal': {'base_hue': 220, 'sat': 60, 'light': 35}, # Authoritative Navy
            'medical': {'base_hue': 160, 'sat': 60, 'light': 45}, # Calming Teal
            'default': {'base_hue': 215, 'sat': 75, 'light': 50} # Balanced Blue
        }
        
        colors = palette_map.get(industry, palette_map['default'])
        
        context['design'] = {
            'palette_config': colors,
            'layout_style': 'clean-grid' if 'Professional' in tone else 'bold-impact',
            'typography_pair': 'modern-sans' if 'Efficient' in tone else 'classic-serif',
            'visual_weight': 'high' if 'Urgent' in tone else 'balanced'
        }
        
        logger.info(f"[Design] Selected palette hue: {colors['base_hue']}")
        return context


class TrustSkill(ImpeccableSkill):
    """
    Skill 4: Dynamic Trust Signals
    Identifies and prioritizes social proof, credentials, and guarantees.
    """
    def __init__(self):
        self.name = "Trust"
    
    def apply(self, context: Dict[str, Any]) -> Dict[str, Any]:
        intake = context.get('intake', {})
        reviews = intake.get('reviews', [])
        licenses = intake.get('licenses', [])
        years_in_business = intake.get('years_in_business', 0)
        
        trust_signals = []
        
        # Add review signal if available
        if reviews and len(reviews) > 0:
            avg_rating = sum(r.get('rating', 5) for r in reviews) / len(reviews)
            trust_signals.append({
                'type': 'rating',
                'icon': '⭐',
                'text': f"{avg_rating:.1f} / 5 — {len(reviews)}+ Reviews",
                'priority': 1
            })
        
        # Add credential signal
        if licenses:
            trust_signals.append({
                'type': 'credential',
                'icon': '🛡️',
                'text': f"Licensed & Insured ({', '.join(licenses[:2])})",
                'priority': 2
            })
        elif years_in_business > 5:
            trust_signals.append({
                'type': 'experience',
                'icon': '🏆',
                'text': f"Serving the Community for {years_in_business}+ Years",
                'priority': 2
            })
        
        # Add guarantee signal (hardcoded for demo richness)
        trust_signals.append({
            'type': 'guarantee',
            'icon': '✅',
            'text': '100% Satisfaction Guaranteed',
            'priority': 3
        })
        
        # Sort by priority
        trust_signals.sort(key=lambda x: x['priority'])
        
        context['trust'] = {
            'signals': trust_signals,
            'show_badge_grid': len(trust_signals) >= 2,
            'primary_proof': trust_signals[0]['text'] if trust_signals else 'Trusted Local Expert'
        }
        
        logger.info(f"[Trust] Assembled {len(trust_signals)} trust signals")
        return context


class ConversionSkill(ImpeccableSkill):
    """
    Skill 5: Conversion Optimization
    Optimizes form placement, CTA wording, and friction reduction.
    """
    def __init__(self):
        self.name = "Conversion"
    
    def apply(self, context: Dict[str, Any]) -> Dict[str, Any]:
        strategy = context.get('strategy', {})
        
        context['conversion'] = {
            'form_position': 'above-fold', # Always visible
            'form_fields': ['name', 'phone', 'service_needed'], # Minimal friction
            'cta_color': 'high-contrast', # Ensures visibility
            'sticky_cta': True, # Mobile optimization
            'urgency_trigger': 'Limited Availability Today' if 'Urgent' in strategy.get('brand_tone', '') else None,
            'guarantee_near_cta': True
        }
        
        logger.info("[Conversion] Optimized form and CTA placement")
        return context


class ImpeccablePipeline:
    """
    Executes the full chain of skills in succession.
    Order: Strategy → Copy → Design → Trust → Conversion
    """
    
    def __init__(self):
        self.skills = [
            StrategySkill(),
            CopySkill(),
            DesignSkill(),
            TrustSkill(),
            ConversionSkill()
        ]
    
    def run(self, raw_context: Dict[str, Any]) -> Dict[str, Any]:
        """Run all skills in sequence, passing the enriched context forward."""
        context = raw_context.copy()
        
        logger.info("Starting Impeccable Skill Pipeline...")
        
        for skill in self.skills:
            try:
                context = skill.apply(context)
            except Exception as e:
                logger.error(f"Error in {skill.name} skill: {str(e)}")
                # Continue with partial context rather than failing completely
        
        logger.info("Impeccable Skill Pipeline complete.")
        return context
