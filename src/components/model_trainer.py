import os
import sys
from dataclasses import dataclass

from catboost import CatBoostRegressor
from sklearn.ensemble import(
    RandomForestRegressor,
    GradientBoostingRegressor,
    AdaBoostRegressor,
)

from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor

from src.exception import CustomException
from src.logger import logging
from src.utils import evaluate_models, save_object


@dataclass
class ModelTrainerConfig:
    trained_model_file_path: str = os.path.join('artifacts', 'model.pkl')

class ModelTrainer:
    def __init__(self):
        self.model_trainer_config = ModelTrainerConfig()

    def initiate_model_trainer(self, train_array, test_array):
        try:
            logging.info("Splitting training and test input data")
            X_train, y_train, X_test, y_test = (
                train_array[:, :-1],
                train_array[:, -1],
                test_array[:, :-1],
                test_array[:, -1],
            )

            models = {
                'RandomForestRegressor': RandomForestRegressor(),
                'GradientBoostingRegressor': GradientBoostingRegressor(),
                'DecisionTreeRegressor': DecisionTreeRegressor(),
                'LinearRegression': LinearRegression(),
                'KNeighborsRegressor': KNeighborsRegressor(),
                'XGBRegressor': XGBRegressor(),
                'CatBoostRegressor': CatBoostRegressor(verbose=False),
                'AdaBoostRegressor': AdaBoostRegressor(),
            }
            params = {
                'DecisionTreeRegressor': {
                    'criterion': ['absolute_error', 'friedman_mse', 'poisson','squared_error'],
                    #'splitter' : ['best', 'random'],
                    #'max_features': ['auto', 'sqrt', 'log2'],
                },
                'RandomForestRegressor': {
                    'n_estimators': [10, 50, 100],
                    'criterion': ['absolute_error', 'friedman_mse', 'poisson','squared_error'],
                    #'max_features': ['auto', 'sqrt', 'log2'],
                },
                'GradientBoostingRegressor': {
                    'n_estimators': [8,10,16,32,50, 100],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'loss': ['squared_error', 'absolute_error', 'huber'],
                },
                "LinearRegression": {
                    # No hyperparameters to tune for Linear Regression
                },
                "KNeighborsRegressor": {
                    'n_neighbors': [3, 5, 7],
                    'weights': ['uniform', 'distance'],
                },
                "XGBRegressor": {
                    'n_estimators': [10, 50, 100],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'max_depth': [3, 5, 7],
                },
                "CatBoostRegressor": {
                    'iterations': [10, 50, 100],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'depth': [3, 5, 7],
                },
                "AdaBoostRegressor": {
                    'n_estimators': [10, 50, 100],
                    'learning_rate': [0.01, 0.1, 0.2],
                }

            }
            model_report:dict=evaluate_models(X_train = X_train, y_train = y_train, X_test = X_test,
                                               y_test = y_test, models = models,param=params)



            # To get best model score from the model report
            best_model_score = max(sorted(model_report.values()))

            # To get best model name from the model report
            best_model_name = list(model_report.keys())[
                list(model_report.values()).index(best_model_score)
            ]

            best_model = models[best_model_name]

            if best_model_score < 0.6:
                raise CustomException("No best model found")
            logging.info(f"Best model found: {best_model_name} with score: {best_model_score}")

            save_object(
                file_path=self.model_trainer_config.trained_model_file_path,
                obj=best_model,
            )

            predicted = best_model.predict(X_test)

            r2_score_value = r2_score(y_test, predicted)
            return r2_score_value


        except Exception as e:
            raise CustomException(e, sys)