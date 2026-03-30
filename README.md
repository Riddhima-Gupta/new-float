# 🌊 FloatChat AI - The Voice of Ocean

FloatChat AI is an intelligent oceanographic data assistant that helps scientists explore and analyze data from oceanographic floats. Built with **Streamlit** and powered by **FastAPI + AI models**, it provides both scientific explanations and interactive visualizations of ocean data.

🌐 Curious to see FloatChat AI at work? Visit the live app and explore ocean data yourself: [Launch FloatChat](<https://riddhima-gupta-new-float-app-o86832.streamlit.app/>)

---

## ✨ Features

- **🤖 AI-Powered Analysis**: Ask questions in natural language about oceanographic data
- **📊 Interactive Visualizations**: Generate plots, heatmaps, and trajectory maps for data exploration
- **🔬 Scientific Insights**: Get detailed explanations about temperature, salinity, and ocean conditions
- **🌍 Real Ocean Data**: Access authentic data from Argo floats worldwide
- **💬 Chat Interface**: Intuitive conversation-based interface with chat history
- **🎤 Voice Input**: Speak queries, see them transcribed into the input bar, edit, and send
- **📥 File Upload in Query Bar**: Attach CSV/TXT files directly where you type queries
- **📤 Export Capabilities**: Download your conversation history and generated charts
- **🎨 Modern UI**: Oceanic-themed design using Streamlit

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher (3.11 is best)
- Git (for cloning)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Riddhima-Gupta/float-djra.git
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app:**
   ```bash
   python run_app.py
   ```

The app will open in your browser at `http://localhost:8501`.

---

## 🎯 How It Works

FloatChat AI uses a combination of technologies to provide intelligent oceanographic data analysis:

### 1. **Retrieval Augmented Generation (RAG)**
- Vector database stores oceanographic float data
- Semantic search finds relevant data based on your questions
- Context is provided to the AI model for accurate responses

### 2. **AI Language Model**
- Generates scientific explanations based on retrieved data
- Understands complex queries about oceanographic phenomena

### 3. **Data Visualization**
- Automatically detects when visualizations are requested
- Generates interactive charts using Plotly/Matplotlib
- Supports multiple chart types: profiles, histograms, trajectories, heatmaps

### 4. **Real Ocean Data**
- Uses authentic Argo float data (temperature, salinity, pressure, location)
- Supports data filtering by specific float IDs

---

## 💡 Example Queries

### Temperature Analysis
- "What is the temperature profile for float 1900979?"
- "Show me temperature data at different depths"
- "Plot temperature vs pressure for float 1900979"

### Salinity Data
- "What is the salinity profile for float 1900975?"
- "Compare salinity at surface vs deep water"

### Visualizations
- "Create a histogram of salinity data"
- "Show the trajectory of float 1900975"
- "Visualize the combined temperature and salinity profile"

---

## 📊 Visualization Features

FloatChat AI can generate various types of visualizations:

- **Temperature vs Pressure Profiles**
- **Salinity vs Pressure Profiles**
- **Combined Profiles**
- **Histograms**
- **Trajectory Maps**
- **Heatmaps**
- **Interactive Charts** (hover, zoom, pan, download as PNG image, autoscale)

---

## 🛠️ Technical Architecture

### Backend Components
- **`api.py`**: FastAPI endpoints for queries, plots, uploads, history
- **`main.py`**: Core AI logic and visualization functions
- **`vector.py`**: Vector database management and retrieval
- **`run_app.py`**: Unified runner for backend + frontend
- **`app.py`**: Streamlit interface

### Data Flow
1. User asks a question or uploads a file
2. Query is processed to extract float ID and visualization needs
3. Vector database retrieves relevant data
4. AI model generates scientific explanation
5. Visualization is created if requested
6. Response is displayed with both text and charts

### Dependencies
- **Streamlit**: Web interface framework
- **FastAPI + Uvicorn**: Backend API
- **ChromaDB / Sentence Transformers**: Vector database and embeddings
- **Plotly / Matplotlib**: Interactive visualizations
- **Pandas / NumPy**: Data manipulation

---

## 🎨 UI Features

- **Modern Oceanic Theme**: clean design
- **File Upload in Query Bar**: Attach CSV/TXT directly
- **Sample Queries**: Sidebar suggestions
- **Chat History**: Persistent and exportable
- **Copy/Share Buttons**: Quick sharing of outputs
- **Download Visualizations**: Save plots as images

---

## 📈 Future Enhancements

- Additional chart types (scatter plots, 3D visualizations)
- Voice Input: Speech-to-text in query bar
- Multi-float comparison
- Time series analysis
- Advanced filtering options
- Cloud deployment for collaborative use

---

## 🤝 Contributing

We welcome contributions! Please feel free to:
- Report bugs and issues
- Suggest new features
- Submit pull requests
- Improve documentation

---

## 📄 License

This project is open source and available under the MIT License.

---

**🌊 FloatChat AI — Exploring the depths of oceanographic data**  
*Made with ❤️ for ocean science and data exploration*
