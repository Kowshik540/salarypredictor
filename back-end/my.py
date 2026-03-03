# import pandas as pd
# import numpy as np
# from sklearn.model_selection import train_test_split
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
# import joblib
# import warnings

# warnings.filterwarnings("ignore")


# class SalaryPredictor:
#     def __init__(self):
#         self.model = None
#         self.feature_cols = []
#         self.skills_vocabulary = set()
#         self.df = None

#     # ---------------- LOAD DATA ----------------
#     def load_data(self, filepath):
#         df = pd.read_csv(filepath)

#         # Normalize text
#         df["job_role"] = df["job_role"].str.strip().str.title()
#         df["region"] = df["region"].str.strip().str.title()

#         # Convert skills string → list
#         df["skills_list"] = df["skills"].apply(
#             lambda x: [s.strip().title() for s in x.split(",")]
#         )

#         self.df = df
#         return df

#     # ---------------- PREPROCESS ----------------
#     def preprocess_data(self):
#         df = self.df.copy()

#         # ---------- JOB ROLE (Top 20) ----------
#         top_jobs = df["job_role"].value_counts().nlargest(20).index
#         for job in top_jobs:
#             df[f"job_{job.replace(' ', '_').lower()}"] = (
#                 df["job_role"] == job
#             ).astype(int)

#         # ---------- REGION (Top 15) ----------
#         top_regions = df["region"].value_counts().nlargest(15).index
#         for region in top_regions:
#             df[f"region_{region.replace(' ', '_').lower()}"] = (
#                 df["region"] == region
#             ).astype(int)

#         # ---------- SKILLS (Top 30) ----------
#         all_skills = [skill for skills in df["skills_list"] for skill in skills]
#         skill_counts = pd.Series(all_skills).value_counts()
#         top_skills = skill_counts.nlargest(30).index

#         self.skills_vocabulary = set(top_skills)

#         for skill in top_skills:
#             df[f"skill_{skill.replace(' ', '_').lower()}"] = df[
#                 "skills_list"
#             ].apply(lambda x: 1 if skill in x else 0)

#         # ---------- NUMBER OF SKILLS ----------
#         df["num_skills"] = df["skills_list"].apply(len)

#         # ---------- FEATURES ----------
#         feature_cols = []
#         feature_cols.extend(
#             [f"job_{job.replace(' ', '_').lower()}" for job in top_jobs]
#         )
#         feature_cols.extend(
#             [f"region_{r.replace(' ', '_').lower()}" for r in top_regions]
#         )
#         feature_cols.extend(
#             [f"skill_{s.replace(' ', '_').lower()}" for s in top_skills]
#         )
#         feature_cols.append("num_skills")

#         self.feature_cols = feature_cols

#         X = df[feature_cols].fillna(0)
#         y = df["salary"]

#         return X, y

#     # ---------------- TRAIN MODEL ----------------
#     def train_model(self, test_size=0.2, random_state=42):
#         X, y = self.preprocess_data()

#         X_train, X_test, y_train, y_test = train_test_split(
#             X, y, test_size=test_size, random_state=random_state
#         )

#         self.model = RandomForestRegressor(
#             n_estimators=150,
#             max_depth=25,
#             min_samples_split=5,
#             min_samples_leaf=2,
#             random_state=random_state,
#             n_jobs=-1,
#         )

#         self.model.fit(X_train, y_train)

#         y_pred_train = self.model.predict(X_train)
#         y_pred_test = self.model.predict(X_test)

#         metrics = {
#             "train_r2": r2_score(y_train, y_pred_train),
#             "test_r2": r2_score(y_test, y_pred_test),
#             "train_mae": mean_absolute_error(y_train, y_pred_train),
#             "test_mae": mean_absolute_error(y_test, y_pred_test),
#             "train_rmse": np.sqrt(mean_squared_error(y_train, y_pred_train)),
#             "test_rmse": np.sqrt(mean_squared_error(y_test, y_pred_test)),
#         }

#         return metrics

#     # ---------------- PREDICT ----------------
#     def predict_salary(self, job_title, skills, country):
#         if self.model is None:
#             raise ValueError("Model not trained or loaded")

#         job_title = job_title.strip().title()
#         country = country.strip().title()

#         if isinstance(skills, str):
#             skills_list = [s.strip().title() for s in skills.split(",")]
#         else:
#             skills_list = skills

#         features = np.zeros(len(self.feature_cols))
#         feature_index = {f: i for i, f in enumerate(self.feature_cols)}

#         # Job role
#         job_key = f"job_{job_title.replace(' ', '_').lower()}"
#         if job_key in feature_index:
#             features[feature_index[job_key]] = 1

#         # Region
#         region_key = f"region_{country.replace(' ', '_').lower()}"
#         if region_key in feature_index:
#             features[feature_index[region_key]] = 1

#         # Skills
#         for skill in skills_list:
#             skill_key = f"skill_{skill.replace(' ', '_').lower()}"
#             if skill_key in feature_index:
#                 features[feature_index[skill_key]] = 1

#         # Num skills
#         features[feature_index["num_skills"]] = len(skills_list)

#         prediction = self.model.predict([features])[0]
#         return round(prediction, 2)

#     # ---------------- SAVE / LOAD ----------------
#     def save_model(self, filename="salary_predictor_model.pkl"):
#         joblib.dump(
#             {
#                 "model": self.model,
#                 "feature_cols": self.feature_cols,
#                 "skills_vocabulary": list(self.skills_vocabulary),
#             },
#             filename,
#         )
#         print(f"Model saved as {filename}")

#     def load_saved_model(self, filename="salary_predictor_model.pkl"):
#         data = joblib.load(filename)
#         self.model = data["model"]
#         self.feature_cols = data["feature_cols"]
#         self.skills_vocabulary = set(data["skills_vocabulary"])
#         print(f"Model loaded from {filename}")


# # ---------------- MAIN ----------------
# if __name__ == "__main__":
#     predictor = SalaryPredictor()

#     print("Loading dataset...")
#     predictor.load_data("software_jobs_dataset_10000_rows.csv")

#     print("Training model...")
#     metrics = predictor.train_model()

#     print("\nMODEL PERFORMANCE")
#     for k, v in metrics.items():
#         print(f"{k.upper():12}: {v:.4f}")

#     predictor.save_model()

#     print("\nEXAMPLE PREDICTION")
#     salary = predictor.predict_salary(
#         job_title="Full Stack Developer",
#         skills="React, Node.js, MongoDB, AWS",
#         country="United States",
#     )
#     print(f"Predicted Salary: ${salary:,.2f}")

# import pandas as pd
# import numpy as np
# from sklearn.model_selection import train_test_split
# from sklearn.ensemble import GradientBoostingRegressor
# from sklearn.preprocessing import OneHotEncoder
# from sklearn.ensemble import HistGradientBoostingRegressor
# from sklearn.compose import ColumnTransformer
# from sklearn.pipeline import Pipeline
# from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
# import joblib
# import warnings

# warnings.filterwarnings("ignore")


# class SalaryPredictor:
#     def __init__(self):
#         self.model = None
#         self.preprocessor = None
#         self.df = None

#     # ---------------- LOAD DATA ----------------
#     def load_data(self, filepath):
#         df = pd.read_csv(filepath)

#         df["job_role"] = df["job_role"].str.strip().str.title()
#         df["region"] = df["region"].str.strip().str.title()
#         df["skills"] = df["skills"].str.strip().str.title()

#         self.df = df
#         return df

#     # ---------------- PREPROCESS ----------------
#     def preprocess_data(self):
#         df = self.df.copy()

#         X = df[["job_role", "skills", "region", "years_of_experience"]]
#         y = df["salary"]

#         categorical_features = ["job_role", "skills", "region"]
#         numeric_features = ["years_of_experience"]

#         self.preprocessor = ColumnTransformer(
#             transformers=[
#                 ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features),
#                 ("num", "passthrough", numeric_features),
#             ]
#         )

#         return X, y

#     # ---------------- TRAIN MODEL ----------------
#     def train_model(self, test_size=0.2, random_state=42):
#         X, y = self.preprocess_data()

#         X_train, X_test, y_train, y_test = train_test_split(
#             X, y, test_size=test_size, random_state=random_state
#         )

#         self.model = Pipeline(steps=[
#             ("preprocess", self.preprocessor),
#             # ("regressor", GradientBoostingRegressor(
#             #     n_estimators=300,
#             #     learning_rate=0.05,
#             #     max_depth=5,
#             #     random_state=random_state
#             # ))
#             ("regressor", HistGradientBoostingRegressor(
#     max_iter=120,
#     learning_rate=0.08,
#     max_depth=6,
#     random_state=random_state
# ))

#         ])

#         self.model.fit(X_train, y_train)

#         y_pred_train = self.model.predict(X_train)
#         y_pred_test = self.model.predict(X_test)

#         metrics = {
#             "train_r2": r2_score(y_train, y_pred_train),
#             "test_r2": r2_score(y_test, y_pred_test),
#             "train_mae": mean_absolute_error(y_train, y_pred_train),
#             "test_mae": mean_absolute_error(y_test, y_pred_test),
#             "train_rmse": np.sqrt(mean_squared_error(y_train, y_pred_train)),
#             "test_rmse": np.sqrt(mean_squared_error(y_test, y_pred_test)),
#         }

#         return metrics

#     # ---------------- PREDICT ----------------
#     def predict_salary(self, job_title, skills, country, years_of_experience):
#         if self.model is None:
#             raise ValueError("Model not trained or loaded")

#         row = pd.DataFrame([{
#             "job_role": job_title.strip().title(),
#             "skills": skills.strip().title(),
#             "region": country.strip().title(),
#             "years_of_experience": years_of_experience
#         }])

#         prediction = self.model.predict(row)[0]
#         return round(float(prediction), 2)

#     # ---------------- SAVE / LOAD ----------------
#     def save_model(self, filename="salary_predictor_model.pkl"):
#         joblib.dump(self.model, filename)
#         print(f"Model saved as {filename}")

#     def load_saved_model(self, filename="salary_predictor_model.pkl"):
#         self.model = joblib.load(filename)
#         print(f"Model loaded from {filename}")


# # ---------------- MAIN ----------------
# if __name__ == "__main__":
#     predictor = SalaryPredictor()

#     print("Loading dataset...")
#     predictor.load_data("global_job_salaries_200k_usd.csv")

#     print("Training model...")
#     metrics = predictor.train_model()

#     print("\nMODEL PERFORMANCE")
#     for k, v in metrics.items():
#         print(f"{k.upper():12}: {v:.4f}")

#     predictor.save_model()

#     print("\nEXAMPLE PREDICTION")
#     salary = predictor.predict_salary(
#         job_title="Full Stack Developer",
#         skills="React, Node.js, Aws",
#         country="United States",
#         years_of_experience=5
#     )
#     print(f"Predicted Salary: ${salary:,.2f}")




import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# 🔧 ADDED: PPP factors for training normalization
PPP_FACTOR = {
    "United States": 1.0,
    "India": 0.32,
    "Germany": 1.05,
    "United Kingdom": 1.02,
    "Canada": 1.03,
    "Australia": 1.01,
    "Japan": 0.95
}

def normalize_salary(row):
    ppp = PPP_FACTOR.get(row["region"], 1.0)
    return row["salary"] / ppp


class SalaryPredictor:
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.df = None

    # ---------------- LOAD DATA ----------------
    def load_data(self, filepath):
        df = pd.read_csv(filepath)
        df["job_role"] = df["job_role"].str.strip().str.title()
        df["region"] = df["region"].str.strip().str.title()
        df["skills"] = df["skills"].str.strip().str.title()
        df["years_of_experience"] = df["years_of_experience"].fillna(0)

        # 🔧 ADDED: PPP normalized salary for training
        df["salary_global"] = df.apply(normalize_salary, axis=1)

        self.df = df
        return df

    # ---------------- PREPROCESS ----------------
    def preprocess_data(self):
        df = self.df.copy()
        X = df[["job_role", "skills", "region", "years_of_experience"]]

        # 🔧 CHANGED: train on normalized salary instead of raw local salary
        y = df["salary_global"]

        categorical_features = ["job_role", "skills", "region"]
        numeric_features = ["years_of_experience"]

        self.preprocessor = ColumnTransformer(
            transformers=[
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features),
                ("num", "passthrough", numeric_features),
            ]
        )
        return X, y

    # ---------------- TRAIN MODEL ----------------
    def train_model(self, test_size=0.2, random_state=42):
        X, y = self.preprocess_data()
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        self.model = Pipeline(steps=[
            ("preprocess", self.preprocessor),
            ("regressor", HistGradientBoostingRegressor(
                max_iter=150,
                learning_rate=0.08,
                max_depth=6,
                random_state=random_state
            ))
        ])

        self.model.fit(X_train, y_train)

        y_pred_train = self.model.predict(X_train)
        y_pred_test = self.model.predict(X_test)

        metrics = {
            "train_r2": r2_score(y_train, y_pred_train),
            "test_r2": r2_score(y_test, y_pred_test),
            "train_mae": mean_absolute_error(y_train, y_pred_train),
            "test_mae": mean_absolute_error(y_test, y_pred_test),
            "train_rmse": np.sqrt(mean_squared_error(y_train, y_pred_train)),
            "test_rmse": np.sqrt(mean_squared_error(y_test, y_pred_test)),
        }

        return metrics

    # ---------------- PREDICT ----------------
    def predict_salary(self, job_title, skills, country, years_of_experience):
        if self.model is None:
            raise ValueError("Model not trained or loaded")

        row = pd.DataFrame([{
            "job_role": job_title.strip().title(),
            "skills": skills.strip().title(),
            "region": country.strip().title(),
            "years_of_experience": years_of_experience
        }])

        prediction = self.model.predict(row)[0]
        return round(float(prediction), 2)

    # 🔧 ADDED: explicit global salary predictor (same logic, cleaner name)
    def predict_global_salary(self, job_title, skills, country, years_of_experience):
        return self.predict_salary(job_title, skills, country, years_of_experience)

    # ---------------- SAVE / LOAD ----------------
    def save_model(self, filename="salary_predictor_model.pkl"):
        joblib.dump(self.model, filename)
        print(f"Model saved as {filename}")

    def load_saved_model(self, filename="salary_predictor_model.pkl"):
        self.model = joblib.load(filename)
        print(f"Model loaded from {filename}")


# ---------------- MAIN ----------------
if __name__ == "__main__":
    predictor = SalaryPredictor()
    print("Loading dataset...")
    predictor.load_data("global_job_salaries_200k_usd.csv")

    print("Training model...")
    metrics = predictor.train_model()

    print("\nMODEL PERFORMANCE")
    for k, v in metrics.items():
        print(f"{k.upper():12}: {v:.4f}")

    predictor.save_model()

    print("\nEXAMPLE PREDICTION")

    salary = predictor.predict_salary(
        job_title="Front End Developer",
        skills="Node.js",
        country="India",
        years_of_experience=1
    )
    print(f"Predicted Salary (Global USD): ${salary:,.2f}")
