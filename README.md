# BTC Algorithmic Trading Platform

Production-quality BTC/USDT algorithmic trading platform with backtesting, risk management, and paper trading capabilities.

## Features

✅ **Multiple Trading Modes**
- Backtesting on historical data
- Paper trading (risk-free simulation)
- Testnet trading (exchange test environment)
- Live trading with capital preservation

✅ **Risk Management**
- Position sizing and leverage control
- Daily loss limits and drawdown thresholds
- Real-time risk monitoring
- Automated stop-loss and take-profit

✅ **Advanced Features**
- Multiple technical analysis strategies (EMA, RSI, MACD, Bollinger Bands)
- Real-time WebSocket data feeds
- Performance analytics and reporting
- Database persistence for trade history
- Redis caching for low-latency operations

## Project Structure

```
btc-algo-platform/
├── src/
│   ├── core/                 # Core trading engine
│   │   ├── engine.py         # Main trading engine
│   │   ├── strategy.py       # Strategy interface and implementations
│   │   ├── risk.py           # Risk management module
│   │   └── backtest.py       # Backtesting engine
│   ├── exchange/             # Exchange integrations
│   │   ├── base.py           # Base exchange interface
│   │   └── binance.py        # Binance integration
│   ├── data/                 # Data management
│   │   ├── models.py         # Data models
│   │   ├── repository.py     # Database access layer
│   │   └── cache.py          # Redis caching
│   ├── api/                  # REST API
│   │   ├── server.py         # FastAPI server
│   │   ├── routes.py         # API endpoints
│   │   ├── websocket.py      # WebSocket handlers
│   │   └── schemas.py        # Request/response schemas
│   ├── utils/                # Utilities
│   │   ├── logger.py         # Logging setup
│   │   ├── config.py         # Configuration management
│   │   └── decorators.py     # Common decorators
│   └── main.py               # Application entry point
├── tests/
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── conftest.py           # Pytest fixtures
├── config/
│   ├── database.py           # Database configuration
│   ├── redis.py              # Redis configuration
│   └── settings.py           # Application settings
├── migrations/               # Database migrations
│   └── versions/
├── docker/
│   ├── Dockerfile            # Application container
│   └── Dockerfile.nginx      # Nginx reverse proxy
├── deploy/
│   ├── docker-compose.yml    # Local development
│   ├── docker-compose.prod.yml # Production setup
│   ├── k8s/                  # Kubernetes manifests
│   └── scripts/              # Deployment scripts
├── .github/workflows/        # CI/CD pipelines
├── .env.example              # Environment template
├── requirements.txt          # Python dependencies
├── pyproject.toml            # Project metadata
├── pytest.ini                # Pytest configuration
├── Makefile                  # Common commands
└── docs/                     # Documentation
    ├── ARCHITECTURE.md       # Architecture overview
    ├── DEPLOYMENT.md         # Deployment guide
    ├── API.md                # API documentation
    └── STRATEGIES.md         # Strategy documentation
```

## Quick Start

### Prerequisites
- Python 3.9+
- Docker & Docker Compose
- PostgreSQL 13+
- Redis 6+

### Development Setup

```bash
# Clone the repository
git clone https://github.com/sandipp00/btc-algo-platform.git
cd btc-algo-platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Start infrastructure (PostgreSQL + Redis)
docker-compose up -d

# Run database migrations
alembic upgrade head

# Start the application
python src/main.py
```

### Docker Setup

```bash
# Build and start all services
docker-compose up --build

# API will be available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

## Configuration

See `.env.example` for all available options:

```bash
# Trading Configuration
MODE=paper                    # backtest, paper, testnet, live
SYMBOL=BTC/USDT
TIMEFRAME=1h

# Capital & Risk
INITIAL_CAPITAL=10000
RISK_PER_TRADE=0.01
MAX_DAILY_LOSS=0.03
MAX_DRAWDOWN=0.10
MAX_POSITIONS=3

# Exchange (never commit real keys)
EXCHANGE_API_KEY=your_api_key
EXCHANGE_API_SECRET=your_api_secret

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/btc_algo

# Redis
REDIS_URL=redis://localhost:6379/0

# API Server
API_HOST=0.0.0.0
API_PORT=8000
```

## API Endpoints

### Trading Operations
```
GET    /api/v1/trades              # List trades
POST   /api/v1/trades              # Create new trade
GET    /api/v1/trades/{id}         # Get trade details
PATCH  /api/v1/trades/{id}         # Update trade
DELETE /api/v1/trades/{id}         # Cancel trade
```

### Portfolio
```
GET    /api/v1/portfolio           # Get portfolio overview
GET    /api/v1/portfolio/positions # Get open positions
GET    /api/v1/portfolio/balance   # Get account balance
```

### Analytics
```
GET    /api/v1/analytics/pnl       # Profit & Loss analysis
GET    /api/v1/analytics/performance # Performance metrics
GET    /api/v1/analytics/backtest  # Backtest results
```

### WebSocket
```
WS     /ws/trades                  # Real-time trade updates
WS     /ws/portfolio               # Real-time portfolio updates
WS     /ws/market                  # Market data stream
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test suite
pytest tests/unit/
pytest tests/integration/

# Run with verbose output
pytest -v
```

## Deployment

### Production Deployment

See `deploy/DEPLOYMENT.md` for detailed instructions:

```bash
# Using Docker Compose (single server)
docker-compose -f deploy/docker-compose.prod.yml up -d

# Using Kubernetes (recommended for production)
kubectl apply -f deploy/k8s/
```

### CI/CD Pipeline

GitHub Actions automatically:
- Runs tests on every push
- Builds Docker images
- Deploys to staging/production
- Runs security scans

## Documentation

- [Architecture Guide](docs/ARCHITECTURE.md) - System design and components
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment instructions
- [API Reference](docs/API.md) - Complete API documentation
- [Strategy Guide](docs/STRATEGIES.md) - Building custom strategies

## Development Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes and run tests
pytest

# Format and lint code
make format
make lint

# Commit and push
git commit -am "feat: Add your feature"
git push origin feature/your-feature

# Create pull request on GitHub
```

## Performance Monitoring

The platform includes built-in monitoring:
- Trade execution metrics
- Strategy performance analytics
- Risk assessment dashboards
- Market data latency tracking

## Security

- API key management via environment variables
- Database connection pooling with SSL
- Rate limiting on API endpoints
- Input validation and sanitization
- CORS configuration for frontend access

## Troubleshooting

See the [docs](docs/) directory for common issues and solutions.

## License

MIT

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation
- Review test cases for usage examples
