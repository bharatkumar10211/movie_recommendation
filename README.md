# 🎬 Movie Recommendation System

An interactive, high-performance web application built with **Streamlit** that provides customized movie recommendations. The system implements two primary recommendation strategies: **Content-Based Filtering** (using text metadata, NLP, and Cosine Similarity) and **Popularity-Based Filtering** (using the IMDB Weighted Rating formula).

---

## 🌟 Features

- **Dual Recommendation Engines**:
  - **🎯 Content-Based**: Recommends movies similar to a chosen title by analyzing genres, keywords, cast, crew, and overviews. It handles spelling search adjustments and matches closest titles.
  - **📈 Popularity-Based**: Recommends the highest-rated movies within a selected genre and language using a robust weighted score.
- **Premium User Interface**:
  - Clean, responsive design overrides with standard styling hooks.
  - Interactive navigation bar (Home, About, Dataset Info).
  - Clean layout containing pill toggles, sliders for recommendation counts, and dynamic tables.
  - Fast response times (< 50ms query latency) via cached dataset loaders.

---

## 🛠️ Machine Learning Pipeline & Algorithms

### 1. Content-Based Recommendation
The system processes metadata fields from TMDB movies and credits:
- **Feature Extraction**: Merges `genres`, `keywords`, `cast` (top actors), `crew` (directors), and `overview` text into a single metadata `tag` string.
- **Text Preprocessing**: Normalizes text and applies stemming using NLTK's **PorterStemmer** to reduce words to their base form.
- **Vectorization**: Vectorizes the processed tags using a **Bag of Words** model (via `CountVectorizer`, restricted to top 5,000 features).
- **Similarity Measure**: Computes the **Cosine Similarity** matrix across all 4,803 movies:
  $$\text{Cosine Similarity}(\vec{A}, \vec{B}) = \frac{\vec{A} \cdot \vec{B}}{\|\vec{A}\| \|\vec{B}\|}$$
- **Inference**: Looks up the target movie's similarity vector, sorts similar movies in descending order, and displays top results.

### 2. Popularity-Based Recommendation
To prevent bias from movies with very few ratings (e.g., a movie with one 10/10 rating), the system uses the **IMDB Weighted Rating** formula:
$$\text{Score} = \left(\frac{v}{v+m}\right) \times R + \left(\frac{m}{v+m}\right) \times C$$

Where:
- $v$: Number of votes for the movie (`vote_count`).
- $m$: Minimum votes required to be listed in the chart (set dynamically as the 90th percentile of vote counts in the filtered subset).
- $R$: Average rating of the movie (`vote_average`).
- $C$: The mean vote across the entire dataset.

This formula ensures popular recommendations are both highly rated and widely viewed.

---

## 📁 Project Structure

```bash
├── .streamlit/
│   └── config.toml          # Custom theme configuration for Streamlit
├── app.py                   # Main Streamlit web application
├── content.ipynb            # Jupyter Notebook for Content-Based model development
├── popularity.ipynb         # Jupyter Notebook for Popularity-Based analysis
├── movies.pkl               # Pickled DataFrame of processed movies metadata
├── similarity.pkl           # Pickled precomputed 4,803 × 4,803 similarity matrix
├── tmdb_5000_movies.csv     # Movie dataset (metadata, budget, ratings, etc.)
└── tmdb_5000_credits.csv    # Credits dataset (cast, crew, movie_id)
```

---

## 🚀 Setup & Execution

### Prerequisites
Make sure you have Python installed. The system requires the following libraries:
- `streamlit`
- `pandas`
- `numpy`
- `nltk`
- `scikit-learn`

### Installation
1. Clone or download this repository.
2. Install the required dependencies:
   ```bash
   pip install streamlit pandas numpy nltk scikit-learn
   ```

### Preprocessing (Optional)
The similarity matrix (`similarity.pkl`) and clean metadata are already precomputed and provided. However, if you want to rebuild the models or inspect the data pipeline:
1. Open and run all cells in `content.ipynb` to regenerate `movies.pkl` and `similarity.pkl`.
2. Open and run `popularity.ipynb` to inspect the weighted rating distribution.

### Running the App
Launch the interactive web interface by running the Streamlit app:
```bash
streamlit run app.py
```
Open the local URL displayed in your command prompt (usually `http://localhost:8501`) in your browser.

---

## 📊 Dataset Information

The recommendation model utilizes the **TMDB 5000 Movies Dataset**, which contains:
- **4,803 Movies** and metadata spanning **37 Unique Languages**.
- Detailed listings of genres, production budgets, popularity metrics, release dates, and vote stats.
- Complete cast lists and production crew details.

---

## 📜 License & Acknowledgments

- Dataset provided by [TMDB](https://www.themoviedb.org/) via Kaggle.
- Developed with Python, Scikit-Learn, and Streamlit.
