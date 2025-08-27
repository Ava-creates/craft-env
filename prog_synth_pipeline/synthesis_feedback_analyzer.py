import json
import re
import os
from typing import List, Dict, Any
from dsl_improvement_pipeline import SynthesisResult, DSLImprovementPipeline

class SynthesisFeedbackAnalyzer:
    def __init__(self, results_dir: str = "results"):
        self.results_dir = results_dir
        
    def parse_synthesis_log(self, log_file: str) -> List[SynthesisResult]:
        """Parse a synthesis log file and extract results"""
        results = []
        
        with open(log_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Try to parse as JSON first (for newer format)
                    if line.startswith('{'):
                        try:
                            log_entry = json.loads(line)
                            result = self.parse_json_entry(log_entry)
                            if result:
                                results.append(result)
                            continue
                        except json.JSONDecodeError:
                            pass
                    
                    # Parse as text format (for solutions_from_prog_synth.txt format)
                    result = self.parse_text_entry(line)
                    if result:
                        results.append(result)
                        
                except Exception as e:
                    print(f"Error parsing line {line_num}: {e}")
                    print(f"Line content: {line[:100]}...")
                    continue
        
        return results
    
    def parse_json_entry(self, log_entry: Dict[str, Any]) -> SynthesisResult:
        """Parse a JSON log entry"""
        program = log_entry.get('function_body', '')
        
        # Extract task name from program or metadata
        task_name = self.extract_task_name(program, log_entry)
        
        # Extract success/reward information
        success, reward, execution_time, error_msg = self.extract_performance_metrics(log_entry)
        
        return SynthesisResult(
            task_name=task_name,
            program=program,
            success=success,
            reward=reward,
            execution_time=execution_time,
            error_message=error_msg
        )
    
    def parse_text_entry(self, line: str) -> SynthesisResult:
        """Parse a text format log entry like: make[slingshot]: COLLECT_FUNC(GRASS) ;, solution: False, reward: 0.5, evaluation_time: 0.0054s"""
        
        # Parse the format: task: program, solution: bool, reward: float, evaluation_time: float
        pattern = r'^([^:]+):\s*(.*?),\s*solution:\s*(True|False),\s*reward:\s*([\d.-]+),\s*evaluation_time:\s*([\d.]+)s'
        match = re.match(pattern, line)
        
        if not match:
            return None
        
        task_name = match.group(1).strip()
        program = match.group(2).strip()
        success = match.group(3) == 'True'
        reward = float(match.group(4))
        execution_time = float(match.group(5))
        
        # Clean up the program (remove trailing semicolon if present)
        if program.endswith(';'):
            program = program[:-1].strip()
        
        return SynthesisResult(
            task_name=task_name,
            program=program,
            success=success,
            reward=reward,
            execution_time=execution_time,
            error_message="" if success else "Task failed"
        )
    
    def extract_task_name(self, program: str, log_entry: Dict[str, Any]) -> str:
        """Extract task name from program or log entry"""
        
        # Try to get from log entry metadata
        if 'task_name' in log_entry:
            return log_entry['task_name']
        
        # Try to extract from program content
        if 'make[' in program:
            match = re.search(r'make\[([^\]]+)\]', program)
            if match:
                return f"make[{match.group(1)}]"
        
        # Try to extract from scores if available
        if 'scores' in log_entry:
            scores = log_entry['scores']
            if isinstance(scores, dict) and scores:
                # Assume the first task in scores is the main task
                return list(scores.keys())[0]
        
        # Default fallback
        return "unknown_task"
    
    def extract_performance_metrics(self, log_entry: Dict[str, Any]) -> tuple:
        """Extract performance metrics from log entry"""
        
        # Default values
        success = False
        reward = 0.0
        execution_time = 0.0
        error_msg = ""
        
        # Try to extract from scores
        if 'scores' in log_entry:
            scores = log_entry['scores']
            if isinstance(scores, dict):
                # Look for reward values
                for task, score in scores.items():
                    if isinstance(score, (int, float)):
                        reward = float(score)
                        success = reward > 0
                        break
            elif isinstance(scores, tuple):
                # Handle tuple format (reward, success)
                if len(scores) >= 2:
                    reward = float(scores[0])
                    success = bool(scores[1])
        
        # Try to extract from island_id or other metadata
        if 'island_id' in log_entry:
            # This might indicate a successful synthesis
            success = True
        
        # Try to extract error information
        if 'error' in log_entry:
            error_msg = str(log_entry['error'])
            success = False
        
        return success, reward, execution_time, error_msg
    
    def analyze_all_logs(self) -> List[SynthesisResult]:
        """Analyze all synthesis log files in the results directory"""
        all_results = []
        
        for filename in os.listdir(self.results_dir):
            if filename.endswith('.log') or filename.endswith('.txt'):
                log_path = os.path.join(self.results_dir, filename)
                print(f"Analyzing {filename}...")
                
                try:
                    results = self.parse_synthesis_log(log_path)
                    all_results.extend(results)
                    print(f"  Found {len(results)} results")
                except Exception as e:
                    print(f"  Error analyzing {filename}: {e}")
        
        return all_results
    
    def filter_results_by_task(self, results: List[SynthesisResult], task_pattern: str = None) -> List[SynthesisResult]:
        """Filter results by task name pattern"""
        if task_pattern is None:
            return results
        
        filtered = []
        for result in results:
            if task_pattern.lower() in result.task_name.lower():
                filtered.append(result)
        
        return filtered
    
    def generate_improvement_report(self, results: List[SynthesisResult], output_file: str = "improvement_report.json"):
        """Generate a comprehensive improvement report"""
        
        # Initialize pipeline
        pipeline = DSLImprovementPipeline("http://129.128.243.184:11434/api/generate")
        
        # Get current DSL and implementations
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
        
        # Read current implementations
        try:
            with open("craft_func.py", 'r') as f:
                craft_impl = f.read()
        except:
            craft_impl = "# CRAFT_FUNC implementation not found"
        
        try:
            with open("collect_func.py", 'r') as f:
                collect_impl = f.read()
        except:
            collect_impl = "# COLLECT_FUNC implementation not found"
        
        current_implementations = {
            "craft": craft_impl,
            "collect": collect_impl
        }
        
        # Get improvements
        improvements = pipeline.get_dsl_improvements(
            current_dsl, current_implementations, results
        )
        
        # Save report
        pipeline.save_improvement_results(improvements, output_file)
        
        return improvements

def main():
    """Example usage of the synthesis feedback analyzer"""
    
    analyzer = SynthesisFeedbackAnalyzer()
    
    # Analyze all logs
    print("Analyzing synthesis logs...")
    all_results = analyzer.analyze_all_logs()
    
    print(f"\nTotal results found: {len(all_results)}")
    
    # Filter for specific tasks if needed
    craft_results = analyzer.filter_results_by_task(all_results, "craft")
    collect_results = analyzer.filter_results_by_task(all_results, "collect")
    
    print(f"Craft task results: {len(craft_results)}")
    print(f"Collect task results: {len(collect_results)}")
    
    # Generate improvement report
    if all_results:
        print("\nGenerating improvement report...")
        improvements = analyzer.generate_improvement_report(all_results)
        
        if 'analysis_summary' in improvements:
            summary = improvements['analysis_summary']
            print(f"Overall success rate: {summary['overall_success_rate']:.1%}")
            print(f"Tasks analyzed: {summary['tasks_analyzed']}")
        
        print("Improvement report saved to: improvement_report.json")
    else:
        print("No results found to analyze")

if __name__ == "__main__":
    main() 