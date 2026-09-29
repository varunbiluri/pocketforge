"""Independent plain scikit-learn workflow on the identical frozen task splits."""
import argparse
import json
from pathlib import Path
import yaml
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('task')
parser.add_argument('--report', required=True)
args = parser.parse_args()
root = Path(args.task).parent
config = yaml.safe_load(Path(args.task).read_text())
def rows(split):
    return [json.loads(line) for line in (root / config['splits'][split]).read_text().splitlines() if line.strip()]
training, test = rows('train'), rows('test')
model = make_pipeline(TfidfVectorizer(analyzer='char', ngram_range=(1,5), max_features=50000), LogisticRegression(max_iter=1000, random_state=0))
model.fit([r['text'] for r in training], [r['label'] for r in training])
predicted = model.predict([r['text'] for r in test]).tolist()
truth = [r['label'] for r in test]
report = json.loads(Path(args.report).read_text())
assert predicted == report['results']['tfidf_linear']['predictions']
print(json.dumps({'accuracy': accuracy_score(truth, predicted), 'macro_f1': f1_score(truth,predicted,labels=config['labels'],average='macro',zero_division=0), 'all_predictions_match_pocketforge': True},indent=2))
