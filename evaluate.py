import json
import time
from datetime import timedelta
from translator import process_nl_query


def load_json(filename):
    with open(f'data/{filename}', 'r', encoding='utf-8') as f:
        return json.load(f)


def save_to_file(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def create_new_example(ex, nl_query, generated_sql, result):
    return {
        "labels": ex["labels"],
        "Arabic-Query": ex["Arabic-Query"],
        "SQL-Query": ex["SQL-Query"],
        "output": ex["output"],
        "variation": nl_query,
        "Generated-SQL": generated_sql,
        "Generated-Output": result
    }


def create_new_entry(example, new_example):
    return {
        "English-Query": example["English-Query"],
        "Arabic-Query": example["Arabic-Query"],
        "SQL-Query": example["SQL-Query"],
        "importancy": example["importancy"],
        "id": example["id"],
        "evaluation-example": new_example
    }


def compare_variations(nl_query, variations):
    """Compare the NL query with the variations after removing all spaces and leading/trailing whitespaces"""
    variations_cleaned = [var.strip().replace(' ', '') for var in variations]
    nl_query_cleaned = nl_query.strip().replace(' ', '')
    return nl_query_cleaned in variations_cleaned


def compare_sqls(true_sql, generated_sql):
    """Compare SQL statements after removing all spaces and leading/trailing whitespaces"""
    return true_sql.replace(' ', '').strip() == generated_sql.replace(' ', '').strip()


def compare_outputs(true_output, result):
    """Compare outputs after removing all spaces and leading/trailing whitespaces"""
    return true_output.replace(' ', '').strip() == result.replace(' ', '').strip()


def check_accuracy(correct_count, total_queries):
    return correct_count / total_queries


def print_and_save_metrics(accuracy, exact_match_rate, average_execution_time, execution_success_rate, total_time, total_evaluated_examples):
    with open("output/metrics.txt", "w", encoding="utf-8") as f:
        f.write(f"Accuracy: {accuracy:.2f}\n")
        f.write(f"Exact Match Rate: {exact_match_rate:.2f}\n")
        f.write(
            f"Average SQL Generation Time: {average_execution_time:.2f} seconds\n")
        f.write(f"Execution Success Rate: {execution_success_rate:.2f}\n")
        f.write(f"Total Evaluation Time: {total_time}\n")
        f.write(f"Total Evaluated Examples: {total_evaluated_examples}\n")

    print(f"Accuracy: {accuracy:.2f}")
    print(f"Exact Match Rate: {exact_match_rate:.2f}")
    print(f"Average SQL Generation Time: {average_execution_time:.2f} seconds")
    print(f"Execution Success Rate: {execution_success_rate:.2f}")
    print(f"Total Evaluation Time: {total_time}")
    print(f"Total Evaluated Examples: {total_evaluated_examples}")


def process_data():
    dev_data = load_json('dev_dataset.json')
    example_data = load_json('simple_data_with_examples_and_variations.json')

    correct_count = 0
    total_queries = len(dev_data)
    final_output = []
    exact_match_count = 0
    total_execution_time = 0
    total_executable_queries = 0

    # Start of evaluation
    start_time = time.time()

    for i, entry in enumerate(dev_data, start=1):
        nl_query = entry["input"]

        # Translate the NL query to SQL and get results
        generated_sql, result, error_occurred, execution_time = process_nl_query(
            nl_query)

        total_execution_time += execution_time

        if not error_occurred:
            total_executable_queries += 1

        if error_occurred:
            print(f"SQL error at query {i}: {generated_sql}")
            result = "sql error"

        # Check the results with the true output
        for example in example_data:
            for ex in example["examples"]:
                if compare_variations(nl_query, ex["variations"]):
                    true_output = ex["output"]
                    true_sql = ex["SQL-Query"]

                    # Save generated SQLs and results in a new dict
                    new_example = create_new_example(
                        ex, nl_query, generated_sql, result)

                    # Create new entry for the output
                    new_entry = create_new_entry(example, new_example)

                    # Add this entry to the final output
                    final_output.append(new_entry)

                    # Check accuracy first by SQL comparison
                    if compare_sqls(true_sql, generated_sql):
                        correct_count += 1
                        exact_match_count += 1
                    else:
                        # if SQLs are different, then compare the outputs
                        if compare_outputs(true_output, result):
                            correct_count += 1
                    break

        # Print progress
        accuracy = check_accuracy(correct_count, i)
        print(
            f"{i/total_queries*100:.2f}% ({i}/{total_queries}) | accuracy: {accuracy*100:.2f}%")

    # End of evaluation
    end_time = time.time()
    total_time = end_time - start_time
    total_time_str = str(timedelta(seconds=int(total_time)))

    # Save the modified examples with generated SQLs and results
    save_to_file("output/evaluation_data.json", final_output)

    # Calculate the metrics
    accuracy = check_accuracy(correct_count, total_queries)
    exact_match_rate = exact_match_count / total_queries
    average_execution_time = total_execution_time / total_queries
    execution_success_rate = total_executable_queries / total_queries
    total_evaluated_examples = len(final_output)

    # Print and save the metrics
    print_and_save_metrics(accuracy, exact_match_rate, average_execution_time,
                           execution_success_rate, total_time_str, total_evaluated_examples)


if __name__ == '__main__':
    process_data()
