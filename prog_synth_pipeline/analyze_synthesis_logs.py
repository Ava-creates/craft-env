import json
import re
import os
from typing import List, Dict, Any, Counter
from collections import defaultdict

class SynthesisLogAnalyzer:
    def __init__(self, log_file_path: str):
        self.log_file_path = log_file_path
        self.results = []
        
    def parse_log_file(self):
        """Parse the synthesis log file"""
        with open(self.log_file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                # Parse the format: task: program, solution: bool, reward: float, evaluation_time: float
                pattern = r'^([^:]+):\s*(.*?),\s*solution:\s*(True|False),\s*reward:\s*([\d.-]+),\s*evaluation_time:\s*([\d.]+)s'
                match = re.match(pattern, line)
                
                if match:
                    task_name = match.group(1).strip()
                    program = match.group(2).strip()
                    success = match.group(3) == 'True'
                    reward = float(match.group(4))
                    execution_time = float(match.group(5))
                    
                    # Clean up the program
                    if program.endswith(';'):
                        program = program[:-1].strip()
                    
                    self.results.append({
                        'task_name': task_name,
                        'program': program,
                        'success': success,
                        'reward': reward,
                        'execution_time': execution_time,
                        'line_number': line_num
                    })
                else:
                    print(f"Warning: Could not parse line {line_num}: {line[:50]}...")
    
    def analyze_results(self) -> Dict[str, Any]:
        """Analyze the synthesis results"""
        
        # Basic statistics
        total_programs = len(self.results)
        successful_programs = sum(1 for r in self.results if r['success'])
        overall_success_rate = successful_programs / total_programs if total_programs > 0 else 0
        
        # Task-specific analysis
        task_stats = defaultdict(lambda: {
            'total': 0,
            'successful': 0,
            'programs': [],
            'avg_reward': 0.0,
            'avg_execution_time': 0.0
        })
        
        for result in self.results:
            task = result['task_name']
            task_stats[task]['total'] += 1
            task_stats[task]['programs'].append(result['program'])
            
            if result['success']:
                task_stats[task]['successful'] += 1
            
            task_stats[task]['avg_reward'] += result['reward']
            task_stats[task]['avg_execution_time'] += result['execution_time']
        
        # Calculate averages
        for task in task_stats:
            total = task_stats[task]['total']
            task_stats[task]['success_rate'] = task_stats[task]['successful'] / total
            task_stats[task]['avg_reward'] /= total
            task_stats[task]['avg_execution_time'] /= total
        
        # Analyze program patterns
        program_patterns = self.analyze_program_patterns()
        
        # DSL construct usage analysis
        construct_usage = self.analyze_construct_usage()
        
        return {
            'summary': {
                'total_programs': total_programs,
                'successful_programs': successful_programs,
                'overall_success_rate': overall_success_rate,
                'unique_tasks': len(task_stats)
            },
            'task_analysis': dict(task_stats),
            'program_patterns': program_patterns,
            'construct_usage': construct_usage,
            'dsl_simplification_suggestions': self.generate_simplification_suggestions(
                task_stats, program_patterns, construct_usage
            )
        }
    
    def analyze_program_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in the generated programs"""
        
        # Extract all unique programs
        unique_programs = list(set(r['program'] for r in self.results))
        
        # Analyze program lengths
        program_lengths = [len(p.split()) for p in unique_programs]
        
        # Find most common programs
        program_counter = Counter(r['program'] for r in self.results)
        most_common_programs = program_counter.most_common(10)
        
        # Analyze success rates by program pattern
        program_success_rates = {}
        for program in unique_programs:
            programs_with_this_pattern = [r for r in self.results if r['program'] == program]
            success_count = sum(1 for r in programs_with_this_pattern if r['success'])
            program_success_rates[program] = {
                'count': len(programs_with_this_pattern),
                'success_count': success_count,
                'success_rate': success_count / len(programs_with_this_pattern)
            }
        
        return {
            'unique_programs': len(unique_programs),
            'avg_program_length': sum(program_lengths) / len(program_lengths) if program_lengths else 0,
            'most_common_programs': most_common_programs,
            'program_success_rates': program_success_rates
        }
    
    def analyze_construct_usage(self) -> Dict[str, Any]:
        """Analyze usage of DSL constructs"""
        
        construct_stats = defaultdict(lambda: {
            'total_usage': 0,
            'successful_usage': 0,
            'failed_usage': 0,
            'examples': []
        })
        
        for result in self.results:
            program = result['program']
            
            # Extract constructs from program
            constructs = self.extract_constructs(program)
            
            for construct in constructs:
                construct_stats[construct]['total_usage'] += 1
                
                if result['success']:
                    construct_stats[construct]['successful_usage'] += 1
                else:
                    construct_stats[construct]['failed_usage'] += 1
                
                # Add example (limit to 3)
                if len(construct_stats[construct]['examples']) < 3:
                    construct_stats[construct]['examples'].append(program)
        
        # Calculate success rates
        for construct in construct_stats:
            total = construct_stats[construct]['total_usage']
            successful = construct_stats[construct]['successful_usage']
            construct_stats[construct]['success_rate'] = successful / total if total > 0 else 0
        
        return dict(construct_stats)
    
    def extract_constructs(self, program: str) -> List[str]:
        """Extract DSL constructs from a program"""
        constructs = []
        
        # Extract function calls
        func_calls = re.findall(r'(\w+_FUNC)\([^)]*\)', program)
        constructs.extend(func_calls)
        
        # Extract keywords
        keywords = re.findall(r'\b(if|HAS|then|SEMI)\b', program)
        constructs.extend(keywords)
        
        # Extract items and primitives
        items = re.findall(r'\b(ROPE|KNIFE|SLINGSHOT|ARROW|GOLDARROW)\b', program)
        constructs.extend(items)
        
        primitives = re.findall(r'\b(BOUNDARY|WATER|STONE|WORKSHOP\d+|WOOD|IRON|GRASS|ROCK|GOLD|GEM)\b', program)
        constructs.extend(primitives)
        
        return list(set(constructs))
    
    def generate_simplification_suggestions(self, task_stats: Dict, program_patterns: Dict, 
                                          construct_usage: Dict) -> Dict[str, List[Dict]]:
        """Generate DSL simplification suggestions based on analysis"""
        
        suggestions = {
            'removals': [],
            'simplifications': [],
            'improvements': []
        }
        
        # Identify unused constructs
        all_constructs = set(construct_usage.keys())
        used_constructs = {c for c in all_constructs if construct_usage[c]['total_usage'] > 0}
        unused_constructs = all_constructs - used_constructs
        
        for construct in unused_constructs:
            suggestions['removals'].append({
                'construct': construct,
                'reason': 'Never used in any program',
                'impact': 'Reduces DSL complexity without affecting functionality'
            })
        
        # Identify problematic constructs
        for construct, stats in construct_usage.items():
            if stats['total_usage'] >= 5 and stats['success_rate'] < 0.3:
                suggestions['simplifications'].append({
                    'construct': construct,
                    'reason': f'Low success rate ({stats["success_rate"]:.1%}) despite {stats["total_usage"]} uses',
                    'suggestion': self.get_construct_suggestion(construct),
                    'impact': 'Should improve synthesis success rate'
                })
        
        # Identify simple but successful patterns
        successful_simple_programs = [
            prog for prog, stats in program_patterns['program_success_rates'].items()
            if stats['success_rate'] > 0.8 and len(prog.split()) <= 3
        ]
        
        if successful_simple_programs:
            suggestions['improvements'].append({
                'type': 'simple_patterns',
                'description': f'Found {len(successful_simple_programs)} simple, successful patterns',
                'examples': successful_simple_programs[:3],
                'suggestion': 'Consider making these patterns more prominent in the DSL'
            })
        
        # Identify task-specific issues
        for task, stats in task_stats.items():
            if stats['success_rate'] < 0.5:
                suggestions['improvements'].append({
                    'type': 'task_specific',
                    'task': task,
                    'issue': f'Low success rate ({stats["success_rate"]:.1%})',
                    'suggestion': f'Focus on improving synthesis for {task} specifically'
                })
        
        return suggestions
    
    def get_construct_suggestion(self, construct: str) -> str:
        """Get improvement suggestion for a construct"""
        suggestions = {
            'COLLECT_FUNC': 'Consider adding resource location hints or automatic pathfinding',
            'CRAFT_FUNC': 'Consider adding automatic dependency resolution',
            'MOVE_FUNC': 'Consider adding navigation functions for common movement patterns',
            'if HAS': 'Consider making dependencies explicit in recipes instead of runtime checks',
            'then': 'Consider simplifying to direct function calls',
            'SEMI': 'Consider using newlines instead of explicit semicolons'
        }
        
        return suggestions.get(construct, 'Consider simplifying or removing this construct')
    
    def save_analysis_report(self, analysis: Dict[str, Any], output_file: str = "synthesis_analysis_report.json"):
        """Save the analysis report to a file"""
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
    
    def print_summary(self, analysis: Dict[str, Any]):
        """Print a summary of the analysis"""
        summary = analysis['summary']
        print("\n" + "="*60)
        print("SYNTHESIS ANALYSIS SUMMARY")
        print("="*60)
        print(f"Total programs analyzed: {summary['total_programs']}")
        print(f"Successful programs: {summary['successful_programs']}")
        print(f"Overall success rate: {summary['overall_success_rate']:.1%}")
        print(f"Unique tasks: {summary['unique_tasks']}")
        
        print(f"\nTask-specific success rates:")
        for task, stats in analysis['task_analysis'].items():
            print(f"  {task}: {stats['success_rate']:.1%} ({stats['successful']}/{stats['total']})")
        
        print(f"\nProgram patterns:")
        patterns = analysis['program_patterns']
        print(f"  Unique programs: {patterns['unique_programs']}")
        print(f"  Average program length: {patterns['avg_program_length']:.1f} tokens")
        
        print(f"\nMost common programs:")
        for program, count in patterns['most_common_programs'][:5]:
            print(f"  '{program}' (used {count} times)")
        
        print(f"\nDSL simplification suggestions:")
        suggestions = analysis['dsl_simplification_suggestions']
        print(f"  Removals: {len(suggestions['removals'])}")
        print(f"  Simplifications: {len(suggestions['simplifications'])}")
        print(f"  Improvements: {len(suggestions['improvements'])}")

def main():
    """Main function to analyze synthesis logs"""
    
    # Analyze the specific log file
    log_file = "solutions_from_prog_synth.txt"
    
    if not os.path.exists(log_file):
        print(f"Error: Log file '{log_file}' not found!")
        return
    
    print(f"Analyzing synthesis log: {log_file}")
    
    # Create analyzer and parse logs
    analyzer = SynthesisLogAnalyzer(log_file)
    analyzer.parse_log_file()
    
    if not analyzer.results:
        print("No results found in the log file!")
        return
    
    # Analyze results
    analysis = analyzer.analyze_results()
    
    # Print summary
    analyzer.print_summary(analysis)
    
    # Save detailed report
    output_file = "synthesis_analysis_report.json"
    analyzer.save_analysis_report(analysis, output_file)
    print(f"\nDetailed analysis saved to: {output_file}")
    
    # Print key simplification suggestions
    suggestions = analysis['dsl_simplification_suggestions']
    
    if suggestions['removals']:
        print(f"\nSuggested removals:")
        for removal in suggestions['removals']:
            print(f"  - {removal['construct']}: {removal['reason']}")
    
    if suggestions['simplifications']:
        print(f"\nSuggested simplifications:")
        for simplification in suggestions['simplifications']:
            print(f"  - {simplification['construct']}: {simplification['reason']}")
            print(f"    Suggestion: {simplification['suggestion']}")

if __name__ == "__main__":
    main() 