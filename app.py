import streamlit as st
import pandas as pd
import seaborn as sb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import confusion_matrix, roc_auc_score
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

# Load Dataset
uploaded_file = st.file_uploader("Upload the Wine Quality Dataset (CSV file)", type="csv")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    st.title("Wine Quality Analysis App")
    st.write("Dataset Overview:")
    st.dataframe(df.head())
    
    # Show dataset info
    st.write("Dataset Info:")
    st.text(df.info())

    # Show statistics
    st.write("Dataset Statistics:")
    st.dataframe(df.describe().T)

    # Check for missing values
    st.write("Missing Values in the Dataset:")
    missing_values = df.isnull().sum()
    st.dataframe(missing_values[missing_values > 0])

    # Fill missing values
    for col in df.columns:
        if df[col].isnull().sum() > 0:
            df[col] = df[col].fillna(df[col].mean())

    # Display histograms for numerical features using seaborn
    st.write("Histograms of Numerical Features:")
    numeric_columns = df.select_dtypes(include=["float64", "int64"]).columns
    for col in numeric_columns:
        sb.histplot(df[col], kde=True)
        st.pyplot()

    # Correlation heatmap using seaborn
    st.write("Correlation Heatmap:")
    fig = plt.figure(figsize=(12, 8))
    sb.heatmap(df.corr(), annot=True, cmap="coolwarm")
    st.pyplot(fig)

    # Feature Engineering
    if 'quality' in df.columns:
        df['best quality'] = [1 if x > 5 else 0 for x in df['quality']]
        features = df.drop(['quality', 'best quality'], axis=1)
        target = df['best quality']
    else:
        st.error("'quality' column not found in dataset!")
        st.stop()

    # Impute missing values
    imputer = SimpleImputer(strategy="mean")
    features = pd.DataFrame(imputer.fit_transform(features), columns=features.columns)

    # Train-Test Split
    xtrain, xtest, ytrain, ytest = train_test_split(features, target, test_size=0.2, random_state=42)

    # Scale Features
    scaler = MinMaxScaler()
    xtrain = scaler.fit_transform(xtrain)
    xtest = scaler.transform(xtest)

    # Model Training
    models = [LogisticRegression(), XGBClassifier(), SVC(kernel='rbf')]
    model_names = ["Logistic Regression", "XGBoost Classifier", "SVC"]
    model_accuracies = []

    st.write("Model Performance:")
    for i, model in enumerate(models):
        model.fit(xtrain, ytrain)
        train_acc = roc_auc_score(ytrain, model.predict(xtrain))
        test_acc = roc_auc_score(ytest, model.predict(xtest))
        st.write(f"**{model_names[i]}**")
        st.write(f"- Training ROC-AUC Score: {train_acc:.2f}")
        st.write(f"- Validation ROC-AUC Score: {test_acc:.2f}")
        model_accuracies.append(test_acc)

    # Display Confusion Matrix for Best Model
    best_model_idx = model_accuracies.index(max(model_accuracies))
    st.write(f"The best-performing model is: **{model_names[best_model_idx]}**")

    cm = confusion_matrix(ytest, models[best_model_idx].predict(xtest))
    fig = plt.figure(figsize=(8, 6))
    sb.heatmap(cm, annot=True, fmt='d', cmap="Blues", xticklabels=["No", "Yes"], yticklabels=["No", "Yes"])
    st.pyplot(fig)

    # Histogram of a specific feature
    st.write("Wine Quality Histogram")

    # Allow the user to choose a feature for histogram after uploading the file
    feature = st.selectbox('Select a feature for histogram:', df.columns)

    # Display the histogram for the selected feature
    st.subheader(f'Histogram of {feature}')
    sb.histplot(df[feature], kde=True)
    st.pyplot()