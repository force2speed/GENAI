# AI-Powered Misinformation Detection API

A fully AI-powered misinformation detection system that uses Google Gemini to dynamically optimize all parameters without any hardcoded values.

## 🚀 Features

- **🤖 AI-Driven Configuration**: All parameters dynamically optimized by Google Gemini AI
- **🧠 Intelligent Claim Extraction**: AI-powered claim identification and validation
- **📊 Smart Evidence Retrieval**: Dynamic source evaluation with RAG (Retrieval-Augmented Generation)
- **🎯 Adaptive Stance Detection**: AI-powered relationship analysis between claims and evidence
- **⚖️ Dynamic Risk Scoring**: AI-calculated risk assessments with adaptive thresholds
- **🌐 Intelligent URL Processing**: Smart content extraction and quality filtering
- **🔄 Zero Hardcoded Values**: Complete elimination of static configuration

## 🏗️ Architecture

The system consists of AI-powered components:

- **AI Configuration Manager** (`ai_config_manager.py`) - Central AI optimization system
- **Claim Extractor** (`claim_extractor.py`) - AI-driven claim identification
- **Evidence Retriever** (`evidence_retriever.py`) - RAG-based evidence collection
- **Stance Detector** (`stance_detector.py`) - AI relationship analysis
- **Risk Scorer** (`risk_scorer.py`) - Dynamic risk assessment
- **URL Extractor** (`url_extractor.py`) - Intelligent content processing
- **Main API** (`main.py`) - FastAPI-based REST interface

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/sakethksg/Gen_Ai.git
   cd Gen_Ai/sakethms
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

4. **Run the API**:
   ```bash
   python main.py
   ```

The API will start on `http://localhost:5000`

## 🔧 Configuration

The system uses AI-powered configuration management. Set these environment variables:

- `GEMINI_API_KEY`: Your Google Gemini API key (required)
- `REDIS_URL`: Redis connection string (optional, for caching)
- `LOG_LEVEL`: Logging level (default: INFO)

## 📡 API Endpoints

### Main Analysis
- `POST /analyze` - Analyze text or URL for misinformation
- `GET /health` - Health check and system status
- `GET /metrics` - Performance and system metrics
- `POST /add-evidence` - Add evidence documents to the database

### Example Request
```json
{
  "text": "The Earth is flat and NASA has been hiding this truth.",
  "url": "https://example.com/article"
}
```

### Example Response
```json
{
  "status": "success",
  "claims": [...],
  "evidence": [...],
  "stance_analysis": [...],
  "risk_scoring": {
    "overall_score": 0.85,
    "verdict": "LIKELY_MISINFORMATION",
    "confidence": 0.92,
    "explanation": "AI-generated risk assessment..."
  },
  "processing_time": 2.34,
  "metadata": {...}
}
```

## 🧪 Testing

```bash
# Test API health
curl http://localhost:5000/health

# Test analysis
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Sample text to analyze"}'
```

## 🚀 Advanced Features

- **Dynamic Parameter Optimization**: AI continuously optimizes system parameters
- **Intelligent Caching**: Smart caching with AI-optimized invalidation
- **Adaptive Thresholds**: Risk thresholds adjust based on content analysis
- **Context-Aware Processing**: Different optimization strategies for different content types
- **Performance Learning**: System improves based on processing history

## 🏆 Performance

- **Processing Speed**: ~2-5 seconds per analysis
- **Accuracy**: AI-optimized for maximum precision
- **Scalability**: Async processing with intelligent resource management
- **Reliability**: Comprehensive error handling and fallback mechanisms

## 🔐 Security

- Environment-based configuration
- Input validation and sanitization
- Rate limiting and resource protection
- Secure API key management

## 📊 Monitoring

The system provides comprehensive metrics:
- Processing times and success rates
- AI optimization effectiveness
- Cache hit rates and performance
- Resource utilization and health status

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API health endpoint for system status

## 🎯 Version History

- **v3.0-AI**: Complete AI-powered transformation, zero hardcoded values
- **v2.0**: Enhanced RAG implementation with vector database
- **v1.0**: Initial misinformation detection pipeline

---

**Built with ❤️ using Google Gemini AI and FastAPI**
