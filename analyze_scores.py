import json
from datetime import datetime
from collections import defaultdict

def analyze_scores(log_file):
    first_25_score = None
    total_25_scores = 0
    line_number = 0
    
    with open(log_file, 'r') as f:
        for line in f:
            line_number += 1
            try:
                data = json.loads(line.strip())
                scores = data.get('scores', {})
                
                # Check if any score is 2.5
                if any(score == 2.5 for score in scores.values()):
                    total_25_scores += 1
                    # Only record the first occurrence
                    if first_25_score is None:
                        first_25_score = {
                            'line_number': line_number,
                            'scores': scores
                        }
            except json.JSONDecodeError:
                continue
    
    print(f"Total number of times score 2.5 appears: {total_25_scores}")
    if first_25_score:
        print(f"First occurrence of score 2.5 found at line: {first_25_score['line_number']}")
        print(f"Scores at that time: {first_25_score['scores']}")
    else:
        print("No score of 2.5 found in the log file.")

def extract_scores_to_file(input_log_file, output_file):
    count = 0
    
    with open(input_log_file, 'r') as f_in, open(output_file, 'w') as f_out:
        for line_number, line in enumerate(f_in, 1):
            try:
                data = json.loads(line.strip())
                scores = data.get('scores', {})
                
                # Check if any score is 2.5
                if any(score == 2.5 for score in scores.values()):
                    count += 1
                    # Write the line number and the full JSON data
                    output_data = {
                        'line_number': line_number,
                        'data': data
                    }
                    f_out.write(json.dumps(output_data) + '\n')
            except json.JSONDecodeError:
                continue
    
    print(f"Found {count} instances with score 2.5")
    print(f"Results have been written to {output_file}")

def extract_distinct_function_bodies(input_log_file, output_file):
    # Dictionary to store function bodies and their occurrences
    function_bodies = defaultdict(list)
    
    with open(input_log_file, 'r') as f:
        for line_number, line in enumerate(f, 1):
            try:
                data = json.loads(line.strip())
                scores = data.get('scores', {})
                
                # Check if any score is 2.5
                if any(score == 1.0 for score in scores.values()):
                    function_body = data.get('function_body', '')
                    if function_body:
                        function_bodies[function_body].append({
                            'line_number': line_number,
                            'data': data
                        })
            except json.JSONDecodeError:
                continue
    
    # Convert to list and sort by occurrence count
    sorted_bodies = []
    for function_body, occurrences in function_bodies.items():
        sorted_bodies.append({
            'function_body': function_body,
            'occurrence_count': len(occurrences)
        })
    
    # Sort by occurrence count in descending order
    sorted_bodies.sort(key=lambda x: x['occurrence_count'], reverse=True)
    
    # Write results to file
    with open(output_file, 'w') as f_out:
        for body_data in sorted_bodies:
            f_out.write(json.dumps(body_data) + '\n')
    
    print(f"Found {len(function_bodies)} distinct function bodies with score 2.5")
    print(f"Results have been written to {output_file}")
    
    # Print top 5 most frequent function bodies
    print("\nTop 5 most frequent function bodies:")
    for i, body_data in enumerate(sorted_bodies[:5], 1):
        print(f"{i}. Occurrence count: {body_data['occurrence_count']}")
        print(f"   Function body: {body_data['function_body']}")
        print()

if __name__ == "__main__":
    log_file = "/Users/avanitiwari/Downloads/program_registration_2025-05-12_10-32-45.log"
    # output_file = "scores_25_instances.json"
    distinct_bodies_file = "distinct_function_bodies_[].json"
    
    analyze_scores(log_file)
    
    # extract_scores_to_file(log_file, output_file)
    
    extract_distinct_function_bodies(log_file, distinct_bodies_file) 