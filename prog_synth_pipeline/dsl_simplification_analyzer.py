import json
import re
import os
from typing import Dict, List, Any, Set
from dataclasses import dataclass
from collections import Counter

@dataclass
class DSLConstruct:
    """Represents a construct in the DSL"""
    name: str
    definition: str
    usage_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    examples: List[str] = None
    
    @property
    def success_rate(self) -> float:
        if self.usage_count == 0:
            return 0.0
        return self.success_count / self.usage_count
    
    @property
    def is_problematic(self) -> bool:
        return self.usage_count > 5 and self.success_rate < 0.3
    
    @property
    def is_unused(self) -> bool:
        return self.usage_count == 0

class DSLSimplificationAnalyzer:
    def __init__(self):
        self.constructs = {}
        self.program_patterns = []
        
    def analyze_dsl_grammar(self, dsl_text: str) -> Dict[str, DSLConstruct]:
        """Parse DSL grammar and extract all constructs"""
        constructs = {}
        
        # Extract function definitions
        func_patterns = [
            (r'(\w+_FUNC)\s*::=', 'function'),
            (r'(UP|DOWN|LEFT|RIGHT)', 'direction'),
            (r'(ROPE|KNIFE|SLINGSHOT|ARROW|GOLDARROW)', 'item'),
            (r'(BOUNDARY|WATER|STONE|WORKSHOP\d+|WOOD|IRON|GRASS|ROCK|GOLD|GEM)', 'primitive'),
            (r'(if|HAS|then|SEMI)', 'keyword')
        ]
        
        lines = dsl_text.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            for pattern, construct_type in func_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    if match not in constructs:
                        constructs[match] = DSLConstruct(
                            name=match,
                            definition=f"Line {i+1}: {line}",
                            examples=[]
                        )
        
        return constructs
    
    def analyze_program_usage(self, programs: List[str], success_flags: List[bool]) -> Dict[str, DSLConstruct]:
        """Analyze how constructs are used in actual programs"""
        
        for program, success in zip(programs, success_flags):
            # Extract all constructs from program
            program_constructs = self.extract_constructs_from_program(program)
            
            for construct_name in program_constructs:
                if construct_name not in self.constructs:
                    # Add new construct found in programs
                    self.constructs[construct_name] = DSLConstruct(
                        name=construct_name,
                        definition="Found in program usage",
                        examples=[]
                    )
                
                construct = self.constructs[construct_name]
                construct.usage_count += 1
                
                if success:
                    construct.success_count += 1
                else:
                    construct.failure_count += 1
                
                # Add example (limit to 3)
                if len(construct.examples) < 3:
                    construct.examples.append(program[:100] + "..." if len(program) > 100 else program)
        
        return self.constructs
    
    def extract_constructs_from_program(self, program: str) -> Set[str]:
        """Extract all constructs used in a program"""
        constructs = set()
        
        # Extract function calls
        func_calls = re.findall(r'(\w+_FUNC)\([^)]*\)', program)
        constructs.update(func_calls)
        
        # Extract keywords and other constructs
        keywords = re.findall(r'\b(if|HAS|then|SEMI|UP|DOWN|LEFT|RIGHT)\b', program)
        constructs.update(keywords)
        
        # Extract items and primitives
        items = re.findall(r'\b(ROPE|KNIFE|SLINGSHOT|ARROW|GOLDARROW)\b', program)
        constructs.update(items)
        
        primitives = re.findall(r'\b(BOUNDARY|WATER|STONE|WORKSHOP\d+|WOOD|IRON|GRASS|ROCK|GOLD|GEM)\b', program)
        constructs.update(primitives)
        
        return constructs
    
    def identify_redundant_patterns(self, programs: List[str]) -> List[Dict[str, Any]]:
        """Identify redundant patterns in programs"""
        redundant_patterns = []
        
        # Common redundant patterns
        pattern_definitions = [
            {
                'name': 'repeated_moves',
                'pattern': r'(MOVE_FUNC\([^)]+\);\s*){3,}',
                'description': 'Multiple consecutive moves',
                'suggestion': 'Replace with NAVIGATE_FUNC(target)',
                'complexity_reduction': 'high'
            },
            {
                'name': 'repeated_collects',
                'pattern': r'(COLLECT_FUNC\([^)]+\);\s*){3,}',
                'description': 'Multiple consecutive collects',
                'suggestion': 'Replace with COLLECT_MULTI_FUNC(items)',
                'complexity_reduction': 'medium'
            },
            {
                'name': 'conditional_crafting',
                'pattern': r'if HAS\([^)]+\) then CRAFT_FUNC\([^)]+\)',
                'description': 'Conditional crafting with explicit checks',
                'suggestion': 'Remove conditional, make dependencies explicit in recipes',
                'complexity_reduction': 'high'
            },
            {
                'name': 'unnecessary_semicolons',
                'pattern': r';\s*;',
                'description': 'Multiple consecutive semicolons',
                'suggestion': 'Use single semicolon',
                'complexity_reduction': 'low'
            }
        ]
        
        for pattern_def in pattern_definitions:
            count = 0
            examples = []
            
            for program in programs:
                matches = re.findall(pattern_def['pattern'], program)
                if matches:
                    count += len(matches)
                    if len(examples) < 2:
                        examples.append(program[:100] + "..." if len(program) > 100 else program)
            
            if count > 0:
                redundant_patterns.append({
                    'name': pattern_def['name'],
                    'description': pattern_def['description'],
                    'occurrence_count': count,
                    'suggestion': pattern_def['suggestion'],
                    'complexity_reduction': pattern_def['complexity_reduction'],
                    'examples': examples
                })
        
        return redundant_patterns
    
    def generate_simplification_report(self, dsl_text: str, programs: List[str], 
                                     success_flags: List[bool]) -> Dict[str, Any]:
        """Generate a comprehensive DSL simplification report"""
        
        # Analyze DSL grammar
        dsl_constructs = self.analyze_dsl_grammar(dsl_text)
        self.constructs.update(dsl_constructs)
        
        # Analyze program usage
        usage_analysis = self.analyze_program_usage(programs, success_flags)
        
        # Identify redundant patterns
        redundant_patterns = self.identify_redundant_patterns(programs)
        
        # Categorize constructs
        unused_constructs = [c for c in self.constructs.values() if c.is_unused]
        problematic_constructs = [c for c in self.constructs.values() if c.is_problematic]
        well_used_constructs = [c for c in self.constructs.values() 
                              if not c.is_unused and not c.is_problematic and c.usage_count > 0]
        
        # Generate simplification suggestions
        suggestions = self.generate_simplification_suggestions(
            unused_constructs, problematic_constructs, redundant_patterns
        )
        
        # Create simplified DSL
        simplified_dsl = self.create_simplified_dsl(dsl_text, unused_constructs, problematic_constructs)
        
        return {
            "analysis_summary": {
                "total_constructs": len(self.constructs),
                "unused_constructs": len(unused_constructs),
                "problematic_constructs": len(problematic_constructs),
                "well_used_constructs": len(well_used_constructs),
                "redundant_patterns": len(redundant_patterns),
                "overall_success_rate": sum(1 for flag in success_flags if flag) / len(success_flags) if success_flags else 0
            },
            "unused_constructs": [
                {
                    "name": c.name,
                    "definition": c.definition,
                    "reason": "Never used in any program"
                } for c in unused_constructs
            ],
            "problematic_constructs": [
                {
                    "name": c.name,
                    "usage_count": c.usage_count,
                    "success_rate": c.success_rate,
                    "examples": c.examples,
                    "suggestion": self.get_construct_suggestion(c)
                } for c in problematic_constructs
            ],
            "redundant_patterns": redundant_patterns,
            "simplification_suggestions": suggestions,
            "simplified_dsl": simplified_dsl,
            "expected_impact": self.calculate_expected_impact(
                unused_constructs, problematic_constructs, redundant_patterns
            )
        }
    
    def generate_simplification_suggestions(self, unused: List[DSLConstruct], 
                                          problematic: List[DSLConstruct],
                                          redundant: List[Dict]) -> Dict[str, List[Dict]]:
        """Generate specific simplification suggestions"""
        
        suggestions = {
            "removals": [],
            "replacements": [],
            "simplifications": []
        }
        
        # Removal suggestions
        for construct in unused:
            suggestions["removals"].append({
                "construct": construct.name,
                "action": "REMOVE",
                "reason": "Never used in any program",
                "impact": "Reduces DSL complexity without affecting functionality",
                "definition": construct.definition
            })
        
        # Problematic construct suggestions
        for construct in problematic:
            suggestions["simplifications"].append({
                "construct": construct.name,
                "action": "SIMPLIFY",
                "reason": f"Low success rate ({construct.success_rate:.1%}) despite {construct.usage_count} uses",
                "suggestion": self.get_construct_suggestion(construct),
                "impact": "Should improve synthesis success rate"
            })
        
        # Redundant pattern suggestions
        for pattern in redundant:
            suggestions["replacements"].append({
                "pattern": pattern["name"],
                "action": "REPLACE",
                "description": pattern["description"],
                "occurrences": pattern["occurrence_count"],
                "suggestion": pattern["suggestion"],
                "impact": f"Simplifies {pattern['occurrence_count']} programs"
            })
        
        return suggestions
    
    def get_construct_suggestion(self, construct: DSLConstruct) -> str:
        """Get improvement suggestion for a construct"""
        suggestions = {
            'if HAS': 'Remove conditional checks, make dependencies explicit in recipes',
            'then': 'Simplify to direct function calls',
            'MOVE_FUNC': 'Add navigation functions for common movement patterns',
            'CRAFT_FUNC': 'Add automatic dependency resolution',
            'COLLECT_FUNC': 'Add resource location hints or automatic pathfinding',
            'SEMI': 'Consider removing explicit semicolons, use newlines instead'
        }
        
        return suggestions.get(construct.name, 'Consider simplifying or removing this construct')
    
    def create_simplified_dsl(self, original_dsl: str, unused: List[DSLConstruct], 
                            problematic: List[DSLConstruct]) -> str:
        """Create a simplified version of the DSL"""
        
        # Start with original DSL
        simplified_lines = original_dsl.split('\n')
        
        # Remove lines containing unused constructs
        constructs_to_remove = {c.name for c in unused}
        
        filtered_lines = []
        for line in simplified_lines:
            should_keep = True
            for construct in constructs_to_remove:
                if construct in line:
                    should_keep = False
                    break
            if should_keep:
                filtered_lines.append(line)
        
        # Add simplification comments
        simplified_dsl = "# SIMPLIFIED DSL - Removed unused constructs\n"
        simplified_dsl += "# Removed constructs: " + ", ".join([c.name for c in unused]) + "\n\n"
        simplified_dsl += "\n".join(filtered_lines)
        
        return simplified_dsl
    
    def calculate_expected_impact(self, unused: List[DSLConstruct], 
                                problematic: List[DSLConstruct],
                                redundant: List[Dict]) -> Dict[str, str]:
        """Calculate expected impact of simplifications"""
        
        total_removals = len(unused)
        total_simplifications = len(problematic)
        total_replacements = len(redundant)
        
        complexity_reduction = total_removals + total_replacements
        failure_reduction = total_simplifications
        
        return {
            "complexity_reduction": f"{complexity_reduction} constructs simplified/removed",
            "failure_reduction": f"{failure_reduction} problematic constructs addressed",
            "overall_improvement": "Simplified DSL should lead to higher synthesis success rates",
            "estimated_success_rate_improvement": f"{failure_reduction * 0.1:.1%} - {failure_reduction * 0.2:.1%}"
        }

def main():
    """Example usage of the DSL simplification analyzer"""
    
    # Example DSL
    example_dsl = """
s ::= task SEMI s | task SEMI
task ::= move | craft | collect | ifhas do
move ::= MOVE_FUNC LPAR dir RPAR
dir ::= UP | DOWN | LEFT | RIGHT
craft ::= CRAFT_FUNC LPAR item RPAR
collect ::= COLLECT_FUNC LPAR primitive RPAR
item ::= ROPE | KNIFE | SLINGSHOT | ARROW | GOLDARROW
ifhas ::= if HAS LPAR item RPAR
primitive ::= BOUNDARY | WATER | STONE | WORKSHOP0 | WORKSHOP1 | WORKSHOP2 | WOOD | IRON | GRASS | ROCK | GOLD | GEM
do ::= then task
"""
    
    # Example programs (replace with your actual data)
    example_programs = [
        "COLLECT_FUNC(IRON); COLLECT_FUNC(ROCK); CRAFT_FUNC(KNIFE);",
        "COLLECT_FUNC(WOOD); CRAFT_FUNC(ARROW);",  # Failed - missing knife
        "COLLECT_FUNC(GRASS); CRAFT_FUNC(ROPE); COLLECT_FUNC(WOOD); COLLECT_FUNC(ROCK); CRAFT_FUNC(SLINGSHOT);",
        "if HAS(KNIFE) then CRAFT_FUNC(ARROW);",  # Conditional - might be problematic
        "MOVE_FUNC(UP); MOVE_FUNC(UP); MOVE_FUNC(UP); COLLECT_FUNC(WOOD);",  # Repeated moves
        "COLLECT_FUNC(IRON); COLLECT_FUNC(IRON); COLLECT_FUNC(IRON); CRAFT_FUNC(KNIFE);"  # Repeated collects
    ]
    
    example_success = [True, False, True, False, True, True]
    
    # Analyze
    analyzer = DSLSimplificationAnalyzer()
    report = analyzer.generate_simplification_report(example_dsl, example_programs, example_success)
    
    # Save report
    with open("dsl_simplification_report.json", 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    # Print summary
    summary = report["analysis_summary"]
    print("DSL Simplification Analysis Complete!")
    print(f"Total constructs: {summary['total_constructs']}")
    print(f"Unused constructs: {summary['unused_constructs']}")
    print(f"Problematic constructs: {summary['problematic_constructs']}")
    print(f"Redundant patterns: {summary['redundant_patterns']}")
    print(f"Overall success rate: {summary['overall_success_rate']:.1%}")
    
    print(f"\nReport saved to: dsl_simplification_report.json")
    
    # Print key suggestions
    suggestions = report["simplification_suggestions"]
    print(f"\nKey Simplification Suggestions:")
    print(f"Removals: {len(suggestions['removals'])}")
    print(f"Replacements: {len(suggestions['replacements'])}")
    print(f"Simplifications: {len(suggestions['simplifications'])}")

if __name__ == "__main__":
    main() 