# Innopolis Report

A comprehensive reporting system with generator and client components for blockchain-based discussions.




# What is InnoPolis
InnoPolis is a decentralized version of [pol.is](https://pol.is/home). Polis is an open-source technology for surveys (or wikisurveys, to be more precise). It is a system that allows people to submit statements about an issue, and vote on each other's statements (agree/disagree/pass). Machine learning is used to process the data and transform it into a report, where major clusters in the different points of view could be seen and analyzed. It helps with finding major points of consensus, disagreement or misunderstanding between participants.

# Why InnoPolis?

While Polis is a powerful deliberation tool, it has yet to be widely adopted by cryptocurrency communities. InnoPolis bridges this gap by providing:

## Community Definition
Flexible community identification through various on-chain credentials:
  - ERC20 holdings
  - NFT holdings
  - ENS
  - Custom Authentication 

## Data-Driven Insights
- Standardized reporting of collective sentiment and ideas
- Statistical analysis of community consensus and divergence
- Visual representation of opinion clusters

## Use Cases
- Enhanced DAO governance and decision-making processes
- Direct feedback channels between developers and users
- Collective expression tools for Web3 communities
- Community sentiment analysis and trend identification

# Data

All data is stored on chain, therefore it can not be deleted or modified. There is frontend page to generate report. This frontend takes data from blockchain and generates HTML page with vote statistics. Anyone can launch docker image to generate report locally.

## Project Structure

The repository consists of three main components:

- `generator/` - Python-based report generation service
- `client-report/` - React-based report viewing interface
- `InnoPolis-frontend/` - Frontend submodule (separate repository)

## Generator Service

### Prerequisites

- Python 3.x
- PostgreSQL client
- Virtual environment (recommended)

### Dependencies
```python
eth_abi==5.1.0
Flask==3.1.0
psycopg2-binary==2.9.10
python-dotenv==1.0.1
web3==7.5.0
```

### Installation
```bash
cd generator
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Client Report

### Prerequisites

- Node.js
- NPM

### Installation
```bash
cd client-report
npm install
```

### Available Scripts

- `npm start` - Runs the webpack dev server for development
- `npm run build:prod` - Builds static assets for production deployment

## Docker Setup

The project uses Docker for containerized development and deployment. Each component has its own Docker configuration.

### Prerequisites

- Docker
- Docker Compose

### Generator Service Docker

The generator service uses a multi-stage build process:

```bash
# Build the image
docker build -t innopolis-generator ./generator
# Run the container
docker run -p 5000:5000 \
-e DATABASE_URL=postgresql://user:password@host:5432/dbname \
innopolis-generator
```


### Docker Compose

For running the entire stack:
```bash
# Start all services
docker-compose up -d
# View logs
docker-compose logs -f
# Stop all services
docker-compose down
```

Environment variables can be configured in a `.env` file:
```text
DATABASE_URL=postgresql://user:password@host:5432/dbname
SERVICE_URL=http://generator:5000
```

### Docker Development Tips

- Use volume mounts for development to enable hot-reloading:
  ```yaml
  volumes:
    - ./generator:/app
    - ./client-report:/app
  ```
- Use Docker networks to enable service communication
- Use Docker Compose profiles for different deployment scenarios

## Development Setup

1. Clone the repository with submodules:
   ```bash
   git clone --recursive https://github.com/[username]/innopolis-report.git
   ```

2. If you've already cloned the repository:
   ```bash
   git submodule update --init --recursive
   ```

3. Set up each component following their respective installation instructions

4. Set up each component following their respective installation instructions

## File Structure
```
innopolis-report/
├── generator/
│ ├── math/
│ ├── requirements.txt
│ └── test-data/
├── client-report/
│ ├── public/
│ ├── src/
│ └── package.json
└── InnoPolis-frontend/ (submodule)
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Ignored Files

The following files and directories are ignored in version control:
```
.env
venvpycache
.swp
node_modules
output
```

Make sure to properly configure these files in your development environment.
