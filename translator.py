from transformers import T5Tokenizer, T5ForConditionalGeneration
from config import MODEL_CONFIG
from database import execute_and_fetch_query
import time

tokenizer = T5Tokenizer.from_pretrained(MODEL_CONFIG['model_name'])
model = T5ForConditionalGeneration.from_pretrained(MODEL_CONFIG['model_name'])


def generate_sql_statement(nl_input: str) -> str:
    """ Generate the most probable SQL statement from the input natural language query."""
    encoding = tokenizer.encode_plus(
        nl_input, padding='max_length', max_length=MODEL_CONFIG['max_length'], return_tensors="pt")
    input_ids, attention_masks = encoding["input_ids"], encoding["attention_mask"]

    # Generate the most probable output
    most_probable_output = model.generate(
        input_ids=input_ids,
        attention_mask=attention_masks,
        max_length=MODEL_CONFIG['max_length'],
        do_sample=False,
        early_stopping=True,
        num_return_sequences=1
    )
    sql = tokenizer.decode(
        most_probable_output[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)

    return sql


def process_nl_query(nl_query: str):
    """
    Translates Natural Language query to SQL, executes it and fetches the results.
    """

    start_time = time.time()
    generated_sql = generate_sql_statement(nl_query)
    end_time = time.time()
    execution_time = end_time - start_time


    result, error_occurred = execute_and_fetch_query(generated_sql)

    return generated_sql, result, error_occurred, execution_time
