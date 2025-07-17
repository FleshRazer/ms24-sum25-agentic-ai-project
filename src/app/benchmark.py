from pathlib import Path
import pandas as pd
from enum import Enum
from sklearn.metrics.pairwise import cosine_similarity
from bert_score import score
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from schemas import Item, ItemList
from settings import settings
from typing import Dict
from concurrent.futures import ThreadPoolExecutor


class MetricsNames(Enum):
    EXACT = 'exact'
    COSINE = 'cosine'
    BERT = 'bert'


def compute_metrics(generated: Item, golden: Item, embeddings: GoogleGenerativeAIEmbeddings) -> Dict:
    """Calculate metrics for each field between generated and golden items."""
    metrics = {}

    for field in Item.model_fields:
        gen_val = getattr(generated, field, None)
        gold_val = getattr(golden, field, None)

        if gen_val is None or gold_val is None:
            continue

        gen_str = str(gen_val)
        gold_str = str(gold_val)
        
        # Exact match
        metrics[f'{field}_{MetricsNames.EXACT.value}'] = int(gen_val == gold_val)

        # Text embeddings similarity
        gen_embed = embeddings.embed_query(gen_str)
        gold_embed = embeddings.embed_query(gold_str)
        metrics[f'{field}_{MetricsNames.COSINE.value}'] = float(cosine_similarity(
            [gen_embed], [gold_embed]
        )[0][0])

        # BERT Score
        _, _, bert_f1 = score(
            [gen_str],
            [gold_str],
            lang='ru',
            model_type='bert-base-multilingual-cased',
            verbose=False
        )
        metrics[f'{field}_{MetricsNames.BERT.value}'] = float(bert_f1.numpy().item())

    return metrics


def process_file(gen_path: Path, test_set_dir: Path, embeddings: GoogleGenerativeAIEmbeddings) -> Dict:
    """Process a single file and return its metrics."""
    golden_path = test_set_dir / gen_path.name
    if not golden_path.exists():
        return None

    with open(gen_path) as f:
        generated = ItemList.model_validate_json(f.read()).root[0]
    
    with open(golden_path) as f:
        golden = ItemList.model_validate_json(f.read()).root[0]

    return compute_metrics(generated, golden, embeddings)


def main(extracted_set_dir: Path, test_set_dir: Path, results_dir: Path):
    """Run benchmark against golden test set."""
    
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=settings.GOOGLE_API_KEY
    )
    
    model_names = [d.name for d in extracted_set_dir.iterdir() if d.is_dir()]
    
    for model_name in model_names:
        generated_dir = extracted_set_dir / model_name
        json_files = list(generated_dir.glob('*.json'))
        
        # Process files in parallel
        with ThreadPoolExecutor() as executor:
            results = list(filter(None, executor.map(
                lambda x: process_file(x, test_set_dir, embeddings),
                json_files
            )))
        
        if not results:
            print(f"No results for model {model_name}")
            continue
        
        df = pd.DataFrame(results)
        
        # Calculate means
        for metric_name in MetricsNames:
            metric_cols = df.filter(like=f'_{metric_name.value}').columns
            df[f'{metric_name.value}_mean'] = df[metric_cols].mean(axis=1)
        
        df['filename'] = [f.name for f in json_files] if json_files else ['']
        
        # Calculate overall mean
        mean_metrics = df.drop(columns=['filename']).mean().to_dict()
        mean_metrics['filename'] = 'overall_mean'
        df = pd.concat([df, pd.DataFrame([mean_metrics])], ignore_index=True)

        # Save results
        results_dir.mkdir(exist_ok=True)
        results_path = results_dir / f'{model_name}_results.csv'
        df.to_csv(results_path, index=False)

        print(f"Benchmark completed for {model_name}. Results saved to {results_path}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--extracted_set_dir', type=Path, default=Path('data/kamaz_energo/items'),
                      help='Path to generated JSON files')
    parser.add_argument('--test_set_dir', type=Path, default=Path('data/kamaz_energo/test/items'),
                      help='Path to golden JSON files')
    parser.add_argument('--results_dir', type=Path, default=Path('data/kamaz_energo/benchmark'),
                      help='Path to save benchmark results')
    args = parser.parse_args()
    
    main(args.extracted_set_dir, args.test_set_dir, args.results_dir)
