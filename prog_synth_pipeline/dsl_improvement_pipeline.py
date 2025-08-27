import json
import requests
import os
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import re

@dataclass
class SynthesisResult:
    """Represents the result of a program synthesis experiment"""
    task_name: str
    program: str
    success: bool
    reward: float
    execution_time: float
    error_message: str = ""
    issues: List[str] = None

@dataclass
class TaskPerformance:
    """Aggregated performance metrics for a task"""
    task_name: str
    success_rate: float
    avg_reward: float
    avg_execution_time: float
    common_issues: List[str]
    successful_programs: List[str]
    failed_programs: List[str]

class DSLImprovementPipeline:
    def __init__(self, api_url: str, model_name: str = "qwen2.5-coder:32b"):
        self.api_url = api_url
        self.model_name = model_name
        self.headers = {"Content-Type": "application/json"}
        
    def analyze_synthesis_results(self, results: List[SynthesisResult]) -> Dict[str, TaskPerformance]:
        """Analyze synthesis results and extract performance metrics"""
        task_results = {}
        
        for result in results:
            if result.task_name not in task_results:
                task_results[result.task_name] = {
                    'successful': [],
                    'failed': [],
                    'rewards': [],
                    'execution_times': [],
                    'issues': set()
                }
            
            task_data = task_results[result.task_name]
            if result.success:
                task_data['successful'].append(result.program)
            else:
                task_data['failed'].append(result.program)
                if result.error_message:
                    task_data['issues'].add(result.error_message)
                if result.issues:
                    task_data['issues'].update(result.issues)
            
            task_data['rewards'].append(result.reward)
            task_data['execution_times'].append(result.execution_time)
        
        # Convert to TaskPerformance objects
        performance_metrics = {}
        for task_name, data in task_results.items():
            total_attempts = len(data['successful']) + len(data['failed'])
            success_rate = len(data['successful']) / total_attempts if total_attempts > 0 else 0
            avg_reward = sum(data['rewards']) / len(data['rewards']) if data['rewards'] else 0
            avg_execution_time = sum(data['execution_times']) / len(data['execution_times']) if data['execution_times'] else 0
            
            performance_metrics[task_name] = TaskPerformance(
                task_name=task_name,
                success_rate=success_rate,
                avg_reward=avg_reward,
                avg_execution_time=avg_execution_time,
                common_issues=list(data['issues']),
                successful_programs=data['successful'],
                failed_programs=data['failed']
            )
        
        return performance_metrics
    
    def analyze_dsl_redundancy(self, 
                             current_dsl: str,
                             synthesis_results: List[SynthesisResult],
                             performance_metrics: Dict[str, TaskPerformance]) -> Dict[str, Any]:
        """Analyze DSL for redundant or unnecessary constructs"""
        
        # Analyze construct usage patterns
        construct_usage = self.analyze_construct_usage(synthesis_results)
        
        # Identify unused constructs
        unused_constructs = self.identify_unused_constructs(construct_usage, current_dsl)
        
        # Identify problematic constructs
        problematic_constructs = self.identify_problematic_constructs(synthesis_results, performance_metrics)
        
        # Identify redundant constructs
        redundant_constructs = self.identify_redundant_constructs(construct_usage, synthesis_results)
        
        return {
            "unused_constructs": unused_constructs,
            "problematic_constructs": problematic_constructs,
            "redundant_constructs": redundant_constructs,
            "construct_usage": construct_usage,
            "simplification_suggestions": self.generate_simplification_suggestions(
                unused_constructs, problematic_constructs, redundant_constructs
            )
        }
    
    def analyze_construct_usage(self, synthesis_results: List[SynthesisResult]) -> Dict[str, Dict[str, Any]]:
        """Analyze how often each DSL construct is used"""
        usage_stats = {}
        
        # Initialize construct tracking
        constructs = {
            'MOVE_FUNC': {'count': 0, 'success_rate': 0, 'failures': []},
            'CRAFT_FUNC': {'count': 0, 'success_rate': 0, 'failures': []},
            'COLLECT_FUNC': {'count': 0, 'success_rate': 0, 'failures': []},
            'if HAS': {'count': 0, 'success_rate': 0, 'failures': []},
            'then': {'count': 0, 'success_rate': 0, 'failures': []},
            'SEMI': {'count': 0, 'success_rate': 0, 'failures': []}
        }
        
        for result in synthesis_results:
            program = result.program
            
            # Count construct usage
            for construct in constructs.keys():
                if construct in program:
                    constructs[construct]['count'] += 1
                    
                    # Track success/failure
                    if result.success:
                        constructs[construct]['success_rate'] += 1
                    else:
                        constructs[construct]['failures'].append({
                            'program': program,
                            'error': result.error_message
                        })
        
        # Calculate success rates
        for construct, stats in constructs.items():
            if stats['count'] > 0:
                stats['success_rate'] = stats['success_rate'] / stats['count']
        
        return constructs
    
    def identify_unused_constructs(self, construct_usage: Dict[str, Dict[str, Any]], current_dsl: str) -> List[Dict[str, Any]]:
        """Identify constructs that are never used in successful programs"""
        unused = []
        
        # Extract all constructs from DSL grammar
        dsl_constructs = self.extract_dsl_constructs(current_dsl)
        
        for construct in dsl_constructs:
            if construct in construct_usage:
                usage = construct_usage[construct]
                if usage['count'] == 0:
                    unused.append({
                        'construct': construct,
                        'reason': 'Never used in any program',
                        'dsl_location': self.find_construct_in_dsl(construct, current_dsl)
                    })
                elif usage['success_rate'] == 0 and usage['count'] > 5:
                    unused.append({
                        'construct': construct,
                        'reason': f'Used {usage["count"]} times but never successful',
                        'dsl_location': self.find_construct_in_dsl(construct, current_dsl)
                    })
        
        return unused
    
    def identify_problematic_constructs(self, synthesis_results: List[SynthesisResult], 
                                     performance_metrics: Dict[str, TaskPerformance]) -> List[Dict[str, Any]]:
        """Identify constructs that frequently cause failures"""
        problematic = []
        
        # Analyze failure patterns
        failure_patterns = {}
        for result in synthesis_results:
            if not result.success:
                # Extract constructs from failed program
                constructs_in_program = self.extract_constructs_from_program(result.program)
                for construct in constructs_in_program:
                    if construct not in failure_patterns:
                        failure_patterns[construct] = {'count': 0, 'errors': []}
                    failure_patterns[construct]['count'] += 1
                    failure_patterns[construct]['errors'].append(result.error_message)
        
        # Identify problematic constructs
        for construct, pattern in failure_patterns.items():
            if pattern['count'] >= 3:  # At least 3 failures
                problematic.append({
                    'construct': construct,
                    'failure_count': pattern['count'],
                    'common_errors': self.get_common_errors(pattern['errors']),
                    'suggestion': self.get_construct_improvement_suggestion(construct, pattern['errors'])
                })
        
        return problematic
    
    def identify_redundant_constructs(self, construct_usage: Dict[str, Dict[str, Any]], 
                                   synthesis_results: List[SynthesisResult]) -> List[Dict[str, Any]]:
        """Identify constructs that can be replaced by simpler alternatives"""
        redundant = []
        
        # Check for redundant patterns
        redundant_patterns = [
            {
                'pattern': ['if HAS', 'then', 'CRAFT_FUNC'],
                'alternative': 'CRAFT_FUNC',
                'reason': 'Conditional crafting often unnecessary when dependencies are explicit'
            },
            {
                'pattern': ['MOVE_FUNC', 'MOVE_FUNC', 'MOVE_FUNC'],
                'alternative': 'NAVIGATE_FUNC',
                'reason': 'Multiple consecutive moves can be replaced with navigation'
            },
            {
                'pattern': ['COLLECT_FUNC', 'COLLECT_FUNC', 'COLLECT_FUNC'],
                'alternative': 'COLLECT_MULTI_FUNC',
                'reason': 'Multiple consecutive collects can be batched'
            }
        ]
        
        for pattern_info in redundant_patterns:
            pattern = pattern_info['pattern']
            count = self.count_pattern_occurrences(pattern, synthesis_results)
            
            if count > 0:
                redundant.append({
                    'pattern': pattern,
                    'alternative': pattern_info['alternative'],
                    'occurrence_count': count,
                    'reason': pattern_info['reason']
                })
        
        return redundant
    
    def extract_dsl_constructs(self, dsl: str) -> List[str]:
        """Extract all constructs from DSL grammar"""
        constructs = []
        
        # Extract function names
        func_patterns = [
            r'(\w+_FUNC)',
            r'(UP|DOWN|LEFT|RIGHT)',
            r'(ROPE|KNIFE|SLINGSHOT|ARROW|GOLDARROW)',
            r'(BOUNDARY|WATER|STONE|WORKSHOP\d+|WOOD|IRON|GRASS|ROCK|GOLD|GEM)',
            r'(if|HAS|then|SEMI)'
        ]
        
        for pattern in func_patterns:
            matches = re.findall(pattern, dsl)
            constructs.extend(matches)
        
        return list(set(constructs))
    
    def extract_constructs_from_program(self, program: str) -> List[str]:
        """Extract constructs used in a program"""
        constructs = []
        
        # Extract function calls
        func_calls = re.findall(r'(\w+_FUNC)\([^)]*\)', program)
        constructs.extend(func_calls)
        
        # Extract other constructs
        other_constructs = re.findall(r'\b(if|HAS|then|SEMI|UP|DOWN|LEFT|RIGHT)\b', program)
        constructs.extend(other_constructs)
        
        return list(set(constructs))
    
    def count_pattern_occurrences(self, pattern: List[str], synthesis_results: List[SynthesisResult]) -> int:
        """Count how often a pattern occurs in programs"""
        count = 0
        
        for result in synthesis_results:
            program = result.program
            # Simple pattern matching (can be made more sophisticated)
            pattern_str = ' '.join(pattern)
            if pattern_str in program:
                count += 1
        
        return count
    
    def get_common_errors(self, errors: List[str]) -> List[str]:
        """Get most common error messages"""
        error_counts = {}
        for error in errors:
            error_counts[error] = error_counts.get(error, 0) + 1
        
        # Return top 3 most common errors
        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        return [error for error, count in sorted_errors[:3]]
    
    def get_construct_improvement_suggestion(self, construct: str, errors: List[str]) -> str:
        """Get improvement suggestion for a problematic construct"""
        suggestions = {
            'if HAS': 'Consider making dependencies explicit in recipes instead of runtime checks',
            'MOVE_FUNC': 'Consider adding navigation functions for common movement patterns',
            'CRAFT_FUNC': 'Consider adding dependency validation or automatic dependency resolution',
            'COLLECT_FUNC': 'Consider adding resource location hints or automatic pathfinding'
        }
        
        return suggestions.get(construct, 'Consider simplifying or removing this construct')
    
    def find_construct_in_dsl(self, construct: str, dsl: str) -> str:
        """Find where a construct is defined in the DSL"""
        lines = dsl.split('\n')
        for i, line in enumerate(lines):
            if construct in line:
                return f"Line {i+1}: {line.strip()}"
        return "Not found in DSL"
    
    def generate_simplification_suggestions(self, unused: List[Dict], problematic: List[Dict], 
                                         redundant: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive simplification suggestions"""
        
        suggestions = {
            "removals": [],
            "replacements": [],
            "simplifications": [],
            "expected_impact": {}
        }
        
        # Suggest removals
        for item in unused:
            suggestions["removals"].append({
                "construct": item['construct'],
                "reason": item['reason'],
                "dsl_location": item['dsl_location'],
                "impact": "Reduces complexity without affecting functionality"
            })
        
        # Suggest replacements
        for item in redundant:
            suggestions["replacements"].append({
                "from": item['pattern'],
                "to": item['alternative'],
                "reason": item['reason'],
                "occurrences": item['occurrence_count'],
                "impact": f"Simplifies {item['occurrence_count']} programs"
            })
        
        # Suggest simplifications
        for item in problematic:
            suggestions["simplifications"].append({
                "construct": item['construct'],
                "issue": f"{item['failure_count']} failures",
                "suggestion": item['suggestion'],
                "impact": "Reduces failure rate"
            })
        
        # Calculate expected impact
        total_removals = len(suggestions["removals"])
        total_replacements = len(suggestions["replacements"])
        total_simplifications = len(suggestions["simplifications"])
        
        suggestions["expected_impact"] = {
            "complexity_reduction": f"{total_removals + total_replacements} constructs simplified",
            "failure_reduction": f"{total_simplifications} problematic constructs addressed",
            "overall_improvement": "Simplified DSL should lead to higher synthesis success rates"
        }
        
        return suggestions

    def generate_improvement_prompt(self, 
                                  current_dsl: str,
                                  current_implementations: Dict[str, str],
                                  performance_metrics: Dict[str, TaskPerformance],
                                  synthesis_results: List[SynthesisResult]) -> str:
        """Generate a comprehensive improvement prompt based on synthesis feedback"""
        
        # Analyze DSL redundancy
        redundancy_analysis = self.analyze_dsl_redundancy(current_dsl, synthesis_results, performance_metrics)
        
        # Format performance metrics
        performance_summary = []
        for task_name, metrics in performance_metrics.items():
            performance_summary.append(
                f"- {task_name}: Success Rate: {metrics.success_rate:.1%}, "
                f"Avg Reward: {metrics.avg_reward:.2f}, "
                f"Common Issues: {', '.join(metrics.common_issues[:3])}"
            )
        
        # Analyze common failure patterns
        all_failed_programs = []
        for metrics in performance_metrics.values():
            all_failed_programs.extend(metrics.failed_programs[:2])  # Take first 2 examples per task
        
        # Analyze successful patterns
        all_successful_programs = []
        for metrics in performance_metrics.values():
            all_successful_programs.extend(metrics.successful_programs[:2])  # Take first 2 examples per task
        
        prompt = f"""You are an expert DSL designer and program synthesis researcher. You have received comprehensive feedback from program synthesis experiments and need to improve the DSL grammar and function implementations.

## CURRENT DSL GRAMMAR
```
{current_dsl}
```

## CURRENT FUNCTION IMPLEMENTATIONS

**CRAFT_FUNC Implementation:**
```python
{current_implementations.get('craft', 'Not provided')}
```

**COLLECT_FUNC Implementation:**
```python
{current_implementations.get('collect', 'Not provided')}
```

## SYNTHESIS FEEDBACK ANALYSIS

**Task Performance Summary:**
{chr(10).join(performance_summary)}

**Successful Program Examples:**
```
{chr(10).join([f"✓ {prog}" for prog in all_successful_programs[:4]])}
```

**Failed Program Examples:**
```
{chr(10).join([f"✗ {prog}" for prog in all_failed_programs[:4]])}
```

## DSL REDUNDANCY ANALYSIS

**Unused Constructs:**
{chr(10).join([f"- {item['construct']}: {item['reason']}" for item in redundancy_analysis['unused_constructs'][:5]])}

**Problematic Constructs:**
{chr(10).join([f"- {item['construct']}: {item['failure_count']} failures - {item['suggestion']}" for item in redundancy_analysis['problematic_constructs'][:5]])}

**Redundant Patterns:**
{chr(10).join([f"- {item['pattern']} → {item['alternative']}: {item['reason']}" for item in redundancy_analysis['redundant_constructs'][:3]])}

## IMPROVEMENT OBJECTIVES

### 1. DSL Simplification (PRIORITY)
Based on the redundancy analysis, focus on:
- **REMOVING** unused constructs that add complexity without value
- **REPLACING** redundant patterns with simpler alternatives
- **SIMPLIFYING** problematic constructs that cause frequent failures
- **STREAMLINING** the grammar to reduce synthesis confusion

### 2. DSL Grammar Enhancements
Only add new constructs if they directly address specific synthesis failures:
- Dependency management constructs (if needed)
- Resource requirement specifications (if needed)
- Error handling and recovery (if needed)

### 3. Function Implementation Improvements
Address the identified issues in:
- Pathfinding and navigation algorithms
- Resource collection strategies
- Workshop selection and usage
- State validation and error recovery

## OUTPUT FORMAT
Provide your analysis and suggestions in the following structured format:

```
## DSL SIMPLIFICATION (HIGH PRIORITY)
[Specific constructs to remove and why]

## DSL GRAMMAR IMPROVEMENTS
[Only essential additions that address specific failures]

## FUNCTION IMPLEMENTATION IMPROVEMENTS
[Specific code improvements with explanations]

## SIMPLIFIED DSL GRAMMAR
[Complete simplified grammar]

## IMPLEMENTATION EXAMPLES
[Code examples for the improvements]

## EXPECTED IMPACT ANALYSIS
[Quantified predictions for improvement in success rates]

## MIGRATION STRATEGY
[How to transition from current DSL to simplified version]
```

**IMPORTANT: Focus heavily on SIMPLIFICATION and REMOVAL of unnecessary constructs. Only add new constructs if they are absolutely essential for addressing specific synthesis failures.**
"""
        return prompt
    
    def get_dsl_improvements(self, 
                           current_dsl: str,
                           current_implementations: Dict[str, str],
                           synthesis_results: List[SynthesisResult]) -> Dict[str, Any]:
        """Get DSL improvements based on synthesis feedback"""
        
        # Analyze results
        performance_metrics = self.analyze_synthesis_results(synthesis_results)
        
        # Generate improvement prompt
        improvement_prompt = self.generate_improvement_prompt(
            current_dsl, current_implementations, performance_metrics, synthesis_results
        )
        
        # Call LLM for improvements
        payload = {
            "model": self.model_name,
            "prompt": improvement_prompt,
            "template": "{{.Prompt}}",
            "stream": False,
            "options": {
                "num_ctx": 8192,
                "temperature": 0.1
            }
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=600)
            response.raise_for_status()
            improvement_suggestions = response.json()["response"]
            
            return {
                "improvement_suggestions": improvement_suggestions,
                "performance_metrics": performance_metrics,
                "analysis_summary": {
                    "total_programs": len(synthesis_results),
                    "overall_success_rate": sum(m.success_rate for m in performance_metrics.values()) / len(performance_metrics),
                    "tasks_analyzed": list(performance_metrics.keys())
                }
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "performance_metrics": performance_metrics
            }
    
    def save_improvement_results(self, results: Dict[str, Any], output_file: str):
        """Save improvement results to file"""
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

def main():
    """Example usage of the DSL improvement pipeline"""
    
    # Example synthesis results (replace with your actual data)
    example_results = [
        SynthesisResult("make[knife]", "COLLECT_FUNC(IRON); COLLECT_FUNC(ROCK); CRAFT_FUNC(KNIFE);", True, 0.8, 2.5),
        SynthesisResult("make[knife]", "COLLECT_FUNC(IRON); CRAFT_FUNC(KNIFE);", False, 0.0, 1.2, "Missing ROCK"),
        SynthesisResult("make[arrow]", "COLLECT_FUNC(WOOD); CRAFT_FUNC(ARROW);", False, 0.0, 1.8, "Missing KNIFE dependency"),
        SynthesisResult("make[arrow]", "COLLECT_FUNC(IRON); COLLECT_FUNC(ROCK); CRAFT_FUNC(KNIFE); COLLECT_FUNC(WOOD); CRAFT_FUNC(ARROW);", True, 0.9, 4.2),
        SynthesisResult("make[slingshot]", "COLLECT_FUNC(GRASS); CRAFT_FUNC(ROPE); CRAFT_FUNC(SLINGSHOT);", False, 0.0, 2.1, "Missing WOOD and ROCK"),
        SynthesisResult("make[goldarrow]", "COLLECT_FUNC(GOLD); COLLECT_FUNC(WOOD); CRAFT_FUNC(GOLDARROW);", True, 0.95, 2.8),
    ]
    
    # Current DSL and implementations
    current_dsl = """
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
    
    current_implementations = {
        "craft": "# CRAFT_FUNC implementation would go here",
        "collect": "# COLLECT_FUNC implementation would go here"
    }
    
    # Initialize pipeline
    pipeline = DSLImprovementPipeline("http://129.128.243.184:11434/api/generate")
    
    # Get improvements
    improvements = pipeline.get_dsl_improvements(current_dsl, current_implementations, example_results)
    
    # Save results
    pipeline.save_improvement_results(improvements, "dsl_improvement_results.json")
    
    print("DSL improvement analysis completed!")
    print(f"Overall success rate: {improvements['analysis_summary']['overall_success_rate']:.1%}")
    print(f"Results saved to: dsl_improvement_results.json")

if __name__ == "__main__":
    main() 