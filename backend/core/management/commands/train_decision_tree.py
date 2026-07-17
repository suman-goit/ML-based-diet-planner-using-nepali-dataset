"""
python manage.py train_decision_tree

Builds Decision Tree training data from the *current* Food table (sodium/sugar
threshold labels, not user behavior — see architecture doc section 4) and
fits+saves the shallow DecisionTreeClassifier used by core/decision_tree.py.

Run this after seed_data, and again any time Food rows change.
"""
import pandas as pd
from django.core.management.base import BaseCommand

from core import decision_tree
from core.models import Food


class Command(BaseCommand):
    help = "Train and cache the medical-suitability Decision Tree"

    def handle(self, *args, **options):
        foods = Food.objects.all()
        if not foods.exists():
            self.stderr.write(
                self.style.ERROR("No foods in the database yet — run seed_data first.")
            )
            return

        df = pd.DataFrame(
            list(
                foods.values(
                    "food_id", "sodium_mg", "sugar_g", "carbs_g", "fat_g", "calories"
                )
            )
        )
        clf = decision_tree.train_and_save(df)

        train_df = decision_tree.build_training_data(df)
        accuracy = (clf.predict(train_df[decision_tree.FEATURE_COLS]) == train_df["suitable"]).mean()

        self.stdout.write(
            self.style.SUCCESS(
                f"Trained on {len(df)} foods x 2 conditions ({len(train_df)} rows). "
                f"Training accuracy: {accuracy:.1%}. Saved to {decision_tree.MODEL_PATH}"
            )
        )
