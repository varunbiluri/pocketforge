"""Optional local MiniLM classifier, with optional encoder fine-tuning."""
import copy
import numpy as np
from sklearn.linear_model import LogisticRegression

MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
REVISION = '1110a243fdf4706b3f48f1d95db1a4f5529b4d41'


class MiniLMClassifier:
    def __init__(self, epochs=0):
        self.epochs = epochs

    def fit(self, texts, labels, validation=None):
        import torch
        from sentence_transformers import SentenceTransformer
        torch.manual_seed(0)
        torch.set_num_threads(4)
        self.encoder = SentenceTransformer(MODEL, revision=REVISION, device='cpu', trust_remote_code=False)
        self.encoder.max_seq_length = 256
        self.classes = sorted(set(labels))
        self.history = []
        if self.epochs:
            from .core import score
            head = torch.nn.Linear(self.encoder.get_sentence_embedding_dimension(), len(self.classes))
            optimizer = torch.optim.AdamW(list(self.encoder.parameters()) + list(head.parameters()), lr=2e-5)
            targets = torch.tensor([self.classes.index(x) for x in labels])
            best_score, best_state = -1.0, None
            generator = torch.Generator().manual_seed(0)
            for epoch in range(self.epochs):
                self.encoder.train()
                head.train()
                order = torch.randperm(len(texts), generator=generator)
                for offset in range(0, len(order), 32):
                    indices = order[offset:offset + 32]
                    features = self.encoder.tokenize([texts[i] for i in indices.tolist()])
                    embeddings = self.encoder(features)['sentence_embedding']
                    loss = torch.nn.functional.cross_entropy(head(embeddings), targets[indices])
                    optimizer.zero_grad()
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(list(self.encoder.parameters()) + list(head.parameters()), 1.0)
                    optimizer.step()
                self.encoder.eval()
                with torch.no_grad():
                    embedded = self.encoder.encode(validation[0], convert_to_tensor=True, show_progress_bar=False)
                    predicted = [self.classes[i] for i in head(embedded).argmax(1).tolist()]
                quality = score(self.classes, validation[1], predicted)['macro_f1']
                self.history.append({'epoch': epoch + 1, 'validation_macro_f1': quality})
                if quality > best_score:
                    best_score = quality
                    best_state = copy.deepcopy(self.encoder.state_dict())
                    self.selected_epoch = epoch + 1
            self.encoder.load_state_dict(best_state)
        else:
            self.selected_epoch = 0
        self.encoder.eval()
        embeddings = self.encoder.encode(texts, batch_size=32, normalize_embeddings=True, show_progress_bar=False)
        self.head = LogisticRegression(max_iter=1000, random_state=0)
        self.head.fit(embeddings, labels)
        return self

    def predict(self, texts):
        embeddings = self.encoder.encode(texts, batch_size=32, normalize_embeddings=True, show_progress_bar=False)
        return np.asarray(self.head.predict(embeddings))

    def save(self, directory):
        import joblib
        directory.mkdir()
        self.encoder.save_pretrained(str(directory / 'encoder'))
        from pathlib import Path
        import shutil
        shutil.copyfile(Path(__file__).with_name("APACHE-2.0.txt"), directory / "LICENSE.encoder.txt")
        (directory / "NOTICE.txt").write_text(f"Derived from {MODEL} at {REVISION}. Apache-2.0. Encoder fine-tuning epochs: {self.epochs}. Classifier adapted by PocketForge. See https://huggingface.co/{MODEL} for upstream model details.\n")
        joblib.dump(self.head, directory / 'head.joblib')

    @classmethod
    def load(cls, directory):
        import joblib
        import torch
        from sentence_transformers import SentenceTransformer
        torch.set_num_threads(4)
        result = cls()
        result.encoder = SentenceTransformer(str(directory / 'encoder'), device='cpu', local_files_only=True, trust_remote_code=False)
        result.head = joblib.load(directory / 'head.joblib')
        return result
