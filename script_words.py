from app.database import session_factory
import json
from app.models.word import WordORM
from app.models.forbidden_word import ForbiddenWordORM

def main():
    with open(file='words.json', mode='r', encoding='utf-8') as f:
        content = json.load(f)

    with session_factory() as session:
        for word, forbidden_words in content.items():
            word = WordORM(
                word=word,
            )
            session.add(word)
            session.flush()
            for forbidden_word in forbidden_words:
                new_forbidden_word = ForbiddenWordORM(
                    word_id = word.id,
                    forbidden_word=forbidden_word
                )
                session.add(new_forbidden_word)
        session.commit()

if __name__ == "__main__":
    main()